# Materialize Sync Plan Artifacts Quality

Feature ID: sync-plan-artifacts
Status: validated
Why: Local GitHub sync artifacts must be reviewable without weakening SpecSpine's no-token, no-network, no-subprocess default.

## Required Checks

- [x] Artifact directory layout and manifest fields are covered by focused unit tests.
- [x] JSON stdout compatibility with `--output-dir` is covered.
- [x] Overwrite protection and `--force` behavior are covered.
- [x] `commands.sh` and manifest safety invariants are covered, including no PR dry-run flag and draft PR commands.
- [x] External-call isolation covers subprocess calls, GitHub token reads, and network access.
- [x] Documentation and agent guidance describe `--output-dir` as a local review workflow.
- [x] Dogfood readiness and validation pass for `sync-plan-artifacts`.

## Test Coverage

- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_writes_reviewable_artifacts
- [x] AC002 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_writes_reviewable_artifacts
- [x] AC003 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_writes_reviewable_artifacts
- [x] AC004 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_writes_reviewable_artifacts
- [x] AC005 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_json_stdout_and_output_dir_both_work
- [x] AC006 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_overwrite_requires_force
- [x] AC007 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_writes_reviewable_artifacts
- [x] AC008 -> tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_does_not_read_tokens_call_network_or_subprocess

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_features.FeatureBundleTests.test_feature_sync_plan_output_dir_writes_reviewable_artifacts tests.test_features.FeatureBundleTests.test_feature_sync_plan_json_stdout_and_output_dir_both_work tests.test_features.FeatureBundleTests.test_feature_sync_plan_output_dir_overwrite_requires_force tests.test_features.FeatureBundleTests.test_feature_sync_plan_output_dir_does_not_read_tokens_call_network_or_subprocess`.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready sync-plan-artifacts . --json`.

## Review Notes

- [x] The implementation writes local files only and does not chmod or execute `commands.sh`.
- [x] The manifest enhances command records with `body_file` and `artifact_path` while preserving existing sync-plan fields.
- [x] Existing stdout JSON is intentionally unchanged so current scripts remain compatible.
- [x] `commands.sh` uses local artifact paths for `--body-file`, includes `--draft` for PR creation, and contains no PR dry-run flag.

## Release Readiness

- [x] Acceptance criteria are implemented and covered by focused tests.
- [x] Documentation and agent guidance describe local artifact review.
- [x] `specspine feature ready sync-plan-artifacts . --json` passes.
- [x] `specspine validate . --fusion --features` passes.
- [x] No known blockers remain.
