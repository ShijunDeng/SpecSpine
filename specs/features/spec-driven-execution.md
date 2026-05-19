# Spec-Driven Execution Orchestrator

Feature ID: spec-driven-execution
Status: implemented
Priority: medium
Owner: unassigned
Milestone: unassigned
Target Release: unassigned
Project: unassigned
Effort: unknown

## Why

Autonomous spec-to-implementation orchestration with outcomes-based grading system for AI agents to self-correct until all acceptance criteria pass.

## Users

- AI agents that need structured execution plans derived from spec, execution, and quality files.
- Developers who need to understand the dependency-ordered implementation sequence for a feature.
- QA engineers who need grading rubrics to verify acceptance criteria coverage completeness.
- Tech leads who need execution loop results showing iteration-by-iteration pass/fail progress.

## Scope

- `build_execution_plan(slug, root)` returns a dict with plan_steps, dependency_order, verification_commands, grading_rubric, and summary.
- `build_grading_rubric(slug, root)` returns a dict with rubric_items evaluating each AC's pass/warn/fail status based on done checkbox and coverage link completeness.
- `run_execution_loop(slug, root, max_iterations)` simulates iterative execution grading, returning iteration results, final_status, and remaining_gaps.
- `_build_steps_from_contents` parses tasks from execution file, maps them to ACs from spec file, resolves task dependencies, and produces ordered steps with blocked status.
- `_topo_sort_steps` uses topological_sort from dependency module to order steps by dependency; falls back to original order on cycles.
- `_build_grading_rubric_internal` evaluates each AC as pass (done + coverage complete), warn (done + partial coverage, or coverage exists but AC not done), or fail (no coverage).
- Grading rubric also includes a QUALITY_CHECKS item evaluating all quality checks as pass (all done) or warn (some open).
- `_build_verification_commands` returns 6 standard commands: verify matrix, feature trace, feature tests, feature ready, consistency scan, and validate.
- Execution loop runs up to max_iterations (clamped 1-10), grading rubric items each iteration, stopping early if no gaps remain.
- JSON and text renderers for plan (`render_plan_json/text`), grade (`render_grade_json/text`), and loop (`render_loop_json/text`) outputs.

## Non-Goals

- Does not execute any code, tests, or implementation steps; only builds plans and simulates grading.
- Does not modify feature bundles, spec files, or test files.
- Does not invoke external tools or APIs during execution loop simulation.
- Does not provide real-time execution monitoring; each call is a point-in-time snapshot.
- Does not handle multi-feature dependency ordering; only orders tasks within a single feature.

## Acceptance Criteria

- [x] AC001: `build_execution_plan` returns a dict with root, feature_id, feature_status, plan_steps, dependency_order, verification_commands, grading_rubric, summary, and safety_notes.
- [x] AC002: `_build_steps_from_contents` maps tasks to ACs by text similarity (case-insensitive substring match) and resolves task dependencies from execution file text.
- [x] AC003: `_topo_sort_steps` orders steps by dependency using topological_sort; falls back to original step order when cycles are detected.
- [x] AC004: Plan steps include blocked status computed from dependency completion; blocked_reason lists uncompleted dependencies.
- [x] AC005: `build_grading_rubric` returns rubric items with ac_id, ac_text, check_type, pass_criteria, current_status (pass/warn/fail), and gap_reason.
- [x] AC006: Grading status is "pass" when AC is done and coverage is complete; "warn" when done with partial coverage or coverage exists but AC not done; "fail" when no coverage.
- [x] AC007: Grading rubric includes a QUALITY_CHECKS item evaluating all quality checks with pass/warn status.
- [x] AC008: `run_execution_loop` iterates up to max_iterations (clamped 1-10), grading rubric each iteration, stopping early when no gaps remain.
- [x] AC009: Execution loop final_status is "complete" when no gaps, "gaps_remaining" when gaps persist after max iterations, or "incomplete" initially.
- [x] AC010: FeatureBundleNotFoundError is raised when feature bundle has no content files (spec, execution, quality).

## Edge Cases

- Feature with no tasks: plan_steps is empty list; dependency_order is empty; summary shows total_steps=0.
- Feature with circular task dependencies: topological_sort returns None; falls back to original step order.
- Quality file with no coverage links: all ACs graded as "fail" with gap_reason "No test coverage links found".
- AC marked done but no coverage links: graded as "fail" because coverage_complete is false.
- Quality checks all done: QUALITY_CHECKS item graded as "pass"; partial completion graded as "warn".
- max_iterations=0: clamped to minimum of 1; loop runs at least once.
- max_iterations>10: clamped to maximum of 10; prevents excessive iteration.
- Feature status unknown: feature_status defaults to "unknown" when get_feature_status returns None.

## Constraints

- Task-to-AC mapping uses case-insensitive substring matching (either AC text in task text or task text in AC text).
- Task dependency parsing uses regex pattern: (?:after|depends\s+on|blocked\s+by)\s+([Tt]\d{3,}).
- Verification commands are fixed 6 commands: verify matrix, feature trace, feature tests, feature ready, consistency scan, validate.
- Safety notes confirm no tests, subprocesses, network calls, GitHub API calls, upstream CLIs, environment variables, or tokens are accessed.
- Feature slug validation follows the standard `[a-z0-9]([a-z0-9-]*[a-z0-9])?` pattern.

## Traceability Notes

- Source: src/specspine/executor.py (594 lines)
- Tests: tests/test_executor.py
- Execution plan building: src/specspine/executor.py lines 108-163, 277-358
- Topological sorting: src/specspine/executor.py lines 166-179
- Grading rubric: src/specspine/executor.py lines 193-274, 361-385
- Execution loop: src/specspine/executor.py lines 388-460
- Plan text/JSON renderers: src/specspine/executor.py lines 463-522
- Grade text/JSON renderers: src/specspine/executor.py lines 525-550
- Loop text/JSON renderers: src/specspine/executor.py lines 553-594
