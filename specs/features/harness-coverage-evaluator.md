# Harness Coverage Evaluator

Feature ID: harness-coverage-evaluator
Status: implemented
Priority: medium
Owner: unassigned
Milestone: unassigned
Target Release: unassigned
Project: unassigned
Effort: unknown

## Why

Evaluate harness coverage and quality across all 8 governed dimensions. Identify blind spots, detect sensor redundancy, generate improvement plans, and track harness maturity trends over time.

## Users

- Maintainers who need to assess the completeness of harness feedback sensors.
- AI agents that want to understand harness maturity before starting feature work.

## Scope

- Add `specspine harness coverage [path] [--feature <slug>] [--json]` command.
- Evaluate coverage across 8 dimensions: verification, coverage, grading, validation, consistency, hygiene, security, change_risk.
- Compute maturity score (0-5) based on sensor coverage and pass rates.
- Detect blind spots (dimensions with no sensors) and redundant sensors.
- Generate improvement plans with actionable recommendations.
- Support baseline comparison for trend analysis with `.specspine/harness-baseline.json`.
- Output stable JSON with dimensions, maturity_score, blind_spots, improvement_plan, baseline_comparison.
- Output concise text with per-dimension status and improvement recommendations.

## Non-Goals

- Running tests or invoking subprocesses; this is advisory local evidence.
- Calling GitHub APIs, reading tokens, or network access.
- Modifying harness sensors; only evaluates existing ones.

## Acceptance Criteria

- [x] `specspine harness coverage [path] [--feature <slug>] [--json]` produces a HarnessCoverageReport.
- [x] Report evaluates all 8 governed dimensions with sensor count, pass count, and coverage percentage.
- [x] Maturity score computed on 0-5 scale with labels: none, initial, managed, defined, optimized, mastered.
- [x] Blind spots detected as dimensions with zero sensors.
- [x] Redundant sensors detected when multiple sensors in a dimension share AC coverage.
- [x] Improvement plan generated with actionable steps for each blind spot and low-coverage dimension.
- [x] Baseline comparison supported via `.specspine/harness-baseline.json` with maturity delta and trend.
- [x] JSON output includes feature_id, dimensions, maturity_score, blind_spots, improvement_plan, baseline_comparison, safety_notes.
- [x] Text output shows per-dimension status, blind spots, improvement plan, and safety notes.
- [x] Workspace-level evaluation aggregates dimensions across all feature bundles.

## Edge Cases

- Empty workspaces produce a report with all dimensions at 0% coverage.
- Invalid feature slugs return exit code 2.
- Malformed baseline files are gracefully ignored.

## Constraints

- Read-only advisory evidence; no subprocess, network, or API calls.
- Zero dependencies beyond the existing SpecSpine codebase.

## Traceability Notes

- Implementation: `src/specspine/harness_coverage.py`
- Tests: `tests/test_harness_coverage.py`
