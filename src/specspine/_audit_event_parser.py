from __future__ import annotations

from ._audit_hash_utils import _hash_content
from .audit_models import AuditEvent, GIT_LOG_DATE_RE
from .features import FEATURE_FILE_PATHS

__all__ = [
    "_parse_audit_event_line",
    "_classify_event_type",
    "_compute_evidence_hash",
]


def _classify_event_type(message: str) -> str:
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ("status", "lifecycle", "transition")):
        return "lifecycle"
    if any(kw in msg_lower for kw in ("validat", "verif")):
        return "validation"
    if any(kw in msg_lower for kw in ("test", "coverage")):
        return "test"
    if any(kw in msg_lower for kw in ("drift", "consisten")):
        return "consistency"
    return "file_change"


def _filter_by_since(date_str: str, since: str | None) -> bool:
    if since is None:
        return True
    date_match = GIT_LOG_DATE_RE.match(date_str)
    if date_match:
        commit_date = date_match.group(0)
        if commit_date < since:
            return False
    return True


def _compute_evidence_hash(commit_hash: str, rel_paths: list[str], root, _run_git) -> str:
    content_parts: list[str] = []
    for rel in rel_paths:
        show_result = _run_git(["show", f"{commit_hash}:{rel}"], root)
        if show_result.returncode == 0:
            content_parts.append(show_result.stdout)
    return _hash_content("\n".join(content_parts)) if content_parts else ""


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
