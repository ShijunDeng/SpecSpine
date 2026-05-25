from __future__ import annotations

from ..feature_bundle_models import FEATURE_FILE_PATHS

__all__ = [
    "_build_quality_template",
]


def _build_quality_template(slug: str, resolved_title: str, resolved_why: str) -> tuple[str, str]:
    return (
        FEATURE_FILE_PATHS["quality"].format(slug=slug),
        f"""
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
    )
