from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class BaseAlgorithm(ABC):
    account_id: str
    algo_name: str
    pair: str
    amount: Decimal
    position_curr: str = "BTC"

    @abstractmethod
    async def run(self) -> None:
        raise NotImplementedError

