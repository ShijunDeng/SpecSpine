# Review Packet Execution

Feature ID: review-packet
Status: validated
Why: Reviewers need one local packet that composes validation, quality gates, test impact, feature evidence, and safety notes before merge without executing commands.

## Milestones

- Define the review packet schema, review checks, summary fields, and safety notes.
- Implement the local report builder, JSON renderer, text renderer, and CLI command.
- Update generated templates and project guidance so review packets become a visible pre-merge step.
- Add focused unit tests and dogfood evidence.

## Tasks

- [x] AC001 Add `review packet` parsing and CLI routing under `src/specspine/cli.py`.
- [x] AC002 Add `src/specspine/review.py` with deterministic JSON and text packet rendering.
- [x] AC003 Compose feature handoff, coverage-required readiness, trace, tests, gaps, blockers, and source files when `--feature` is provided.
- [x] AC004 Forward repeated `--changed PATH` values to the static test impact report.
- [x] AC005 Preserve stable exit codes for missing feature bundles and invalid feature slugs.
- [x] AC006 Add tests proving the command is local-only and does not execute subprocesses, network calls, GitHub calls, upstream CLIs, or token reads.
- [x] AC007 Update README, AGENTS, architecture, product, execution, quality, and generated feature templates.

## Dependencies

- Existing validation report and compact validation summary.
- Existing quality gate definition exporter.
- Existing static test impact report.
- Existing native feature handoff, readiness, trace, and tests reports.
- Python standard library only.

## Open Questions

- Future work can decide whether review packets should support policy-selected review profiles or remain a direct composition of existing local reports.
