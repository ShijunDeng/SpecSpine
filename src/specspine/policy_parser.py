from __future__ import annotations

from typing import Any

from .features import FEATURE_PRIORITIES, FEATURE_STATUSES
from .policy_models import ReadinessCoveragePolicy


def _clean_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:index]
    return line


def _parse_policy_subset(content: str) -> dict[str, object]:
    require_coverage: dict[str, object] = {}
    current_list: str | None = None
    in_readiness = False
    in_require_coverage = False

    for raw_line in content.splitlines():
        line = _strip_comment(raw_line).rstrip()
        stripped = line.strip()
        if not stripped:
            continue

        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            in_readiness = stripped == "readiness:"
            in_require_coverage = False
            current_list = None
            continue

        if not in_readiness:
            continue

        if indent == 2:
            in_require_coverage = stripped == "require_coverage:"
            current_list = None
            continue

        if not in_require_coverage:
            continue

        if indent == 4 and stripped.endswith(":"):
            current_list = stripped[:-1].strip()
            require_coverage.setdefault(current_list, [])
            continue

        if indent == 4 and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_list = None
            require_coverage[key.strip()] = _clean_scalar(value)
            continue

        if indent >= 6 and current_list and stripped.startswith("- "):
            values = require_coverage.setdefault(current_list, [])
            if isinstance(values, list):
                values.append(str(_clean_scalar(stripped[2:])))

    return require_coverage


def _dedupe_strings(values: object) -> tuple[str, ...]:
    if not isinstance(values, list):
        return ()

    deduped: list[str] = []
    for value in values:
        normalized = str(value).strip().lower()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return tuple(deduped)


def _build_require_coverage_policy(values: dict[str, object]) -> ReadinessCoveragePolicy:
    warnings: list[str] = []
    enabled = values.get("enabled", False)
    default = values.get("default", False)
    if not isinstance(enabled, bool):
        warnings.append("readiness.require_coverage.enabled must be true or false.")
        enabled = False
    if not isinstance(default, bool):
        warnings.append("readiness.require_coverage.default must be true or false.")
        default = False

    priorities = _dedupe_strings(values.get("priorities", []))
    statuses = _dedupe_strings(values.get("statuses", []))
    feature_ids = _dedupe_strings(values.get("feature_ids", []))

    for priority in priorities:
        if priority not in FEATURE_PRIORITIES:
            warnings.append(f"Unknown readiness.require_coverage priority: {priority}.")
    for status in statuses:
        if status not in FEATURE_STATUSES:
            warnings.append(f"Unknown readiness.require_coverage status: {status}.")

    return ReadinessCoveragePolicy(
        enabled=enabled,
        default=default,
        priorities=tuple(priority for priority in priorities if priority in FEATURE_PRIORITIES),
        statuses=tuple(status for status in statuses if status in FEATURE_STATUSES),
        feature_ids=feature_ids,
        warnings=tuple(warnings),
    )


__all__ = [
    "_build_require_coverage_policy",
    "_clean_scalar",
    "_dedupe_strings",
    "_parse_policy_subset",
    "_strip_comment",
]
