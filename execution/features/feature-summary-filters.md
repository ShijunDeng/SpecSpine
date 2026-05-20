# Feature Summary Filters Execution

Feature ID: feature-summary-filters
Status: validated
Why: Multi-feature workspaces need a fast local way to narrow and order optional feature summaries.

## Milestones

- Extend the status summary builder with focused filter and sort helpers.
- Wire the new CLI arguments into `specspine status`.
- Add tests for compatibility, filters, sorting, no-match output, and invalid argument handling.
- Update repository documentation and agent guidance.
- Add this dogfood bundle and verify readiness.

## Tasks

- [x] AC001 Add supported status, readiness, and sort key parsing with code `2` failures for unsupported values.
- [x] AC002 Gate all summary filter and sort options behind `--feature-summaries`.
- [x] AC003 Filter JSON and text summaries by lifecycle status and readiness.
- [x] AC004 Sort summaries by slug, status, readiness, gap count, blocking count, and open task count.
- [x] AC005 Preserve default compact `status --json` output.
- [x] AC006 Preserve unfiltered feature summary JSON shape.
- [x] AC007 Add unit tests for single and repeated status filters.
- [x] AC008 Add unit tests for ready and not-ready aliases.
- [x] AC009 Add unit tests for supported sort keys and descending order.
- [x] AC009 Add unit tests for no-match text and JSON output.
- [x] AC009 Add unit tests for missing `--feature-summaries` and invalid option values.
- [x] AC009 Update README, architecture docs, specs, execution plan, quality review, AGENTS.md, and the generated agent template.
- [x] AC009 Run the required unit, validation, status, readiness, and token-prefix checks.

## Dependencies

- Existing local native feature bundle discovery.
- Existing status feature summary construction.
- Existing feature handoff and readiness reports.

## Open Questions

- Whether future multi-feature triage needs additional local sort keys, such as oldest modified file or explicit user-owned priority metadata.
