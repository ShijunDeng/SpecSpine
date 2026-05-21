from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .consistency import _explicit_paths_from_feature_files, LOCAL_PATH_RE
from .consistency import _read_text
from .drift_models import DriftEvent
from .features import FEATURE_FILE_PATHS

AC_ID_RE = re.compile(r"(AC\d{3})")
TASK_ID_RE = re.compile(r"(T\d{3})")
QUALITY_CHECK_RE = re.compile(r"(QC\d{3})")
COV_LINK_RE = re.compile(r"- \[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")

__all__ = [
    "_detect_code_drift",
    "_detect_spec_drift",
    "_detect_task_drift",
    "_detect_quality_drift",
    "_detect_test_drift",
    "_feature_peer_content",
    "_extract_acs_from_spec",
    "_extract_tasks_from_execution",
    "_extract_acs_from_quality",
    "_extract_cov_links_from_quality",
    "_extract_qc_ids_from_quality",
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


def _detect_spec_drift(slug: str, root: Path, baseline: str | None) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    current = _feature_peer_content(root, slug, "spec")
    if current is None:
        return events

    current_acs = _extract_acs_from_spec(current)

    if baseline is not None:
        before = _baseline_peer_content(root, slug, "spec", baseline)
        if before is None:
            if current_acs:
                events.append(
                    DriftEvent(
                        event_type="spec",
                        severity="high",
                        timestamp=_now_iso(),
                        description=f"Spec file exists but missing at baseline '{baseline}'; all ACs are new",
                        affected_acs=tuple(sorted(set(current_acs))),
                    )
                )
            return events

        before_acs = _extract_acs_from_spec(before)
        before_set = set(before_acs)
        current_set = set(current_acs)

        removed = sorted(before_set - current_set)
        added = sorted(current_set - before_set)

        if removed:
            events.append(
                DriftEvent(
                    event_type="spec",
                    severity="critical",
                    timestamp=_now_iso(),
                    description=f"ACs removed from spec compared to baseline '{baseline}'",
                    affected_acs=tuple(removed),
                )
            )

        if added:
            events.append(
                DriftEvent(
                    event_type="spec",
                    severity="medium",
                    timestamp=_now_iso(),
                    description=f"ACs added to spec compared to baseline '{baseline}'",
                    affected_acs=tuple(added),
                )
            )

    return events


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


def _detect_code_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    spec_content = _feature_peer_content(root, slug, "spec")
    if spec_content is None:
        return events

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


def _detect_task_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    exec_content = _feature_peer_content(root, slug, "execution")
    spec_content = _feature_peer_content(root, slug, "spec")
    if exec_content is None or spec_content is None:
        return events

    exec_tasks = _extract_tasks_from_execution(exec_content)
    spec_acs = _extract_acs_from_spec(spec_content)

    task_ac_refs: set[str] = set()
    for line in exec_content.splitlines():
        for ac_match in AC_ID_RE.finditer(line):
            task_ac_refs.add(ac_match.group(1))

    missing = sorted(set(spec_acs) - task_ac_refs)
    if missing:
        events.append(
            DriftEvent(
                event_type="task",
                severity="medium",
                timestamp=_now_iso(),
                description="Tasks in execution do not reference all spec ACs",
                affected_acs=tuple(missing),
            )
        )

    return events


def _detect_quality_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    quality_content = _feature_peer_content(root, slug, "quality")
    spec_content = _feature_peer_content(root, slug, "spec")
    if quality_content is None:
        return events

    quality_check_re = re.compile(r"(QC\d{3})")
    cov_link_re = re.compile(r"- \[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")

    qc_ids_in_quality = set(quality_check_re.findall(quality_content))
    cov_links = cov_link_re.findall(quality_content)
    covered_acs = {ac_id for ac_id, _ in cov_links}

    if spec_content is not None:
        spec_acs = set(_extract_acs_from_spec(spec_content))
        acs_without_qc = sorted(spec_acs - qc_ids_in_quality - covered_acs)
        if acs_without_qc:
            events.append(
                DriftEvent(
                    event_type="quality",
                    severity="low",
                    timestamp=_now_iso(),
                    description="Spec ACs missing quality check or coverage link",
                    affected_acs=tuple(acs_without_qc),
                )
            )

    for ac_id, target_path in cov_links:
        if not target_path.startswith("tests/"):
            events.append(
                DriftEvent(
                    event_type="quality",
                    severity="low",
                    timestamp=_now_iso(),
                    description=f"Coverage link for {ac_id} does not point to a tests/ path",
                    affected_acs=(ac_id,),
                )
            )

    return events


def _detect_test_drift(slug: str, root: Path) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    spec_content = _feature_peer_content(root, slug, "spec")
    quality_content = _feature_peer_content(root, slug, "quality")
    if spec_content is None or quality_content is None:
        return events

    cov_link_re = re.compile(r"- \[[ xX]\]\s+(AC\d{3})\s*->\s*(\S+)")

    spec_acs = set(_extract_acs_from_spec(spec_content))
    cov_links = cov_link_re.findall(quality_content)
    covered_acs: set[str] = set()
    for ac_id, target_path in cov_links:
        covered_acs.add(ac_id)
        if not (root / target_path).exists():
            events.append(
                DriftEvent(
                    event_type="test",
                    severity="high",
                    timestamp=_now_iso(),
                    description=f"Test coverage link references stale test file",
                    affected_acs=(ac_id,),
                )
            )

    uncovered_acs = sorted(spec_acs - covered_acs)
    if uncovered_acs:
        events.append(
            DriftEvent(
                event_type="test",
                severity="high",
                timestamp=_now_iso(),
                description="Spec ACs have no test coverage link in quality file",
                affected_acs=tuple(uncovered_acs),
            )
        )

    return events
