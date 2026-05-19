import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import main
from specspine.features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    create_feature_bundle,
)
from specspine.scaffold import (
    ScaffoldCoverageLink,
    ScaffoldRemediationStep,
    ScaffoldReport,
    ScaffoldSkippedCriterion,
    ScaffoldTestMethod,
    _ac_id_snake,
    _build_remediation_plan,
    _existing_coverage_links,
    _extract_ac_keyword,
    _generate_test_class,
    _generate_test_method,
    _slug_to_camel,
    _update_quality_file,
    build_ac_test_scaffold,
    render_scaffold_json,
    render_scaffold_text,
)


def _write_feature_with_ac(root: Path, slug: str, ac_lines: list[str], status: str = "planned") -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    ac_block = "\n".join(f"- [ ] {line}" for line in ac_lines)
    (root / "specs" / "features" / f"{slug}.md").write_text(
        f"# Test Feature\n\nFeature ID: {slug}\nStatus: {status}\n\n## Acceptance Criteria\n\n{ac_block}\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        f"# Test Feature Execution\n\nFeature ID: {slug}\nStatus: {status}\n\n## Tasks\n\n- [ ] Do something.\n",
        encoding="utf-8",
    )
    (root / "quality" / "features" / f"{slug}.md").write_text(
        f"# Test Feature Quality\n\nFeature ID: {slug}\nStatus: {status}\n\n## Required Checks\n\n- [ ] Check something.\n\n## Test Coverage\n\n\n## Test Plan\n\n- Run tests.\n",
        encoding="utf-8",
    )


class TestSlugToCamel(TestCase):
    def test_simple_slug(self) -> None:
        self.assertEqual(_slug_to_camel("dark-mode"), "DarkMode")

    def test_single_word(self) -> None:
        self.assertEqual(_slug_to_camel("login"), "Login")

    def test_multiple_hyphens(self) -> None:
        self.assertEqual(_slug_to_camel("add-user-profile-page"), "AddUserProfilePage")


class TestAcIdSnake(TestCase):
    def test_uppercase_ac(self) -> None:
        self.assertEqual(_ac_id_snake("AC001"), "ac001")

    def test_already_lower(self) -> None:
        self.assertEqual(_ac_id_snake("ac002"), "ac002")


class TestExtractAcKeyword(TestCase):
    def test_can_keyword(self) -> None:
        self.assertEqual(_extract_ac_keyword("Users can enable dark mode"), "enable")

    def test_should_keyword(self) -> None:
        self.assertEqual(_extract_ac_keyword("System should validate input"), "validate")

    def test_must_keyword(self) -> None:
        self.assertEqual(_extract_ac_keyword("Admin must approve requests"), "approve")

    def test_no_keyword_uses_first_word(self) -> None:
        self.assertEqual(_extract_ac_keyword("Dark mode toggle"), "dark")

    def test_empty_string(self) -> None:
        self.assertEqual(_extract_ac_keyword(""), "behavior")


class TestGenerateTestMethod(TestCase):
    def test_basic_method(self) -> None:
        result = _generate_test_method("AC001", "Users can enable dark mode", "dark-mode")
        self.assertEqual(result["method_name"], "test_ac001_enable")
        self.assertEqual(result["docstring"], "Users can enable dark mode")
        self.assertIn("self.fail", result["body"])


class TestGenerateTestClass(TestCase):
    def test_class_with_methods(self) -> None:
        methods = [
            {"method_name": "test_ac001_enable", "docstring": "Enable dark mode", "body": 'self.fail("TODO")'},
        ]
        source = _generate_test_class("dark-mode", methods)
        self.assertIn("class DarkModeScaffoldTests(unittest.TestCase)", source)
        self.assertIn("def test_ac001_enable(self)", source)
        self.assertIn("Enable dark mode", source)

    def test_class_no_methods(self) -> None:
        source = _generate_test_class("empty-feature", [])
        self.assertIn("class EmptyFeatureScaffoldTests(unittest.TestCase)", source)
        self.assertIn("test_no_criteria", source)

    def test_multiple_methods_separated(self) -> None:
        methods = [
            {"method_name": "test_ac001_enable", "docstring": "Enable", "body": 'self.fail("TODO")'},
            {"method_name": "test_ac002_disable", "docstring": "Disable", "body": 'self.fail("TODO")'},
        ]
        source = _generate_test_class("dark-mode", methods)
        self.assertIn("test_ac001_enable", source)
        self.assertIn("test_ac002_disable", source)


