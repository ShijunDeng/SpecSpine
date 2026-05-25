from __future__ import annotations

from .adapter_handoff_render import (
    render_adapter_feature_handoff_adapter_json,
    render_adapter_feature_handoff_adapter_text,
    render_adapter_feature_handoff_json,
    render_adapter_feature_handoff_text,
)
from .adapter_models import (
    AdapterFeatureHandoffReport,
    ADAPTER_SPECS,
)

__all__ = [
    "_build_adapter_handoff_content",
]


def _build_adapter_handoff_content(
    report: AdapterFeatureHandoffReport,
) -> dict[str, str]:
    content_by_relative_path: dict[str, str] = {
        "combined.md": render_adapter_feature_handoff_text(report),
        "combined.json": render_adapter_feature_handoff_json(report),
    }
    for key in ADAPTER_SPECS:
        content_by_relative_path[f"adapters/{key}.md"] = (
            render_adapter_feature_handoff_adapter_text(report, key)
        )
        content_by_relative_path[f"adapters/{key}.json"] = (
            render_adapter_feature_handoff_adapter_json(report, key)
        )
    return content_by_relative_path
