from __future__ import annotations

__all__ = [
    "RepairStrategyHashEq",
]


class RepairStrategyHashEq:
    def __hash__(self) -> int:
        return hash((
            self.ac_id,
            self.target_file,
            self.edit_description,
            self.verification_command,
            self.success_criteria,
        ))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RepairStrategyHashEq):
            return NotImplemented
        return (
            self.ac_id == other.ac_id
            and self.target_file == other.target_file
            and self.edit_description == other.edit_description
            and self.verification_command == other.verification_command
            and self.success_criteria == other.success_criteria
        )
