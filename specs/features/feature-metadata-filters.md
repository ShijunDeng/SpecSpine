# Feature Metadata Filters

Feature ID: feature-metadata-filters
Status: validated
Priority: high
Owner: SpecSpine maintainers
Milestone: Local triage metadata
Target Release: next
Project: Native feature bundles
Effort: M

## Why

Maintainers and agents need to select the next local feature from structured metadata before any remote GitHub Project, Issue Field, milestone, or typed field sync exists. SpecSpine already records milestone, target release, project, and effort locally, so the optional feature summary view should let users filter and sort by those fields without leaving the repository.

## Users

- Maintainers comparing native feature bundles by release, project, or effort.
- Implementation agents choosing a ready item from structured local metadata.
- Review and release agents preparing local handoff context before any remote synchronization.

## Scope

- Add repeatable `--feature-milestone`, `--feature-target-release`, `--feature-project`, and `--feature-effort` filters to `specspine status --feature-summaries`.
- Normalize missing milestone, target release, and project values to `unassigned`, and missing effort to `unknown`.
- Extend `--feature-sort` with `milestone`, `target-release`, `project`, and `effort`.
- Keep default feature summary JSON and text output unchanged unless a new filter or sort is requested.
- Keep every new option local, deterministic, dependency-free, network-free, token-free, and valid only with `--feature-summaries`.

## Non-Goals

- Calling GitHub APIs, invoking `gh`, reading tokens, or writing remote Issue Fields or Project fields.
- Adding remote sync behavior for metadata filters.
- Requiring existing feature specs to add the newer metadata fields.
- Changing existing priority, owner, status, readiness, or default feature summary behavior.

## Acceptance Criteria

- [x] `--feature-milestone VALUE` filters feature summaries by normalized milestone and is repeatable.
- [x] `--feature-target-release VALUE` filters feature summaries by normalized target release and is repeatable.
- [x] `--feature-project VALUE` filters feature summaries by normalized project and is repeatable.
- [x] `--feature-effort VALUE` filters feature summaries by normalized effort and is repeatable.
- [x] Missing or blank milestone, target release, and project values match `unassigned`; missing or blank effort matches `unknown`.
- [x] The new filters return code `2` without `--feature-summaries`, and the error lists the new flags.
- [x] `--feature-sort` accepts `milestone`, `target-release`, `project`, and `effort`; invalid sort errors list the expanded key set.
- [x] Metadata sorting is stable and deterministic, uses slug as a tie-breaker, keeps default values last, and supports descending order.
- [x] Existing priority, owner, status, and readiness filters continue to work.
- [x] The implementation does not add dependencies, call GitHub, invoke subprocesses, read tokens, or use network access.
