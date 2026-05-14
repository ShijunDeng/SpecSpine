# Feature Summary Metadata Quality

Feature ID: feature-summary-metadata
Status: validated
Why: Metadata triage affects agent feature selection, so output and filters must remain deterministic, local, and compatible with compact default status.

## Required Checks

- [x] Unit tests verify JSON summaries include priority and owner.
- [x] Unit tests verify generated feature specs include `Priority: medium` and `Owner: unassigned`.
- [x] Unit tests verify priority and owner filters require `--feature-summaries`.
- [x] Unit tests verify invalid priority filters return code `2` with a clear error.
- [x] Unit tests verify priority sort covers `high`, `medium`, `low`, `unknown`, and descending order.
- [x] Unit tests verify text summaries display priority and owner.
- [x] Dogfood validation verifies this bundle has consistent `validated` lifecycle status.
- [x] Dogfood readiness verifies this bundle passes the local feature gate.
- [x] Token-prefix scanning verifies no GitHub token was added.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_in_plain_workspace
- [x] AC002 -> tests/test_status.py::StatusTests::test_status_json_cli_can_include_feature_summaries
- [x] AC006 -> tests/test_status.py::StatusTests::test_status_feature_summary_options_require_feature_summaries
- [x] AC007 -> tests/test_status.py::StatusTests::test_status_feature_summary_invalid_options_return_two
- [x] AC009 -> tests/test_status.py::StatusTests::test_status_feature_priority_sort_covers_unknown_and_descending

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-summary-metadata . --json`.
- Run `git diff --check`.
- Run the repository GitHub token-prefix scan and confirm it produces no matches.

## Review Notes

- Priority and owner are read from the spec peer only; execution and quality files remain focused on delivery and evidence.
- Invalid priority metadata is normalized to `unknown` rather than failing validation, preserving compatibility for existing bundles.
- Owner filtering is exact after case folding so local routing stays deterministic.
- No GitHub API, `gh`, network, token, or upstream CLI path is introduced.

## Release Readiness

- [x] Default status JSON remains compact without feature summaries.
- [x] Feature summary metadata is visible only in opt-in summaries.
- [x] Filtering, sorting, and invalid option behavior are covered by unit tests.
- [x] Documentation describes the source of truth and CLI behavior.
- [x] Validation, readiness, and token-prefix checks pass.
