# Extended Feature Metadata Execution

Feature ID: extended-feature-metadata
Status: validated
Why: Local feature bundles need richer machine-consumable triage metadata before any remote issue or PR synchronization is reviewed.

## Milestones

- Extend the shared metadata value object and parser.
- Refresh generated feature templates.
- Thread metadata through status, issue, PR, handoff, tests, and sync-plan reports.
- Materialize metadata into sync-plan manifest and Markdown body artifacts.
- Update documentation and dogfood coverage.

## Tasks

- [x] AC001 Add `milestone`, `target_release`, `project`, and `effort` fields to `FeatureMetadata`.
- [x] AC002 Normalize missing assignment-style fields to `unassigned` and missing effort to `unknown`.
- [x] AC003 Generate extended metadata defaults in new feature specs.
- [x] AC004 Add extended metadata to feature summary JSON and concise text rows.
- [x] AC005 Add metadata sections to issue, task issue, PR, and sync-plan Markdown bodies.
- [x] AC006 Include metadata in handoff and test packet JSON.
- [x] AC007 Include metadata in sync-plan artifact manifests.
- [x] AC008 Add unit tests for defaults, old-file compatibility, full parsing, status summaries, drafts, artifacts, dogfood, and no remote behavior.
- [x] AC009 Update README, product, architecture, execution, quality, and agent guidance.

## Dependencies

- Existing feature metadata parser.
- Existing feature summary builder.
- Existing issue, PR, handoff, tests, and sync-plan report builders.
- Existing readiness and coverage gates.

## Open Questions

- Whether future GitHub integrations should map these local fields to typed Issue Fields after an explicit authenticated sync workflow exists.

## Agent Handoff

- Run `specspine status . --json --feature-summaries --feature-sort priority`.
- Run `specspine feature handoff extended-feature-metadata . --json`.
- Run `specspine feature tests extended-feature-metadata . --json`.
- Run `specspine feature sync-plan extended-feature-metadata . --json`.
- Run `specspine feature ready extended-feature-metadata . --json --require-coverage`.
- Run `specspine feature ready extended-feature-metadata . --json --policy`.
- Run `specspine validate . --fusion --features`.
