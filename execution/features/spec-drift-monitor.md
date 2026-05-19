# Spec Drift Monitor & Audit Trail Execution

Feature ID: spec-drift-monitor
Status: implemented
Why: Continuous drift monitoring across all 55 features with historical trend analysis, severity classification, and compliance-ready audit trail. Addresses normalization of deviance risk as AI agents scale.

## Milestones

- [x] M001: Core data structures (DriftEvent, FeatureDriftRecord, DriftAuditReport) implemented with frozen dataclasses and as_dict serialization.
- [x] M002: Spec drift detection comparing ACs between current and baseline with removed/added classification.
- [x] M003: Code drift detecting orphaned source references and incomplete task-to-AC mapping.
- [x] M004: Test drift detecting stale coverage links and uncovered spec ACs.
- [x] M005: Quality drift detecting missing QC/coverage links and non-tests/ coverage paths.
- [x] M006: Git-based drift history extraction with keyword-based severity classification.
- [x] M007: Cross-feature drift correlation for cascade risk detection.
- [x] M008: Compliance section with SHA-256 evidence hash and per-dimension pass/fail.
- [x] M009: Summary computation with severity distribution and drift-free counts.
- [x] M010: JSON and text renderers for drift audit reports.

## Tasks

- [x] T001: Implement DriftEvent dataclass with event_type, severity, timestamp, description, affected_acs, affected_tasks.
- [x] T002: Implement FeatureDriftRecord with feature_id, severity, spec/code/test/quality_drift tuples, drift_events, cascade_risk.
- [x] T003: Implement DriftAuditReport with root, scan_metadata, features, summary, trends, compliance, recommended_commands, safety_notes.
- [x] T004: Implement utility functions _now_iso and _git_commit for timestamping and git HEAD resolution.
- [x] T005: Implement AC/task/QC/coverage link extraction regex patterns.
- [x] T006: Implement _feature_peer_content and _baseline_peer_content for current and git-based file content retrieval.
- [x] T007: Implement _detect_spec_drift comparing current vs baseline ACs with removed/added classification.
- [x] T008: Implement _detect_code_drift checking orphaned source paths and task-to-AC reference completeness.
- [x] T009: Implement _detect_test_drift checking stale test links and uncovered spec ACs.
- [x] T010: Implement _detect_quality_drift checking missing QC/coverage links and non-tests/ paths.
- [x] T011: Implement _classify_severity returning highest severity across all event types.
- [x] T012: Implement _build_drift_history from git log with keyword-based severity classification.
- [x] T013: Implement _correlate_cross_feature_drift marking cascade_risk for dependency-linked critical features.
- [x] T014: Implement _build_compliance_section with SHA-256 evidence hash and per-dimension pass/fail.
- [x] T015: Implement _severity_distribution counting features by severity level.
- [x] T016: Implement _recommended_commands with deduplication.
- [x] T017: Implement build_drift_monitor_report as main entry point with feature_filter, baseline, and since parameters.
- [x] T018: Implement render_drift_json and render_drift_text for output formatting.

## Dependencies

- src/specspine/consistency.py (_read_text, _explicit_paths_from_feature_files, LOCAL_PATH_RE)
- src/specspine/dependency.py (_list_feature_slugs, _extract_slugs_from_text)
- src/specspine/evolution.py (_run_git)
- src/specspine/features.py (FEATURE_FILE_PATHS, InvalidFeatureSlug, feature_bundle_paths, list_feature_bundles, validate_feature_slug)

## Open Questions

- None; feature is implemented and tested.

## Agent Handoff

- Run `specspine feature handoff spec-drift-monitor . --json` before implementation or review handoff.
- Run `specspine adapters handoff spec-drift-monitor . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks spec-drift-monitor . --json` for the focused implementation checklist.
- Run `specspine feature task-issues spec-drift-monitor . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace spec-drift-monitor . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests spec-drift-monitor . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature spec-drift-monitor --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature spec-drift-monitor --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature spec-drift-monitor --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix spec-drift-monitor . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature spec-drift-monitor --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature spec-drift-monitor --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature spec-drift-monitor --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature spec-drift-monitor --json` to compose local pre-merge review evidence.
- Run `specspine feature ready spec-drift-monitor . --json` after implementation evidence is complete.
- Run `specspine feature pr spec-drift-monitor . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan spec-drift-monitor . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan spec-drift-monitor . --output-dir .specspine/sync-plan/spec-drift-monitor` to materialize local sync review artifacts.
- Run `specspine feature archive spec-drift-monitor . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
