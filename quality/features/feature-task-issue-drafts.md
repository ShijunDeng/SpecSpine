# Feature Task Issue Drafts Quality

Feature ID: feature-task-issue-drafts
Status: validated
Why: Task issue drafts are useful only if they are local, deterministic, complete, and aligned with the existing exporter contract.

## Required Checks

- [x] Unit tests cover task issue JSON and text output for a ready bundle.
- [x] Unit tests cover partial bundles with missing execution files.
- [x] Unit tests cover all-missing bundles and invalid slugs.
- [x] Unit tests cover output overwrite protection and `--force`.
- [x] Unit tests guard against GitHub token use and subprocess invocation.
- [x] Documentation and agent guidance describe offline task issue drafts.
- [x] Dogfood readiness and validation pass for `feature-task-issue-drafts`.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_task_issues_cli_text_and_json_outputs_ready_bundle
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_task_issues_cli_text_and_json_outputs_ready_bundle
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_task_issues_cli_text_and_json_outputs_ready_bundle
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_task_issues_output_file_overwrite_force_and_json_output
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_task_issues_handles_missing_execution_partial_bundle
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_task_issues_does_not_require_gh_tokens_network_or_subprocess
- [x] AC007 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_agents_file_preserves_project_rules

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_features.FeatureBundleTests`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_dogfood_artifacts.DogfoodArtifactsTests`.
- Run `PYTHONPATH=src python3 -m specspine feature task-issues feature-task-issue-drafts . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-task-issue-drafts . --json`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.

## Review Notes

- The report composes existing local task and trace evidence instead of creating a remote GitHub issue.
- File output writes the text package even when JSON is printed to stdout.
- The command follows existing feature exporter exit codes for partial, missing, invalid, and output conflict cases.

## Release Readiness

- [x] Acceptance criteria, execution tasks, required checks, and test plan evidence are complete.
- [x] README, architecture, product, execution, quality, AGENTS, and agent template guidance mention the command.
- [x] `specspine feature task-issues feature-task-issue-drafts . --json` output is stable and local.
- [x] `specspine feature ready feature-task-issue-drafts . --json` and `specspine validate . --fusion --features` have been run.
- [x] No known blockers remain.
