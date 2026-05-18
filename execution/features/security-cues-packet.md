# Security Cues Packet Execution

Feature ID: security-cues-packet
Status: validated
Why: Reviewers need a local security cue packet that highlights sensitive changed-path text before review without running scanners or external tools.

## Milestones

- Define security cue categories, severity levels, safe file-read behavior, and summary fields.
- Implement the local report builder, JSON renderer, text renderer, and CLI command.
- Update generated templates and project guidance so security cues become visible before review packets.
- Add focused unit tests and dogfood evidence.

## Tasks

- [x] AC001 Add `security cues` parsing and CLI routing under `src/specspine/cli.py`.
- [x] AC002 Add `src/specspine/security.py` with deterministic JSON and text packet rendering.
- [x] AC003 Implement bounded local text reads with missing, binary, too-large, and outside-root reporting.
- [x] AC004 Detect security-sensitive keyword cues without printing source lines or secret values.
- [x] AC005 Infer feature ids from native peer paths and dedupe them with explicit `--feature` input.
- [x] AC006 Compose coverage-required feature readiness evidence for inferred and provided feature ids.
- [x] AC007 Preserve stable exit codes for missing feature bundles and invalid feature slugs.
- [x] AC008 Add tests proving the command is local-only and does not execute subprocesses, network calls, GitHub calls, upstream CLIs, environment reads, or token reads.
- [x] AC009 Update README, AGENTS, architecture, product, execution, quality, and generated feature templates.

## Dependencies

- Existing native feature handoff report.
- Existing feature readiness gate with coverage required.
- Existing change risk, test impact, and review packet commands for recommended follow-up.
- Python standard library only.

## Open Questions

- Future work can decide whether cue keywords should become configurable after real false-positive patterns are observed.
