from __future__ import annotations

import shlex

from .adapter_models import (
    AdapterHandoffStep,
)

__all__ = [
    "_render_step_line",
]


def _render_step_line(step: AdapterHandoffStep) -> str:
    if step.argv:
        command = " ".join(shlex.quote(part) for part in step.argv)
        detail = f"`{command}`"
    else:
        detail = step.instruction
    return (
        f"- {step.id} ({step.kind}): {step.description} "
        f"executed=no safe_to_auto_run=no creates_remote=no "
        f"requires_network=no requires_token=no"
        + (f" - {detail}" if detail else "")
    )
