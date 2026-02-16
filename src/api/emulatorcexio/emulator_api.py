from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional, Dict

from sqlalchemy import select, desc

from src.api.emulatorcexio.order_state import build_active_order, calc_quote_needed_for_buy
from src.database.models import Im_Transaction
from src.database.trade_queries.set_orders import save_active_order
# твои константы
from src.trade_parameters import TradeConfig
from src.trade_utils.date_unix import _format_iso_z
from src.trade_utils.util_decimal import _fmt8, _d

BASE_MIN = TradeConfig.BASE_MIN

# если хочешь сохранить генератор id как сейчас
from perfomance.cache.values import ValuesOrder
from src.api.base_api import BaseApi, JsonDict, PairsList
from src.api.emulatorcexio.em_requests import EmulatorHistoryRepo, EmulatorOrdersRepo, EmulatorBalanceRepo
from src.database.connect import DataBase


class EmulatorApi(BaseApi):
    def __init__(self, username: str, unix_curr_time: int, account_id=None):
        self.username = username
        self.unix_curr_time = unix_curr_time
        self.db = DataBase()
        self.account_id = account_id

    # -------- market data --------
    async def trade_history(self, pair: str = "BTC-USD") -> JsonDict:
        async with self.db.get_session_maker()() as session:
            repo = EmulatorHistoryRepo(session)
            trades = await repo.get_trades_before(self.unix_curr_time, limit=1000)
            return {"ok": "ok", "data": {"pageSize": 1000, "trades": trades}}

    async def ticker(self, pairs: PairsList = ["BTC/USD"]) -> JsonDict:
        # если нужно — можно эмулировать из последнего тика в im_cex_history_tik
        return {"ok": "not_implemented"}

    async def candles(
        self,
        dataType: Optional[str],
        pair: str = "BTC-USD",
        limit: Optional[int] = None,
        resolution: str = "1h",
        fromDT: Optional[str] = None,
        toDT: Optional[str] = None,
    ) -> JsonDict:
        return {"ok": "not_implemented"}

    async def currencies_info(self) -> JsonDict:
        return {"ok": "not_implemented"}

    async def order_book(self, params: Optional[JsonDict] = None) -> JsonDict:
        return {"ok": "not_implemented"}

    # -------- orders --------
    async def open_orders(self, params: Optional[JsonDict] = None) -> JsonDict:
        async with self.db.get_session_maker()() as session:
            repo = EmulatorOrdersRepo(session)
            orders = await repo.list_active_orders()

            data = []
            for o in orders:
                data.append(
                    {
                        "orderId": o.id,
                        "clientOrderId": o.accountId,
                        "clientId": self.username,
                        "accountId": self.account_id,
                        "status": "NEW",
                        "statusIsFinal": False,
                        "currency1": o.base,
                        "currency2": o.quote,
                        "side": o.side,
                        "orderType": o.order_type,
                        "timeInForce": "GTC",
                        "comment": None,
                        "rejectCode": None,
                        "rejectReason": None,
                        "initialOnHoldAmountCcy1": str(o.amount),
                        "initialOnHoldAmountCcy2": None,
                        "executedAmountCcy1": None,
                        "executedAmountCcy2": None,
                        "requestedAmountCcy1": str(o.amount),
                        "requestedAmountCcy2": None,
                        "feeAmount": "0.00000000",
                        "feeCurrency": o.quote,
                        "price": str(o.price),
                        "averagePrice": None,
                        "clientCreateTimestamp": o.unix_date,
                        "serverCreateTimestamp": None,
                        "lastUpdateTimestamp": None,
                        "expireTime": None,
                        "effectiveTime": None,
                    }
                )

            return {"ok": "ok", "data": data}

    async def sell_limit_order(
        self,
        amount: Any,
        price: Any,
        clientOrderId: Optional[str] = None,
        market: str = "BTC/USD",
    ) -> JsonDict:
        amount = Decimal(str(amount))
        price = Decimal(str(price))

        base, quote = market.split("/")

        # min check
        if amount < Decimal(str(BASE_MIN)):
            return self._reject_min_amount(amount)

        async with self.db.get_session_maker()() as session:
            repo = EmulatorOrdersRepo(session)

            bal_amount = await repo.get_balance_amount(base)
            bal_amount = Decimal(str(bal_amount or 0))

            if bal_amount < amount:
                return self._reject_insufficient()

            # create active order
            order = build_active_order(
                unix_ms=self.unix_curr_time,
                base=base,
                quote=quote,
                side="SELL",
                amount=amount,
                price=price,
                order_type="Limit",
            )

            order = await repo.upsert_active_order(order)  # сохраняем в БД

            # reserve base (пример: уменьшаем amount, увеличиваем reserved)
            await repo.update_balance(curr=base, amount_delta=-order.reserved, reserved_delta=order.reserved)

            res = self._new_order_response(order_id=order.id, side="SELL", base=base, quote=quote, amount=amount, price=price, clientOrderId=clientOrderId)

            # await session.flush()
            await session.commit()

            return res

    async def buy_limit_order(
        self,
        amount: Any,
        price: Any,
        clientOrderId: Optional[str] = None,
        market: str = "BTC/USD",
    ) -> JsonDict:
        amount = Decimal(str(amount))
        price = Decimal(str(price))

        base, quote = market.split("/")

        if amount < Decimal(str(BASE_MIN)):
            return self._reject_min_amount(amount)

        need_quote = calc_quote_needed_for_buy(amount, price)

        async with self.db.get_session_maker()() as session:
            repo = EmulatorOrdersRepo(session)

            bal_quote = await repo.get_balance_amount(quote)
            bal_quote = Decimal(str(bal_quote or 0))

            if bal_quote < need_quote:
                return self._reject_insufficient()

            order = build_active_order(
                unix_ms=self.unix_curr_time,
                base=base,
                quote=quote,
                side="BUY",
                amount=amount,
                price=price,
                order_type="Limit",
            )
            order = await repo.upsert_active_order(order)

            # reserve quote
            await repo.update_balance(curr=quote, amount_delta=-need_quote, reserved_delta=need_quote)

            res = self._new_order_response(order_id=order.id, side="BUY", base=base, quote=quote, amount=amount, price=price, clientOrderId=clientOrderId)

            await session.commit()

            return res

    async def cancel_order(self, OrderId: Any) -> JsonDict:
        order_id = int(OrderId)
        async with self.db.get_session_maker()() as session:
            repo = EmulatorOrdersRepo(session)
            order = await repo.get_active_order(order_id)
            if order is None:
                # можно вернуть ok (как многие биржи) или ошибку
                return {"ok": "ok", "data": {}}

            side = (order.side or "").upper()
            reserved = Decimal(str(order.reserved or 0))

            # 1) вернуть резерв обратно в баланс
            if reserved != 0:
                if side == "SELL":
                    # SELL резервируется base (BTC)
                    await repo.update_balance(
                        curr=order.base,
                        amount_delta=reserved,
                        reserved_delta=-reserved,
                    )
                elif side == "BUY":
                    # BUY резервируется quote (USD)
                    await repo.update_balance(
                        curr=order.quote,
                        amount_delta=reserved,
                        reserved_delta=-reserved,
                    )
                else:
                    # если внезапно side не BUY/SELL — лучше не делать кривые движения
                    raise ValueError(f"Unknown side={order.side!r} for order_id={order_id}")

            # 2) удалить ордер из активных
            await repo.delete_active_order(order)

            await session.commit()

            # формат как у api.cancel_order(...)
            return {"ok": "ok", "data": {}}



    async def cancel_client_order(self, clientOrderId: Any) -> JsonDict:
        return {"ok": "not_implemented"}

    async def cancel_all_order(self) -> JsonDict:
        return {"ok": "not_implemented"}

    async def set_order(self, amount, price, sell_buy, orderType="Limit", market="BTC/USD", clientOrderId=None) -> JsonDict:
        if clientOrderId is None:
            unix_dt = int(datetime.now().timestamp() * 1000)
            clientOrderId = str(unix_dt)

        if sell_buy == "BUY":
            return await self.buy_limit_order(amount=amount, price=price, clientOrderId=clientOrderId, market=market)
        return await self.sell_limit_order(amount=amount, price=price, clientOrderId=clientOrderId, market=market)

    async def get_order(self, order_id: str) -> JsonDict:
        return {"ok": "not_implemented"}

    async def account_status(self, accountId=None, curr_unixdate: Optional[int] = None) -> JsonDict:
        converted = "USD"
        t = int(curr_unixdate if curr_unixdate is not None else self.unix_curr_time)

        async with self.db.get_session_maker()() as session:
            bal_repo = EmulatorBalanceRepo(session)
            hist_repo = EmulatorHistoryRepo(session)

            last_price = await hist_repo.get_last_price_at(t)
            last_price = _d(last_price)  # если None -> 0

            rows = await bal_repo.get_balance(self.username)

            per_account: Dict[str, Dict[str, dict]] = {}

            for r in rows:
                acc = r.accountId or self.username
                per_account.setdefault(acc, {})

                amount = _d(r.amount)
                on_hold = _d(r.reserved)
                total = amount + on_hold

                # конвертация в USD по цене на момент t
                if r.curr == converted:
                    converted_val = total
                elif r.curr == "BTC" and converted == "USD":
                    converted_val = total * last_price
                else:
                    converted_val = Decimal("0")

                per_account[acc][r.curr] = {
                    "balance": _fmt8(total),
                    "balanceOnHold": _fmt8(on_hold),
                    "balanceAvailable": _fmt8(amount),
                    "balanceInConvertedCurrency": _fmt8(converted_val),
                }

            return {
                "ok": "ok",
                "data": {
                    "convertedCurrency": converted,
                    "balancesPerAccounts": per_account,
                },
            }

    async def transaction_history(self, accountId: str) -> JsonDict:
        async with self.db.get_session_maker()() as session:
            repo = EmulatorHistoryRepo(session)
            rows = await repo.get_transactions(self.username)

            data = []
            for row in rows:
                data.append(
                    {
                        "transactionId": row.transaction_id,
                        "timestamp": _format_iso_z(row.timestamp),
                        "accountId": row.account_id,
                        "type": row.type,
                        "amount": str(row.amount),
                        "details": row.details,
                        "currency": row.currency,
                    }
                )

            return {"ok": "ok", "data": data}



    # -------- helpers --------
    def _transact_time(self) -> str:
        # формат времени
        ts_ms = self.unix_curr_time + 2000
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts_ms % 1000:03d}Z"


    def _new_order_response(self, *, order_id: int, side: str, base: str, quote: str, amount: Decimal, price: Decimal, clientOrderId) -> JsonDict:
        return {
            "ok": "ok",
            "data": {
                "messageType": "executionReport",
                "clientId": self.username,
                "orderId": order_id,
                "clientOrderId": clientOrderId,
                "accountId": self.account_id,
                "status": "NEW",
                "currency1": base,
                "currency2": quote,
                "side": side,
                "executedAmountCcy1": "0.00000000",
                "executedAmountCcy2": "0.00000000",
                "requestedAmountCcy1": str(amount),
                "requestedAmountCcy2": None,
                "orderType": "Limit",
                "timeInForce": "GTC",
                "comment": None,
                "executionType": "New",
                "executionId": f"{self.unix_curr_time}_X_{order_id}",
                "transactTime": self._transact_time(),
                "expireTime": None,
                "effectiveTime": None,
                "price": str(price),
                "averagePrice": None,
                "feeAmount": "0.00000000",
                "feeCurrency": quote,

                #доп. поля. Не нужны
                "clientCreateTimestamp": self.unix_curr_time,
                "serverCreateTimestamp": self.unix_curr_time + 1000,
                "lastUpdateTimestamp": self.unix_curr_time + 10000,
            },
        }

    def _reject_min_amount(self, amount: Decimal) -> JsonDict:
        return {
            "ok": "ok",
            "data": {
                "messageType": "executionReport",
                "clientId": self.username,
                "orderId": None,
                "clientOrderId": str(self.unix_curr_time),
                "accountId": self.account_id,
                "status": "REJECTED",
                "currency1": None,
                "currency2": None,
                "side": None,
                "executedAmountCcy1": "0.00000000",
                "executedAmountCcy2": "0.00000000",
                "requestedAmountCcy1": str(amount),
                "requestedAmountCcy2": None,
                "orderType": "Limit",
                "timeInForce": "GTC",
                "comment": None,
                "executionType": "Rejected",
                "executionId": None,
                "transactTime": self._transact_time(),
                "expireTime": None,
                "effectiveTime": None,
                "price": None,
                "averagePrice": None,
                "feeAmount": None,
                "feeCurrency": None,
                "orderRejectReason": "min order amount failed",
                "rejectCode": 414,
                "rejectReason": "min order amount failed",
            },
        }

    def _reject_insufficient(self) -> JsonDict:
        return {
            "ok": "ok",
            "data": {
                "messageType": "executionReport",
                "clientId": self.username,
                "orderId": None,
                "clientOrderId": str(self.unix_curr_time),
                "accountId": self.account_id,
                "status": "REJECTED",
                "executionType": "Rejected",
                "orderRejectReason": '{"code":403,"reason":"Insufficient funds"}',
                "rejectCode": 403,
                "rejectReason": "Insufficient funds",
                "transactTime": self._transact_time(),
            },
        }



async def main():


    api = EmulatorApi('test_user', 1689533488861, account_id='trade_test')
    # res = asyncio.run(api.buy_limit_order(0.005,30000))

    # res = asyncio.run(api.open_orders())

    res = await api.set_order(0.005, 30000, "BUY")
    await save_active_order(res, algo="algo_1")

    #res = await api.cancel_order(14)

    print(res)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())