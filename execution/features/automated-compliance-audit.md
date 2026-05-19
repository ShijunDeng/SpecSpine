# Automated Compliance & Audit Trail Execution

Feature ID: automated-compliance-audit
Status: implemented
Why: Generate compliance-ready audit reports from all spec-driven development evidence. Tracks feature lifecycle transitions, validation evidence, and drift history for regulatory compliance.

## Milestones

- TODO: List the meaningful delivery checkpoints.

## Tasks

- [ ] TODO: Break the work into implementation tasks.

## Dependencies

- TODO: Note upstream decisions, systems, people, or artifacts needed first.

## Open Questions

- TODO: Track questions that must be answered before or during implementation.

## Agent Handoff

- Run `specspine feature handoff automated-compliance-audit . --json` before implementation or review handoff.
- Run `specspine adapters handoff automated-compliance-audit . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks automated-compliance-audit . --json` for the focused implementation checklist.
- Run `specspine feature task-issues automated-compliance-audit . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace automated-compliance-audit . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests automated-compliance-audit . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature automated-compliance-audit --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature automated-compliance-audit --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature automated-compliance-audit --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix automated-compliance-audit . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature automated-compliance-audit --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature automated-compliance-audit --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature automated-compliance-audit --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature automated-compliance-audit --json` to compose local pre-merge review evidence.
- Run `specspine feature ready automated-compliance-audit . --json` after implementation evidence is complete.
- Run `specspine feature pr automated-compliance-audit . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan automated-compliance-audit . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan automated-compliance-audit . --output-dir .specspine/sync-plan/automated-compliance-audit` to materialize local sync review artifacts.
- Run `specspine feature archive automated-compliance-audit . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
