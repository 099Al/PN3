from __future__ import annotations

import json
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.emulatorcexio.order_state import calc_quote_needed_for_buy
from src.database.connect import DataBase
from src.database.models import ActiveOrder
from src.trade_utils.date_unix import utcnow_dt, parse_iso_z_to_naive



"""
После устанорвки ордеров, нужно сохранить в таблицу active_orders_table
В локальной базе для аналитики

"""

def _calc_reserved(side: str, amount: Decimal, price: Decimal) -> Decimal:
    s = (side or "").upper()
    if s == "BUY":
        need_quote = calc_quote_needed_for_buy(amount, price)
        return Decimal(str(need_quote))
    if s == "SELL":
        return amount
    raise ValueError(f"Unknown side={side!r}")


async def save_active_order(
    execution_report: dict,
    *,
    algo: str = "",
) -> None:

    db = DataBase()
    async with db.get_session_maker()() as session:

        data = execution_report["data"]

        order_id = int(data["orderId"])
        side = str(data["side"]).upper()

        amount = Decimal(str(data["requestedAmountCcy1"]))
        price = Decimal(str(data["price"]))
        reserved = _calc_reserved(side, amount, price)

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

        merged = await session.merge(order)

        await session.commit()


