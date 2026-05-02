from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.algos.first_algo import Algo_1
from src.algos.first_algo.config import (
    FIRST_ALGO_BALANCE_LIMIT,
    FIRST_ALGO_CONFIG,
    FIRST_ALGO_NAME,
)


@dataclass(frozen=True)
class AlgorithmDefinition:
    name: str
    algo_class: type
    default_config: dict[str, Any]
    balance_limit: dict[str, Any]


ALGORITHM_REGISTRY: dict[str, AlgorithmDefinition] = {
    FIRST_ALGO_NAME: AlgorithmDefinition(
        name=FIRST_ALGO_NAME,
        algo_class=Algo_1,
        default_config=FIRST_ALGO_CONFIG,
        balance_limit=FIRST_ALGO_BALANCE_LIMIT,
    ),
}


def get_algorithm_definition(algo_name: str) -> AlgorithmDefinition:
    try:
        return ALGORITHM_REGISTRY[algo_name]
    except KeyError as exc:
        raise KeyError(f"Algorithm {algo_name!r} is not registered") from exc


def build_algorithm(algo_name: str, **overrides: Any):
    definition = get_algorithm_definition(algo_name)
    algo_config = dict(definition.default_config)
    algo_config.update(overrides)
    return definition.algo_class(**algo_config)

