import json
import os
import shutil
import socket
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.adapters import ADAPTER_LIFECYCLE_MAPPINGS
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


def write_feature_bundle(
    root: Path,
    slug: str = "add-dark-mode",
    *,
    status: str = "validated",
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
                "Priority: high",
                "Owner: Platform Team",
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
                "- [x] Add theme tests.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
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
                "## Test Coverage",
                "",
                "- [x] AC001 -> tests/test_adapter_handoff.py",
                "",
                "## Test Plan",
                "",
                "- Run `python -m unittest`.",
                "",
                "## Review Notes",
                "",
                "- Adapter handoff reviewed.",
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


class AdapterFeatureHandoffTests(TestCase):
    def test_handoff_json_shape_for_fused_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            write_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["adapters", "handoff", "add-dark-mode", str(root), "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(
                set(payload),
                {
                    "adapters",
                    "blocking_checks",
                    "feature_id",
                    "gaps",
                    "missing_files",
                    "ready",
                    "recommended_commands",
                    "root",
                    "source_files",
                    "sources",
                    "status",
                    "summary",
                },
            )
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["status"], "validated")
            self.assertTrue(payload["ready"])
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(payload["gaps"], [])
            self.assertEqual(payload["blocking_checks"], [])
            self.assertEqual(
                payload["source_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            self.assertEqual(
                payload["summary"]["adapters"],
                {"config_exists": 3, "enabled": 3, "total": 3},
            )
            self.assertEqual(payload["summary"]["steps"], {"total": 13})
            self.assertEqual(payload["summary"]["gaps"], {"total": 0})
            self.assertEqual(payload["summary"]["blocking_checks"], {"total": 0})
            self.assertEqual(
                payload["recommended_commands"],
                [
                    "specspine feature handoff add-dark-mode . --json",
                    "specspine adapters lifecycle . --json",
                    "specspine feature ready add-dark-mode . --json",
                    "specspine validate . --fusion --features",
                ],
            )

            for adapter_key, adapter in payload["adapters"].items():
                self.assertEqual(
                    set(adapter),
                    {
                        "agent_focus",
                        "config",
                        "config_exists",
                        "display_name",
                        "enabled",
                        "integration_surface",
                        "key",
                        "local_commands",
                        "native_status",
                        "notes",
                        "recommended_upstream_steps",
                        "upstream_artifacts",
                        "upstream_phase",
                        "upstream_url",
                    },
                )
                self.assertEqual(adapter["key"], adapter_key)
                self.assertEqual(adapter["native_status"], "validated")
                self.assertTrue(adapter["enabled"])
                self.assertTrue(adapter["config_exists"])
                self.assertTrue(adapter["integration_surface"])
                self.assertTrue(adapter["upstream_phase"])
                self.assertTrue(adapter["upstream_artifacts"])
                self.assertTrue(adapter["agent_focus"])
                self.assertTrue(adapter["local_commands"])
                self.assertTrue(adapter["recommended_upstream_steps"])

    def test_handoff_text_output_contains_feature_adapter_steps_and_local_commands(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            write_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["adapters", "handoff", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("# Adapter Feature Handoff: add-dark-mode", text)
            self.assertIn("## Feature", text)
            self.assertIn("- Status: validated", text)
            self.assertIn("- Ready: yes", text)
            self.assertIn("- Summary: adapters=3 enabled=3 config_exists=3 steps=13", text)
            self.assertIn("### OpenSpec (openspec)", text)
            self.assertIn("- Upstream phase: OpenSpec validation and review passed", text)
            self.assertIn("openspec status --json", text)
            self.assertIn("openspec instructions apply --change add-dark-mode --json", text)
            self.assertIn("### Spec Kit (speckit)", text)
            self.assertIn("Spec Kit's Spec phase", text)
            self.assertIn("Spec Kit's Implement phase", text)
            self.assertIn("### Superpowers (superpowers)", text)
            self.assertIn("superpowers.test-driven-development", text)
            self.assertIn("superpowers.verification-before-completion", text)
            self.assertIn("## Recommended Local Commands", text)
            self.assertIn("specspine adapters lifecycle . --json", text)

    def test_output_file_semantics_keep_json_stdout_and_markdown_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            write_feature_bundle(root)
            output_file = root / "reports" / "adapter-handoff.md"
            output_file.parent.mkdir()
            output_file.write_text("existing\n", encoding="utf-8")
            stderr = StringIO()
            stdout = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                returncode = main(
                    [
                        "adapters",
                        "handoff",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("Output file already exists", stderr.getvalue())
            self.assertEqual(output_file.read_text(encoding="utf-8"), "existing\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "adapters",
                        "handoff",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--output",
                        str(output_file),
                        "--force",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertIn("# Adapter Feature Handoff: add-dark-mode", output_file.read_text(encoding="utf-8"))
            self.assertNotIn("Wrote adapter feature handoff", stdout.getvalue())

    def test_current_status_selects_each_adapter_mapping(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")

            for status in NATIVE_STATUSES:
                with self.subTest(status=status):
                    write_feature_bundle(root, status=status)
                    output = StringIO()
                    with redirect_stdout(output):
                        returncode = main(
                            ["adapters", "handoff", "add-dark-mode", str(root), "--json"]
                        )
                    payload = json.loads(output.getvalue())
                    self.assertEqual(returncode, 0)
                    for adapter_key, mappings in ADAPTER_LIFECYCLE_MAPPINGS.items():
                        expected = next(mapping for mapping in mappings if mapping.status == status)
                        adapter = payload["adapters"][adapter_key]
                        self.assertEqual(adapter["native_status"], status)
                        self.assertEqual(adapter["upstream_phase"], expected.upstream_phase)
                        self.assertEqual(adapter["upstream_artifacts"], list(expected.upstream_artifacts))
                        self.assertEqual(adapter["agent_focus"], expected.agent_focus)

    def test_recommended_upstream_steps_are_safe_unexecuted_and_adapter_specific(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            write_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["adapters", "handoff", "add-dark-mode", str(root), "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            for adapter in payload["adapters"].values():
                for step in adapter["recommended_upstream_steps"]:
                    self.assertFalse(step["creates_remote"])
                    self.assertFalse(step["requires_network"])
                    self.assertFalse(step["requires_token"])
                    self.assertFalse(step["safe_to_auto_run"])
                    self.assertFalse(step["executed"])
                    self.assertIn(step["kind"], {"cli-command", "agent-action"})
                    self.assertTrue(step.get("argv") or step.get("instruction"))

            openspec_argvs = payload["adapters"]["openspec"]["recommended_upstream_steps"]
            self.assertIn(
                ["openspec", "status", "--json"],
                [step["argv"] for step in openspec_argvs],
            )
            self.assertIn(
                ["openspec", "instructions", "apply", "--change", "add-dark-mode", "--json"],
                [step["argv"] for step in openspec_argvs],
            )
            self.assertIn(
                ["openspec", "validate", "--all", "--json"],
                [step["argv"] for step in openspec_argvs],
            )

            speckit_step_ids = {
                step["id"]
                for step in payload["adapters"]["speckit"]["recommended_upstream_steps"]
            }
            self.assertEqual(
                speckit_step_ids,
                {"speckit.spec", "speckit.plan", "speckit.tasks", "speckit.implement"},
            )
            superpowers_step_ids = {
                step["id"]
                for step in payload["adapters"]["superpowers"]["recommended_upstream_steps"]
            }
            self.assertIn("superpowers.brainstorming", superpowers_step_ids)
            self.assertIn("superpowers.writing-plans", superpowers_step_ids)
            self.assertIn("superpowers.test-driven-development", superpowers_step_ids)
            self.assertIn("superpowers.subagent-driven-development", superpowers_step_ids)
            self.assertIn("superpowers.requesting-code-review", superpowers_step_ids)
            self.assertIn("superpowers.verification-before-completion", superpowers_step_ids)

    def test_recommended_upstream_step_order_matches_adapter_workflows(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            write_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["adapters", "handoff", "add-dark-mode", str(root), "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(
                [
                    step["id"]
                    for step in payload["adapters"]["speckit"]["recommended_upstream_steps"]
                ],
                ["speckit.spec", "speckit.plan", "speckit.tasks", "speckit.implement"],
            )
            self.assertEqual(
                [
                    step["id"]
                    for step in payload["adapters"]["superpowers"]["recommended_upstream_steps"]
                ],
                [
                    "superpowers.brainstorming",
                    "superpowers.writing-plans",
                    "superpowers.test-driven-development",
                    "superpowers.subagent-driven-development",
                    "superpowers.requesting-code-review",
                    "superpowers.verification-before-completion",
                ],
            )

    def test_partial_bundle_returns_zero_and_records_missing_gaps_blockers(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            write_feature_bundle(root, status="implemented")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["adapters", "handoff", "add-dark-mode", str(root), "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertFalse(payload["ready"])
            self.assertEqual(payload["missing_files"], ["quality/features/add-dark-mode.md"])
            self.assertGreater(payload["summary"]["gaps"]["total"], 0)
            self.assertGreater(payload["summary"]["blocking_checks"]["total"], 0)
            self.assertEqual(payload["adapters"]["openspec"]["native_status"], "implemented")

    def test_missing_bundle_and_invalid_slug_exit_codes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stderr = StringIO()

            with redirect_stderr(stderr):
                missing_returncode = main(["adapters", "handoff", "add-dark-mode", str(root), "--json"])

            self.assertEqual(missing_returncode, 1)
            self.assertIn("No feature files found", stderr.getvalue())

            stderr = StringIO()
            with redirect_stderr(stderr):
                invalid_returncode = main(["adapters", "handoff", "BadSlug", str(root)])

            self.assertEqual(invalid_returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_handoff_does_not_call_subprocess_network_probe_or_read_tokens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            write_feature_bundle(root)
            output = StringIO()
            token_names = {
                "GH_TOKEN",
                "GITHUB_API_TOKEN",
                "GITHUB_PAT",
                "GITHUB_TOKEN",
            }
            environ_type = os.environ.__class__
            original_get = environ_type.get
            original_getitem = environ_type.__getitem__
            original_contains = environ_type.__contains__

            def guarded_get(environ, key, default=None):
                if key in token_names:
                    raise AssertionError(f"token read: {key}")
                return original_get(environ, key, default)

            def guarded_getitem(environ, key):
                if key in token_names:
                    raise AssertionError(f"token read: {key}")
                return original_getitem(environ, key)

            def guarded_contains(environ, key):
                if key in token_names:
                    raise AssertionError(f"token read: {key}")
                return original_contains(environ, key)

            with patch.dict(
                "os.environ",
                {
                    "GH_TOKEN": "secret-gh-token",
                    "GITHUB_API_TOKEN": "secret-github-api-token",
                    "GITHUB_PAT": "secret-github-pat",
                    "GITHUB_TOKEN": "secret-github-token",
                    "PATH": "",
                },
            ):
                with (
                    patch.object(environ_type, "get", guarded_get),
                    patch.object(environ_type, "__getitem__", guarded_getitem),
                    patch.object(environ_type, "__contains__", guarded_contains),
                    patch("specspine.cli.probe_adapters", side_effect=AssertionError("probe called")),
                    patch("specspine.adapters.probe_adapters", side_effect=AssertionError("probe called")),
                    patch.object(subprocess, "run", side_effect=AssertionError("subprocess called")),
                    patch.object(subprocess, "Popen", side_effect=AssertionError("subprocess called")),
                    patch.object(subprocess, "call", side_effect=AssertionError("subprocess called")),
                    patch.object(subprocess, "check_call", side_effect=AssertionError("subprocess called")),
                    patch.object(subprocess, "check_output", side_effect=AssertionError("subprocess called")),
                    patch.object(shutil, "which", side_effect=AssertionError("tool probe called")),
                    patch.object(os, "system", side_effect=AssertionError("os.system called")),
                    patch.object(socket, "create_connection", side_effect=AssertionError("network called")),
                    patch.object(socket, "socket", side_effect=AssertionError("network called")),
                    redirect_stdout(output),
                ):
                    returncode = main(["adapters", "handoff", "add-dark-mode", str(root), "--json"])

            self.assertEqual(returncode, 0)
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-api-token", output.getvalue())
            self.assertNotIn("secret-github-pat", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())

    def test_adapter_feature_handoff_dogfood_bundle_passes_readiness_and_validation(self) -> None:
        readiness = build_feature_ready_report(REPO_ROOT, "adapter-feature-handoff")
        validation = build_validation_report(
            REPO_ROOT,
            include_fusion=True,
            include_features=True,
        )

        self.assertTrue(readiness.ready)
        self.assertEqual(readiness.status, "validated")
        self.assertEqual(validation["summary"]["fail"], 0)
