import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database.models.models import Exchange

from src.database.connect import DataBase


class ExchangeConfig:
    """
    Exchange rates config.

    Usage:
        ExchangeConfig.load(session)
        ExchangeConfig.usd_bye(bank="TINKOFF")
        ExchangeConfig.usd_sell(bank="TINKOFF")
    """

    _model = Exchange

    # ---------- INTERNAL STORAGE ----------
    # key: (bank, dt) -> (bye, sell)
    _usd_rates: dict[tuple[str, datetime], tuple[Decimal, Decimal]] = {}

    _loaded: bool = False

    # ---------- LOADERS ----------
    @classmethod
    def load(cls, session: Session) -> None:
        rows = session.execute(
            select(cls._model)
            .where(
                cls._model.base == "USD",
                cls._model.quote == "RUB",
            )
        ).scalars().all()

        cls._apply(rows)
        cls._loaded = True

    @classmethod
    async def load_async(cls, session: AsyncSession) -> None:
        result = await session.execute(
            select(cls._model)
            .where(
                cls._model.base == "USD",
                cls._model.quote == "RUB",
            )
        )
        rows = result.scalars().all()

        cls._apply(rows)
        cls._loaded = True

    # ---------- INTERNAL ----------
    @classmethod
    def _apply(cls, rows) -> None:
        cls._usd_rates.clear()

        for r in rows:
            key = (r.bank.upper(), r.dt)
            cls._usd_rates[key] = (r.bye, r.sell)

    # ---------- PUBLIC API ----------
    @classmethod
    def usd_bye(
        cls,
        bank: str,
        dt: Optional[datetime] = None,
    ) -> Decimal:
        return cls._get(bank, dt)[0]

    @classmethod
    def usd_sell(
        cls,
        bank: str,
        dt: Optional[datetime] = None,
    ) -> Decimal:
        return cls._get(bank, dt)[1]

    # ---------- CORE LOGIC ----------
    @classmethod
    def _get(
        cls,
        bank: str,
        dt: Optional[datetime],
    ) -> tuple[Decimal, Decimal]:
        if not cls._loaded:
            raise RuntimeError("ExchangeConfig is not loaded")

        bank = bank.upper()

        # если dt не задан — берём самый свежий курс
        candidates = [
            (k_dt, v)
            for (k_bank, k_dt), v in cls._usd_rates.items()
            if k_bank == bank and (dt is None or k_dt <= dt)
        ]

        if not candidates:
            raise KeyError(f"No USD/RUB rate for bank={bank}, dt={dt}")

        # берём максимальный dt
        latest_dt, rates = max(candidates, key=lambda x: x[0])
        return rates


async def _load_config_async():
    db = DataBase()
    session_maker = db.get_session_maker()
    async with session_maker() as session:
        await ExchangeConfig.load_async(session)


def load_exchange_config():
    """
    Запускать в main, чтобы загрузить значения из БД
    """
    asyncio.run(_load_config_async())

#Пример использования:
# load_exchange_config()
# bye = ExchangeConfig.usd_bye(bank="ALFA")