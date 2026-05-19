# Spec Drift Monitor & Audit Trail Quality

Feature ID: spec-drift-monitor
Status: implemented
Why: Continuous drift monitoring across all 55 features with historical trend analysis, severity classification, and compliance-ready audit trail. Addresses normalization of deviance risk as AI agents scale.

## Required Checks

- [x] QC001: All 10 acceptance criteria verified against drift.py implementation - dataclasses, drift detection methods, history extraction, cross-feature correlation, compliance, and renderers match spec.
- [x] QC002: Test coverage in test_drift.py proves spec drift detection correctly identifies removed and added ACs between baseline and current.
- [x] QC003: Test coverage proves test drift detection correctly identifies stale coverage links and uncovered spec ACs.
- [x] QC004: `specspine feature ready spec-drift-monitor . --json` has no blocking checks after evidence is complete.
- [x] QC005: `specspine validate . --fusion --features` passes.

## Test Coverage

Use `- [ ] AC001 -> tests/...` to link existing local test files or test selectors.

- [x] AC001 -> tests/test_drift.py
- [x] AC002 -> tests/test_drift.py
- [x] AC003 -> tests/test_drift.py
- [x] AC004 -> tests/test_drift.py
- [x] AC005 -> tests/test_drift.py
- [x] AC006 -> tests/test_drift.py
- [x] AC007 -> tests/test_drift.py
- [x] AC008 -> tests/test_drift.py
- [x] AC009 -> tests/test_drift.py
- [x] AC010 -> tests/test_drift.py

## Test Plan

- Unit tests for DriftEvent, FeatureDriftRecord, DriftAuditReport dataclasses and as_dict methods.
- Unit tests for _detect_spec_drift verifying removed ACs (critical) and added ACs (medium) detection.
- Unit tests for _detect_spec_drift with no baseline verifying skip behavior.
- Unit tests for _detect_code_drift verifying orphaned source paths and incomplete task-to-AC mapping.
- Unit tests for _detect_test_drift verifying stale test links and uncovered spec ACs.
- Unit tests for _detect_quality_drift verifying missing QC/coverage links and non-tests/ paths.
- Unit tests for _build_drift_history verifying git log parsing and keyword-based severity classification.
- Unit tests for _correlate_cross_feature_drift verifying cascade_risk propagation.
- Unit tests for _build_compliance_section verifying SHA-256 evidence hash and per-dimension pass/fail.
- Integration tests for end-to-end drift report generation with real feature bundles.

## Review Notes

- Drift detection covers 4 dimensions: spec, code, test, and quality with distinct severity levels.
- Cross-feature cascade risk detection uses dependency extraction to propagate critical drift signals.
- Compliance section generates deterministic SHA-256 hash from sorted evidence components.
- Safety notes consistently confirm only local files are read with git show/log for baseline comparison.

## Release Readiness

- [x] RR001: All 10 acceptance criteria, 18 tasks, 5 required checks, and test plan evidence are complete.
- [x] RR002: `specspine feature pr spec-drift-monitor . --json` output is ready for reviewers.
- [x] RR003: `specspine tests impact . --feature spec-drift-monitor --json` has been reviewed for focused local test commands.
- [x] RR004: `specspine consistency scan . --feature spec-drift-monitor --json` has been reviewed for local spec-code-test-doc drift.
- [x] RR005: `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted repository residue.
- [x] RR006: `specspine retrospective report . --json` has been reviewed for local feature improvement signals.
- [x] RR007: `specspine coverage plan . --feature spec-drift-monitor --json` has been reviewed if missing AC coverage remains.
- [x] RR008: `specspine verify matrix spec-drift-monitor . --json` has been reviewed for AC-level verification evidence.
- [x] RR009: `specspine change risk . --feature spec-drift-monitor --json` has been reviewed for changed-path risk evidence.
- [x] RR010: `specspine security cues . --feature spec-drift-monitor --json` has been reviewed for security-sensitive cues.
- [x] RR011: `specspine provenance manifest . --feature spec-drift-monitor --json` has been reviewed for local evidence hashes.
- [x] RR012: `specspine review packet . --feature spec-drift-monitor --json` has been reviewed for local pre-merge evidence.
- [x] RR013: `specspine feature sync-plan spec-drift-monitor . --json` has been reviewed before any remote GitHub sync.
- [x] RR014: `specspine feature archive spec-drift-monitor . --json` has been reviewed before marking status archived.
- [x] RR015: `specspine feature ready spec-drift-monitor . --json` and `specspine validate . --fusion --features` have been run.
- [x] RR016: No known blockers remain, or blockers are documented in review notes.
