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

- [x] Parse `Priority:` and `Owner:` from `specs/features/<slug>.md`.
- [x] Normalize priorities to `high`, `medium`, `low`, or `unknown`.
- [x] Normalize missing or blank owners to `unassigned`.
- [x] Add priority and owner fields to feature summary JSON.
- [x] Show priority and owner in text feature summaries.
- [x] Add repeated `--feature-priority` and `--feature-owner` filters behind `--feature-summaries`.
- [x] Add priority sorting and descending priority sort behavior.
- [x] Update generated feature spec templates.
- [x] Update README, architecture docs, product spec, execution plan, and review notes.
- [x] Add focused unit tests for metadata output, filtering, sorting, invalid options, and template content.
- [x] Run the required unit, validation, readiness, diff, and token-prefix checks.

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
