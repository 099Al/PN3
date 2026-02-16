# balances_init_async.py
from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Mapping, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect import DataBase
from src.database.models import Balance, Balance_Algo

from src.trade_utils.util_decimal import _d2 as _d

async def init_balance(
    session: AsyncSession,
    *,
    usd_amount: Decimal | int | str = Decimal("100"),
    usd_reserved: Decimal | int | str = Decimal("0"),
    btc_amount: Decimal | int | str = Decimal("1"),
    btc_reserved: Decimal | int | str = Decimal("0"),
    l_algos: Iterable[Mapping[str, Any]] = (),
) -> None:
    """
    1) Заносит стартовые значения в таблицу balance:
       USD: amount=100, reserved=0
       BTC: amount=1,   reserved=0

    2) Заносит список алгоритмов в balance_algo:
       - usd и btc пишет в amount_limit
       - amount оставляет 0 (по умолчанию), reserved = 0

    3) Перед вставкой проверяет, что сумма лимитов по USD (amount_limit)
       по всем алгоритмам не превышает balance.USD.amount.
    """

    usd_amount = _d(usd_amount)
    usd_reserved = _d(usd_reserved)
    btc_amount = _d(btc_amount)
    btc_reserved = _d(btc_reserved)

    # --- 1) upsert balance ---
    await _upsert_balance(session, "USD", usd_amount, usd_reserved)
    await _upsert_balance(session, "BTC", btc_amount, btc_reserved)

    # flush, чтобы гарантировать наличие строк перед проверками и FK
    await session.flush()

    # --- 2) проверка лимитов по USD ---
    total_usd_limit = Decimal("0")
    for a in l_algos:
        total_usd_limit += _d(a.get("usd", 0))

    bal_usd = await session.get(Balance, "USD")
    if bal_usd is None:
        raise RuntimeError("Balance USD not found (unexpected after upsert).")

    if total_usd_limit > _d(bal_usd.amount):
        raise ValueError(
            f"Сумма лимитов USD по алгоритмам ({total_usd_limit}) "
            f"превышает баланс USD ({bal_usd.amount})."
        )

    # Если надо — аналогичная проверка по BTC:
    # total_btc_limit = sum((_d(a.get("btc", 0)) for a in l_algos), Decimal("0"))
    # bal_btc = await session.get(Balance, "BTC")
    # if total_btc_limit > _d(bal_btc.amount):
    #     raise ValueError(
    #         f"Сумма лимитов BTC по алгоритмам ({total_btc_limit}) "
    #         f"превышает баланс BTC ({bal_btc.amount})."
    #     )

    # --- 3) upsert balance_algo ---
    for a in l_algos:
        algo_name = a.get("name")
        if not algo_name:
            raise ValueError(f"В l_algos есть элемент без 'name': {a}")

        usd_limit = _d(a.get("usd", 0))
        btc_limit = _d(a.get("btc", 0))

        await _upsert_balance_algo(
            session,
            algo=str(algo_name),
            curr="USD",
            amount_limit=usd_limit,
        )
        await _upsert_balance_algo(
            session,
            algo=str(algo_name),
            curr="BTC",
            amount_limit=btc_limit,
        )

    await session.commit()


async def _upsert_balance(
    session: AsyncSession,
    curr: str,
    amount: Decimal,
    reserved: Decimal,
) -> None:
    row = await session.get(Balance, curr)
    if row is None:
        session.add(Balance(curr=curr, amount=amount, reserved=reserved))
    else:
        row.amount = amount
        row.reserved = reserved


async def _upsert_balance_algo(
    session: AsyncSession,
    *,
    algo: str,
    curr: str,
    amount_limit: Decimal,
) -> None:
    """
    Upsert строки balance_algo по составному PK: (algo, curr).
    amount_limit обновляем, amount оставляем как есть (или 0 при создании),
    reserved держим не-NULL (0 при создании; при NULL в БД — приводим к 0).
    """
    row = await session.get(Balance_Algo, (algo, curr))
    if row is None:
        session.add(
            Balance_Algo(
                algo=algo,
                curr=curr,
                amount_limit=amount_limit,
                amount=Decimal("0"),
                reserved=Decimal("0"),
            )
        )
    else:
        row.amount_limit = amount_limit
        if row.reserved is None:
            row.reserved = Decimal("0")


async def set_balance(l_algos):

    db = DataBase()

    async_sessionmaker = db.get_session_maker()

    async with async_sessionmaker() as session:
        await init_balance(session, l_algos=l_algos)