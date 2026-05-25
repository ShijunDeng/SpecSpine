from __future__ import annotations

from ..feature_bundle_models import FEATURE_FILE_PATHS

__all__ = [
    "_build_spec_template",
]


def _build_spec_template(slug: str, resolved_title: str, resolved_why: str) -> tuple[str, str]:
    return (
        FEATURE_FILE_PATHS["spec"].format(slug=slug),
        f"""
            # {resolved_title}

            Feature ID: {slug}
            Status: proposed
            Priority: medium
            Owner: unassigned
            Milestone: unassigned
            Target Release: unassigned
            Project: unassigned
            Effort: unknown

            ## Why

            {resolved_why}

            ## Users

            - TODO: Identify the users or roles that benefit from this feature.

            ## Scope

            - TODO: Describe the behavior, workflows, and boundaries included in this feature.

            ## Non-Goals

            - TODO: Record what this feature intentionally will not address.

            ## Acceptance Criteria

            - [ ] TODO: Define one observable outcome that can be mapped directly to a test case.

            ## Edge Cases

            - TODO: Capture boundary, error, permission, migration, or rollback cases reviewers should check.

            ## Constraints

            - TODO: Note technical, operational, policy, compatibility, or timing constraints.

            ## Traceability Notes

            - TODO: Link acceptance criteria to tasks, tests, docs, rollout evidence, or review notes as work progresses.
        """,
    )
