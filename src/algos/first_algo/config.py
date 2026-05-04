from __future__ import annotations

from decimal import Decimal


FIRST_ALGO_NAME = "algo_1"
FIRST_ALGO_CAPITAL_ALLOCATION = {"name": FIRST_ALGO_NAME, "usd": 99, "btc": 0.005}
FIRST_ALGO_INITIAL_BALANCE = {
    "USD": {"amount": 99, "reserved": 0},
    "BTC": {"amount": 0, "reserved": 0},
}


FIRST_ALGO_CONFIG = {
    "account_id": "trade_test",
    "algo_name": FIRST_ALGO_NAME,
    "pair": "BTC/USD",
    "amount": Decimal("0.001"),
    "price1": Decimal("29877.3"),
    "price2": Decimal("29880.5"),
    "buy_fee_percent": Decimal("0.005"),
    "sell_fee_percent": Decimal("0.005"),
    "min_profit_quote": Decimal("0.001"),
    "position_curr": "BTC",
}
