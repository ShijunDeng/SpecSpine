from __future__ import annotations

import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import main
from specspine.retrospective import (
    build_retrospective_report,
    render_retrospective_text,
)


def write_feature(
    root: Path,
    slug: str,
    *,
    status: str,
    checked: bool,
    coverage: bool,
    priority: str = "medium",
    owner: str = "Team",
) -> None:
    marker = "x" if checked else " "
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "tests" / f"test_{slug.replace('-', '_')}.py").write_text(
        "# coverage target\n",
        encoding="utf-8",
    )
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug}",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                f"Priority: {priority}",
                f"Owner: {owner}",
                "",
                "## Acceptance Criteria",
                "",
                f"- [{marker}] AC001: When a user asks, the system shall respond.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug} Execution",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "",
                "## Tasks",
                "",
                f"- [{marker}] TASK001: Implement behavior.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    coverage_marker = "x" if coverage else " "
    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug} Quality",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "",
                "## Required Checks",
                "",
                f"- [{marker}] Acceptance reviewed.",
                "",
                "## Test Coverage",
                "",
                f"- [{coverage_marker}] AC001 -> tests/test_{slug.replace('-', '_')}.py",
                "",
                "## Test Plan",
                "",
                "- Run focused tests.",
                "",
                "## Release Readiness",
                "",
                f"- [{marker}] Ready for review.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class RetrospectiveReportTests(TestCase):
    def test_report_includes_contract_fields_and_feature_records(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature(root, "ready-feature", status="validated", checked=True, coverage=True)
            write_feature(root, "planned-feature", status="planned", checked=False, coverage=False)

            report = build_retrospective_report(root)

            self.assertEqual(
                set(report),
                {
                    "features",
                    "feature_filter",
                    "recommendations",
                    "recommended_commands",
                    "root",
                    "safety_notes",
                    "summary",
                    "themes",
                },
            )
            self.assertEqual(report["summary"]["features_total"], 2)
            self.assertEqual(report["summary"]["features_ready"], 1)
            self.assertEqual(report["summary"]["features_not_ready"], 1)
            planned = next(
                feature
                for feature in report["features"]
                if feature["feature_id"] == "planned-feature"
            )
            self.assertEqual(planned["status"], "planned")
            self.assertFalse(planned["ready"])
            self.assertEqual(planned["priority"], "medium")
            self.assertEqual(planned["owner"], "Team")
            self.assertEqual(planned["task_counts"], {"done": 0, "open": 1, "total": 1})
            self.assertGreater(planned["readiness_counts"]["fail"], 0)
            self.assertGreater(len(planned["blocking_checks"]), 0)
            self.assertEqual(planned["coverage_state"]["state"], "partial")
            self.assertIn(
                "specs/features/planned-feature.md",
                planned["source_files"],
            )
            self.assertIn(
                "specspine feature ready planned-feature . --json --require-coverage",
                planned["recommended_commands"],
            )

    def test_recommendations_are_ranked_and_limit_only_trims_rows(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature(root, "ready-feature", status="validated", checked=True, coverage=True)
            write_feature(root, "blocked-feature", status="planned", checked=False, coverage=False)

            report = build_retrospective_report(root, limit=1)

            self.assertEqual(report["summary"]["features_total"], 2)
            self.assertEqual(report["themes"]["open_tasks"]["total"], 1)
            self.assertEqual(len(report["recommendations"]), 1)
            self.assertEqual(
                report["recommendations"][0]["feature_id"],
                "blocked-feature",
            )

    def test_focused_scan_and_missing_feature_cli_exit_codes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature(root, "ready-feature", status="validated", checked=True, coverage=True)

            out = StringIO()
            with redirect_stdout(out):
                exit_code = main(
                    [
                        "retrospective",
                        "report",
                        str(root),
                        "--feature",
                        "ready-feature",
                        "--json",
                    ]
                )
            payload = json.loads(out.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["feature_filter"], "ready-feature")
            self.assertEqual(len(payload["features"]), 1)

            out = StringIO()
            with redirect_stdout(out):
                exit_code = main(
                    [
                        "retrospective",
                        "report",
                        str(root),
                        "--feature",
                        "missing-feature",
                        "--json",
                    ]
                )
            payload = json.loads(out.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["summary"]["missing_feature"], "missing-feature")
            self.assertEqual(payload["features"], [])

    def test_invalid_slug_and_negative_limit_return_usage_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            err = StringIO()
            with redirect_stderr(err):
                exit_code = main(
                    [
                        "retrospective",
                        "report",
                        str(root),
                        "--feature",
                        "Bad Slug",
                        "--json",
                    ]
                )
            self.assertEqual(exit_code, 2)
            self.assertIn("Invalid retrospective option", err.getvalue())

            err = StringIO()
            with redirect_stderr(err):
                exit_code = main(
                    [
                        "retrospective",
                        "report",
                        str(root),
                        "--limit",
                        "-1",
                    ]
                )
            self.assertEqual(exit_code, 2)
            self.assertIn("limit must be a nonnegative integer", err.getvalue())

    def test_invalid_workspace_path_returns_runtime_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            err = StringIO()
            with redirect_stderr(err):
                exit_code = main(
                    [
                        "retrospective",
                        "report",
                        str(root / "missing"),
                        "--json",
                    ]
                )
            self.assertEqual(exit_code, 1)
            self.assertIn("Could not build retrospective", err.getvalue())

            file_path = root / "not-a-directory.txt"
            file_path.write_text("content\n", encoding="utf-8")
            err = StringIO()
            with redirect_stderr(err):
                exit_code = main(
                    [
                        "retrospective",
                        "report",
                        str(file_path),
                    ]
                )
            self.assertEqual(exit_code, 1)
            self.assertIn("Could not build retrospective", err.getvalue())

    def test_text_rendering_and_safety_notes_are_read_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_retrospective_report(root)
            text = render_retrospective_text(report)

            self.assertIn("Retrospective report:", text)
            self.assertIn("Safety notes:", text)
            self.assertFalse((root / ".specspine" / "retrospective").exists())
            safety = " ".join(report["safety_notes"])
            for expected in (
                "does not write files",
                "Does not run tests",
                "invoke subprocesses",
                "network services",
                "GitHub",
                "upstream CLIs",
                "environment variables",
                "tokens",
                "advisory and are not executed",
            ):
                self.assertIn(expected, safety)
