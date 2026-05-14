# Status Feature Summaries

Feature ID: status-feature-summaries
Status: validated

## Why

Workspace startup status is intentionally compact, but agents sometimes need to choose between several native features before opening a focused handoff packet. Optional feature summaries let that comparison happen from one local status call without expanding the default context payload.

## Users

- Implementation agents deciding which native feature to work on next.
- Review agents comparing ready gates, gaps, and blocking checks across features.
- Maintainers checking workspace progress before assigning follow-up work.

## Scope

- Add `specspine status [path] --feature-summaries`.
- Keep default `specspine status [path] --json` and default text output unchanged.
- Include compact per-feature JSON summaries with lifecycle status, completeness, readiness, missing files, task counts, ready counts, gap count, blocking count, next actions, and recommended local commands.
- Include a short text `Feature summaries` section only when the flag is present.
- Reuse local feature bundle discovery and feature handoff evidence without network calls, token reads, GitHub API calls, upstream CLI calls, or new dependencies.
- Handle invalid feature filenames without crashing status output.

## Non-Goals

- Replacing focused `feature handoff`, `feature trace`, `feature tasks`, or `feature ready` commands.
- Running tests or readiness evidence dynamically from the status command.
- Adding generated or AI-inferred recommendations.

## Acceptance Criteria

- [x] `status` accepts `--feature-summaries` with `--json`, `--validate`, and `--adapters`.
- [x] Default JSON status omits `feature_summaries`.
- [x] JSON status with the flag includes stable compact summaries for native feature bundles.
- [x] Text status with the flag includes a short `Feature summaries` section.
- [x] Partial bundles expose missing files, gap counts, blocking counts, and deterministic next actions.
- [x] Invalid feature slugs do not crash workspace status.
- [x] Agent guidance explains that startup remains compact and summaries are for comparing multiple features.
