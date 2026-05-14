# GitHub Sync Plan Quality

Feature ID: github-sync-plan
Status: validated
Why: The local GitHub sync plan must be reviewable and deterministic without weakening SpecSpine's no-token, no-network default.

## Required Checks

- [x] JSON shape and command counts are covered by unit tests.
- [x] Command argv arrays include expected labels and omit `--assignee` and `--dry-run`.
- [x] Text output includes safety notes and shell-quoted commands for human review only.
- [x] Output-file behavior matches existing exporters, including `--json --output`.
- [x] Partial, missing, and invalid bundle return codes are tested.
- [x] External-call isolation covers token reads, subprocess calls, `gh`, and network access.
- [x] Dogfood readiness and validation pass for `github-sync-plan`.
- [x] README, architecture, product, execution, review, and AGENTS guidance describe local sync planning accurately.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_text_output_contains_safe_command_lines_and_notes
- [x] AC008 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_text_output_contains_safe_command_lines_and_notes
- [x] AC009 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_file_overwrite_force_and_json_output
- [x] AC010 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_partial_bundle_returns_zero_with_missing_info
- [x] AC011 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_does_not_read_tokens_call_network_or_subprocess

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
- Run `PYTHONPATH=src python3 -m specspine feature sync-plan github-sync-plan . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready github-sync-plan . --json`.
- Run `git diff --check`.
- Run the repository token-prefix scan.

## Review Notes

- [x] The implementation intentionally generates argv arrays and text commands only; it never executes them.
- [x] `--dry-run` is deliberately omitted from PR argv because it is not a safe automatic execution guarantee.
- [x] Owner metadata is left as review context and is never converted to GitHub assignees automatically.
- [x] Priority is represented as a portable label instead of GitHub Issue Fields API usage.

## Release Readiness

- [x] Acceptance criteria are implemented and covered by focused tests.
- [x] Documentation and agent guidance describe the local-only safety model.
- [x] `specspine feature ready github-sync-plan . --json` passes.
- [x] `specspine validate . --fusion --features` passes.
- [x] No known blockers remain.
