from __future__ import annotations

from ..impact_inventory import _unittest_command

__all__ = [
    "_command_for_coverage_target",
]


def _command_for_coverage_target(target_path: str) -> str | None:
    target = target_path.split("::", 1)[0]
    if not target.startswith("tests/") or not target.endswith(".py"):
        return None
    return _unittest_command(target)
