from __future__ import annotations

from typing import Any

from ._policy_scalar_utils import _clean_scalar
from ._policy_comment_strip import _strip_comment


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


__all__ = [
    "_parse_policy_subset",
]
