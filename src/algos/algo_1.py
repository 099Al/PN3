from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect import DataBase
from src.database.models import CexHistoryTik, ActiveOrder
from src.database.trade_queries.set_orders import algo_set_order


def _d(x) -> Decimal:
    return Decimal(str(x))


@dataclass
class Algo_1:
    """
    Простейшая логика:
    - если нет позиции -> BUY по price1
    - если есть позиция -> SELL по price2

    position_curr: какая валюта считается "позиционной" (обычно base, например BTC)
    """

    # TODO: заменить методы на метьоды из Api и trade request. Чтобы коррекетро считался баланс

    account_id: str
    algo_name: str
    pair: str  # "BTC/USD"
    amount: Decimal
    price1: Decimal  # BUY limit
    price2: Decimal  # SELL limit
    position_curr: str = "BTC"

    async def _last_price(self, session: AsyncSession) -> Optional[Decimal]:
        stmt = (
            select(CexHistoryTik.price)
            .order_by(desc(CexHistoryTik.unixdate))
            .limit(1)
        )
        return (await session.execute(stmt)).scalar_one_or_none()

    async def _has_active_order(self, session: AsyncSession, side: str) -> bool:
        side = side.lower()  # в ActiveOrder enum хранит buy/sell
        stmt = (
            select(ActiveOrder.orderId)
            .where(ActiveOrder.accountId == self.account_id)
            .where(ActiveOrder.algo == self.algo_name)
            .where(ActiveOrder.side == side)
            .limit(1)
        )
        return (await session.execute(stmt)).scalar_one_or_none() is not None

    async def _get_position_amount(self, session: AsyncSession) -> Decimal:
        # Если у тебя позиция хранится в Balance — лучше читать оттуда.
        # Здесь упрощённо: считаем позицию = amount в Balance по position_curr.
        from src.database.models import Balance
        row = await session.get(Balance, self.position_curr)
        if row is None:
            return Decimal("0")
        return _d(row.calc_amount if row.calc_amount is not None else row.amount)

    async def run(self) -> None:
        db = DataBase()
        async with db.get_session_maker()() as session:
            last_price = await self._last_price(session)
            if last_price is None:
                return

            pos = await self._get_position_amount(session)

            # ====== BUY logic ======
            if pos <= Decimal("0"):
                # чтобы не дублировать BUY
                if await self._has_active_order(session, "buy"):
                    return

                # можно добавить фильтр: last_price <= price1
                if last_price <= self.price1:
                    await algo_set_order(
                        amount=self.amount,
                        price=self.price1,
                        sell_buy="BUY",
                        accountId=self.account_id,
                        algo_name=self.algo_name,
                    )
                return

            # ====== SELL logic ======
            # pos > 0
            if await self._has_active_order(session, "sell"):
                return

            # можно добавить фильтр: last_price >= price2
            if last_price >= self.price2:
                await algo_set_order(
                    amount=self.amount,
                    price=self.price2,
                    sell_buy="SELL",
                    accountId=self.account_id,
                    algo_name=self.algo_name,
                )
