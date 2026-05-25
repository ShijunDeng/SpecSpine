from __future__ import annotations

from pathlib import Path

from .feature_bundle_models import FeatureBundleExistsError
from .feature_bundle_validation import validate_feature_slug
from .workspace import normalize_template
from .feature_bundle_io_spec_templates import build_feature_files

__all__ = [
    "create_feature_bundle",
]


def create_feature_bundle(
    root: Path,
    slug: str,
    *,
    title: str | None = None,
    why: str | None = None,
    force: bool = False,
) -> list[Path]:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    files = build_feature_files(slug, title=title, why=why)
    targets = {
        relative_path: resolved_root / relative_path
        for relative_path in files
    }
    existing_paths = tuple(path for path in targets.values() if path.exists())

    if existing_paths and not force:
        raise FeatureBundleExistsError(slug=slug, existing_paths=existing_paths)

    written: list[Path] = []
    for relative_path, content in files.items():
        target = targets[relative_path]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(normalize_template(content), encoding="utf-8")
        written.append(target)

    return written
