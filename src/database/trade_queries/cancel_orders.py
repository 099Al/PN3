from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.provider import ApiProvider
from src.database.connect import DataBase
from src.database.models import ActiveOrder, Balance, Balance_Algo
from src.trade_utils.date_unix import utcnow_dt


"""
Модуль снятия ордера:
- вызывает API cancel_order(orderId)
- если ок -> удаляет ордер из ActiveOrder
- возвращает reserved обратно в amount (и в calc_* тоже)
- аналогично правит Balance_Algo (algo берём из ActiveOrder)
"""


async def algo_cancel_order(order_id: int, *, accountId: str) -> dict:
    api = ApiProvider.get(account_id=accountId)

    res = await api.cancel_order(order_id)
    if res.get("ok") != "ok":
        return res

    # cancel_order у тебя возвращает {'ok':'ok','data':{}}
    # значит, после успеха синхронизируем локальную БД
    await cancel_active_order_local(order_id=order_id)

    return res


async def cancel_active_order_local(*, order_id: int) -> None:
    db = DataBase()
    async with db.get_session_maker()() as session:
        await _cancel_active_order_tx(session=session, order_id=order_id)
        await session.commit()


async def _cancel_active_order_tx(*, session: AsyncSession, order_id: int) -> None:
    order = (
        (await session.execute(select(ActiveOrder).where(ActiveOrder.orderId == order_id)))
        .scalars()
        .first()
    )
    if order is None:
        return  # уже нет

    side_u = (order.side or "").upper()  # BUY/SELL (в БД у тебя lower)
    base = order.base
    quote = order.quote
    reserved = Decimal(str(order.reserved or 0))
    algo = order.algo or ""

    # 1) вернуть reserved обратно в balance
    # BUY -> reserved в quote
    # SELL -> reserved в base
    if reserved != 0:
        if side_u == "BUY":
            await _apply_balance_release(session, curr=quote, delta_amount=reserved, delta_reserved=-reserved)
            await _apply_balance_algo_release(session, algo=algo, curr=quote, delta_amount=reserved, delta_reserved=-reserved)
        elif side_u == "SELL":
            await _apply_balance_release(session, curr=base, delta_amount=reserved, delta_reserved=-reserved)
            await _apply_balance_algo_release(session, algo=algo, curr=base, delta_amount=reserved, delta_reserved=-reserved)
        else:
            raise ValueError(f"Unknown side={order.side!r} for orderId={order_id}")

    # 2) удалить ActiveOrder
    await session.execute(delete(ActiveOrder).where(ActiveOrder.orderId == order_id))


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


async def _apply_balance_algo_release(
    session: AsyncSession,
    *,
    algo: str,
    curr: str,
    delta_amount: Decimal,
    delta_reserved: Decimal,
) -> None:
    if not algo:
        return
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


async def _apply_balance_release(
    session: AsyncSession,
    *,
    curr: str,
    delta_amount: Decimal,
    delta_reserved: Decimal,
) -> None:
    """
    Возвращаем reserved обратно в amount.
    Также правим calc_amount/calc_reserved так же.
    """
    values = {
        Balance.amount: Balance.amount + delta_amount,
        Balance.reserved: func.coalesce(Balance.reserved, 0) + delta_reserved,
        Balance.calc_amount: func.coalesce(Balance.calc_amount, 0) + delta_amount,
        Balance.calc_reserved: func.coalesce(Balance.calc_reserved, 0) + delta_reserved,
    }

    stmt = (
        update(Balance)
        .where(Balance.curr == curr)
        .values(values)
    )
    await session.execute(stmt)
