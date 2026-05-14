# GitHub Sync Plan

Feature ID: github-sync-plan
Status: validated
Priority: high
Owner: SpecSpine maintainers

## Why

SpecSpine already exports offline feature issue drafts, task issue draft packages, and Pull Request drafts. Maintainers now need one reviewable local bridge that shows exactly which GitHub CLI commands a human could run later, while keeping default workflows token-free, network-free, and safe from accidental remote writes.

## Users

- [x] Maintainers preparing GitHub issue and Pull Request synchronization after local feature evidence is complete.
- [x] Review agents checking whether remote sync intent matches the local SpecSpine bundle.
- [x] Release agents that need labels and draft body sources before any GitHub resource is created.

## Scope

- [x] Add `specspine feature sync-plan <slug> [path] [--json] [--output FILE] [--force]`.
- [x] Compose the plan from existing local feature issue, task issue, PR, metadata, status, and readiness evidence.
- [x] Export GitHub CLI argv arrays for feature issue, task issues, and draft Pull Request creation.
- [x] Include safety fields, notes, recommended local commands, and body source references without executing anything.

## Non-Goals

- [x] Do not create remote GitHub issues, Pull Requests, projects, milestones, or issue fields.
- [x] Do not call `gh`, GitHub APIs, network services, upstream CLIs, or subprocesses.
- [x] Do not read, write, validate, or print GitHub tokens.
- [x] Do not map free-form local owner metadata to GitHub assignees automatically.

## Acceptance Criteria

- [x] `specspine feature sync-plan <slug> . --json` returns a stable JSON plan for a partial or complete native feature bundle.
- [x] JSON includes feature id, status, readiness, sources, missing files, gaps, blockers, metadata, summary, commands, notes, and recommended commands.
- [x] A feature-level `gh issue create` command includes title, body-file, and labels for `specspine`, feature slug, status, and priority.
- [x] One task-level `gh issue create` command is generated for each execution checklist task with task labels.
- [x] A draft `gh pr create` command is generated with `--draft` and no `--dry-run`.
- [x] Every planned command records `creates_remote=true`, `requires_token=true`, `requires_network=true`, and `safe_to_auto_run=false`.
- [x] Notes explain non-execution, manual authentication, project scope, PR dry-run risk, local priority labels, and owner-to-assignee behavior.
- [x] Text output is reviewable Markdown with summary, metadata, notes, commands, safety fields, and shell-quoted command lines.
- [x] `--output` writes text with overwrite protection; `--json --output` prints JSON and writes text.
- [x] Partial bundles return `0` with missing evidence; all missing bundles return `1`; invalid slugs return `2`.
- [x] Tests prove no subprocess, `gh`, network, token read, or dependency is required.

## Edge Cases

- [x] Missing execution files produce no task issue commands but still keep feature issue and PR commands when another peer file exists.
- [x] `Priority: unknown` remains deterministic through a `priority:unknown` label.
- [x] `Owner:` metadata always adds an owner-to-assignee safety note and never adds `--assignee`.
- [x] Shell-quoted text is only for human copy/paste review and is never executed by SpecSpine.

## Constraints

- [x] Use only Python standard library APIs.
- [x] Reuse existing local draft/readiness builders rather than duplicating feature parsing logic.
- [x] Keep command argv as arrays in JSON so downstream agents do not need to parse shell strings.
- [x] Keep roadmap wording clear that this is a local sync plan before remote execution, not real remote synchronization.

## Traceability Notes

- [x] AC001 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands`
- [x] AC002 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands`
- [x] AC003 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands`
- [x] AC004 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands`
- [x] AC005 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands`
- [x] AC006 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_json_outputs_reviewable_github_commands`
- [x] AC007 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_text_output_contains_safe_command_lines_and_notes`
- [x] AC008 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_cli_text_output_contains_safe_command_lines_and_notes`
- [x] AC009 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_output_file_overwrite_force_and_json_output`
- [x] AC010 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_partial_bundle_returns_zero_with_missing_info`
- [x] AC011 -> `tests/test_features.py::FeatureBundleTests::test_feature_sync_plan_does_not_read_tokens_call_network_or_subprocess`
