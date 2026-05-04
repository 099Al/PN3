import asyncio
from datetime import datetime, timezone
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.algos.registry import (
    build_algorithm,
    get_algorithm_definition,
    get_registered_capital_allocations,
)
from src.api.emulatorcexio.emulator_api import EmulatorApi
from src.run_emulation.balances_init import set_balance
from src.run_emulation.settings import EMULATION_SETTINGS

from src.api.emulatorcexio.matcher import emulation_check_orders
from src.database.trade_queries.get_new_history import get_new_data


t_start = EMULATION_SETTINGS["t_start"]
period = int(EMULATION_SETTINGS["period"])
steps = int(EMULATION_SETTINGS.get("steps", 15))
period_ms = period * 1000


def get_selected_algo_name() -> str:
    selected_algo_name = str(EMULATION_SETTINGS["selected_algo_name"])
    get_algorithm_definition(selected_algo_name)
    return selected_algo_name


def get_selected_account_id() -> str | None:
    account_id = str(
        get_algorithm_definition(get_selected_algo_name()).default_config.get("account_id", "")
    ).strip()
    return account_id or None


api = EmulatorApi(
    EMULATION_SETTINGS["api_user"],
    EMULATION_SETTINGS["api_start_time"],
    account_id=get_selected_account_id(),
)


def build_selected_algo():
    return build_algorithm(get_selected_algo_name())


async def trading():
    algo = build_selected_algo()

    t_start_unix = int(
        datetime.strptime(t_start, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp() * 1000
    )

    curr_unix_time = t_start_unix
    n = 0

    while True:
        n += 1
        curr_unix_time += period_ms

        await emulation_check_orders(curr_unix_time)
        await get_new_data(pair="BTC/USD", unix_curr_time=curr_unix_time)
        await algo.run(curr_unix_time)

        if n >= steps:
            break


async def main():
    await set_balance(get_registered_capital_allocations())
    await trading()


if __name__ == "__main__":
    asyncio.run(main())
