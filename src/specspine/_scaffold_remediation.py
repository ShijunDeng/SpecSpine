from __future__ import annotations

from .scaffold_models import (
    ScaffoldRemediationStep,
)
from .scaffold_generator import (
    _generate_test_method,
)

__all__ = [
    "_build_remediation_plan",
]


def _build_remediation_plan(
    slug: str,
    uncovered_acs: list[dict[str, str]],
    test_path: str,
    class_name: str,
) -> list[ScaffoldRemediationStep]:
    steps = []
    for ac in uncovered_acs:
        method_info = _generate_test_method(ac["ac_id"], ac["ac_text"], slug)
        steps.append(
            ScaffoldRemediationStep(
                ac_id=ac["ac_id"],
                action=f"Implement {method_info['method_name']} in {test_path}",
                target_path=test_path,
                class_name=class_name,
                method_name=method_info["method_name"],
            )
        )
    return steps
