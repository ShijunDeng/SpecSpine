# Feature Metadata Filters Quality

Feature ID: feature-metadata-filters
Status: validated
Why: Metadata triage changes which local feature an agent may pick next, so filters and sorts must be deterministic, compatible, and safely local.

## Required Checks

- [x] Unit tests cover each new filter with single and repeated values.
- [x] Unit tests cover default normalization for old or blank metadata.
- [x] Unit tests cover each new sort key and descending behavior.
- [x] Unit tests cover invalid sort key errors listing the expanded key set.
- [x] Unit tests cover using new filters without `--feature-summaries`.
- [x] Existing priority, owner, status, and ready filters continue to pass.
- [x] No-unsafe status summary tests include the new metadata filters and sort.
- [x] Dogfood readiness passes default, coverage-required, and policy gates.

## Test Coverage

- [x] AC001 -> tests/test_status.py::StatusTests::test_status_feature_metadata_filters_single_and_repeated_values
- [x] AC002 -> tests/test_status.py::StatusTests::test_status_feature_metadata_filters_single_and_repeated_values
- [x] AC003 -> tests/test_status.py::StatusTests::test_status_feature_metadata_filters_single_and_repeated_values
- [x] AC004 -> tests/test_status.py::StatusTests::test_status_feature_metadata_filters_single_and_repeated_values
- [x] AC005 -> tests/test_status.py::StatusTests::test_status_feature_metadata_filters_match_default_values
- [x] AC006 -> tests/test_status.py::StatusTests::test_status_feature_summary_options_require_feature_summaries
- [x] AC007 -> tests/test_status.py::StatusTests::test_status_feature_summary_invalid_options_return_two
- [x] AC008 -> tests/test_status.py::StatusTests::test_status_feature_metadata_sort_keys_and_descending_order
- [x] AC009 -> tests/test_status.py::StatusTests::test_status_feature_priority_and_owner_filters
- [x] AC009 -> tests/test_status.py::StatusTests::test_status_feature_status_filter_single_and_multiple_values
- [x] AC009 -> tests/test_status.py::StatusTests::test_status_feature_ready_filter_accepts_aliases
- [x] AC010 -> tests/test_status.py::StatusTests::test_status_feature_summaries_do_not_call_gh_network_or_read_tokens
- [x] AC010 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_metadata_filters_dogfood_bundle_passes_default_coverage_and_policy_gates

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine status . --json --feature-summaries --feature-project "Native feature bundles" --feature-sort effort`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-metadata-filters . --json --require-coverage`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-metadata-filters . --json --policy`.

## Review Notes

- Metadata filters use the same normalized values already shown in feature summaries.
- Metadata sort keys keep default buckets last while preserving existing sort behavior for older keys.
- The status command still builds local reports only; it does not execute remote commands or read credentials.

## Release Readiness

- [x] Default feature summary output remains compatible.
- [x] New filters and sorts are covered by unit tests.
- [x] Dogfood bundle passes default readiness, coverage readiness, policy readiness, and validation.
- [x] Documentation and agent guidance describe metadata triage as local-only behavior.
