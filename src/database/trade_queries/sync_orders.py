from __future__ import annotations

import re
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.provider import ApiProvider
from src.database.connect import DataBase
from src.database.models import ActiveOrder, Balance, Balance_Algo, LogDoneTransactions, LogBalance, LogBalance_Algo
from src.trade_utils.date_unix import utcnow_dt


def _d(x: Any) -> Decimal:
    return Decimal(str(x or 0))


# details: "Commission for orderId=2690215 for up112344963"
_RE_ORDERID = re.compile(r"\borderId=(\d+)\b")


def _extract_order_id(details: Optional[str]) -> Optional[int]:
    if not details:
        return None
    m = _RE_ORDERID.search(details)
    return int(m.group(1)) if m else None


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
                amount_limit=Decimal("0"),
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
    """
    Меняет:
      amount/reserved
      calc_amount/calc_reserved (если переданы; иначе = delta_amount/delta_reserved)
    """
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

async def _save_balance_snapshot(session, order_id=None) -> int:
    """
    Копирует текущие значения из Balance в LogBalance как snapshot.
    Возвращает кол-во записей.
    """
    snapshot_dt = utcnow_dt()

    rows = (await session.execute(select(Balance))).scalars().all()

    if not rows:
        return 0

    for b in rows:
        session.add(
            LogBalance(
                curr=b.curr,
                amount=b.amount or Decimal("0"),
                reserved=b.reserved,
                calc_amount=b.calc_amount or Decimal("0"),
                calc_reserved=b.calc_reserved,
                order_id=order_id,
                snapshot_dt=snapshot_dt,
            )
        )
    await session.commit()
    return len(rows)


async def _save_balance_algo_snapshot(session, algo_name, order_id=None) -> int:
    """
    Копирует текущие значения из Balance в LogBalance как snapshot.
    Возвращает кол-во записей.
    """
    snapshot_dt = utcnow_dt()

    rows = (await session.execute(
        select(Balance_Algo)
        .where(Balance_Algo.algo == algo_name)
    )).scalars().all()

    if not rows:
        return 0

    for b in rows:
        session.add(
            LogBalance_Algo(
                algo=b.algo,
                curr=b.curr,
                amount=b.amount or Decimal("0"),
                reserved=b.reserved,
                calc_amount=b.calc_amount or Decimal("0"),
                calc_reserved=b.calc_reserved,
                order_id=order_id,
                snapshot_dt=snapshot_dt,
            )
        )
    await session.commit()
    return len(rows)




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
    """
    В БД enum sidetype хранит 'buy'/'sell'
    """
    s = (side or "").lower()
    if s not in ("buy", "sell"):
        raise ValueError(f"Bad side value: {side!r}")
    return s


async def sync_orders(*, account_id: str) -> dict:
    api = ApiProvider.get(account_id=account_id)

    # 1) open_orders source
    src = await api.open_orders()
    if src.get("ok") != "ok":
        raise RuntimeError(f"open_orders failed: {src}")

    src_orders = src.get("data", []) or []
    src_ids = {int(o["orderId"]) for o in src_orders if o.get("orderId") is not None}

    # 2) transaction history source (1 раз)
    tx_res = await api.transaction_history(account_id=account_id)
    if tx_res.get("ok") != "ok":
        raise RuntimeError(f"transaction_history failed: {tx_res}")

    txs = tx_res.get("data", []) or []

    # индексируем транзакции по orderId из details
    tx_by_oid: dict[int, list[dict]] = {}
    for t in txs:
        oid = _extract_order_id(t.get("details"))
        if oid is None:
            continue
        tx_by_oid.setdefault(oid, []).append(t)

    db = DataBase()
    async with db.get_session_maker()() as session:
        db_rows = (await session.execute(select(ActiveOrder))).scalars().all()
        db_ids = {int(o.orderId) for o in db_rows}

        missing_ids = sorted(db_ids - src_ids)
        if not missing_ids:
            return {"ok": "ok", "removed": 0, "processed_orderIds": []}

        processed: list[int] = []

        for oid in missing_ids:
            order: Optional[ActiveOrder] = (
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

            # --- A) release reserved (и обычные, и calc) ---
            if reserved != 0:
                if side == "buy":
                    # reserved в quote
                    await _balance_apply(
                        session,
                        curr=quote,
                        delta_amount=reserved,
                        delta_reserved=-reserved,
                    )
                    await _balance_algo_apply(
                        session,
                        algo=algo,
                        curr=quote,
                        delta_amount=reserved,
                        delta_reserved=-reserved,
                    )
                else:  # sell
                    # reserved в base
                    await _balance_apply(
                        session,
                        curr=base,
                        delta_amount=reserved,
                        delta_reserved=-reserved,
                    )
                    await _balance_algo_apply(
                        session,
                        algo=algo,
                        curr=base,
                        delta_amount=reserved,
                        delta_reserved=-reserved,
                    )

            # --- B) применяем транзакции как delta (signed amount) ---
            # также подготовим commission_sum (обычно в USD) для логирования
            commission_sum = sum(
                (_d(t["amount"]) for t in order_txs if str(t.get("type")).lower() == "commission"),
                start=Decimal("0"),
            )
            # commission в примере отрицательная -> в лог лучше положительное число комиссии
            commission_abs = abs(commission_sum)

            price = _d(order.price)

            for t in order_txs:  #запись в транзакции на одну сделку состоит из 3х частей (BTC, USD, commission)
                curr = str(t.get("currency"))
                amt = _d(t.get("amount"))
                typ = str(t.get("type") or "").lower()

                # Баланс меняем для любого типа (trade/commission)
                await _balance_apply(session, curr=curr, delta_amount=amt)
                await _balance_algo_apply(session, algo=algo, curr=curr, delta_amount=amt)


                await _save_balance_snapshot(session, order_id=oid)
                await _save_balance_algo_snapshot(session, algo_name=algo, order_id=oid)


                # --- C) логируем совершённые сделки ---
                # В LogDoneTransactions пишем только trade (как "сделки"),
                # commission записываем полем commission (одинаковое для обеих trade-строк ордера)
                if typ == "trade":
                    # timestamp приходит как ISO Z -> можно хранить как "сейчас" или распарсить
                    # тут берём unix_date из order.unix_date (у тебя BIGINT ms)
                    log_row = LogDoneTransactions(
                        date=order.date,
                        unix_date=int(order.unix_date // 1000) if order.unix_date else 0,  # если в секундах нужно
                        curr=curr,
                        amount=amt,
                        commission=commission_abs,
                        price=price,
                        algo_name=algo,
                        tid=str(t.get("transactionId")),
                        order_side=side,  # enum sidetype принимает 'buy'/'sell'
                        sys_date=func.now(),  # или utcnow_dt()
                    )
                    session.add(log_row)

            # --- D) удаляем ордер ---
            await session.execute(delete(ActiveOrder).where(ActiveOrder.orderId == oid))

            processed.append(oid)

        await session.commit()

        return {"ok": "ok", "removed": len(processed), "processed_orderIds": processed}
