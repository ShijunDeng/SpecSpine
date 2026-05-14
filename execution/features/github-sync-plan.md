# GitHub Sync Plan Execution

Feature ID: github-sync-plan
Status: validated
Why: Provide a reviewable local GitHub CLI synchronization plan without executing remote operations.

## Milestones

- [x] Define the sync plan shape around existing issue, task issue, PR, metadata, and readiness evidence.
- [x] Implement the local report builder and Markdown/JSON renderers.
- [x] Register the CLI command with exporter-style output semantics.
- [x] Add dogfood documentation and tests.

## Tasks

- [x] Add sync-plan dataclasses and stable command records in `src/specspine/features.py`.
- [x] Reuse `build_issue_draft`, `build_feature_task_issues_report`, `build_pull_request_draft`, `read_feature_metadata`, and readiness/handoff helpers.
- [x] Generate feature issue, task issue, and draft PR argv arrays with deterministic labels.
- [x] Mark every remote-creating command as requiring token/network and not safe to auto-run.
- [x] Render reviewable text with shell-quoted command lines through the standard library.
- [x] Register `specspine feature sync-plan` in `src/specspine/cli.py`.
- [x] Preserve exporter output behavior for text, JSON, `--output`, and `--force`.
- [x] Cover complete, partial, missing, invalid, output, safety, and dogfood behavior in tests.
- [x] Update README, architecture docs, product specs, execution plan, review notes, and agent guidance.
- [x] Verify validation, readiness, unit tests, diff whitespace, and token-prefix scan.

## Dependencies

- [x] Existing local feature issue, task issue, PR, metadata, handoff, and readiness builders.
- [x] Python standard library `shlex` for human-readable shell quoting.

## Open Questions

- [x] Remote execution remains out of scope until a future feature specifies confirmation, authentication, project scope handling, and failure recovery.
- [x] GitHub Issue Fields remain out of scope until they are generally available enough to model portably.

## Agent Handoff

- Run `specspine feature sync-plan github-sync-plan . --json` to inspect the generated GitHub CLI sync intent.
- Run `specspine feature issue github-sync-plan . --json` to inspect the feature issue body.
- Run `specspine feature task-issues github-sync-plan . --json` to inspect task issue bodies.
- Run `specspine feature pr github-sync-plan . --json` to inspect the draft Pull Request body.
- Run `specspine feature ready github-sync-plan . --json` to confirm the dogfood bundle is ready.
- Run `specspine validate . --fusion --features` before handoff.
