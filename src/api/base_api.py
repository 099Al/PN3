from __future__ import annotations

from typing import Protocol, Any, Optional, Dict, List, Literal

JsonDict = Dict[str, Any]
PairsList = List[str]


class BaseApi(Protocol):

    async def api_call(self, command: str, param: Optional[JsonDict] = None) -> JsonDict: ...

    # PUBLIC COMMANDS
    async def currencies_info(self) -> JsonDict: ...
    async def candles(
        self,
        dataType: Optional[str],
        pair: str = "BTC-USD",
        limit: Optional[int] = None,
        resolution: str = "1h",
        fromDT: Optional[str] = None,
        toDT: Optional[str] = None,
    ) -> JsonDict: ...
    async def trade_history(self, pair: str = "BTC-USD") -> JsonDict: ...
    async def ticker(self, pairs: PairsList = ["BTC/USD"]) -> JsonDict: ...

    # PRIVATE COMMANDS
    async def account_status(self, account_id: str) -> JsonDict: ...
    async def get_myfee(self) -> JsonDict: ...
    async def transaction_history(self) -> JsonDict: ...
    async def open_orders(self, params: Optional[JsonDict] = None) -> JsonDict: ...
    async def get_order(self, order_id: str) -> JsonDict: ...
    async def order_book(self, params: JsonDict = {"pair": "BTC-USD"}) -> JsonDict: ...

    async def set_order(
        self,
        amount: Any,
        price: Any,
        sell_buy: Literal["SELL", "BUY"],
        orderType: str = "Limit",
        market: str = "BTC/USD",
        clientOrderId: Optional[str] = None,
    ) -> JsonDict: ...

    async def sell_limit_order(
        self,
        amount: Any,
        price: Any,
        clientOrderId: Optional[str] = None,
        market: str = "BTC/USD",
    ) -> JsonDict: ...

    async def buy_limit_order(
        self,
        amount: Any,
        price: Any,
        clientOrderId: Optional[str] = None,
        market: str = "BTC/USD",
    ) -> JsonDict: ...

    async def cancel_order(self, OrderId: Any) -> JsonDict: ...
    async def cancel_client_order(self, clientOrderId: Any) -> JsonDict: ...
    async def cancel_all_order(self) -> JsonDict: ...

    # CUSTOM COMMANDS
    async def limit_info(self, pairs: str = "BTC/USD") -> JsonDict: ...
    async def current_prices(self, pair: str = "BTC/USD") -> JsonDict: ...
    async def fee(self, pair: str = "BTC/USD") -> Any: ...
