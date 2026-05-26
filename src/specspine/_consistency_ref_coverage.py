from __future__ import annotations

from .consistency_models import (
    ConsistencyReference,
)
from .consistency_utils import (
    _dedupe_references,
)

__all__ = [
    "_coverage_references",
]


def _coverage_references(report) -> tuple[ConsistencyReference, ...]:
    references = []
    for link in report.test_coverage:
        if not link.target_path.startswith("tests/"):
            continue
        references.append(
            ConsistencyReference(
                path=link.target_path,
                line=link.line,
                kind="test",
                matched=link.acceptance_criterion_id,
                exists=link.target_exists,
            )
        )
    return _dedupe_references(references)
