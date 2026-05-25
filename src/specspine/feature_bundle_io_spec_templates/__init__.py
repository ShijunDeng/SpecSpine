from __future__ import annotations

from ._spec_template_execution import _build_execution_template
from ._spec_template_quality import _build_quality_template
from ._spec_template_spec import _build_spec_template
from ..feature_bundle_validation import feature_title, validate_feature_slug
from ..feature_bundle_io_helpers import _feature_why

__all__ = [
    "build_feature_files",
]


def build_feature_files(
    slug: str,
    *,
    title: str | None = None,
    why: str | None = None,
) -> dict[str, str]:
    slug = validate_feature_slug(slug)
    resolved_title = feature_title(slug, title)
    resolved_why = _feature_why(why)

    spec_path, spec_content = _build_spec_template(slug, resolved_title, resolved_why)
    exec_path, exec_content = _build_execution_template(slug, resolved_title, resolved_why)
    quality_path, quality_content = _build_quality_template(slug, resolved_title, resolved_why)

    return {
        spec_path: spec_content,
        exec_path: exec_content,
        quality_path: quality_content,
    }
