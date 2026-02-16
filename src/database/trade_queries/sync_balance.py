from decimal import Decimal
from typing import Optional

from sqlalchemy import select

from src.api.provider import ApiProvider
from src.database.connect import DataBase
from src.database.models import Balance
from src.trade_utils.util_decimal import _d


async def sync_balance(account_id):

    api = ApiProvider.get(account_id=account_id)

    response = await api.account_status(account_id=account_id)

    if response.get("ok") != "ok":
        raise RuntimeError(f"account_status failed: {response}")

    balances = (
        response.get("data", {})
        .get("balancesPerAccounts", {})
        .get(account_id, {})
    )

    db = DataBase()

    async with db.get_session_maker()() as session:

        for curr, data in balances.items():

            amount = _d(data.get("balanceAvailable"))
            reserved = _d(data.get("balanceOnHold"))

            stmt = select(Balance).where(Balance.curr == curr)
            row = (await session.execute(stmt)).scalars().first()

            if row is None:
                row = Balance(
                    curr=curr,
                    amount=amount,
                    reserved=reserved,
                )
                session.add(row)
            else:
                row.amount = amount
                row.reserved = reserved

        await session.commit()


async def compare_balance_ratio(curr: str) -> Optional[Decimal]:
    """
    Возвращает коэффициент совпадения amount и calc_amount.
    1.0 = 100% совпадение
    0.0 = полностью разные / один из них 0
    None = если записи нет
    """

    db = DataBase()

    async with db.get_session_maker()() as session:
        stmt = select(Balance).where(Balance.curr == curr)
        row = (await session.execute(stmt)).scalars().first()

        if row is None:
            return None

        amount = _d(row.amount)
        calc_amount = _d(row.calc_amount)

        # оба нули → считаем 100%
        if amount == 0 and calc_amount == 0:
            return Decimal("1")

        # один из нулей → 0%
        if amount == 0 or calc_amount == 0:
            return Decimal("0")

        smaller = min(amount, calc_amount)
        bigger = max(amount, calc_amount)

        return (smaller / bigger).quantize(Decimal("0.00000001"))