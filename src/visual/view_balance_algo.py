import asyncio
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from sqlalchemy import select

from src.database.connect import DataBase
from src.database.models import LogBalance_Algo


async def plot_log_balance_algo(
    algo: str,
    curr: str,
    date_from: datetime,
    date_to: datetime,
):
    db = DataBase()

    async with db.get_session_maker()() as session:
        stmt = (
            select(LogBalance_Algo)
            .where(LogBalance_Algo.algo == algo)
            .where(LogBalance_Algo.curr == curr)
            .where(LogBalance_Algo.snapshot_dt >= date_from)
            .where(LogBalance_Algo.snapshot_dt <= date_to)
            .order_by(LogBalance_Algo.snapshot_dt)
        )

        result = await session.execute(stmt)
        rows = result.scalars().all()

    if not rows:
        print("No data found")
        return

    df = pd.DataFrame([
        {
            "snapshot_dt": r.snapshot_dt,
            "amount_limit": float(r.amount_limit or 0),
            "amount": float(r.amount or 0),
            "reserved": float(r.reserved or 0),
        }
        for r in rows
    ])

    df.sort_values("snapshot_dt", inplace=True)

    plt.figure()
    plt.plot(df["snapshot_dt"], df["amount_limit"])
    plt.plot(df["snapshot_dt"], df["amount"])
    plt.plot(df["snapshot_dt"], df["reserved"])

    plt.xlabel("Time")
    plt.ylabel("Balance")
    plt.title(f"Algo balance history | {algo} | {curr}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    asyncio.run(
        plot_log_balance_algo(
            algo="algo_1",
            curr="USD",
            date_from=datetime(2026, 1, 1),
            date_to=datetime(2026, 12, 31),
        )
    )
