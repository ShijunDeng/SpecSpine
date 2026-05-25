from __future__ import annotations

from pathlib import Path

from .drift_models import DriftEvent
from .drift_detection_extractors import (
    _now_iso,
    _feature_peer_content,
)
from .consistency import LOCAL_PATH_RE


def _extract_referenced_code_paths(root: Path, slug: str) -> list[str]:
    source_files: list[str] = []
    for kind in ("spec", "execution", "quality"):
        content = _feature_peer_content(root, slug, kind)
        if content is not None:
            source_files.append(content)

    referenced_paths: set[str] = set()
    for content in source_files:
        for match in LOCAL_PATH_RE.finditer(content):
            p = match.group("path").rstrip(".,);]`")
            referenced_paths.add(p)

    return [p for p in referenced_paths if p.startswith("src/")]


def _find_orphaned_files(root: Path, code_paths: list[str]) -> list[str]:
    return [p for p in sorted(code_paths) if not (root / p).exists()]


def _detect_orphaned_code_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    spec_content = _feature_peer_content(root, slug, "spec")
    if spec_content is None:
        return events

    code_paths = _extract_referenced_code_paths(root, slug)
    orphaned = _find_orphaned_files(root, code_paths)

    if orphaned:
        events.append(
            DriftEvent(
                event_type="code",
                severity="medium",
                timestamp=_now_iso(),
                description=f"Source files referenced in spec do not exist on disk",
            )
        )

    return events


__all__ = [
    "_extract_referenced_code_paths",
    "_find_orphaned_files",
    "_detect_orphaned_code_drift",
]
