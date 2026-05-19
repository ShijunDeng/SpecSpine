# Spec Evolution Tracker Execution

Feature ID: spec-evolution-tracker
Status: implemented
Why: Track spec changes over time, compute semantic diffs between versions, and assess downstream impact on tasks, tests, and dependent features.

## Milestones

- TODO: List the meaningful delivery checkpoints.

## Tasks

- [ ] TODO: Break the work into implementation tasks.

## Dependencies

- TODO: Note upstream decisions, systems, people, or artifacts needed first.

## Open Questions

- TODO: Track questions that must be answered before or during implementation.

## Agent Handoff

- Run `specspine feature handoff spec-evolution-tracker . --json` before implementation or review handoff.
- Run `specspine adapters handoff spec-evolution-tracker . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks spec-evolution-tracker . --json` for the focused implementation checklist.
- Run `specspine feature task-issues spec-evolution-tracker . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace spec-evolution-tracker . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests spec-evolution-tracker . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature spec-evolution-tracker --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature spec-evolution-tracker --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature spec-evolution-tracker --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix spec-evolution-tracker . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature spec-evolution-tracker --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature spec-evolution-tracker --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature spec-evolution-tracker --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature spec-evolution-tracker --json` to compose local pre-merge review evidence.
- Run `specspine feature ready spec-evolution-tracker . --json` after implementation evidence is complete.
- Run `specspine feature pr spec-evolution-tracker . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan spec-evolution-tracker . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan spec-evolution-tracker . --output-dir .specspine/sync-plan/spec-evolution-tracker` to materialize local sync review artifacts.
- Run `specspine feature archive spec-evolution-tracker . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
