from __future__ import annotations

import hashlib
from pathlib import Path

from .audit_models import (
    AuditEvent,
    GIT_LOG_DATE_RE,
    LIFECYCLE_STATUS_RE,
)
from .consistency import _read_text
from .evolution import _run_git
from .features import FEATURE_FILE_PATHS, feature_bundle_paths

__all__ = [
    "_build_lifecycle_transitions",
    "_collect_audit_events",
    "_feature_peer_content",
    "_hash_content",
]


def _feature_peer_content(root: Path, slug: str, kind: str) -> str | None:
    rel_path = FEATURE_FILE_PATHS.get(kind)
    if rel_path is None:
        return None
    path = root / rel_path.format(slug=slug)
    if not path.exists():
        return None
    return _read_text(path)


def _collect_audit_events(slug: str, root: Path, since: str | None) -> list[AuditEvent]:
    events: list[AuditEvent] = []
    peer_files = feature_bundle_paths(root, slug)
    if not peer_files:
        return events

    rel_paths: list[str] = []
    for kind in ("spec", "execution", "quality"):
        p = peer_files.get(kind)
        if p is not None and p.exists():
            try:
                rel_paths.append(str(p.relative_to(root)))
            except ValueError:
                pass

    if not rel_paths:
        return events

    git_args = ["log", "--format=%H|%ai|%an|%s", "--"] + rel_paths
    result = _run_git(git_args, root)
    if result.returncode != 0:
        return events

    for line in result.stdout.strip().splitlines():
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commit_hash, date_str, author, message = parts

        if since is not None:
            date_match = GIT_LOG_DATE_RE.match(date_str)
            if date_match:
                commit_date = date_match.group(0)
                if commit_date < since:
                    continue

        event_type = "file_change"
        msg_lower = message.lower()
        if any(kw in msg_lower for kw in ("status", "lifecycle", "transition")):
            event_type = "lifecycle"
        elif any(kw in msg_lower for kw in ("validat", "verif")):
            event_type = "validation"
        elif any(kw in msg_lower for kw in ("test", "coverage")):
            event_type = "test"
        elif any(kw in msg_lower for kw in ("drift", "consisten")):
            event_type = "consistency"

        content_parts: list[str] = []
        for kind in ("spec", "execution", "quality"):
            rel = FEATURE_FILE_PATHS.get(kind, "").format(slug=slug)
            show_result = _run_git(["show", f"{commit_hash}:{rel}"], root)
            if show_result.returncode == 0:
                content_parts.append(show_result.stdout)
        evidence_hash = _hash_content("\n".join(content_parts)) if content_parts else ""

        events.append(
            AuditEvent(
                event_type=event_type,
                timestamp=date_str.strip(),
                feature_id=slug,
                description=f"Commit {commit_hash[:8]}: {message}",
                evidence_hash=evidence_hash,
                actor=author.strip(),
            )
        )

    return events


def _build_lifecycle_transitions(slug: str, root: Path) -> list[dict[str, str]]:
    transitions: list[dict[str, str]] = []
    peer_files = feature_bundle_paths(root, slug)
    if not peer_files:
        return transitions

    rel_paths: list[str] = []
    for kind in ("spec", "execution", "quality"):
        p = peer_files.get(kind)
        if p is not None and p.exists():
            try:
                rel_paths.append(str(p.relative_to(root)))
            except ValueError:
                pass

    if not rel_paths:
        return transitions

    git_args = ["log", "--format=%H|%ai|%an|%s", "--diff-filter=ACDMR", "--"] + rel_paths
    result = _run_git(git_args, root)
    if result.returncode != 0:
        return transitions

    previous_status: str | None = None
    for line in result.stdout.strip().splitlines():
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        commit_hash, date_str, author, message = parts

        spec_rel = FEATURE_FILE_PATHS.get("spec", "").format(slug=slug)
        show_result = _run_git(["show", f"{commit_hash}:{spec_rel}"], root)
        if show_result.returncode != 0:
            continue

        status_match = LIFECYCLE_STATUS_RE.search(show_result.stdout)
        if status_match:
            current_status = status_match.group(1)
            if previous_status is None or current_status != previous_status:
                transitions.append({
                    "commit": commit_hash[:8],
                    "date": date_str.strip(),
                    "author": author.strip(),
                    "from_status": previous_status or "unknown",
                    "to_status": current_status,
                    "message": message,
                })
                previous_status = current_status

    return transitions


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
