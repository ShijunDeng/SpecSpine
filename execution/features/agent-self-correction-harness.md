# Agent Self-Correction Harness Execution

Feature ID: agent-self-correction-harness
Status: implemented
Why: Wire SpecSpine verification, coverage debt, and grading rubrics into deterministic feedback loops that produce LLM-consumable repair instructions. Turns SpecSpine from planning tool into behavior harness for autonomous coding agents.

## Milestones

- TODO: List the meaningful delivery checkpoints.

## Tasks

- [ ] TODO: Break the work into implementation tasks.

## Dependencies

- TODO: Note upstream decisions, systems, people, or artifacts needed first.

## Open Questions

- TODO: Track questions that must be answered before or during implementation.

## Agent Handoff

- Run `specspine feature handoff agent-self-correction-harness . --json` before implementation or review handoff.
- Run `specspine adapters handoff agent-self-correction-harness . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks agent-self-correction-harness . --json` for the focused implementation checklist.
- Run `specspine feature task-issues agent-self-correction-harness . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace agent-self-correction-harness . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests agent-self-correction-harness . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature agent-self-correction-harness --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature agent-self-correction-harness --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature agent-self-correction-harness --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix agent-self-correction-harness . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature agent-self-correction-harness --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature agent-self-correction-harness --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature agent-self-correction-harness --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature agent-self-correction-harness --json` to compose local pre-merge review evidence.
- Run `specspine feature ready agent-self-correction-harness . --json` after implementation evidence is complete.
- Run `specspine feature pr agent-self-correction-harness . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan agent-self-correction-harness . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan agent-self-correction-harness . --output-dir .specspine/sync-plan/agent-self-correction-harness` to materialize local sync review artifacts.
- Run `specspine feature archive agent-self-correction-harness . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
