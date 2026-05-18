# Feature archive package Quality

Feature ID: feature-archive-package
Status: validated

## Required Checks

- [x] Archive JSON exposes stable status, metadata, ready, trace, task, test, source, missing-file, safety, and recommended-command fields.
- [x] Archive text output includes a compact closure summary and lifecycle archive command.
- [x] Archive output packages write only under `--output-dir` and protect existing command-owned files unless `--force` is passed.
- [x] Invalid slug, missing feature, explicit archive id, and read-only behavior are covered by focused tests.
- [x] The implementation avoids subprocess, network, token, GitHub, and upstream CLI calls.

## Test Coverage

- [x] AC001 -> tests/test_archive.py
- [x] AC002 -> tests/test_archive.py
- [x] AC003 -> tests/test_archive.py
- [x] AC004 -> tests/test_archive.py
- [x] AC005 -> tests/test_archive.py
- [x] AC006 -> tests/test_archive.py

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_archive`.
- Run `PYTHONPATH=src python3 -m specspine feature archive feature-archive-package . --json --archive-id 2026-05-18-feature-archive-package`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-archive-package . --json --require-coverage`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.

## Review Notes

- The archive package composes existing local reports and source snapshots; it does not create a second lifecycle model.
- Report-only mode stays read-only and returns success for not-ready bundles so reviewers can inspect blockers without writing files.
- Lifecycle closure remains explicit through `specspine feature status feature-archive-package . --set archived --enforce-transition --json`.

## Release Readiness

- [x] Acceptance criteria, tasks, required checks, and test coverage are complete.
- [x] Documentation and agent guidance are updated.
- [x] `PYTHONPATH=src python3 -m unittest tests.test_archive` passes.
- [x] No known blockers remain.
