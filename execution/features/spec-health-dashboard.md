# Spec Health Dashboard Execution

Feature ID: spec-health-dashboard
Status: implemented
Why: Unified observability dashboard composing all 54 existing evidence sources into one actionable health report. Provides command-center view of entire spec-driven workflow for agents and maintainers.

## Milestones

- [x] M001: Core data structures (WorkspaceHealth, FeaturePipeline, ValidationHealth, CoverageDebt, ConsistencyDrift, ReadinessGates, QualityGates, DependencyHealth, SecuritySummary, RetrospectiveTheme, HealthReport) implemented with frozen dataclasses and as_dict serialization.
- [x] M002: Workspace health checking BASE_WORKSPACE_FILES for present/missing status.
- [x] M003: Feature pipeline aggregating feature counts by status.
- [x] M004: Validation health aggregating pass/fail/warn/skip counts with top failing rules.
- [x] M005: Coverage debt tracking features with debt and top uncovered features.
- [x] M006: Consistency drift tracking check results with top failing features.
- [x] M007: Readiness gates tracking ready/not-ready features with top blockers.
- [x] M008: Quality gates, dependency health, security summary, and retrospective theme builders.
- [x] M009: Health score computation with 7 weighted dimensions and workspace shortcut.
- [x] M010: Recommended actions and commands generation with JSON/text renderers.

## Tasks

- [x] AC001 T001: Implement WorkspaceHealth with complete, present, and missing fields.
- [x] AC002 T002: Implement FeaturePipeline with features_total and by_status dict.
- [x] AC003 T003: Implement ValidationHealth with ok, pass/fail/warn/skip/total counts and top_failing_rules.
- [x] AC004 T004: Implement CoverageDebt with features_with_debt, missing/covered/total ACs, and top_features.
- [x] AC005 T005: Implement ConsistencyDrift with features_scanned, checks pass/fail/warn/total, and top_failing_features.
- [x] AC006 T006: Implement ReadinessGates with features_total, ready, not_ready, blocking_checks_total, gaps_total, and top_blockers.
- [x] AC007 T007: Implement QualityGates with required_total/done/open and definition_total.
- [x] AC008 T008: Implement DependencyHealth with features_total, cycles, critical_path, and critical_path_effort.
- [x] AC009 T009: Implement SecuritySummary with cues_total and high/medium/low counts.
- [x] AC010 T010: Implement RetrospectiveTheme with top_blocker_theme, blocking_checks, gaps, coverage_states, and open_tasks.
- [x] AC010 T011: Implement HealthReport composing all 10 dimensions plus health_score, recommended_actions, recommended_commands, safety_notes.
- [x] AC010 T012: Implement _build_workspace_health using check_workspace with BASE_WORKSPACE_FILES.
- [x] AC010 T013: Implement _build_feature_pipeline using list_feature_bundles with status aggregation.
- [x] AC010 T014: Implement _build_validation_health with OSError fallback returning zeroed ValidationHealth.
- [x] AC010 T015: Implement _build_coverage_debt_data with OSError fallback and top 5 features sorting.
- [x] AC010 T016: Implement _build_consistency_drift with OSError fallback and top 5 failing features.
- [x] AC010 T017: Implement _build_readiness_gates with OSError fallback and top 5 blockers.
- [x] AC010 T018: Implement _build_quality_gates, _build_dependency_health, _build_security_summary, _build_retrospective_theme with OSError fallbacks.
- [x] AC010 T019: Implement compute_health_score with 7 weighted dimensions and 0 shortcut for missing workspace.
- [x] AC010 T020: Implement generate_recommended_actions and _generate_recommended_commands.
- [x] AC010 T021: Implement build_health_report as main entry point composing all dimensions.
- [x] AC010 T022: Implement render_health_json and render_health_text for output formatting.

## Dependencies

- src/specspine/consistency.py (build_consistency_report)
- src/specspine/coverage.py (build_coverage_debt_report)
- src/specspine/dependency.py (build_dependency_graph)
- src/specspine/features.py (list_feature_bundles)
- src/specspine/gates.py (build_quality_gate_report)
- src/specspine/retrospective.py (build_retrospective_report)
- src/specspine/security.py (build_security_cue_report)
- src/specspine/status.py (build_readiness_summary, build_status)
- src/specspine/validation.py (build_validation_report)
- src/specspine/workspace.py (BASE_WORKSPACE_FILES, check_workspace)

## Open Questions

- None; feature is implemented and tested.

## Agent Handoff

- Run `specspine feature handoff spec-health-dashboard . --json` before implementation or review handoff.
- Run `specspine adapters handoff spec-health-dashboard . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks spec-health-dashboard . --json` for the focused implementation checklist.
- Run `specspine feature task-issues spec-health-dashboard . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace spec-health-dashboard . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests spec-health-dashboard . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature spec-health-dashboard --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature spec-health-dashboard --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature spec-health-dashboard --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix spec-health-dashboard . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature spec-health-dashboard --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature spec-health-dashboard --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature spec-health-dashboard --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature spec-health-dashboard --json` to compose local pre-merge review evidence.
- Run `specspine feature ready spec-health-dashboard . --json` after implementation evidence is complete.
- Run `specspine feature pr spec-health-dashboard . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan spec-health-dashboard . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan spec-health-dashboard . --output-dir .specspine/sync-plan/spec-health-dashboard` to materialize local sync review artifacts.
- Run `specspine feature archive spec-health-dashboard . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
