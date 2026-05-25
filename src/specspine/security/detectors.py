from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..features import (
    build_feature_handoff_report,
    build_feature_ready_report,
)
from .patterns import _CUE_PATTERNS
from .helpers import _is_within_root, _read_small_text

__all__ = [
    "_detect_cues",
    "_feature_evidence",
]


def _detect_cues(path: str, category: str, text: str) -> tuple[dict[str, Any], ...]:
    cues: list[dict[str, Any]] = []
    sequence = 1
    for line_number, line in enumerate(text.splitlines(), start=1):
        for keyword, pattern, severity, cue_category, message in _CUE_PATTERNS:
            if re.search(pattern, line, flags=re.IGNORECASE):
                cues.append(
                    {
                        "category": cue_category,
                        "id": f"{path}:{line_number}:{keyword}:{sequence}",
                        "keyword": keyword,
                        "line": line_number,
                        "message": message,
                        "path": path,
                        "severity": severity,
                    }
                )
                sequence += 1
    return tuple(cues)


def _feature_evidence(root: Path, slug: str) -> dict[str, Any]:
    handoff = build_feature_handoff_report(root, slug, require_coverage=True)
    ready = build_feature_ready_report(root, slug, require_coverage=True)
    return {
        "blocking_checks": [check.as_dict() for check in ready.blocking_checks],
        "feature_id": slug,
        "gaps": [dict(gap) for gap in ready.gaps],
        "has_native_files": handoff.has_native_files,
        "missing_files": list(ready.missing_files),
        "ready": ready.ready,
        "source_files": [
            str(source["path"])
            for source in handoff.sources.values()
            if source.get("exists")
        ],
        "status": ready.status,
    }
