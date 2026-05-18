# Feature archive package

Feature ID: feature-archive-package
Priority: high
Owner: Platform Team
Milestone: 2026.5
Target Release: 2026.5
Project: Native feature bundles
Effort: M
Status: validated

## Why

SpecSpine can enforce archive readiness through lifecycle status updates, but maintainers also need a local closure packet that preserves the durable evidence for why and how a feature was finished before the status is moved to `archived`.

## Users

- Maintainers who close native feature bundles.
- Review agents that need stable local evidence before accepting archive transitions.
- Future auditors who need to inspect status, trace, tasks, tests, and source snapshots without calling remote services.

## Scope

- Add `specspine feature archive <slug> [path]` as a local report command.
- Add `--json`, `--output-dir DIR`, `--archive-id ID`, and `--force`.
- Compose existing feature status, metadata, ready, trace, task, and test evidence.
- Write package artifacts only under an explicit output directory.

## Non-Goals

- Marking features archived automatically.
- Running tests or subprocesses.
- Calling network services, GitHub APIs, token providers, or upstream CLIs.
- Adding server or remote protocol surfaces.

## Acceptance Criteria

- [x] AC001: Report-only archive analysis returns stable JSON with archive id, feature status, metadata, readiness, trace, task, test, source, missing-file, safety-note, and recommended-command evidence.
- [x] AC002: Text output summarizes the archive package plan and includes the enforced lifecycle command to mark a ready feature archived.
- [x] AC003: `--output-dir` writes `README.md`, `archive.json`, and source snapshots under clear package paths, with deterministic content when `--archive-id` is provided.
- [x] AC004: Existing package files are not overwritten unless `--force` is passed.
- [x] AC005: Invalid slugs return `2`, missing features return `1`, and report-only not-ready bundles still return `0` when local evidence exists.
- [x] AC006: The archive command remains local and read-only unless `--output-dir` is explicitly provided.

## Edge Cases

- Partial bundles should report missing files and readiness blockers without blocking report construction.
- Workspaces with `## Test Coverage` evidence should use coverage-aware readiness in the archive report.
- Existing unknown files in an output directory should be left untouched unless they collide with command-owned paths.

## Constraints

- Reuse existing local feature reports instead of inventing a parallel feature model.
- Keep output deterministic for tests when `--archive-id` is provided.
- Do not create server files or remote command surfaces.

## Traceability Notes

- Covered by `tests/test_archive.py`.
