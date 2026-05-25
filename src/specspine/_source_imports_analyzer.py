from __future__ import annotations

import ast
from typing import Any

__all__ = [
    "_modules_from_imports",
]


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
