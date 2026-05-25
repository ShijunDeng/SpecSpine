from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..consistency import _explicit_paths_from_feature_files, LOCAL_PATH_RE
from ..consistency import _read_text
from ..features import FEATURE_FILE_PATHS
from ..evolution import _run_git

__all__ = [
    "_now_iso",
    "_feature_peer_content",
    "_baseline_peer_content",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _feature_peer_content(root: Path, slug: str, kind: str) -> str | None:
    rel_path = FEATURE_FILE_PATHS.get(kind)
    if rel_path is None:
        return None
    path = root / rel_path.format(slug=slug)
    if not path.exists():
        return None
    return _read_text(path)


def _baseline_peer_content(root: Path, slug: str, kind: str, baseline: str) -> str | None:
    rel_path = FEATURE_FILE_PATHS.get(kind)
    if rel_path is None:
        return None
    rel = rel_path.format(slug=slug)
    result = _run_git(["show", f"{baseline}:{rel}"], root)
    if result.returncode == 0:
        return result.stdout
    return None
