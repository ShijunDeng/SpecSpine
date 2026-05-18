from __future__ import annotations

import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from specspine.cli import main
from specspine.hygiene import build_hygiene_scan_report


def _join(*parts: str) -> str:
    return "".join(parts)


def _lower_marker() -> str:
    return _join("m", "cp")


def _remote_flag() -> str:
    return _join("--", "github", "-token")


def _credential_prefix() -> str:
    return _join("g", "hp_")


def _blocked_source_path() -> str:
    return "src/specspine/" + _lower_marker() + ".py"


class HygieneReportTests(unittest.TestCase):
    def _run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_clean_fixture_json_and_text(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src" / "pkg" / "app.py"
            source.parent.mkdir(parents=True)
            source.write_text("VALUE = 1\n", encoding="utf-8")

            code, stdout, stderr = self._run_cli(
                "hygiene",
                "scan",
                str(root),
                "--json",
            )

            self.assertEqual(code, 0, stderr)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(
                set(payload),
                {
                    "changed_files",
                    "findings",
                    "recommended_commands",
                    "root",
                    "safety_notes",
                    "summary",
                },
            )
            self.assertEqual(payload["findings"], [])
            self.assertEqual(payload["summary"]["findings_total"], 0)
            self.assertEqual(payload["summary"]["files_scanned"], 1)
            self.assertEqual(payload["summary"]["files_skipped"], 0)

            code, stdout, stderr = self._run_cli("hygiene", "scan", str(root))

            self.assertEqual(code, 0, stderr)
            self.assertIn("Repository hygiene scan:", stdout)
            self.assertIn("Summary:", stdout)
            self.assertIn("Findings:", stdout)
            self.assertIn("- None.", stdout)
            self.assertIn("Recommended commands:", stdout)
            self.assertIn("Safety notes:", stdout)

    def test_generated_artifact_findings(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "__pycache__").mkdir()
            (root / ".pytest_cache").mkdir()
            (root / ".DS_Store").write_text("", encoding="utf-8")
            (root / "loose.pyc").write_bytes(b"cache")
            (root / "loose.pyo").write_bytes(b"cache")

            report = build_hygiene_scan_report(root)

            paths = {finding.path for finding in report.findings}
            sources = {finding.source for finding in report.findings}
            self.assertEqual(report.summary["findings_total"], 5)
            self.assertEqual(report.summary["by_category"]["generated_artifact"], 5)
            self.assertTrue(all(finding.severity == "low" for finding in report.findings))
            self.assertIn("__pycache__/", paths)
            self.assertIn(".pytest_cache/", paths)
            self.assertIn(".DS_Store", paths)
            self.assertIn("loose.pyc", paths)
            self.assertIn("loose.pyo", paths)
            self.assertIn("*.pyc", sources)
            self.assertIn("*.pyo", sources)

    def test_forbidden_path_findings(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / _blocked_source_path()
            target.parent.mkdir(parents=True)
            target.write_text("VALUE = 1\n", encoding="utf-8")

            report = build_hygiene_scan_report(root)

            self.assertEqual(report.summary["by_category"]["forbidden_path"], 1)
            finding = next(
                item for item in report.findings if item.category == "forbidden_path"
            )
            self.assertEqual(finding.id, "forbidden-path-remnant")
            self.assertEqual(finding.severity, "critical")
            self.assertEqual(finding.path, _blocked_source_path())

    def test_forbidden_content_findings_include_line_numbers_without_values(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src" / "pkg" / "sample.txt"
            source.parent.mkdir(parents=True)
            sensitive_value = _credential_prefix() + "abc123"
            source.write_text(
                "\n".join(
                    [
                        "clean",
                        _lower_marker(),
                        _remote_flag(),
                        sensitive_value,
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            code, stdout, stderr = self._run_cli(
                "hygiene",
                "scan",
                str(root),
                "--json",
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertNotIn(sensitive_value, stdout)
            by_source = {
                finding["source"]: finding
                for finding in payload["findings"]
                if finding["category"] == "forbidden_content"
            }
            self.assertEqual(by_source[_lower_marker()]["line"], 2)
            self.assertEqual(by_source[_remote_flag()]["line"], 3)
            self.assertEqual(by_source[_credential_prefix()]["line"], 4)
            self.assertTrue(
                all(finding["severity"] == "high" for finding in by_source.values())
            )

    def test_changed_path_normalization_and_content_exclusions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src" / "specspine" / "hygiene.py"
            test_file = root / "tests" / "test_hygiene.py"
            source.parent.mkdir(parents=True)
            test_file.parent.mkdir(parents=True)
            source.write_text(_lower_marker() + "\n", encoding="utf-8")
            test_file.write_text(_remote_flag() + "\n", encoding="utf-8")

            report = build_hygiene_scan_report(
                root,
                changed_files=(
                    str(source),
                    "./src/specspine/hygiene.py",
                    "tests/test_hygiene.py",
                ),
            )

            self.assertEqual(
                report.changed_files,
                ("src/specspine/hygiene.py", "tests/test_hygiene.py"),
            )
            self.assertEqual(report.findings, ())
            self.assertEqual(
                report.summary["skipped_reasons"]["content_scan_excluded"],
                2,
            )

    def test_binary_files_are_skipped_without_findings(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "blob.bin").write_bytes(b"\0not text")

            report = build_hygiene_scan_report(root)

            self.assertEqual(report.findings, ())
            self.assertEqual(report.summary["files_skipped"], 1)
            self.assertEqual(report.summary["skipped_reasons"]["binary"], 1)

    def test_strict_exit_code_for_high_findings(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "src" / "pkg" / "sample.txt"
            source.parent.mkdir(parents=True)
            source.write_text(_remote_flag() + "\n", encoding="utf-8")

            code, _stdout, stderr = self._run_cli("hygiene", "scan", str(root))
            self.assertEqual(code, 0, stderr)

            code, _stdout, stderr = self._run_cli(
                "hygiene",
                "scan",
                str(root),
                "--strict",
            )
            self.assertEqual(code, 1, stderr)


if __name__ == "__main__":
    unittest.main()
