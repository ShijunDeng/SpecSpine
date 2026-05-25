from __future__ import annotations

from .._audit_hash_utils import _hash_content

__all__ = [
    "_compute_evidence_hash",
]


def _compute_evidence_hash(commit_hash: str, rel_paths: list[str], root, _run_git) -> str:
    content_parts: list[str] = []
    for rel in rel_paths:
        show_result = _run_git(["show", f"{commit_hash}:{rel}"], root)
        if show_result.returncode == 0:
            content_parts.append(show_result.stdout)
    return _hash_content("\n".join(content_parts)) if content_parts else ""
