# Feature Task Issue Drafts

Feature ID: feature-task-issue-drafts
Status: validated

## Why

Implementation agents often need task-level GitHub issue text, but SpecSpine must keep that workflow local and deterministic. A task issue draft package lets each execution checklist item become a reviewable issue draft without reading tokens, calling GitHub, invoking `gh`, or depending on upstream CLIs.

## Users

- Maintainers who split native feature work into task-sized GitHub issues.
- Implementation agents that need one issue body per execution task.
- Reviewers who want to inspect task-level draft text before any remote issue is created.

## Scope

- Add `specspine feature task-issues <slug> [path] [--json] [--output FILE] [--force]`.
- Build one issue draft per execution checklist task from `execution/features/<slug>.md`.
- Compose draft bodies from existing local task, trace, and feature status evidence.
- Preserve existing exporter behavior for JSON stdout and text file output.
- Document the offline, token-free, subprocess-free command in user and agent guidance.

## Non-Goals

- Creating, updating, or syncing remote GitHub issues.
- Reading GitHub tokens or requiring `gh`.
- Calling Spec Kit, OpenSpec, Superpowers, network APIs, or upstream CLIs.
- Inferring tasks from prose outside the execution checklist.

## Acceptance Criteria

- [x] `feature task-issues` is registered under the `feature` command group with `--json`, `--output`, and `--force`.
- [x] JSON output includes `feature_id`, `status`, `source_file`, `source_missing`, `missing_files`, `issues`, `summary`, and `recommended_commands`.
- [x] Each issue draft includes `title`, `body`, `feature_id`, `task_id`, `task_text`, `task_done`, `source_file`, and `line`.
- [x] Text output is a local GitHub issue draft package with each issue title and body.
- [x] Partial bundles with missing execution files return zero with empty issues and `source_missing=true`, while all-missing bundles return non-zero.
- [x] The command remains offline, token-free, network-free, subprocess-free, zero-dependency, and deterministic.
- [x] Documentation, agent guidance, generated templates, tests, and dogfood artifacts describe the task issue draft workflow.

## Edge Cases

- Missing execution peer file while spec or quality peers exist.
- Execution peer file exists but has no checklist tasks.
- Invalid feature slug.
- Existing output file without `--force`.
- Long task text in issue titles.

## Constraints

- Use only Python standard library and existing local SpecSpine parsers.
- Do not vendor upstream source code.
- Do not read environment tokens.
- Do not call network APIs or subprocesses.

## Traceability Notes

- AC001 maps to CLI registration and command parsing tests.
- AC002 and AC003 map to JSON output tests.
- AC004 maps to text output and file export tests.
- AC005 maps to partial and missing bundle tests.
- AC006 maps to token and subprocess guard tests.
- AC007 maps to README, architecture, product, execution, quality, agent, and dogfood updates.
