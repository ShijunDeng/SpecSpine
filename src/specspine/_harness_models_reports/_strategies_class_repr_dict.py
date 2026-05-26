from __future__ import annotations

__all__ = [
    "RepairStrategyReprDict",
]


class RepairStrategyReprDict:
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
