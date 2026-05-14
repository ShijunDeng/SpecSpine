# Feature Metadata Filters Execution

Feature ID: feature-metadata-filters
Status: validated
Why: Structured local feature metadata needs to drive deterministic summary triage for agents choosing the next item of work.

## Milestones

- Extend status filter parsing for milestone, target release, project, and effort.
- Extend status sort keys for the same metadata fields.
- Preserve default summary output and existing filters.
- Add focused tests and dogfood coverage.
- Refresh docs and agent guidance.

## Tasks

- [x] Add repeatable metadata filter CLI options behind `--feature-summaries`.
- [x] Normalize metadata filter values using the same default buckets as summaries.
- [x] Thread metadata filter tuples through status construction.
- [x] Add metadata sort keys with deterministic slug tie-breaks.
- [x] Keep `unassigned` and `unknown` default values last for metadata sorts.
- [x] Update invalid sort and summary-only option errors.
- [x] Add tests for single and repeated filters, default normalization, sort and descending order, invalid options, old filters, dogfood, and no unsafe behavior.
- [x] Update README, product, architecture, execution, quality, and AGENTS guidance.

## Dependencies

- Existing feature metadata parser and `FeatureMetadata` defaults.
- Existing `status --feature-summaries` summary builder.
- Existing local readiness, coverage, and policy gates.

## Open Questions

- Whether a later explicit authenticated sync should map these fields into GitHub Issue Fields or Projects.
- Whether future effort values should be constrained beyond deterministic ordering of common sizes.

## Agent Handoff

- Run `specspine status . --json --feature-summaries --feature-project "Native feature bundles" --feature-sort effort`.
- Run `specspine feature handoff feature-metadata-filters . --json`.
- Run `specspine feature tests feature-metadata-filters . --json`.
- Run `specspine feature ready feature-metadata-filters . --json --require-coverage`.
- Run `specspine feature ready feature-metadata-filters . --json --policy`.
- Run `specspine validate . --fusion --features`.
