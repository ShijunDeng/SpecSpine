from __future__ import annotations

from pathlib import Path

__all__ = [
    "_read_peer_file",
]


def _read_peer_file(
    slug: str,
    kind: str,
    target: Path,
    relative_path: str,
) -> tuple[str | None, list]:
    try:
        content = target.read_text(encoding="utf-8")
        return content, []
    except OSError:
        from .validation_feature_helpers import _check
        error_check = _check(
            f"feature.readable:{slug}:{kind}",
            "fail",
            f"Feature {slug} {kind} file could not be read: {relative_path}",
        )
        return None, [error_check]
