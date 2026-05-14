import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.adapters import ADAPTER_SPECS, AdapterStatus
from specspine.cli import main
from specspine.fusion import init_fusion_workspace
from specspine.validation import (
    build_validation_report,
    render_validation_json,
    validation_exit_code,
)
from specspine.workspace import init_workspace


def fake_missing_adapters(keys: list[str]) -> list[AdapterStatus]:
    return [
        AdapterStatus(
            key=key,
            display_name=ADAPTER_SPECS[key].display_name,
            available=False,
            detail=f"fake {key} missing",
            version=None,
            command=ADAPTER_SPECS[key].command,
            install_hint=ADAPTER_SPECS[key].install_hint,
            upstream_url=ADAPTER_SPECS[key].upstream_url,
        )
        for key in keys
    ]


class ValidationTests(TestCase):
    def test_basic_workspace_validation_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            report = build_validation_report(root)

            self.assertTrue(report["ok"])
            self.assertEqual(report["summary"]["fail"], 0)
            self.assertTrue(
                any(
                    check["id"] == "workspace.required_file:.specspine/spine.yaml"
                    and check["status"] == "pass"
                    for check in report["checks"]
                )
            )
            self.assertFalse(
                any(check["id"].startswith("fusion.") for check in report["checks"])
            )

    def test_missing_workspace_file_fails_validation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            (root / "quality" / "checklist.md").unlink()

            report = build_validation_report(root)

            self.assertFalse(report["ok"])
            self.assertEqual(validation_exit_code(report), 1)
            self.assertTrue(
                any(
                    check["id"] == "workspace.required_file:quality/checklist.md"
                    and check["status"] == "fail"
                    for check in report["checks"]
                )
            )

    def test_fusion_workspace_validation_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")

            report = build_validation_report(root, include_fusion=True)

            self.assertTrue(report["ok"])
            self.assertEqual(report["summary"]["fail"], 0)
            self.assertTrue(
                any(
                    check["id"] == "fusion.integration_mode"
                    and check["status"] == "pass"
                    for check in report["checks"]
                )
            )
            self.assertTrue(
                any(
                    check["id"] == "fusion.adapter_boundary:openspec"
                    and check["status"] == "pass"
                    for check in report["checks"]
                )
            )

    def test_plain_workspace_fusion_validation_requires_fusion_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--fusion", "--json"])

            payload = json.loads(output.getvalue())
            failing_fusion_checks = {
                check["id"]
                for check in payload["checks"]
                if check["status"] == "fail"
                and check["id"].startswith("fusion.required_file:")
            }
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ok"])
            self.assertIn(
                "fusion.required_file:.specspine/fusion.yaml",
                failing_fusion_checks,
            )
            self.assertIn(
                "fusion.required_file:.specspine/fusion-map.md",
                failing_fusion_checks,
            )

    def test_vendored_flag_true_fails_fusion_validation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            fusion_yaml = root / ".specspine" / "fusion.yaml"
            fusion_yaml.write_text(
                fusion_yaml.read_text(encoding="utf-8").replace(
                    "vendored_upstream_code: false",
                    "vendored_upstream_code: true",
                ),
                encoding="utf-8",
            )

            report = build_validation_report(root, include_fusion=True)

            self.assertFalse(report["ok"])
            self.assertTrue(
                any(
                    check["id"] == "fusion.vendored_upstream_code"
                    and check["status"] == "fail"
                    for check in report["checks"]
                )
            )

    def test_adapter_docs_without_no_vendored_boundary_fail_validation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            (root / ".specspine" / "adapters" / "openspec.md").write_text(
                "# OpenSpec Adapter\n\nIntegration mode: external CLI.\n",
                encoding="utf-8",
            )

            report = build_validation_report(root, include_fusion=True)

            self.assertFalse(report["ok"])
            self.assertTrue(
                any(
                    check["id"] == "fusion.adapter_boundary:openspec"
                    and check["status"] == "fail"
                    for check in report["checks"]
                )
            )

    def test_adapter_probe_failures_fail_validation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")

            report = build_validation_report(
                root,
                include_fusion=True,
                include_adapters=True,
                adapter_probe=fake_missing_adapters,
            )

            self.assertFalse(report["ok"])
            self.assertEqual(report["summary"]["fail"], 3)
            self.assertTrue(
                any(
                    check["id"] == "adapter.available:openspec"
                    and check["status"] == "fail"
                    for check in report["checks"]
                )
            )

    def test_adapter_validation_skips_disabled_upstreams(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex", include_speckit=False)
            probed: list[str] = []

            def fake_available_adapters(keys: list[str]) -> list[AdapterStatus]:
                probed.extend(keys)
                return [
                    AdapterStatus(
                        key=key,
                        display_name=ADAPTER_SPECS[key].display_name,
                        available=True,
                        detail=f"fake {key} available",
                        version="1.0.0",
                        command=ADAPTER_SPECS[key].command,
                        install_hint=ADAPTER_SPECS[key].install_hint,
                        upstream_url=ADAPTER_SPECS[key].upstream_url,
                    )
                    for key in keys
                ]

            report = build_validation_report(
                root,
                include_fusion=True,
                include_adapters=True,
                adapter_probe=fake_available_adapters,
            )

            self.assertTrue(report["ok"])
            self.assertEqual(validation_exit_code(report), 0)
            self.assertNotIn("speckit", probed)
            self.assertTrue(
                any(
                    check["id"] == "adapter.available:speckit"
                    and check["status"] == "skip"
                    for check in report["checks"]
                )
            )

    def test_validate_json_output_is_parseable_and_returns_zero_on_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--fusion", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["root"], str(root.resolve()))
            self.assertIn("checks", payload)
            self.assertIn("summary", payload)
            for check in payload["checks"]:
                self.assertGreaterEqual(
                    set(check),
                    {"id", "status", "message", "severity"},
                )

    def test_validate_json_output_is_parseable_and_returns_nonzero_on_fail(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            (root / "quality" / "checklist.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ok"])
            self.assertGreater(payload["summary"]["fail"], 0)

    def test_validate_text_output_includes_result_and_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root)])

            self.assertEqual(returncode, 0)
            self.assertIn("Result: ok", output.getvalue())
            self.assertIn("Summary: ", output.getvalue())

    def test_validation_json_renderer_is_stable_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            payload = json.loads(render_validation_json(build_validation_report(root)))

            self.assertTrue(payload["ok"])
            self.assertEqual(payload["summary"]["warn"], 0)
