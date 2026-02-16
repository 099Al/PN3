from decimal import Decimal
from typing import Any

D100 = Decimal("100")
D0 = Decimal("0")

def to_decimal(x: Any) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def to_int(x: Any) -> int:
    return int(x)

def _d(x: Any) -> Decimal:
    return Decimal(str(x or 0))


def _fmt8(x: Decimal) -> str:
    return f"{x:.8f}"
