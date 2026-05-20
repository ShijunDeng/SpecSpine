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

- [x] AC001 Add repeatable metadata filter CLI options behind `--feature-summaries`.
- [x] AC002 Normalize metadata filter values using the same default buckets as summaries.
- [x] AC003 Thread metadata filter tuples through status construction.
- [x] AC004 Add metadata sort keys with deterministic slug tie-breaks.
- [x] AC005 Keep `unassigned` and `unknown` default values last for metadata sorts.
- [x] AC006 Update invalid sort and summary-only option errors.
- [x] AC007 Add tests for single and repeated filters, default normalization, sort and descending order, invalid options, old filters, dogfood, and no unsafe behavior.
- [x] AC008 Update README, product, architecture, execution, quality, and AGENTS guidance.
- [x] AC009 Verify existing priority, owner, status, and readiness filters continue to work alongside new metadata filters.
- [x] AC010 Confirm zero dependencies, no GitHub calls, no subprocesses, no token reads, and no network access.

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
