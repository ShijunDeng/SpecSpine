import json
import os
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.impact import build_test_impact_report
from specspine.workspace import init_workspace


def write_python_impact_workspace(root: Path) -> None:
    (root / "src" / "specspine").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "src" / "specspine" / "__init__.py").write_text(
        "__version__ = '0.0.0'\n",
        encoding="utf-8",
    )
    (root / "src" / "specspine" / "cli.py").write_text(
        "def main():\n    return 0\n",
        encoding="utf-8",
    )
    (root / "src" / "specspine" / "impact.py").write_text(
        "class ImpactReport:\n    pass\n",
        encoding="utf-8",
    )
    (root / "tests" / "test_cli.py").write_text(
        "from specspine.cli import main\n\n"
        "def test_main():\n"
        "    assert main() == 0\n",
        encoding="utf-8",
    )
    (root / "tests" / "test_impact.py").write_text(
        "import specspine.impact\n\n"
        "def test_impact_import():\n"
        "    assert specspine.impact is not None\n",
        encoding="utf-8",
    )


def write_feature_bundle(root: Path, slug: str = "test-impact-packet") -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "tests" / "test_impact_feature.py").write_text(
        "# feature coverage target\n",
        encoding="utf-8",
    )
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Test impact packet",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Acceptance Criteria",
                "",
                "- [x] Impact report recommends affected tests.",
                "- [x] Feature coverage targets are included.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Test impact packet Execution",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Tasks",
                "",
                "- [x] Build impact graph.",
                "- [x] Add feature coverage integration.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Test impact packet Quality",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Required Checks",
                "",
                "- [x] Impact report tests pass.",
                "",
                "## Test Coverage",
                "",
                "- [x] AC001 -> tests/test_impact_feature.py",
                "- [x] AC002 -> tests/test_cli.py::ImpactCliTests::test_feature",
                "",
                "## Test Plan",
                "",
                "- Run `PYTHONPATH=src python3 -m unittest tests.test_impact`.",
                "",
                "## Release Readiness",
                "",
                "- [x] Local-only behavior is reviewed.",
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


class ImpactCommandTests(TestCase):
    def test_json_full_graph_recommends_discovery_without_changed_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_python_impact_workspace(root)

            code, stdout, stderr = run_cli(["tests", "impact", str(root), "--json"])

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["changed_files"], [])
            self.assertIn(
                "PYTHONPATH=src python3 -m unittest discover -s tests",
                payload["recommended_commands"],
            )
            modules = {module["module"]: module for module in payload["source_modules"]}
            self.assertEqual(modules["specspine.cli"]["test_files"], ["tests/test_cli.py"])
            self.assertEqual(
                modules["specspine.impact"]["test_files"],
                ["tests/test_impact.py"],
            )
            tests = {test["path"]: test for test in payload["test_files"]}
            self.assertEqual(tests["tests/test_cli.py"]["imports"], ["specspine.cli"])

    def test_changed_source_recommends_impacted_unittest_module(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_python_impact_workspace(root)

            code, stdout, stderr = run_cli(
                [
                    "tests",
                    "impact",
                    str(root),
                    "--json",
                    "--changed",
                    "src/specspine/impact.py",
                ]
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["changed_files"], ["src/specspine/impact.py"])
            self.assertIn(
                "PYTHONPATH=src python3 -m unittest tests.test_impact",
                payload["recommended_commands"],
            )
            self.assertFalse(payload["recommendations"][0]["fallback"])

    def test_changed_test_recommends_that_test_module(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_python_impact_workspace(root)

            code, stdout, stderr = run_cli(
                [
                    "tests",
                    "impact",
                    str(root),
                    "--json",
                    "--changed",
                    "tests/test_cli.py",
                ]
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(
                payload["recommended_commands"],
                ["PYTHONPATH=src python3 -m unittest tests.test_cli"],
            )
            self.assertEqual(
                payload["recommendations"][0]["reason"],
                "Changed file is itself a unittest module.",
            )

    def test_unknown_changed_file_adds_full_discovery_fallback(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_python_impact_workspace(root)

            code, stdout, stderr = run_cli(
                [
                    "tests",
                    "impact",
                    str(root),
                    "--json",
                    "--changed",
                    "README.md",
                ]
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertTrue(payload["recommendations"][0]["fallback"])
            self.assertEqual(
                payload["recommended_commands"],
                ["PYTHONPATH=src python3 -m unittest discover -s tests"],
            )

    def test_feature_flag_includes_coverage_targets_and_commands(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_python_impact_workspace(root)
            write_feature_bundle(root)

            code, stdout, stderr = run_cli(
                [
                    "tests",
                    "impact",
                    str(root),
                    "--json",
                    "--feature",
                    "test-impact-packet",
                ]
            )

            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["feature"]["feature_id"], "test-impact-packet")
            self.assertTrue(payload["feature"]["has_native_files"])
            self.assertEqual(
                payload["feature"]["coverage_targets"],
                [
                    "tests/test_cli.py",
                    "tests/test_impact_feature.py",
                ],
            )
            self.assertIn(
                "PYTHONPATH=src python3 -m unittest tests.test_cli",
                payload["feature"]["recommended_commands"],
            )
            self.assertIn(
                "PYTHONPATH=src python3 -m unittest tests.test_impact_feature",
                payload["feature"]["recommended_commands"],
            )

    def test_invalid_feature_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_python_impact_workspace(root)

            code, _stdout, stderr = run_cli(
                ["tests", "impact", str(root), "--json", "--feature", "Bad_Slug"]
            )

            self.assertEqual(code, 2)
            self.assertIn("Invalid feature slug", stderr)

    def test_missing_feature_returns_one_with_report(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_python_impact_workspace(root)

            code, stdout, stderr = run_cli(
                ["tests", "impact", str(root), "--json", "--feature", "missing-feature"]
            )

            self.assertEqual(code, 1, stderr)
            payload = json.loads(stdout)
            self.assertFalse(payload["feature"]["has_native_files"])
            self.assertEqual(payload["feature"]["missing_files"], [
                "specs/features/missing-feature.md",
                "execution/features/missing-feature.md",
                "quality/features/missing-feature.md",
            ])

    def test_report_is_read_only_and_does_not_use_external_calls(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_python_impact_workspace(root)

            class GuardedEnviron(dict):
                def __getitem__(self, key: str) -> str:
                    if "TOKEN" in key.upper():
                        raise AssertionError(f"unexpected token read: {key}")
                    return super().__getitem__(key)

                def get(self, key: str, default: object = None) -> object:
                    if "TOKEN" in key.upper():
                        raise AssertionError(f"unexpected token read: {key}")
                    return super().get(key, default)

            with patch("subprocess.run", side_effect=AssertionError("unexpected process")):
                with patch("socket.create_connection", side_effect=AssertionError("unexpected network")):
                    with patch("urllib.request.urlopen", side_effect=AssertionError("unexpected network")):
                        with patch("os.environ", GuardedEnviron(os.environ)):
                            report = build_test_impact_report(
                                root,
                                changed_files=("src/specspine/cli.py",),
                            )

            self.assertEqual(report.changed_files, ("src/specspine/cli.py",))
            self.assertIn(
                "PYTHONPATH=src python3 -m unittest tests.test_cli",
                report.recommended_commands,
            )
