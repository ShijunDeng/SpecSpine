# Agent Loop Packet Execution

Feature ID: agent-loop-packet
Status: validated
Why: Agents need one local workspace loop packet that combines status, readiness, lifecycle guidance, subagent boundaries, validation commands, safety notes, and upstream metadata.

## Milestones

- Define the loop packet schema and static local safety flags.
- Implement report construction, JSON rendering, text rendering, and CLI output behavior.
- Update repository guidance so agent loops can start from `specspine loop packet`.
- Add dogfood artifacts and focused unit coverage for builder and CLI behavior.

## Tasks

- [x] AC001 Add `src/specspine/loop.py` with a deterministic local packet builder and renderers.
- [x] AC002 Reuse status feature summaries, readiness summary, recommendations, and upstream metadata without adapter probing.
- [x] AC003 Register `loop packet` in `src/specspine/cli.py` with JSON, output, force, and deadline options.
- [x] AC004 Ensure `--json --output` prints JSON to stdout while writing the text packet.
- [x] AC005 Add tests proving output behavior, stable packet shape, token-free output, subprocess-free behavior, and no adapter probing.
- [x] AC006 Update README, architecture, product, review, and agent guidance.
- [x] AC007 Run focused unit tests and local feature validation.
- [x] AC008 Update documentation, agent guidance, dogfood artifacts, and focused tests for the loop packet workflow.

## Dependencies

- Existing workspace status builder.
- Existing feature summary and readiness summary support.
- Existing native feature dogfood validation.
- Python standard library only.

## Open Questions

- Future work can decide whether loop packets should support optional policy-selected coverage readiness or feature filters.
