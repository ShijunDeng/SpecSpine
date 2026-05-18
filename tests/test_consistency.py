import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import main
from specspine.consistency import (
    build_consistency_report,
    render_consistency_json,
    render_consistency_text,
)
from specspine.features import InvalidFeatureSlug


def write_consistency_fixture(root: Path, slug: str = "add-dark-mode") -> None:
    for directory in (
        "src/myapp",
        "src/specspine",
        "tests/unit",
        "tests",
        "docs",
        "specs/features",
        "execution/features",
        "quality/features",
    ):
        (root / directory).mkdir(parents=True, exist_ok=True)

    (root / "src/specspine/theme.py").write_text(
        "FEATURE_ID = 'add-dark-mode'\n",
        encoding="utf-8",
    )
    (root / "src/myapp/widget.py").write_text(
        "FEATURE_ID = 'add-dark-mode'\n",
        encoding="utf-8",
    )
    (root / "src/myapp/unlisted.py").write_text(
        "FEATURE_ID = 'add-dark-mode'\n",
        encoding="utf-8",
    )
    (root / "tests/test_theme.py").write_text(
        "from specspine import theme\n\n"
        "class ThemeTests:\n"
        "    pass\n",
        encoding="utf-8",
    )
    (root / "tests/unit/test_widget.py").write_text(
        "class WidgetTests:\n"
        "    pass\n",
        encoding="utf-8",
    )
    (root / "tests/unit/test_unlisted.py").write_text(
        "FEATURE_ID = 'add-dark-mode'\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "Run `specspine consistency scan . --feature add-dark-mode --json`.\n",
        encoding="utf-8",
    )
    (root / "AGENTS.md").write_text(
        "Use `specspine consistency scan . --json` before implementation.\n",
        encoding="utf-8",
    )
    (root / "docs/theme.md").write_text(
        "Feature add-dark-mode documents theme behavior.\n",
        encoding="utf-8",
    )
    (root / "specs/features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Add dark mode",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Acceptance Criteria",
                "",
                "- [x] AC001: Users can enable dark mode.",
                "",
                "## Traceability Notes",
                "",
                "- Implementation: `src/specspine/theme.py`.",
                "- Secondary implementation: `src/myapp/widget.py`.",
                "- Tests: `tests/test_theme.py::ThemeTests`.",
                "- Unit tests: `tests/unit/test_widget.py::WidgetTests`.",
                "- Docs: `README.md`, `AGENTS.md`, and `docs/theme.md`.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution/features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Add dark mode Execution",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Tasks",
                "",
                "- [x] TASK001: AC001 implemented in `src/specspine/theme.py`.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "quality/features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Add dark mode Quality",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Required Checks",
                "",
                "- [x] AC001 implementation and docs reviewed.",
                "",
                "## Test Coverage",
                "",
                "- [x] AC001 -> tests/test_theme.py::ThemeTests",
                "",
                "## Test Plan",
                "",
                "- Run `PYTHONPATH=src python3 -m unittest tests.test_theme`.",
                "",
                "## Release Readiness",
                "",
                "- [x] No known blockers remain.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class ConsistencyReportTests(TestCase):
    def test_scan_links_feature_files_to_code_tests_docs_and_changed_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_consistency_fixture(root)

            report = build_consistency_report(
                root,
                feature_filter="add-dark-mode",
                changed_files=("src/specspine/theme.py", "docs/theme.md"),
            )

            self.assertEqual(report.feature_filter, "add-dark-mode")
            self.assertEqual(report.summary["features_scanned"], 1)
            feature = report.features[0]
            self.assertEqual(feature.status, "validated")
            self.assertEqual(feature.missing_files, ())
            self.assertEqual(feature.summary["checks_fail"], 0)
            self.assertEqual(feature.summary["checks_warn"], 0)
            self.assertIn(
                "src/specspine/theme.py",
                {reference.path for reference in feature.implementation_references},
            )
            self.assertIn(
                "src/myapp/widget.py",
                {reference.path for reference in feature.implementation_references},
            )
            self.assertIn(
                "src/myapp/unlisted.py",
                {reference.path for reference in feature.implementation_references},
            )
            self.assertIn(
                "tests/test_theme.py",
                {reference.path for reference in feature.test_references},
            )
            self.assertIn(
                "tests/unit/test_widget.py",
                {reference.path for reference in feature.test_references},
            )
            self.assertIn(
                "tests/unit/test_unlisted.py",
                {reference.path for reference in feature.test_references},
            )
            self.assertTrue(all(reference.exists for reference in feature.test_references))
            self.assertIn(
                "README.md",
                {reference.path for reference in feature.documentation_references},
            )
            self.assertIn(
                "AGENTS.md",
                {reference.path for reference in feature.documentation_references},
            )
            self.assertEqual(
                {reference.path for reference in feature.changed_references},
                {"src/specspine/theme.py", "docs/theme.md"},
            )

    def test_scan_all_features_is_stable_json_and_text(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_consistency_fixture(root)

            report = build_consistency_report(root)
            payload = json.loads(render_consistency_json(report))
            text = render_consistency_text(report)

            self.assertEqual(payload["summary"]["features_scanned"], 1)
            self.assertEqual(payload["features"][0]["feature_id"], "add-dark-mode")
            self.assertIn("Spec-code consistency report", text)
            self.assertIn("add-dark-mode", text)
            self.assertIn("Recommended commands are advisory", text)

    def test_missing_feature_returns_structured_report(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            report = build_consistency_report(root, feature_filter="missing-feature")

            self.assertEqual(report.summary["features_scanned"], 1)
            self.assertEqual(report.summary["checks_fail"], 1)
            feature = report.features[0]
            self.assertEqual(feature.feature_id, "missing-feature")
            self.assertIsNone(feature.status)
            self.assertEqual(feature.source_files, ())
            self.assertEqual(len(feature.missing_files), 3)

    def test_invalid_slug_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(InvalidFeatureSlug):
                build_consistency_report(Path(tmp), feature_filter="Bad Slug")

    def test_consistency_scan_cli_exit_codes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_consistency_fixture(root)

            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                returncode = main(
                    [
                        "consistency",
                        "scan",
                        str(root),
                        "--feature",
                        "add-dark-mode",
                        "--json",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_filter"], "add-dark-mode")
            self.assertEqual(stderr.getvalue(), "")

            stdout = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                missing_returncode = main(
                    [
                        "consistency",
                        "scan",
                        str(root),
                        "--feature",
                        "missing-feature",
                        "--json",
                    ]
                )
            self.assertEqual(missing_returncode, 1)
            self.assertEqual(json.loads(stdout.getvalue())["summary"]["checks_fail"], 1)

            stderr = StringIO()
            with redirect_stdout(StringIO()), redirect_stderr(stderr):
                invalid_returncode = main(
                    [
                        "consistency",
                        "scan",
                        str(root),
                        "--feature",
                        "Bad Slug",
                    ]
                )
            self.assertEqual(invalid_returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())
