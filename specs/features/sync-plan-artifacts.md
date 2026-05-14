# Materialize Sync Plan Artifacts

Feature ID: sync-plan-artifacts
Status: validated
Priority: high
Owner: SpecSpine maintainers

## Why

Maintainers need `feature sync-plan` to write the local body files and manifest that its planned GitHub CLI argv references, so remote sync review can happen from inspectable files without executing `gh`.

## Users

- [x] Maintainers reviewing GitHub issue and Pull Request bodies before manually running GitHub CLI commands.
- [x] Review agents checking that sync intent, body files, and safety flags are traceable from a local manifest.
- [x] Release agents preparing draft PR and task issue material without reading tokens or touching the network.

## Scope

- [x] Add `specspine feature sync-plan <slug> [path] --output-dir DIR`.
- [x] Write `manifest.json`, `feature-issue.md`, `task-issues/T001.md`, `pull-request.md`, and `commands.sh` under the requested directory.
- [x] Keep `--output FILE` as the text-plan export and allow `--json --output-dir` to print JSON while writing artifacts.
- [x] Reject overwriting command-owned artifact files unless `--force` is passed, while preserving unknown files in the output directory.
- [x] Make `commands.sh` review-only text with shell-quoted `gh ... --body-file <local file>` commands and no automatic execution behavior.

## Non-Goals

- [x] Do not execute `gh`, call GitHub APIs, probe GitHub CLI, read tokens, use network access, or call subprocesses.
- [x] Do not add a remote-sync command or confirmation workflow in this feature.
- [x] Do not rely on PR dry-run as a safety guarantee.
- [x] Do not map local `Owner:` metadata to GitHub assignees.
- [x] Do not delete unknown files from artifact output directories.

## Acceptance Criteria

- [x] `--output-dir` writes manifest, feature issue body, task issue bodies, PR body, and commands script for a complete bundle.
- [x] `manifest.json` includes the existing sync-plan JSON plus local artifact path fields and an artifact index.
- [x] `commands.sh` contains review-only comments and shell-quoted `gh` commands that use `--body-file` paths pointing at written local files.
- [x] PR commands include `--draft` and generated artifact command data omits the PR dry-run flag.
- [x] JSON stdout remains compatible when `--json` is combined with `--output-dir`.
- [x] Existing command-owned files are refused without `--force`; `--force` overwrites only those files and preserves unknown files.
- [x] Every remote command keeps `creates_remote=true`, `requires_token=true`, `requires_network=true`, and `safe_to_auto_run=false`.
- [x] Tests prove no subprocess, GitHub CLI lookup, network call, or GitHub token read occurs.

## Edge Cases

- [x] Existing output directories are allowed when command-owned files do not conflict.
- [x] Output paths that are files instead of directories fail clearly.
- [x] Partial bundles still write the artifacts for commands the sync plan can derive.
- [x] Stable task issue filenames use existing task ids such as `T001.md`.

## Constraints

- [x] Use only Python standard library APIs.
- [x] Preserve the existing `feature sync-plan --json` schema for stdout.
- [x] Keep artifact paths stable and relative to the manifest directory.
- [x] Follow existing exporter overwrite semantics.

## Traceability Notes

- [x] AC001 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_writes_reviewable_artifacts`
- [x] AC002 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_writes_reviewable_artifacts`
- [x] AC003 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_writes_reviewable_artifacts`
- [x] AC004 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_writes_reviewable_artifacts`
- [x] AC005 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_json_stdout_and_output_dir_both_work`
- [x] AC006 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_overwrite_requires_force`
- [x] AC007 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_writes_reviewable_artifacts`
- [x] AC008 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_dir_does_not_read_tokens_call_network_or_subprocess`
