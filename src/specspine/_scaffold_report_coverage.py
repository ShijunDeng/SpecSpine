from __future__ import annotations

from pathlib import Path

from .features import (
    build_feature_trace_report,
    validate_feature_slug,
)
from .scaffold_generator import (
    _existing_coverage_links,
)

__all__ = [
    "ScaffoldCoverageContext",
    "compute_scaffold_coverage_context",
]


class ScaffoldCoverageContext:
    def __init__(
        self,
        slug: str,
        class_name: str,
        test_filename: str,
        test_path: str,
        covered_acs: set[str],
        trace_report,
    ) -> None:
        self.slug = slug
        self.class_name = class_name
        self.test_filename = test_filename
        self.test_path = test_path
        self.covered_acs = covered_acs
        self.trace_report = trace_report


def compute_scaffold_coverage_context(
    root: Path, slug: str
) -> ScaffoldCoverageContext:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    trace_report = build_feature_trace_report(resolved_root, slug)
    covered_acs = _existing_coverage_links(resolved_root, slug)
    from .scaffold_generator import _slug_to_camel

    camel = _slug_to_camel(slug)
    class_name = f"{camel}ScaffoldTests"
    test_filename = f"test_{slug.replace('-', '_')}_scaffold.py"
    test_path = f"tests/{test_filename}"

    return ScaffoldCoverageContext(
        slug=slug,
        class_name=class_name,
        test_filename=test_filename,
        test_path=test_path,
        covered_acs=covered_acs,
        trace_report=trace_report,
    )
