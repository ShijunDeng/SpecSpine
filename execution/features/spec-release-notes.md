# Spec-Backed Release Notes & Changelog Generation Execution

Feature ID: spec-release-notes
Status: implemented
Why: Aggregate validated and archived feature evidence into structured, user-facing release communication. Closes the last mile gap in spec-to-PR pipeline with deterministic, multi-format release artifacts.

## Milestones

- TODO: List the meaningful delivery checkpoints.

## Tasks

- [ ] TODO: Break the work into implementation tasks.

## Dependencies

- TODO: Note upstream decisions, systems, people, or artifacts needed first.

## Open Questions

- TODO: Track questions that must be answered before or during implementation.

## Agent Handoff

- Run `specspine feature handoff spec-release-notes . --json` before implementation or review handoff.
- Run `specspine adapters handoff spec-release-notes . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks spec-release-notes . --json` for the focused implementation checklist.
- Run `specspine feature task-issues spec-release-notes . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace spec-release-notes . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests spec-release-notes . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature spec-release-notes --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature spec-release-notes --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature spec-release-notes --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix spec-release-notes . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature spec-release-notes --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature spec-release-notes --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature spec-release-notes --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature spec-release-notes --json` to compose local pre-merge review evidence.
- Run `specspine feature ready spec-release-notes . --json` after implementation evidence is complete.
- Run `specspine feature pr spec-release-notes . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan spec-release-notes . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan spec-release-notes . --output-dir .specspine/sync-plan/spec-release-notes` to materialize local sync review artifacts.
- Run `specspine feature archive spec-release-notes . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
