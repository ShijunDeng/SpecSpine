# Automated Compliance & Audit Trail Execution

Feature ID: automated-compliance-audit
Status: implemented
Why: Generate compliance-ready audit reports from all spec-driven development evidence. Tracks feature lifecycle transitions, validation evidence, and drift history for regulatory compliance.

## Milestones

- [x] M001: Core data structures (AuditEvent, AuditTrail, ComplianceReport) implemented with frozen dataclasses and as_dict serialization.
- [x] M002: Git-based audit event collection with commit classification by message keywords.
- [x] M003: Lifecycle transition tracking from spec file git history.
- [x] M004: Validation evidence gathering with AC/task/QC counting and coverage link validation.
- [x] M005: Drift history extraction from git log with severity classification.
- [x] M006: Compliance summary generation with per-feature pass/fail across 7 dimensions.
- [x] M007: Recommendation generation from compliance gaps.
- [x] M008: JSON and text renderers for compliance reports.

## Tasks

- [x] AC001 T001: Implement AuditEvent dataclass with event_type, timestamp, feature_id, description, evidence_hash, actor fields.
- [x] AC002 T002: Implement AuditTrail dataclass with feature_id, events, lifecycle_transitions, validation_evidence, drift_history.
- [x] AC003 T003: Implement ComplianceReport dataclass with root, audit_date, scope, features, compliance_summary, evidence_hashes, recommendations, safety_notes.
- [x] AC004 T004: Implement utility functions _now_iso and _hash_content for timestamping and SHA-256 hashing.
- [x] AC005 T005: Implement _feature_peer_content to read spec/execution/quality file contents for a given slug.
- [x] AC006 T006: Implement _collect_audit_events using git log with format=%H|%ai|%an|%s for each feature's peer files.
- [x] AC007 T007: Implement event type classification based on commit message keywords (lifecycle, validation, test, consistency).
- [x] AC008 T008: Implement evidence hash computation using git show to retrieve file contents at each commit.
- [x] AC009 T009: Implement _build_lifecycle_transitions by parsing Status: field from spec file history with diff-filter=ACDMR.
- [x] AC010 T010: Implement _gather_validation_evidence with AC count, task count, QC count, coverage link counting.
- [x] AC010 T011: Implement AC coverage validation comparing spec ACs against quality file coverage links.
- [x] AC010 T012: Implement _build_drift_history from git log with severity classification (high/low/medium).
- [x] AC010 T013: Implement _generate_compliance_summary with pass_fail_per_dimension, gaps, compliance_rate.
- [x] AC010 T014: Implement build_compliance_report as main entry point iterating all slugs or single feature_filter.
- [x] AC010 T015: Implement render_compliance_json and render_compliance_text for output formatting.
- [x] AC010 T016: Add safety_notes confirming only local files and git log/show are accessed.

## Dependencies

- src/specspine/consistency.py (_read_text utility)
- src/specspine/dependency.py (_list_feature_slugs)
- src/specspine/drift.py (_build_drift_history as _drift_build_history)
- src/specspine/evolution.py (_run_git utility)
- src/specspine/features.py (FEATURE_FILE_PATHS, FEATURE_STATUSES, feature_bundle_paths, list_feature_bundles, validate_feature_slug)

## Open Questions

- None; feature is implemented and tested.

## Agent Handoff

- Run `specspine feature handoff automated-compliance-audit . --json` before implementation or review handoff.
- Run `specspine adapters handoff automated-compliance-audit . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks automated-compliance-audit . --json` for the focused implementation checklist.
- Run `specspine feature task-issues automated-compliance-audit . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace automated-compliance-audit . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests automated-compliance-audit . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature automated-compliance-audit --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature automated-compliance-audit --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature automated-compliance-audit --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix automated-compliance-audit . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature automated-compliance-audit --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature automated-compliance-audit --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature automated-compliance-audit --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature automated-compliance-audit --json` to compose local pre-merge review evidence.
- Run `specspine feature ready automated-compliance-audit . --json` after implementation evidence is complete.
- Run `specspine feature pr automated-compliance-audit . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan automated-compliance-audit . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan automated-compliance-audit . --output-dir .specspine/sync-plan/automated-compliance-audit` to materialize local sync review artifacts.
- Run `specspine feature archive automated-compliance-audit . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
