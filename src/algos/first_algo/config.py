from __future__ import annotations

from decimal import Decimal


FIRST_ALGO_NAME = "algo_1"
FIRST_ALGO_CAPITAL_ALLOCATION = {"name": FIRST_ALGO_NAME, "usd": 99, "btc": 0.005}
FIRST_ALGO_INITIAL_BALANCE = {
    "USD": {"amount": 150, "reserved": 2},
    "BTC": {"amount": 0.005, "reserved": 0.001},
}


FIRST_ALGO_CONFIG = {
    "account_id": "trade_test",
    "algo_name": FIRST_ALGO_NAME,
    "pair": "BTC/USD",
    "amount": Decimal("0.005"),
    "price1": Decimal("30000"),
    "price2": Decimal("31000"),
    "position_curr": "BTC",
}
