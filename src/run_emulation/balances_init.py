# balances_init_async.py
from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Mapping, Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.algos.registry import get_algorithm_definition, get_registered_initial_balance_algos
from src.database.connect import DataBase
from src.database.models import (
    ActiveOrder,
    Balance,
    Balance_Algo,
    Im_ActiveOrder,
    Im_Balance,
    Im_Transaction,
    LogBalance_Algo,
    LogBalance,
    LogDoneTransactions,
    LogOrders,
)
from src.run_emulation.settings import EMULATION_SETTINGS

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
       - usd и btc пишет в allocation_limit
       - amount оставляет 0 (по умолчанию), reserved = 0

    3) Перед вставкой проверяет, что сумма лимитов по USD (allocation_limit)
       по всем алгоритмам не превышает balance.USD.amount.
    """

    usd_amount = _d(usd_amount)
    usd_reserved = _d(usd_reserved)
    btc_amount = _d(btc_amount)
    btc_reserved = _d(btc_reserved)

    await _truncate_table(LogBalance_Algo.__tablename__, cascade=True)
    await _truncate_table(LogBalance.__tablename__, cascade=True)
    await _truncate_table(LogDoneTransactions.__tablename__, cascade=True)
    await _truncate_table(LogOrders.__tablename__, cascade=True)
    await _truncate_table(ActiveOrder.__tablename__, cascade=True)
    await _truncate_table("emulator.im_active_orders", cascade=True)
    await _truncate_table("emulator.im_transactions", cascade=True)

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
            allocation_limit=usd_limit,
            amount=_d(a.get("USD_amount", usd_limit)),
            reserved=_d(a.get("USD_reserved", 0)),
        )
        await _upsert_balance_algo(
            session,
            algo=str(algo_name),
            curr="BTC",
            allocation_limit=btc_limit,
            amount=_d(a.get("BTC_amount", btc_limit)),
            reserved=_d(a.get("BTC_reserved", 0)),
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
        session.add(
            Balance(
                curr=curr,
                amount=amount,
                reserved=reserved,
                calc_amount=amount,
                calc_reserved=reserved,
            )
        )
    else:
        row.amount = amount
        row.reserved = reserved
        row.calc_amount = amount
        row.calc_reserved = reserved


async def _upsert_emulator_balance(
    session: AsyncSession,
    *,
    account_id: str,
    curr: str,
    amount: Decimal,
    reserved: Decimal,
) -> None:
    row = await session.get(Im_Balance, curr)
    if row is None:
        session.add(
            Im_Balance(
                accountId=account_id,
                curr=curr,
                amount=amount,
                reserved=reserved,
            )
        )
    else:
        row.accountId = account_id
        row.amount = amount
        row.reserved = reserved


async def _upsert_balance_algo(
    session: AsyncSession,
    *,
    algo: str,
    curr: str,
    allocation_limit: Decimal,
    amount: Decimal,
    reserved: Decimal,
) -> None:
    """
    Upsert строки balance_algo по составному PK: (algo, curr).
    allocation_limit обновляем, amount оставляем как есть (или 0 при создании),
    reserved держим не-NULL (0 при создании; при NULL в БД — приводим к 0).
    """
    row = await session.get(Balance_Algo, (algo, curr))
    if row is None:
        session.add(
            Balance_Algo(
                algo=algo,
                curr=curr,
                allocation_limit=allocation_limit,
                amount=amount,
                reserved=reserved,
            )
        )
    else:
        row.allocation_limit = allocation_limit
        row.amount = amount
        row.reserved = reserved

async def _truncate_table(table_name: str, *, cascade: bool = False) -> None:
    """
    Полностью очищает таблицу LogDoneTransactions.
    cascade=True → добавляет CASCADE (если есть FK-зависимости)
    """

    db = DataBase()

    async with db.get_session_maker()() as session:
        sql = f"TRUNCATE TABLE {table_name}"
        if cascade:
            sql += " CASCADE"

        await session.execute(text(sql))
        await session.commit()


async def set_balance(l_algos):
    db = DataBase()
    async_sessionmaker = db.get_session_maker()
    initial_balance = EMULATION_SETTINGS.get("initial_balance", {})
    initial_balance_algo = get_registered_initial_balance_algos()
    usd_balance = initial_balance.get("USD", {})
    btc_balance = initial_balance.get("BTC", {})
    prepared_algos: list[dict[str, Any]] = []

    for algo_data in l_algos:
        algo_name = str(algo_data["name"])
        algo_definition = get_algorithm_definition(algo_name)
        algo_balance = initial_balance_algo.get(algo_name, {})
        usd_amount = algo_balance.get("USD", {}).get("amount", algo_data.get("usd", 0))
        usd_reserved = algo_balance.get("USD", {}).get("reserved", 0)
        btc_amount = algo_balance.get("BTC", {}).get("amount", algo_data.get("btc", 0))
        btc_reserved = algo_balance.get("BTC", {}).get("reserved", 0)

        prepared_algos.append(
            {
                **algo_data,
                "USD_amount": usd_amount,
                "USD_reserved": usd_reserved,
                "BTC_amount": btc_amount,
                "BTC_reserved": btc_reserved,
                "account_id": str(algo_definition.default_config.get("account_id", "")),
            }
        )

    async with async_sessionmaker() as session:
        await init_balance(
            session,
            usd_amount=usd_balance.get("amount", 100),
            usd_reserved=usd_balance.get("reserved", 0),
            btc_amount=btc_balance.get("amount", 1),
            btc_reserved=btc_balance.get("reserved", 0),
            l_algos=prepared_algos,
        )
        for algo_data in prepared_algos:
            account_id = str(algo_data.get("account_id", "")).strip()
            if not account_id:
                continue
            await _upsert_emulator_balance(
                session,
                account_id=account_id,
                curr="USD",
                amount=_d(usd_balance.get("amount", 100)),
                reserved=_d(usd_balance.get("reserved", 0)),
            )
            await _upsert_emulator_balance(
                session,
                account_id=account_id,
                curr="BTC",
                amount=_d(btc_balance.get("amount", 1)),
                reserved=_d(btc_balance.get("reserved", 0)),
            )
        await session.commit()
