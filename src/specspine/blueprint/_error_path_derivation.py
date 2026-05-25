from __future__ import annotations

import re

from .blueprint_extraction import _extract_ac_ids
from .blueprint_models import (
    BlueprintErrorPath,
    _ERROR_INDICATORS,
)

__all__ = [
    "_derive_error_paths",
]


def _derive_error_paths(
    ac_list: list[dict[str, str]],
    slug: str,
) -> list[BlueprintErrorPath]:
    error_paths: list[BlueprintErrorPath] = []

    for ac in ac_list:
        text = ac.get("full_text", ac["text"])
        lower = text.lower()
        ac_ids = _extract_ac_ids(text)

        if not any(indicator in lower for indicator in _ERROR_INDICATORS):
            continue

        condition = text.strip()
        if "when" in lower:
            cond_match = re.search(r"when\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
            if cond_match:
                condition = cond_match.group(1).strip()
        elif "if" in lower:
            cond_match = re.search(r"if\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
            if cond_match:
                condition = cond_match.group(1).strip()

        exception_type = "ValueError"
        if any(w in lower for w in ("missing", "not found", "absent")):
            exception_type = "FileNotFoundError"
        elif any(w in lower for w in ("timeout", "unavailable")):
            exception_type = "TimeoutError"
        elif any(w in lower for w in ("reject", "refuse", "invalid")):
            exception_type = "ValueError"
        elif any(w in lower for w in ("error", "fail")):
            exception_type = "RuntimeError"

        handling = f"Log the error and return a failure indication for: {condition}"

        error_paths.append(
            BlueprintErrorPath(
                condition=condition,
                exception_type=exception_type,
                handling=handling,
                ac_ids=ac_ids,
            )
        )

    return error_paths
