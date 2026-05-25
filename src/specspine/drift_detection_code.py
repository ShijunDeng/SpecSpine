from __future__ import annotations

from pathlib import Path

from .drift_models import DriftEvent
from .drift_detection_extractors import (
    _now_iso,
    _feature_peer_content,
    _extract_acs_from_spec,
    _extract_tasks_from_execution,
    AC_ID_RE,
)


def _detect_code_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    spec_content = _feature_peer_content(root, slug, "spec")
    if spec_content is None:
        return events

    from .consistency import LOCAL_PATH_RE

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

    code_paths = [p for p in referenced_paths if p.startswith("src/")]
    orphaned: list[str] = []
    for path in sorted(code_paths):
        if not (root / path).exists():
            orphaned.append(path)

    if orphaned:
        events.append(
            DriftEvent(
                event_type="code",
                severity="medium",
                timestamp=_now_iso(),
                description=f"Source files referenced in spec do not exist on disk",
            )
        )

    exec_content = _feature_peer_content(root, slug, "execution")
    if exec_content is not None:
        tasks_in_exec = _extract_tasks_from_execution(exec_content)
        tasks_in_spec = _extract_acs_from_spec(spec_content)
        task_ac_refs: set[str] = set()
        for line in exec_content.splitlines():
            for ac_match in AC_ID_RE.finditer(line):
                task_ac_refs.add(ac_match.group(1))

        missing_ac_links = sorted(set(tasks_in_spec) - task_ac_refs)
        if missing_ac_links:
            events.append(
                DriftEvent(
                    event_type="code",
                    severity="medium",
                    timestamp=_now_iso(),
                    description="Tasks in execution file do not reference all spec ACs",
                    affected_acs=tuple(missing_ac_links),
                )
            )

    return events


__all__ = [
    "_detect_code_drift",
]
