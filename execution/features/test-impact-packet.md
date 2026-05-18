# Test impact packet Execution

Feature ID: test-impact-packet
Status: validated

## Milestones

- [x] Define the static source-to-test impact schema.
- [x] Add CLI integration for `specspine tests impact`.
- [x] Add focused unit coverage for changed paths, feature coverage, fallbacks, and safety.
- [x] Update docs, agent guidance, and dogfood artifacts.

## Tasks

- [x] T001: Build a local impact module that inventories `src/specspine/*.py` and `tests/test_*.py`.
- [x] T002: Parse test imports with `ast` and add conservative deterministic text matches.
- [x] T003: Recommend unittest commands for changed source files, changed test files, and unmapped fallback cases.
- [x] T004: Include feature Test Coverage targets when `--feature` is provided.
- [x] T005: Wire the CLI, JSON renderer, text renderer, and exit-code behavior.
- [x] T006: Add focused tests and update documentation.

## Dependencies

- Existing feature test packet parsing for local Test Coverage links.
- Existing native feature slug validation and missing-bundle behavior.

## Open Questions

- [x] Should the command execute recommended tests? No; it reports commands only.

## Agent Handoff

- Run `specspine tests impact . --json`.
- Run `specspine tests impact . --changed src/specspine/impact.py --json`.
- Run `specspine tests impact . --feature test-impact-packet --json`.
- Run `specspine feature ready test-impact-packet . --json --require-coverage`.
- Run `specspine validate . --fusion --features`.
