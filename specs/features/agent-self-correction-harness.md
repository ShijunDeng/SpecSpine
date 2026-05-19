# Agent Self-Correction Harness

Feature ID: agent-self-correction-harness
Status: implemented
Priority: medium
Owner: unassigned
Milestone: unassigned
Target Release: unassigned
Project: unassigned
Effort: unknown

## Why

Wire SpecSpine verification, coverage debt, and grading rubrics into deterministic feedback loops that produce LLM-consumable repair instructions. Turns SpecSpine from planning tool into behavior harness for autonomous coding agents.

## Users

- Autonomous coding agents that need structured feedback to self-correct implementation gaps.
- Developers who want deterministic repair strategies for failing acceptance criteria.
- QA engineers who need root-cause classification across computational and inferential quality dimensions.

## Scope

- `build_harness_feedback(slug, root)` runs 8 quality sensors (4 computational, 4 inferential) against a feature bundle and returns a `HarnessFeedbackReport` with pass/fail/warn status per sensor.
- Computational sensors: verification_matrix, coverage_debt, grading_rubric, validation_contract.
- Inferential sensors: consistency_scan, hygiene_scan, security_cues, change_risk.
- `_generate_repair_strategies()` produces `RepairStrategy` objects for each failing AC with target file, edit description, verification command, and success criteria.
- `_classify_root_causes()` categorizes gaps into missing_spec, missing_code, missing_test, stale_coverage, or contract_violation.
- `build_harness_quality(root, feature_id)` computes dimension-level scores across 8 quality dimensions with pass percentage per dimension.
- JSON and text renderers (`render_harness_feedback_json`, `render_harness_feedback_text`, `render_harness_quality_json`, `render_harness_quality_text`) provide structured and human-readable output.
- Safety notes are included in every report confirming no tests, subprocesses, network calls, or tokens were used.

## Non-Goals

- Does not execute repairs or invoke any upstream tools automatically.
- Does not run actual tests or CI pipelines; all evidence is read-only local file analysis.
- Does not modify feature bundles, spec files, or test files.
- Does not provide real-time monitoring or continuous feedback loops; each call is a point-in-time snapshot.

## Acceptance Criteria

- [x] AC001: `build_harness_feedback` returns a `HarnessFeedbackReport` with feature_id, status, sensors tuple, repair_strategies tuple, root_causes dict, steering_summary dict, harness_quality, and safety_notes.
- [x] AC002: Computational sensors (verification_matrix, coverage_debt, grading_rubric, validation_contract) each return pass/fail status with relevant output metrics and flagged AC IDs.
- [x] AC003: Inferential sensors (consistency_scan, hygiene_scan, security_cues, change_risk) each return pass/fail status with relevant output metrics.
- [x] AC004: Overall harness status is "healthy" when all sensors pass, "degraded" when only warnings exist, and "unhealthy" when any sensor fails.
- [x] AC005: Repair strategies are generated for each failing AC with target_file, edit_description, verification_command, and success_criteria fields.
- [x] AC006: Root cause classification categorizes gaps into 5 categories: missing_spec, missing_code, missing_test, stale_coverage, contract_violation.
- [x] AC007: `build_harness_quality` returns a `HarnessQualityReport` with 8 governed dimensions and per-dimension pass percentage scores.
- [x] AC008: `render_harness_feedback_json` produces valid JSON with sorted keys; `render_harness_feedback_text` produces human-readable text with sensor statuses and repair strategies.
- [x] AC009: `render_harness_quality_json` produces valid JSON with sorted keys; `render_harness_quality_text` produces human-readable text with dimension scores and safety notes.
- [x] AC010: All reports include safety_notes confirming no tests, subprocesses, network calls, GitHub API calls, upstream CLIs, environment variables, or tokens were accessed.

## Edge Cases

- Feature bundle not found: sensors gracefully return fail status with error output instead of raising exceptions.
- Invalid feature slug: `validate_feature_slug` raises `InvalidFeatureSlug` before sensor execution.
- Empty spec file: `_extract_ac_ids` returns empty tuple; sensors still run but report no AC-specific findings.
- Missing quality files: coverage_debt and grading_rubric sensors handle FileNotFoundError gracefully.
- No failing ACs but sensor-level failures: repair strategies include SENSOR_FAILURE entries for computational sensor failures.
- Workspace-level quality (no feature_id): `build_harness_quality` iterates all feature bundles and aggregates scores across the workspace.

## Constraints

- All sensor execution is read-only; no files are written or modified.
- Sensor data comes from existing SpecSpine modules (consistency, coverage, executor, features, hygiene, security, change, verification).
- JSON output uses `sort_keys=True` and `indent=2` for deterministic formatting.
- Safety notes are immutable tuples appended to every report.
- Feature slug validation follows the `[a-z0-9]([a-z0-9-]*[a-z0-9])?` pattern.

## Traceability Notes

- Source: src/specspine/harness.py (734 lines)
- Tests: tests/test_harness.py
- Computational sensors: src/specspine/harness.py lines 125-265
- Inferential sensors: src/specspine/harness.py lines 268-395
- Repair strategies: src/specspine/harness.py lines 398-463
- Root cause classification: src/specspine/harness.py lines 466-505
- Quality scoring: src/specspine/harness.py lines 594-657
- Text/JSON renderers: src/specspine/harness.py lines 660-733
