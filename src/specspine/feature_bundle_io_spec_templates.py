from __future__ import annotations

from .feature_bundle_models import FEATURE_FILE_PATHS
from .feature_bundle_validation import validate_feature_slug, feature_title
from .feature_bundle_io_helpers import _feature_why

__all__ = [
    "build_feature_files",
]


def build_feature_files(
    slug: str,
    *,
    title: str | None = None,
    why: str | None = None,
) -> dict[str, str]:
    slug = validate_feature_slug(slug)
    resolved_title = feature_title(slug, title)
    resolved_why = _feature_why(why)

    return {
        FEATURE_FILE_PATHS["spec"].format(slug=slug): f"""
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
        FEATURE_FILE_PATHS["execution"].format(slug=slug): f"""
            # {resolved_title} Execution

            Feature ID: {slug}
            Status: proposed
            Why: {resolved_why}

            ## Milestones

            - TODO: List the meaningful delivery checkpoints.

            ## Tasks

            - [ ] TODO: Break the work into implementation tasks.

            ## Dependencies

            - TODO: Note upstream decisions, systems, people, or artifacts needed first.

            ## Open Questions

            - TODO: Track questions that must be answered before or during implementation.

            ## Agent Handoff

            - Run `specspine feature handoff {slug} . --json` before implementation or review handoff.
            - Run `specspine adapters handoff {slug} . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
            - Run `specspine feature tasks {slug} . --json` for the focused implementation checklist.
            - Run `specspine feature task-issues {slug} . --json` to draft one local GitHub issue per execution task.
            - Run `specspine feature trace {slug} . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
            - Run `specspine feature tests {slug} . --json` to build the acceptance-test packet.
            - Run `specspine tests impact . --feature {slug} --json` to inspect local source-to-test impact recommendations.
            - Run `specspine consistency scan . --feature {slug} --json` to inspect local spec-code-test-doc drift.
            - Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
            - Run `specspine retrospective report . --json` before planning the next iteration.
            - Run `specspine coverage plan . --feature {slug} --json` when missing AC coverage needs read-only remediation steps.
            - Run `specspine verify matrix {slug} . --json` to inspect AC-level verification evidence.
            - Run `specspine change risk . --feature {slug} --json` to inspect local changed-path risk evidence.
            - Run `specspine security cues . --feature {slug} --json` to inspect local security-sensitive review cues.
            - Run `specspine provenance manifest . --feature {slug} --json` to hash local evidence artifacts before review or archive.
            - Run `specspine review packet . --feature {slug} --json` to compose local pre-merge review evidence.
            - Run `specspine feature ready {slug} . --json` after implementation evidence is complete.
            - Run `specspine feature pr {slug} . --json` to draft local Pull Request review notes.
            - Run `specspine feature sync-plan {slug} . --json` to review GitHub CLI sync intent without executing it.
            - Run `specspine feature sync-plan {slug} . --output-dir .specspine/sync-plan/{slug}` to materialize local sync review artifacts.
            - Run `specspine feature archive {slug} . --json` to package local archive evidence before lifecycle closure.
            - Run `specspine validate . --fusion --features` before handoff or release.
        """,
        FEATURE_FILE_PATHS["quality"].format(slug=slug): f"""
            # {resolved_title} Quality

            Feature ID: {slug}
            Status: proposed
            Why: {resolved_why}

            ## Required Checks

            - [ ] TODO: Acceptance criteria are reviewed against implementation evidence.
            - [ ] TODO: Test coverage proves the changed behavior and edge cases.
            - [ ] TODO: Documentation, release notes, or PR draft reflect user-facing behavior.
            - [ ] TODO: `specspine feature ready {slug} . --json` has no blocking checks after evidence is complete.
            - [ ] TODO: `specspine validate . --fusion --features` passes.

            ## Test Coverage

            Use `- [ ] AC001 -> tests/...` to link existing local test files or test selectors.

            - [ ] AC001 -> tests/...

            ## Test Plan

            - TODO: Add unit, integration, CLI, manual, or exploratory checks that prove each acceptance criterion.

            ## Review Notes

            - TODO: Capture review findings, decisions, and follow-up work.

            ## Release Readiness

            - [ ] TODO: Acceptance criteria, tasks, required checks, and test plan evidence are complete.
            - [ ] TODO: Docs, release notes, or `specspine feature pr {slug} . --json` output are ready for reviewers.
            - [ ] TODO: `specspine tests impact . --feature {slug} --json` has been reviewed for focused local test commands.
            - [ ] TODO: `specspine consistency scan . --feature {slug} --json` has been reviewed for local spec-code-test-doc drift.
            - [ ] TODO: `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted repository residue.
            - [ ] TODO: `specspine retrospective report . --json` has been reviewed for local feature improvement signals.
            - [ ] TODO: `specspine coverage plan . --feature {slug} --json` has been reviewed if missing AC coverage remains.
            - [ ] TODO: `specspine verify matrix {slug} . --json` has been reviewed for AC-level verification evidence.
            - [ ] TODO: `specspine change risk . --feature {slug} --json` has been reviewed for changed-path risk evidence.
            - [ ] TODO: `specspine security cues . --feature {slug} --json` has been reviewed for security-sensitive cues.
            - [ ] TODO: `specspine provenance manifest . --feature {slug} --json` has been reviewed for local evidence hashes.
            - [ ] TODO: `specspine review packet . --feature {slug} --json` has been reviewed for local pre-merge evidence.
            - [ ] TODO: `specspine feature sync-plan {slug} . --json` or `--output-dir .specspine/sync-plan/{slug}` has been reviewed before any remote GitHub sync.
            - [ ] TODO: `specspine feature archive {slug} . --json` has been reviewed before marking status archived.
            - [ ] TODO: `specspine feature ready {slug} . --json` and `specspine validate . --fusion --features` have been run.
            - [ ] TODO: No known blockers remain, or blockers are documented in review notes.
        """,
    }
