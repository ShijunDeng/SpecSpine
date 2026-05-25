from __future__ import annotations

from pathlib import Path

from .validation_models import ValidationCheck, WORKSPACE_PLACEHOLDER_PHRASES
from ._validation_helpers import _check


def _workspace_placeholder_checks(root: Path) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for relative_path, phrases in sorted(WORKSPACE_PLACEHOLDER_PHRASES.items()):
        target = root / relative_path
        if not target.exists():
            continue

        try:
            content = target.read_text(encoding="utf-8")
        except OSError:
            continue

        if any(phrase in content for phrase in phrases):
            checks.append(
                _check(
                    f"workspace.placeholder:{relative_path}",
                    "warn",
                    f"Workspace file still contains scaffold placeholder content: {relative_path}",
                )
            )

    return checks


__all__ = [
    "_workspace_placeholder_checks",
]
