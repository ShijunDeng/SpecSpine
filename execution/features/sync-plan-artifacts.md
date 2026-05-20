# Materialize Sync Plan Artifacts Execution

Feature ID: sync-plan-artifacts
Status: validated
Why: Let maintainers review GitHub CLI body files and manifest locally before any remote sync.

## Milestones

- [x] Define the artifact directory contract and overwrite semantics.
- [x] Implement artifact manifest, body file, and commands script writing.
- [x] Add CLI `--output-dir` handling alongside existing `--output` and `--json` behavior.
- [x] Update tests, docs, and dogfood bundle.

## Tasks

- [x] AC001 Add sync-plan artifact dataclasses, manifest builder, command script renderer, and writer in `src/specspine/features.py`.
- [x] AC002 Register `--output-dir DIR` in `src/specspine/cli.py`.
- [x] AC003 Preflight command-owned output files and require `--force` before overwriting them.
- [x] AC004 Write body files for feature issues, task issues, and draft Pull Requests using stable relative paths.
- [x] AC005 Write `commands.sh` with review-only comments and shell-quoted `gh` commands using local `--body-file` paths.
- [x] AC006 Keep JSON stdout unchanged while allowing artifact directory writes.
- [x] AC007 Add focused tests for artifact content, overwrite behavior, command safety, and external-call isolation.
- [x] AC008 Update README, docs, specs, execution, review, and agent guidance.

## Dependencies

- [x] Existing sync-plan command records, draft bodies, labels, and safety flags.
- [x] Python standard library `json`, `pathlib`, and `shlex`.

## Open Questions

- [x] Remote execution remains out of scope until a future explicitly confirmed sync workflow is specified.
- [x] Artifact directories intentionally preserve unknown files; cleanup remains manual.

## Agent Handoff

- Run `specspine feature sync-plan sync-plan-artifacts . --json --output-dir .specspine/sync-plan/sync-plan-artifacts`.
- Run `specspine feature ready sync-plan-artifacts . --json` to confirm the dogfood bundle is ready.
- Run `specspine validate . --fusion --features` before handoff.
