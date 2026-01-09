# trade_config.py
from __future__ import annotations

import asyncio
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect import DataBase
from src.database.models import Trade_Parameters


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

    BUY_FEE: float = 0.18513
    SELL_FEE: float = 0.25

    MAKER_TAKER: float = 0.25
    MAKER: float = 0.16
    TAKER: float = 0.25

    _loaded: bool = False

    # ---------- PUBLIC API ----------
    @classmethod
    def load(cls, session: Session, model_cls) -> None:
        rows = session.execute(select(model_cls)).scalars().all()
        cls._apply(rows)
        cls._loaded = True

    @classmethod
    async def load_async(cls, session: AsyncSession, model_cls) -> None:
        result = await session.execute(select(model_cls))
        rows = result.scalars().all()
        cls._apply(rows)
        cls._loaded = True

    # ---------- INTERNAL ----------
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

async def _load_config_async():
    db = DataBase()
    session_maker = db.get_session_maker()
    async with session_maker() as session:
        await TradeConfig.load_async(session, Trade_Parameters)


def load_trade_config():
    """
    Запускать в main, чтобы загрузить значения из БД
    """
    asyncio.run(_load_config_async())
