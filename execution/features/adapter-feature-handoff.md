# Adapter Feature Handoff Execution

Feature ID: adapter-feature-handoff
Status: validated
Why: Agents need a feature-specific adapter handoff packet that joins native SpecSpine evidence with OpenSpec, Spec Kit, and Superpowers lifecycle context while staying fully local and non-executing.

## Milestones

- Define the adapter feature handoff report shape and safe recommended step schema.
- Reuse native feature handoff evidence and adapter lifecycle mappings.
- Wire `specspine adapters handoff` into the CLI with JSON, Markdown, output file, and error-code behavior.
- Add focused tests for shape, rendering, mapping selection, safe steps, partial and missing bundles, and offline boundaries.
- Update documentation, agent guidance, and dogfood artifacts.
- Run focused tests, full tests, feature readiness, and fused feature validation.

## Tasks

- [x] AC001 Add adapter handoff dataclasses for report entries and recommended upstream steps.
- [x] AC002 Compose feature id, status, readiness, source files, missing files, gaps, blockers, and summary from existing native feature reports.
- [x] AC003 Select each adapter's lifecycle mapping from the current native feature status.
- [x] AC004 Add OpenSpec recommended CLI argv for `status --json`, `instructions apply --change <slug> --json`, and `validate --all --json`.
- [x] AC005 Add Spec Kit recommended agent actions for Spec, Plan, Tasks, and Implement.
- [x] AC006 Add Superpowers recommended agent actions for brainstorming, writing-plans, test-driven-development, subagent-driven-development, requesting-code-review, and verification-before-completion.
- [x] AC007 Mark every upstream step as non-remote, token-free, network-free, unsafe to auto-run, and unexecuted.
- [x] AC008 Add JSON and Markdown renderers for the adapter feature handoff.
- [x] AC009 Wire `specspine adapters handoff <slug> [path] [--json] [--output FILE] [--force]`.
- [x] AC010 Preserve partial bundle success and missing bundle or invalid slug exit codes.
- [x] AC010 Add tests for JSON shape, text output, output file behavior, mapping selection, safe steps, partial bundles, error codes, and no subprocess/network/probe/token reads.
- [x] AC010 Update README, architecture docs, upstream docs, product and architecture specs, execution plan and tasks, quality review notes, and agent instructions.
- [x] AC010 Add this validated dogfood bundle and verify readiness and validation.

## Dependencies

- Existing `specspine feature handoff` report.
- Existing `specspine adapters lifecycle` mappings.
- Existing fusion config parser and adapter metadata.
- Existing output file overwrite semantics used by feature exporters.

## Open Questions

- Whether future adapter handoff packets should optionally materialize per-adapter Markdown files.
- Whether future upstream sync work should consume this packet directly or derive a narrower adapter-specific packet.

## Agent Handoff

- Run `specspine adapters handoff adapter-feature-handoff . --json` to inspect this feature's adapter handoff.
- Run `specspine adapters lifecycle . --json` to compare the full lifecycle mapping table.
- Run `specspine feature handoff adapter-feature-handoff . --json`.
- Run `specspine feature tests adapter-feature-handoff . --json`.
- Run `specspine feature ready adapter-feature-handoff . --json`.
- Run `specspine validate . --fusion --features`.
