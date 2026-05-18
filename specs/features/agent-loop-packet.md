# Agent Loop Packet

Feature ID: agent-loop-packet
Status: validated
Priority: high
Owner: platform
Milestone: local agent workflows
Target Release: 0.2.x
Project: Native feature bundles
Effort: M

## Why

Implementation workers need one deterministic workspace packet before they start a local agent loop. Existing status, readiness, handoff, and validation commands expose the right evidence, but agents still have to stitch together workspace context, lifecycle guidance, subagent roles, validation commands, safety boundaries, and upstream metadata manually.

## Users

- Implementation agents starting work in a SpecSpine repository.
- Review agents checking local safety boundaries before delegating work.
- Maintainers who need a packet that is safe to generate without GitHub, tokens, network access, subprocesses, or adapter probes.

## Scope

- Add `specspine loop packet [path] [--json] [--output FILE] [--force] [--deadline VALUE]`.
- Compose the packet from local status, feature summaries, readiness summary, and upstream metadata.
- Emit stable JSON with root, deadline, core features, summary counts, context commands, lifecycle steps, subagents, validation commands, safety notes, upstreams, and recommended commands.
- Emit readable Markdown-like text with the same key sections.
- Keep the command local and deterministic; only `--output` writes an explicit text packet.

## Non-Goals

- Running tests, subprocesses, upstream CLIs, adapter probes, GitHub commands, or network calls.
- Reading or writing tokens.
- Replacing focused feature handoff, tests, tasks, ready, coverage debt, or validation commands.

## Acceptance Criteria

- [x] `specspine loop packet [path] [--json] [--output FILE] [--force] [--deadline VALUE]` is registered under the `loop` command group.
- [x] JSON output includes `root`, `deadline`, `core_features`, `summary`, `context_commands`, `lifecycle_steps`, `subagents`, `validation_commands`, `safety_notes`, `upstreams`, and `recommended_commands`.
- [x] Summary counts include feature totals, ready/not-ready totals, open task totals, gap totals, blocking check totals, and enabled upstream totals.
- [x] Text output contains the same key sections in readable Markdown-like form.
- [x] `--output` writes the text packet, refuses existing files unless `--force` is used, and with `--json` still prints JSON to stdout.
- [x] The builder reuses `build_status(..., include_feature_summaries=True, include_readiness_summary=True, ...)` and upstream metadata from status.
- [x] The command does not call GitHub, read or write tokens, invoke subprocesses, probe adapters, or access the network.
- [x] Documentation, agent guidance, dogfood artifacts, and focused tests cover the loop packet workflow.
