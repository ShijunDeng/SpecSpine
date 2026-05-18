# Change Risk Packet Execution

Feature ID: change-risk-packet
Status: validated
Why: Reviewers need changed-path risk evidence before deciding whether focused test, readiness, and review packets cover a local change.

## Milestones

- Define changed-path categories, advisory risk levels, and summary fields.
- Implement the local report builder, JSON renderer, text renderer, and CLI command.
- Update generated templates and project guidance so change risk becomes visible before review packets.
- Add focused unit tests and dogfood evidence.

## Tasks

- [x] AC001 Add `change risk` parsing and CLI routing under `src/specspine/cli.py`.
- [x] AC002 Add `src/specspine/change.py` with deterministic JSON and text packet rendering.
- [x] AC003 Classify source, test, feature peer, project docs, config, and other paths with stable advisory risk levels.
- [x] AC004 Infer feature ids from native peer paths and dedupe them with explicit `--feature` input.
- [x] AC005 Compose coverage-required feature readiness evidence for inferred and provided feature ids.
- [x] AC006 Preserve stable exit codes for missing feature bundles and invalid feature slugs.
- [x] AC007 Add tests proving the command is local-only and does not execute subprocesses, network calls, GitHub calls, upstream CLIs, or token reads.
- [x] AC008 Update README, AGENTS, architecture, product, execution, quality, and generated feature templates.

## Dependencies

- Existing native feature handoff report.
- Existing feature readiness gate with coverage required.
- Existing review packet and test impact commands for recommended follow-up.
- Python standard library only.

## Open Questions

- Future work can decide whether a separate opt-in flag should infer changed files from git status.
