# Automated Compliance & Audit Trail

Feature ID: automated-compliance-audit
Status: implemented
Priority: medium
Owner: unassigned
Milestone: unassigned
Target Release: unassigned
Project: unassigned
Effort: unknown

## Why

Generate compliance-ready audit reports from all spec-driven development evidence. Tracks feature lifecycle transitions, validation evidence, and drift history for regulatory compliance.

## Users

- Engineering managers who need compliance reports for audit readiness and regulatory reviews.
- QA leads who need validation evidence tracking across all feature bundles.
- Compliance officers who need lifecycle transition history and drift event records.
- Developers who need to understand which features are missing spec, execution, or quality files.

## Scope

- `build_compliance_report(root, feature_filter, since)` generates a `ComplianceReport` covering all feature bundles or a single filtered feature.
- `_collect_audit_events` queries git log for each feature's spec, execution, and quality files, classifying commits as file_change, lifecycle, validation, test, or consistency events.
- `_build_lifecycle_transitions` tracks status changes by parsing `Status:` field from spec file history across git commits.
- `_gather_validation_evidence` checks existence of spec/execution/quality files, counts ACs, tasks, quality checks, and coverage links, and validates AC coverage completeness.
- `_build_drift_history` builds drift event records from git history with severity classification (high for remove/delete/drop, low for add/new/create, medium otherwise).
- `_generate_compliance_summary` computes per-feature pass/fail for spec, execution, quality, AC coverage, execution presence, quality presence, and lifecycle transitions.
- JSON and text renderers (`render_compliance_json`, `render_compliance_text`) provide structured and human-readable audit output.
- Safety notes confirm only local workspace files and git history (via `git log`/`git show`) are accessed.

## Non-Goals

- Does not execute tests, CI pipelines, or any validation commands.
- Does not call external compliance services or regulatory APIs.
- Does not automatically fix compliance gaps; only generates recommendations.
- Does not track real-time compliance status; reports are point-in-time snapshots from git history.
- Does not enforce compliance policies; only reports current compliance state.

## Acceptance Criteria

- [x] AC001: `build_compliance_report` returns a `ComplianceReport` with root, audit_date, scope, features tuple, compliance_summary, evidence_hashes, recommendations, and safety_notes.
- [x] AC002: Audit events are collected from git log for each feature's spec, execution, and quality files with event_type classification (file_change, lifecycle, validation, test, consistency).
- [x] AC003: Lifecycle transitions are extracted by parsing `Status:` field from spec file history, tracking from_status and to_status changes.
- [x] AC004: Validation evidence includes spec existence with AC count, execution existence with task count, quality existence with QC count and coverage links.
- [x] AC005: AC coverage check validates that every AC in the spec file has a corresponding coverage link in the quality file.
- [x] AC006: Drift history events are classified with severity: high (remove/delete/drop), low (add/new/create), medium (all others).
- [x] AC007: Compliance summary includes per-feature pass/fail for spec, execution, quality, ac_coverage, execution_present, quality_present, and lifecycle dimensions.
- [x] AC008: Recommendations are generated for each compliance gap (missing spec, missing execution, missing quality, uncovered ACs, no lifecycle transitions).
- [x] AC009: Evidence hashes are SHA-256 digests computed from feature slug concatenated with event evidence hashes.
- [x] AC010: `render_compliance_text` produces human-readable output with summary statistics, compliance dimensions per feature, lifecycle transitions, and recommendations.

## Edge Cases

- Feature with no git history: audit events and lifecycle transitions return empty tuples; compliance checks file existence only.
- Feature bundle partially missing (e.g., spec exists but execution missing): validation evidence correctly marks missing files as fail.
- Since parameter filtering: only git commits after the specified date are included in audit events and drift history.
- Invalid feature slug in feature_filter: `validate_feature_slug` raises `InvalidFeatureSlug` before processing.
- Git command failure: `_run_git` return code != 0 results in empty events/transitions instead of raising exceptions.
- Multiple status changes in same commit: only first detected status transition is recorded per commit.
- No compliant features: compliance_rate is 0.0; all gaps are listed in recommendations.

## Constraints

- Git history access is limited to `git log` and `git show` commands on feature bundle file paths.
- Evidence hashes use SHA-256 algorithm for deterministic fingerprinting.
- Compliance scope is either "feature" (single feature_filter) or "workspace" (all bundles).
- Audit date is ISO 8601 UTC timestamp from `datetime.now(timezone.utc)`.
- Regex patterns are used for parsing AC (AC\d{3}), task (T\d{3}), quality check (QC\d{3}), and coverage link formats.
- Recommendations are limited to gap-specific fixes; no generic advice when gaps exist.

## Traceability Notes

- Source: src/specspine/audit.py (613 lines)
- Tests: tests/test_audit.py
- Audit event collection: src/specspine/audit.py lines 115-181
- Lifecycle transitions: src/specspine/audit.py lines 184-233
- Validation evidence: src/specspine/audit.py lines 236-312
- Drift history: src/specspine/audit.py lines 315-373
- Compliance summary: src/specspine/audit.py lines 376-442
- Main entry point: src/specspine/audit.py lines 445-533
- Text/JSON renderers: src/specspine/audit.py lines 536-613
