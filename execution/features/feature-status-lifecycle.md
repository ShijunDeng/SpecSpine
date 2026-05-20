# Feature Status Lifecycle Execution

Feature ID: feature-status-lifecycle
Status: validated
Why: Feature bundles need to advance beyond proposal state while staying file-native and agent-readable.

## Milestones

- Define the lifecycle state constants in the native feature module.
- Add reusable status inspection and update functions.
- Add the `feature status` CLI subcommand with text and JSON output.
- Extend workspace status output with feature status and consistency fields.
- Extend feature validation to require allowed statuses and peer consistency.
- Dogfood the behavior with this repository feature bundle.
- Update user docs and project execution artifacts.
- Run the full unit suite and repository validation commands.

## Tasks

- [x] AC001 Implement allowed status validation.
- [x] AC002 Implement status report JSON fields for feature bundles.
- [x] AC003 Implement status updates for existing peer files.
- [x] AC004 Preserve partial bundle behavior and clear all-missing failure.
- [x] AC005 Add CLI tests for query, set, invalid input, and partial bundles.
- [x] AC006 Add validation tests for allowed, invalid, and mixed statuses.
- [x] AC007 Add dogfood artifact coverage for the repository bundle.
- [x] AC007 Update README, architecture docs, execution plan, tasks, and review notes.

## Dependencies

- Python standard library only.
- Existing native feature bundle layout under `specs/features`, `execution/features`, and `quality/features`.
- Existing CLI, status, and validation modules.

## Open Questions

- Whether future releases should enforce transition ordering or keep lifecycle moves intentionally manual.
- Whether external adapter mappings should translate native lifecycle states into upstream-specific states.
