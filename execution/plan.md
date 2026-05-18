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
- Local native feature archive evidence reporting and package materialization through `specspine feature archive`.
- Native acceptance-test packet export through `specspine feature tests`.
- Local static source-to-test impact reporting through `specspine tests impact`.
- Local spec-code-test-doc consistency reporting through `specspine consistency scan`, linking feature peers to code, tests, docs, and changed paths without running commands.
- Local repository hygiene reporting through `specspine hygiene scan`, surfacing generated cache artifacts and denylisted residue before review or commit.
- Local feature retrospective reporting through `specspine retrospective report`, summarizing readiness, blockers, coverage gaps, open tasks, themes, and deterministic follow-up commands before the next iteration.
- Local acceptance-criterion verification matrix reporting through `specspine verify matrix`.
- Refreshed native feature bundle templates with focused handoff, task issue draft, tests, PR, readiness, and validation guidance.
- Fusion layer generation for OpenSpec, Spec Kit, and Superpowers.
- Status JSON, validation JSON/text, adapter doctor, and install hints.
- Static adapter lifecycle mappings through `specspine adapters lifecycle`.
- Feature-specific adapter handoff packets and per-adapter artifact materialization through `specspine adapters handoff --output-dir`.
- Optional validation summaries in `specspine status --json --validate`.
- Opt-in validation warning details in `specspine status --json --validate --validation-warnings`.
- Optional native feature summaries in `specspine status --json --feature-summaries`, with local status/readiness/metadata filters, coverage-required readiness, and deterministic sorting by operational and metadata fields.
- Optional workspace readiness policy through `.specspine/policy.yaml`, `specspine policy`, `feature ready --policy`, and `status --feature-summaries --feature-policy`.
- Optional workspace readiness rollups in `specspine status --json --readiness-summary`, with coverage-required and policy-selected readiness modes.
- Workspace-level coverage debt reporting through `specspine coverage debt`, with universal and policy-selected coverage-required modes.
- Read-only native feature consistency and coverage analysis through `specspine analyze`, with feature filtering and opt-in failing issue exits.
- Natural-language feature proposal generation through `specspine propose`, with deterministic native bundle generation, dry-run previews, JSON output, metadata flags, conflict protection, and no external services.
- Repository-level quality gate definition export through `specspine gates`, including optional severity, owner, and CI metadata labels.
- Local changed-path risk packet export through `specspine change risk`, classifying changed files and composing optional feature evidence without running commands.
- Local security-sensitive cue packet export through `specspine security cues`, surfacing review keywords without running scanners or proving vulnerabilities.
- Local provenance manifest export through `specspine provenance manifest`, hashing feature evidence files without printing contents or proving command execution.
- Local pre-merge review packet export through `specspine review packet`, composing validation, quality gates, test impact, and optional feature evidence without running commands.
- Unit tests and GitHub Actions coverage for the current command surface.

## Current Milestone

Dogfood SpecSpine as its own fused workspace. The repository should expose real intent, product, architecture, execution, and quality artifacts so future agents can use SpecSpine conventions while improving SpecSpine itself.

## Near-Term Plan

