# Intent

SpecSpine exists to give AI-assisted engineering a durable project backbone: intent, specs, execution, and quality artifacts that agents can read and validate without relying on a hosted service.

## Why

Spec-driven AI work often fragments across prompts, generated plans, issue trackers, and tool-specific folders. SpecSpine makes the contract explicit in ordinary repository files so an agent can answer three questions before editing: why this matters, what is in scope, and how completion will be verified.

The project also provides a fusion layer for teams that already use OpenSpec, Spec Kit, or Superpowers. SpecSpine records how those tools fit together while preserving their upstream ownership.

## Users

- Developers using Codex, Claude, Gemini, Copilot, Cursor, OpenCode, or Windsurf for repository work.
- Maintainers who want repeatable context packets, local validation, and traceable feature bundles.
- Teams adopting OpenSpec, Spec Kit, or Superpowers without copying their source code into each product repository.

## Outcomes

- A fresh repository can be initialized with `specspine init`, `specspine agents init`, or `specspine fuse`.
- `specspine status . --json` gives agents a compact, machine-readable workspace summary.
- `specspine validate . --fusion --features` enforces workspace, fusion, adapter, and native feature contracts.
- Native feature bundles can be created and exported into local GitHub issue drafts without reading tokens or calling GitHub APIs.

## Constraints

- The CLI is zero-dependency Python and must remain usable through `PYTHONPATH=src python3 -m specspine`.
- OpenSpec, Spec Kit, and Superpowers stay external. `integration_mode: adapter` and `vendored_upstream_code: false` are required.
- Upstream initializer commands run only when the user opts in with `--run-upstream`.
- Local workflows must not require GitHub credentials or network access unless a user explicitly asks for external integration.
