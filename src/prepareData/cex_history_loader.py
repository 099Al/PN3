from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select, func, Column, Text, BigInteger, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect import DataBase
from src.database.models.models_img import Im_CexHistoryTik, ImCexHistoryFileLog  # поправь импорт

Base = declarative_base()

"""
Загрузка данных в таблицу im_cex_history_tik
Данные находятся в директории hist_data/trades

Таблица im_cex_history_tik  используется как эмуляция источника данных

"""



def project_root() -> Path:
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    return p.parents[2]


def hist_dir() -> Path:
    return project_root() / "hist_data" / "trades"


def parse_iso_z(dt_str: str) -> datetime:
    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    return dt.replace(tzinfo=None)


def normalize_payload(payload: Any) -> list[dict]:
    trades = payload.get("data", {}).get("trades", [])
    rows: list[dict] = []
    for t in trades:
        dt = parse_iso_z(t["dateISO"])
        rows.append(
            dict(
                tid=str(t["tradeId"]),
                unixdate=int(dt.replace(tzinfo=timezone.utc).timestamp()),
                date=dt,
                side=str(t.get("side", "")).lower(),
                amount=Decimal(str(t.get("amount"))),
                price=Decimal(str(t.get("price"))),
                trade_data=json.dumps(t, ensure_ascii=False),
            )
        )
    return rows


async def get_max_unixdate(session: AsyncSession) -> int:
    mx = await session.scalar(select(func.max(Im_CexHistoryTik.unixdate)))
    return int(mx or 0)


async def insert_ignore_conflicts(session: AsyncSession, rows: list[dict]) -> int:
    if not rows:
        return 0
    stmt = (
        pg_insert(Im_CexHistoryTik)
        .values(rows)
        .on_conflict_do_nothing(index_elements=[Im_CexHistoryTik.tid])
    )
    res = await session.execute(stmt)
    return int(res.rowcount or 0)


async def load_only_new_from_files(
    directory: Optional[Path] = None,
) -> None:
    data_dir = directory or hist_dir()
    if not data_dir.exists():
        raise FileNotFoundError(f"Directory not found: {data_dir}")

    db = DataBase()
    session_maker = db.get_session_maker()

    async with session_maker() as session:
        # 1) watermark по времени
        max_unixdate = await get_max_unixdate(session)

        # 2) Загружаем уже обработанные имена файлов + метаданные
        loaded = await session.execute(
            select(ImCexHistoryFileLog.filename, ImCexHistoryFileLog.file_mtime, ImCexHistoryFileLog.file_size)
        )
        loaded_map = {fn: (mt, sz) for fn, mt, sz in loaded.all()}

        files = sorted(data_dir.glob("*.txt"))
        for f in files:
            stat = f.stat()
            fname = f.name
            mtime = int(stat.st_mtime)
            fsize = int(stat.st_size)

            # 3) Быстрый skip: файл уже грузили и он не менялся
            old = loaded_map.get(fname)
            if old is not None and old == (mtime, fsize):
                continue

            # 4) Читаем и грузим только если файл новый/изменён
            payload = json.loads(f.read_text(encoding="utf-8"))
            rows = normalize_payload(payload)

            # фильтр "только новое" — оставляем как дешёвую оптимизацию
            new_rows = [r for r in rows if int(r["unixdate"]) > max_unixdate]
            if new_rows:
                inserted = await insert_ignore_conflicts(session, new_rows)
                max_unixdate = max(max_unixdate, max(int(r["unixdate"]) for r in new_rows))
            else:
                inserted = 0

            # 5) Записываем/обновляем лог обработанного файла (UPSERT)
            log_stmt = (
                pg_insert(ImCexHistoryFileLog)
                .values(
                    filename=fname,
                    loaded_at=datetime.now(timezone.utc),
                    file_mtime=mtime,
                    file_size=fsize,
                )
                .on_conflict_do_update(
                    index_elements=[ImCexHistoryFileLog.filename],
                    set_={
                        "loaded_at": datetime.now(timezone.utc),
                        "file_mtime": mtime,
                        "file_size": fsize,
                    },
                )
            )
            await session.execute(log_stmt)
            await session.commit()

            print(f"[OK] {fname}: candidates={len(rows)} new={len(new_rows)} inserted={inserted}")


if __name__ == '__main__':



    asyncio.run(load_only_new_from_files())