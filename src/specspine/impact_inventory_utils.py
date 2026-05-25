from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .impact_models import DISCOVERY_COMMAND  # noqa: F401

__all__ = [
    "_relative_path",
    "_source_module_name",
    "_test_module_name",
    "_unittest_command",
    "_normalise_changed_file",
    "_definition_symbols",
]


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _source_module_name(path: Path) -> str:
    if path.stem == "__init__":
        return "specspine"
    return f"specspine.{path.stem}"


def _test_module_name(relative_path: str) -> str:
    return relative_path.removesuffix(".py").replace("/", ".")


def _unittest_command(test_file: str) -> str:
    return f"PYTHONPATH=src python3 -m unittest {_test_module_name(test_file)}"


def _normalise_changed_file(root: Path, value: str) -> str:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    return _relative_path(root, candidate.resolve())


def _definition_symbols(path: Path) -> tuple[str, ...]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return ()

    symbols: list[str] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(node.name)
    return tuple(sorted(set(symbols)))
