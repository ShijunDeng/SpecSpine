# Verification Matrix Execution

Feature ID: verification-matrix
Status: validated
Why: Reviewers need one local AC-level packet that connects feature criteria to test evidence and readiness gaps without running commands.

## Milestones

- Define matrix row shape, summary fields, evidence fields, exit behavior, and safety notes.
- Implement the verification matrix builder, JSON renderer, text renderer, and CLI route.
- Update generated templates, AGENTS guidance, project docs, and dogfood checks.
- Add focused unit tests plus repository documentation assertions.

## Tasks

- [x] AC001 Add `verify matrix` parsing and CLI routing under `src/specspine/cli.py`.
- [x] AC002 Add `src/specspine/verification.py` with deterministic JSON and text rendering.
- [x] AC003 Map acceptance criteria to feature test cases and local Test Coverage links.
- [x] AC004 Mark rows verified only when AC evidence is checked and at least one checked local coverage target exists.
- [x] AC005 Preserve unverified rows and explicit gap reasons for missing, unchecked, or missing-target coverage.
- [x] AC006 Preserve stable exit codes for missing feature bundles and invalid feature slugs.
- [x] AC007 Add tests proving the command is local-only and does not execute subprocesses, network calls, GitHub calls, upstream CLIs, environment reads, or token reads.
- [x] AC008 Update README, AGENTS, architecture, product, execution, quality, and generated feature templates.

## Dependencies

- Existing native feature trace report.
- Existing feature acceptance-test packet.
- Existing feature readiness gate with coverage required.
- Existing local review, change risk, security cue, provenance, and validation packets for recommended follow-up commands.
- Python standard library only.

## Open Questions

- Future work can decide whether verification matrices should ingest signed test-run artifacts after real release workflows need proof of execution.
