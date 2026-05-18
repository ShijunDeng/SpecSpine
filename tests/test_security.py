from __future__ import annotations

import json
import os
import subprocess
import unittest
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from specspine.cli import main
from specspine.features import InvalidFeatureSlug, create_feature_bundle
from specspine.security import (
    build_security_cue_report,
    render_security_cue_json,
    render_security_cue_text,
)


class SecurityCueReportTests(unittest.TestCase):
    def test_detects_security_cues_without_emitting_file_content(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src" / "specspine" / "service.py"
            source.parent.mkdir(parents=True)
            source.write_text(
                "\n".join(
                    [
                        "API_KEY = 'do-not-emit-this-value'",
                        "subprocess.run(command, shell=True)",
                        "yaml.load(payload)",
                        "path = '../secrets.txt'",
                    ]
                ),
                encoding="utf-8",
            )

            report = build_security_cue_report(
                root,
                changed_files=("src/specspine/service.py",),
            )

            self.assertEqual(report.summary["changed_files"], 1)
            self.assertEqual(report.summary["files_existing"], 1)
            self.assertGreaterEqual(report.summary["high"], 4)
            self.assertGreaterEqual(report.summary["cues_total"], 4)
            self.assertEqual(report.files[0]["category"], "source")
            self.assertTrue(report.files[0]["exists"])
            self.assertTrue(report.files[0]["text_read"])

            keywords = {cue["keyword"] for cue in report.cues}
            self.assertIn("api_key", keywords)
            self.assertIn("subprocess", keywords)
            self.assertIn("shell", keywords)
            self.assertIn("yaml.load", keywords)
            self.assertIn("../", keywords)
            for cue in report.cues:
                self.assertNotIn("do-not-emit-this-value", json.dumps(cue))
                self.assertEqual(cue["path"], "src/specspine/service.py")
                self.assertIn(cue["severity"], {"low", "medium", "high"})

            rendered = render_security_cue_json(report)
            self.assertNotIn("do-not-emit-this-value", rendered)
            self.assertIn('"cues_total"', rendered)

    def test_missing_files_are_reported_without_crashing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            report = build_security_cue_report(
                root,
                changed_files=("tests/test_missing.py",),
            )

            self.assertEqual(report.summary["changed_files"], 1)
            self.assertEqual(report.summary["files_existing"], 0)
            self.assertEqual(report.summary["cues_total"], 0)
            self.assertEqual(report.files[0]["category"], "test")
            self.assertFalse(report.files[0]["exists"])
            self.assertFalse(report.files[0]["text_read"])

    def test_feature_is_inferred_from_peer_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_feature_bundle(root, "security-cues")

            report = build_security_cue_report(
                root,
                changed_files=(
                    "specs/features/security-cues.md",
                    "quality/features/security-cues.md",
                ),
            )

            self.assertIsNone(report.feature_id)
            self.assertEqual(report.summary["feature_ids"], ["security-cues"])
            self.assertEqual(len(report.feature_evidence), 1)
            evidence = report.feature_evidence[0]
            self.assertEqual(evidence["feature_id"], "security-cues")
            self.assertTrue(evidence["has_native_files"])
            self.assertIn("status", evidence)
            self.assertIn("ready", evidence)
            self.assertIn("blocking_checks", evidence)
            self.assertIn("source_files", evidence)
            self.assertIn(
                "specspine feature ready security-cues . --json --require-coverage",
                report.recommended_commands,
            )
            self.assertIn(
                "specs/features/security-cues.md",
                evidence["source_files"],
            )

    def test_missing_feature_is_reported_without_crashing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            report = build_security_cue_report(root, feature="missing-feature")

            self.assertEqual(report.feature_id, "missing-feature")
            self.assertEqual(report.summary["feature_ids"], ["missing-feature"])
            self.assertEqual(len(report.feature_evidence), 1)
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
                build_security_cue_report(Path(tmp), feature="Bad Slug")

    def test_builder_is_local_only_and_renderers_are_pure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_feature_bundle(root, "security-cues")
            source = root / "src" / "specspine" / "security_local.py"
            source.parent.mkdir(parents=True)
            source.write_text("token = 'redacted'\n", encoding="utf-8")

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
                report = build_security_cue_report(
                    root,
                    changed_files=(
                        "src/specspine/security_local.py",
                        "specs/features/security-cues.md",
                    ),
                    feature="security-cues",
                )
                json_output = render_security_cue_json(report)
                text_output = render_security_cue_text(report)

            self.assertIn('"feature_id": "security-cues"', json_output)
            self.assertIn("advisory only", text_output)
            self.assertIn("not proof of a vulnerability", text_output)
            self.assertEqual(report.summary["feature_ids"], ["security-cues"])
            self.assertIn(
                "specspine change risk . --changed src/specspine/security_local.py --json",
                report.recommended_commands,
            )
            self.assertIn(
                "specspine review packet . --changed src/specspine/security_local.py --json",
                report.recommended_commands,
            )
            self.assertIn(
                "specspine tests impact . --changed src/specspine/security_local.py --json",
                report.recommended_commands,
            )

    def test_cli_json_and_missing_feature_exit_codes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_feature_bundle(root, "security-cues")
            source = root / "src" / "specspine" / "security_local.py"
            source.parent.mkdir(parents=True)
            source.write_text("password = 'do-not-emit'\n", encoding="utf-8")
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(
                    [
                        "security",
                        "cues",
                        str(root),
                        "--json",
                        "--changed",
                        "src/specspine/security_local.py",
                        "--feature",
                        "security-cues",
                    ]
                )

            self.assertEqual(code, 0, stderr.getvalue())
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["feature_id"], "security-cues")
            self.assertEqual(payload["files"][0]["category"], "source")
            self.assertTrue(payload["feature_evidence"][0]["has_native_files"])
            self.assertGreaterEqual(payload["summary"]["high"], 1)
            self.assertNotIn("do-not-emit", stdout.getvalue())

            missing_stdout = StringIO()
            with redirect_stdout(missing_stdout), redirect_stderr(StringIO()):
                missing_code = main(
                    [
                        "security",
                        "cues",
                        str(root),
                        "--json",
                        "--feature",
                        "missing-feature",
                    ]
                )
            self.assertEqual(missing_code, 1)
            self.assertFalse(
                json.loads(missing_stdout.getvalue())["feature_evidence"][0][
                    "has_native_files"
                ]
            )

    def test_cli_invalid_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(["security", "cues", tmp, "--feature", "Bad Slug"])

            self.assertEqual(code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("Invalid feature slug", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
