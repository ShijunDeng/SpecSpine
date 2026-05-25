from __future__ import annotations

from pathlib import Path

from ..features import InvalidFeatureSlug, validate_feature_slug

__all__ = [
    "MAX_TEXT_BYTES",
    "_classify_changed_file",
    "_feature_slug_from_path",
    "_read_small_text",
]

MAX_TEXT_BYTES = 128 * 1024


def _classify_changed_file(path: str) -> str:
    if path.startswith("src/specspine/") and path.endswith(".py"):
        return "source"
    if path.startswith("tests/test_") and path.endswith(".py"):
        return "test"
    if path.startswith("specs/features/") and path.endswith(".md"):
        return "feature-spec"
    if path.startswith("execution/features/") and path.endswith(".md"):
        return "feature-execution"
    if path.startswith("quality/features/") and path.endswith(".md"):
        return "feature-quality"
    if (
        path in {"README.md", "AGENTS.md"}
        or path.startswith("docs/")
        or path
        in {
            "execution/plan.md",
            "quality/review.md",
            "specs/architecture.md",
            "specs/product.md",
        }
    ):
        return "project-doc"
    if path == "pyproject.toml" or path.startswith(".github/") or path.startswith(
        ".specspine/"
    ):
        return "config"
    return "other"


def _feature_slug_from_path(path: str) -> str | None:
    for prefix in ("specs/features/", "execution/features/", "quality/features/"):
        if path.startswith(prefix) and path.endswith(".md"):
            slug = path.removeprefix(prefix).removesuffix(".md")
            if "/" not in slug:
                try:
                    return validate_feature_slug(slug)
                except InvalidFeatureSlug:
                    return None
    return None


def _read_small_text(path: Path) -> tuple[str | None, str | None]:
    try:
        stat = path.stat()
    except OSError as error:
        return None, f"stat_error:{error.__class__.__name__}"
    if not path.is_file():
        return None, "not_file"
    if stat.st_size > MAX_TEXT_BYTES:
        return None, "too_large"
    try:
        raw = path.read_bytes()
    except OSError as error:
        return None, f"read_error:{error.__class__.__name__}"
    if b"\0" in raw:
        return None, "binary"
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError:
        try:
            return raw.decode("utf-8", errors="replace"), None
        except UnicodeDecodeError:
            return None, "decode_error"
