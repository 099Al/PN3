from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timezone
from typing import Any, Optional

from src.database.models import ActiveOrder
from src.database.models.models_img import Im_ActiveOrder
from src.database.models.models_types import SideTypeEnum, OrderTypeEnum

from src.config import prj_configs
from src.trade_utils.date_unix import dt_from_unix_ms, utcnow_dt

from src.trade_utils.trade import X_for_buyBTC





def calc_quote_needed_for_buy(amount: Decimal, price: Decimal) -> Decimal:
    return Decimal(str(X_for_buyBTC(amount, price)))


def calc_reserved(side: str, amount: Decimal, price: Decimal) -> Decimal:
    s = str(side).upper()
    if s == "BUY":
        return calc_quote_needed_for_buy(amount, price)
    if s == "SELL":
        return amount
    raise ValueError(f"Unknown side: {side}")


def build_active_order(
    *,
    unix_ms: int,
    base: str,
    quote: str,
    side: str,
    amount: Decimal,
    price: Decimal,
    order_type: str = "Limit",
    #algo: str | None = None,
    #full_traid: str | None = None,
) -> Im_ActiveOrder:


    reserved = calc_reserved(side=side, amount=amount, price=price)

    return Im_ActiveOrder(
        # id автогенерируется БД
        date=dt_from_unix_ms(unix_ms),
        unix_date=unix_ms,
        base=base,
        quote=quote,
        side=side,
        amount=amount,
        price=price,
        reserved=reserved,
        order_type=order_type,
        # full_traid=full_traid,
        # algo=algo,
        sys_date=utcnow_dt(),
    )
