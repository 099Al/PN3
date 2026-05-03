from __future__ import annotations

from decimal import Decimal


FIRST_ALGO_NAME = "algo_1"
FIRST_ALGO_BALANCE_LIMIT = {"name": FIRST_ALGO_NAME, "usd": 100, "btc": 0}


FIRST_ALGO_CONFIG = {
    "account_id": "trade_test",
    "algo_name": FIRST_ALGO_NAME,
    "pair": "BTC/USD",
    "amount": Decimal("0.005"),
    "price1": Decimal("30000"),
    "price2": Decimal("31000"),
    "position_curr": "BTC",
}