- Keep this repository complete under `specspine status . --json`.
- Prefer `specspine status . --json --validate` when an agent needs both context and quality-gate summary in one packet.
- Add `--validation-warnings` only when an agent needs scaffold placeholder warning ids; keep default status validation focused on failed checks.
- Use `specspine status . --json --validate --feature-summaries` when an agent needs to choose or compare multiple native features; add filters such as `--feature-status validated --feature-ready yes --feature-priority high --feature-sort priority` when a multi-feature workspace needs focused triage; add `--feature-require-coverage` when every candidate must include checked local AC coverage links; add `--feature-policy` when `.specspine/policy.yaml` should decide stricter readiness per feature; keep the default startup packet compact otherwise.
- Use `specspine status . --json --readiness-summary` when an agent or CI job needs whole-workspace ready/not-ready feature counts in one packet; add `--readiness-require-coverage` for universal coverage gates or `--readiness-policy` when `.specspine/policy.yaml` should decide per feature.
- Use `specspine coverage debt . --json` after coverage-required readiness rollups to locate exact feature and AC coverage gaps; add `--policy` when only policy-selected features should count as required debt.
- Use `specspine analyze . --json` after tasks are drafted and before implementation to review cross-artifact consistency, AC-to-task traceability, and local coverage evidence; add `--feature <slug>` for a focused packet or `--fail-on-issues` only when CI should fail on findings.
- Use `specspine tests impact . --json` before or after implementation to inspect static source-to-test recommendations; add `--changed PATH` for focused changes or `--feature <slug>` for feature coverage targets.
- Use `specspine consistency scan . --json` before or after implementation to inspect local spec-code-test-doc drift; add `--changed PATH` for focused changes or `--feature <slug>` for one native feature.
- Use `specspine hygiene scan . --json` before review or commit to inspect generated cache artifacts and denylisted repository residue; add `--changed PATH` for focused context or `--strict` when high-risk findings should fail.
- Use `specspine retrospective report . --json` before planning the next iteration or after review to inspect local feature delivery themes, blockers, coverage gaps, open tasks, and deterministic recommendations; add `--feature <slug>` for one native feature or `--limit N` to trim recommendation rows only.
- Use `specspine verify matrix <slug> . --json` before review or release to inspect AC-level verification evidence, coverage gaps, and advisory follow-up commands.
- Use `specspine change risk . --json` before review to classify changed paths by local risk and evidence expectations; add `--changed PATH` and `--feature <slug>` for focused change review.
- Use `specspine security cues . --json` before review to surface local security-sensitive cues without treating them as proven vulnerabilities; add `--changed PATH` and `--feature <slug>` for focused security review.
- Use `specspine provenance manifest . --json` before review or archive to record local SHA-256 evidence hashes; add `--include PATH` and `--feature <slug>` for focused audit context.
- Use `specspine review packet . --json` before review or merge to compose local validation, quality gate, test impact, and safety evidence; add `--feature <slug>` and `--changed PATH` for focused native feature review.
- Use `specspine feature handoff <slug> . --json` as the default feature-level packet for implementation, acceptance, and review agents.
- Use `specspine feature tasks <slug> . --json` when an agent needs a feature implementation checklist.
- Use `specspine feature task-issues <slug> . --json` when an agent needs one local GitHub issue draft per execution task.
- Use `specspine feature trace <slug> . --json` when an agent or reviewer needs acceptance criteria, tasks, checks, test plan, and gaps in one packet.
- Use `specspine feature ready <slug> . --json` when a reviewer, agent, or CI step needs a failing per-feature release gate; add `--require-coverage` before high-risk release handoffs when every AC must have checked local test coverage evidence; add `--policy` when the workspace policy should make that decision.
- Use `specspine policy . --json` when an agent needs the local readiness governance packet and warning count.
- Use `specspine feature tests <slug> . --json` when QA or testing agents need acceptance criteria mapped to pending test cases plus existing test plan, gaps, and blockers.
- Use `specspine feature pr <slug> . --json` when a reviewer or release agent needs a local Pull Request draft without touching GitHub.
- Use `specspine feature sync-plan <slug> . --json` when a maintainer needs to review GitHub CLI issue/PR sync intent before any remote execution; add `--output-dir .specspine/sync-plan/<slug>` when the body files, manifest, and review-only command script should be materialized locally.
- Use `specspine feature archive <slug> . --json` when a maintainer or reviewer needs durable local closure evidence before archiving; add `--output-dir .specspine/archive/<slug>` when `README.md`, `archive.json`, and source snapshots should be materialized locally.
- Use `specspine gates . --json` when an agent, reviewer, or CI author needs repository-level quality gate definitions, severity/owner/CI metadata, and metadata coverage counts before running or wiring checks.
- Use `specspine adapters lifecycle . --json` when an agent or maintainer needs local status-to-upstream phase definitions before adapter sync or upstream planning.
- Use `specspine adapters handoff <slug> . --json` when an agent needs OpenSpec, Spec Kit, and Superpowers handoff steps for one native feature without executing upstream tooling; add `--output-dir .specspine/adapter-handoff/<slug>` when separate reviewable Markdown files, structured JSON files, a safety manifest, and SHA-256 checksums should be materialized locally.
- Use `specspine validate . --fusion --features` as the project-level gate.
- Let `specspine propose "..." . --slug <slug>` seed natural-language feature work with populated spec, execution, and quality peers. Use `specspine feature new <slug> . --title "..." --why "..."` when a manual template is more appropriate.
- Use native feature lifecycle states to move bundles from `proposed` through `validated` or `archived`; prefer `--enforce-transition` for ordered lifecycle advancement while keeping manual updates available by default.
- Run `specspine feature ready <slug> . --json` and `specspine feature archive <slug> . --json` before enforced archive updates so readiness blockers and durable evidence are reviewed separately from transition rules.
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
- Should future remote sync map local milestone, target release, project, or effort metadata into GitHub Issue Fields only after an explicit authenticated workflow is requested?
- Resolved: readiness summaries are available in workspace status through explicit `--readiness-summary`, while default status remains compact and focused per-feature gates remain available.
- Should future policy sections cover lifecycle transitions or adapter handoff gates beyond readiness coverage?
- Should the refreshed feature bundle template later grow explicit rollout-owner or implementation-file metadata, or stay minimal until a real workflow needs it?
- Should future remote sync consume quality gate `ci_check` labels for branch-protection required checks, or should SpecSpine continue to export them only as local planning metadata?
- Should a future remote-sync command consume `feature sync-plan --output-dir` artifacts after explicit confirmation, or should SpecSpine remain plan-only for GitHub writes?
- Should future adapter handoff artifacts include a signed manifest or schema version after the current structured JSON files and SHA-256 checksums prove useful?
- Should change risk later infer changed files from VCS state behind an explicit flag, or remain purely caller-supplied to avoid subprocesses?
- Should security cues later support a configurable keyword policy file, or stay built-in until real false-positive patterns appear?
- Should review packets later support policy-selected review profiles, or stay compositional over the existing local reports?
- Should verification matrices later support storing signed run-result evidence, or remain a local evidence index until real release workflows need that?
- Should repository hygiene rules later become configurable through policy, or remain built-in until repeated false-positive patterns appear?
