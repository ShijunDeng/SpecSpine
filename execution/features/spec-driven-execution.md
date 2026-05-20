# Spec-Driven Execution Orchestrator Execution

Feature ID: spec-driven-execution
Status: implemented
Why: Autonomous spec-to-implementation orchestration with outcomes-based grading system for AI agents to self-correct until all acceptance criteria pass.

## Milestones

- [x] M001: Core data structures (ExecutionPlan, GradingRubric, ExecutionLoopResult) implemented with frozen dataclasses and as_dict serialization.
- [x] M002: Step building from feature contents with task-to-AC mapping and dependency resolution.
- [x] M003: Topological sorting of steps with cycle detection fallback.
- [x] M004: Blocked status computation from dependency completion state.
- [x] M005: Grading rubric with per-AC pass/warn/fail evaluation based on done status and coverage completeness.
- [x] M006: Quality checks grading item with aggregate pass/warn status.
- [x] M007: Execution loop simulation with configurable max_iterations (clamped 1-10).
- [x] M008: Verification command generation (6 standard commands).
- [x] M009: JSON and text renderers for plan, grade, and loop outputs.

## Tasks

- [x] AC001 T001: Implement ExecutionPlan dataclass with root, feature_id, feature_status, plan_steps, dependency_order, verification_commands, grading_rubric, summary, safety_notes.
- [x] AC002 T002: Implement GradingRubric dataclass with feature_id and rubric_items.
- [x] AC003 T003: Implement ExecutionLoopResult dataclass with feature_id, iterations, final_status, remaining_gaps.
- [x] AC004 T004: Implement regex patterns for checkbox tasks, AC IDs, dependency patterns, and task dependency patterns.
- [x] AC005 T005: Implement _parse_task_dependencies extracting task dependency IDs from text.
- [x] AC006 T006: Implement _read_feature_contents loading spec, execution, quality files from feature bundle paths.
- [x] AC007 T007: Implement _build_steps_from_contents parsing tasks, mapping to ACs, resolving dependencies, and building step dicts.
- [x] AC008 T008: Implement _topo_sort_steps using topological_sort with cycle fallback.
- [x] AC009 T009: Implement _build_verification_commands returning 6 standard commands.
- [x] AC010 T010: Implement _build_grading_rubric_internal evaluating AC coverage completeness and quality check status.
- [x] AC010 T011: Implement build_execution_plan as main entry point with FeatureBundleNotFoundError for empty bundles.
- [x] AC010 T012: Implement build_grading_rubric as standalone entry point for rubric-only queries.
- [x] AC010 T013: Implement run_execution_loop with configurable max_iterations and early termination on no gaps.
- [x] AC010 T014: Implement render_plan_json and render_plan_text for plan output formatting.
- [x] AC010 T015: Implement render_grade_json and render_grade_text for grade output formatting.
- [x] AC010 T016: Implement render_loop_json and render_loop_text for loop output formatting.

## Dependencies

- src/specspine/dependency.py (topological_sort)
- src/specspine/features.py (FEATURE_FILE_PATHS, FeatureBundleNotFoundError, InvalidFeatureSlug, _extract_markdown_section, _extract_markdown_section_lines, feature_bundle_paths, get_feature_status, parse_acceptance_criteria, parse_feature_tasks, parse_quality_checks, parse_test_coverage, parse_test_plan, read_feature_metadata, validate_feature_slug)

## Open Questions

- None; feature is implemented and tested.

## Agent Handoff

- Run `specspine feature handoff spec-driven-execution . --json` before implementation or review handoff.
- Run `specspine adapters handoff spec-driven-execution . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks spec-driven-execution . --json` for the focused implementation checklist.
- Run `specspine feature task-issues spec-driven-execution . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace spec-driven-execution . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests spec-driven-execution . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature spec-driven-execution --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature spec-driven-execution --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature spec-driven-execution --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix spec-driven-execution . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature spec-driven-execution --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature spec-driven-execution --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature spec-driven-execution --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature spec-driven-execution --json` to compose local pre-merge review evidence.
- Run `specspine feature ready spec-driven-execution . --json` after implementation evidence is complete.
- Run `specspine feature pr spec-driven-execution . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan spec-driven-execution . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan spec-driven-execution . --output-dir .specspine/sync-plan/spec-driven-execution` to materialize local sync review artifacts.
- Run `specspine feature archive spec-driven-execution . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
