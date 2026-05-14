# Feature Summary Filters

Feature ID: feature-summary-filters
Status: validated

## Why

Maintainers and agents now compare several native feature bundles in one workspace. The optional feature summary view needs local filters and deterministic sorting so a user can find ready work, blocked work, or lifecycle-specific work without opening every feature handoff packet.

## Users

- Implementation agents choosing the next feature to work on.
- Review agents looking for validated or ready feature bundles.
- Maintainers triaging multi-feature dogfood workspaces.

## Scope

- Add `--feature-status STATUS` to `specspine status [path] --feature-summaries`, repeatable for lifecycle filters.
- Add `--feature-ready READY` with `yes`, `no`, `true`, `false`, `ready`, and `not-ready` aliases.
- Add `--feature-sort KEY` for `slug`, `status`, `ready`, `gaps`, `blocking`, and `tasks-open`.
- Add `--feature-sort-desc` for descending summary order.
- Apply filters and sorting to both JSON `feature_summaries` and the text Feature summaries section.
- Return code `2` with a clear error when summary filter or sort options are used without `--feature-summaries`, or when unsupported values are passed.
- Keep default `specspine status --json` compact and keep unfiltered `--feature-summaries` behavior compatible.

## Non-Goals

- Calling GitHub, upstream CLIs, network services, or token-backed APIs.
- Adding new dependencies or remote data sources.
- Replacing focused `feature handoff`, `feature trace`, `feature tasks`, `feature tests`, or `feature ready` packets.
- Inferring priorities beyond local status, readiness, counts, and existing next actions.

## Acceptance Criteria

- [x] Default `status --json` still omits `feature_summaries`.
- [x] Unfiltered `status --feature-summaries` preserves the existing summary shape and order.
- [x] `--feature-status` supports single and repeated lifecycle filters, plus abnormal `invalid` and `unknown` filters.
- [x] `--feature-ready` accepts all requested ready and not-ready aliases.
- [x] `--feature-sort` supports `slug`, `status`, `ready`, `gaps`, `blocking`, and `tasks-open`; `--feature-sort-desc` reverses the selected order.
- [x] JSON and text outputs show no matching summaries as an empty list or a clear `none` section.
- [x] Summary filter and sort options without `--feature-summaries` return code `2`.
- [x] Unsupported status, readiness, or sort values return code `2`.
- [x] The implementation is local, deterministic, zero-dependency, and does not read tokens.
