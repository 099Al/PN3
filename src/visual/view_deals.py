from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

import matplotlib.pyplot as plt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect import DataBase
from src.database.models import CexHistoryTik, LogDoneTransactions


def _parse_dt(s: str | datetime) -> datetime:
    """
    Принимает:
      - datetime
      - "2026-02-01 12:00:00"
      - "2026-02-01T12:00:00"
    Важно: в БД у тебя DateTime WITHOUT TZ (naive UTC), поэтому возвращаем naive datetime.
    """
    if isinstance(s, datetime):
        return s.replace(tzinfo=None)
    s = s.strip().replace("T", " ")
    return datetime.fromisoformat(s).replace(tzinfo=None)


async def _fetch_cex_ticks(
    session: AsyncSession,
    *,
    date_from: datetime,
    date_to: datetime,
) -> list[CexHistoryTik]:
    stmt = (
        select(CexHistoryTik)
        .where(CexHistoryTik.date >= date_from)
        .where(CexHistoryTik.date <= date_to)
        .order_by(CexHistoryTik.date.asc())
    )
    return (await session.execute(stmt)).scalars().all()


async def _fetch_my_trades(
    session: AsyncSession,
    *,
    date_from: datetime,
    date_to: datetime,
    algo_name: str,
) -> list[LogDoneTransactions]:
    stmt = (
        select(LogDoneTransactions)
        .where(LogDoneTransactions.date >= date_from)
        .where(LogDoneTransactions.date <= date_to)
        .where(LogDoneTransactions.algo_name == algo_name)
        .order_by(LogDoneTransactions.date.asc())
    )
    return (await session.execute(stmt)).scalars().all()


async def plot_ticks_with_my_trades(
    *,
    date_from: str | datetime,
    date_to: str | datetime,
    algo_name: str,
) -> None:
    dt_from = _parse_dt(date_from)
    dt_to = _parse_dt(date_to)

    db = DataBase()
    async with db.get_session_maker()() as session:
        ticks = await _fetch_cex_ticks(session, date_from=dt_from, date_to=dt_to)
        my_trades = await _fetch_my_trades(session, date_from=dt_from, date_to=dt_to, algo_name=algo_name)

    # -------- Market ticks split --------
    mkt_buy_x, mkt_buy_y = [], []
    mkt_sell_x, mkt_sell_y = [], []

    for t in ticks:
        side = (t.type or "").upper()
        if side == "BUY":
            mkt_buy_x.append(t.date)
            mkt_buy_y.append(float(t.price))
        elif side == "SELL":
            mkt_sell_x.append(t.date)
            mkt_sell_y.append(float(t.price))

    # -------- My trades split (LogDoneTransactions) --------
    my_buy_x, my_buy_y = [], []
    my_sell_x, my_sell_y = [], []

    for tr in my_trades:
        side = str(tr.order_side).lower()  # enum or string -> normalize
        if "buy" in side:
            my_buy_x.append(tr.date)
            my_buy_y.append(float(tr.price))
        elif "sell" in side:
            my_sell_x.append(tr.date)
            my_sell_y.append(float(tr.price))

    # -------- Plot --------
    plt.figure(figsize=(14, 6))

    # Market
    if mkt_buy_x:
        plt.scatter(mkt_buy_x, mkt_buy_y, s=8, alpha=0.25, label="Market BUY", c="tab:green")
    if mkt_sell_x:
        plt.scatter(mkt_sell_x, mkt_sell_y, s=8, alpha=0.25, label="Market SELL", c="tab:red")

    # My trades overlay (bigger markers)
    if my_buy_x:
        plt.scatter(my_buy_x, my_buy_y, s=90, marker="^", label=f"My BUY ({algo_name})", c="limegreen")
    if my_sell_x:
        plt.scatter(my_sell_x, my_sell_y, s=90, marker="v", label=f"My SELL ({algo_name})", c="darkred")

    plt.title(f"Ticks (market) + My trades overlay | {dt_from} .. {dt_to} | algo={algo_name}")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    asyncio.run(
        plot_ticks_with_my_trades(
            date_from="2026-02-10 00:00:00",
            date_to="2026-02-11 23:59:59",
            algo_name="algo_1",
        )
    )
