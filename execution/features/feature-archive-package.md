# Feature archive package Execution

Feature ID: feature-archive-package
Status: validated

## Milestones

- [x] Define archive report payload and local package contents.
- [x] Add the native feature CLI command.
- [x] Add focused unit tests and dogfood evidence.
- [x] Update user-facing guidance.

## Tasks

- [x] AC001 T001: Add a reusable archive report module that composes existing status, ready, trace, tasks, tests, metadata, sources, and missing-file evidence.
- [x] AC002 T002: Wire `specspine feature archive <slug> [path] [--json] [--output-dir DIR] [--archive-id ID] [--force]`.
- [x] AC003 T003: Implement archive package writing with `README.md`, `archive.json`, and source snapshots under an explicit output directory.
- [x] AC004 T004: Add conflict protection and `--force` overwrite behavior for command-owned package files.
- [x] AC005 T005: Add tests for JSON, text, explicit archive ids, output packages, conflicts, invalid and missing features, and read-only local behavior.
- [x] AC006 T006: Update README, agent guidance, architecture/product docs, execution plan, quality review, and dogfood feature artifacts.

## Dependencies

- Existing native feature status, ready, trace, tasks, and tests reports.
- Existing local Test Coverage metadata.

## Open Questions

- [x] Should archive packaging mark lifecycle status itself? No; it recommends the existing enforced lifecycle command after evidence review.

## Agent Handoff

- Run `specspine feature archive feature-archive-package . --json --archive-id 2026-05-18-feature-archive-package`.
- Run `specspine feature ready feature-archive-package . --json --require-coverage`.
- Run `specspine validate . --fusion --features --json`.
