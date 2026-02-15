from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.models_img import Im_ActiveOrder, Im_CexHistoryTik, Im_Balance
# предположим, что ты уже переделал модель транзакций:
from src.database.models.models_img import Im_Transaction  # или путь где ты её держишь
from src.trade_utils.date_unix import dt_from_unix_ms
from src.trade_utils.util_decimal import D0


@dataclass(frozen=True)
class Fill:
    tid: str
    unix_ms: int
    price: Decimal
    side: str  # 'BUY'|'SELL' из history


class EmulatorMatchRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_active_orders(self, account_id: str) -> list[Im_ActiveOrder]:
        stmt = (
            select(Im_ActiveOrder)
            .where(Im_ActiveOrder.accountId == account_id)
            .order_by(Im_ActiveOrder.unix_date.asc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def find_fill_for_order(self, order: Im_ActiveOrder, until_unix_ms: int) -> Optional[Fill]:
        """
        Логика:
        - LIMIT SELL исполняется, когда появляется сделка BUY по цене >= order.price
        - LIMIT BUY  исполняется, когда появляется сделка SELL по цене <= order.price

        + учитываем side тика (buy/sell) из истории.
        """
        side = str(order.side).upper()

        if side == "SELL":
            stmt = (
                select(Im_CexHistoryTik)
                .where(Im_CexHistoryTik.unixdate > order.unix_date)
                .where(Im_CexHistoryTik.unixdate <= until_unix_ms)
                .where(Im_CexHistoryTik.side.ilike("BUY"))
                .where(Im_CexHistoryTik.price >= order.price)
                .order_by(Im_CexHistoryTik.unixdate.asc())
                .limit(1)
            )
        elif side == "BUY":
            stmt = (
                select(Im_CexHistoryTik)
                .where(Im_CexHistoryTik.unixdate > order.unix_date)
                .where(Im_CexHistoryTik.unixdate <= until_unix_ms)
                .where(Im_CexHistoryTik.side.ilike("SELL"))
                .where(Im_CexHistoryTik.price <= order.price)
                .order_by(Im_CexHistoryTik.unixdate.asc())
                .limit(1)
            )
        else:
            raise ValueError(f"Unknown order side: {order.side}")

        row = (await self.session.execute(stmt)).scalars().first()
        if not row:
            return None

        return Fill(tid=row.tid, unix_ms=row.unixdate, price=row.price, side=str(row.side).upper())

    async def delete_active_order(self, order_id: int) -> None:
        await self.session.execute(delete(Im_ActiveOrder).where(Im_ActiveOrder.id == order_id))

    async def get_balance(self, account_id: str, curr: str) -> Optional[Im_Balance]:
        stmt = select(Im_Balance).where(Im_Balance.curr == curr).where(Im_Balance.accountId == account_id)
        return (await self.session.execute(stmt)).scalars().first()

    async def apply_balance_delta(self, account_id: str, *, curr: str, amount_delta: Decimal = D0, reserved_delta: Decimal = D0) -> None:
        """
        Обновляем balance.amount и balance.reserved (reserved может быть NULL).
        Делается через ORM объект (проще и безопаснее).
        """
        bal = await self.get_balance(account_id, curr=curr)
        if bal is None:
            # если валюты нет — создаём (по желанию можно запрещать)
            bal = Im_Balance(account_id=account_id, curr=curr, amount=D0, reserved=D0)
            self.session.add(bal)
            await self.session.flush()

        bal.amount = (bal.amount or D0) + amount_delta
        bal.reserved = (bal.reserved or D0) + reserved_delta

    async def add_transaction(
        self,
        *,
        transaction_id: str,
        order_id: int,
        unix_ms: int,
        type: str,
        currency: str,
        amount: Decimal,
        details: str,
        account_id: str = "",
    ) -> None:
        tx = Im_Transaction(
            transaction_id=transaction_id,
            order_id=order_id,
            unix_ms=unix_ms,
            timestamp=dt_from_unix_ms(unix_ms),
            type=type,
            currency=currency,
            amount=amount,
            details=details,
            account_id=account_id,
        )
        self.session.add(tx)
