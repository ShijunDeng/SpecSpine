from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from specspine.mcp import (
    MCP_PROTOCOL_VERSION,
    MCP_TOOLS,
    _handle_initialize,
    _handle_initialized,
    _handle_request,
    _handle_tool_call,
    _handle_tools_list,
    _json_error,
    _json_response,
    generate_client_config,
)


class TestJsonRpcHelpers(unittest.TestCase):
    def test_json_response_structure(self):
        response = _json_response(1, {"key": "value"})
        data = json.loads(response)
        self.assertEqual(data["jsonrpc"], "2.0")
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["result"], {"key": "value"})

    def test_json_response_with_string_id(self):
        response = _json_response("abc", "result")
        data = json.loads(response)
        self.assertEqual(data["id"], "abc")

    def test_json_response_with_null_id(self):
        response = _json_response(None, "result")
        data = json.loads(response)
        self.assertIsNone(data["id"])

    def test_json_error_structure(self):
        response = _json_error(1, -32600, "Invalid Request")
        data = json.loads(response)
        self.assertEqual(data["jsonrpc"], "2.0")
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["error"]["code"], -32600)
        self.assertEqual(data["error"]["message"], "Invalid Request")

    def test_json_error_with_null_id(self):
        response = _json_error(None, -32700, "Parse error")
        data = json.loads(response)
        self.assertIsNone(data["id"])

    def test_response_ends_with_newline(self):
        response = _json_response(1, {})
        self.assertTrue(response.endswith("\n"))

    def test_error_ends_with_newline(self):
        response = _json_error(1, -32600, "test")
        self.assertTrue(response.endswith("\n"))


class TestInitialize(unittest.TestCase):
    def test_initialize_returns_protocol_version(self):
        response = _handle_initialize(1, None)
        data = json.loads(response)
        self.assertEqual(data["result"]["protocolVersion"], MCP_PROTOCOL_VERSION)

    def test_initialize_returns_server_info(self):
        response = _handle_initialize(1, None)
        data = json.loads(response)
        self.assertEqual(data["result"]["serverInfo"]["name"], "specspine")
        self.assertEqual(data["result"]["serverInfo"]["version"], "0.2.0")

    def test_initialize_returns_tools_capability(self):
        response = _handle_initialize(1, None)
        data = json.loads(response)
        self.assertIn("tools", data["result"]["capabilities"])

    def test_initialized_no_response(self):
        result = _handle_initialized(None)
        self.assertIsNone(result)

    def test_initialized_with_params_no_response(self):
        result = _handle_initialized({"key": "value"})
        self.assertIsNone(result)

    def test_initialize_with_client_info(self):
        params = {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"},
        }
        response = _handle_initialize(1, params)
        data = json.loads(response)
        self.assertEqual(data["result"]["protocolVersion"], MCP_PROTOCOL_VERSION)


class TestToolsList(unittest.TestCase):
    def test_tools_list_returns_five_tools(self):
        response = _handle_tools_list(1)
        data = json.loads(response)
        self.assertEqual(len(data["result"]["tools"]), 5)

    def test_tools_list_has_specspine_status(self):
        response = _handle_tools_list(1)
        data = json.loads(response)
        names = [t["name"] for t in data["result"]["tools"]]
        self.assertIn("specspine_status", names)

    def test_tools_list_has_specspine_propose(self):
        response = _handle_tools_list(1)
        data = json.loads(response)
        names = [t["name"] for t in data["result"]["tools"]]
        self.assertIn("specspine_propose", names)

    def test_tools_list_has_specspine_feature_ready(self):
        response = _handle_tools_list(1)
        data = json.loads(response)
        names = [t["name"] for t in data["result"]["tools"]]
        self.assertIn("specspine_feature_ready", names)

    def test_tools_list_has_specspine_validate(self):
        response = _handle_tools_list(1)
        data = json.loads(response)
        names = [t["name"] for t in data["result"]["tools"]]
        self.assertIn("specspine_validate", names)

    def test_tools_list_has_specspine_coverage_debt(self):
        response = _handle_tools_list(1)
        data = json.loads(response)
        names = [t["name"] for t in data["result"]["tools"]]
        self.assertIn("specspine_coverage_debt", names)

    def test_each_tool_has_input_schema(self):
        response = _handle_tools_list(1)
        data = json.loads(response)
        for tool in data["result"]["tools"]:
            self.assertIn("inputSchema", tool)
            self.assertEqual(tool["inputSchema"]["type"], "object")

    def test_each_tool_has_description(self):
        response = _handle_tools_list(1)
        data = json.loads(response)
        for tool in data["result"]["tools"]:
            self.assertIn("description", tool)
            self.assertTrue(len(tool["description"]) > 0)

    def test_mcp_tools_constant_has_five_entries(self):
        self.assertEqual(len(MCP_TOOLS), 5)

    def test_specspine_propose_requires_intent(self):
        response = _handle_tools_list(1)
        data = json.loads(response)
        propose = next(t for t in data["result"]["tools"] if t["name"] == "specspine_propose")
        self.assertIn("required", propose["inputSchema"])
        self.assertIn("intent", propose["inputSchema"]["required"])

    def test_specspine_feature_ready_requires_slug(self):
        response = _handle_tools_list(1)
        data = json.loads(response)
        ready = next(
            t for t in data["result"]["tools"] if t["name"] == "specspine_feature_ready"
        )
        self.assertIn("required", ready["inputSchema"])
        self.assertIn("slug", ready["inputSchema"]["required"])


