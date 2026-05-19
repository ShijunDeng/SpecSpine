# Agent Self-Correction Harness Execution

Feature ID: agent-self-correction-harness
Status: implemented
Why: Wire SpecSpine verification, coverage debt, and grading rubrics into deterministic feedback loops that produce LLM-consumable repair instructions. Turns SpecSpine from planning tool into behavior harness for autonomous coding agents.

## Milestones

- [x] M001: Core data structures (HarnessFeedbackSensor, RepairStrategy, HarnessQualityReport, HarnessFeedbackReport) implemented with frozen dataclasses and as_dict serialization.
- [x] M002: Computational sensors (verification_matrix, coverage_debt, grading_rubric, validation_contract) implemented with graceful error handling.
- [x] M003: Inferential sensors (consistency_scan, hygiene_scan, security_cues, change_risk) implemented with graceful error handling.
- [x] M004: Repair strategy generation with AC-specific and sensor-level failure strategies.
- [x] M005: Root cause classification into 5 categories (missing_spec, missing_code, missing_test, stale_coverage, contract_violation).
- [x] M006: Harness quality scoring across 8 dimensions with workspace-level aggregation.
- [x] M007: JSON and text renderers for feedback reports and quality reports.
- [x] M008: Safety notes included in all reports.

## Tasks

- [x] T001: Implement HarnessFeedbackSensor dataclass with sensor_type, name, status, output, ac_ids fields and as_dict method.
- [x] T002: Implement RepairStrategy dataclass with ac_id, target_file, edit_description, verification_command, success_criteria fields.
- [x] T003: Implement HarnessQualityReport dataclass with feature_id, governed_dimensions, sensor_count, harness_coverage_pct, dimension_scores.
- [x] T004: Implement HarnessFeedbackReport dataclass with all sensor, strategy, root_cause, and quality fields.
- [x] T005: Implement _read_feature_contents to load spec, execution, quality files from feature bundle paths.
- [x] T006: Implement _extract_ac_ids to parse AC identifiers from spec content.
- [x] T007: Implement _run_computational_sensors with 4 sensors: verification_matrix, coverage_debt, grading_rubric, validation_contract.
- [x] T008: Implement _run_inferential_sensors with 4 sensors: consistency_scan, hygiene_scan, security_cues, change_risk.
- [x] T009: Implement _generate_repair_strategies with AC-specific strategies and SENSOR_FAILURE fallback.
- [x] T010: Implement _classify_root_causes with keyword-based categorization into 5 buckets.
- [x] T011: Implement _collect_gaps_from_sensors to aggregate sensor failures and flagged AC IDs.
- [x] T012: Implement build_harness_feedback as the main entry point combining all sensors, strategies, and quality scoring.
- [x] T013: Implement build_harness_quality for workspace-level and feature-level quality scoring.
- [x] T014: Implement render_harness_feedback_json and render_harness_feedback_text for output formatting.
- [x] T015: Implement render_harness_quality_json and render_harness_quality_text for output formatting.
- [x] T016: Add immutable safety_notes to all reports.

## Dependencies

- src/specspine/consistency.py (build_consistency_report)
- src/specspine/coverage.py (build_coverage_debt_report)
- src/specspine/executor.py (build_grading_rubric)
- src/specspine/features.py (feature_bundle_paths, parse_acceptance_criteria, validate_feature_slug, list_feature_bundles)
- src/specspine/hygiene.py (build_hygiene_scan_report)
- src/specspine/security.py (build_security_cue_report)
- src/specspine/change.py (build_change_risk_report)
- src/specspine/verification.py (build_verification_matrix)

## Open Questions

- None; feature is implemented and tested.

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
