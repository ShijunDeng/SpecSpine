# Offline Pull Request Draft Export

Feature ID: feature-pr-draft
Status: validated

## Why

SpecSpine already turns native feature bundles into local issue drafts, task lists, trace packets, readiness gates, and agent handoffs. Review and release agents also need a Pull Request-shaped artifact that carries the same evidence into GitHub review conventions without creating a remote PR, reading credentials, or depending on upstream code.

## Users

- Maintainers preparing review text before opening a Pull Request.
- AI coding agents that need a stable local PR packet for acceptance and release review.
- Teams using Spec Kit PR Bridge-style workflows while keeping SpecSpine as the local source of truth.

## Scope

- Add `specspine feature pr <slug> [path] [--json] [--output FILE] [--force]`.
- Compose the draft from existing local feature status, handoff, trace, readiness, release readiness, and source-file evidence.
- Emit stable JSON and GitHub Markdown text without calling GitHub APIs, `gh`, network services, or token reads.
- Preserve partial-bundle behavior by generating drafts with missing files, gaps, and blocking checks recorded.

## Non-Goals

- Creating remote Pull Requests.
- Synchronizing with GitHub branches, reviews, labels, projects, or checks.
- Copying OpenSpec, Spec Kit, Superpowers, or PR Bridge source code.

## Acceptance Criteria

- [x] `specspine feature pr <slug> [path] [--json] [--output FILE] [--force]` is registered under the `feature` command group.
- [x] JSON output includes title, body, feature id, status, readiness, source files, missing files, gaps, blocking checks, summary, and recommended commands.
- [x] Text output includes title and a Pull Request body with Summary, Feature, Why, Acceptance Criteria, Tasks, Test Plan, Release Readiness, Readiness / Blocking Checks, Source Files, Missing Files, and Key Commands.
- [x] Acceptance criteria, tasks, release readiness, gaps, and readiness checks use GitHub Markdown checklist syntax.
- [x] Partial bundles return zero with missing evidence recorded, while bundles with no native feature files return non-zero.
- [x] Invalid slugs return code `2`.
- [x] The command remains offline, deterministic, zero-dependency, and free of GitHub token/API assumptions.
