# Adapter Handoff Structured Artifacts Execution

Feature ID: adapter-handoff-structured-artifacts
Status: validated
Why: Adapter handoff directories should be directly consumable by agents and local review scripts without Markdown parsing or unchecked artifact drift.

## Milestones

- Extend the adapter handoff artifact contract with structured JSON paths.
- Render full and focused JSON payloads from the existing handoff report only.
- Compute SHA-256 checksums over non-manifest managed artifact bytes.
- Add overwrite protection for the new JSON files.
- Add JSON stdout artifact metadata for output-dir exports.
- Update tests, dogfood artifacts, README, AGENTS, product, architecture, execution, and quality docs.

## Tasks

- [x] Add a focused per-adapter JSON payload renderer with feature evidence, safety flags, summary, recommended commands, and the adapter entry.
- [x] Write `combined.json` and `adapters/*.json` alongside the existing Markdown artifacts.
- [x] Add `combined_json`, `adapter_json`, `checksum_algorithm`, and `artifact_checksums` to the manifest while keeping existing manifest keys.
- [x] Compute SHA-256 digests from content bytes before writing the manifest and leave `manifest.json` out of the checksum map.
- [x] Add the new JSON files to command-managed overwrite protection.
- [x] Add artifact paths and checksum metadata to `--json --output-dir` stdout.
- [x] Extend adapter handoff tests for JSON file content, manifest paths and checksums, overwrite behavior, JSON stdout metadata, and offline safety.
- [x] Update docs and close the earlier structured JSON/content hash open question.
- [x] Validate this dogfood bundle with default and coverage-required readiness gates.

## Dependencies

- Existing `build_adapter_feature_handoff_report` data.
- Existing adapter handoff Markdown artifact writer.
- Python standard library `hashlib`.

## Open Questions

- Should a future release publish a formal JSON schema for these artifact payloads after the current shape stabilizes through agent use?

## Agent Handoff

- Run `specspine adapters handoff adapter-handoff-structured-artifacts . --json`.
- Run `specspine adapters handoff adapter-handoff-structured-artifacts . --output-dir .specspine/adapter-handoff-structured-artifacts-test --force --json`.
- Run `specspine feature ready adapter-handoff-structured-artifacts . --json`.
- Run `specspine feature ready adapter-handoff-structured-artifacts . --json --require-coverage`.
- Run `specspine validate . --fusion --features`.
