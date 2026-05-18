# Offline Pull Request Draft Export Quality

Feature ID: feature-pr-draft
Status: validated
Why: The PR draft bridge must be reviewable, local, deterministic, and credential-free before agents rely on it.

## Required Checks

- [x] CLI parser accepts `feature pr` with `--json`, `--output`, and `--force`.
- [x] JSON output exposes the required PR draft fields with deterministic ordering.
- [x] Text output uses GitHub Markdown checklist syntax for reviewable evidence.
- [x] Partial bundles produce drafts with missing files, gaps, and blocking checks.
- [x] Missing bundles return non-zero and invalid slugs return `2`.
- [x] Output files refuse overwrite unless `--force` is passed.
- [x] Tests confirm the command does not require `gh`, GitHub tokens, subprocess calls, or network access.
- [x] Documentation and agent instructions describe the command as an offline draft bridge.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_pr_cli_generates_text_for_ready_bundle
- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_pr_cli_json_output_is_parseable
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_pr_cli_json_output_is_parseable
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_pr_cli_generates_text_for_ready_bundle
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_pr_cli_generates_text_for_ready_bundle
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_pr_partial_bundle_marks_missing_files
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_pr_all_files_missing_returns_nonzero
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_pr_invalid_slug_returns_two
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_feature_pr_output_file_overwrite_force_and_json_output
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_feature_pr_does_not_need_gh_api_or_token
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_feature_pr_does_not_read_tokens_or_call_network

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-pr-draft . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature pr feature-pr-draft . --json`.
- Run the repository GitHub personal access token prefix scan with ripgrep.

## Review Notes

- The implementation composes existing local evidence and does not create a GitHub adapter or remote synchronization layer.
- The `--output` file contains only the PR body so callers can paste or bridge it into external tools while stdout remains JSON when requested.

## Release Readiness

- [x] Unit tests cover the new command behavior.
- [x] Dogfood feature bundle is validated and ready.
- [x] Documentation identifies the command as local, offline, and token-free.
- [x] No upstream source code is vendored.
