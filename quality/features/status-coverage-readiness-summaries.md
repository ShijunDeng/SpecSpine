# Status Coverage Readiness Summaries Quality

Feature ID: status-coverage-readiness-summaries
Status: validated
Why: The stricter summary mode influences agent scheduling, so compatibility and coverage-aware filtering must be explicit and locally verifiable.

## Required Checks

- [x] Default feature summary JSON fields and readiness counts remain unchanged.
- [x] Coverage-required summaries use the same `feature.test_coverage` gate as `feature ready --require-coverage`.
- [x] Coverage-required summaries add `coverage_required: true` without adding that field to default summaries.
- [x] Missing, unchecked, or missing-target coverage appears as a blocking next action.
- [x] `--feature-ready yes/no` filters coverage-required readiness when requested.
- [x] Text summaries show a concise coverage-required marker only under the new flag.
- [x] Summary-only option validation includes `--feature-require-coverage`.
- [x] The implementation remains local-only and dependency-free.

## Test Coverage

- [x] AC001 -> tests/test_status.py::StatusTests::test_status_json_feature_summaries_can_require_coverage
- [x] AC002 -> tests/test_status.py::StatusTests::test_status_json_cli_can_include_feature_summaries
- [x] AC003 -> tests/test_status.py::StatusTests::test_status_feature_summary_options_require_feature_summaries
- [x] AC004 -> tests/test_status.py::StatusTests::test_status_json_feature_summaries_can_require_coverage
- [x] AC005 -> tests/test_status.py::StatusTests::test_status_json_feature_summaries_can_require_coverage
- [x] AC006 -> tests/test_status.py::StatusTests::test_status_feature_require_coverage_ready_filter_uses_coverage_gate
- [x] AC007 -> tests/test_status.py::StatusTests::test_status_text_feature_summaries_show_coverage_requirement
- [x] AC008 -> tests/test_status.py::StatusTests::test_status_feature_summaries_do_not_call_gh_network_or_read_tokens
- [x] AC009 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_status_coverage_readiness_summaries_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries --feature-require-coverage --feature-ready yes --feature-sort priority`.
- Run `PYTHONPATH=src python3 -m specspine feature ready status-coverage-readiness-summaries . --json --require-coverage`.

## Review Notes

- The summary mode changes only opt-in status behavior; default summaries still use default readiness and omit `coverage_required`.
- The coverage gate is metadata validation only and uses existing local coverage target checks.
- No test command, upstream command, network request, or token lookup is performed by status summary construction.

## Release Readiness

- [x] Implementation, tests, and docs are complete.
- [x] Default summary behavior remains compatible.
- [x] Coverage-required status summaries expose coverage blockers and filters.
- [x] This dogfood bundle passes default and coverage-required readiness.
- [x] `specspine validate . --fusion --features` passes.
