from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .workspace import normalize_template
from .agents_template import AGENTS_FILE_NAME, AGENTS_TEMPLATE

__all__ = [
    "AGENTS_FILE_NAME",
    "AGENTS_TEMPLATE",
    "AgentsFileExistsError",
    "build_agents_file",
    "init_agents_file",
]


@dataclass(frozen=True)
class AgentsFileExistsError(FileExistsError):
    path: Path

    def __str__(self) -> str:
        return f"{AGENTS_FILE_NAME} already exists at {self.path}. Use --force to overwrite it."


def build_agents_file() -> str:
    return normalize_template(AGENTS_TEMPLATE)


def init_agents_file(root: Path, *, force: bool = False) -> Path:
    resolved_root = root.expanduser().resolve()
    target = resolved_root / AGENTS_FILE_NAME

    if target.exists() and not force:
        raise AgentsFileExistsError(path=target)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_agents_file(), encoding="utf-8")
    return target
