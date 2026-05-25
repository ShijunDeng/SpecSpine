from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .impact_models import DISCOVERY_COMMAND


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


__all__ = [
    "_relative_path",
    "_source_module_name",
    "_test_module_name",
    "_unittest_command",
    "_normalise_changed_file",
    "_definition_symbols",
    "_source_inventory",
    "_modules_from_imports",
    "_modules_from_text",
    "_test_inventory",
]
