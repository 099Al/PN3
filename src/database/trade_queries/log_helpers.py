from __future__ import annotations

import hashlib
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Balance, Balance_Algo, LogBalance, LogBalance_Algo, LogOrders
from src.trade_utils.date_unix import utcnow_dt


def _normalize_log_unixdate(unix_ms: int) -> int:
    value = int(unix_ms or 0)
    if value > 2_147_483_647:
        return value // 1000
    return value


def _as_order_log_id(*, order_id: int | str, status: str, unix_ms: int) -> str:
    suffix = utcnow_dt().strftime("%Y%m%d%H%M%S%f")
    return f"{order_id}:{status}:{unix_ms}:{suffix}"


def _fit_event_id(event_id: str) -> str:
    value = str(event_id)
    if len(value) <= 20:
        return value

    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    head = value[:11]
    return f"{head}:{digest}"[:20]


def _enum_aware_str(value: object, *, upper: bool = False) -> str:
    raw = value.value if isinstance(value, Enum) else value
    text = str(raw)
    return text.upper() if upper else text.lower()


async def save_balance_snapshot(session: AsyncSession, *, order_id: int | str | None = None) -> int:
    rows = (await session.execute(select(Balance))).scalars().all()
    if not rows:
        return 0

    snapshot_dt = utcnow_dt()
    payload = [
        {
            "curr": row.curr,
            "amount": row.amount or Decimal("0"),
            "reserved": row.reserved,
            "calc_amount": row.calc_amount or Decimal("0"),
            "calc_reserved": row.calc_reserved,
            "snapshot_dt": snapshot_dt,
        }
        for row in rows
    ]
    await session.execute(delete(LogBalance))
    await session.execute(insert(LogBalance), payload)
    return len(payload)


async def save_balance_algo_snapshot(
    session: AsyncSession,
    *,
    algo_name: str,
    order_id: int | str | None = None,
) -> int:
    if not algo_name:
        return 0

    rows = (
        await session.execute(
            select(Balance_Algo)
            .where(Balance_Algo.algo == algo_name)
        )
    ).scalars().all()
    if not rows:
        return 0

    snapshot_dt = utcnow_dt()
    payload = [
        {
            "algo": row.algo,
            "curr": row.curr,
            "allocation_limit": row.allocation_limit or Decimal("0"),
            "amount": row.amount or Decimal("0"),
            "reserved": row.reserved,
            "snapshot_dt": snapshot_dt,
        }
        for row in rows
    ]
    await session.execute(delete(LogBalance_Algo).where(LogBalance_Algo.algo == algo_name))
    await session.execute(insert(LogBalance_Algo), payload)
    return len(payload)


async def log_order_event(
    session: AsyncSession,
    *,
    status: str,
    order_id: int | str,
    side: str,
    date,
    unix_ms: int,
    base: str,
    quote: str,
    amount: Decimal,
    price: Decimal,
    reserved: Decimal,
    fee: Decimal = Decimal("0"),
    reject_reason: Optional[str] = None,
    order_type: str = "limit",
    expire: int = 0,
    full_trade: str = "{}",
    algo: str = "",
    flag_reason: Optional[str] = None,
    event_id: Optional[str] = None,
) -> str:
    event_id = event_id or _as_order_log_id(order_id=order_id, status=status, unix_ms=unix_ms)
    event_id = _fit_event_id(event_id)

    await session.execute(
        insert(LogOrders).values(
            status=_enum_aware_str(status, upper=True),
            id=event_id,
            side=_enum_aware_str(side),
            date=date,
            unixdate=_normalize_log_unixdate(unix_ms),
            base=base,
            quote=quote,
            amount=amount,
            price=price,
            reserved=reserved,
            fee=fee,
            reject_reason=reject_reason,
            order_type=_enum_aware_str(order_type),
            expire=expire,
            full_traid=full_trade,
            algo=algo,
            flag_reason=flag_reason,
        )
    )
    return event_id
