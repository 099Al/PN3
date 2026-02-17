# trade_config.py
from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect import DataBase
from src.database.models import Trade_Parameters, DepositFee


class TradeConfig:
    """
    Global trading config.

    Usage:
        from trade_config import TradeConfig

        TradeConfig.REQUEST_PERIOD
        TradeConfig.load(session, Trade_Parameters)
    """

    # ---------- DEFAULTS ----------
    REQUEST_PERIOD: int = 120
    USER_NAME: str = "up_user_1"

    BASE_MIN: float = 0.00042278
    QUOTE_MIN: float = 10.0

    BUY_FEE: float = 0.25 # 0.18513
    SELL_FEE: float = 0.25

    MAKER_TAKER: float = 0.25
    MAKER: float = 0.16
    TAKER: float = 0.25

    DEPO_LIMIT_IN_USD: float = 20
    DEPO_LIMIT_IN_RUB: float = 1200

    # USD
    u_dep_prc: Decimal = Decimal("0")
    u_dep_fix: Decimal = Decimal("0")
    u_wthrw_prc: Decimal = Decimal("0")
    u_wthrw_fix: Decimal = Decimal("0")

    # RUB
    r_dep_prc: Decimal = Decimal("0")
    r_dep_fix: Decimal = Decimal("0")
    r_wthrw_prc: Decimal = Decimal("0")
    r_wthrw_fix: Decimal = Decimal("0")


    _loaded: bool = False

    # ---------- MODELS ----------
    _trade_model = Trade_Parameters
    _deposit_model = DepositFee


    # ---------- PUBLIC API ----------
    @classmethod
    async def load_async(
            cls,
            session: AsyncSession
    ) -> None:
        await cls._load_trade_params_async(session)
        await cls._load_deposit_fees_async(session)
        cls._loaded = True



    # ---------- INTERNAL ----------
    @classmethod
    async def _load_trade_params_async(cls, session: AsyncSession, model_cls) -> None:
        result = await session.execute(select(model_cls))
        rows = result.scalars().all()
        cls._apply(rows)
        cls._loaded = True

    @classmethod
    def _apply(cls, rows) -> None:
        for r in rows:
            value = cls._cast(r.value, r.v_type)
            setattr(cls, r.key, value)

    @staticmethod
    def _cast(value: str, v_type: str | None) -> Any:
        if not v_type:
            return value

        t = v_type.lower()
        if t in ("int", "integer"):
            return int(value)
        if t in ("float", "double", "decimal"):
            return float(value)
        if t in ("bool", "boolean"):
            return value.lower() in ("1", "true", "yes", "on")
        return value

    @classmethod
    async def _load_deposit_fees_async(cls, session: AsyncSession) -> None:
        result = await session.execute(select(cls._deposit_model))
        rows = result.scalars().all()
        cls._apply_deposit_fees(rows)

    @classmethod
    def _apply_deposit_fees(cls, rows) -> None:
        for r in rows:
            curr = r.curr.upper()

            if curr == "USD":
                cls.u_dep_prc = r.deposit
                cls.u_dep_fix = r.deposit_fix
                cls.u_wthrw_prc = r.withdrawal
                cls.u_wthrw_fix = r.withdrawal_fix

            elif curr == "RUB":
                cls.r_dep_prc = r.deposit
                cls.r_dep_fix = r.deposit_fix
                cls.r_wthrw_prc = r.withdrawal
                cls.r_wthrw_fix = r.withdrawal_fix


async def _load_config_async():
    db = DataBase()
    session_maker = db.get_session_maker()
    async with session_maker() as session:
        await TradeConfig.load_async(session)


def load_trade_config():
    """
    Запускать в main, чтобы загрузить значения из БД
    """
    asyncio.run(_load_config_async())
