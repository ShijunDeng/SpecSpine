# Workspace Readiness Policy Quality

Feature ID: workspace-readiness-policy
Status: validated
Why: Workspace governance must be machine-readable and auditable while remaining opt-in for existing repositories.

## Required Checks

- [x] Missing policy files do not break status, validation, or policy export.
- [x] Policy parsing is dependency-free and limited to the documented local YAML subset.
- [x] Unknown priority and status values are warnings, not command failures.
- [x] `feature ready --policy` reports policy application fields and uses the existing coverage gate when selected.
- [x] `--require-coverage` and `--feature-require-coverage` remain explicit overrides.
- [x] `status --feature-policy` requires `--feature-summaries` and computes readiness per feature.
- [x] Default command behavior remains compatible when policy flags are absent.
- [x] Repository dogfood policy targets only this feature.

## Test Coverage

- [x] AC001 -> tests/test_policy.py::WorkspacePolicyTests::test_policy_missing_reports_defaults_without_failure
- [x] AC002 -> tests/test_policy.py::WorkspacePolicyTests::test_policy_parser_supports_require_coverage_selectors
- [x] AC003 -> tests/test_policy.py::WorkspacePolicyTests::test_invalid_policy_values_warn_without_failure
- [x] AC004 -> tests/test_policy.py::WorkspacePolicyTests::test_feature_ready_policy_selectors_require_coverage
- [x] AC005 -> tests/test_policy.py::WorkspacePolicyTests::test_feature_ready_require_coverage_overrides_policy
- [x] AC006 -> tests/test_policy.py::WorkspacePolicyTests::test_status_feature_policy_requires_feature_summaries
- [x] AC007 -> tests/test_policy.py::WorkspacePolicyTests::test_status_feature_policy_ready_filter_uses_policy_readiness
- [x] AC008 -> tests/test_policy.py::WorkspacePolicyTests::test_default_status_and_ready_remain_compatible
- [x] AC009 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_workspace_readiness_policy_dogfood_bundle_passes_default_coverage_and_policy_gates
- [x] AC010 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_workspace_readiness_policy_artifacts_are_present

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine policy . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready workspace-readiness-policy . --json --policy`.
- Run `PYTHONPATH=src python3 -m specspine status . --json --feature-summaries --feature-policy --feature-ready yes`.

## Review Notes

- The policy file is optional governance context; absence means defaults and no stricter coverage selection.
- Policy mode never runs tests. It only checks local coverage links already recorded in quality artifacts.
- The repository policy intentionally selects only this dogfood feature to avoid redefining historical readiness.

## Release Readiness

- [x] Implementation, tests, docs, and dogfood artifacts are complete.
- [x] Default readiness remains unchanged.
- [x] Coverage-required readiness works through explicit flags and policy selection.
- [x] `specspine validate . --fusion --features` passes.
