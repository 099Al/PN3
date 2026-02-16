from __future__ import annotations

import json
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, func

from src.api.emulatorcexio.order_state import calc_quote_needed_for_buy
from src.api.provider import ApiProvider
from src.database.connect import DataBase
from src.database.models import ActiveOrder, Balance, Balance_Algo
from src.trade_utils.date_unix import utcnow_dt, parse_iso_z_to_naive



"""
После устанорвки ордеров, нужно сохранить в таблицу active_orders_table
В локальной базе для аналитики

"""
async def algo_set_order(amount, price, sell_buy, accountId, algo_name):

    api_provider = ApiProvider.get(account_id=accountId)

    res = await api_provider.set_order(amount, price, sell_buy)
    if res.get("data", {}).get("status") == "NEW":
        await save_active_order(res, algo=algo_name)



async def save_active_order(
    execution_report: dict,
    *,
    algo: str = "",
) -> None:

    db = DataBase()
    async with db.get_session_maker()() as session:

        data = execution_report["data"]

        side_u = str(data["side"]).upper()

        amount = Decimal(str(data["requestedAmountCcy1"]))
        price = Decimal(str(data["price"]))
        reserved = _calc_reserved(side_u, amount, price)

        base = str(data["currency1"])
        quote = str(data["currency2"])

        order = ActiveOrder(
            orderId=int(data["orderId"]),
            clientOrderId=str(data["clientOrderId"]),
            accountId=(data.get("accountId") or None),
            date=parse_iso_z_to_naive(str(data["transactTime"])),
            unix_date=int(data["clientCreateTimestamp"]),  # ms
            base=str(data["currency1"]),
            quote=str(data["currency2"]),
            side=str(data["side"]).lower(),
            amount=amount,
            price=price,
            reserved=reserved,
            order_type=str(data.get("orderType").lower() or "limit"),
            full_traid=json.dumps(data, ensure_ascii=False),
            algo=algo,
            sys_date=utcnow_dt(),
        )

        #Запись в ACTIVE_ORDERS
        merged = await session.merge(order)

        if side_u == "BUY":
            # резервируется quote.
            # Запись в BALANCE
            await _apply_balance_reserve(
                session,
                curr=quote,
                delta_amount=-reserved,
                delta_reserved=reserved,
            )
            #Запись в BALANCE_ALGO
            await _apply_balance_algo_reserve(
                session,
                algo=algo,
                curr=quote,
                delta_amount=-reserved,
                delta_reserved=reserved,
            )


        else:  # SELL
            # резервируется base
            await _apply_balance_reserve(
                session,
                curr=base,
                delta_amount=-reserved,
                delta_reserved=reserved,
            )
            await _apply_balance_algo_reserve(
                session,
                algo=algo,
                curr=base,
                delta_amount=-reserved,
                delta_reserved=reserved,
            )


        await session.commit()



def _calc_reserved(side: str, amount: Decimal, price: Decimal) -> Decimal:
    s = (side or "").upper()
    if s == "BUY":
        need_quote = calc_quote_needed_for_buy(amount, price)
        return Decimal(str(need_quote))
    if s == "SELL":
        return amount
    raise ValueError(f"Unknown side={side!r}")

async def _ensure_balance_algo_row(session: AsyncSession, *, algo: str, curr: str) -> None:
    res = await session.execute(
        select(Balance_Algo.algo).where(Balance_Algo.algo == algo, Balance_Algo.curr == curr)
    )
    if res.scalar_one_or_none() is None:
        session.add(
            Balance_Algo(
                algo=algo,
                curr=curr,
                amount_limit=Decimal("0"),
                amount=Decimal("0"),
                reserved=Decimal("0"),
            )
        )
        await session.flush()

async def _apply_balance_algo_reserve(
    session: AsyncSession,
    *,
    algo: str,
    curr: str,
    delta_amount: Decimal,
    delta_reserved: Decimal,
) -> None:
    # создаём строку если нет
    await _ensure_balance_algo_row(session, algo=algo, curr=curr)

    stmt = (
        update(Balance_Algo)
        .where(Balance_Algo.algo == algo, Balance_Algo.curr == curr)
        .values(
            {
                Balance_Algo.amount: Balance_Algo.amount + delta_amount,
                Balance_Algo.reserved: func.coalesce(Balance_Algo.reserved, 0) + delta_reserved,
            }
        )
    )
    await session.execute(stmt)


async def _apply_balance_reserve(
    session: AsyncSession,
    *,
    curr: str,
    delta_amount: Decimal,
    delta_reserved: Decimal,
) -> None:
    """
    delta_amount: на сколько изменить amount (например -reserved)
    delta_reserved: на сколько изменить reserved (например +reserved)
    """
    # amount = amount + delta_amount
    # reserved = coalesce(reserved,0) + delta_reserved
    values = {
        Balance.amount: Balance.amount + delta_amount,
        Balance.reserved: func.coalesce(Balance.reserved, 0) + delta_reserved,
    }

    values.update(
        {
            Balance.calc_amount: func.coalesce(Balance.calc_amount, 0) + delta_amount,
            Balance.calc_reserved: func.coalesce(Balance.calc_reserved, 0) + delta_reserved,
        }
    )

    stmt = (
        update(Balance)
        .where(Balance.curr == curr)
        .values(values)
    )
    await session.execute(stmt)









