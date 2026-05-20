# Feature Transition Policy Execution

Feature ID: feature-transition-policy
Status: validated
Why: Agents need opt-in lifecycle ordering and archive readiness checks while keeping default manual status updates compatible.

## Milestones

- Define the conservative transition graph and archive readiness guard.
- Add transition validation helpers and stable failure payloads in the feature status implementation.
- Register the CLI flag and preserve existing exit-code behavior for invalid slugs and statuses.
- Cover default, allowed, rejected, terminal, mixed, archive-ready, archive-blocked, JSON, agent-template, and dogfood paths with tests.
- Update user documentation, architecture notes, project specs, task plans, review notes, and agent instructions.

## Tasks

- [x] AC001 Add transition rule data and write-before validation in `src/specspine/features.py`.
- [x] AC002 Add `--enforce-transition` parsing and error rendering in `src/specspine/cli.py`.
- [x] AC003 Reuse `build_feature_ready_report` as the enforced archive guard.
- [x] AC004 Add unit tests for default compatibility and enforced transition behavior.
- [x] AC005 Update `README.md`, `docs/architecture.md`, `specs/product.md`, execution notes, quality notes, `AGENTS.md`, and the agent template.
- [x] AC006 Add this validated dogfood feature bundle and verify it passes `feature ready`.
- [x] AC007 Update documentation and agent instructions describing the policy as opt-in.

## Dependencies

- Existing native feature status parsing and file update helpers.
- Existing feature readiness report and stable JSON rendering.
- Python standard library only.

## Open Questions

- Future rounds can decide whether teams need a configuration file to make enforcement the workspace default.
