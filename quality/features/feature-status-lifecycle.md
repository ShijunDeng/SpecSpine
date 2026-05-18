# Feature Status Lifecycle Quality

Feature ID: feature-status-lifecycle
Status: validated
Why: Status changes affect CLI behavior, validation gates, and machine-readable agent context.

## Required Checks

- [x] Querying status as JSON includes `feature_id`, `status`, `consistent`, `files`, and `missing_files`.
- [x] Setting status as JSON also includes `updated_files`.
- [x] Invalid status and slug inputs use return code `2`.
- [x] Partial bundles preserve missing file reporting and update existing peer files.
- [x] `validate --features` accepts every allowed status.
- [x] `validate --features` fails invalid or mixed statuses.
- [x] `specspine status . --json` includes this dogfood feature as consistent and validated.
- [x] Token-prefix scan does not find GitHub secret patterns.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_json_query_reports_consistent_status
- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_text_reports_lifecycle_value_for_consistent_status
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_set_updates_existing_peer_files
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_validate_features_accepts_all_allowed_statuses
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_rejects_invalid_status_and_slug
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_status_cli_set_updates_partial_bundle_only
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_validate_features_accepts_all_allowed_statuses
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_validate_features_rejects_illegal_status
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_validate_features_rejects_mixed_status
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_status_json_lists_feature_files
- [x] AC006 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_current_repository_reports_complete_fused_workspace
- [x] AC007 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_status_lifecycle_bundle_has_no_todo_placeholders
- [x] AC007 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_status_lifecycle_dogfood_bundle_passes_default_and_coverage_gates

## Test Plan

- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `PYTHONPATH=src python3 -m specspine status . --json`
- `PYTHONPATH=src python3 -m specspine validate . --fusion --features`
- Repository token-prefix scan for GitHub secret patterns.

## Review Notes

- The implementation keeps lifecycle state in the peer Markdown files instead of adding a sidecar index.
- JSON output is built from local file reads only and does not touch environment tokens or network APIs.
- Status consistency is a validation failure so agents cannot accidentally treat divergent peer files as a ready feature.

## Release Readiness

- [x] CLI behavior is covered by unit tests.
- [x] Validation and status JSON behavior are covered by unit tests.
- [x] Documentation and dogfood artifacts are aligned with the implemented lifecycle states.