class TestExistingCoverageLinks(TestCase):
    def test_no_quality_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = _existing_coverage_links(root, "test-feature")
            self.assertEqual(result, set())

    def test_empty_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "quality" / "features").mkdir(parents=True)
            (root / "quality" / "features" / "test-feature.md").write_text(
                "# Quality\n\nFeature ID: test-feature\n\n## Test Coverage\n\n",
                encoding="utf-8",
            )
            result = _existing_coverage_links(root, "test-feature")
            self.assertEqual(result, set())


class TestUpdateQualityFile(TestCase):
    def test_no_links_returns_false(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "quality" / "features").mkdir(parents=True)
            (root / "quality" / "features" / "test-feature.md").write_text(
                "# Quality\n\nFeature ID: test-feature\n\n## Test Coverage\n\n\n## Test Plan\n",
                encoding="utf-8",
            )
            result = _update_quality_file(root, "test-feature", [])
            self.assertFalse(result)

    def test_appends_links(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "quality" / "features").mkdir(parents=True)
            (root / "quality" / "features" / "test-feature.md").write_text(
                "# Quality\n\nFeature ID: test-feature\n\n## Test Coverage\n\n\n## Test Plan\n",
                encoding="utf-8",
            )
            links = [{"ac_id": "AC001", "target_path": "tests/test_scaffold.py"}]
            result = _update_quality_file(root, "test-feature", links)
            self.assertTrue(result)
            content = (root / "quality" / "features" / "test-feature.md").read_text(encoding="utf-8")
            self.assertIn("AC001", content)
            self.assertIn("tests/test_scaffold.py", content)


class TestBuildRemediationPlan(TestCase):
    def test_creates_steps(self) -> None:
        uncovered = [
            {"ac_id": "AC001", "ac_text": "Users can login"},
        ]
        plan = _build_remediation_plan("user-auth", uncovered, "tests/test_user_auth_scaffold.py", "UserAuthScaffoldTests")
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0].ac_id, "AC001")
        self.assertIn("test_ac001", plan[0].method_name)


class TestBuildAcTestScaffold(TestCase):
    def test_basic_scaffold(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "test-feature", ["Users can login", "Users can logout"])
            report = build_ac_test_scaffold(root, "test-feature")
            self.assertEqual(report.feature_id, "test-feature")
            self.assertEqual(len(report.test_methods), 2)
            self.assertEqual(len(report.coverage_links), 2)
            self.assertEqual(len(report.skipped_criteria), 0)

    def test_method_naming(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "test-feature", ["Users can login"])
            report = build_ac_test_scaffold(root, "test-feature")
            method = report.test_methods[0]
            self.assertIn("test_ac001", method.method_name)

    def test_scaffold_file_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "my-feature", ["Users can do something"])
            report = build_ac_test_scaffold(root, "my-feature")
            self.assertEqual(report.scaffold_file, "tests/test_my_feature_scaffold.py")

    def test_safety_notes_present(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "test-feature", ["Users can login"])
            report = build_ac_test_scaffold(root, "test-feature")
            self.assertGreater(len(report.safety_notes), 0)
            for note in report.safety_notes:
                self.assertIsInstance(note, str)

    def test_remediation_plan_populated(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "test-feature", ["Users can login"])
            report = build_ac_test_scaffold(root, "test-feature")
            self.assertEqual(len(report.remediation_plan), 1)
            self.assertEqual(report.remediation_plan[0].ac_id, "AC001")

    def test_skips_covered_ac(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "test-feature", ["Users can login", "Users can logout"])
            quality = root / "quality" / "features" / "test-feature.md"
            content = quality.read_text(encoding="utf-8")
            content = content.replace(
                "## Test Coverage\n\n",
                "## Test Coverage\n\n- [x] AC001 -> specs/features/test-feature.md\n\n",
                1,
            )
            (root / "specs" / "features" / "test-feature.md").touch()
            quality.write_text(content, encoding="utf-8")
            report = build_ac_test_scaffold(root, "test-feature")
            skipped = [s for s in report.skipped_criteria if s.ac_id == "AC001"]
            self.assertEqual(len(skipped), 1)

    def test_no_acceptance_criteria(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "empty-feature", [])
            report = build_ac_test_scaffold(root, "empty-feature")
            self.assertEqual(len(report.test_methods), 0)
            self.assertEqual(len(report.coverage_links), 0)


