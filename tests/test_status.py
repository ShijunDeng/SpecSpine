import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.adapters import ADAPTER_SPECS, AdapterStatus
from specspine.cli import main
from specspine.fusion import init_fusion_workspace
from specspine.status import build_status, render_status_text
from specspine.workspace import init_workspace


def write_status_feature_bundle(
    root: Path,
    slug: str = "add-dark-mode",
    *,
    status: str = "validated",
    include_quality: bool = True,
    open_task: bool = False,
) -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Add dark mode",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "",
                "## Acceptance Criteria",
                "",
                "- [x] Users can enable dark mode.",
                "- [x] Users can return to light mode.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    task_marker = " " if open_task else "x"
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Add dark mode Execution",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "",
                "## Tasks",
                "",
                "- [x] Implement theme storage.",
                f"- [{task_marker}] Add theme tests.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    if include_quality:
        (root / "quality" / "features" / f"{slug}.md").write_text(
            "\n".join(
                [
                    "# Add dark mode Quality",
                    "",
                    f"Feature ID: {slug}",
                    f"Status: {status}",
                    "",
                    "## Required Checks",
                    "",
                    "- [x] Unit tests pass.",
                    "- [x] Documentation updated.",
                    "",
                    "## Test Plan",
                    "",
                    "- Run `python -m unittest`.",
                    "",
                    "## Release Readiness",
                    "",
                    "- [x] Reviewer gate passes.",
                    "- [x] No release blockers remain.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )


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


def fake_available_adapter_probe(keys: list[str]) -> list[AdapterStatus]:
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
            write_status_feature_bundle(root)
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
            self.assertNotIn("validation", payload)
            self.assertNotIn("feature_summaries", payload)

    def test_status_json_cli_can_include_feature_summaries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--json", "--feature-summaries"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertIn("feature_summaries", payload)
            self.assertEqual(len(payload["feature_summaries"]), 1)
            summary = payload["feature_summaries"][0]
            self.assertEqual(
                set(summary),
                {
                    "blocking_checks",
                    "complete",
                    "feature_id",
                    "gaps",
                    "missing_files",
                    "next_actions",
                    "ready",
                    "ready_summary",
                    "recommended_commands",
                    "slug",
                    "status",
                    "tasks_summary",
                },
            )
            self.assertEqual(summary["feature_id"], "add-dark-mode")
            self.assertEqual(summary["slug"], "add-dark-mode")
            self.assertEqual(summary["status"], "validated")
            self.assertTrue(summary["complete"])
            self.assertTrue(summary["ready"])
            self.assertEqual(summary["missing_files"], [])
            self.assertEqual(summary["tasks_summary"], {"done": 2, "open": 0, "total": 2})
            self.assertEqual(summary["ready_summary"], {"fail": 0, "pass": 9, "total": 9})
            self.assertEqual(summary["gaps"], 0)
            self.assertEqual(summary["blocking_checks"], 0)
            self.assertEqual(
                summary["next_actions"],
                ["Review, merge, or archive the ready feature bundle."],
            )
            self.assertIn(
                "specspine feature handoff add-dark-mode . --json",
                summary["recommended_commands"],
            )

    def test_status_json_cli_validate_includes_validation_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            output = StringIO()

            def fail_probe(keys: list[str]) -> list[AdapterStatus]:
                raise AssertionError("adapter probe should not run")

            with patch("specspine.cli.probe_adapters", side_effect=fail_probe):
                with redirect_stdout(output):
                    returncode = main(["status", str(root), "--json", "--validate"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertIn("validation", payload)
            validation = payload["validation"]
            self.assertTrue(validation["ok"])
            self.assertIn("summary", validation)
            self.assertIn("failed_checks", validation)
            self.assertEqual(validation["failed_checks"], [])
            self.assertEqual(
                validation["included"],
                {
                    "workspace": True,
                    "fusion": True,
                    "features": True,
                    "adapters": False,
                },
            )

    def test_status_json_cli_validate_preserves_feature_summaries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--validate",
                        "--feature-summaries",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertIn("validation", payload)
            self.assertIn("feature_summaries", payload)
            self.assertEqual(payload["feature_summaries"][0]["slug"], "add-dark-mode")

    def test_status_text_cli_validate_includes_brief_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--validate"])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("Validation:", text)
            self.assertIn("Result: failed", text)
            self.assertIn("Summary: pass=", text)
            self.assertIn("fusion.required_file:.specspine/fusion.yaml", text)
            self.assertNotIn("workspace.required_file:.specspine/spine.yaml", text)
            self.assertNotIn("fusion.integration_mode", text)

    def test_status_text_feature_summaries_are_opt_in(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(root)
            default_output = StringIO()
            summary_output = StringIO()

            with redirect_stdout(default_output):
                default_returncode = main(["status", str(root)])
            with redirect_stdout(summary_output):
                summary_returncode = main(["status", str(root), "--feature-summaries"])

            self.assertEqual(default_returncode, 0)
            self.assertEqual(summary_returncode, 0)
            self.assertNotIn("Feature summaries:", default_output.getvalue())
            text = summary_output.getvalue()
            self.assertIn("Feature summaries:", text)
            self.assertIn("add-dark-mode - status=validated ready=yes tasks=2/0 gaps=0 blocking=0", text)
            self.assertIn("next: Review, merge, or archive the ready feature bundle.", text)

    def test_status_feature_summary_reports_partial_bundle_actions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(
                root,
                status="implemented",
                include_quality=False,
                open_task=True,
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--json", "--feature-summaries"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            summary = payload["feature_summaries"][0]
            self.assertFalse(summary["complete"])
            self.assertFalse(summary["ready"])
            self.assertEqual(summary["tasks_summary"], {"done": 1, "open": 1, "total": 2})
            self.assertIn("quality/features/add-dark-mode.md", summary["missing_files"])
            self.assertGreater(summary["gaps"], 0)
            self.assertGreater(summary["blocking_checks"], 0)
            self.assertTrue(
                any("Add missing peer file(s)" in action for action in summary["next_actions"])
            )

    def test_status_feature_summary_handles_invalid_slug_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
            (root / "specs" / "features" / "BadSlug.md").write_text(
                "# Bad slug\n\nFeature ID: BadSlug\nStatus: proposed\n",
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--json", "--feature-summaries"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            summary = payload["feature_summaries"][0]
            self.assertEqual(summary["slug"], "BadSlug")
            self.assertEqual(summary["status"], "invalid")
            self.assertFalse(summary["ready"])
            self.assertEqual(summary["blocking_checks"], 1)
            self.assertIn("Invalid feature slug", summary["next_actions"][0])

    def test_status_validate_reports_failed_checks_but_returns_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            (root / "quality" / "checklist.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--json", "--validate"])

            payload = json.loads(output.getvalue())
            failed_ids = {
                check["id"]
                for check in payload["validation"]["failed_checks"]
            }
            self.assertEqual(returncode, 0)
            self.assertFalse(payload["validation"]["ok"])
            self.assertIn("workspace.required_file:quality/checklist.md", failed_ids)
            self.assertNotIn("fusion.integration_mode", failed_ids)
            for check in payload["validation"]["failed_checks"]:
                self.assertEqual(check["status"], "fail")
                self.assertGreaterEqual(
                    set(check),
                    {"id", "message", "severity", "status"},
                )

    def test_status_validate_with_adapters_uses_mock_probe(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            output = StringIO()
            probed: list[str] = []

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

            def fake_probe(keys: list[str]) -> list[AdapterStatus]:
                probed.extend(keys)
                return fake_available_adapter_probe(keys)

            with patch(
                "specspine.cli.build_status",
                side_effect=build_status_with_fake_probe,
            ), patch("specspine.cli.probe_adapters", side_effect=fake_probe):
                with redirect_stdout(output):
                    returncode = main(
                        ["status", str(root), "--adapters", "--json", "--validate"]
                    )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(sorted(probed), ["openspec", "speckit", "superpowers"])
            self.assertIn("adapters", payload)
            self.assertTrue(payload["validation"]["included"]["adapters"])
            self.assertEqual(payload["validation"]["summary"]["fail"], 0)

    def test_status_validate_with_adapters_preserves_feature_summaries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            write_status_feature_bundle(root)
            output = StringIO()
            probed: list[str] = []

            def build_status_with_fake_probe(
                path: Path,
                *,
                include_adapters: bool = False,
                include_feature_summaries: bool = False,
            ) -> dict[str, object]:
                return build_status(
                    path,
                    include_adapters=include_adapters,
                    include_feature_summaries=include_feature_summaries,
                    adapter_probe=fake_available_adapters,
                )

            def fake_probe(keys: list[str]) -> list[AdapterStatus]:
                probed.extend(keys)
                return fake_available_adapter_probe(keys)

            with patch(
                "specspine.cli.build_status",
                side_effect=build_status_with_fake_probe,
            ), patch("specspine.cli.probe_adapters", side_effect=fake_probe):
                with redirect_stdout(output):
                    returncode = main(
                        [
                            "status",
                            str(root),
                            "--adapters",
                            "--json",
                            "--validate",
                            "--feature-summaries",
                        ]
                    )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(sorted(probed), ["openspec", "speckit", "superpowers"])
            self.assertIn("adapters", payload)
            self.assertIn("validation", payload)
            self.assertTrue(payload["validation"]["included"]["adapters"])
            self.assertIn("feature_summaries", payload)
            self.assertEqual(len(payload["feature_summaries"]), 1)
            self.assertEqual(payload["feature_summaries"][0]["slug"], "add-dark-mode")

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
            self.assertNotIn("validation", payload)
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
            self.assertNotIn("Feature summaries:", text)

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
