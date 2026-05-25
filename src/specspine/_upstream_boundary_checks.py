from __future__ import annotations

from typing import Any

from .validation_fusion_utils import _check
from .validation_models import ValidationCheck

__all__ = [
    "_check_adapter_boundary",
]


def _check_adapter_boundary(
    key: str, upstream: dict[str, Any], content: str
) -> ValidationCheck:
    has_boundary = "no vendored source code" in content or "no vendored" in content
    return _check(
        f"fusion.adapter_boundary:{key}",
        "pass" if has_boundary else "fail",
        f"{upstream['display_name']} adapter docs state the no-vendored-code boundary."
        if has_boundary
        else f"{upstream['display_name']} adapter docs must state a no-vendored-code boundary.",
    )
