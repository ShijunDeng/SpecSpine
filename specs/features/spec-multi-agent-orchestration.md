# Spec-Governed Multi-Agent Orchestration

Feature ID: spec-multi-agent-orchestration
Status: implemented
Priority: medium
Owner: unassigned
Milestone: unassigned
Target Release: unassigned
Project: unassigned
Effort: unknown

## Why

Coordinate multiple AI agents implementing features in parallel with conflict detection, dependency sequencing, and cross-feature integration validation.

## Users

- Engineering managers who need to plan parallel feature implementation across multiple AI agents.
- Tech leads who need to identify file overlap, contract conflicts, and semantic conflicts between features.
- Developers who need to understand execution order and parallel groups for their features.
- QA engineers who need to know which features have blocking conflicts that must be resolved before integration.

## Scope

- `build_orchestration_plan(root, feature_filter)` returns an `OrchestrationReport` with conflicts, execution plan, integration recommendations, status, and blocking items.
- `_detect_file_conflicts` scans feature file paths for overlapping references between feature pairs; severity is high if >3 shared paths, medium otherwise.
- `_detect_contract_conflicts` extracts contracts (endpoints, schemas, configs) from feature content using regex patterns; severity is critical if endpoint overlap, high otherwise.
- `_detect_semantic_conflicts` detects conflicting enable/disable configurations between feature pairs; severity is critical.
- `_build_dependency_graph` builds adjacency list of feature dependencies using _extract_slugs_from_text from dependency module.
- `_topological_sort` computes topological ordering of features; reversed order used for execution (dependencies first).
- `_compute_parallel_groups` computes parallel execution groups using in-degree based scheduling; features with no remaining dependencies are grouped together.
- `_generate_integration_recommendations` produces recommendations for file overlap, contract overlap, integration testing order, and multi-dependency features.
- `OrchestrationPlan` includes execution_order, parallel_groups, blocked_features, and safe_for_parallel boolean.
- `OrchestrationConflict` includes conflict_type (file/contract/semantic), affected_files, affected_ac_ids, features_involved, severity, and description.
- JSON and text renderers (`render_orchestration_json`, `render_orchestration_text`) provide structured and human-readable output.

## Non-Goals

- Does not execute any features or invoke AI agents; only plans and detects conflicts.
- Does not modify any feature bundles or source files.
- Does not resolve conflicts automatically; only reports them with recommendations.
- Does not integrate with external orchestration platforms or agent frameworks.
- Does not provide real-time orchestration monitoring; each call is a point-in-time snapshot.

## Acceptance Criteria

- [x] AC001: `build_orchestration_plan` returns an `OrchestrationReport` with root, feature_filter, conflicts, plan, integration_recommendations, status, blocking_items, and safety_notes.
- [x] AC002: `_detect_file_conflicts` identifies overlapping file path references between feature pairs with severity high (>3 shared) or medium.
- [x] AC003: `_detect_contract_conflicts` extracts contracts using CONTRACT_PATTERN, API_ENDPOINT_PATTERNS, SCHEMA_PATTERNS, CONFIG_PATTERNS; severity critical for endpoint overlap, high for schema/config.
- [x] AC004: `_detect_semantic_conflicts` detects conflicting enable/disable configurations between feature pairs with critical severity.
- [x] AC005: `_build_dependency_graph` returns adjacency dict mapping each slug to its set of dependency slugs extracted from feature content.
- [x] AC006: `_topological_sort` returns reversed topological order for execution (dependencies before dependents); returns empty list on cycles.
- [x] AC007: `_compute_parallel_groups` computes parallel execution groups using in-degree scheduling; features with zero in-degree grouped together per iteration.
- [x] AC008: `OrchestrationPlan` includes safe_for_parallel=True only when single parallel group and no blocking conflicts.
- [x] AC009: Report status is "ok" when no blocking items, "blocked" when critical conflicts exist, "warnings" when only high/medium conflicts exist.
- [x] AC010: `_generate_integration_recommendations` produces recommendations for file overlap, contract overlap, integration testing, and multi-dependency features.

## Edge Cases

- No features: empty slugs list; all conflict detection returns empty; plan has empty execution order; status is "ok".
- Single feature: no pairwise conflicts possible; execution order has single entry; one parallel group.
- Circular dependencies: topological sort returns None; execution order is empty list; blocking item added for cycle detection.
- Feature with no peer files: _scan_feature_file_paths returns empty set; no file conflicts detected for that feature.
- Contract pattern doesn't match: _extract_contracts returns empty dict; no contract conflicts for that feature pair.
- All features independent: all features in single parallel group; safe_for_parallel=True.
- Semantic conflict deduplication: checked_pairs set prevents duplicate conflict reports for same feature pair.

## Constraints

- Contract extraction uses case-insensitive regex patterns for endpoints, schemas, and configs.
- File path scanning skips lines starting with "src", "tests", "docs" and lines without "/" character.
- Severity levels: critical (semantic conflicts, endpoint overlaps), high (file conflicts >3, schema/config overlaps), medium (file conflicts <=3).
- Parallel group computation uses in-degree based scheduling with remaining set tracking.
- Safety notes confirm only local workspace files are read; no tests, subprocesses, network, or tokens.
- Feature slug validation follows the standard `[a-z0-9]([a-z0-9-]*[a-z0-9])?` pattern.

## Traceability Notes

- Source: src/specspine/orchestration.py (554 lines)
- Tests: tests/test_orchestration.py
- Conflict data structures: src/specspine/orchestration.py lines 38-107
- File conflict detection: src/specspine/orchestration.py lines 146-176
- Contract extraction: src/specspine/orchestration.py lines 179-197
- Contract conflict detection: src/specspine/orchestration.py lines 200-251
- Semantic conflict detection: src/specspine/orchestration.py lines 254-311
- Parallel group computation: src/specspine/orchestration.py lines 314-350
- Integration recommendations: src/specspine/orchestration.py lines 353-405
- Main entry point: src/specspine/orchestration.py lines 408-489
- Text/JSON renderers: src/specspine/orchestration.py lines 492-554
