# MCP Server Adapter

Feature ID: mcp-server-adapter
Status: implemented
Priority: high
Owner: SpecSpine maintainers
Milestone: AI agent integration
Target Release: 0.4.0
Project: Native feature bundles
Effort: XL

## Why

AI coding agents (Claude Code, Cursor, VS Code Copilot, Windsurf) cannot natively discover or invoke SpecSpine capabilities. MCP (Model Context Protocol) is now the de facto standard for connecting AI tools to external capabilities, with 23k+ GitHub stars. This feature exposes SpecSpine commands as MCP tools, enabling any MCP-compatible host to discover and use SpecSpine natively through the LLM's tool-selection mechanism.

## Users

- Developers using Claude Code, Cursor, VS Code Copilot, or Windsurf who want native SpecSpine integration
- AI coding agents that discover capabilities through MCP tools/list and invoke them via tools/call
- Teams adopting SpecSpine in multi-agent workflows where agents need programmatic access to spec lifecycle

## Scope

- `specspine mcp server` launches an MCP-compliant stdio server with JSON-RPC 2.0 protocol
- `specspine mcp config` generates MCP client configuration JSON for Claude Desktop, VS Code, Cursor
- Zero-dependency implementation (pure Python stdlib)
- Exposes 5 MCP tools: specspine_status, specspine_propose, specspine_feature_ready, specspine_validate, specspine_coverage_debt
- Each tool has typed inputSchema matching existing CLI arguments
- All tool results return structured JSON matching existing --json CLI output
- Proper JSON-RPC 2.0 error handling

## Non-Goals

- No external Python dependencies
- No network calls or HTTP server (stdio only)
- No token management or GitHub API access
- No direct upstream tool invocation

## Acceptance Criteria

- [x] AC001: `specspine mcp server` launches an MCP-compliant stdio server responding to initialize, tools/list, and tools/call JSON-RPC 2.0 requests
- [x] AC002: MCP server exposes 5 tools with descriptive description and typed inputSchema
- [x] AC003: specspine_status tool accepts path, validate, feature_summaries, readiness_summary and returns status JSON
- [x] AC004: specspine_propose tool accepts intent (required), slug, dry_run and returns generated spec bundle JSON
- [x] AC005: specspine_feature_ready tool accepts slug (required), path, require_coverage and returns readiness gate JSON
- [x] AC006: All MCP tool results return structured JSON with content format matching --json CLI output
- [x] AC007: MCP server handles invalid arguments with proper JSON-RPC 2.0 error responses (-32602, -32601)
- [x] AC008: MCP server works with zero external Python dependencies beyond stdlib
- [x] AC009: specspine mcp server is configurable in Claude Desktop / VS Code via config JSON
- [x] AC010: specspine mcp config generates correct MCP client configuration for Claude Desktop, VS Code, Cursor

## Edge Cases

- Malformed JSON-RPC requests return error response without crashing
- Interrupted stdio (EOF) exits gracefully
- Concurrent tool calls handled sequentially (single-threaded stdio)
- Unicode characters in paths and intent preserved

## Constraints

- Zero-dependency Python (no external packages beyond stdlib)
- No network calls or API keys
- JSON-RPC 2.0 protocol implemented directly
- Single-threaded (stdio protocol constraint)

## Traceability Notes

- AC001-AC010 map to test cases in tests/test_mcp.py
- 53 unit tests covering transport, lifecycle, tool calls, error handling, config generation
