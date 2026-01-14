import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.database.connect import DataBase
from src.run_traiding.balances_init import set_balance


l_algos = [
    {"name": "algo_1", "usd": 100, "btc": 1},
    {"name": "algo_2", "usd": 0,   "btc": 0.2},
]




if __name__ == '__main__':

    asyncio.run(set_balance(l_algos))
