from __future__ import annotations

from ._strategies_class_hash_eq import RepairStrategyHashEq
from ._strategies_class_init import RepairStrategyInit
from ._strategies_class_repr_dict import RepairStrategyReprDict

__all__ = [
    "RepairStrategy",
]


class RepairStrategy(RepairStrategyInit, RepairStrategyHashEq, RepairStrategyReprDict):
    pass
