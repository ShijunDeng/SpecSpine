from __future__ import annotations

from pathlib import Path

from ..features import InvalidFeatureSlug, validate_feature_slug

__all__ = [
    "MAX_TEXT_BYTES",
    "_relative_path",
    "_normalise_changed_file",
    "_classify_changed_file",
    "_feature_slug_from_path",
    "_dedupe",
    "_is_within_root",
    "_read_small_text",
]

MAX_TEXT_BYTES = 128 * 1024


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _normalise_changed_file(root: Path, value: str) -> tuple[str, Path]:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    return _relative_path(root, resolved), resolved


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


def _dedupe(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            deduped.append(value)
            seen.add(value)
    return tuple(deduped)


def _is_within_root(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


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
