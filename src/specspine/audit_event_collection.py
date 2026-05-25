from __future__ import annotations

import hashlib
from pathlib import Path

from .audit_models import AuditEvent, GIT_LOG_DATE_RE
from .features import FEATURE_FILE_PATHS, feature_bundle_paths
from .evolution import _run_git

__all__ = [
    "_collect_audit_events",
    "_hash_content",
]


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


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
