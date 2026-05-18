# Feature Readiness Gate Quality

Feature ID: feature-readiness-gate
Status: validated
Why: A readiness gate is only useful if it is deterministic, local, strict enough to fail incomplete bundles, and easy for reviewers to inspect.

## Required Checks

- [x] Unit tests cover ready JSON/text output and non-ready exit behavior.
- [x] Unit tests cover invalid slug exit code `2` and missing native feature files exit code `1`.
- [x] Unit tests cover representative failures for missing peer files, inconsistent peer status, unreleasable lifecycle status, trace gaps, incomplete acceptance criteria, missing tasks, missing required checks, missing test plan content, and incomplete release readiness checklist items.
- [x] Dogfood tests assert that `feature-readiness-gate` is validated and passes its own readiness gate.
- [x] Documentation describes `feature ready` as a local reviewer and agent quality gate.
- [x] The implementation does not call GitHub APIs, read tokens, call upstream CLIs, access network services, or add third-party dependencies.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_cli_returns_zero_for_ready_bundle_text_and_json
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_cli_returns_zero_for_ready_bundle_text_and_json
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_cli_returns_zero_for_ready_bundle_text_and_json
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_cli_reports_core_failures_for_partial_bundle
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_cli_invalid_slug_returns_two
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_cli_missing_bundle_returns_report_and_nonzero
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_cli_reports_core_failures_for_partial_bundle
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_cli_reports_trace_gaps_without_missing_files
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_cli_reports_unfinished_required_checklists
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_cli_reports_empty_test_plan
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_cli_reports_core_failures_for_partial_bundle
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_ready_require_coverage_does_not_read_tokens_or_call_network
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_dogfood_feature_readiness_gate_is_validated_and_ready

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-readiness-gate . --json`.
- Run the requested repository token-prefix scan and confirm no credential token prefixes are present.

## Review Notes

- The readiness gate intentionally evaluates local Markdown state and trace completeness; it does not execute test plan commands.
- The command is suitable for CI or reviewer gates because failed checks are returned as `blocking_checks` and cause exit code `1`.
- Missing bundles produce a readiness report instead of a stack trace or remote lookup.

## Release Readiness

- [x] `feature-readiness-gate` has complete spec, execution, and quality peer files.
- [x] Lifecycle status is `validated` across all peer files.
- [x] Acceptance criteria, tasks, required checks, test plan, and release readiness evidence are complete.
- [x] Local verification commands for this round pass.
