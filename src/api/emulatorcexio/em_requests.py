from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Sequence, Optional

from certifi import where
from sqlalchemy import select, desc, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.models_img import Im_CexHistoryTik, Im_ActiveOrder, Im_Balance, Im_Transaction


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

        trades: list[dict] = []
        for (trade_data,) in rows:
            if trade_data:
                trades.append(json.loads(trade_data))
        return trades


    async def get_last_price_at(self, curr_unixdate: int) -> Optional[Decimal]:
        """
        Берём цену последней сделки на момент времени curr_unixdate:
        max(unixdate) where unixdate <= curr_unixdate
        """
        stmt = (
            select(Im_CexHistoryTik.price)
            .where(Im_CexHistoryTik.unixdate <= curr_unixdate)
            .order_by(desc(Im_CexHistoryTik.unixdate))
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalars().first()



    async def get_transactions(self, accountId: str) -> list[Im_Transaction]:
        stmt = (
                select(Im_Transaction)
                .where(Im_Transaction.account_id == accountId)
                .order_by(desc(Im_Transaction.unix_ms))
        )

        rows = (await self.session.execute(stmt)).scalars().all()

        return rows

class EmulatorOrdersRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_active_orders(self, account_id: str) -> list[Im_ActiveOrder]:
        stmt = (
            select(Im_ActiveOrder)
            .where(Im_ActiveOrder.accountId == account_id)
            .order_by(Im_ActiveOrder.unix_date.asc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_balance_amount(self, account_id: str, curr: str) -> Any | None:
        stmt = (
            select(Im_Balance.amount)
            .where(Im_Balance.curr == curr)
            .where(Im_Balance.accountId == account_id)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def upsert_active_order(self, order: Im_ActiveOrder) -> Im_ActiveOrder:
        merged = await self.session.merge(order)
        await self.session.flush()
        return merged

    async def update_balance(self, account_id: str, curr: str, amount_delta, reserved_delta=0) -> None:
        stm = (
            select(Im_Balance)
            .where(Im_Balance.curr == curr)
            .where(Im_Balance.accountId == account_id)
        )
        bal = (await self.session.execute(stm)).scalar_one_or_none()
        if bal is None:
            bal = Im_Balance(account_id=account_id, curr=curr, amount=0, reserved=0)
            self.session.add(bal)

        if amount_delta:
            bal.amount = (bal.amount or 0) + amount_delta
        if reserved_delta:
            bal.reserved = (bal.reserved or 0) + reserved_delta

    async def get_active_order(self, order_id: int) -> Optional[Im_ActiveOrder]:
        res = await self.session.execute(
            select(Im_ActiveOrder).where(Im_ActiveOrder.id == order_id)
        )
        return res.scalar_one_or_none()

    async def delete_active_order(self, order: Im_ActiveOrder) -> None:
        await self.session.delete(order)



class EmulatorBalanceRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_balance_curr(self, account_id: str, curr: str) -> Optional[Im_Balance]:
        stmt = (
            select(Im_Balance)
            .where(Im_Balance.accountId == account_id)
            .where(Im_Balance.curr == curr)
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def get_balance(self, account_id: str) -> list[Im_Balance]:
        stmt = (
            select(Im_Balance)
            .where(Im_Balance.accountId == account_id)
        )
        return (await self.session.execute(stmt)).all()

    async def ensure_row(self, account_id: str, curr: str) -> Im_Balance:
        row = await self.get_balance_curr(account_id, curr)
        if row is not None:
            return row

        row = Im_Balance(
            accountId=account_id,
            curr=curr,
            amount=Decimal("0"),
            reserved=Decimal("0"),
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def update_balance(
            self,
            *,
            account_id: str,
            curr: str,
            amount_delta: Decimal = Decimal("0"),
            reserved_delta: Decimal = Decimal("0"),
    ) -> None:
        """
        amount += amount_delta
        reserved = coalesce(reserved,0) + reserved_delta
        """
        await self.ensure_row(account_id, curr)

        stmt = (
            update(Im_Balance)
            .where(Im_Balance.accountId == account_id)
            .where(Im_Balance.curr == curr)
            .values(
                {
                    Im_Balance.amount: Im_Balance.amount + amount_delta,
                    Im_Balance.reserved: func.coalesce(Im_Balance.reserved, 0) + reserved_delta,
                }
            )
        )
        await self.session.execute(stmt)

    async def set_balance(
            self,
            *,
            account_id: str,
            curr: str,
            amount: Decimal,
            reserved: Optional[Decimal] = None,
    ) -> None:
        """
        Установить значения явно (upsert-like).
        """
        row = await self.ensure_row(account_id, curr)
        row.amount = amount
        if reserved is not None:
            row.reserved = reserved
        await self.session.flush()
