# Feature Readiness Gate

Feature ID: feature-readiness-gate
Status: validated

## Why

Reviewers and implementation agents can already export trace evidence for native feature bundles, but they still need a deterministic local command that turns that evidence into a failing quality gate. The readiness gate makes feature completion explicit before a bundle is accepted as releasable.

## Users

- Maintainers deciding whether a native feature bundle is ready to merge or release.
- Implementation agents that need a local pass/fail gate after completing tasks.
- Reviewers checking whether acceptance, execution, quality, and release evidence are complete.

## Scope

- Add `specspine feature ready <slug> [path] [--json]` under the existing `feature` command group.
- Evaluate native feature peer files, lifecycle status, trace gaps, completed acceptance criteria, completed tasks, completed required checks, non-empty test plan content, and completed release readiness checklist items.
- Emit deterministic JSON and concise text output without calling GitHub, upstream CLIs, token sources, or network services.
- Return `0` only when the feature is ready, `1` when readiness checks fail or no native feature files exist, and `2` for invalid slugs.
- Dogfood the gate with this `feature-readiness-gate` bundle.

## Non-Goals

- Inferring semantic coverage between acceptance criteria and tasks.
- Running test commands or external verification tools from the readiness command.
- Replacing repository-level `specspine validate . --fusion --features`.
- Adding third-party Markdown parsing dependencies.

## Acceptance Criteria

- [x] `specspine feature ready <slug> [path] [--json]` is registered under the `feature` subcommand group.
- [x] JSON output includes `feature_id`, `ready`, `status`, `checks`, `blocking_checks`, `summary`, `missing_files`, and `gaps`.
- [x] Ready bundles return exit code `0`; failing bundles and missing bundles return exit code `1`; invalid slugs return exit code `2`.
- [x] Readiness checks cover peer file presence, peer status consistency, releasable lifecycle status, trace gaps, completed acceptance criteria, completed tasks, completed required checks, non-empty test plans, and completed release readiness checklist items.
- [x] Each readiness check has a stable id, pass/fail status, and message, with failed checks listed as blocking checks.
- [x] The implementation reuses native feature trace, task, and checklist parsing helpers and remains zero-dependency and local.
- [x] Documentation, execution artifacts, quality notes, dogfood artifacts, and tests describe the command and workflow.
