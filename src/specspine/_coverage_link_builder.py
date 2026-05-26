from __future__ import annotations

import re
from pathlib import Path

from .feature_bundle_models import (
    AC_ID_RE,
    FeatureTestCoverageLink,
)
from .feature_bundle_coverage_helpers import (
    _strip_markdown_code,
    _test_coverage_target_path,
)

__all__ = [
    "build_coverage_link",
]


def build_coverage_link(
    text: str,
    marker: str,
    line_number: int,
    source_file: str,
    resolved_root: Path,
    link_index: int,
) -> FeatureTestCoverageLink:
    normalized_text = text.strip()
    ac_match = AC_ID_RE.search(normalized_text)
    acceptance_criterion_id = (
        ac_match.group(0).upper() if ac_match is not None else "unknown"
    )
    target = ""
    if "->" in normalized_text:
        _left, right = normalized_text.split("->", 1)
        target = _strip_markdown_code(right)
    target_path = _test_coverage_target_path(target)
    target_path_obj = Path(target_path)
    target_exists = (
        bool(target)
        and not target_path_obj.is_absolute()
        and (resolved_root / target_path_obj).exists()
    )
    return FeatureTestCoverageLink(
        id=f"COV{link_index + 1:03d}",
        acceptance_criterion_id=acceptance_criterion_id,
        target=target,
        target_path=target_path,
        target_exists=target_exists,
        done=marker.lower() == "x",
        text=normalized_text,
        source_file=source_file,
        line=line_number,
    )
