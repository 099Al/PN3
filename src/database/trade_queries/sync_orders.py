from __future__ import annotations

import re
from datetime import timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.provider import ApiProvider
from src.database.connect import DataBase
from src.database.models import ActiveOrder, Balance, Balance_Algo, LogDoneTransactions
from src.database.trade_queries.log_helpers import log_order_event, save_balance_algo_snapshot, save_balance_snapshot
from src.trade_utils.date_unix import parse_iso_z_to_naive


def _d(x: Any) -> Decimal:
    return Decimal(str(x or 0))


_RE_ORDERID = re.compile(r"\borderId=(\d+)\b")


def _extract_order_id(details: Optional[str]) -> Optional[int]:
    if not details:
        return None
    match = _RE_ORDERID.search(details)
    return int(match.group(1)) if match else None


async def _ensure_balance_row(session: AsyncSession, curr: str) -> None:
    res = await session.execute(select(Balance.curr).where(Balance.curr == curr))
    if res.scalar_one_or_none() is None:
        session.add(
            Balance(
                curr=curr,
                amount=Decimal("0"),
                reserved=Decimal("0"),
                calc_amount=Decimal("0"),
                calc_reserved=Decimal("0"),
            )
        )
        await session.flush()


async def _ensure_balance_algo_row(session: AsyncSession, *, algo: str, curr: str) -> None:
    res = await session.execute(
        select(Balance_Algo.algo).where(Balance_Algo.algo == algo, Balance_Algo.curr == curr)
    )
    if res.scalar_one_or_none() is None:
        session.add(
            Balance_Algo(
                algo=algo,
                curr=curr,
                allocation_limit=Decimal("0"),
                amount=Decimal("0"),
                reserved=Decimal("0"),
            )
        )
        await session.flush()


async def _balance_apply(
    session: AsyncSession,
    *,
    curr: str,
    delta_amount: Decimal = Decimal("0"),
    delta_reserved: Decimal = Decimal("0"),
    delta_calc_amount: Optional[Decimal] = None,
    delta_calc_reserved: Optional[Decimal] = None,
) -> None:
    await _ensure_balance_row(session, curr)

    if delta_calc_amount is None:
        delta_calc_amount = delta_amount
    if delta_calc_reserved is None:
        delta_calc_reserved = delta_reserved

    stmt = (
        update(Balance)
        .where(Balance.curr == curr)
        .values(
            {
                Balance.amount: Balance.amount + delta_amount,
                Balance.reserved: func.coalesce(Balance.reserved, 0) + delta_reserved,
                Balance.calc_amount: func.coalesce(Balance.calc_amount, 0) + delta_calc_amount,
                Balance.calc_reserved: func.coalesce(Balance.calc_reserved, 0) + delta_calc_reserved,
            }
        )
    )
    await session.execute(stmt)


