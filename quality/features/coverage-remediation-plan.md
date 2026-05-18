# Coverage Remediation Plan Quality

Feature ID: coverage-remediation-plan
Status: validated

## Required Checks

- [x] JSON output exposes stable top-level fields and per-item remediation fields for missing AC coverage.
- [x] Text output is concise and includes safety notes that keep the plan advisory.
- [x] Policy mode follows the same workspace readiness policy selection as coverage debt and feature readiness.
- [x] Feature filtering distinguishes existing features, missing features, and invalid slugs with the required exit codes.
- [x] Limit handling trims only item rows and leaves summary counts stable.
- [x] No-debt workspaces return success with empty plan items.
- [x] The implementation reads local SpecSpine files only and does not execute tests, subprocesses, network calls, GitHub APIs, upstream CLIs, or token providers.
- [x] Documentation and agent guidance describe the command as read-only remediation planning, not proof of test quality.

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_coverage_plan`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_coverage_debt tests.test_agents tests.test_dogfood_artifacts`.
- Run `PYTHONPATH=src python3 -m specspine coverage plan . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready coverage-remediation-plan . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready coverage-remediation-plan . --json --require-coverage`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.

## Review Notes

- Coverage gaps are treated as planning signals. The command suggests quality links but never writes them.
- Recommended commands are local follow-up commands and are not executed by the planner.

## Release Readiness

- [x] JSON and text output have focused remediation content for reviewer and agent workflows.
- [x] Missing feature, invalid slug, and invalid limit behavior is deterministic.
- [x] Safety notes explicitly state that coverage links do not prove test quality.
- [x] Dogfood readiness passes default and coverage-required gates.

## Test Coverage

- [x] AC001 -> tests/test_coverage_plan.py::CoveragePlanTests::test_json_reports_actionable_items_for_missing_acceptance_criteria
- [x] AC002 -> tests/test_coverage_plan.py::CoveragePlanTests::test_text_output_includes_plan_items_and_safety_notes
- [x] AC003 -> tests/test_coverage_plan.py::CoveragePlanTests::test_policy_mode_limits_plan_items_to_policy_selected_features
- [x] AC004 -> tests/test_coverage_plan.py::CoveragePlanTests::test_feature_filter_focuses_summary_and_items
- [x] AC005 -> tests/test_coverage_plan.py::CoveragePlanTests::test_limit_trims_items_without_changing_summary
- [x] AC006 -> tests/test_coverage_plan.py::CoveragePlanTests::test_missing_feature_returns_structured_report_and_exit_one
- [x] AC007 -> tests/test_coverage_plan.py::CoveragePlanTests::test_invalid_slug_and_negative_limit_return_usage_error
- [x] AC008 -> tests/test_coverage_plan.py::CoveragePlanTests::test_coverage_plan_does_not_call_subprocess_network_or_read_tokens
