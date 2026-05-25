from __future__ import annotations

from pathlib import Path
from typing import Any

from .features import list_feature_bundles
from .policy import load_workspace_policy
from .status_readiness_helpers import (
    _readiness_next_actions,
    _readiness_detail_command,
    _invalid_readiness_record,
)
from .readiness_records import _build_readiness_record  # noqa: F401
from .readiness_aggregation import _aggregate_readiness_summary  # noqa: F401

__all__ = [
    "_readiness_next_actions",
    "_readiness_detail_command",
    "_invalid_readiness_record",
    "_build_readiness_record",
    "_aggregate_readiness_summary",
    "build_readiness_summary",
]


def build_readiness_summary(
    root: Path,
    features: list[dict[str, object]] | None = None,
    *,
    require_coverage: bool = False,
    use_policy: bool = False,
) -> dict[str, Any]:
    resolved_root = root.expanduser().resolve()
    feature_bundles = features if features is not None else list_feature_bundles(resolved_root)
    policy = load_workspace_policy(resolved_root) if use_policy else None
    records: list[dict[str, Any]] = []

    for feature in feature_bundles:
        record = _build_readiness_record(
            feature,
            resolved_root,
            require_coverage=require_coverage,
            use_policy=use_policy,
            policy=policy,
        )
        if record is not None:
            records.append(record)

    return _aggregate_readiness_summary(
        records,
        require_coverage=require_coverage,
        use_policy=use_policy,
        policy=policy,
    )
