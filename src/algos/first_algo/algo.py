from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_UP
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.algos.base import BaseAlgorithm
from src.database.connect import DataBase
from src.database.models import ActiveOrder, CexHistoryTik, LogOrders
from src.database.trade_queries.set_orders import algo_set_order
from src.trade_parameters import TradeConfig
from src.trade_utils.trade import X_for_buyBTC


def _d(x) -> Decimal:
    return Decimal(str(x))


@dataclass
class Algo_1(BaseAlgorithm):
    """Alternating one-order strategy: BUY on price1, then SELL on price2."""

    price1: Decimal
    price2: Decimal
    buy_fee_percent: Decimal = _d(TradeConfig.BUY_FEE)
    sell_fee_percent: Decimal = _d(TradeConfig.SELL_FEE)
    min_profit_quote: Decimal = Decimal("0.05")

    async def _last_price(self, session: AsyncSession, unix_curr_time: int | None = None) -> Optional[Decimal]:
        stmt = select(CexHistoryTik.price)
        if unix_curr_time is not None:
            stmt = stmt.where(CexHistoryTik.date <= datetime.utcfromtimestamp(unix_curr_time / 1000))
        stmt = stmt.order_by(desc(CexHistoryTik.unixdate)).limit(1)
        return (await session.execute(stmt)).scalar_one_or_none()

    async def _has_active_order(self, session: AsyncSession) -> bool:
        stmt = (
            select(ActiveOrder.orderId)
            .where(ActiveOrder.accountId == self.account_id)
            .where(ActiveOrder.algo == self.algo_name)
            .limit(1)
        )
        return (await session.execute(stmt)).scalar_one_or_none() is not None

    async def _get_position_amount(self, session: AsyncSession) -> Decimal:
        from src.database.models import Balance

        row = await session.get(Balance, self.position_curr)
        if row is None:
            return Decimal("0")
        return _d(row.calc_amount if row.calc_amount is not None else row.amount)

    async def _last_filled_buy_price(self, session: AsyncSession) -> Optional[Decimal]:
        stmt = (
            select(LogOrders.price)
            .where(LogOrders.algo == self.algo_name)
            .where(LogOrders.status == "DONE")
            .where(LogOrders.side == "buy")
            .order_by(desc(LogOrders.date), desc(LogOrders.id))
            .limit(1)
        )
        return (await session.execute(stmt)).scalar_one_or_none()

    def _min_profitable_sell_price(self, buy_price: Decimal, sell_amount: Decimal) -> Decimal:
        buy_cost = _d(X_for_buyBTC(sell_amount, buy_price, float(self.buy_fee_percent)))
        target_net_quote = buy_cost + self.min_profit_quote
        sell_multiplier = Decimal("1") - (self.sell_fee_percent / Decimal("100"))
        if sell_multiplier <= Decimal("0"):
            raise ValueError("sell_fee_percent must be lower than 100")

        min_price = target_net_quote / (sell_amount * sell_multiplier)
        return min_price.quantize(Decimal("0.01"), rounding=ROUND_UP)

    async def run(self, unix_curr_time: int | None = None) -> None:
        db = DataBase()
        async with db.get_session_maker()() as session:
            last_price = await self._last_price(session, unix_curr_time)
            if last_price is None:
                return

            if await self._has_active_order(session):
                return

            pos = await self._get_position_amount(session)
            if pos <= Decimal("0"):
                if last_price <= self.price1:
                    await algo_set_order(
                        amount=self.amount,
                        price=self.price1,
                        sell_buy="BUY",
                        accountId=self.account_id,
                        algo_name=self.algo_name,
                        unix_curr_time=unix_curr_time,
                    )
                return

            sell_amount = min(pos, self.amount)
            if sell_amount <= Decimal("0"):
                return

            last_buy_price = await self._last_filled_buy_price(session)
            reference_buy_price = _d(last_buy_price) if last_buy_price is not None else self.price1
            profitable_sell_price = self._min_profitable_sell_price(reference_buy_price, sell_amount)
            sell_price = max(self.price2, profitable_sell_price)

            if last_price >= sell_price:
                await algo_set_order(
                    amount=sell_amount,
                    price=sell_price,
                    sell_buy="SELL",
                    accountId=self.account_id,
                    algo_name=self.algo_name,
                    unix_curr_time=unix_curr_time,
                )
