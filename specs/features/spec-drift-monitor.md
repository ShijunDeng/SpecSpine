# Spec Drift Monitor & Audit Trail

Feature ID: spec-drift-monitor
Status: implemented
Priority: medium
Owner: unassigned
Milestone: unassigned
Target Release: unassigned
Project: unassigned
Effort: unknown

## Why

Continuous drift monitoring across all 55 features with historical trend analysis, severity classification, and compliance-ready audit trail. Addresses normalization of deviance risk as AI agents scale.

## Users

- Engineering managers who need workspace-wide drift visibility to catch spec-code-test misalignment early.
- QA leads who need to identify uncovered ACs and stale test links across the feature portfolio.
- Compliance officers who need drift audit trails with evidence hashes for regulatory reviews.
- Developers who need to understand what has changed in their feature since a baseline commit.

## Scope

- `build_drift_monitor_report(root, feature_filter, baseline, since)` generates a `DriftAuditReport` with per-feature drift records, summary, trends, compliance, and recommended commands.
- `_detect_spec_drift` compares current spec ACs against baseline spec ACs, detecting removed (critical severity) and added (medium severity) ACs.
- `_detect_code_drift` identifies orphaned source file references (files referenced in spec but not on disk) and tasks that don't reference all spec ACs.
- `_detect_test_drift` identifies stale test coverage links (referencing non-existent test files) and spec ACs with no coverage link in quality file.
- `_detect_quality_drift` identifies spec ACs missing quality checks or coverage links, and coverage links not pointing to tests/ paths.
- `_build_drift_history` extracts drift events from git log with severity classification based on commit message keywords.
- `_correlate_cross_feature_drift` marks features as cascade_risk when they depend on features with critical severity drift.
- `_build_compliance_section` generates SHA-256 evidence hash and pass/fail per dimension (spec, code, test, quality).
- `_classify_severity` determines overall feature severity as the highest severity across all drift event types.
- `_severity_distribution` counts features by severity level (critical, high, medium, low, none).
- JSON and text renderers (`render_drift_json`, `render_drift_text`) provide structured and human-readable output.

## Non-Goals

- Does not automatically fix drift; only detects and reports it.
- Does not monitor drift in real-time; each call is a point-in-time snapshot.
- Does not modify any feature bundles or source files.
- Does not enforce drift remediation policies; only reports current drift state.
- Does not integrate with external monitoring or alerting systems.

## Acceptance Criteria

- [x] AC001: `build_drift_monitor_report` returns a `DriftAuditReport` with root, scan_metadata, features tuple, summary, trends, compliance, recommended_commands, and safety_notes.
- [x] AC002: `_detect_spec_drift` compares ACs between current and baseline spec, reporting removed ACs as critical severity and added ACs as medium severity.
- [x] AC003: `_detect_code_drift` identifies orphaned source file references and tasks not referencing all spec ACs as medium severity.
- [x] AC004: `_detect_test_drift` identifies stale test coverage links and uncovered spec ACs as high severity.
- [x] AC005: `_detect_quality_drift` identifies ACs missing quality checks/coverage links and non-tests/ coverage paths as low severity.
- [x] AC006: `_build_drift_history` extracts git log events with severity based on commit message keywords (remove/delete/drop=high, add/new/create=low, medium otherwise).
- [x] AC007: `_correlate_cross_feature_drift` marks features as cascade_risk when they depend on features with critical severity drift.
- [x] AC008: `_build_compliance_section` generates SHA-256 evidence hash and pass/fail per dimension (spec, code, test, quality).
- [x] AC009: `_classify_severity` returns the highest severity across all event types using order: critical > high > medium > low > none.
- [x] AC010: Summary includes drift_events_total, drift_free_count, features_scanned, and severity_distribution counts.

## Edge Cases

- No baseline provided: spec drift detection is skipped; only code, test, and quality drift are detected.
- Baseline commit doesn't have spec file: all current ACs reported as new with high severity.
- Feature with no git history: drift history is empty; current drift detection still runs.
- Invalid feature slug in feature_filter: `validate_feature_slug` raises InvalidFeatureSlug before processing.
- Git command failure: _run_git return code != 0 results in empty drift history instead of raising exceptions.
- Feature with no drift events: severity is "none"; feature counted in drift_free_count.
- Multiple features with critical drift: cascade_risk propagates to all features that depend on any critical feature.

## Constraints

- Git history access is limited to `git rev-parse HEAD`, `git log`, and `git show` commands.
- Evidence hash uses SHA-256 computed from sorted concatenation of root, timestamp, git_commit, feature IDs, severities, and event details.
- Scan metadata includes baseline, git_commit, since, and timestamp fields.
- Safety notes confirm only local files are read (with git show/log for baseline comparison); no tests, network calls, or tokens.
- Since parameter filters drift history by commit date matching YYYY-MM-DD pattern.
- Recommended commands are deduplicated using a seen set.

## Traceability Notes

- Source: src/specspine/drift.py (697 lines)
- Tests: tests/test_drift.py
- Spec drift detection: src/specspine/drift.py lines 158-210
- Code drift detection: src/specspine/drift.py lines 213-269
- Test drift detection: src/specspine/drift.py lines 272-307
- Quality drift detection: src/specspine/drift.py lines 310-347
- Drift history: src/specspine/drift.py lines 368-427
- Cross-feature correlation: src/specspine/drift.py lines 430-461
- Compliance section: src/specspine/drift.py lines 464-499
- Main entry point: src/specspine/drift.py lines 530-631
- Text/JSON renderers: src/specspine/drift.py lines 634-697
