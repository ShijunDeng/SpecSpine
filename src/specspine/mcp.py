from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

MCP_PROTOCOL_VERSION = "2024-11-05"

MCP_TOOLS = [
    {
        "name": "specspine_status",
        "description": "Summarize SpecSpine workspace status, optional validation, feature summaries, and readiness counts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Workspace root path (default: current directory).",
                },
                "validate": {
                    "type": "boolean",
                    "description": "Include a validation summary.",
                },
                "feature_summaries": {
                    "type": "boolean",
                    "description": "Include compact per-feature progress summaries.",
                },
                "readiness_summary": {
                    "type": "boolean",
                    "description": "Include a workspace rollup of feature readiness gates.",
                },
            },
        },
    },
    {
        "name": "specspine_propose",
        "description": "Generate a structured spec bundle from natural language intent.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "description": "Natural language description of the feature.",
                },
                "slug": {
                    "type": "string",
                    "description": "Feature slug (auto-generated from intent if omitted).",
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Return generated content without writing files.",
                },
            },
            "required": ["intent"],
        },
    },
    {
        "name": "specspine_feature_ready",
        "description": "Check whether a native feature bundle passes the local readiness gate.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "slug": {
                    "type": "string",
                    "description": "Feature id, such as add-dark-mode.",
                },
                "path": {
                    "type": "string",
                    "description": "Workspace root path (default: current directory).",
                },
                "require_coverage": {
                    "type": "boolean",
                    "description": "Require completed local Test Coverage links for every acceptance criterion.",
                },
            },
            "required": ["slug"],
        },
    },
    {
        "name": "specspine_validate",
        "description": "Validate SpecSpine workspace contracts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Workspace root path (default: current directory).",
                },
                "fusion": {
                    "type": "boolean",
                    "description": "Also require and validate SpecSpine fusion files.",
                },
                "features": {
                    "type": "boolean",
                    "description": "Also validate native feature bundle consistency.",
                },
            },
        },
    },
    {
        "name": "specspine_coverage_debt",
        "description": "Report native feature acceptance-criteria coverage debt.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Workspace root path (default: current directory).",
                },
                "policy": {
                    "type": "boolean",
                    "description": "Only require coverage for features selected by workspace readiness policy.",
                },
            },
        },
    },
]


def _json_response(result_id, result):
    return json.dumps({
        "jsonrpc": "2.0",
        "id": result_id,
        "result": result,
    }) + "\n"


def _json_error(error_id, code, message):
    return json.dumps({
        "jsonrpc": "2.0",
        "id": error_id,
        "error": {
            "code": code,
            "message": message,
        },
    }) + "\n"


def _text_content(text):
    return {
        "content": [
            {"type": "text", "text": text},
        ],
    }


def _handle_initialize(request_id, params):
    result = {
        "protocolVersion": MCP_PROTOCOL_VERSION,
        "capabilities": {
            "tools": {},
        },
        "serverInfo": {
            "name": "specspine",
            "version": "0.2.0",
        },
    }
    return _json_response(request_id, result)


def _handle_initialized(params):
    pass


def _handle_tools_list(request_id):
    return _json_response(request_id, {"tools": MCP_TOOLS})


def _handle_tool_call(request_id, params):
    if params is None:
        return _json_error(
            request_id,
            -32602,
            "Missing params for tools/call",
        )

    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if tool_name == "specspine_status":
        return _call_specspine_status(request_id, arguments)
    if tool_name == "specspine_propose":
        return _call_specspine_propose(request_id, arguments)
    if tool_name == "specspine_feature_ready":
        return _call_specspine_feature_ready(request_id, arguments)
    if tool_name == "specspine_validate":
        return _call_specspine_validate(request_id, arguments)
    if tool_name == "specspine_coverage_debt":
        return _call_specspine_coverage_debt(request_id, arguments)

    return _json_error(
        request_id,
        -32601,
        f"Unknown tool: {tool_name}",
    )


def _call_specspine_status(request_id, arguments):
    try:
        from .status import build_status

        path = Path(arguments.get("path", ".")).expanduser().resolve()
        validate = bool(arguments.get("validate", False))
        feature_summaries = bool(arguments.get("feature_summaries", False))
        readiness_summary = bool(arguments.get("readiness_summary", False))

        status_kwargs = {
            "include_feature_summaries": feature_summaries,
            "include_readiness_summary": readiness_summary,
        }
        status = build_status(path, **status_kwargs)

        if validate:
            from .validation import build_validation_report, build_validation_summary

            report = build_validation_report(
                path,
                include_fusion=True,
                include_features=True,
            )
            status["validation"] = build_validation_summary(
                report,
                included={
                    "workspace": True,
                    "fusion": True,
                    "features": True,
                    "adapters": False,
                },
            )

        output = json.dumps(status, indent=2, sort_keys=True)
        return _json_response(request_id, _text_content(output))
    except Exception as exc:
        return _json_error(request_id, -32603, f"specspine_status failed: {exc}")


