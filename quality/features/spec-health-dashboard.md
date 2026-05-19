# Spec Health Dashboard Quality

Feature ID: spec-health-dashboard
Status: implemented
Why: Unified observability dashboard composing all 54 existing evidence sources into one actionable health report. Provides command-center view of entire spec-driven workflow for agents and maintainers.

## Required Checks

- [x] QC001: All 10 acceptance criteria verified against health.py implementation - dataclasses, 10 dimension builders, health score computation, recommended actions, and renderers match spec.
- [x] QC002: Test coverage in test_health.py proves workspace health checking and feature pipeline aggregation.
- [x] QC003: Test coverage proves health score computation with 7 weighted dimensions and workspace missing shortcut.
- [x] QC004: `specspine feature ready spec-health-dashboard . --json` has no blocking checks after evidence is complete.
- [x] QC005: `specspine validate . --fusion --features` passes.

## Test Coverage

Use `- [ ] AC001 -> tests/...` to link existing local test files or test selectors.

- [x] AC001 -> tests/test_health.py
- [x] AC002 -> tests/test_health.py
- [x] AC003 -> tests/test_health.py
- [x] AC004 -> tests/test_health.py
- [x] AC005 -> tests/test_health.py
- [x] AC006 -> tests/test_health.py
- [x] AC007 -> tests/test_health.py
- [x] AC008 -> tests/test_health.py
- [x] AC009 -> tests/test_health.py
- [x] AC010 -> tests/test_health.py

## Test Plan

- Unit tests for all 10 health data structures (WorkspaceHealth, FeaturePipeline, ValidationHealth, CoverageDebt, ConsistencyDrift, ReadinessGates, QualityGates, DependencyHealth, SecuritySummary, RetrospectiveTheme, HealthReport).
- Unit tests for _build_workspace_health verifying present/missing file detection.
- Unit tests for _build_feature_pipeline verifying status aggregation.
- Unit tests for _build_validation_health with OSError fallback verification.
- Unit tests for _build_coverage_debt_data with top 5 features sorting verification.
- Unit tests for _build_consistency_drift with top 5 failing features sorting.
- Unit tests for _build_readiness_gates with top 5 blockers sorting.
- Unit tests for compute_health_score verifying 7 weighted dimensions and 0 shortcut for missing workspace.
- Unit tests for generate_recommended_actions verifying condition-based action generation.
- Integration tests for end-to-end health report generation with real feature bundles.

## Review Notes

- Health dashboard composes evidence from 10 existing modules with graceful OSError fallback.
- Health score uses explicit weights: workspace=10, pipeline=15, validation=20, coverage=20, consistency=15, readiness=15, gates=5.
- All dimension builders return zeroed data on OSError for graceful degradation.
- Safety notes consistently confirm read-only local analysis with no external calls.

## Release Readiness

- [x] RR001: All 10 acceptance criteria, 22 tasks, 5 required checks, and test plan evidence are complete.
- [x] RR002: `specspine feature pr spec-health-dashboard . --json` output is ready for reviewers.
- [x] RR003: `specspine tests impact . --feature spec-health-dashboard --json` has been reviewed for focused local test commands.
- [x] RR004: `specspine consistency scan . --feature spec-health-dashboard --json` has been reviewed for local spec-code-test-doc drift.
- [x] RR005: `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted repository residue.
- [x] RR006: `specspine retrospective report . --json` has been reviewed for local feature improvement signals.
- [x] RR007: `specspine coverage plan . --feature spec-health-dashboard --json` has been reviewed if missing AC coverage remains.
- [x] RR008: `specspine verify matrix spec-health-dashboard . --json` has been reviewed for AC-level verification evidence.
- [x] RR009: `specspine change risk . --feature spec-health-dashboard --json` has been reviewed for changed-path risk evidence.
- [x] RR010: `specspine security cues . --feature spec-health-dashboard --json` has been reviewed for security-sensitive cues.
- [x] RR011: `specspine provenance manifest . --feature spec-health-dashboard --json` has been reviewed for local evidence hashes.
- [x] RR012: `specspine review packet . --feature spec-health-dashboard --json` has been reviewed for local pre-merge evidence.
- [x] RR013: `specspine feature sync-plan spec-health-dashboard . --json` has been reviewed before any remote GitHub sync.
- [x] RR014: `specspine feature archive spec-health-dashboard . --json` has been reviewed before marking status archived.
- [x] RR015: `specspine feature ready spec-health-dashboard . --json` and `specspine validate . --fusion --features` have been run.
- [x] RR016: No known blockers remain, or blockers are documented in review notes.
