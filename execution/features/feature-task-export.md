# Feature Task Export Execution

Feature ID: feature-task-export
Status: validated
Why: Agents need a stable task list extracted from native feature execution files.

## Milestones

- Define the task export report shape in the native feature module.
- Parse Markdown checklist items from execution feature files with line numbers.
- Add the `feature tasks` CLI subcommand and file output behavior.
- Cover parser, CLI, partial bundle, missing bundle, output, and token-free behavior with tests.
- Dogfood the command with this repository feature bundle.
- Update documentation and project-level execution and quality artifacts.
- Run the unit suite, task export command, status validation, feature validation, and token-prefix scan.

## Tasks

- [x] AC001 Add a task report model with stable JSON serialization.
- [x] AC002 Parse `- [ ]`, `- [x]`, `* [ ]`, and `* [x]` items from `## Tasks`.
- [x] AC003 Preserve source file and source line for every exported task.
- [x] AC004 Render concise text output that an implementation agent can follow.
- [x] AC005 Implement `--output`, overwrite protection, `--force`, and `--json --output`.
- [x] AC006 Return empty task lists for no checklist items and partial bundles with missing execution files.
- [x] AC007 Return non-zero when no native feature files exist for the slug.
- [x] AC007 Add tests for parser details, CLI outputs, missing files, output files, and token-free behavior.
- [x] AC007 Update README, architecture docs, agent guidance, execution plan, tasks, and review notes.

## Dependencies

- Python standard library only.
- Existing native feature bundle layout under `specs/features`, `execution/features`, and `quality/features`.
- Existing feature status and issue export patterns.

## Open Questions

- Whether future status JSON should include task summaries after task export proves stable.
- Whether future versions should support nested checklist hierarchy while keeping flat agent task ids.
