from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(kw_only=True)
class BaseAlgorithm(ABC):
    account_id: str
    algo_name: str
    pair: str
    amount: Decimal
    position_curr: str = "BTC"

    @abstractmethod
    async def run(self, unix_curr_time: int | None = None) -> None:
        raise NotImplementedError

