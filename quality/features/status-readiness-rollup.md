# Status Readiness Rollup Quality

Feature ID: status-readiness-rollup
Status: validated
Why: The rollup can steer agent and CI decisions across the whole workspace, so compatibility, deterministic gates, and policy interactions must be covered explicitly.

## Required Checks

- [x] Default status JSON and text output remain unchanged unless `--readiness-summary` is passed.
- [x] JSON rollup includes workspace totals, compact per-feature readiness records, and focused recommended commands.
- [x] Per-feature records include readiness, lifecycle status, coverage-required state, policy coverage state, blocker count, gap count, missing files, next actions, and recommended commands.
- [x] Coverage-required rollups reuse the same `feature.test_coverage` gate as focused feature readiness.
- [x] Policy rollups load `.specspine/policy.yaml`, add policy fields, and count policy-selected coverage requirements.
- [x] Explicit coverage-required mode overrides policy selection by requiring coverage for every feature.
- [x] Text output adds only a short opt-in Readiness summary section with not-ready features.
- [x] Readiness-only options without `--readiness-summary` return code `2`.
- [x] The implementation remains local-only and dependency-free.

## Test Coverage

- [x] AC001 -> tests/test_status.py::StatusTests::test_status_json_cli_output_is_parseable
- [x] AC001 -> tests/test_status.py::StatusTests::test_status_text_readiness_summary_is_opt_in
- [x] AC002 -> tests/test_status.py::StatusTests::test_status_json_cli_can_include_readiness_summary
- [x] AC003 -> tests/test_status.py::StatusTests::test_status_json_cli_can_include_readiness_summary
- [x] AC004 -> tests/test_status.py::StatusTests::test_status_json_cli_can_include_readiness_summary
- [x] AC005 -> tests/test_status.py::StatusTests::test_status_json_readiness_summary_can_require_coverage
- [x] AC006 -> tests/test_status.py::StatusTests::test_status_json_readiness_summary_policy_adds_policy_fields
- [x] AC007 -> tests/test_status.py::StatusTests::test_status_json_readiness_summary_policy_adds_policy_fields
- [x] AC008 -> tests/test_status.py::StatusTests::test_status_text_readiness_summary_is_opt_in
- [x] AC009 -> tests/test_status.py::StatusTests::test_status_readiness_summary_options_require_readiness_summary
- [x] AC010 -> tests/test_status.py::StatusTests::test_status_readiness_summary_does_not_call_gh_network_or_read_tokens
- [x] AC011 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_status_readiness_rollup_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_status`.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready status-readiness-rollup . --json --require-coverage`.
- Run the repository token-prefix scan requested for this feature.

## Review Notes

- The rollup is opt-in so the existing compact status packet remains stable.
- The implementation composes existing local readiness and policy logic rather than adding another gate definition.
- Recommended commands are advisory strings only; status does not execute them.
- Coverage link checks remain metadata-only and never run tests.

## Release Readiness

- [x] Implementation, tests, and docs are complete.
- [x] Default status compatibility is preserved.
- [x] Coverage-required and policy rollups are covered.
- [x] This dogfood bundle has checked local coverage links.
- [x] `specspine validate . --fusion --features` passes.
