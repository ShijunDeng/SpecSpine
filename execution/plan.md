# Execution Plan

## Completed Milestones

- Base zero-dependency Python CLI with local module execution.
- Workspace initialization for specs, execution, quality, and `.specspine/spine.yaml`.
- Agent instruction initialization through `specspine agents init`.
- Native feature bundle creation and offline GitHub issue draft export.
- Native feature status lifecycle query/update through `specspine feature status`.
- Native feature execution checklist export through `specspine feature tasks`.
- Native feature task issue draft package export through `specspine feature task-issues`.
- Native feature traceability export through `specspine feature trace`.
- Native feature readiness gates through `specspine feature ready`.
- Opt-in native feature transition enforcement through `specspine feature status --enforce-transition`.
- Offline Pull Request draft export through `specspine feature pr`.
- Native acceptance-test packet export through `specspine feature tests`.
- Refreshed native feature bundle templates with focused handoff, task issue draft, tests, PR, readiness, and validation guidance.
- Fusion layer generation for OpenSpec, Spec Kit, and Superpowers.
- Status JSON, validation JSON/text, adapter doctor, and install hints.
- Optional validation summaries in `specspine status --json --validate`.
- Opt-in validation warning details in `specspine status --json --validate --validation-warnings`.
- Optional native feature summaries in `specspine status --json --feature-summaries`, with local status/readiness filters and deterministic sorting.
- Unit tests and GitHub Actions coverage for the current command surface.

## Current Milestone

Dogfood SpecSpine as its own fused workspace. The repository should expose real intent, product, architecture, execution, and quality artifacts so future agents can use SpecSpine conventions while improving SpecSpine itself.

## Near-Term Plan

- Keep this repository complete under `specspine status . --json`.
- Prefer `specspine status . --json --validate` when an agent needs both context and quality-gate summary in one packet.
- Add `--validation-warnings` only when an agent needs scaffold placeholder warning ids; keep default status validation focused on failed checks.
- Use `specspine status . --json --validate --feature-summaries` when an agent needs to choose or compare multiple native features; add filters such as `--feature-status validated --feature-ready yes --feature-sort slug` when a multi-feature workspace needs focused triage; keep the default startup packet compact otherwise.
- Use `specspine feature handoff <slug> . --json` as the default feature-level packet for implementation, acceptance, and review agents.
- Use `specspine feature tasks <slug> . --json` when an agent needs a feature implementation checklist.
- Use `specspine feature task-issues <slug> . --json` when an agent needs one local GitHub issue draft per execution task.
- Use `specspine feature trace <slug> . --json` when an agent or reviewer needs acceptance criteria, tasks, checks, test plan, and gaps in one packet.
- Use `specspine feature ready <slug> . --json` when a reviewer, agent, or CI step needs a failing per-feature release gate.
- Use `specspine feature tests <slug> . --json` when QA or testing agents need acceptance criteria mapped to pending test cases plus existing test plan, gaps, and blockers.
- Use `specspine feature pr <slug> . --json` when a reviewer or release agent needs a local Pull Request draft without touching GitHub.
- Use `specspine validate . --fusion --features` as the project-level gate.
- Let `specspine feature new <slug> . --title "..." --why "..."` seed the feature's spec, execution, quality, handoff, task issue draft, tests, PR, ready, and validation workflow before implementation begins.
- Use native feature lifecycle states to move bundles from `proposed` through `validated` or `archived`; prefer `--enforce-transition` for ordered lifecycle advancement while keeping manual updates available by default.
- Run `specspine feature ready <slug> . --json` before enforced archive updates so readiness blockers are resolved separately from transition rules.
- Continue dogfooding generated templates and tighten them when repeated manual edits appear.
- Keep upstream integrations adapter-based and avoid vendored code.
- Keep validation warnings local and non-blocking; only failed checks should determine `validate` exit code.

## Dependencies

- Python 3 standard library.
- Optional external upstream tools only when a user explicitly asks for `--run-upstream`.
- Optional Superpowers agent plugin/extension for quality discipline; SpecSpine records policy locally but does not copy skill files.

## Open Questions

- Should enforced lifecycle transitions eventually become the default, or remain opt-in for compatibility?
- Should future warning categories beyond scaffold placeholders be exposed through the same opt-in status flag?
- Should feature summary triage eventually need explicit user-owned priority metadata, or are lifecycle/readiness/count filters enough?
- Should readiness summaries eventually be included in workspace status, or remain an explicit per-feature gate?
- Should acceptance-test packets later include explicit user-supplied AC-to-test-file links, or remain implementation-file agnostic until that metadata exists?
- Should the refreshed feature bundle template later grow explicit rollout-owner or implementation-file metadata, or stay minimal until a real workflow needs it?
