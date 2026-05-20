# Feature Benchmarking & Performance Metrics Execution

Feature ID: feature-benchmarking
Status: implemented
Why: Track and compare feature implementation metrics across the workspace. Provides insights into effort estimation accuracy, implementation velocity, and quality trends for continuous improvement.

## Milestones

- [x] M001: Core data structures (FeatureMetrics, BenchmarkReport) implemented with frozen dataclasses and as_dict serialization.
- [x] M002: Per-feature metrics computation from spec, execution, and quality files using regex extraction.
- [x] M003: Validation and consistency data integration with graceful error handling.
- [x] M004: Aggregate statistics computation (avg, median, p95) across all features.
- [x] M005: Group-by functionality for priority, status, project, and effort dimensions.
- [x] M006: Top performer identification using weighted scoring formula.
- [x] M007: Improvement area identification with primary issue classification.
- [x] M008: Trend computation for coverage, validation, and drift dimensions.
- [x] M009: Recommendation generation based on aggregate metrics.
- [x] M010: JSON and text renderers for benchmark reports.

## Tasks

- [x] AC001 T001: Implement FeatureMetrics dataclass with all metric fields (ac_count, task_count, test_count, coverage_pct, etc.).
- [x] AC002 T002: Implement BenchmarkReport dataclass with metrics, aggregates, top_performers, improvement_areas, trends, recommendations.
- [x] AC003 T003: Implement _read_text utility with OSError handling returning empty string.
- [x] AC004 T004: Implement _count_pattern utility for regex-based counting in file content.
- [x] AC005 T005: Implement _compute_feature_metrics extracting AC count from spec, task count from execution, test count and coverage from quality.
- [x] AC006 T006: Integrate validation pass/fail from build_validation_report with OSError fallback.
- [x] AC007 T007: Integrate consistency_fail from build_consistency_report with OSError/InvalidFeatureSlug fallback.
- [x] AC008 T008: Integrate drift_events from build_coverage_debt_report with OSError fallback.
- [x] AC009 T009: Implement _median utility for median computation with odd/even list handling.
- [x] AC010 T010: Implement _percentile utility for percentile computation with interpolation.
- [x] AC010 T011: Implement _aggregate_metrics with overall stats and group-by grouping.
- [x] AC010 T012: Implement _identify_top_performers with weighted scoring formula (coverage*0.4 + drift*0.3 + consistency*0.3).
- [x] AC010 T013: Implement _identify_improvement_areas with inverse scoring and primary_issue classification.
- [x] AC010 T014: Implement _primary_issue classifier checking low_coverage, high_drift, consistency_failures, no_test_links.
- [x] AC010 T015: Implement _compute_trends with coverage_trend, drift_trend, validation_trend classification.
- [x] AC010 T016: Implement _generate_recommendations based on avg_coverage, avg_drift, low-coverage features, and trends.
- [x] AC010 T017: Implement build_benchmark_report as main entry point with feature_filter and group_by parameters.
- [x] AC010 T018: Implement render_benchmark_json and render_benchmark_text for output formatting.

## Dependencies

- src/specspine/consistency.py (build_consistency_report)
- src/specspine/coverage.py (build_coverage_debt_report)
- src/specspine/features.py (FEATURE_FILE_PATHS, feature_bundle_paths, list_feature_bundles, validate_feature_slug, get_feature_status, read_feature_metadata)
- src/specspine/validation.py (build_validation_report)

## Open Questions

- None; feature is implemented and tested.

## Agent Handoff

- Run `specspine feature handoff feature-benchmarking . --json` before implementation or review handoff.
- Run `specspine adapters handoff feature-benchmarking . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks feature-benchmarking . --json` for the focused implementation checklist.
- Run `specspine feature task-issues feature-benchmarking . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace feature-benchmarking . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests feature-benchmarking . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature feature-benchmarking --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature feature-benchmarking --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature feature-benchmarking --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix feature-benchmarking . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature feature-benchmarking --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature feature-benchmarking --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature feature-benchmarking --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature feature-benchmarking --json` to compose local pre-merge review evidence.
- Run `specspine feature ready feature-benchmarking . --json` after implementation evidence is complete.
- Run `specspine feature pr feature-benchmarking . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan feature-benchmarking . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan feature-benchmarking . --output-dir .specspine/sync-plan/feature-benchmarking` to materialize local sync review artifacts.
- Run `specspine feature archive feature-benchmarking . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
