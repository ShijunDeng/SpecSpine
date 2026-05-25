from __future__ import annotations

from pathlib import Path
from typing import Any

from .impact_inventory_utils import (
    _relative_path,
    _source_module_name,
    _definition_symbols,
)
from ._source_imports_analyzer import _modules_from_imports  # noqa: F401
from ._source_text_matcher import _modules_from_text  # noqa: F401

__all__ = [
    "_source_inventory",
]


def _source_inventory(root: Path) -> dict[str, dict[str, Any]]:
    source_dir = root / "src" / "specspine"
    modules: dict[str, dict[str, Any]] = {}
    for path in sorted(source_dir.glob("*.py")):
        relative_path = _relative_path(root, path)
        module = _source_module_name(path)
        modules[module] = {
            "module": module,
            "path": relative_path,
            "symbols": list(_definition_symbols(path)),
            "test_files": [],
        }
    return modules