class TestRenderScaffoldJson(TestCase):
    def test_json_structure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "test-feature", ["Users can login"])
            report = build_ac_test_scaffold(root, "test-feature")
            output = render_scaffold_json(report)
            data = json.loads(output)
            self.assertEqual(data["feature_id"], "test-feature")
            self.assertIn("test_methods", data)
            self.assertIn("coverage_links", data)
            self.assertIn("safety_notes", data)

    def test_json_is_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "test-feature", ["Users can login"])
            report = build_ac_test_scaffold(root, "test-feature")
            output = render_scaffold_json(report)
            json.loads(output)


class TestRenderScaffoldText(TestCase):
    def test_text_contains_feature_id(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "test-feature", ["Users can login"])
            report = build_ac_test_scaffold(root, "test-feature")
            output = render_scaffold_text(report)
            self.assertIn("test-feature", output)

    def test_text_contains_target(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "test-feature", ["Users can login"])
            report = build_ac_test_scaffold(root, "test-feature")
            output = render_scaffold_text(report)
            self.assertIn("Test methods:", output)


class TestCliScaffoldTests(TestCase):
    def test_scaffold_tests_help(self) -> None:
        import sys
        with self.assertRaises(SystemExit) as cm:
            main(["scaffold", "tests", "--help"])
        self.assertEqual(cm.exception.code, 0)

    def test_scaffold_tests_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "cli-test", ["Users can login"])
            code = main(["scaffold", "tests", "cli-test", tmp, "--json"])
            self.assertEqual(code, 0)

    def test_scaffold_tests_text(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "cli-test", ["Users can login"])
            code = main(["scaffold", "tests", "cli-test", tmp])
            self.assertEqual(code, 0)

    def test_scaffold_missing_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            code = main(["scaffold", "tests", "nonexistent", tmp])
            self.assertEqual(code, 1)

    def test_scaffold_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            code = main(["scaffold", "tests", "INVALID SLUG", tmp])
            self.assertEqual(code, 2)

    def test_scaffold_output_dir(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "dir-test", ["Users can login"])
            out_dir = root / "output"
            code = main(["scaffold", "tests", "dir-test", tmp, "--output-dir", str(out_dir), "--json"])
            self.assertEqual(code, 0)
            self.assertTrue(out_dir.exists())

    def test_scaffold_force_overwrite(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "force-test", ["Users can login"])
            out_dir = root / "output"
            out_dir.mkdir()
            (out_dir / "test_force_test_scaffold.py").write_text("old", encoding="utf-8")
            code = main(["scaffold", "tests", "force-test", tmp, "--output-dir", str(out_dir), "--force", "--json"])
            self.assertEqual(code, 0)

    def test_scaffold_without_force_existing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "noforce-test", ["Users can login"])
            (root / "tests").mkdir()
            (root / "tests" / "test_noforce_test_scaffold.py").write_text("old", encoding="utf-8")
            code = main(["scaffold", "tests", "noforce-test", tmp, "--json"])
            self.assertEqual(code, 1)

    def test_scaffold_updates_quality(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "quality-test", ["Users can login"])
            code = main(["scaffold", "tests", "quality-test", tmp, "--update-quality", "--json"])
            self.assertEqual(code, 0)
            quality = root / "quality" / "features" / "quality-test.md"
            content = quality.read_text(encoding="utf-8")
            self.assertIn("AC001", content)


class TestScaffoldSafety(TestCase):
    def test_no_subprocess_calls(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "safety-test", ["Users can login"])
            report = build_ac_test_scaffold(root, "safety-test")
            for method in report.test_methods:
                self.assertIn("self.fail", method.body)
                self.assertNotIn("subprocess", method.body)

    def test_generated_source_has_imports(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_with_ac(root, "import-test", ["Users can login"])
            report = build_ac_test_scaffold(root, "import-test")
            methods_data = [
                {"method_name": m.method_name, "docstring": m.docstring, "body": m.body}
                for m in report.test_methods
            ]
            source = _generate_test_class("import-test", methods_data)
            self.assertIn("import unittest", source)
