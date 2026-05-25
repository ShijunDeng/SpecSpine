from __future__ import annotations

from typing import Any

from .validation_fusion_utils import _check
from .validation_models import ValidationCheck

__all__ = [
    "_handle_disabled_upstream",
    "_handle_missing_config",
]


def _handle_disabled_upstream(key: str, upstream: dict[str, Any]) -> list[ValidationCheck]:
    return [
        _check(
            f"fusion.adapter_config:{key}",
            "skip",
            f"{upstream['display_name']} is disabled; adapter config is not required.",
        ),
        _check(
            f"fusion.adapter_boundary:{key}",
            "skip",
            f"{upstream['display_name']} is disabled; adapter boundary docs are not required.",
        ),
    ]


def _handle_missing_config(key: str, upstream: dict[str, Any]) -> list[ValidationCheck]:
    adapter_path = upstream["config"]
    return [
        _check(
            f"fusion.adapter_boundary:{key}",
            "skip",
            f"{upstream['display_name']} adapter config is missing, so boundary docs cannot be checked.",
        ),
    ]
