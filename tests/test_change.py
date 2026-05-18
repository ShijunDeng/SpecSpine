from __future__ import annotations

import os
import json
import subprocess
import unittest
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from specspine.change import (
    build_change_risk_report,
    render_change_risk_json,
    render_change_risk_text,
)
from specspine.cli import main
from specspine.features import InvalidFeatureSlug, create_feature_bundle


class ChangeRiskReportTests(unittest.TestCase):
    def test_changed_files_are_classified_and_summarized(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_feature_bundle(root, "risk-report")

            report = build_change_risk_report(
                root,
                changed_files=(
                    "src/specspine/change.py",
                    "tests/test_change.py",
                    "specs/features/risk-report.md",
                    "execution/features/risk-report.md",
                    "quality/features/risk-report.md",
                    "README.md",
                    ".github/workflows/ci.yml",
                    "scripts/local.py",
                ),
            )

            by_path = {file["path"]: file for file in report.files}
            self.assertEqual(by_path["src/specspine/change.py"]["category"], "source")
            self.assertEqual(by_path["src/specspine/change.py"]["risk"], "high")
            self.assertEqual(by_path["tests/test_change.py"]["category"], "test")
            self.assertEqual(by_path["tests/test_change.py"]["risk"], "medium")
            self.assertEqual(
                by_path["specs/features/risk-report.md"]["category"],
                "feature-spec",
            )
            self.assertEqual(
                by_path["execution/features/risk-report.md"]["category"],
                "feature-execution",
            )
            self.assertEqual(
                by_path["quality/features/risk-report.md"]["category"],
                "feature-quality",
            )
            self.assertEqual(by_path["README.md"]["category"], "project-doc")
            self.assertEqual(by_path["README.md"]["risk"], "low")
            self.assertEqual(by_path[".github/workflows/ci.yml"]["category"], "config")
            self.assertEqual(by_path[".github/workflows/ci.yml"]["risk"], "high")
            self.assertEqual(by_path["scripts/local.py"]["category"], "other")
            self.assertEqual(by_path["scripts/local.py"]["risk"], "low")
            self.assertEqual(report.summary["changed_files"], 8)
            self.assertEqual(report.summary["high"], 2)
            self.assertEqual(report.summary["medium"], 4)
            self.assertEqual(report.summary["low"], 2)

    def test_feature_is_inferred_from_peer_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_feature_bundle(root, "risk-report")

            report = build_change_risk_report(
                root,
                changed_files=(
                    "specs/features/risk-report.md",
                    "execution/features/risk-report.md",
                ),
            )

            self.assertIsNone(report.feature_id)
            self.assertEqual(report.summary["feature_ids"], ["risk-report"])
            self.assertEqual(len(report.feature_evidence), 1)
            evidence = report.feature_evidence[0]
            self.assertEqual(evidence["feature_id"], "risk-report")
            self.assertTrue(evidence["has_native_files"])
            self.assertEqual(evidence["missing_files"], [])
            self.assertIn(
                "specspine tests impact . --feature risk-report --json",
                report.recommended_commands,
            )
            self.assertIn(
                "specspine feature ready risk-report . --json --require-coverage",
                report.recommended_commands,
            )
            self.assertIn(
                "specs/features/risk-report.md",
                evidence["source_files"],
            )

    def test_workspace_packet_recommends_conservative_commands(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            report = build_change_risk_report(root)

            self.assertEqual(report.changed_files, ())
            self.assertEqual(report.summary["changed_files"], 0)
            self.assertIn("specspine change risk . --json", report.recommended_commands)
            self.assertIn("specspine review packet . --json", report.recommended_commands)
            self.assertIn(
                "specspine validate . --fusion --features",
                report.recommended_commands,
            )

    def test_missing_feature_is_reported_without_crashing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            report = build_change_risk_report(root, feature="missing-feature")

            self.assertEqual(report.feature_id, "missing-feature")
            self.assertEqual(report.summary["feature_ids"], ["missing-feature"])
            evidence = report.feature_evidence[0]
            self.assertFalse(evidence["has_native_files"])
            self.assertFalse(evidence["ready"])
            self.assertEqual(evidence["status"], "unknown")
            self.assertEqual(
                set(evidence["missing_files"]),
                {
                    "specs/features/missing-feature.md",
                    "execution/features/missing-feature.md",
                    "quality/features/missing-feature.md",
                },
            )

    def test_invalid_feature_slug_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(InvalidFeatureSlug):
                build_change_risk_report(Path(tmp), feature="Bad Slug")

    def test_builder_is_local_only_and_renderers_are_pure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_feature_bundle(root, "risk-report")
            guards = (
                mock.patch.object(
                    subprocess,
                    "run",
                    side_effect=AssertionError("subprocess.run called"),
                ),
                mock.patch.object(
                    subprocess,
                    "Popen",
                    side_effect=AssertionError("subprocess.Popen called"),
                ),
                mock.patch.object(
                    urllib.request,
                    "urlopen",
                    side_effect=AssertionError("network called"),
                ),
                mock.patch.object(
                    os,
                    "getenv",
                    side_effect=AssertionError("environment read"),
                ),
            )

            with guards[0], guards[1], guards[2], guards[3]:
                report = build_change_risk_report(
                    root,
                    changed_files=("specs/features/risk-report.md",),
                    feature="risk-report",
                )
                json_output = render_change_risk_json(report)
                text_output = render_change_risk_text(report)

            self.assertIn('"feature_id": "risk-report"', json_output)
            self.assertIn("advisory only", text_output)
            self.assertEqual(report.summary["feature_ids"], ["risk-report"])
            self.assertIn(
                "specspine review packet . --changed specs/features/risk-report.md --json",
                report.recommended_commands,
            )

    def test_cli_json_and_missing_feature_exit_codes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_feature_bundle(root, "risk-report")
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(
                    [
                        "change",
                        "risk",
                        str(root),
                        "--json",
                        "--changed",
                        "src/specspine/change.py",
                        "--feature",
                        "risk-report",
                    ]
                )

            self.assertEqual(code, 0, stderr.getvalue())
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["feature_id"], "risk-report")
            self.assertEqual(payload["files"][0]["category"], "source")
            self.assertTrue(payload["feature_evidence"][0]["has_native_files"])

            missing_stdout = StringIO()
            with redirect_stdout(missing_stdout), redirect_stderr(StringIO()):
                missing_code = main(
                    [
                        "change",
                        "risk",
                        str(root),
                        "--json",
                        "--feature",
                        "missing-feature",
                    ]
                )
            self.assertEqual(missing_code, 1)
            self.assertFalse(json.loads(missing_stdout.getvalue())["feature_evidence"][0]["has_native_files"])

    def test_cli_invalid_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(["change", "risk", tmp, "--feature", "Bad Slug"])

            self.assertEqual(code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("Invalid feature slug", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
