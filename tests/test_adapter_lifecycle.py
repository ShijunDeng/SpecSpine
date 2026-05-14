import json
import os
import shutil
import socket
import stat
import subprocess
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.adapters import build_adapter_lifecycle_report
from specspine.cli import main
from specspine.features import build_feature_ready_report
from specspine.fusion import init_fusion_workspace
from specspine.validation import build_validation_report
from specspine.workspace import init_workspace


REPO_ROOT = Path(__file__).resolve().parents[1]
NATIVE_STATUSES = (
    "proposed",
    "planned",
    "in-progress",
    "implemented",
    "validated",
    "archived",
)


class AdapterLifecycleTests(TestCase):
    def test_lifecycle_json_shape_for_fused_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex", include_speckit=False)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["adapters", "lifecycle", str(root), "--json"])

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                set(payload),
                {
                    "adapters",
                    "native_statuses",
                    "recommended_commands",
                    "root",
                    "summary",
                },
            )
            self.assertEqual(payload["root"], str(root.resolve()))
            self.assertEqual(tuple(payload["native_statuses"]), NATIVE_STATUSES)
            self.assertEqual(
                sorted(payload["adapters"]),
                ["openspec", "speckit", "superpowers"],
            )
            self.assertEqual(
                payload["summary"],
                {
                    "adapters_total": 3,
                    "enabled_adapters": 2,
                    "mappings_total": 18,
                    "statuses_total": 6,
                },
            )
            self.assertTrue(payload["adapters"]["openspec"]["enabled"])
            self.assertTrue(payload["adapters"]["openspec"]["config_exists"])
            self.assertFalse(payload["adapters"]["speckit"]["enabled"])
            self.assertTrue(payload["adapters"]["speckit"]["config_exists"])
            self.assertTrue(payload["adapters"]["superpowers"]["enabled"])
            self.assertTrue(payload["adapters"]["superpowers"]["config_exists"])

            for adapter_key, adapter in payload["adapters"].items():
                self.assertEqual(
                    set(adapter),
                    {
                        "config",
                        "config_exists",
                        "display_name",
                        "enabled",
                        "mappings",
                        "upstream_url",
                    },
                )
                mappings = adapter["mappings"]
                self.assertEqual(len(mappings), 6)
                self.assertEqual(
                    [mapping["status"] for mapping in mappings],
                    list(NATIVE_STATUSES),
                )
                self.assertEqual(
                    [mapping["id"] for mapping in mappings],
                    [f"{adapter_key}:{status}" for status in NATIVE_STATUSES],
                )
                for mapping in mappings:
                    self.assertEqual(
                        set(mapping),
                        {
                            "agent_focus",
                            "id",
                            "local_commands",
                            "specspine_meaning",
                            "status",
                            "upstream_artifacts",
                            "upstream_phase",
                        },
                    )
                    self.assertTrue(mapping["specspine_meaning"])
                    self.assertTrue(mapping["upstream_phase"])
                    self.assertTrue(mapping["upstream_artifacts"])
                    self.assertTrue(mapping["agent_focus"])
                    self.assertTrue(mapping["local_commands"])

            self.assertEqual(
                payload["recommended_commands"],
                [
                    "specspine status . --json --validate",
                    "specspine adapters doctor",
                    "specspine validate . --fusion --features",
                ],
            )

    def test_lifecycle_json_for_plain_workspace_keeps_mappings_without_enabled_configs(
        self,
    ) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["adapters", "lifecycle", str(root), "--json"])

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["summary"]["mappings_total"], 18)
            self.assertEqual(payload["summary"]["enabled_adapters"], 0)
            for adapter in payload["adapters"].values():
                self.assertFalse(adapter["enabled"])
                self.assertFalse(adapter["config_exists"])
                self.assertEqual(len(adapter["mappings"]), 6)

    def test_lifecycle_json_reports_missing_config_without_failing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            (root / ".specspine" / "adapters" / "superpowers.md").unlink()

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["adapters", "lifecycle", str(root), "--json"])

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["adapters"]["superpowers"]["enabled"])
            self.assertFalse(payload["adapters"]["superpowers"]["config_exists"])
            self.assertEqual(len(payload["adapters"]["superpowers"]["mappings"]), 6)

    def test_lifecycle_text_includes_adapter_names_ids_statuses_and_phases(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["adapters", "lifecycle", str(root)])

            text = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("Adapter lifecycle mappings:", text)
            self.assertIn("Summary: adapters=3 enabled=3 statuses=6 mappings=18", text)
            self.assertIn("OpenSpec", text)
            self.assertIn("Enabled: yes", text)
            self.assertIn("Config: .specspine/adapters/openspec.md (exists: yes)", text)
            self.assertIn("openspec:proposed proposed -> Change proposal drafted", text)
            self.assertIn("Spec Kit", text)
            self.assertIn("Config: .specspine/adapters/speckit.md (exists: yes)", text)
            self.assertIn("speckit:planned planned -> Plan phase", text)
            self.assertIn("Superpowers", text)
            self.assertIn("Config: .specspine/adapters/superpowers.md (exists: yes)", text)
            self.assertIn(
                "superpowers:validated validated -> Verification before completion",
                text,
            )
            self.assertIn("Recommended commands:", text)
            self.assertIn("- specspine status . --json --validate", text)
            self.assertIn("- specspine adapters doctor", text)
            self.assertIn("- specspine validate . --fusion --features", text)

    def test_lifecycle_reads_only_fusion_config_and_skips_external_tools(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            token_file = root / "token.txt"
            token_file.write_text("not-a-real-token\n", encoding="utf-8")
            bin_dir = root / "bin"
            bin_dir.mkdir()
            sentinel = root / "gh-called"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                f"#!/bin/sh\ntouch {sentinel}\nexit 99\n",
                encoding="utf-8",
            )
            gh_path.chmod(gh_path.stat().st_mode | stat.S_IXUSR)

            fusion_path = (root / ".specspine" / "fusion.yaml").resolve()
            original_read_text = Path.read_text
            read_paths: list[Path] = []

            def tracked_read_text(path: Path, *args: object, **kwargs: object) -> str:
                resolved = path.resolve()
                read_paths.append(resolved)
                if resolved != fusion_path:
                    raise AssertionError(f"unexpected file read: {path}")
                return original_read_text(path, *args, **kwargs)

            stdout = StringIO()
            with (
                patch.object(Path, "read_text", autospec=True, side_effect=tracked_read_text),
                patch.object(Path, "read_bytes", side_effect=AssertionError("Path.read_bytes should not be called")),
                patch.object(subprocess, "run", side_effect=AssertionError("subprocess.run should not be called")),
                patch.object(subprocess, "call", side_effect=AssertionError("subprocess.call should not be called")),
                patch.object(subprocess, "Popen", side_effect=AssertionError("subprocess.Popen should not be called")),
                patch.object(subprocess, "check_call", side_effect=AssertionError("subprocess.check_call should not be called")),
                patch.object(subprocess, "check_output", side_effect=AssertionError("subprocess.check_output should not be called")),
                patch.object(shutil, "which", side_effect=AssertionError("shutil.which should not be called")),
                patch.object(socket, "create_connection", side_effect=AssertionError("network should not be called")),
                patch.object(socket, "socket", side_effect=AssertionError("socket should not be called")),
                patch.object(os, "system", side_effect=AssertionError("os.system should not be called")),
                patch.dict(os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}),
                redirect_stdout(stdout),
            ):
                exit_code = main(["adapters", "lifecycle", str(root), "--json"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(read_paths, [fusion_path])
            self.assertFalse(sentinel.exists())
            token_prefix = "gh" + "p_"
            self.assertFalse(token_file.read_text(encoding="utf-8").startswith(token_prefix))

    def test_adapter_lifecycle_mappings_dogfood_bundle_passes_readiness_and_validation(
        self,
    ) -> None:
        report = build_adapter_lifecycle_report(REPO_ROOT)
        readiness = build_feature_ready_report(REPO_ROOT, "adapter-lifecycle-mappings")
        validation = build_validation_report(
            REPO_ROOT,
            include_fusion=True,
            include_features=True,
        )

        self.assertEqual(report.summary["mappings_total"], 18)
        self.assertTrue(readiness.ready)
        self.assertEqual(readiness.status, "validated")
        self.assertEqual(validation["summary"]["fail"], 0)
