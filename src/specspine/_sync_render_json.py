from __future__ import annotations

import json

from .feature_bundle import FeatureSyncPlan

__all__ = [
    "render_feature_sync_plan_json",
]


def render_feature_sync_plan_json(plan: FeatureSyncPlan) -> str:
    return json.dumps(plan.as_dict(), indent=2, sort_keys=True) + "\n"
