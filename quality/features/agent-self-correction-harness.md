# Agent Self-Correction Harness Quality

Feature ID: agent-self-correction-harness
Status: implemented
Why: Wire SpecSpine verification, coverage debt, and grading rubrics into deterministic feedback loops that produce LLM-consumable repair instructions. Turns SpecSpine from planning tool into behavior harness for autonomous coding agents.

## Required Checks

- [x] QC001: All 10 acceptance criteria verified against harness.py implementation - dataclasses, sensors, repair strategies, root causes, quality scoring, and renderers match spec.
- [x] QC002: Test coverage in test_harness.py proves computational sensors (verification_matrix, coverage_debt, grading_rubric, validation_contract) return correct pass/fail status.
- [x] QC003: Test coverage proves inferential sensors (consistency_scan, hygiene_scan, security_cues, change_risk) return correct pass/fail status with output metrics.
- [x] QC004: `specspine feature ready agent-self-correction-harness . --json` has no blocking checks after evidence is complete.
- [x] QC005: `specspine validate . --fusion --features` passes.

## Test Coverage

Use `- [ ] AC001 -> tests/...` to link existing local test files or test selectors.

- [x] AC001 -> tests/test_harness.py
- [x] AC002 -> tests/test_harness.py
- [x] AC003 -> tests/test_harness.py
- [x] AC004 -> tests/test_harness.py
- [x] AC005 -> tests/test_harness.py
- [x] AC006 -> tests/test_harness.py
- [x] AC007 -> tests/test_harness.py
- [x] AC008 -> tests/test_harness.py
- [x] AC009 -> tests/test_harness.py
- [x] AC010 -> tests/test_harness.py

## Test Plan

- Unit tests for HarnessFeedbackSensor, RepairStrategy, HarnessQualityReport, HarnessFeedbackReport dataclasses and as_dict methods.
- Unit tests for _run_computational_sensors with mocked verification_matrix, coverage_debt, grading_rubric, and validation_contract responses.
- Unit tests for _run_inferential_sensors with mocked consistency_scan, hygiene_scan, security_cues, and change_risk responses.
- Unit tests for _generate_repair_strategies verifying AC-specific and SENSOR_FAILURE strategy generation.
- Unit tests for _classify_root_causes verifying keyword-based categorization into 5 buckets.
- Unit tests for build_harness_feedback verifying overall status computation (healthy/degraded/unhealthy).
- Unit tests for build_harness_quality verifying dimension-level score computation.
- Unit tests for render_harness_feedback_json/text and render_harness_quality_json/text output format.
- Integration tests for end-to-end harness feedback generation with real feature bundles.

## Review Notes

- All 8 sensors (4 computational, 4 inferential) gracefully handle missing feature bundles and invalid slugs.
- Repair strategies correctly target spec files for most failures and quality files for coverage_debt/grading_rubric failures.
- Root cause classification uses keyword matching across gap IDs and messages for categorization.
- Safety notes are consistently included in all report outputs confirming read-only local analysis.

## Release Readiness

- [x] RR001: All 10 acceptance criteria, 16 tasks, 5 required checks, and test plan evidence are complete.
- [x] RR002: `specspine feature pr agent-self-correction-harness . --json` output is ready for reviewers.
- [x] RR003: `specspine tests impact . --feature agent-self-correction-harness --json` has been reviewed for focused local test commands.
- [x] RR004: `specspine consistency scan . --feature agent-self-correction-harness --json` has been reviewed for local spec-code-test-doc drift.
- [x] RR005: `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted repository residue.
- [x] RR006: `specspine retrospective report . --json` has been reviewed for local feature improvement signals.
- [x] RR007: `specspine coverage plan . --feature agent-self-correction-harness --json` has been reviewed if missing AC coverage remains.
- [x] RR008: `specspine verify matrix agent-self-correction-harness . --json` has been reviewed for AC-level verification evidence.
- [x] RR009: `specspine change risk . --feature agent-self-correction-harness --json` has been reviewed for changed-path risk evidence.
- [x] RR010: `specspine security cues . --feature agent-self-correction-harness --json` has been reviewed for security-sensitive cues.
- [x] RR011: `specspine provenance manifest . --feature agent-self-correction-harness --json` has been reviewed for local evidence hashes.
- [x] RR012: `specspine review packet . --feature agent-self-correction-harness --json` has been reviewed for local pre-merge evidence.
- [x] RR013: `specspine feature sync-plan agent-self-correction-harness . --json` has been reviewed before any remote GitHub sync.
- [x] RR014: `specspine feature archive agent-self-correction-harness . --json` has been reviewed before marking status archived.
- [x] RR015: `specspine feature ready agent-self-correction-harness . --json` and `specspine validate . --fusion --features` have been run.
- [x] RR016: No known blockers remain, or blockers are documented in review notes.
