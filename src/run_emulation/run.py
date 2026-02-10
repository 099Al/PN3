import asyncio
from datetime import datetime

from numpy.ma.core import get_mask

from src.run_emulation.balances_init import set_balance

from src.api.emulatorcexio.matcher import emulation_check_orders
from src.database.queries.get_new_history import get_new_data

l_algos = [
    {"name": "algo_1", "usd": 100, "btc": 1},
    {"name": "algo_2", "usd": 0,   "btc": 0.2},
]

t_start = '2023-07-22 15:00:00'

period = 60


def traiding():

    t_start_unix = int(datetime.strptime(t_start, '%Y-%m-%d %H:%M:%S').timestamp())

    curr_unix_time = t_start_unix

    n = 0
    curr_unix_time = curr_unix_time

    while True:
        n = n + 1
        curr_unix_time = curr_unix_time + period

        #В случае эмуляции  проверяем ордера на исполнение
        asyncio.run(emulation_check_orders(curr_unix_time))

        # get data from source and save to DB
        asyncio.run(get_new_data())

        # После установки ордера заносим ответ в active_orders
        # save_active_order_execution_report()



        #check orders
        #check_orders(curr_unix_time)

        #algorithms.algo_1.run()



        if n > 15:
            break



if __name__ == '__main__':

    # asyncio.run(set_balance(l_algos))

    asyncio.run(get_new_data(pair='BTC/USD', unix_curr_time=1690089694 * 1000))

    #traiding()

