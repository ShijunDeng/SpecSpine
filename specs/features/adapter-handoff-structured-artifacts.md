# Adapter Handoff Structured Artifacts

Feature ID: adapter-handoff-structured-artifacts
Status: validated
Priority: high
Owner: SpecSpine maintainers
Milestone: adapter fusion
Target Release: current
Project: Native feature bundles
Effort: M

## Why

Adapter handoff artifact directories need machine-readable payloads and content digests so implementation, acceptance, and review agents can consume focused adapter context without scraping Markdown or trusting unchecked files.

## Users

- Main agents materializing adapter handoff directories before delegating subagent work.
- OpenSpec, Spec Kit, and Superpowers-focused subagents reading only their adapter payload.
- Reviewers and CI-like local scripts checking artifact integrity before manual upstream work.

## Scope

- Keep the existing adapter handoff artifact files: `manifest.json`, `combined.md`, and focused per-adapter Markdown files.
- Add `combined.json` with the full adapter handoff report from the same in-memory report used by command JSON output.
- Add focused `adapters/openspec.json`, `adapters/speckit.json`, and `adapters/superpowers.json` payloads with feature evidence, safety flags, summary, recommended commands, and the selected adapter entry.
- Add manifest paths for the new JSON files while preserving existing artifact path keys.
- Add `checksum_algorithm=sha256` and `artifact_checksums` for all non-manifest command-managed content artifacts.
- Treat the new JSON files as command-managed for overwrite protection and `--force`.
- Add artifact path and checksum metadata to `--json --output-dir` stdout.
- Keep the workflow offline and local with no subprocesses, probes, upstream CLIs, network, token reads, GitHub calls, or new dependencies.

## Non-Goals

- Executing OpenSpec, Spec Kit, Superpowers, GitHub CLI, shell commands, or network calls.
- Hashing `manifest.json` inside itself.
- Deleting unknown files in an existing artifact directory.
- Adding schema validation dependencies.

## Acceptance Criteria

- [x] `specspine adapters handoff <slug> [path] --output-dir DIR` still writes `manifest.json`, `combined.md`, and focused per-adapter Markdown files.
- [x] The same output directory also contains `combined.json` and focused per-adapter JSON files.
- [x] `combined.json` contains the full stable adapter handoff report from the same report source as command JSON output.
- [x] Each focused adapter JSON file includes feature id, status, readiness, source files, missing files, gaps, blocking checks, summary, safety flags, adapter entry, and recommended commands.
- [x] `manifest.json` preserves existing artifact path keys and adds JSON artifact path keys.
- [x] `manifest.json` records `checksum_algorithm=sha256` and SHA-256 checksums for all non-manifest managed artifacts.
- [x] Existing new JSON artifact files block writes without `--force`; `--force` overwrites managed files and preserves unknown files.
- [x] `--json --output-dir` stdout remains parseable full report JSON and includes artifact directory, artifact paths, checksum algorithm, and checksums.
- [x] Tests prove structured artifact writing remains offline and does not call probes, subprocesses, upstream CLIs, network services, GitHub APIs, or token reads.
- [x] Documentation, architecture notes, agent guidance, and dogfood artifacts describe structured adapter handoff artifacts.
