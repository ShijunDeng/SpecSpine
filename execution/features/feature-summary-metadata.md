# Feature Summary Metadata Execution

Feature ID: feature-summary-metadata
Status: validated
Why: Feature summary triage needs explicit local priority and owner fields before remote issue or project synchronization exists.

## Milestones

- Add metadata parsing for spec-level priority and owner.
- Extend status summary JSON and text output.
- Add CLI filters and priority sorting.
- Refresh generated feature templates and user-facing documentation.
- Add tests and dogfood this feature bundle.

## Tasks

- [x] AC001 Parse `Priority:` and `Owner:` from `specs/features/<slug>.md`.
- [x] AC002 Normalize priorities to `high`, `medium`, `low`, or `unknown`.
- [x] AC003 Normalize missing or blank owners to `unassigned`.
- [x] AC004 Add priority and owner fields to feature summary JSON.
- [x] AC005 Show priority and owner in text feature summaries.
- [x] AC006 Add repeated `--feature-priority` and `--feature-owner` filters behind `--feature-summaries`.
- [x] AC007 Add priority sorting and descending priority sort behavior.
- [x] AC008 Update generated feature spec templates.
- [x] AC009 Update README, architecture docs, product spec, execution plan, and review notes.
- [x] AC010 Add focused unit tests for metadata output, filtering, sorting, invalid options, and template content.
- [x] AC010 Run the required unit, validation, readiness, diff, and token-prefix checks.

## Dependencies

- Existing native feature bundle discovery.
- Existing status feature summaries and filter/sort plumbing.
- Existing feature handoff and readiness reports.

## Open Questions

- Whether later remote sync should map priority and owner into GitHub Issue Fields, labels, assignees, or project fields.
- Whether future metadata should include milestone, target release, or implementation-file hints.

## Agent Handoff

- Run `specspine status . --json --validate --feature-summaries --feature-priority high --feature-sort priority`.
- Run `specspine feature handoff feature-summary-metadata . --json`.
- Run `specspine feature tests feature-summary-metadata . --json`.
- Run `specspine feature ready feature-summary-metadata . --json`.
- Run `specspine validate . --fusion --features`.
