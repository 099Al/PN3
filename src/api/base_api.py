# src/base_api.py
from __future__ import annotations

from typing import Protocol, Any, Optional, Dict, List, Literal

JsonDict = Dict[str, Any]
PairsList = List[str]


class BaseApi(Protocol):

    def api_call(self, command: str, param: Optional[JsonDict] = None) -> JsonDict: ...

    # PUBLIC COMMANDS
    def currencies_info(self) -> JsonDict: ...
    def candles(
        self,
        dataType: Optional[str],
        pair: str = "BTC-USD",
        limit: Optional[int] = None,
        resolution: str = "1h",
        fromDT: Optional[str] = None,
        toDT: Optional[str] = None,
    ) -> JsonDict: ...
    def trade_history(self, pair: str = "BTC-USD") -> JsonDict: ...
    def ticker(self, pairs: PairsList = ["BTC/USD"]) -> JsonDict: ...

    # PRIVATE COMMANDS
    def account_status(self) -> JsonDict: ...
    def get_myfee(self) -> JsonDict: ...
    def transaction_history(self) -> JsonDict: ...
    def open_orders(self, params: Optional[JsonDict] = None) -> JsonDict: ...
    def get_order(self, order_id: str) -> JsonDict: ...
    def order_book(self, params: JsonDict = {"pair": "BTC-USD"}) -> JsonDict: ...

    def set_order(
        self,
        amount: Any,
        price: Any,
        sell_buy: Literal["SELL", "BUY"],
        orderType: str = "Limit",
        market: str = "BTC/USD",
        clientOrderId: Optional[str] = None,
    ) -> JsonDict: ...

    def sell_limit_order(
        self,
        amount: Any,
        price: Any,
        clientOrderId: Optional[str] = None,
        market: str = "BTC/USD",
    ) -> JsonDict: ...

    def buy_limit_order(
        self,
        amount: Any,
        price: Any,
        clientOrderId: Optional[str] = None,
        market: str = "BTC/USD",
    ) -> JsonDict: ...

    def cancel_order(self, OrderId: Any) -> JsonDict: ...
    def cancel_client_order(self, clientOrderId: Any) -> JsonDict: ...
    def cancel_all_order(self) -> JsonDict: ...

    # CUSTOM COMMANDS
    def limit_info(self, pairs: str = "BTC/USD") -> JsonDict: ...
    def current_prices(self, pair: str = "BTC/USD") -> JsonDict: ...
    def fee(self, pair: str = "BTC/USD") -> Any: ...
