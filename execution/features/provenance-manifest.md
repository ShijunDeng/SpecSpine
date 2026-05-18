# Provenance Manifest Execution

Feature ID: provenance-manifest
Status: validated
Why: Reviewers need a local audit manifest that ties feature evidence files to exact hashes without remote calls or command execution.

## Milestones

- Define local artifact kinds, hash behavior, feature evidence fields, and safety notes.
- Implement the provenance manifest builder, JSON renderer, text renderer, and CLI route.
- Update generated templates, AGENTS guidance, project docs, and dogfood checks.
- Add focused unit tests plus repository documentation assertions.

## Tasks

- [x] AC001 Add `provenance manifest` parsing and CLI routing under `src/specspine/cli.py`.
- [x] AC002 Add `src/specspine/provenance.py` with deterministic JSON and text rendering.
- [x] AC003 Hash existing local files with SHA-256 and byte counts without outputting contents.
- [x] AC004 Report missing, directory, and outside-root artifacts without crashing.
- [x] AC005 Compose native feature peer artifacts and coverage-required readiness evidence.
- [x] AC006 Preserve stable exit codes for missing feature bundles and invalid feature slugs.
- [x] AC007 Add tests proving the command is local-only and does not execute subprocesses, network calls, GitHub calls, upstream CLIs, environment reads, or token reads.
- [x] AC008 Update README, AGENTS, architecture, product, execution, quality, and generated feature templates.

## Dependencies

- Existing native feature handoff report.
- Existing feature readiness gate with coverage required.
- Existing local review, change risk, security cue, trace, and tests packets for recommended follow-up commands.
- Python standard library only.

## Open Questions

- Future work can decide whether provenance manifests should support writing a signed artifact bundle after real maintainer workflows need tamper-evident packages.
