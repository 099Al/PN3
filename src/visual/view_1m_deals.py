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
    if isinstance(s, datetime):
        return s.replace(tzinfo=None)
    s = s.strip().replace("T", " ")
    return datetime.fromisoformat(s).replace(tzinfo=None)


def _bucket_start(dt: datetime, freq: str) -> datetime:
    """
    freq: "1min", "5min", "15min", "1h"
    """
    freq = freq.lower().strip()
    if freq.endswith("min"):
        step = int(freq[:-3])
        minute = (dt.minute // step) * step
        return dt.replace(second=0, microsecond=0, minute=minute)
    if freq.endswith("h"):
        step = int(freq[:-1])
        hour = (dt.hour // step) * step
        return dt.replace(second=0, microsecond=0, minute=0, hour=hour)
    raise ValueError(f"Unsupported freq={freq!r}. Use like '1min', '5min', '15min', '1h'.")


def _vwap_agg(points: list[tuple[datetime, float, float]], freq: str) -> tuple[list[datetime], list[float]]:
    """
    points: [(date, price, amount), ...]
    returns: (bucket_dates, vwap_prices)
    """
    buckets: dict[datetime, tuple[float, float]] = {}  # dt -> (sum_px_amt, sum_amt)
    for dt, price, amount in points:
        b = _bucket_start(dt, freq)
        sum_px_amt, sum_amt = buckets.get(b, (0.0, 0.0))
        sum_px_amt += price * amount
        sum_amt += amount
        buckets[b] = (sum_px_amt, sum_amt)

    xs = sorted(buckets.keys())
    ys = []
    for b in xs:
        sum_px_amt, sum_amt = buckets[b]
        ys.append(sum_px_amt / sum_amt if sum_amt else float("nan"))
    return xs, ys


async def _fetch_cex_ticks(session: AsyncSession, *, date_from: datetime, date_to: datetime) -> list[CexHistoryTik]:
    stmt = (
        select(CexHistoryTik)
        .where(CexHistoryTik.date >= date_from)
        .where(CexHistoryTik.date <= date_to)
        .order_by(CexHistoryTik.date.asc())
    )
    return (await session.execute(stmt)).scalars().all()


async def _fetch_my_trades(
    session: AsyncSession, *, date_from: datetime, date_to: datetime, algo_name: str
) -> list[LogDoneTransactions]:
    stmt = (
        select(LogDoneTransactions)
        .where(LogDoneTransactions.date >= date_from)
        .where(LogDoneTransactions.date <= date_to)
        .where(LogDoneTransactions.algo_name == algo_name)
        .order_by(LogDoneTransactions.date.asc())
    )
    return (await session.execute(stmt)).scalars().all()


async def plot_ticks_with_my_trades_and_agg(
    *,
    date_from: str | datetime,
    date_to: str | datetime,
    algo_name: str,
    freq: str = "1min",
) -> None:
    dt_from = _parse_dt(date_from)
    dt_to = _parse_dt(date_to)

    db = DataBase()
    async with db.get_session_maker()() as session:
        ticks = await _fetch_cex_ticks(session, date_from=dt_from, date_to=dt_to)
        my_trades = await _fetch_my_trades(session, date_from=dt_from, date_to=dt_to, algo_name=algo_name)

    # -------------------- 1) Scatter --------------------
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

    my_buy_x, my_buy_y = [], []
    my_sell_x, my_sell_y = [], []

    for tr in my_trades:
        side = str(tr.order_side).lower()
        if "buy" in side:
            my_buy_x.append(tr.date)
            my_buy_y.append(float(tr.price))
        elif "sell" in side:
            my_sell_x.append(tr.date)
            my_sell_y.append(float(tr.price))

    plt.figure(figsize=(14, 6))
    if mkt_buy_x:
        plt.scatter(mkt_buy_x, mkt_buy_y, s=8, alpha=0.25, label="Market BUY")
    if mkt_sell_x:
        plt.scatter(mkt_sell_x, mkt_sell_y, s=8, alpha=0.25, label="Market SELL")

    if my_buy_x:
        plt.scatter(my_buy_x, my_buy_y, s=90, marker="^", label=f"My BUY ({algo_name})")
    if my_sell_x:
        plt.scatter(my_sell_x, my_sell_y, s=90, marker="v", label=f"My SELL ({algo_name})")

    plt.title(f"Scatter: Market ticks + My trades | {dt_from} .. {dt_to} | algo={algo_name}")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -------------------- 2) Aggregation (VWAP by bucket) --------------------
    mkt_buy_pts = []
    mkt_sell_pts = []
    for t in ticks:
        side = (t.type or "").upper()
        amt = float(t.amount)
        pr = float(t.price)
        if side == "BUY":
            mkt_buy_pts.append((t.date, pr, amt))
        elif side == "SELL":
            mkt_sell_pts.append((t.date, pr, amt))

    my_buy_pts = []
    my_sell_pts = []
    for tr in my_trades:
        side = str(tr.order_side).lower()
        amt = float(tr.amount)
        pr = float(tr.price)
        if "buy" in side:
            my_buy_pts.append((tr.date, pr, amt))
        elif "sell" in side:
            my_sell_pts.append((tr.date, pr, amt))

    mkt_buy_ax, mkt_buy_ay = _vwap_agg(mkt_buy_pts, freq=freq) if mkt_buy_pts else ([], [])
    mkt_sell_ax, mkt_sell_ay = _vwap_agg(mkt_sell_pts, freq=freq) if mkt_sell_pts else ([], [])
    my_buy_ax, my_buy_ay = _vwap_agg(my_buy_pts, freq=freq) if my_buy_pts else ([], [])
    my_sell_ax, my_sell_ay = _vwap_agg(my_sell_pts, freq=freq) if my_sell_pts else ([], [])

    plt.figure(figsize=(14, 6))

    if mkt_buy_ax:
        plt.plot(mkt_buy_ax, mkt_buy_ay, label=f"Market BUY VWAP ({freq})")
    if mkt_sell_ax:
        plt.plot(mkt_sell_ax, mkt_sell_ay, label=f"Market SELL VWAP ({freq})")

    # Мои — пунктиром, чтобы было видно на фоне рынка
    if my_buy_ax:
        plt.plot(my_buy_ax, my_buy_ay, linestyle="--", label=f"My BUY VWAP ({freq}) [{algo_name}]")
    if my_sell_ax:
        plt.plot(my_sell_ax, my_sell_ay, linestyle="--", label=f"My SELL VWAP ({freq}) [{algo_name}]")

    plt.title(f"Aggregation: VWAP by {freq} | {dt_from} .. {dt_to} | algo={algo_name}")
    plt.xlabel("Time bucket")
    plt.ylabel("VWAP price")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    asyncio.run(
        plot_ticks_with_my_trades_and_agg(
            date_from="2026-02-10 00:00:00",
            date_to="2026-02-11 23:59:59",
            algo_name="algo_1",
            freq="1min",
        )
    )
