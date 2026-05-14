# Adapter Handoff Artifacts Execution

Feature ID: adapter-handoff-artifacts
Status: validated
Why: SpecSpine should materialize adapter handoff context into local review artifacts for separate agents without executing any upstream tooling.

## Milestones

- Define the artifact directory contract and manifest shape.
- Add adapter-focused Markdown rendering from the existing adapter handoff report.
- Wire `--output-dir` into `specspine adapters handoff` while preserving `--output` and JSON stdout behavior.
- Add overwrite protection that only manages known artifact files.
- Add focused tests for files, manifest, force behavior, compatibility, error codes, and safety boundaries.
- Update documentation, agent instructions, and this dogfood bundle.

## Tasks

- [x] Add artifact dataclasses and overwrite error for adapter handoff exports.
- [x] Add manifest generation with artifact paths, feature evidence, summary, gaps, blockers, and safety flags.
- [x] Add focused Markdown output for `openspec`, `speckit`, and `superpowers`.
- [x] Write `manifest.json`, `combined.md`, and `adapters/*.md` from the existing report object only.
- [x] Add CLI `--output-dir` and keep `--json` stdout parseable.
- [x] Allow `--output` and `--output-dir` to work together.
- [x] Refuse overwrite of managed files unless `--force` is supplied.
- [x] Preserve unknown files in artifact directories.
- [x] Add tests for artifact content, manifest shape, overwrite behavior, JSON stdout, output compatibility, unchanged error behavior, and offline boundaries.
- [x] Update README, upstream docs, architecture docs, product and architecture specs, execution docs, quality review, and AGENTS guidance.
- [x] Verify dogfood readiness with default and coverage-required gates.

## Dependencies

- Existing `build_adapter_feature_handoff_report` report data.
- Existing combined adapter handoff Markdown renderer.
- Existing feature readiness and validation checks.

## Resolved Decisions

- Per-adapter structured JSON files are implemented by `adapter-handoff-structured-artifacts`.
- Artifact manifests now include SHA-256 content hashes for non-manifest managed artifacts.

## Agent Handoff

- Run `specspine adapters handoff adapter-handoff-artifacts . --json`.
- Run `specspine adapters handoff adapter-handoff-artifacts . --output-dir .specspine/adapter-handoff-artifacts-test --force --json`.
- Run `specspine feature ready adapter-handoff-artifacts . --json`.
- Run `specspine feature ready adapter-handoff-artifacts . --json --require-coverage`.
- Run `specspine validate . --fusion --features`.