def _call_specspine_propose(request_id, arguments):
    try:
        from .proposer import build_proposal_content

        intent = arguments.get("intent")
        if not intent:
            return _json_error(
                request_id,
                -32602,
                "specspine_propose requires 'intent' argument",
            )

        slug = arguments.get("slug", "")
        if not slug:
            from .proposer import generate_slug_from_intent

            slug = generate_slug_from_intent(intent)

        dry_run = bool(arguments.get("dry_run", False))

        result = build_proposal_content(slug, intent)
        output = json.dumps(
            {
                "slug": slug,
                "intent": intent,
                "dry_run": dry_run,
                "files": result,
            },
            indent=2,
            sort_keys=True,
        )
        return _json_response(request_id, _text_content(output))
    except ValueError as exc:
        return _json_error(request_id, -32602, f"specspine_propose invalid input: {exc}")
    except Exception as exc:
        return _json_error(request_id, -32603, f"specspine_propose failed: {exc}")


def _call_specspine_feature_ready(request_id, arguments):
    try:
        from .features import build_feature_ready_report

        slug = arguments.get("slug")
        if not slug:
            return _json_error(
                request_id,
                -32602,
                "specspine_feature_ready requires 'slug' argument",
            )

        path = Path(arguments.get("path", ".")).expanduser().resolve()
        require_coverage = bool(arguments.get("require_coverage", False))

        report = build_feature_ready_report(
            path,
            slug,
            require_coverage=require_coverage,
        )
        output = json.dumps(report.as_dict(), indent=2, sort_keys=True)
        return _json_response(request_id, _text_content(output))
    except ValueError as exc:
        return _json_error(request_id, -32602, f"specspine_feature_ready invalid input: {exc}")
    except Exception as exc:
        return _json_error(request_id, -32603, f"specspine_feature_ready failed: {exc}")


def _call_specspine_validate(request_id, arguments):
    try:
        from .validation import build_validation_report

        path = Path(arguments.get("path", ".")).expanduser().resolve()
        fusion = bool(arguments.get("fusion", False))
        features = bool(arguments.get("features", False))

        report = build_validation_report(
            path,
            include_fusion=fusion,
            include_features=features,
        )
        output = json.dumps(report, indent=2, sort_keys=True)
        return _json_response(request_id, _text_content(output))
    except Exception as exc:
        return _json_error(request_id, -32603, f"specspine_validate failed: {exc}")


def _call_specspine_coverage_debt(request_id, arguments):
    try:
        from .coverage import build_coverage_debt_report

        path = Path(arguments.get("path", ".")).expanduser().resolve()
        policy = bool(arguments.get("policy", False))

        report = build_coverage_debt_report(path, use_policy=policy)
        output = json.dumps(report, indent=2, sort_keys=True)
        return _json_response(request_id, _text_content(output))
    except Exception as exc:
        return _json_error(request_id, -32603, f"specspine_coverage_debt failed: {exc}")


def _handle_request(raw_line):
    try:
        request = json.loads(raw_line)
    except json.JSONDecodeError as exc:
        return _json_error(None, -32700, f"Parse error: {exc}")

    if not isinstance(request, dict):
        return _json_error(None, -32600, "Invalid Request: expected object")

    jsonrpc = request.get("jsonrpc")
    if jsonrpc != "2.0":
        return _json_error(request.get("id"), -32600, "Invalid Request: jsonrpc must be 2.0")

    method = request.get("method")
    if method is None:
        return _json_error(request.get("id"), -32600, "Invalid Request: missing method")

    params = request.get("params")
    request_id = request.get("id")

    if method == "initialize":
        return _handle_initialize(request_id, params)

    if method == "notifications/initialized":
        _handle_initialized(params)
        return None

    if method == "tools/list":
        return _handle_tools_list(request_id)

    if method == "tools/call":
        return _handle_tool_call(request_id, params)

    return _json_error(request_id, -32601, f"Method not found: {method}")


def run_server():
    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        response = _handle_request(raw_line)
        if response is not None:
            sys.stdout.write(response)
            sys.stdout.flush()


def generate_client_config(fmt="claude-desktop", root="."):
    resolved_root = str(Path(root).expanduser().resolve())
    server_entry = {
        "command": "python3",
        "args": ["-m", "specspine", "mcp", "server"],
        "env": {
            "SPECSPINE_ROOT": resolved_root,
        },
    }

    if fmt == "claude-desktop":
        return {
            "mcpServers": {
                "specspine": server_entry,
            },
        }
    if fmt == "vscode":
        return {
            "mcp": {
                "servers": {
                    "specspine": server_entry,
                },
            },
        }
    if fmt == "cursor":
        return {
            "mcpServers": {
                "specspine": server_entry,
            },
        }

    return {
        "mcpServers": {
            "specspine": server_entry,
        },
    }
