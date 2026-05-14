# Execution Plan

## Completed Milestones

- Base zero-dependency Python CLI with local module execution.
- Workspace initialization for specs, execution, quality, and `.specspine/spine.yaml`.
- Agent instruction initialization through `specspine agents init`.
- Native feature bundle creation and offline GitHub issue draft export.
- Native feature status lifecycle query/update through `specspine feature status`.
- Native feature execution checklist export through `specspine feature tasks`.
- Fusion layer generation for OpenSpec, Spec Kit, and Superpowers.
- Status JSON, validation JSON/text, adapter doctor, and install hints.
- Optional validation summaries in `specspine status --json --validate`.
- Unit tests and GitHub Actions coverage for the current command surface.

## Current Milestone

Dogfood SpecSpine as its own fused workspace. The repository should expose real intent, product, architecture, execution, and quality artifacts so future agents can use SpecSpine conventions while improving SpecSpine itself.

## Near-Term Plan

- Keep this repository complete under `specspine status . --json`.
- Prefer `specspine status . --json --validate` when an agent needs both context and quality-gate summary in one packet.
- Use `specspine feature tasks <slug> . --json` when an agent needs a feature implementation checklist.
- Use `specspine validate . --fusion --features` as the project-level gate.
- Use native feature lifecycle states to move bundles from `proposed` through `validated` or `archived`.
- Improve templates when dogfooding reveals repeated manual edits.
- Keep upstream integrations adapter-based and avoid vendored code.

## Dependencies

- Python 3 standard library.
- Optional external upstream tools only when a user explicitly asks for `--run-upstream`.
- Optional Superpowers agent plugin/extension for quality discipline; SpecSpine records policy locally but does not copy skill files.

## Open Questions

- Should future lifecycle updates enforce transition ordering, or remain manual file-native state changes?
- Should status JSON eventually include warning details, or keep the validation summary focused on failed checks?
- Should task summaries be added to workspace status once task export has more dogfood mileage?
- Which generated templates should be tightened based on this dogfood workspace?
