import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.adapters import AdapterStatus
from specspine.cli import main
from specspine.fusion import init_fusion_workspace
from specspine.status import build_status, render_status_text
from specspine.workspace import init_workspace


def fake_available_adapters() -> list[AdapterStatus]:
    return [
        AdapterStatus(
            key="openspec",
            display_name="OpenSpec",
            available=True,
            detail="fake openspec available",
            version="1.0.0",
            command="openspec",
            install_hint="install openspec",
            upstream_url="https://example.test/openspec",
        ),
        AdapterStatus(
            key="speckit",
            display_name="Spec Kit",
            available=True,
            detail="fake speckit available",
            version="2.0.0",
            command="specify",
            install_hint="install speckit",
            upstream_url="https://example.test/speckit",
        ),
        AdapterStatus(
            key="superpowers",
            display_name="Superpowers",
            available=True,
            detail="fake superpowers available",
            version="3.0.0",
            command=None,
            install_hint="install superpowers",
            upstream_url="https://example.test/superpowers",
        ),
    ]


class StatusTests(TestCase):
    def test_status_for_plain_workspace_does_not_probe_adapters(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            def fail_probe() -> list[AdapterStatus]:
                raise AssertionError("adapter probe should not run")

            status = build_status(root, adapter_probe=fail_probe)

            self.assertTrue(status["workspace"]["complete"])
            self.assertFalse(status["fusion"]["complete"])
            self.assertNotIn("adapters", status)
            self.assertFalse(status["upstreams"]["openspec"]["enabled"])

    def test_plain_workspace_recommendations_point_to_fuse(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            status = build_status(root)

            self.assertTrue(status["workspace"]["complete"])
            self.assertFalse(status["fusion"]["complete"])
            self.assertTrue(
                any("specspine fuse" in item for item in status["recommendations"])
            )
            self.assertFalse(
                any("compact context packet" in item for item in status["recommendations"])
            )

    def test_status_for_fusion_workspace_records_enabled_upstreams(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex", include_speckit=False)

            status = build_status(root)

            self.assertTrue(status["workspace"]["complete"])
            self.assertTrue(status["fusion"]["complete"])
            self.assertTrue(status["upstreams"]["openspec"]["enabled"])
            self.assertFalse(status["upstreams"]["speckit"]["enabled"])
            self.assertTrue(status["upstreams"]["superpowers"]["enabled"])
            self.assertTrue(status["artifacts"][".specspine/fusion.yaml"]["exists"])

    def test_status_json_cli_output_is_parseable(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["root"], str(root.resolve()))
            self.assertTrue(payload["workspace"]["complete"])
            self.assertIn("artifacts", payload)
            self.assertIn("recommendations", payload)
            self.assertNotIn("adapters", payload)

    def test_status_json_cli_output_can_include_adapter_probe_results(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            output = StringIO()

            def build_status_with_fake_probe(
                path: Path,
                *,
                include_adapters: bool = False,
            ) -> dict[str, object]:
                return build_status(
                    path,
                    include_adapters=include_adapters,
                    adapter_probe=fake_available_adapters,
                )

            with patch(
                "specspine.cli.build_status",
                side_effect=build_status_with_fake_probe,
            ):
                with redirect_stdout(output):
                    returncode = main(["status", str(root), "--adapters", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertIn("adapters", payload)
            self.assertEqual(
                sorted(payload["adapters"]),
                ["openspec", "speckit", "superpowers"],
            )
            self.assertTrue(payload["adapters"]["openspec"]["available"])
            self.assertTrue(payload["adapters"]["speckit"]["available"])
            self.assertTrue(payload["adapters"]["superpowers"]["available"])

    def test_status_reports_missing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            (root / "quality" / "checklist.md").unlink()

            status = build_status(root)

            self.assertFalse(status["workspace"]["complete"])
            self.assertFalse(status["fusion"]["complete"])
            self.assertIn("quality/checklist.md", status["workspace"]["missing"])
            self.assertFalse(status["artifacts"]["quality/checklist.md"]["exists"])
            self.assertTrue(
                any("specspine init" in item for item in status["recommendations"])
            )

    def test_status_text_includes_required_sections(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            text = render_status_text(build_status(root))

            self.assertIn("Workspace: complete", text)
            self.assertIn("Fusion: incomplete", text)
            self.assertIn("Artifacts:", text)
            self.assertIn("Enabled upstreams:", text)
            self.assertIn("Recommended next actions:", text)

    def test_fusion_workspace_with_available_adapters_recommends_context_packet(
        self,
    ) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")

            status = build_status(
                root,
                include_adapters=True,
                adapter_probe=fake_available_adapters,
            )

            self.assertTrue(status["fusion"]["complete"])
            self.assertEqual(
                status["recommendations"],
                [
                    "Use `specspine status --json` as the compact context packet for agents."
                ],
            )

    def test_status_can_include_adapter_probe_results(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")

            def fake_probe() -> list[AdapterStatus]:
                return [
                    AdapterStatus(
                        key="openspec",
                        display_name="OpenSpec",
                        available=True,
                        detail="fake openspec",
                        version="1.0.0",
                        command="openspec",
                        install_hint="install openspec",
                        upstream_url="https://example.test/openspec",
                    ),
                    AdapterStatus(
                        key="speckit",
                        display_name="Spec Kit",
                        available=False,
                        detail="fake speckit missing",
                        version=None,
                        command="specify",
                        install_hint="install speckit",
                        upstream_url="https://example.test/speckit",
                    ),
                ]

            status = build_status(root, include_adapters=True, adapter_probe=fake_probe)

            self.assertIn("adapters", status)
            self.assertTrue(status["adapters"]["openspec"]["available"])
            self.assertFalse(status["adapters"]["speckit"]["available"])
            self.assertTrue(
                any("Install Spec Kit" in item for item in status["recommendations"])
            )
