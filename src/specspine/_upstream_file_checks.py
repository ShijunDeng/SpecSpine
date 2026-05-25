from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .validation_fusion_utils import _check
from .validation_models import ValidationCheck

__all__ = [
    "ConfigCheckResult",
    "_check_adapter_config_exists",
]


@dataclass(frozen=True)
class ConfigCheckResult:
    check: ValidationCheck
    passed: bool
    target: Path | None = None


def _check_adapter_config_exists(
    key: str, upstream: dict[str, Any], root: Path
) -> ConfigCheckResult:
    adapter_path = upstream["config"]
    target = root / adapter_path
    if target.exists():
        return ConfigCheckResult(
            check=_check(
                f"fusion.adapter_config:{key}",
                "pass",
                f"{upstream['display_name']} adapter config exists: {adapter_path}",
            ),
            passed=True,
            target=target,
        )
    return ConfigCheckResult(
        check=_check(
            f"fusion.adapter_config:{key}",
            "fail",
            f"{upstream['display_name']} adapter config is missing: {adapter_path}",
        ),
        passed=False,
    )
