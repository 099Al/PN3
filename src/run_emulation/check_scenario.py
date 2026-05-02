from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass

from sqlalchemy import func, select

from src.algos.registry import (
    get_algorithm_definition,
    get_registered_algorithm_names,
    get_registered_balance_limits,
)
from src.database.connect import DataBase
from src.database.models import ActiveOrder, Balance_Algo, LogDoneTransactions
from src.run_emulation.balances_init import set_balance
from src.run_emulation.settings import EMULATION_SETTINGS


@dataclass
class AlgoStateSummary:
    algo_name: str
    active_orders: int
    balance_algo_rows: int
    trade_logs: int


def get_selected_algo_name() -> str:
    algo_name = str(EMULATION_SETTINGS["selected_algo_name"])
    get_algorithm_definition(algo_name)
    return algo_name


async def init_balances_for_registered_algorithms() -> None:
    await set_balance(get_registered_balance_limits())


async def collect_algo_state(algo_name: str) -> AlgoStateSummary:
    db = DataBase()
    async with db.get_session_maker()() as session:
        active_orders = (
            await session.execute(
                select(func.count()).select_from(ActiveOrder).where(ActiveOrder.algo == algo_name)
            )
        ).scalar_one()
        balance_algo_rows = (
            await session.execute(
                select(func.count()).select_from(Balance_Algo).where(Balance_Algo.algo == algo_name)
            )
        ).scalar_one()
        trade_logs = (
            await session.execute(
                select(func.count())
                .select_from(LogDoneTransactions)
                .where(LogDoneTransactions.algo_name == algo_name)
            )
        ).scalar_one()

    return AlgoStateSummary(
        algo_name=algo_name,
        active_orders=int(active_orders or 0),
        balance_algo_rows=int(balance_algo_rows or 0),
        trade_logs=int(trade_logs or 0),
    )


async def run_check_scenario() -> dict:
    selected_algo_name = get_selected_algo_name()
    registered_algorithms = get_registered_algorithm_names()

    await init_balances_for_registered_algorithms()
    selected_algo_state = await collect_algo_state(selected_algo_name)

    return {
        "selected_algo_name": selected_algo_name,
        "registered_algorithms": registered_algorithms,
        "registered_balance_limits": get_registered_balance_limits(),
        "selected_algo_state": asdict(selected_algo_state),
        "second_algo_ready": len(registered_algorithms) > 1,
        "note": (
            "A second emulation run can be validated after a second algorithm "
            "is implemented and registered."
        ),
    }


if __name__ == "__main__":
    result = asyncio.run(run_check_scenario())
    print(result)
