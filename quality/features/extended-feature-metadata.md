# Extended Feature Metadata Quality

Feature ID: extended-feature-metadata
Status: validated
Why: Extended metadata affects local triage, handoffs, and sync review packets, so compatibility and no-remote boundaries need explicit coverage.

## Required Checks

- [x] Unit tests verify generated feature specs include the new default metadata.
- [x] Unit tests verify old feature specs parse with default extended metadata.
- [x] Unit tests verify all new metadata fields parse and serialize.
- [x] Unit tests verify status summaries include extended metadata and remain compatible with missing fields.
- [x] Unit tests verify issue and PR drafts include extended metadata in JSON and Markdown bodies.
- [x] Unit tests verify sync-plan JSON, manifest, and body artifacts include extended metadata.
- [x] Existing no-remote sync-plan tests continue to block subprocess, network, GitHub, and token behavior.
- [x] Dogfood readiness passes default, coverage, and policy gates.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_create_feature_bundle_in_plain_workspace
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_read_feature_metadata_defaults_for_old_files
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_read_feature_metadata_parses_extended_fields
- [x] AC004 -> tests/test_status.py::StatusTests::test_status_json_cli_can_include_feature_summaries
- [x] AC004 -> tests/test_status.py::StatusTests::test_status_feature_summaries_include_extended_metadata
- [x] AC005 -> tests/test_status.py::StatusTests::test_status_text_feature_summaries_are_opt_in
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_issue_and_pr_include_extended_metadata
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_writes_reviewable_artifacts
- [x] AC008 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_extended_feature_metadata_dogfood_bundle_passes_default_coverage_and_policy_gates
- [x] AC009 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_does_not_read_tokens_call_network_or_subprocess

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine status . --json --feature-summaries --feature-sort priority`.
- Run `PYTHONPATH=src python3 -m specspine feature sync-plan extended-feature-metadata . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready extended-feature-metadata . --json --require-coverage`.
- Run `PYTHONPATH=src python3 -m specspine feature ready extended-feature-metadata . --json --policy`.

## Review Notes

- Extended fields remain local metadata and are not mapped to GitHub assignees, Projects, milestones, or typed issue fields.
- Default values preserve compatibility for existing feature specs.
- The sync-plan command still emits reviewable argv arrays and body files only; it does not execute remote operations.

## Release Readiness

- [x] Metadata defaults and parsing are covered.
- [x] Status, handoff, tests, issue, PR, and sync-plan outputs carry the same metadata dictionary.
- [x] Sync-plan artifacts include metadata in both manifest and body files.
- [x] Documentation and agent guidance describe the local-only metadata contract.
- [x] Default readiness, coverage readiness, policy readiness, and validation pass.
