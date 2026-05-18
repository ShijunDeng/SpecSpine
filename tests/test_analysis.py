import json
import socket
import subprocess
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.analysis import build_analysis_report
from specspine.cli import main
from specspine.workspace import init_workspace


def write_feature_bundle(
    root: Path,
    slug: str,
    *,
    status: str = "validated",
    acceptance_criteria: list[str] | None = None,
    tasks: list[str] | None = None,
    coverage: list[str] | None = None,
) -> None:
    if acceptance_criteria is None:
        acceptance_criteria = [
            "CLI emits a stable JSON analysis report.",
            "Text output summarizes analysis findings.",
        ]
    if tasks is None:
        tasks = [
            "AC001 Build the JSON report shape.",
            "AC002 Render the compact text report.",
        ]
    if coverage is None:
        coverage = [
            "AC001 -> tests/test_analysis.py::AnalysisCommandTests::test_json_shape_and_feature_filter",
            "AC002 -> tests/test_analysis.py::AnalysisCommandTests::test_text_output_is_report_only_and_fail_flag_is_opt_in",
        ]

    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "tests" / "test_analysis.py").write_text(
        "# local coverage target\n",
        encoding="utf-8",
    )

    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug.title()}",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "Priority: high",
                "Owner: SpecSpine Maintainers",
                "Milestone: analysis",
                "Target Release: 2026.5",
                "Project: Native feature bundles",
                "Effort: M",
                "",
                "## Acceptance Criteria",
                "",
                *[f"- [x] {item}" for item in acceptance_criteria],
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug.title()} Execution",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "",
                "## Tasks",
                "",
                *[f"- [x] {item}" for item in tasks],
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug.title()} Quality",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "",
                "## Required Checks",
                "",
                "- [x] Analysis report behavior is covered.",
                "- [x] Local-only safety behavior is covered.",
                "",
                "## Test Coverage",
                "",
                *[f"- [x] {item}" for item in coverage],
                "",
                "## Test Plan",
                "",
                "- Run `PYTHONPATH=src python3 -m unittest tests.test_analysis`.",
                "",
                "## Release Readiness",
                "",
                "- [x] JSON and text outputs are reviewed.",
                "- [x] Local-only safety checks pass.",
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


