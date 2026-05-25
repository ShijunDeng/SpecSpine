from __future__ import annotations

from ..audit_models import AuditEvent
from ..features import FEATURE_FILE_PATHS
from ._classifier import _classify_event_type, _filter_by_since
from ._evidence import _compute_evidence_hash

__all__ = [
    "_parse_audit_event_line",
]


def _parse_audit_event_line(
    line: str,
    since: str | None,
    slug: str,
    root,
    _run_git,
) -> AuditEvent | None:
    parts = line.split("|", 3)
    if len(parts) < 4:
        return None

    commit_hash, date_str, author, message = parts

    if not _filter_by_since(date_str, since):
        return None

    event_type = _classify_event_type(message)

    rel_paths = []
    for kind in ("spec", "execution", "quality"):
        rel = FEATURE_FILE_PATHS.get(kind, "").format(slug=slug)
        rel_paths.append(rel)

    evidence_hash = _compute_evidence_hash(commit_hash, rel_paths, root, _run_git)

    return AuditEvent(
        event_type=event_type,
        timestamp=date_str.strip(),
        feature_id=slug,
        description=f"Commit {commit_hash[:8]}: {message}",
        evidence_hash=evidence_hash,
        actor=author.strip(),
    )
