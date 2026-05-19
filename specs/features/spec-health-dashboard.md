# Spec Health Dashboard

Feature ID: spec-health-dashboard
Status: implemented
Priority: medium
Owner: unassigned
Milestone: unassigned
Target Release: unassigned
Project: unassigned
Effort: unknown

## Why

Unified observability dashboard composing all 54 existing evidence sources into one actionable health report. Provides command-center view of entire spec-driven workflow for agents and maintainers.

## Users

- Engineering managers who need a single health score to assess overall workspace quality.
- Tech leads who need to identify the top failing validation rules, coverage gaps, and consistency drift.
- Release managers who need readiness gate status, quality gate completion, and recommended actions before release.
- Developers who need to understand workspace completeness, feature pipeline status, and dependency health.

## Scope

- `build_health_report(root)` returns a `HealthReport` composing 10 health dimensions: workspace, feature pipeline, validation, coverage debt, consistency drift, readiness gates, quality gates, dependency health, security summary, and retrospective theme.
- `compute_health_score` computes 0-100 score from 7 weighted dimensions: workspace (10), pipeline (15), validation (20), coverage (20), consistency (15), readiness (15), quality gates (5). Returns 0 if workspace has missing files.
- `generate_recommended_actions` produces up to 5 actions based on: missing workspace files, validation failures, uncovered ACs, consistency failures, and not-ready features.
- `_generate_recommended_commands` returns 6 standard commands: health status, validated status with readiness, coverage debt, consistency scan, validate, and gates.
- Each health dimension has a dedicated builder function (_build_workspace_health, _build_feature_pipeline, etc.) with graceful OSError fallback returning zeroed data.
- Workspace health checks BASE_WORKSPACE_FILES for present/missing status.
- Feature pipeline counts features by status (planned, implemented, validated, archived, etc.).
- Validation health aggregates pass/fail/warn/skip counts with top 5 failing rules.
- Coverage debt tracks features with debt, missing/covered/total ACs, and top 5 features with uncovered ACs.
- Consistency drift tracks checks pass/fail/warn/total with top 5 failing features.
- Readiness gates track ready/not-ready features, blocking checks, and gaps with top 5 blockers.
- Quality gates track required total/done/open and definition total.
- Dependency health tracks features total, cycles, critical path, and critical path effort.
- Security summary tracks cues total with high/medium/low breakdown.
- Retrospective theme tracks top blocker theme, blocking checks, gaps, coverage states, and open tasks.
- JSON and text renderers (`render_health_json`, `render_health_text`) provide structured and human-readable output.

## Non-Goals

- Does not run tests, invoke subprocesses, call network services, or read tokens.
- Does not modify any files or trigger CI/CD pipelines.
- Does not provide real-time health monitoring; each call is a point-in-time snapshot.
- Does not enforce health thresholds or block releases automatically.
- Does not replace individual evidence source commands; composes them into a single view.

## Acceptance Criteria

- [x] AC001: `build_health_report` returns a `HealthReport` with root, workspace, feature_pipeline, validation_health, coverage_debt, consistency_drift, readiness_gates, quality_gates, dependency_health, security_summary, retrospective_theme, health_score, recommended_actions, recommended_commands, and safety_notes.
- [x] AC002: `_build_workspace_health` checks BASE_WORKSPACE_FILES returning WorkspaceHealth with complete boolean, present tuple, and missing tuple.
- [x] AC003: `_build_feature_pipeline` returns FeaturePipeline with features_total and by_status dict sorted by status key.
- [x] AC004: `_build_validation_health` returns ValidationHealth with ok, pass/fail/warn/skip counts, total, and top 5 failing rules; returns zeroed data on OSError.
- [x] AC005: `_build_coverage_debt_data` returns CoverageDebt with features_with_debt, missing/covered/total ACs, and top 5 features sorted by missing count descending.
- [x] AC006: `_build_consistency_drift` returns ConsistencyDrift with features_scanned, checks pass/fail/warn/total, and top 5 failing features sorted by fail count.
- [x] AC007: `_build_readiness_gates` returns ReadinessGates with features_total, ready, not_ready, blocking_checks_total, gaps_total, and top 5 blockers sorted by blocking_checks then gaps.
- [x] AC008: `compute_health_score` returns 0-100 score with 7 weighted dimensions; returns 0 immediately if workspace has missing files.
- [x] AC009: `generate_recommended_actions` produces up to 5 actions addressing missing files, validation failures, coverage gaps, consistency drift, and not-ready features.
- [x] AC010: `render_health_text` produces human-readable output with health score, all 10 dimension summaries, recommended actions, recommended commands, and safety notes.

## Edge Cases

- No feature bundles: feature_pipeline shows 0 total with empty by_status; pipeline_score defaults to 15.
- All evidence sources fail with OSError: each builder returns zeroed data; health_score computed from available dimensions.
- Workspace completely missing: health_score returns 0 immediately without computing other dimensions.
- No validation checks: validation_score defaults to 20 (full points when no data).
- No coverage data: coverage_score defaults to 20 (full points when no data).
- No consistency checks: consistency_score defaults to 15 (full points when no data).
- No readiness data: readiness_score defaults to 15 (full points when no data).
- No quality gate data: gates_score defaults to 5 (full points when no data).
- Health score clamped to 0-100 range using max(0, min(100, score)).
- Recommended actions limited to first 5 entries.

## Constraints

- All evidence source builders use try/except OSError for graceful degradation.
- Health score weights: workspace=10, pipeline=15, validation=20, coverage=20, consistency=15, readiness=15, gates=5 (total=100).
- Top N lists are capped at 5 entries per dimension.
- Safety notes are immutable tuple with 4 entries confirming read-only local analysis.
- Recommended commands are fixed 6 commands for common follow-up actions.

## Traceability Notes

- Source: src/specspine/health.py (778 lines)
- Tests: tests/test_health.py
- Health data structures: src/specspine/health.py lines 28-236
- Workspace health: src/specspine/health.py lines 238-246
- Feature pipeline: src/specspine/health.py lines 249-258
- Validation health: src/specspine/health.py lines 261-296
- Coverage debt: src/specspine/health.py lines 299-331
- Consistency drift: src/specspine/health.py lines 334-368
- Readiness gates: src/specspine/health.py lines 371-408
- Quality gates: src/specspine/health.py lines 411-428
- Dependency health: src/specspine/health.py lines 431-449
- Security summary: src/specspine/health.py lines 452-469
- Retrospective theme: src/specspine/health.py lines 472-498
- Health score computation: src/specspine/health.py lines 501-564
- Main entry point: src/specspine/health.py lines 609-670
- Text/JSON renderers: src/specspine/health.py lines 673-778
