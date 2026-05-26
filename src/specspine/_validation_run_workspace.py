from __future__ import annotations

from pathlib import Path

from .validation_models import AdapterProbe
from .workspace import BASE_WORKSPACE_FILES
from .validation_build_checks import (
    _file_checks,
    _workspace_placeholder_checks,
)

__all__ = [
    "_run_workspace_checks",
]


def _run_workspace_checks(root: Path) -> list:
    from .validation_models import ValidationCheck

    checks: list[ValidationCheck] = []
    checks.extend(
        _file_checks(
            root,
            required_files=BASE_WORKSPACE_FILES,
            prefix="workspace",
            label="Workspace",
        )
    )
    checks.extend(_workspace_placeholder_checks(root))
    return checks
