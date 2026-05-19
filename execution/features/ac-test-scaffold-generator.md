# AC-to-Test Scaffold Generator Execution

Feature ID: ac-test-scaffold-generator
Status: implemented
Why: Generate structured test scaffolds from acceptance criteria to close coverage gaps identified in retrospective. Provides deterministic test scaffolds for humans and AI agents to implement.

## Milestones

- [x] Implement core scaffold dataclasses and utility functions
- [x] Implement test method generation from AC text
- [x] Implement test class generation with proper formatting
- [x] Implement coverage link extraction from quality files
- [x] Implement remediation plan generation
- [x] Implement build_ac_test_scaffold main function
- [x] Implement JSON and text renderers
- [x] Wire into CLI as `specspine scaffold` command
- [x] Write comprehensive unit tests

## Tasks

- [x] Define ScaffoldTestMethod, ScaffoldCoverageLink, ScaffoldSkippedCriterion, ScaffoldRemediationStep, and ScaffoldReport dataclasses
- [x] Implement _slug_to_camel, _ac_id_snake, _extract_ac_keyword utilities
- [x] Implement _generate_test_method to create method dict from AC
- [x] Implement _generate_test_class to produce full test class source
- [x] Implement _existing_coverage_links to parse quality file for covered ACs
- [x] Implement _update_quality_file for optional quality file updates
- [x] Implement _build_remediation_plan for actionable remediation steps
- [x] Implement build_ac_test_scaffold as main orchestration function
- [x] Implement render_scaffold_json and render_scaffold_text
- [x] Register `scaffold` subcommand in cli.py with --json flag

## Dependencies

- Feature trace report (build_feature_trace_report) for AC extraction.
- Feature bundle path resolution (feature_bundle_paths).
- Test coverage parsing (parse_test_coverage).

## Open Questions

- None; feature is implemented and tested.

## Agent Handoff

- Run `specspine feature handoff ac-test-scaffold-generator . --json` before implementation or review handoff.
- Run `specspine adapters handoff ac-test-scaffold-generator . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks ac-test-scaffold-generator . --json` for the focused implementation checklist.
- Run `specspine feature task-issues ac-test-scaffold-generator . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace ac-test-scaffold-generator . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests ac-test-scaffold-generator . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature ac-test-scaffold-generator --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature ac-test-scaffold-generator --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature ac-test-scaffold-generator --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix ac-test-scaffold-generator . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature ac-test-scaffold-generator --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature ac-test-scaffold-generator --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature ac-test-scaffold-generator --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature ac-test-scaffold-generator --json` to compose local pre-merge review evidence.
- Run `specspine feature ready ac-test-scaffold-generator . --json` after implementation evidence is complete.
- Run `specspine feature pr ac-test-scaffold-generator . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan ac-test-scaffold-generator . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan ac-test-scaffold-generator . --output-dir .specspine/sync-plan/ac-test-scaffold-generator` to materialize local sync review artifacts.
- Run `specspine feature archive ac-test-scaffold-generator . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
