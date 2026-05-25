from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .impact_inventory_utils import (
    _relative_path,
    _source_module_name,
    _definition_symbols,
)

__all__ = [
    "_source_inventory",
    "_modules_from_imports",
    "_modules_from_text",
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


def _modules_from_imports(tree: ast.AST, known_modules: set[str]) -> set[str]:
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name in known_modules:
                    imported.add(name)
                elif name.startswith("specspine."):
                    parts = name.split(".")
                    candidate = ".".join(parts[:2])
                    if candidate in known_modules:
                        imported.add(candidate)
                elif name == "specspine" and name in known_modules:
                    imported.add(name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in known_modules:
                imported.add(module)
            elif module.startswith("specspine."):
                parts = module.split(".")
                candidate = ".".join(parts[:2])
                if candidate in known_modules:
                    imported.add(candidate)
            elif module == "specspine":
                if module in known_modules:
                    imported.add(module)
                for alias in node.names:
                    candidate = f"specspine.{alias.name}"
                    if candidate in known_modules:
                        imported.add(candidate)
    return imported


def _modules_from_text(content: str, modules: dict[str, dict[str, Any]]) -> set[str]:
    matched: set[str] = set()
    for module, info in modules.items():
        stem = module.rsplit(".", 1)[-1]
        needles = {module, f"{stem}.py"}
        needles.update(str(symbol) for symbol in info["symbols"])
        if any(needle and needle in content for needle in needles):
            matched.add(module)
    return matched
