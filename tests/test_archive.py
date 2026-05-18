import json
import os
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.archive import build_feature_archive_report
from specspine.cli import main
from specspine.workspace import init_workspace


def write_archive_feature_bundle(
    root: Path,
    slug: str = "feature-archive-package",
    *,
    status: str = "validated",
) -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "tests" / "test_archive_feature.py").write_text(
        "# local archive coverage target\n",
        encoding="utf-8",
    )
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Feature archive package",
                "",
                f"Feature ID: {slug}",
                "Priority: high",
                "Owner: Platform Team",
                "Milestone: 2026.5",
                "Target Release: 2026.5",
                "Project: Native feature bundles",
                "Effort: M",
                f"Status: {status}",
                "",
                "## Why",
                "",
                "Preserve durable closure evidence before lifecycle archiving.",
                "",
                "## Acceptance Criteria",
                "",
                "- [x] Archive reports include status, readiness, trace, tasks, tests, and source file evidence.",
                "- [x] Archive packages write only to an explicit output directory with overwrite protection.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Feature archive package Execution",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "",
                "## Tasks",
                "",
                "- [x] Build archive evidence report.",
                "- [x] Write optional local archive package artifacts.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Feature archive package Quality",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "",
                "## Required Checks",
                "",
                "- [x] Unit tests cover JSON, text, output directories, conflicts, invalid slugs, and missing features.",
                "- [x] Archive mode does not call remote services or write files without an output directory.",
                "",
                "## Test Coverage",
                "",
                "- [x] AC001 -> tests/test_archive_feature.py",
                "- [x] AC002 -> tests/test_archive_feature.py",
                "",
                "## Test Plan",
                "",
                "- Run `PYTHONPATH=src python3 -m unittest tests.test_archive`.",
                "",
                "## Review Notes",
                "",
                "- Archive package evidence is composed from existing local feature reports.",
                "",
                "## Release Readiness",
                "",
                "- [x] Readiness evidence is complete.",
                "- [x] Documentation and tests are updated.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


def workspace_snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class FeatureArchiveTests(TestCase):
    def test_archive_json_shape_uses_existing_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_archive_feature_bundle(root)

            code, stdout, stderr = run_cli(
                [
                    "feature",
                    "archive",
                    "feature-archive-package",
                    str(root),
                    "--json",
                    "--archive-id",
                    "2026-05-18-feature-archive-package",
                ]
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(
                payload["archive_id"],
                "2026-05-18-feature-archive-package",
            )
            self.assertEqual(payload["feature_id"], "feature-archive-package")
            self.assertEqual(payload["status"], "validated")
            self.assertTrue(payload["ready"])
            self.assertTrue(payload["coverage_required"])
            self.assertEqual(payload["metadata"]["project"], "Native feature bundles")
            self.assertEqual(payload["summary"]["source_files"]["total"], 3)
            self.assertEqual(payload["summary"]["test_coverage"]["total"], 2)
            self.assertIn("ready_report", payload)
            self.assertIn("trace_report", payload)
            self.assertIn("tasks_report", payload)
            self.assertIn("tests_report", payload)
            self.assertIn(
                "specspine feature status feature-archive-package . --set archived --enforce-transition --json",
                payload["recommended_commands"],
            )

    def test_archive_text_output_includes_closure_command(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_archive_feature_bundle(root, status="implemented")

            code, stdout, stderr = run_cli(
                [
                    "feature",
                    "archive",
                    "feature-archive-package",
                    str(root),
                    "--archive-id",
                    "stable-archive",
                ]
            )

            self.assertEqual(code, 0, stderr)
            self.assertIn("# Feature Archive Package Plan: feature-archive-package", stdout)
            self.assertIn("- Archive ID: stable-archive", stdout)
            self.assertIn("- Ready: yes", stdout)
            self.assertIn(
                "specspine feature status feature-archive-package . --set archived --enforce-transition --json",
                stdout,
            )

    def test_archive_output_dir_writes_package_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_archive_feature_bundle(root)
            output_dir = root / ".specspine" / "archive" / "feature-archive-package"

            code, stdout, stderr = run_cli(
                [
                    "feature",
                    "archive",
                    "feature-archive-package",
                    str(root),
                    "--json",
                    "--output-dir",
                    str(output_dir),
                    "--archive-id",
                    "2026-05-18-feature-archive-package",
                ]
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["package"]["output_dir"], str(output_dir))
            self.assertTrue((output_dir / "README.md").exists())
            self.assertTrue((output_dir / "archive.json").exists())
            self.assertTrue((output_dir / "sources" / "spec.md").exists())
            self.assertTrue((output_dir / "sources" / "execution.md").exists())
            self.assertTrue((output_dir / "sources" / "quality.md").exists())
            archived_payload = json.loads(
                (output_dir / "archive.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                archived_payload["archive_id"],
                "2026-05-18-feature-archive-package",
            )
            self.assertIn(
                "Feature ID: feature-archive-package",
                (output_dir / "sources" / "spec.md").read_text(encoding="utf-8"),
            )

    def test_archive_output_dir_conflict_requires_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_archive_feature_bundle(root)
            output_dir = root / "archive-output"

            first_code, _stdout, first_stderr = run_cli(
                [
                    "feature",
                    "archive",
                    "feature-archive-package",
                    str(root),
                    "--output-dir",
                    str(output_dir),
                ]
            )
            self.assertEqual(first_code, 0, first_stderr)

            second_code, _stdout, second_stderr = run_cli(
                [
                    "feature",
                    "archive",
                    "feature-archive-package",
                    str(root),
                    "--output-dir",
                    str(output_dir),
                ]
            )
            self.assertEqual(second_code, 1)
            self.assertIn("already exist", second_stderr)

            forced_code, _stdout, forced_stderr = run_cli(
                [
                    "feature",
                    "archive",
                    "feature-archive-package",
                    str(root),
                    "--output-dir",
                    str(output_dir),
                    "--force",
                ]
            )
            self.assertEqual(forced_code, 0, forced_stderr)

    def test_archive_invalid_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, _stdout, stderr = run_cli(
                ["feature", "archive", "Bad_Slug", str(root), "--json"]
            )

            self.assertEqual(code, 2)
            self.assertIn("Invalid feature slug", stderr)

    def test_archive_missing_feature_returns_one(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, _stdout, stderr = run_cli(
                ["feature", "archive", "missing-feature", str(root), "--json"]
            )

            self.assertEqual(code, 1)
            self.assertIn("No feature files found", stderr)
            self.assertIn("specs/features/missing-feature.md", stderr)

    def test_archive_report_only_is_read_only_and_does_not_use_external_calls(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_archive_feature_bundle(root, status="implemented")
            before = workspace_snapshot(root)

            with patch("subprocess.run", side_effect=AssertionError("unexpected process")):
                with patch.dict(os.environ, {"GITHUB_TOKEN": "do-not-read"}):
                    code, stdout, stderr = run_cli(
                        [
                            "feature",
                            "archive",
                            "feature-archive-package",
                            str(root),
                            "--json",
                        ]
                    )

            self.assertEqual(code, 0, stderr)
            self.assertTrue(json.loads(stdout)["ready"])
            self.assertEqual(workspace_snapshot(root), before)

    def test_archive_module_report_is_reusable(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_archive_feature_bundle(root)

            report = build_feature_archive_report(
                root,
                "feature-archive-package",
                archive_id="module-test",
            )

            self.assertEqual(report.archive_id, "module-test")
            self.assertEqual(report.status, "validated")
            self.assertTrue(report.ready)
