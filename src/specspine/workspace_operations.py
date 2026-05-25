from __future__ import annotations

from pathlib import Path

from .workspace_templates import BASE_WORKSPACE_FILES, normalize_template

__all__ = [
    "write_workspace_files",
    "init_workspace",
    "check_workspace",
]


def write_workspace_files(
    root: Path,
    files: dict[str, str],
    *,
    force: bool = False,
) -> list[Path]:
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for relative_path, template in files.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists() and not force:
            continue

        target.write_text(normalize_template(template), encoding="utf-8")
        written.append(target)

    return written


def init_workspace(path: Path, *, force: bool = False) -> list[Path]:
    return write_workspace_files(path, BASE_WORKSPACE_FILES, force=force)


def check_workspace(
    path: Path,
    *,
    required_files: dict[str, str] | None = None,
) -> tuple[list[Path], list[Path]]:
    root = path.expanduser().resolve()
    files = required_files or BASE_WORKSPACE_FILES
    present: list[Path] = []
    missing: list[Path] = []

    for relative_path in files:
        target = root / relative_path
        if target.exists():
            present.append(target)
        else:
            missing.append(target)

    return present, missing
