from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .evolution import _run_git
from .features import (
    FEATURE_FILE_PATHS,
    feature_bundle_paths,
)

GIT_LOG_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")

__all__ = [
    "_build_drift_history",
    "_git_commit",
    "_run_git_log",
]


def _git_commit(root: Path) -> str:
    try:
        result = _run_git(["rev-parse", "HEAD"], root)
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def _run_git_log(root: Path, rel_paths: list[str]) -> list[str]:
    git_args = ["log", "--format=%H|%ai|%s", "--"] + rel_paths
    result = _run_git(git_args, root)
    if result.returncode != 0:
        return []
    return result.stdout.strip().splitlines()


def _build_drift_history(slug: str, root: Path, since: str | None) -> list:
    from .drift_models import DriftEvent

    events: list[DriftEvent] = []
    peer_files = feature_bundle_paths(root, slug)
    if not peer_files:
        return events

    rel_paths = []
    for kind in ("spec", "execution", "quality"):
        p = peer_files.get(kind)
        if p is not None and p.exists():
            try:
                rel_paths.append(str(p.relative_to(root)))
            except ValueError:
                pass

    if not rel_paths:
        return events

    lines = _run_git_log(root, rel_paths)
    for line in lines:
        parts = line.split("|", 2)
        if len(parts) < 2:
            continue
        commit_hash, date_str = parts[0], parts[1]
        message = parts[2] if len(parts) > 2 else ""

        if since is not None:
            date_match = GIT_LOG_DATE_RE.match(date_str)
            if date_match:
                commit_date = date_match.group(0)
                if commit_date < since:
                    continue

        event_type = "spec"
        for kind in ("spec", "execution", "quality"):
            rel = FEATURE_FILE_PATHS.get(kind, "").format(slug=slug)
            if rel in " ".join(rel_paths):
                event_type = kind
                break

        severity = "medium"
        if any(kw in message.lower() for kw in ("remove", "delete", "drop")):
            severity = "high"
        elif any(kw in message.lower() for kw in ("add", "new", "create")):
            severity = "low"

        events.append(
            DriftEvent(
                event_type=event_type,
                severity=severity,
                timestamp=date_str.strip(),
                description=f"Commit {commit_hash[:8]}: {message}",
            )
        )

    return events
