from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.features import InvalidFeatureSlug
from specspine.verification import (
    build_verification_matrix,
    render_verification_matrix_json,
    render_verification_matrix_text,
)


def write_feature(root: Path, *, covered: bool = True) -> None:
    slug = "audit-trail"
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    if covered:
        (root / "tests").mkdir()
        (root / "tests" / "test_audit_trail.py").write_text(
            "# target\n",
            encoding="utf-8",
        )
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Audit Trail",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Acceptance Criteria",
                "",
                "- [x] Audit evidence is visible.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Audit Trail Execution",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Tasks",
                "",
                "- [x] Implement evidence export.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    target = "tests/test_audit_trail.py" if covered else "tests/missing.py"
    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Audit Trail Quality",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Required Checks",
                "",
                "- [x] Evidence export reviewed.",
                "",
                "## Test Coverage",
                "",
                f"- [x] AC001 -> {target}",
                "",
                "## Test Plan",
                "",
                "- Run audit trail tests.",
                "",
                "## Release Readiness",
                "",
                "- [x] Ready for review.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class VerificationMatrixTests(TestCase):
    def test_verified_row_when_acceptance_criterion_has_existing_checked_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature(root)

            matrix = build_verification_matrix(root, "audit-trail")

            self.assertTrue(matrix.ready)
            self.assertEqual(matrix.summary["verified"], 1)
            self.assertEqual(matrix.summary["unverified"], 0)
            self.assertEqual(matrix.matrix[0]["verification_status"], "verified")
            self.assertTrue(matrix.matrix[0]["coverage_complete"])
            self.assertEqual(matrix.matrix[0]["gap_reasons"], [])

    def test_unverified_row_when_coverage_target_is_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature(root, covered=False)

            matrix = build_verification_matrix(root, "audit-trail")

            self.assertFalse(matrix.ready)
            self.assertEqual(matrix.summary["verified"], 0)
            self.assertEqual(matrix.summary["unverified"], 1)
            self.assertEqual(matrix.matrix[0]["verification_status"], "unverified")
            self.assertFalse(matrix.matrix[0]["coverage_complete"])
            self.assertIn("test_coverage_incomplete", matrix.matrix[0]["gap_reasons"])

    def test_unverified_row_when_coverage_link_is_unchecked(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature(root)
            quality = root / "quality" / "features" / "audit-trail.md"
            quality.write_text(
                quality.read_text(encoding="utf-8").replace(
                    "- [x] AC001 -> tests/test_audit_trail.py",
                    "- [ ] AC001 -> tests/test_audit_trail.py",
                ),
                encoding="utf-8",
            )

            matrix = build_verification_matrix(root, "audit-trail")

            self.assertFalse(matrix.ready)
            self.assertEqual(matrix.summary["verified"], 0)
            self.assertEqual(matrix.matrix[0]["verification_status"], "unverified")
            self.assertFalse(matrix.matrix[0]["coverage_complete"])
            self.assertIn("test_coverage_incomplete", matrix.matrix[0]["gap_reasons"])

    def test_unverified_row_when_acceptance_criterion_has_no_coverage_link(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature(root)
            quality = root / "quality" / "features" / "audit-trail.md"
            quality.write_text(
                quality.read_text(encoding="utf-8").replace(
                    "## Test Coverage\n\n- [x] AC001 -> tests/test_audit_trail.py\n\n",
                    "",
                ),
                encoding="utf-8",
            )

            matrix = build_verification_matrix(root, "audit-trail")

            self.assertFalse(matrix.ready)
            self.assertEqual(matrix.summary["verified"], 0)
            self.assertEqual(matrix.matrix[0]["test_coverage"], [])
            self.assertFalse(matrix.matrix[0]["coverage_complete"])
            self.assertIn("missing_test_coverage", matrix.matrix[0]["gap_reasons"])

    def test_missing_feature_returns_structured_report(self) -> None:
        with TemporaryDirectory() as tmp:
            matrix = build_verification_matrix(Path(tmp), "missing-feature")

            self.assertEqual(matrix.feature_id, "missing-feature")
            self.assertFalse(matrix.ready)
            self.assertEqual(matrix.status, "unknown")
            self.assertEqual(matrix.matrix, ())
            self.assertFalse(matrix.evidence["has_native_files"])
            self.assertEqual(matrix.summary["acceptance_criteria"], 0)
            self.assertEqual(len(matrix.evidence["missing_files"]), 3)

    def test_invalid_feature_slug_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(InvalidFeatureSlug):
                build_verification_matrix(Path(tmp), "Bad Slug")

    def test_cli_json_and_exit_codes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature(root)
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                returncode = main(["verify", "matrix", "audit-trail", str(root), "--json"])

            self.assertEqual(returncode, 0)
            self.assertEqual(stderr.getvalue(), "")
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["feature_id"], "audit-trail")
            self.assertEqual(payload["summary"]["verified"], 1)

        with TemporaryDirectory() as tmp:
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                missing_code = main(["verify", "matrix", "missing-feature", tmp, "--json"])

            self.assertEqual(missing_code, 1)
            self.assertEqual(stderr.getvalue(), "")
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["evidence"]["has_native_files"])

            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                invalid_code = main(["verify", "matrix", "Bad Slug", tmp, "--json"])

            self.assertEqual(invalid_code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_builder_is_local_only_and_renderers_are_pure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature(root)

            with patch.object(
                subprocess,
                "run",
                side_effect=AssertionError("subprocess should not run"),
            ), patch.object(
                urllib.request,
                "urlopen",
                side_effect=AssertionError("network should not run"),
            ), patch.object(
                os,
                "getenv",
                side_effect=AssertionError("env should not be read"),
            ):
                matrix = build_verification_matrix(root, "audit-trail")
                json_output = render_verification_matrix_json(matrix)
                text_output = render_verification_matrix_text(matrix)

            payload = json.loads(json_output)
            self.assertEqual(payload["feature_id"], "audit-trail")
            self.assertIn("matrix", payload)
            self.assertIn("evidence", payload)
            self.assertIn("recommended_commands", payload)
            self.assertIn("safety_notes", payload)
            self.assertIn("Verification matrix:", text_output)
            self.assertIn("does not prove tests were run", text_output)
