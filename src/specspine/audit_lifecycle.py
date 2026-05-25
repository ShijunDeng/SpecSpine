from __future__ import annotations

from pathlib import Path

from .audit_models import LIFECYCLE_STATUS_RE
from .features import FEATURE_FILE_PATHS, feature_bundle_paths
from .evolution import _run_git

__all__ = [
    "_build_lifecycle_transitions",
]


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
