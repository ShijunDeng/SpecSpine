# Feature Impact Analysis Execution

Feature ID: feature-impact-analysis
Status: proposed
Why: Analyze the downstream impact of feature changes before implementation. Predict which features, tests, and code will be affected by proposed spec modifications.

## Milestones

- TODO: List the meaningful delivery checkpoints.

## Tasks

- [ ] TODO: Break the work into implementation tasks.

## Dependencies

- TODO: Note upstream decisions, systems, people, or artifacts needed first.

## Open Questions

- TODO: Track questions that must be answered before or during implementation.

## Agent Handoff

- Run `specspine feature handoff feature-impact-analysis . --json` before implementation or review handoff.
- Run `specspine adapters handoff feature-impact-analysis . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks feature-impact-analysis . --json` for the focused implementation checklist.
- Run `specspine feature task-issues feature-impact-analysis . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace feature-impact-analysis . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests feature-impact-analysis . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature feature-impact-analysis --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature feature-impact-analysis --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature feature-impact-analysis --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix feature-impact-analysis . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature feature-impact-analysis --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature feature-impact-analysis --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature feature-impact-analysis --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature feature-impact-analysis --json` to compose local pre-merge review evidence.
- Run `specspine feature ready feature-impact-analysis . --json` after implementation evidence is complete.
- Run `specspine feature pr feature-impact-analysis . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan feature-impact-analysis . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan feature-impact-analysis . --output-dir .specspine/sync-plan/feature-impact-analysis` to materialize local sync review artifacts.
- Run `specspine feature archive feature-impact-analysis . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
