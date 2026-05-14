# Feature Handoff Packet Execution

Feature ID: feature-handoff-packet
Status: validated
Why: Agents need one local feature packet that combines status, tasks, trace, readiness, release evidence, and deterministic next actions.

## Milestones

- Define the handoff report schema and next-action ordering.
- Implement report composition, JSON rendering, text rendering, and CLI output behavior.
- Update agent templates and repository guidance to make handoff the default feature packet.
- Add dogfood artifacts and focused unit coverage for ready, partial, missing, output, and template behavior.

## Tasks

- [x] Add handoff report construction and renderers in `src/specspine/features.py`.
- [x] Register `feature handoff` in `src/specspine/cli.py` with JSON, output, force, and exit-code behavior.
- [x] Generate deterministic next actions from native files, trace gaps, open tasks, blocking checks, and readiness state.
- [x] Update README, architecture, product, execution, quality, current `AGENTS.md`, and the `src/specspine/agents.py` template.
- [x] Add tests for JSON/text, partial bundles, missing bundles, output overwrite and force behavior, JSON plus output, next actions, agent template guidance, and dogfood readiness.
- [x] Run unit tests, fused feature validation, handoff JSON, readiness JSON, and token-prefix scan.

## Dependencies

- Existing native feature path and lifecycle status helpers.
- Existing task, trace, readiness, and release readiness parsers.
- Python standard library only.

## Open Questions

- Future rounds can decide whether handoff should include deterministic cross-reference coverage once explicit relationship metadata exists.
