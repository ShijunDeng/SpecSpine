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
- Optional coverage-required readiness gates through `specspine feature ready --require-coverage`.
- Opt-in native feature transition enforcement through `specspine feature status --enforce-transition`.
- Offline Pull Request draft export through `specspine feature pr`.
- Local GitHub CLI synchronization planning and artifact materialization through `specspine feature sync-plan`.
- Native acceptance-test packet export through `specspine feature tests`.
- Refreshed native feature bundle templates with focused handoff, task issue draft, tests, PR, readiness, and validation guidance.
- Fusion layer generation for OpenSpec, Spec Kit, and Superpowers.
- Status JSON, validation JSON/text, adapter doctor, and install hints.
- Static adapter lifecycle mappings through `specspine adapters lifecycle`.
- Feature-specific adapter handoff packets through `specspine adapters handoff`.
- Optional validation summaries in `specspine status --json --validate`.
- Opt-in validation warning details in `specspine status --json --validate --validation-warnings`.
- Optional native feature summaries in `specspine status --json --feature-summaries`, with local status/readiness filters and deterministic sorting.
- Repository-level quality gate definition export through `specspine gates`.
- Unit tests and GitHub Actions coverage for the current command surface.

## Current Milestone

Dogfood SpecSpine as its own fused workspace. The repository should expose real intent, product, architecture, execution, and quality artifacts so future agents can use SpecSpine conventions while improving SpecSpine itself.

## Near-Term Plan

- Keep this repository complete under `specspine status . --json`.
- Prefer `specspine status . --json --validate` when an agent needs both context and quality-gate summary in one packet.
- Add `--validation-warnings` only when an agent needs scaffold placeholder warning ids; keep default status validation focused on failed checks.
- Use `specspine status . --json --validate --feature-summaries` when an agent needs to choose or compare multiple native features; add filters such as `--feature-status validated --feature-ready yes --feature-priority high --feature-sort priority` when a multi-feature workspace needs focused triage; keep the default startup packet compact otherwise.
- Use `specspine feature handoff <slug> . --json` as the default feature-level packet for implementation, acceptance, and review agents.
- Use `specspine feature tasks <slug> . --json` when an agent needs a feature implementation checklist.
- Use `specspine feature task-issues <slug> . --json` when an agent needs one local GitHub issue draft per execution task.
- Use `specspine feature trace <slug> . --json` when an agent or reviewer needs acceptance criteria, tasks, checks, test plan, and gaps in one packet.
- Use `specspine feature ready <slug> . --json` when a reviewer, agent, or CI step needs a failing per-feature release gate; add `--require-coverage` before high-risk release handoffs when every AC must have checked local test coverage evidence.
- Use `specspine feature tests <slug> . --json` when QA or testing agents need acceptance criteria mapped to pending test cases plus existing test plan, gaps, and blockers.
- Use `specspine feature pr <slug> . --json` when a reviewer or release agent needs a local Pull Request draft without touching GitHub.
- Use `specspine feature sync-plan <slug> . --json` when a maintainer needs to review GitHub CLI issue/PR sync intent before any remote execution; add `--output-dir .specspine/sync-plan/<slug>` when the body files, manifest, and review-only command script should be materialized locally.
- Use `specspine gates . --json` when an agent, reviewer, or CI author needs repository-level quality gate definitions before running or wiring checks.
- Use `specspine adapters lifecycle . --json` when an agent or maintainer needs local status-to-upstream phase definitions before adapter sync or upstream planning.
- Use `specspine adapters handoff <slug> . --json` when an agent needs OpenSpec, Spec Kit, and Superpowers handoff steps for one native feature without executing upstream tooling.
- Use `specspine validate . --fusion --features` as the project-level gate.
- Let `specspine feature new <slug> . --title "..." --why "..."` seed the feature's spec, execution, quality, handoff, task issue draft, tests, PR, ready, validation workflow, and initial `Priority: medium` / `Owner: unassigned` metadata before implementation begins.
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
- Should feature summary triage later need richer structured metadata beyond local `Priority:` and `Owner:`, such as milestone, target release, or remote project fields?
- Should readiness summaries eventually be included in workspace status, or remain an explicit per-feature gate?
- Should workspaces eventually have a policy file that chooses when `feature ready --require-coverage` is mandatory?
- Should the refreshed feature bundle template later grow explicit rollout-owner or implementation-file metadata, or stay minimal until a real workflow needs it?
- Should future quality gate definitions include structured severity, owning role, or expected CI check names, or stay as Markdown-derived records until remote sync exists?
- Should a future remote-sync command consume `feature sync-plan --output-dir` artifacts after explicit confirmation, or should SpecSpine remain plan-only for GitHub writes?
- Should adapter handoff packets later support per-adapter output files, or is one combined packet enough for agents?
