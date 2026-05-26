from __future__ import annotations

from ._strategies_base import _FrozenBase

__all__ = [
    "RepairStrategyInit",
]


class RepairStrategyInit(_FrozenBase):
    ac_id: str
    target_file: str
    edit_description: str
    verification_command: str
    success_criteria: str

    def __init__(
        self,
        ac_id: str,
        target_file: str,
        edit_description: str,
        verification_command: str,
        success_criteria: str,
    ) -> None:
        object.__setattr__(self, "ac_id", ac_id)
        object.__setattr__(self, "target_file", target_file)
        object.__setattr__(self, "edit_description", edit_description)
        object.__setattr__(self, "verification_command", verification_command)
        object.__setattr__(self, "success_criteria", success_criteria)
