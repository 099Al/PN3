import asyncio
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from sqlalchemy import select

from src.database.connect import DataBase
from src.database.models import LogBalance


async def plot_log_balance(curr: str, date_from: datetime, date_to: datetime):
    db = DataBase()

    async with db.get_session_maker()() as session:
        stmt = (
            select(LogBalance)
            .where(LogBalance.curr == curr)
            .where(LogBalance.snapshot_dt >= date_from)
            .where(LogBalance.snapshot_dt <= date_to)
            .order_by(LogBalance.snapshot_dt)
        )

        result = await session.execute(stmt)
        rows = result.scalars().all()

    if not rows:
        print("No data found")
        return

    df = pd.DataFrame([
        {
            "snapshot_dt": r.snapshot_dt,
            "amount": float(r.amount or 0),
            "reserved": float(r.reserved or 0),
            "calc_amount": float(r.calc_amount or 0),
            "calc_reserved": float(r.calc_reserved or 0),
        }
        for r in rows
    ])

    df.sort_values("snapshot_dt", inplace=True)

    plt.figure()
    plt.plot(df["snapshot_dt"], df["amount"])
    plt.plot(df["snapshot_dt"], df["reserved"])
    plt.plot(df["snapshot_dt"], df["calc_amount"])
    plt.plot(df["snapshot_dt"], df["calc_reserved"])

    plt.xlabel("Time")
    plt.ylabel("Balance")
    plt.title(f"Balance history for {curr}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    asyncio.run(
        plot_log_balance(
            curr="USD",
            date_from=datetime(2026, 1, 1),
            date_to=datetime(2026, 12, 31),
        )
    )
