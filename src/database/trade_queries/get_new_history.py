from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Iterable, Optional

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.provider import ApiProvider
from src.database.connect import DataBase
from src.database.models import CexHistoryTik
from src.trade_utils.date_unix import dt_from_unix_ms, parse_iso_z_to_naive, utcnow_dt
from src.trade_utils.util_decimal import to_decimal


@dataclass(frozen=True)
class TickRow:
    tid: str
    type: str          # BUY/SELL (или buy/sell — выбери единый стиль)
    unixdate: int      # unix ms
    date: datetime     # naive UTC (под timestamp without time zone)
    amount: Decimal
    price: Decimal
    sys_insert: datetime

def tradeid_to_unix_ms(trade_id: str) -> int:
    # "1768935923275-0" -> 1768935923275
    return int(trade_id.split("-", 1)[0])



def normalize_trade(raw: dict) -> TickRow:
    """
    raw пример:
    {'tradeId': '1768935923275-0', 'dateISO': '2026-01-20T19:05:23.275Z',
     'side': 'SELL', 'price': '89439.9', 'amount': '0.00250000'}
    """
    tid = str(raw["tradeId"])
    unix_ms = tradeid_to_unix_ms(tid)

    side = str(raw.get("side", "")).upper()
    if side not in ("BUY", "SELL"):
        raise ValueError(f"Unknown side in trade: {raw}")

    # date лучше брать из dateISO (истина), а unixdate — из tradeId (удобный ключ)
    # Если dateISO вдруг нет — восстановим по unix_ms.
    if "dateISO" in raw and raw["dateISO"]:
        date = parse_iso_z_to_naive(str(raw["dateISO"]))
    else:
        date = dt_from_unix_ms(unix_ms)

    return TickRow(
        tid=tid,
        type=side,                 # в CexHistoryTik поле называется type — логично хранить BUY/SELL
        unixdate=unix_ms,
        date=date,
        amount=to_decimal(raw["amount"]),
        price=to_decimal(raw["price"]),
        sys_insert=utcnow_dt(),
    )

def dedupe_by_tid(rows: Iterable[TickRow]) -> list[TickRow]:
    """
    Убираем повторы внутри одного ответа.
    По одному tid оставим последний (по unixdate).
    """
    d: dict[str, TickRow] = {}
    for r in rows:
        prev = d.get(r.tid)
        if prev is None or r.unixdate >= prev.unixdate:
            d[r.tid] = r
    return list(d.values())

class CexHistoryRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_many(self, rows: list[TickRow]) -> int:
        if not rows:
            return 0

        l_payload = [
            {
                "tid": r.tid,
                "type": r.type,
                "unixdate": r.unixdate,
                "date": r.date,
                "amount": r.amount,
                "price": r.price,
                "sys_insert": r.sys_insert,
            }
            for r in rows
        ]

        stmt = pg_insert(CexHistoryTik).values(l_payload).on_conflict_do_nothing(index_elements=[CexHistoryTik.tid])



        await self.session.execute(stmt)
        return len(rows)


async def get_new_data(pair: str, *, unix_curr_time: Optional[int] = None) -> int:
    """
    pair: "BTC/USD"
    unix_curr_time: нужен только для EMULATION, в TRAIDING можно None
    """
    p1, p2 = pair.split("/")
    pair_api = f"{p1}-{p2}"

    api = ApiProvider.get(unix_curr_time=unix_curr_time)
    res = await api.trade_history(pair_api)

    trades = res.get("data", {}).get("trades", []) or []

    rows = [normalize_trade(t) for t in trades]
    rows = dedupe_by_tid(rows)

    db = DataBase()
    async with db.get_session_maker()() as session:
        repo = CexHistoryRepo(session)
        await repo.upsert_many(rows)
        await session.commit()

    return len(rows)