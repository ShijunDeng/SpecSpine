# Spec-Governed Multi-Agent Orchestration Execution

Feature ID: spec-multi-agent-orchestration
Status: implemented
Why: Coordinate multiple AI agents implementing features in parallel with conflict detection, dependency sequencing, and cross-feature integration validation.

## Milestones

- [x] M001: Core data structures (OrchestrationConflict, ParallelGroup, OrchestrationPlan, OrchestrationReport) implemented with frozen dataclasses and as_dict serialization.
- [x] M002: File conflict detection scanning feature file paths for overlapping references.
- [x] M003: Contract conflict detection extracting endpoints, schemas, and configs using regex patterns.
- [x] M004: Semantic conflict detection for conflicting enable/disable configurations.
- [x] M005: Dependency graph construction and topological sorting for execution ordering.
- [x] M006: Parallel group computation using in-degree based scheduling.
- [x] M007: Integration recommendation generation for conflicts and multi-dependency features.
- [x] M008: JSON and text renderers for orchestration reports.

## Tasks

- [x] T001: Implement OrchestrationConflict dataclass with conflict_type, affected_files, affected_ac_ids, features_involved, severity, description.
- [x] T002: Implement ParallelGroup dataclass with group_id and features tuple.
- [x] T003: Implement OrchestrationPlan dataclass with execution_order, parallel_groups, blocked_features, safe_for_parallel.
- [x] T004: Implement OrchestrationReport dataclass with root, feature_filter, conflicts, plan, integration_recommendations, status, blocking_items, safety_notes.
- [x] T005: Implement contract regex patterns: CONTRACT_PATTERN, API_ENDPOINT_PATTERNS, SCHEMA_PATTERNS, CONFIG_PATTERNS.
- [x] T006: Implement _scan_feature_file_paths extracting file path references from feature content.
- [x] T007: Implement _extract_ac_ids using regex for AC\d{3,4} patterns.
- [x] T008: Implement _build_dependency_graph using _extract_slugs_from_text from dependency module.
- [x] T009: Implement _detect_file_conflicts comparing file path sets between feature pairs.
- [x] T010: Implement _extract_contracts extracting endpoint, schema, and config contracts from content.
- [x] T011: Implement _detect_contract_conflicts comparing contract sets between feature pairs.
- [x] T012: Implement _detect_semantic_conflicts detecting conflicting enable/disable configurations.
- [x] T013: Implement _compute_parallel_groups using in-degree based scheduling with remaining set tracking.
- [x] T014: Implement _generate_integration_recommendations producing recommendations for file/contract overlap and multi-dependency features.
- [x] T015: Implement build_orchestration_plan as main entry point with feature_filter support.
- [x] T016: Implement render_orchestration_json and render_orchestration_text for output formatting.

## Dependencies

- src/specspine/dependency.py (_extract_slugs_from_text, _list_feature_slugs, _read_all_feature_content, _topological_sort)
- src/specspine/features.py (FEATURE_FILE_PATHS, read_feature_metadata, validate_feature_slug)

## Open Questions

- None; feature is implemented and tested.

## Agent Handoff

- Run `specspine feature handoff spec-multi-agent-orchestration . --json` before implementation or review handoff.
- Run `specspine adapters handoff spec-multi-agent-orchestration . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks spec-multi-agent-orchestration . --json` for the focused implementation checklist.
- Run `specspine feature task-issues spec-multi-agent-orchestration . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace spec-multi-agent-orchestration . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests spec-multi-agent-orchestration . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature spec-multi-agent-orchestration --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature spec-multi-agent-orchestration --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature spec-multi-agent-orchestration --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix spec-multi-agent-orchestration . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature spec-multi-agent-orchestration --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature spec-multi-agent-orchestration --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature spec-multi-agent-orchestration --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature spec-multi-agent-orchestration --json` to compose local pre-merge review evidence.
- Run `specspine feature ready spec-multi-agent-orchestration . --json` after implementation evidence is complete.
- Run `specspine feature pr spec-multi-agent-orchestration . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan spec-multi-agent-orchestration . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan spec-multi-agent-orchestration . --output-dir .specspine/sync-plan/spec-multi-agent-orchestration` to materialize local sync review artifacts.
- Run `specspine feature archive spec-multi-agent-orchestration . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
