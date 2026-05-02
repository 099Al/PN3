import asyncio
from datetime import datetime
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.algos.registry import (
    build_algorithm,
    get_algorithm_definition,
    get_registered_balance_limits,
)
from src.api.emulatorcexio.emulator_api import EmulatorApi
from src.run_emulation.balances_init import set_balance
from src.run_emulation.settings import EMULATION_SETTINGS

from src.api.emulatorcexio.matcher import emulation_check_orders
from src.database.trade_queries.get_new_history import get_new_data


t_start = EMULATION_SETTINGS["t_start"]
period = int(EMULATION_SETTINGS["period"])

api = EmulatorApi(
    EMULATION_SETTINGS["api_user"],
    EMULATION_SETTINGS["api_start_time"],
)


def get_selected_algo_name() -> str:
    selected_algo_name = str(EMULATION_SETTINGS["selected_algo_name"])
    get_algorithm_definition(selected_algo_name)
    return selected_algo_name


def build_selected_algo():
    return build_algorithm(get_selected_algo_name())


def traiding():
    algo = build_selected_algo()

    t_start_unix = int(datetime.strptime(t_start, '%Y-%m-%d %H:%M:%S').timestamp())

    curr_unix_time = t_start_unix

    n = 0
    curr_unix_time = curr_unix_time

    while True:
        n = n + 1
        curr_unix_time = curr_unix_time + period

        #В случае эмуляции  проверяем ордера на исполнение
        asyncio.run(emulation_check_orders(curr_unix_time))

        # 2) подгружаем тики и пишем в CexHistoryTik
        asyncio.run(get_new_data(pair="BTC/USD", unix_curr_time=curr_unix_time))

        # 3) запускаем алгоритм (ставит BUY/SELL через algo_set_order)
        asyncio.run(algo.run())

        #check orders
        #check_orders(curr_unix_time)

        #algorithms.algo_1.run()



        if n > 15:
            break



if __name__ == '__main__':

    # asyncio.run(set_balance(get_registered_balance_limits()))

    # asyncio.run(get_new_data(pair='BTC/USD', unix_curr_time=1690089694 * 1000))

    l_orders = asyncio.run(api.open_orders())

    print(l_orders)

    #traiding()