class AnalysisCommandTests(TestCase):
    def test_json_shape_and_feature_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "analysis-command")
            write_feature_bundle(root, "other-feature")

            code, stdout, stderr = run_cli(
                ["analyze", str(root), "--json", "--feature", "analysis-command"]
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["root"], str(root.resolve()))
            self.assertEqual(payload["feature_filter"], "analysis-command")
            self.assertEqual(payload["summary"]["features_total"], 1)
            self.assertEqual(payload["summary"]["issues_total"], 0)
            self.assertEqual(
                payload["summary"]["issue_counts_by_severity"]["high"],
                0,
            )
            self.assertEqual(len(payload["features"]), 1)
            feature = payload["features"][0]
            self.assertEqual(feature["feature_id"], "analysis-command")
            self.assertEqual(feature["metrics"]["acceptance_criteria_total"], 2)
            self.assertEqual(feature["metrics"]["covered_acceptance_criteria"], 2)
            self.assertEqual(payload["issues"], [])

    def test_issue_detection_from_local_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "broken-analysis",
                acceptance_criteria=[
                    "Users get simple insight from the report.",
                    "Users get simple insight from the report.",
                ],
                tasks=["Build report output without an evidence reference."],
                coverage=[
                    "AC001 -> tests/test_analysis.py::AnalysisCommandTests::test_issue_detection_from_local_artifacts",
                    "AC003 -> tests/missing_analysis.py",
                ],
            )

            report = build_analysis_report(root, feature_filter="broken-analysis")
            codes = {issue.code for issue in report.issues}

            self.assertIn("acceptance.no_task_reference", codes)
            self.assertIn("acceptance.no_coverage_link", codes)
            self.assertIn("coverage.unknown_acceptance_criterion", codes)
            self.assertIn("coverage.missing_target", codes)
            self.assertIn("task.no_reference", codes)
            self.assertIn("acceptance.duplicate_text", codes)
            self.assertIn("acceptance.vague_text", codes)
            self.assertGreaterEqual(report.summary["issues_total"], 7)

    def test_issue_ordering_and_ids_are_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "zeta-determinism",
                tasks=["Implement the report without references."],
                coverage=["AC001 -> tests/missing_zeta.py::test_missing_zeta"],
            )
            write_feature_bundle(
                root,
                "alpha-determinism",
                tasks=["Implement the report without references."],
                coverage=["AC001 -> tests/missing_alpha.py::test_missing_alpha"],
            )

            first = build_analysis_report(root)
            second = build_analysis_report(root)

            first_issues = [issue.as_dict() for issue in first.issues]
            second_issues = [issue.as_dict() for issue in second.issues]
            self.assertEqual(first_issues, second_issues)
            self.assertEqual(
                [issue.id for issue in first.issues],
                [f"AN{index:03d}" for index in range(1, len(first.issues) + 1)],
            )
            severity_rank = {
                "critical": 0,
                "high": 1,
                "medium": 2,
                "low": 3,
            }
            issue_keys = [
                (
                    issue.feature_id,
                    severity_rank[issue.severity],
                    issue.category,
                    issue.code,
                    issue.source_file,
                    issue.line or 0,
                    issue.message,
                )
                for issue in first.issues
            ]
            self.assertEqual(issue_keys, sorted(issue_keys))
            self.assertEqual(first.issues[0].feature_id, "alpha-determinism")

    def test_missing_coverage_target_is_high_severity_coverage_issue(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "missing-target",
                acceptance_criteria=["CLI flags missing local coverage targets."],
                tasks=["AC001 Classify missing coverage targets."],
                coverage=["AC001 -> tests/missing_target.py::test_missing_target"],
            )

            report = build_analysis_report(root, feature_filter="missing-target")
            missing_target_issues = [
                issue
                for issue in report.issues
                if issue.code == "coverage.missing_target"
            ]

            self.assertEqual(len(missing_target_issues), 1)
            issue = missing_target_issues[0]
            self.assertEqual(issue.severity, "high")
            self.assertEqual(issue.category, "coverage")
            self.assertEqual(
                issue.evidence,
                {
                    "coverage_link_id": "COV001",
                    "target_path": "tests/missing_target.py",
                },
            )
            self.assertIn("tests/missing_target.py", issue.message)

    def test_unchecked_missing_coverage_target_reports_missing_and_open_link(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "unchecked-missing-target",
                acceptance_criteria=["CLI flags unchecked missing local coverage targets."],
                tasks=["AC001 Classify unchecked missing coverage targets."],
                coverage=["AC001 -> tests/missing.py"],
            )
            quality_path = (
                root / "quality" / "features" / "unchecked-missing-target.md"
            )
            quality_path.write_text(
                quality_path.read_text(encoding="utf-8").replace(
                    "- [x] AC001 -> tests/missing.py",
                    "- [ ] AC001 -> tests/missing.py",
                    1,
                ),
                encoding="utf-8",
            )

            report = build_analysis_report(
                root,
                feature_filter="unchecked-missing-target",
            )
            by_code = {issue.code: issue for issue in report.issues}

            self.assertIn("coverage.missing_target", by_code)
            self.assertIn("coverage.open_link", by_code)
            self.assertEqual(by_code["coverage.missing_target"].severity, "high")
            self.assertEqual(
                by_code["coverage.missing_target"].evidence,
                {
                    "coverage_link_id": "COV001",
                    "target_path": "tests/missing.py",
                },
            )

    def test_text_output_is_report_only_and_fail_flag_is_opt_in(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "issue-feature",
                tasks=["Implement output."],
                coverage=[],
            )

            code, stdout, stderr = run_cli(["analyze", str(root)])
            self.assertEqual(code, 0, stderr)
            self.assertIn("SpecSpine analysis", stdout)
            self.assertIn("Issues:", stdout)
            self.assertIn("issue-feature", stdout)

            fail_code, _stdout, fail_stderr = run_cli(
                ["analyze", str(root), "--fail-on-issues"]
            )
            self.assertEqual(fail_code, 1, fail_stderr)

    def test_clean_text_output_reports_success_and_fail_flag_still_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "clean-analysis")

            code, stdout, stderr = run_cli(
                ["analyze", str(root), "--feature", "clean-analysis"]
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Issues:\n- None. No consistency or coverage issues found.", stdout)
            self.assertIn(
                "- Analysis is clean; continue with validation or implementation handoff.",
                stdout,
            )
            self.assertNotIn("[high]", stdout)
            self.assertEqual(stderr, "")

            fail_code, fail_stdout, fail_stderr = run_cli(
                [
                    "analyze",
                    str(root),
                    "--feature",
                    "clean-analysis",
                    "--fail-on-issues",
                ]
            )
            self.assertEqual(fail_code, 0, fail_stderr)
            self.assertIn("issues=0", fail_stdout)

    def test_missing_feature_filter_reports_issue_without_crashing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            code, stdout, stderr = run_cli(
                ["analyze", str(root), "--json", "--feature", "missing-feature"]
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["summary"]["features_total"], 1)
            self.assertEqual(payload["issues"][0]["code"], "feature.missing_bundle")
            self.assertEqual(payload["issues"][0]["severity"], "critical")
            self.assertEqual(payload["issues"][0]["id"], "AN001")
            self.assertEqual(payload["issues"][0]["feature_id"], "missing-feature")

            fail_code, fail_stdout, fail_stderr = run_cli(
                [
                    "analyze",
                    str(root),
                    "--json",
                    "--feature",
                    "missing-feature",
                    "--fail-on-issues",
                ]
            )
            self.assertEqual(fail_code, 1, fail_stderr)
            self.assertEqual(json.loads(fail_stdout)["issues"][0]["id"], "AN001")

    def test_invalid_feature_filter_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            code, stdout, stderr = run_cli(
                ["analyze", tmp, "--feature", "Invalid Feature"]
            )

            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertIn("Invalid feature slug", stderr)

    def test_analyze_is_read_only_local_and_does_not_probe_external_services(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "safe-analysis")
            before = {
                str(path.relative_to(root)): path.read_text(encoding="utf-8")
                for path in sorted(root.rglob("*"))
                if path.is_file()
            }

            with patch.object(subprocess, "run") as run_mock, patch.object(
                subprocess,
                "check_output",
            ) as check_output_mock, patch.object(
                socket,
                "create_connection",
            ) as socket_mock, patch.object(
                urllib.request,
                "urlopen",
            ) as urlopen_mock, patch.dict(
                "os.environ",
                {"GITHUB_TOKEN": "unused-token", "GH_TOKEN": "unused-token"},
            ):
                code, stdout, stderr = run_cli(["analyze", str(root), "--json"])

            after = {
                str(path.relative_to(root)): path.read_text(encoding="utf-8")
                for path in sorted(root.rglob("*"))
                if path.is_file()
            }
            self.assertEqual(code, 0, stderr)
            self.assertEqual(before, after)
            self.assertEqual(json.loads(stdout)["summary"]["issues_total"], 0)
            run_mock.assert_not_called()
            check_output_mock.assert_not_called()
            socket_mock.assert_not_called()
            urlopen_mock.assert_not_called()
