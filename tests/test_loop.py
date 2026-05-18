import json
import os
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.loop import (
    build_loop_packet,
    render_loop_packet_json,
    render_loop_packet_text,
)
from specspine.status import build_status
from specspine.workspace import init_workspace


def write_loop_feature_bundle(root: Path, slug: str = "agent-loop-packet") -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "tests" / "test_loop.py").write_text("# loop tests\n", encoding="utf-8")

    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Agent Loop Packet",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "Priority: high",
                "Owner: platform",
                "",
                "## Acceptance Criteria",
                "",
                "- [x] AC001 Builder emits a local deterministic packet.",
                "- [x] AC002 CLI writes text while keeping JSON on stdout.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Agent Loop Packet Execution",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Tasks",
                "",
                "- [x] Build packet exporter.",
                "- [x] Add CLI output handling.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Agent Loop Packet Quality",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Required Checks",
                "",
                "- [x] Unit tests pass.",
                "- [x] Local-only safety contract is covered.",
                "",
                "## Test Plan",
                "",
                "- Run `PYTHONPATH=src python3 -m unittest tests.test_loop`.",
                "",
                "## Test Coverage",
                "",
                "- [x] AC001 -> tests/test_loop.py::LoopPacketTests::test_builder_emits_local_deterministic_packet",
                "- [x] AC002 -> tests/test_loop.py::LoopPacketTests::test_cli_json_output_writes_text_packet",
                "",
                "## Release Readiness",
                "",
                "- [x] Documentation updated.",
                "- [x] No release blockers remain.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class LoopPacketTests(TestCase):
    def assert_local_safety_flags_false(self, record: dict[str, object]) -> None:
        for flag in (
            "creates_remote",
            "executed",
            "requires_network",
            "requires_token",
            "safe_to_auto_run",
        ):
            self.assertIn(flag, record)
            self.assertFalse(record[flag], f"{flag} should be false for {record}")

    def test_builder_emits_local_deterministic_packet(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_loop_feature_bundle(root)

            packet = build_loop_packet(root, deadline="2026-05-20")
            rebuilt_packet = build_loop_packet(root, deadline="2026-05-20")
            first_json = render_loop_packet_json(packet)
            second_json = render_loop_packet_json(rebuilt_packet)
            text = render_loop_packet_text(packet)
            rebuilt_text = render_loop_packet_text(rebuilt_packet)

            self.assertEqual(first_json, second_json)
            self.assertEqual(text, rebuilt_text)
            self.assertEqual(packet["root"], str(root.resolve()))
            self.assertEqual(packet["deadline"], "2026-05-20")
            self.assertIn("agent-loop-packet", [feature["slug"] for feature in packet["core_features"]])
            self.assertEqual(packet["summary"]["features_total"], 1)
            self.assertEqual(packet["summary"]["features_ready"], 1)
            self.assertIn("context_commands", packet)
            self.assertIn("lifecycle_steps", packet)
            self.assertIn("subagents", packet)
            self.assertIn("validation_commands", packet)
            self.assertIn("safety_notes", packet)
            self.assertIn("upstreams", packet)
            self.assertIn("recommended_commands", packet)
            self.assertNotIn("adapters", packet)
            self.assertIn("## Core Features", text)

    def test_packet_command_and_subagent_safety_flags_are_false(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_loop_feature_bundle(root)

            packet = build_loop_packet(root)

            for command in packet["context_commands"]:
                self.assert_local_safety_flags_false(command)
            for command in packet["validation_commands"]:
                self.assert_local_safety_flags_false(command)
            for step in packet["lifecycle_steps"]:
                for command in step["commands"]:
                    self.assert_local_safety_flags_false(command)
            for subagent in packet["subagents"]:
                self.assert_local_safety_flags_false(subagent["safety"])

    def test_builder_does_not_probe_adapters(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            def guarded_status_builder(path: Path, **kwargs: object) -> dict[str, object]:
                self.assertFalse(kwargs["include_adapters"])
                self.assertIn("adapter_probe", kwargs)
                return build_status(path, **kwargs)

            packet = build_loop_packet(root, status_builder=guarded_status_builder)

            self.assertEqual(packet["summary"]["features_total"], 0)

    def test_cli_text_output_includes_main_sections_and_deadline(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_loop_feature_bundle(root)
            stdout = StringIO()

            with redirect_stdout(stdout):
                code = main(
                    [
                        "loop",
                        "packet",
                        str(root),
                        "--deadline",
                        "2026-05-22",
                    ]
                )

            text = stdout.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("# SpecSpine Agent Loop Packet", text)
            self.assertIn("Deadline: 2026-05-22", text)
            for section in (
                "## Summary",
                "## Core Features",
                "## Context Commands",
                "## Lifecycle Steps",
                "## Subagents",
                "## Validation Commands",
                "## Safety Notes",
                "## Upstreams",
                "## Recommended Commands",
            ):
                self.assertIn(section, text)

    def test_cli_json_output_writes_text_packet(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_loop_feature_bundle(root)
            output = root / "packet.md"
            stdout = StringIO()

            with redirect_stdout(stdout):
                code = main(
                    [
                        "loop",
                        "packet",
                        str(root),
                        "--json",
                        "--output",
                        str(output),
                        "--deadline",
                        "Friday",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            written_text = output.read_text(encoding="utf-8")
            self.assertEqual(code, 0)
            self.assertEqual(payload["deadline"], "Friday")
            self.assertEqual(payload["root"], str(root.resolve()))
            self.assertIn("# SpecSpine Agent Loop Packet", written_text)
            self.assertIn("Deadline: Friday", written_text)
            self.assertNotIn("Wrote loop packet", stdout.getvalue())

    def test_cli_output_refuses_existing_file_without_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = root / "packet.md"
            output.write_text("existing\n", encoding="utf-8")
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(["loop", "packet", str(root), "--output", str(output)])

            self.assertEqual(code, 1)
            self.assertEqual(output.read_text(encoding="utf-8"), "existing\n")
            self.assertIn("Output file already exists", stderr.getvalue())

    def test_cli_output_confirmation_without_json_and_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = root / "packet.md"
            output.write_text("existing\n", encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                code = main(["loop", "packet", str(root), "--output", str(output), "--force"])

            self.assertEqual(code, 0)
            self.assertIn("Wrote loop packet to", stdout.getvalue())
            self.assertIn("# SpecSpine Agent Loop Packet", output.read_text(encoding="utf-8"))

    def test_cli_packet_is_token_free_and_does_not_invoke_subprocesses(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            token = "FAKE_SECRET_TOKEN_VALUE"

            with patch.dict(os.environ, {"GITHUB_TOKEN": token}), patch.object(
                subprocess,
                "run",
                side_effect=AssertionError("loop packet must not invoke subprocesses"),
            ), redirect_stdout(stdout):
                code = main(["loop", "packet", str(root), "--json"])

            self.assertEqual(code, 0)
            self.assertNotIn(token, stdout.getvalue())
            payload = json.loads(stdout.getvalue())
            self.assertNotIn("adapters", payload)
            self.assertTrue(
                any(
                    "does not call GitHub APIs" in note
                    for note in payload["safety_notes"]
                )
            )