async def _balance_algo_apply(
    session: AsyncSession,
    *,
    algo: str,
    curr: str,
    delta_amount: Decimal = Decimal("0"),
    delta_reserved: Decimal = Decimal("0"),
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


def _side_enum_value(side: str) -> str:
    value = (side or "").lower()
    if value not in ("buy", "sell"):
        raise ValueError(f"Bad side value: {side!r}")
    return value


def _event_dt_and_unix_ms(order: ActiveOrder, order_txs: list[dict]) -> tuple:
    event_date = order.date
    event_unix_ms = int(order.unix_date or 0)

    if order_txs:
        event_date = max(
            (parse_iso_z_to_naive(str(tx["timestamp"])) for tx in order_txs if tx.get("timestamp")),
            default=order.date,
        )
        event_unix_ms = int(event_date.replace(tzinfo=timezone.utc).timestamp() * 1000)

    return event_date, event_unix_ms


async def sync_orders(*, account_id: str) -> dict:
    api = ApiProvider.get(account_id=account_id)

    src = await api.open_orders()
    if src.get("ok") != "ok":
        raise RuntimeError(f"open_orders failed: {src}")

    src_orders = src.get("data", []) or []
    src_ids = {int(order["orderId"]) for order in src_orders if order.get("orderId") is not None}

    tx_res = await api.transaction_history(account_id=account_id)
    if tx_res.get("ok") != "ok":
        raise RuntimeError(f"transaction_history failed: {tx_res}")

    txs = tx_res.get("data", []) or []
    tx_by_oid: dict[int, list[dict]] = {}
    for tx in txs:
        order_id = _extract_order_id(tx.get("details"))
        if order_id is None:
            continue
        tx_by_oid.setdefault(order_id, []).append(tx)

    db = DataBase()
    async with db.get_session_maker()() as session:
        db_rows = (await session.execute(select(ActiveOrder))).scalars().all()
        db_ids = {int(order.orderId) for order in db_rows}

        missing_ids = sorted(db_ids - src_ids)
        if not missing_ids:
            return {"ok": "ok", "removed": 0, "processed_orderIds": []}

        processed: list[int] = []

        for oid in missing_ids:
            order = (
                (await session.execute(select(ActiveOrder).where(ActiveOrder.orderId == oid)))
                .scalars()
                .first()
            )
            if order is None:
                continue

            side = _side_enum_value(order.side)
            base = order.base
            quote = order.quote
            reserved = _d(order.reserved)
            algo = order.algo or ""
            order_txs = tx_by_oid.get(oid, [])
            order_status = "DONE" if order_txs else "CANCELED"

            if reserved != 0:
                if side == "buy":
                    await _balance_apply(session, curr=quote, delta_amount=reserved, delta_reserved=-reserved)
                    await _balance_algo_apply(
                        session,
                        algo=algo,
                        curr=quote,
                        delta_amount=reserved,
                        delta_reserved=-reserved,
                    )
                else:
                    await _balance_apply(session, curr=base, delta_amount=reserved, delta_reserved=-reserved)
                    await _balance_algo_apply(
                        session,
                        algo=algo,
                        curr=base,
                        delta_amount=reserved,
                        delta_reserved=-reserved,
                    )

            commission_sum = sum(
                (_d(tx["amount"]) for tx in order_txs if str(tx.get("type")).lower() == "commission"),
                start=Decimal("0"),
            )
            commission_abs = abs(commission_sum)
            price = _d(order.price)

            for tx in order_txs:
                curr = str(tx.get("currency"))
                amount = _d(tx.get("amount"))
                tx_type = str(tx.get("type") or "").lower()

                await _balance_apply(session, curr=curr, delta_amount=amount)
                await _balance_algo_apply(session, algo=algo, curr=curr, delta_amount=amount)

                if tx_type == "trade":
                    session.add(
                        LogDoneTransactions(
                            date=order.date,
                            unix_date=int(order.unix_date // 1000) if order.unix_date else 0,
                            curr=curr,
                            amount=amount,
                            commission=commission_abs,
                            price=price,
                            algo_name=algo,
                            tid=str(tx.get("transactionId")),
                            order_side=side,
                            sys_date=func.now(),
                        )
                    )

            event_date, event_unix_ms = _event_dt_and_unix_ms(order, order_txs)
            await log_order_event(
                session,
                status=order_status,
                order_id=order.orderId,
                side=order.side,
                date=event_date,
                unix_ms=event_unix_ms,
                base=order.base,
                quote=order.quote,
                amount=_d(order.amount),
                price=price,
                reserved=reserved,
                fee=commission_abs,
                order_type=order.order_type,
                full_trade=order.full_traid,
                algo=algo,
                flag_reason=f"TRADING_{order_status}",
                event_id=f"{order.orderId}:{order_status}",
            )
            await save_balance_snapshot(session, order_id=oid)
            await save_balance_algo_snapshot(session, algo_name=algo, order_id=oid)

            await session.execute(delete(ActiveOrder).where(ActiveOrder.orderId == oid))
            processed.append(oid)

        await session.commit()
        return {"ok": "ok", "removed": len(processed), "processed_orderIds": processed}
