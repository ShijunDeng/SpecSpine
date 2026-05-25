from __future__ import annotations

from ._strategies_base import _FrozenBase

__all__ = [
    "RepairStrategy",
]

STRATEGY_FIELDS: tuple[str, ...] = (
    "ac_id",
    "target_file",
    "edit_description",
    "verification_command",
    "success_criteria",
)


class RepairStrategy(_FrozenBase):
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

    def __hash__(self) -> int:
        return hash((
            self.ac_id,
            self.target_file,
            self.edit_description,
            self.verification_command,
            self.success_criteria,
        ))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RepairStrategy):
            return NotImplemented
        return (
            self.ac_id == other.ac_id
            and self.target_file == other.target_file
            and self.edit_description == other.edit_description
            and self.verification_command == other.verification_command
            and self.success_criteria == other.success_criteria
        )

    def __repr__(self) -> str:
        return (
            f"RepairStrategy(ac_id={self.ac_id!r}, target_file={self.target_file!r}, "
            f"edit_description={self.edit_description!r}, "
            f"verification_command={self.verification_command!r}, "
            f"success_criteria={self.success_criteria!r})"
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "edit_description": self.edit_description,
            "success_criteria": self.success_criteria,
            "target_file": self.target_file,
            "verification_command": self.verification_command,
        }
