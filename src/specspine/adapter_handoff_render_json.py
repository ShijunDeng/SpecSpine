from __future__ import annotations

import json

from .adapter_handoff_render_utils import adapter_feature_handoff_focused_payload


def render_adapter_feature_handoff_json(report) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_adapter_feature_handoff_adapter_json(
    report,
    adapter_key: str,
) -> str:
    return (
        json.dumps(
            adapter_feature_handoff_focused_payload(report, adapter_key),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


__all__ = [
    "render_adapter_feature_handoff_json",
    "render_adapter_feature_handoff_adapter_json",
]
