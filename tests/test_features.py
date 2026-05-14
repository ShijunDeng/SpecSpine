import json
import os
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.features import (
    FEATURE_STATUSES,
    FeatureBundleExistsError,
    InvalidFeatureSlug,
    build_issue_draft,
    build_feature_tasks_report,
    create_feature_bundle,
    parse_feature_tasks,
    set_feature_status,
)
from specspine.status import build_status
from specspine.validation import build_validation_report, validation_exit_code
from specspine.workspace import init_workspace


EXPECTED_FEATURE_FILES = {
    "specs/features/add-dark-mode.md",
    "execution/features/add-dark-mode.md",
    "quality/features/add-dark-mode.md",
}

REPO_ROOT = Path(__file__).resolve().parents[1]


class FeatureBundleTests(TestCase):
    def test_create_feature_bundle_in_plain_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            written = create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
            )

            self.assertEqual(
                {str(path.relative_to(root)) for path in written},
                EXPECTED_FEATURE_FILES,
            )
            for relative_path in EXPECTED_FEATURE_FILES:
                content = (root / relative_path).read_text(encoding="utf-8")
                self.assertIn("Add dark mode", content)
                self.assertIn("Reduce eye strain", content)
                self.assertIn("Feature ID: add-dark-mode", content)
                self.assertIn("Status: proposed", content)

            spec = (root / "specs" / "features" / "add-dark-mode.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## Why", spec)
            self.assertIn("## Users", spec)
            self.assertIn("## Scope", spec)
            self.assertIn("## Non-Goals", spec)
            self.assertIn("## Acceptance Criteria", spec)

            execution = (
                root / "execution" / "features" / "add-dark-mode.md"
            ).read_text(encoding="utf-8")
            self.assertIn("## Milestones", execution)
            self.assertIn("## Tasks", execution)
            self.assertIn("## Dependencies", execution)
            self.assertIn("## Open Questions", execution)

            quality = (root / "quality" / "features" / "add-dark-mode.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## Required Checks", quality)
            self.assertIn("## Test Plan", quality)
            self.assertIn("## Review Notes", quality)
            self.assertIn("## Release Readiness", quality)

            report = build_validation_report(root, include_features=True)
            self.assertTrue(report["ok"])
            self.assertEqual(validation_exit_code(report), 0)

    def test_create_feature_bundle_does_not_overwrite_existing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            existing = root / "specs" / "features" / "add-dark-mode.md"
            existing.write_text("custom spec\n", encoding="utf-8")

            with self.assertRaises(FeatureBundleExistsError):
                create_feature_bundle(root, "add-dark-mode")

            self.assertEqual(existing.read_text(encoding="utf-8"), "custom spec\n")
            self.assertFalse(
                (root / "execution" / "features" / "add-dark-mode.md").exists()
            )
            self.assertFalse(
                (root / "quality" / "features" / "add-dark-mode.md").exists()
            )

    def test_create_feature_bundle_force_overwrites_existing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text("custom spec\n", encoding="utf-8")

            create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
                force=True,
            )

            content = spec.read_text(encoding="utf-8")
            self.assertNotEqual(content, "custom spec\n")
            self.assertIn("Add dark mode", content)
            self.assertIn("Reduce eye strain", content)

    def test_invalid_feature_slug_is_rejected(self) -> None:
        invalid_slugs = ["Add-dark-mode", "-bad", "bad-", "bad_slug", "bad.slug"]

        for slug in invalid_slugs:
            with self.subTest(slug=slug):
                with self.assertRaises(InvalidFeatureSlug):
                    create_feature_bundle(Path("."), slug)

    def test_single_character_feature_slug_is_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            written = create_feature_bundle(root, "a")

            self.assertEqual(
                {str(path.relative_to(root)) for path in written},
                {
                    "specs/features/a.md",
                    "execution/features/a.md",
                    "quality/features/a.md",
                },
            )
            self.assertIn(
                "Feature ID: a",
                (root / "specs" / "features" / "a.md").read_text(encoding="utf-8"),
            )

    def test_feature_slug_allows_consecutive_hyphens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            written = create_feature_bundle(root, "add--dark-mode")

            self.assertEqual(len(written), 3)
            self.assertTrue((root / "specs" / "features" / "add--dark-mode.md").exists())

    def test_feature_new_cli_creates_bundle_and_returns_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "new",
                        "add-dark-mode",
                        str(root),
                        "--title",
                        "Add dark mode",
                        "--why",
                        "Reduce eye strain",
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Created SpecSpine feature bundle", output.getvalue())
            for relative_path in EXPECTED_FEATURE_FILES:
                self.assertTrue((root / relative_path).exists())

    def test_feature_new_cli_rejects_invalid_slug_with_nonzero_return_code(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "new", "BadSlug", str(root)])

            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_feature_new_cli_does_not_overwrite_without_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "new", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 1)
            self.assertIn("Use --force", stderr.getvalue())
            self.assertIn(
                "existing specs/features/add-dark-mode.md",
                stderr.getvalue(),
            )
            self.assertIn(
                "existing execution/features/add-dark-mode.md",
                stderr.getvalue(),
            )
            self.assertIn(
                "existing quality/features/add-dark-mode.md",
                stderr.getvalue(),
            )

    def test_feature_new_cli_force_overwrites(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text("custom spec\n", encoding="utf-8")

            with redirect_stdout(StringIO()):
                returncode = main(
                    [
                        "feature",
                        "new",
                        "add-dark-mode",
                        str(root),
                        "--title",
                        "Add dark mode",
                        "--force",
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Add dark mode", spec.read_text(encoding="utf-8"))

    def test_parse_feature_tasks_preserves_order_lines_and_done_flags(self) -> None:
        content = "\n".join(
            [
                "# Add dark mode Execution",
                "",
                "Feature ID: add-dark-mode",
                "Status: planned",
                "",
                "## Tasks",
                "",
                "- [ ] Implement theme storage.",
                "* [x] Add system preference detection.",
                "- [X] Update docs.",
                "- plain bullet ignored",
                "notes ignored",
                "",
                "## Dependencies",
                "",
                "- [ ] Not part of tasks.",
            ]
        )

        tasks = parse_feature_tasks(
            content,
            source_file="execution/features/add-dark-mode.md",
        )

        self.assertEqual([task.id for task in tasks], ["T001", "T002", "T003"])
        self.assertEqual(
            [task.text for task in tasks],
            [
                "Implement theme storage.",
                "Add system preference detection.",
                "Update docs.",
            ],
        )
        self.assertEqual([task.done for task in tasks], [False, True, True])
        self.assertEqual([task.line for task in tasks], [8, 9, 10])
        self.assertEqual(
            {task.source_file for task in tasks},
            {"execution/features/add-dark-mode.md"},
        )

    def test_parse_feature_tasks_keeps_lower_heading_tasks_and_markdown_text(self) -> None:
        content = "\n".join(
            [
                "# Add dark mode Execution",
                "",
                "## Tasks",
                "",
                "- [ ] Keep inline `mode: dark` value: unchanged.",
                "- not a checklist",
                "### Follow-up",
                "",
                "* [X] Preserve `cli --flag`: output text.",
                "",
                "## Dependencies",
                "",
                "- [ ] Not part of tasks.",
            ]
        )

        tasks = parse_feature_tasks(
            content,
            source_file="execution/features/add-dark-mode.md",
        )

        self.assertEqual([task.id for task in tasks], ["T001", "T002"])
        self.assertEqual(
            [task.text for task in tasks],
            [
                "Keep inline `mode: dark` value: unchanged.",
                "Preserve `cli --flag`: output text.",
            ],
        )
        self.assertEqual([task.done for task in tasks], [False, True])
        self.assertEqual([task.line for task in tasks], [5, 9])

    def test_feature_tasks_cli_text_and_json_outputs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            execution = root / "execution" / "features" / "add-dark-mode.md"
            execution.write_text(
                "\n".join(
                    [
                        "# Add dark mode Execution",
                        "",
                        "Feature ID: add-dark-mode",
                        "Status: planned",
                        "",
                        "## Tasks",
                        "- [ ] Implement theme storage.",
                        "- [x] Add theme tests.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            text_output = StringIO()
            with redirect_stdout(text_output):
                text_returncode = main(
                    ["feature", "tasks", "add-dark-mode", str(root)]
                )

            self.assertEqual(text_returncode, 0)
            text = text_output.getvalue()
            self.assertIn("Feature tasks: add-dark-mode", text)
            self.assertIn("Status: mixed", text)
            self.assertIn("Summary: total=2 done=1 open=1", text)
            self.assertIn(
                "- [ ] T001 execution/features/add-dark-mode.md:7 Implement theme storage.",
                text,
            )
            self.assertIn(
                "- [x] T002 execution/features/add-dark-mode.md:8 Add theme tests.",
                text,
            )

            json_output = StringIO()
            with redirect_stdout(json_output):
                json_returncode = main(
                    ["feature", "tasks", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(json_output.getvalue())
            self.assertEqual(json_returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["source_file"], "execution/features/add-dark-mode.md")
            self.assertFalse(payload["source_missing"])
            self.assertEqual(payload["summary"], {"done": 1, "open": 1, "total": 2})
            self.assertEqual(
                payload["tasks"],
                [
                    {
                        "done": False,
                        "id": "T001",
                        "line": 7,
                        "source_file": "execution/features/add-dark-mode.md",
                        "text": "Implement theme storage.",
                    },
                    {
                        "done": True,
                        "id": "T002",
                        "line": 8,
                        "source_file": "execution/features/add-dark-mode.md",
                        "text": "Add theme tests.",
                    },
                ],
            )

    def test_feature_tasks_cli_reports_no_tasks_found(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            execution = root / "execution" / "features" / "add-dark-mode.md"
            execution.write_text(
                "\n".join(
                    [
                        "# Add dark mode Execution",
                        "",
                        "Feature ID: add-dark-mode",
                        "Status: planned",
                        "",
                        "## Tasks",
                        "",
                        "- plain bullet",
                        "implementation notes",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "tasks", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 0)
            self.assertIn("Summary: total=0 done=0 open=0", output.getvalue())
            self.assertIn(
                "No checklist tasks found in execution/features/add-dark-mode.md.",
                output.getvalue(),
            )

    def test_feature_tasks_cli_handles_missing_execution_partial_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "execution" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "tasks", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["source_missing"])
            self.assertEqual(payload["tasks"], [])
            self.assertEqual(payload["summary"], {"done": 0, "open": 0, "total": 0})
            self.assertEqual(
                payload["missing_files"],
                ["execution/features/add-dark-mode.md"],
            )

    def test_feature_tasks_cli_text_reports_missing_execution_source(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "execution" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "tasks", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 0)
            self.assertIn("Source: execution/features/add-dark-mode.md", output.getvalue())
            self.assertIn(
                "No tasks found because source file is missing: "
                "execution/features/add-dark-mode.md",
                output.getvalue(),
            )

    def test_feature_tasks_cli_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "tasks", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 1)
            self.assertIn("No feature files found", stderr.getvalue())
            self.assertIn(
                "missing execution/features/add-dark-mode.md",
                stderr.getvalue(),
            )

    def test_feature_tasks_cli_all_files_missing_does_not_call_gh_or_leak_tokens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            stderr = StringIO()

            with patch.dict(
                os.environ,
                {
                    "PATH": "",
                    "GH_TOKEN": "secret-gh-token",
                    "GITHUB_TOKEN": "secret-github-token",
                },
            ):
                with patch("subprocess.run", side_effect=AssertionError("gh called")):
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        returncode = main(
                            ["feature", "tasks", "add-dark-mode", str(root)]
                        )

            combined = stdout.getvalue() + stderr.getvalue()
            self.assertEqual(returncode, 1)
            self.assertNotIn("secret-gh-token", combined)
            self.assertNotIn("secret-github-token", combined)

    def test_feature_tasks_cli_output_file_overwrite_force_and_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output_file = root / "tasks.txt"
            output_file.write_text("existing\n", encoding="utf-8")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "tasks",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("Output file already exists", stderr.getvalue())
            self.assertEqual(output_file.read_text(encoding="utf-8"), "existing\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "tasks",
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
            self.assertIn("Feature tasks: add-dark-mode", output_file.read_text(encoding="utf-8"))
            self.assertNotIn("Wrote feature task list", stdout.getvalue())

    def test_feature_tasks_cli_output_creates_missing_parent_directories(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output_file = root / "nested" / "reports" / "tasks.txt"
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "tasks",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertTrue(output_file.exists())
            self.assertIn("Wrote feature task list", output.getvalue())
            self.assertIn(
                "Feature tasks: add-dark-mode",
                output_file.read_text(encoding="utf-8"),
            )

    def test_feature_tasks_cli_does_not_require_gh_or_github_tokens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()
            fake_token = "secret-test-token"

            with patch.dict(os.environ, {"PATH": "", "GITHUB_TOKEN": fake_token}):
                with redirect_stdout(output):
                    returncode = main(
                        ["feature", "tasks", "add-dark-mode", str(root), "--json"]
                    )

            self.assertEqual(returncode, 0)
            self.assertNotIn(fake_token, output.getvalue())

    def test_build_feature_tasks_report_matches_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")

            report = build_feature_tasks_report(root, "add-dark-mode")

            self.assertEqual(report.summary["total"], 1)
            self.assertEqual(report.tasks[0].id, "T001")

    def test_status_json_lists_feature_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")

            status = build_status(root)

            self.assertEqual(status["features"][0]["slug"], "add-dark-mode")
            self.assertTrue(status["features"][0]["complete"])
            self.assertEqual(status["features"][0]["status"], "proposed")
            self.assertTrue(status["features"][0]["status_consistent"])
            self.assertTrue(
                status["artifacts"]["specs/features/add-dark-mode.md"]["exists"]
            )

    def test_feature_status_cli_json_query_reports_consistent_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "status", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["status"], "proposed")
            self.assertTrue(payload["consistent"])
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(payload["files"]["spec"]["status"], "proposed")

    def test_feature_status_cli_json_query_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()
            stderr = StringIO()

            with redirect_stdout(output), redirect_stderr(stderr):
                returncode = main(
                    ["feature", "status", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIsNone(payload["status"])
            self.assertFalse(payload["consistent"])
            self.assertEqual(
                payload["missing_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            self.assertFalse(any(file["exists"] for file in payload["files"].values()))

    def test_feature_status_cli_text_query_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()
            stderr = StringIO()

            with redirect_stdout(output), redirect_stderr(stderr):
                returncode = main(["feature", "status", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 1)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIn("Feature add-dark-mode status: unknown (mixed/inconsistent)", text)
            self.assertIn("[missing] spec: specs/features/add-dark-mode.md (unknown)", text)

    def test_feature_status_cli_text_reports_mixed_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            execution = root / "execution" / "features" / "add-dark-mode.md"
            execution.write_text(
                execution.read_text(encoding="utf-8").replace(
                    "Status: proposed",
                    "Status: planned",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "status", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 0)
            self.assertIn("mixed/inconsistent", output.getvalue())
            self.assertIn("execution/features/add-dark-mode.md (planned)", output.getvalue())

    def test_feature_status_cli_set_updates_existing_peer_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "implemented",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["status"], "implemented")
            self.assertTrue(payload["consistent"])
            self.assertEqual(
                payload["updated_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            for relative_path in EXPECTED_FEATURE_FILES:
                content = (root / relative_path).read_text(encoding="utf-8")
                self.assertIn("Status: implemented", content)
                self.assertNotIn("Status: proposed", content)

    def test_feature_status_cli_set_inserts_missing_status_line(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace("Status: proposed\n", ""),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "validated",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["status"], "validated")
            self.assertTrue(payload["consistent"])
            lines = spec.read_text(encoding="utf-8").splitlines()
            feature_id_index = lines.index("Feature ID: add-dark-mode")
            self.assertEqual(lines[feature_id_index + 1], "Status: validated")

    def test_feature_status_cli_rejects_invalid_status_and_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")

            stderr = StringIO()
            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "done",
                    ]
                )
            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature status", stderr.getvalue())

            stderr = StringIO()
            with redirect_stderr(stderr):
                returncode = main(["feature", "status", "BadSlug", str(root)])
            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_feature_status_cli_set_updates_partial_bundle_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "planned",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["status"], "planned")
            self.assertTrue(payload["consistent"])
            self.assertEqual(
                payload["missing_files"],
                ["quality/features/add-dark-mode.md"],
            )
            self.assertEqual(
                payload["updated_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                ],
            )

    def test_feature_status_cli_set_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "planned",
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("No feature files found", stderr.getvalue())

    def test_feature_status_cli_text_reports_lifecycle_value_for_consistent_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            set_feature_status(root, "add-dark-mode", "in-progress")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "status", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("Feature add-dark-mode status: in-progress", text)
            self.assertNotIn("mixed/inconsistent", text)
            self.assertIn("specs/features/add-dark-mode.md (in-progress)", text)
            self.assertIn("execution/features/add-dark-mode.md (in-progress)", text)
            self.assertIn("quality/features/add-dark-mode.md (in-progress)", text)

    def test_dogfood_feature_task_export_is_validated_and_exports_tasks(self) -> None:
        report = build_feature_tasks_report(REPO_ROOT, "feature-task-export")

        self.assertEqual(report.status, "validated")
        self.assertGreater(report.summary["total"], 0)
        self.assertTrue(all(task.source_file == "execution/features/feature-task-export.md" for task in report.tasks))
        self.assertTrue(all("TODO" not in task.text for task in report.tasks))

    def test_validate_cli_can_check_feature_bundles(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--features", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.id:add-dark-mode:spec"
                    and check["status"] == "pass"
                    for check in payload["checks"]
                )
            )
            self.assertTrue(
                any(
                    check["id"] == "feature.status_consistency:add-dark-mode"
                    and check["status"] == "pass"
                    for check in payload["checks"]
                )
            )

    def test_validate_features_accepts_all_allowed_statuses(self) -> None:
        for status in FEATURE_STATUSES:
            with self.subTest(status=status):
                with TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    init_workspace(root)
                    create_feature_bundle(root, "add-dark-mode")
                    set_feature_status(root, "add-dark-mode", status)

                    report = build_validation_report(root, include_features=True)

                    self.assertTrue(report["ok"])

    def test_validate_features_rejects_illegal_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace(
                    "Status: proposed",
                    "Status: done",
                ),
                encoding="utf-8",
            )

            report = build_validation_report(root, include_features=True)

            self.assertFalse(report["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.status:add-dark-mode:spec"
                    and check["status"] == "fail"
                    for check in report["checks"]
                )
            )

    def test_validate_features_rejects_missing_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace("Status: proposed\n", ""),
                encoding="utf-8",
            )

            report = build_validation_report(root, include_features=True)

            self.assertFalse(report["ok"])
            checks = {(check["id"], check["status"]) for check in report["checks"]}
            self.assertIn(("feature.status:add-dark-mode:spec", "fail"), checks)
            self.assertIn(("feature.status_consistency:add-dark-mode", "fail"), checks)

    def test_validate_features_rejects_mixed_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            execution = root / "execution" / "features" / "add-dark-mode.md"
            execution.write_text(
                execution.read_text(encoding="utf-8").replace(
                    "Status: proposed",
                    "Status: planned",
                ),
                encoding="utf-8",
            )

            report = build_validation_report(root, include_features=True)

            self.assertFalse(report["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.status_consistency:add-dark-mode"
                    and check["status"] == "fail"
                    for check in report["checks"]
                )
            )

    def test_validate_features_skips_when_no_feature_bundles_exist(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--features", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.discovery"
                    and check["status"] == "skip"
                    for check in payload["checks"]
                )
            )

    def test_validate_features_fails_when_feature_id_does_not_match_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace(
                    "Feature ID: add-dark-mode",
                    "Feature ID: wrong-feature",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--features", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.id:add-dark-mode:spec"
                    and check["status"] == "fail"
                    for check in payload["checks"]
                )
            )

    def test_feature_validation_fails_incomplete_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "execution" / "features" / "add-dark-mode.md").unlink()

            report = build_validation_report(root, include_features=True)

            self.assertFalse(report["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.required_file:add-dark-mode:execution"
                    and check["status"] == "fail"
                    for check in report["checks"]
                )
            )

    def test_feature_issue_cli_generates_text_for_complete_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "issue", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("Title: Add dark mode", text)
            self.assertIn("- Feature ID: `add-dark-mode`", text)
            self.assertIn("- Status: proposed", text)
            self.assertIn("## Why", text)
            self.assertIn("Reduce eye strain", text)
            self.assertIn("## Acceptance Criteria", text)
            self.assertIn("## Tasks", text)
            self.assertIn("## Test Plan", text)
            self.assertIn("## Source Files", text)
            self.assertIn("specs/features/add-dark-mode.md", text)
            self.assertIn("execution/features/add-dark-mode.md", text)
            self.assertIn("quality/features/add-dark-mode.md", text)
            self.assertIn("## Missing Files\n\nNone.", text)

    def test_feature_issue_cli_reflects_current_non_proposed_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            set_feature_status(root, "add-dark-mode", "validated")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "issue", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertIn("- Status: validated", payload["body"])
            self.assertNotIn("- Status: proposed", payload["body"])

    def test_feature_issue_cli_json_output_is_parseable(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "issue", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["title"], "Add dark mode")
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(
                payload["source_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            self.assertIn("Reduce eye strain", payload["body"])

    def test_feature_issue_title_falls_back_to_slug_title_without_spec_h1(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "specs" / "features" / "add-dark-mode.md").write_text(
                "\n".join(
                    [
                        "Feature ID: add-dark-mode",
                        "Status: proposed",
                        "",
                        "## Why",
                        "",
                        "Make evening use comfortable.",
                        "",
                        "## Acceptance Criteria",
                        "",
                        "- [ ] Users can switch to a dark color scheme.",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            draft = build_issue_draft(root, "add-dark-mode")

            self.assertEqual(draft.title, "Add Dark Mode")
            self.assertIn("Make evening use comfortable.", draft.body)

    def test_feature_issue_partial_bundle_marks_missing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "issue", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(
                payload["missing_files"],
                ["quality/features/add-dark-mode.md"],
            )
            self.assertEqual(
                payload["source_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                ],
            )
            self.assertIn("quality/features/add-dark-mode.md", payload["body"])
            self.assertIn(
                "TODO: Add `quality/features/add-dark-mode.md` with a `## Test Plan` section.",
                payload["body"],
            )

    def test_feature_issue_partial_bundle_text_lists_missing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "issue", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("## Missing Files", text)
            self.assertIn(
                "This draft was generated from an incomplete feature bundle.",
                text,
            )
            self.assertIn("- quality/features/add-dark-mode.md", text)
            self.assertIn(
                "TODO: Add `quality/features/add-dark-mode.md` with a `## Test Plan` section.",
                text,
            )

    def test_feature_issue_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                returncode = main(["feature", "issue", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("No feature files found", stderr.getvalue())
            self.assertIn("missing specs/features/add-dark-mode.md", stderr.getvalue())
            self.assertIn(
                "missing execution/features/add-dark-mode.md",
                stderr.getvalue(),
            )
            self.assertIn(
                "missing quality/features/add-dark-mode.md",
                stderr.getvalue(),
            )

    def test_feature_issue_output_file_does_not_overwrite_by_default(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            target = root / "issue.md"
            target.write_text("existing draft\n", encoding="utf-8")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "issue",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(target),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("Output file already exists", stderr.getvalue())
            self.assertEqual(target.read_text(encoding="utf-8"), "existing draft\n")

    def test_feature_issue_output_file_force_overwrites(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            target = root / "issue.md"
            target.write_text("existing draft\n", encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "issue",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(target),
                        "--force",
                    ]
                )

            content = target.read_text(encoding="utf-8")
            self.assertEqual(returncode, 0)
            self.assertIn("Wrote GitHub issue draft body", output.getvalue())
            self.assertNotIn("Title:", content)
            self.assertIn("- Feature ID: `add-dark-mode`", content)

    def test_feature_issue_output_creates_missing_parent_directories(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            target = root / "drafts" / "github" / "issue.md"
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "issue",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(target),
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Wrote GitHub issue draft body", output.getvalue())
            self.assertTrue(target.exists())
            self.assertIn(
                "- Feature ID: `add-dark-mode`",
                target.read_text(encoding="utf-8"),
            )

    def test_feature_issue_json_with_output_writes_body_and_prints_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
            )
            target = root / "issue.md"
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "issue",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(target),
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["title"], "Add dark mode")
            self.assertEqual(target.read_text(encoding="utf-8"), payload["body"])
            self.assertNotIn("Wrote GitHub issue draft body", output.getvalue())

    def test_feature_issue_does_not_need_gh_or_token(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()

            with patch.dict(
                "os.environ",
                {
                    "GH_TOKEN": "secret-gh-token",
                    "GITHUB_TOKEN": "secret-github-token",
                    "PATH": "",
                },
            ):
                with redirect_stdout(output):
                    returncode = main(
                        ["feature", "issue", "add-dark-mode", str(root), "--json"]
                    )

            self.assertEqual(returncode, 0)
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["feature_id"], "add-dark-mode")

    def test_feature_issue_section_missing_uses_placeholders(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "specs" / "features" / "add-dark-mode.md").write_text(
                "# Add dark mode\n\nFeature ID: add-dark-mode\nStatus: proposed\n",
                encoding="utf-8",
            )
            (root / "execution" / "features" / "add-dark-mode.md").write_text(
                "# Add dark mode Execution\n\nFeature ID: add-dark-mode\nStatus: proposed\n",
                encoding="utf-8",
            )
            (root / "quality" / "features" / "add-dark-mode.md").write_text(
                "# Add dark mode Quality\n\nFeature ID: add-dark-mode\nStatus: proposed\n",
                encoding="utf-8",
            )

            draft = build_issue_draft(root, "add-dark-mode")

            self.assertEqual(draft.title, "Add dark mode")
            self.assertIn(
                "TODO: Add a `## Why` section to `specs/features/add-dark-mode.md`.",
                draft.body,
            )
            self.assertIn(
                "TODO: Add a `## Acceptance Criteria` section to `specs/features/add-dark-mode.md`.",
                draft.body,
            )
            self.assertIn(
                "TODO: Add a `## Tasks` section to `execution/features/add-dark-mode.md`.",
                draft.body,
            )
            self.assertIn(
                "TODO: Add a `## Test Plan` section to `quality/features/add-dark-mode.md`.",
                draft.body,
            )