class TestToolCalls(unittest.TestCase):
    def test_tool_call_unknown_tool(self):
        params = {"name": "unknown_tool", "arguments": {}}
        response = _handle_tool_call(1, params)
        data = json.loads(response)
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], -32601)

    def test_tool_call_missing_params(self):
        response = _handle_tool_call(1, None)
        data = json.loads(response)
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], -32602)

    def test_status_tool_call_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "specs").mkdir()
            (root / "execution").mkdir()
            (root / "quality").mkdir()
            (root / "AGENTS.md").write_text("# Test", encoding="utf-8")

            params = {
                "name": "specspine_status",
                "arguments": {"path": str(root)},
            }
            response = _handle_tool_call(1, params)
            data = json.loads(response)
            self.assertIn("result", data)
            content = data["result"]["content"][0]["text"]
            status = json.loads(content)
            self.assertIn("root", status)

    def test_validate_tool_call_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "specs").mkdir()
            (root / "execution").mkdir()
            (root / "quality").mkdir()
            (root / "AGENTS.md").write_text("# Test", encoding="utf-8")

            params = {
                "name": "specspine_validate",
                "arguments": {"path": str(root), "fusion": True, "features": True},
            }
            response = _handle_tool_call(1, params)
            data = json.loads(response)
            self.assertIn("result", data)
            content = data["result"]["content"][0]["text"]
            report = json.loads(content)
            self.assertIn("checks", report)

    def test_coverage_debt_tool_call_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "specs").mkdir()
            (root / "execution").mkdir()
            (root / "quality").mkdir()
            (root / "AGENTS.md").write_text("# Test", encoding="utf-8")

            params = {
                "name": "specspine_coverage_debt",
                "arguments": {"path": str(root)},
            }
            response = _handle_tool_call(1, params)
            data = json.loads(response)
            self.assertIn("result", data)
            content = data["result"]["content"][0]["text"]
            report = json.loads(content)
            self.assertIn("features_total", report)

    def test_propose_tool_call_missing_intent(self):
        params = {"name": "specspine_propose", "arguments": {}}
        response = _handle_tool_call(1, params)
        data = json.loads(response)
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], -32602)

    def test_propose_tool_call_success(self):
        params = {
            "name": "specspine_propose",
            "arguments": {"intent": "add dark mode toggle"},
        }
        response = _handle_tool_call(1, params)
        data = json.loads(response)
        self.assertIn("result", data)
        content = data["result"]["content"][0]["text"]
        result = json.loads(content)
        self.assertIn("slug", result)
        self.assertIn("files", result)

    def test_propose_tool_call_with_slug(self):
        params = {
            "name": "specspine_propose",
            "arguments": {"intent": "add dark mode", "slug": "my-dark-mode"},
        }
        response = _handle_tool_call(1, params)
        data = json.loads(response)
        result = json.loads(data["result"]["content"][0]["text"])
        self.assertEqual(result["slug"], "my-dark-mode")

    def test_feature_ready_tool_call_missing_slug(self):
        params = {"name": "specspine_feature_ready", "arguments": {}}
        response = _handle_tool_call(1, params)
        data = json.loads(response)
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], -32602)

    def test_feature_ready_tool_call_with_nonexistent_feature(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            params = {
                "name": "specspine_feature_ready",
                "arguments": {"slug": "nonexistent-feature", "path": tmpdir},
            }
            response = _handle_tool_call(1, params)
            data = json.loads(response)
            self.assertIn("result", data)
            content = data["result"]["content"][0]["text"]
            result = json.loads(content)
            self.assertEqual(result["feature_id"], "nonexistent-feature")
            self.assertFalse(result["ready"])

    def test_tool_call_returns_text_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "specs").mkdir()
            (root / "execution").mkdir()
            (root / "quality").mkdir()
            (root / "AGENTS.md").write_text("# Test", encoding="utf-8")

            params = {
                "name": "specspine_status",
                "arguments": {"path": str(root)},
            }
            response = _handle_tool_call(1, params)
            data = json.loads(response)
            content = data["result"]["content"]
            self.assertEqual(len(content), 1)
            self.assertEqual(content[0]["type"], "text")


