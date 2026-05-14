# Architecture

## System Shape

SpecSpine is a small Python package under `src/specspine` with a command-line entry point. The architecture is file-first:

- `workspace` owns base workspace templates and required artifact checks.
- `agents` writes project-local `AGENTS.md` instructions.
- `features` creates and reads native feature bundles, updates lifecycle status, exports execution task handoffs, exports traceability handoffs, evaluates readiness gates, exports compact feature handoff packets, and exports offline issue drafts.
- `adapters` describes external upstream tools and probes local availability.
- `fusion` writes the OpenSpec + Spec Kit + Superpowers adapter layer.
- `status` builds machine-readable workspace summaries, recommendations, optional validation summaries, and optional native feature summaries.
- `validation` turns workspace, fusion, adapter, and feature contracts into checks and compact summary records.
- `cli` maps command-line arguments to those modules.

## Data And Interfaces

- `.specspine/spine.yaml` maps the backbone files for a workspace.
- `.specspine/fusion.yaml` records enabled upstreams, the selected agent profile, and the adapter/no-vendor boundary.
- `.specspine/fusion-map.md` and `.specspine/adapters/*.md` document the human-facing integration contract.
- `specs/`, `execution/`, and `quality/` carry the repository-owned source of truth.
- Native feature bundles use peer files with matching `Feature ID: <slug>` markers and one allowed lifecycle `Status`.
- The main machine interfaces are `specspine status . --json`, `specspine status . --json --validate`, `specspine status . --json --validate --feature-summaries`, `specspine feature handoff <slug> . --json`, `specspine feature trace <slug> . --json`, `specspine feature ready <slug> . --json`, and `specspine validate . --fusion --features`.

## Decisions

- Keep the CLI zero-dependency so it runs in constrained agent environments and source checkouts.
- Treat upstream tools as adapters. SpecSpine can print install hints and optionally run public initializer commands, but it does not copy or own upstream code.
- Keep GitHub issue support offline by drafting structured text/JSON instead of requiring `gh`, tokens, or API access.
- Keep feature traceability export offline and extractive by parsing native Markdown sections without AI inference, upstream CLIs, GitHub APIs, or token reads.
- Keep feature readiness gates deterministic by deriving pass/fail checks from native files, trace gaps, lifecycle status, completed checklists, and release readiness evidence.
- Keep feature handoff packets compact by composing existing local status, trace, task, readiness, and release readiness evidence rather than generating new content.
- Keep workspace feature summaries opt-in so default status remains a minimal startup context; compose summaries from local feature handoff evidence when multi-feature comparison is needed.
- Make validation executable and local so agents can detect missing files and broken contracts before and after edits.
- Keep `status --validate` as a report surface that summarizes failed checks while `validate` remains the failing gate command.

## Risks

- Template drift can make generated artifacts too generic. Dogfood this repository and update templates when repeated manual corrections appear.
- Upstream command surfaces may change. Keep adapter docs explicit and probe availability separately from core validation.
- Feature bundles can diverge across spec, execution, and quality files. Validate matching IDs, allowed statuses, and peer-file status consistency.
- Agent instructions can become stale. Prefer short rules that point back to status, validation, and repository specs.
