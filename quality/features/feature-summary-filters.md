# Feature Summary Filters Quality

Feature ID: feature-summary-filters
Status: validated
Why: Filtering and sorting are agent-facing triage behavior, so they must remain deterministic, local, and compatible with compact startup status.

## Required Checks

- [x] Unit tests verify default feature summaries remain compatible and default `status --json` stays compact.
- [x] Unit tests verify `--feature-status` single and repeated filters.
- [x] Unit tests verify `--feature-ready` ready and not-ready aliases.
- [x] Unit tests verify every supported `--feature-sort` key and descending order.
- [x] Unit tests verify no-match JSON returns an empty list and text output shows `none`.
- [x] Unit tests verify summary filter and sort options without `--feature-summaries` return code `2`.
- [x] Unit tests verify unsupported status, readiness, and sort values return code `2`.
- [x] Dogfood validation verifies this bundle has consistent `validated` lifecycle status.
- [x] Dogfood readiness verifies this bundle passes the local feature gate.

## Test Coverage

- [x] AC001 -> tests/test_status.py::StatusTests::test_status_json_cli_output_is_parseable
- [x] AC001 -> tests/test_status.py::StatusTests::test_status_text_feature_summaries_are_opt_in
- [x] AC002 -> tests/test_status.py::StatusTests::test_status_json_cli_can_include_feature_summaries
- [x] AC002 -> tests/test_status.py::StatusTests::test_status_text_feature_summaries_are_opt_in
- [x] AC003 -> tests/test_status.py::StatusTests::test_status_feature_status_filter_single_and_multiple_values
- [x] AC003 -> tests/test_status.py::StatusTests::test_status_feature_status_filter_accepts_invalid_and_unknown
- [x] AC004 -> tests/test_status.py::StatusTests::test_status_feature_ready_filter_accepts_aliases
- [x] AC005 -> tests/test_status.py::StatusTests::test_status_feature_sort_keys_and_descending_order
- [x] AC005 -> tests/test_status.py::StatusTests::test_status_text_feature_summaries_apply_filters_and_sorting
- [x] AC006 -> tests/test_status.py::StatusTests::test_status_feature_summary_filter_no_matches_text_and_json
- [x] AC007 -> tests/test_status.py::StatusTests::test_status_feature_summary_options_require_feature_summaries
- [x] AC008 -> tests/test_status.py::StatusTests::test_status_feature_summary_invalid_options_return_two
- [x] AC009 -> tests/test_status.py::StatusTests::test_status_feature_summaries_do_not_call_gh_network_or_read_tokens
- [x] AC009 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_feature_summary_filters_dogfood_bundle_passes_its_gate

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries --feature-status validated --feature-ready yes --feature-sort slug`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-summary-filters . --json`.
- Run the repository token-prefix scan requested for this feature.

## Review Notes

- The status command still composes local feature summary evidence and does not call GitHub, upstream tools, network services, or token-backed APIs.
- Default status output remains compact because feature summaries and their filters are opt-in.
- Invalid option handling returns code `2` before status construction so unsupported values are not silently ignored.

## Release Readiness

- [x] Default status compatibility is preserved.
- [x] Feature summary filters and sorting are deterministic and local.
- [x] Documentation and agent guidance describe the new triage flags.
- [x] Validation and dogfood readiness pass.
