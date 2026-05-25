from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

__all__ = [
    "_candidate_superpowers_paths",
    "find_superpowers_install",
    "read_superpowers_version",
]


def _candidate_superpowers_paths() -> Iterable[Path]:
    env_path = os.environ.get("SPECSPINE_SUPERPOWERS_PATH")
    if env_path:
        yield Path(env_path)

    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    yield codex_home / "plugins" / "superpowers"
    yield codex_home / ".tmp" / "plugins" / "plugins" / "superpowers"
    yield Path.home() / ".claude" / "plugins" / "superpowers"


def find_superpowers_install() -> Path | None:
    for path in _candidate_superpowers_paths():
        if (path / "skills").exists() or (path / ".codex-plugin" / "plugin.json").exists():
            return path
    return None


def read_superpowers_version(path: Path) -> str | None:
    plugin_json = path / ".codex-plugin" / "plugin.json"
    if not plugin_json.exists():
        return None

    try:
        import json
        payload = json.loads(plugin_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    version = payload.get("version")
    if isinstance(version, str):
        return version
    return None
