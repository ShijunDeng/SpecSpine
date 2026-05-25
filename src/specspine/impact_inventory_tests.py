from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .impact_inventory_utils import (
    _relative_path,
    _test_module_name,
)
from .impact_inventory_source import (
    _modules_from_imports,
    _modules_from_text,
)

__all__ = [
    "_test_inventory",
]


def _test_inventory(
    root: Path,
    modules: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], ...]:
    tests_dir = root / "tests"
    known_modules = set(modules)
    test_records: list[dict[str, Any]] = []
    for path in sorted(tests_dir.glob("test_*.py")):
        relative_path = _relative_path(root, path)
        content = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(content, filename=str(path))
            import_matches = _modules_from_imports(tree, known_modules)
        except SyntaxError:
            import_matches = set()
        text_matches = _modules_from_text(content, modules)
        source_modules = tuple(sorted(import_matches | text_matches))
        for module in source_modules:
            modules[module]["test_files"].append(relative_path)
        test_records.append(
            {
                "imports": sorted(import_matches),
                "module": _test_module_name(relative_path),
                "path": relative_path,
                "source_modules": list(source_modules),
                "text_matches": sorted(text_matches - import_matches),
            }
        )

    for module in modules.values():
        module["test_files"] = sorted(set(module["test_files"]))
    return tuple(test_records)
