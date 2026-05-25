from __future__ import annotations

from ..feature_bundle_models import FEATURE_FILE_PATHS

__all__ = [
    "_build_execution_template",
]


def _build_execution_template(slug: str, resolved_title: str, resolved_why: str) -> tuple[str, str]:
    return (
        FEATURE_FILE_PATHS["execution"].format(slug=slug),
        f"""
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
    )
