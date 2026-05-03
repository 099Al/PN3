from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.algos.base import BaseAlgorithm
from src.algos.first_algo import Algo_1
from src.algos.first_algo.config import (
    FIRST_ALGO_CAPITAL_ALLOCATION,
    FIRST_ALGO_CONFIG,
    FIRST_ALGO_NAME,
)


@dataclass(frozen=True)
class AlgorithmDefinition:
    name: str
    algo_class: type[BaseAlgorithm]
    default_config: dict[str, Any]
    capital_allocation: dict[str, Any]


ALGORITHM_REGISTRY: dict[str, AlgorithmDefinition] = {
    FIRST_ALGO_NAME: AlgorithmDefinition(
        name=FIRST_ALGO_NAME,
        algo_class=Algo_1,
        default_config=FIRST_ALGO_CONFIG,
        capital_allocation=FIRST_ALGO_CAPITAL_ALLOCATION,
    ),
}


def get_algorithm_definition(algo_name: str) -> AlgorithmDefinition:
    try:
        return ALGORITHM_REGISTRY[algo_name]
    except KeyError as exc:
        raise KeyError(f"Algorithm {algo_name!r} is not registered") from exc


def get_registered_algorithm_names() -> list[str]:
    return list(ALGORITHM_REGISTRY.keys())


def get_registered_capital_allocations() -> list[dict[str, Any]]:
    return [dict(definition.capital_allocation) for definition in ALGORITHM_REGISTRY.values()]


def build_algorithm(algo_name: str, **overrides: Any) -> BaseAlgorithm:
    definition = get_algorithm_definition(algo_name)
    algo_config = dict(definition.default_config)
    algo_config.update(overrides)
    return definition.algo_class(**algo_config)
