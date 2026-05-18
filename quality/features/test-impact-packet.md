# Test impact packet Quality

Feature ID: test-impact-packet
Status: validated

## Required Checks

- [x] Impact JSON exposes source modules, test files, recommendations, summary, commands, and safety notes.
- [x] Changed source and changed test recommendations are deterministic.
- [x] Fallback recommendations are explicit when direct static impact is unavailable.
- [x] Feature coverage targets are included without running tests.
- [x] The implementation avoids subprocess, network, token, GitHub, and upstream CLI calls.

## Test Coverage

- [x] AC001 -> tests/test_impact.py
- [x] AC002 -> tests/test_impact.py
- [x] AC003 -> tests/test_impact.py
- [x] AC004 -> tests/test_impact.py
- [x] AC005 -> tests/test_impact.py
- [x] AC006 -> tests/test_impact.py

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_impact`.
- Run `PYTHONPATH=src python3 -m specspine tests impact . --json`.
- Run `PYTHONPATH=src python3 -m specspine tests impact . --changed src/specspine/impact.py --json`.
- Run `PYTHONPATH=src python3 -m specspine tests impact . --feature test-impact-packet --json`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features --json`.

## Review Notes

- The impact packet is advisory: recommended commands are not executed by SpecSpine.
- Static analysis is intentionally conservative and falls back to full discovery when direct impact is unknown.

## Release Readiness

- [x] Acceptance criteria, tasks, required checks, and test coverage are complete.
- [x] Documentation and agent guidance are updated.
- [x] `PYTHONPATH=src python3 -m unittest tests.test_impact` passes.
- [x] No known blockers remain.