class TestHandleRequest(unittest.TestCase):
    def test_malformed_json(self):
        response = _handle_request("not json at all")
        data = json.loads(response)
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], -32700)

    def test_non_object_json(self):
        response = _handle_request("42")
        data = json.loads(response)
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], -32600)

    def test_wrong_jsonrpc_version(self):
        request = json.dumps({"jsonrpc": "1.0", "id": 1, "method": "initialize"})
        response = _handle_request(request)
        data = json.loads(response)
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], -32600)

    def test_missing_method(self):
        request = json.dumps({"jsonrpc": "2.0", "id": 1})
        response = _handle_request(request)
        data = json.loads(response)
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], -32600)

    def test_unknown_method(self):
        request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "unknown"})
        response = _handle_request(request)
        data = json.loads(response)
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], -32601)

    def test_initialize_via_handle_request(self):
        request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        response = _handle_request(request)
        data = json.loads(response)
        self.assertEqual(data["result"]["protocolVersion"], MCP_PROTOCOL_VERSION)

    def test_initialized_notification_returns_none(self):
        request = json.dumps(
            {"jsonrpc": "2.0", "method": "notifications/initialized"}
        )
        response = _handle_request(request)
        self.assertIsNone(response)

    def test_tools_list_via_handle_request(self):
        request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        response = _handle_request(request)
        data = json.loads(response)
        self.assertEqual(len(data["result"]["tools"]), 5)

    def test_tools_call_via_handle_request(self):
        request = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "specspine_propose",
                "arguments": {"intent": "add a feature"},
            },
        })
        response = _handle_request(request)
        data = json.loads(response)
        self.assertIn("result", data)


class TestGenerateClientConfig(unittest.TestCase):
    def test_claude_desktop_format(self):
        config = generate_client_config(fmt="claude-desktop")
        self.assertIn("mcpServers", config)
        self.assertIn("specspine", config["mcpServers"])
        server = config["mcpServers"]["specspine"]
        self.assertEqual(server["command"], "python3")
        self.assertEqual(server["args"], ["-m", "specspine", "mcp", "server"])

    def test_vscode_format(self):
        config = generate_client_config(fmt="vscode")
        self.assertIn("mcp", config)
        self.assertIn("servers", config["mcp"])
        self.assertIn("specspine", config["mcp"]["servers"])

    def test_cursor_format(self):
        config = generate_client_config(fmt="cursor")
        self.assertIn("mcpServers", config)
        self.assertIn("specspine", config["mcpServers"])

    def test_default_format_is_claude_desktop(self):
        config = generate_client_config()
        self.assertIn("mcpServers", config)

    def test_config_includes_env_with_root(self):
        config = generate_client_config(root="/some/path")
        server = config["mcpServers"]["specspine"]
        self.assertIn("env", server)

    def test_config_root_resolution(self):
        config = generate_client_config(root=".")
        server = config["mcpServers"]["specspine"]
        self.assertIn("SPECSPINE_ROOT", server["env"])


class TestMcpConstants(unittest.TestCase):
    def test_protocol_version(self):
        self.assertEqual(MCP_PROTOCOL_VERSION, "2024-11-05")

    def test_mcp_tools_is_list(self):
        self.assertIsInstance(MCP_TOOLS, list)

    def test_mcp_tools_all_have_names(self):
        for tool in MCP_TOOLS:
            self.assertIn("name", tool)
            self.assertIsInstance(tool["name"], str)


if __name__ == "__main__":
    unittest.main()
