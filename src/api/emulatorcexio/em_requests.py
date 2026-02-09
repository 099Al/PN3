from __future__ import annotations

import json
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.models_img import Im_CexHistoryTik, Im_ActiveOrder, Im_Balance


class EmulatorHistoryRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_trades_before(self, unix_ms: int, limit: int = 1000) -> list[dict]:
        stmt = (
            select(Im_CexHistoryTik.trade_data)
            .where(Im_CexHistoryTik.unixdate <= unix_ms)
            .order_by(Im_CexHistoryTik.unixdate.desc())
            .limit(limit)
        )
        rows: Sequence[tuple[str | None]] = (await self.session.execute(stmt)).all()

        # trade_data у тебя Text/str с json
        trades: list[dict] = []
        for (trade_data,) in rows:
            if trade_data:
                trades.append(json.loads(trade_data))
        return trades


class EmulatorOrdersRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_active_orders(self) -> list[Im_ActiveOrder]:
        stmt = select(Im_ActiveOrder).order_by(Im_ActiveOrder.unix_date.asc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_balance_amount(self, curr: str) -> Any | None:
        stmt = select(Im_Balance.amount).where(Im_Balance.curr == curr)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def upsert_active_order(self, order: Im_ActiveOrder) -> Im_ActiveOrder:
        merged = await self.session.merge(order)
        await self.session.flush()
        return merged

    async def update_balance(self, curr: str, amount_delta, reserved_delta=0) -> None:
        bal = (await self.session.execute(select(Im_Balance).where(Im_Balance.curr == curr))).scalar_one_or_none()
        if bal is None:
            bal = Im_Balance(curr=curr, amount=0, reserved=0)
            self.session.add(bal)

        if amount_delta:
            bal.amount = (bal.amount or 0) + amount_delta
        if reserved_delta:
            bal.reserved = (bal.reserved or 0) + reserved_delta
