from __future__ import annotations

import re
from pathlib import Path

from .consistency import _explicit_paths_from_feature_files, LOCAL_PATH_RE
from .consistency import _read_text
from .features import FEATURE_FILE_PATHS

AC_ID_RE = re.compile(r"(AC\d{3})")
TASK_ID_RE = re.compile(r"(T\d{3})")
QUALITY_CHECK_RE = re.compile(r"(QC\d{3})")
COV_LINK_RE = re.compile(r"- \[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")

__all__ = [
    "AC_ID_RE",
    "TASK_ID_RE",
    "QUALITY_CHECK_RE",
    "COV_LINK_RE",
    "_now_iso",
    "_feature_peer_content",
    "_extract_acs_from_spec",
    "_extract_tasks_from_execution",
    "_extract_acs_from_quality",
    "_extract_cov_links_from_quality",
    "_extract_qc_ids_from_quality",
    "_baseline_peer_content",
]


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _feature_peer_content(root: Path, slug: str, kind: str) -> str | None:
    rel_path = FEATURE_FILE_PATHS.get(kind)
    if rel_path is None:
        return None
    path = root / rel_path.format(slug=slug)
    if not path.exists():
        return None
    return _read_text(path)


def _extract_acs_from_spec(content: str) -> list[str]:
    return AC_ID_RE.findall(content)


def _extract_tasks_from_execution(content: str) -> list[str]:
    return TASK_ID_RE.findall(content)


def _extract_acs_from_quality(content: str) -> list[str]:
    return AC_ID_RE.findall(content)


def _extract_cov_links_from_quality(content: str) -> list[tuple[str, str]]:
    return COV_LINK_RE.findall(content)


def _extract_qc_ids_from_quality(content: str) -> list[str]:
    return QUALITY_CHECK_RE.findall(content)


def _baseline_peer_content(root: Path, slug: str, kind: str, baseline: str) -> str | None:
    from .evolution import _run_git
    rel_path = FEATURE_FILE_PATHS.get(kind)
    if rel_path is None:
        return None
    rel = rel_path.format(slug=slug)
    result = _run_git(["show", f"{baseline}:{rel}"], root)
    if result.returncode == 0:
        return result.stdout
    return None
