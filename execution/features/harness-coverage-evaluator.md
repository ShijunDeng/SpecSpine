# Harness Coverage Evaluator Execution

Feature ID: harness-coverage-evaluator
Status: proposed
Why: Evaluate harness coverage and quality across all 8 governed dimensions. Identify blind spots, detect sensor redundancy, generate improvement plans, and track harness maturity trends over time.

## Milestones

- TODO: List the meaningful delivery checkpoints.

## Tasks

- [ ] TODO: Break the work into implementation tasks.

## Dependencies

- TODO: Note upstream decisions, systems, people, or artifacts needed first.

## Open Questions

- TODO: Track questions that must be answered before or during implementation.

## Agent Handoff

- Run `specspine feature handoff harness-coverage-evaluator . --json` before implementation or review handoff.
- Run `specspine adapters handoff harness-coverage-evaluator . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks harness-coverage-evaluator . --json` for the focused implementation checklist.
- Run `specspine feature task-issues harness-coverage-evaluator . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace harness-coverage-evaluator . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests harness-coverage-evaluator . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature harness-coverage-evaluator --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature harness-coverage-evaluator --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature harness-coverage-evaluator --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix harness-coverage-evaluator . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature harness-coverage-evaluator --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature harness-coverage-evaluator --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature harness-coverage-evaluator --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature harness-coverage-evaluator --json` to compose local pre-merge review evidence.
- Run `specspine feature ready harness-coverage-evaluator . --json` after implementation evidence is complete.
- Run `specspine feature pr harness-coverage-evaluator . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan harness-coverage-evaluator . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan harness-coverage-evaluator . --output-dir .specspine/sync-plan/harness-coverage-evaluator` to materialize local sync review artifacts.
- Run `specspine feature archive harness-coverage-evaluator . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
