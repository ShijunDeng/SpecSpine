# Feature Test Packet Execution

Feature ID: feature-test-packet
Status: validated
Why: QA and testing agents need a local feature packet focused on acceptance tests, existing test plan evidence, and unresolved gaps.

## Milestones

- Define the test packet schema and AC-to-TC mapping behavior.
- Implement report composition, JSON rendering, text rendering, and CLI output behavior.
- Update repository docs and agent guidance so testing agents can discover the new packet.
- Add focused unit coverage and a complete dogfood bundle.
- Run unit tests, fused feature validation, readiness, packet export, and token-prefix scan.

## Tasks

- [x] AC001 Add test packet report construction and renderers in `src/specspine/features.py`.
- [x] AC002 Register `feature tests` in `src/specspine/cli.py` with JSON, output, force, and exit-code behavior.
- [x] AC003 Generate deterministic pending test cases from acceptance criteria without inferring implementation files or generating code.
- [x] AC004 Update README, architecture, product, execution, quality, current `AGENTS.md`, and the `src/specspine/agents.py` template.
- [x] AC005 Add tests for JSON/text output, output overwrite and force behavior, partial bundles, missing bundles, invalid slugs, offline/token-free behavior, and dogfood readiness.
- [x] AC006 Add the `feature-test-packet` dogfood peer files with complete local quality evidence.
- [x] AC007 Implement `--output` that writes the text packet, refuses overwrite by default, honors `--force`, and keeps stdout JSON with `--json`.
- [x] AC008 Handle partial bundles returning 0 with missing files and gaps, missing bundles returning non-zero, and invalid slugs returning 2.
- [x] AC009 Update documentation, agent guidance, tests, and dogfood artifacts for the testing packet workflow.

## Dependencies

- Existing native feature path and lifecycle helpers.
- Existing feature handoff, trace, readiness, status, and source-file evidence.
- Python standard library only.

## Open Questions

- Future work can add explicit user-authored links to existing test files if SpecSpine gains native metadata for that relationship.
