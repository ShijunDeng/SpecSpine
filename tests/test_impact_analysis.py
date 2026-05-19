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
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
)
from specspine.impact_analysis import (
    IMPACT_TYPE_CODE,
    IMPACT_TYPE_FEATURE,
    IMPACT_TYPE_TEST,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    ImpactAnalysis,
    ImpactItem,
    _compute_risk_score,
    _extract_acceptance_criteria,
    _extract_slugs_from_text,
    _find_affected_code,
    _find_affected_features,
    _find_affected_tests,
    _generate_mitigation_steps,
    _module_name,
    _read_text,
    _relative_path,
    analyze_feature_impact,
    render_impact_json,
    render_impact_text,
)
from specspine.workspace import init_workspace


def write_feature_bundle(
    root: Path,
    slug: str,
    *,
    status: str = "proposed",
    priority: str = "medium",
    effort: str = "unknown",
    milestone: str = "unassigned",
    acceptance_criteria: list[str] | None = None,
    tasks: list[str] | None = None,
    extra_content: str = "",
) -> None:
    if acceptance_criteria is None:
        acceptance_criteria = ["Users get value from the feature."]
    if tasks is None:
        tasks = ["Implement the feature."]

    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)

    spec_lines = [
        f"# {slug.title()}",
        "",
        f"Feature ID: {slug}",
        f"Status: {status}",
        f"Priority: {priority}",
        "Owner: test-owner",
        f"Milestone: {milestone}",
        "Target Release: unassigned",
        "Project: unassigned",
        f"Effort: {effort}",
        "",
        "## Acceptance Criteria",
        "",
        *[f"- [ ] {item}" for item in acceptance_criteria],
    ]
    if extra_content:
        spec_lines.append("")
        spec_lines.append(extra_content)

    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(spec_lines) + "\n",
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
                *[f"- [ ] {item}" for item in tasks],
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
                "- [ ] Quality checks pass.",
                "",
                "## Test Coverage",
                "",
                "- [ ] AC001 -> tests/test_feature.py",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_source_module(root: Path, module_path: str, content: str) -> None:
    full_path = root / module_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")


def write_test_file(root: Path, test_path: str, content: str) -> None:
    full_path = root / test_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(argv)
    except SystemExit as e:
        code = e.code if e.code is not None else 0
    return code, stdout.getvalue(), stderr.getvalue()


class RelativePathTests(TestCase):
    def test_relative_path_within_root(self) -> None:
        root = Path("/tmp/test")
        path = root / "src" / "module.py"
        result = _relative_path(root, path)
        self.assertEqual(result, "src/module.py")

    def test_relative_path_outside_root(self) -> None:
        root = Path("/tmp/test")
        path = Path("/other/file.py")
        result = _relative_path(root, path)
        self.assertEqual(result, "/other/file.py")


class ReadTextTests(TestCase):
    def test_read_existing_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "test.txt"
            test_file.write_text("hello", encoding="utf-8")
            result = _read_text(test_file)
            self.assertEqual(result, "hello")

    def test_read_nonexistent_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = _read_text(root / "missing.txt")
            self.assertEqual(result, "")


class ExtractAcceptanceCriteriaTests(TestCase):
    def test_extract_acs_from_spec(self) -> None:
        content = """# Test
## Acceptance Criteria

- [ ] First criterion
- [ ] Second criterion
## Other Section
"""
        result = _extract_acceptance_criteria(content)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][1], "First criterion")
        self.assertEqual(result[1][1], "Second criterion")

    def test_no_acceptance_criteria_section(self) -> None:
        content = """# Test
## Other Section
"""
        result = _extract_acceptance_criteria(content)
        self.assertEqual(result, [])

    def test_acs_with_ids(self) -> None:
        content = """## Acceptance Criteria

- [ ] AC001 - User can login
- [ ] AC002 - User can logout
"""
        result = _extract_acceptance_criteria(content)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], "AC001")
        self.assertEqual(result[1][0], "AC002")


class ExtractSlugsFromTextTests(TestCase):
    def test_feature_id_reference(self) -> None:
        text = "This depends on Feature ID: base-feature"
        result = _extract_slugs_from_text(text, "current", {"base-feature"})
        self.assertIn("base-feature", result)

    def test_depends_on_reference(self) -> None:
        text = "depends on auth"
        result = _extract_slugs_from_text(text, "app", {"auth"})
        self.assertIn("auth", result)

    def test_requires_reference(self) -> None:
        text = "This feature requires core"
        result = _extract_slugs_from_text(text, "plugin", {"core"})
        self.assertIn("core", result)

    def test_filters_out_current_slug(self) -> None:
        text = "Feature ID: self-ref"
        result = _extract_slugs_from_text(text, "self-ref", {"self-ref"})
        self.assertEqual(result, [])

    def test_filters_invalid_slugs(self) -> None:
        text = "depends on nonexistent"
        result = _extract_slugs_from_text(text, "app", {"auth"})
        self.assertEqual(result, [])


class FindAffectedFeaturesTests(TestCase):
    def test_no_dependent_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            result = _find_affected_features("alpha", root)
            self.assertEqual(result, [])

    def test_finds_dependent_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "base")
            write_feature_bundle(
                root,
                "dependent",
                extra_content="depends on base",
            )
            result = _find_affected_features("base", root)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].id, "dependent")

    def test_multiple_dependent_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "core")
            write_feature_bundle(
                root,
                "feat-a",
                extra_content="depends on core",
            )
            write_feature_bundle(
                root,
                "feat-b",
                extra_content="requires core",
            )
            result = _find_affected_features("core", root)
            self.assertEqual(len(result), 2)
            ids = {item.id for item in result}
            self.assertIn("feat-a", ids)
            self.assertIn("feat-b", ids)

    def test_high_priority_dependency_has_high_severity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "lib")
            write_feature_bundle(
                root,
                "app",
                priority="high",
                extra_content="depends on lib",
            )
            result = _find_affected_features("lib", root)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].severity, SEVERITY_HIGH)

    def test_medium_priority_dependency_has_medium_severity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "lib")
            write_feature_bundle(
                root,
                "app",
                priority="medium",
                extra_content="depends on lib",
            )
            result = _find_affected_features("lib", root)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].severity, SEVERITY_MEDIUM)

    def test_low_priority_dependency_has_low_severity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "lib")
            write_feature_bundle(
                root,
                "app",
                priority="low",
                extra_content="depends on lib",
            )
            result = _find_affected_features("lib", root)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].severity, SEVERITY_LOW)

    def test_missing_feature_returns_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            result = _find_affected_features("nonexistent", root)
            self.assertEqual(result, [])

    def test_shared_paths_proposed_changes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha", extra_content="src/shared/module.py")
            write_feature_bundle(root, "beta", extra_content="src/shared/module.py")
            result = _find_affected_features(
                "alpha",
                root,
                proposed_changes={"shared_paths": ["src/shared/module.py"]},
            )
            ids = {item.id for item in result}
            self.assertIn("beta", ids)


class FindAffectedTestsTests(TestCase):
    def test_finds_tests_referencing_feature_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "my-feature")
            write_test_file(
                root,
                "tests/test_my_feature.py",
                "# Tests for my-feature\ndef test_something(): pass\n",
            )
            result = _find_affected_tests("my-feature", root)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].id, "test_my_feature")

    def test_finds_tests_referencing_ac(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "login",
                acceptance_criteria=["User can login with credentials"],
            )
            write_test_file(
                root,
                "tests/test_login.py",
                "def test_login():\n    # User can login with credentials\n    pass\n",
            )
            result = _find_affected_tests("login", root)
            self.assertTrue(len(result) >= 1)
            ids = {item.id for item in result}
            self.assertIn("test_login", ids)

    def test_finds_tests_from_quality_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "auth")
            write_test_file(
                root,
                "tests/test_auth.py",
                "def test_auth(): pass\n",
            )
            (root / "quality" / "features" / "auth.md").write_text(
                "## Test Coverage\n- [ ] AC001 -> tests/test_auth.py\n",
                encoding="utf-8",
            )
            result = _find_affected_tests("auth", root)
            ids = {item.id for item in result}
            self.assertIn("test_auth", ids)

    def test_no_tests_returns_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "isolated")
            result = _find_affected_tests("isolated", root)
            self.assertEqual(result, [])

    def test_test_severity_is_medium(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "svc")
            write_test_file(
                root,
                "tests/test_svc.py",
                "# svc tests\n",
            )
            result = _find_affected_tests("svc", root)
            self.assertEqual(result[0].severity, SEVERITY_MEDIUM)

    def test_quality_referenced_test_has_low_severity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "mod")
            write_test_file(
                root,
                "tests/test_mod_only.py",
                "def test_mod(): pass\n",
            )
            (root / "quality" / "features" / "mod.md").write_text(
                "## Test Coverage\n- [ ] AC001 -> tests/test_mod_only.py\n",
                encoding="utf-8",
            )
            result = _find_affected_tests("mod", root)
            quality_items = [
                item for item in result if item.id == "test_mod_only"
            ]
            self.assertTrue(len(quality_items) >= 1)

    def test_deduplicates_test_items(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "api")
            write_test_file(
                root,
                "tests/test_api.py",
                "# api feature tests\n# api references\n",
            )
            result = _find_affected_tests("api", root)
            api_items = [item for item in result if item.id == "test_api"]
            self.assertEqual(len(api_items), 1)


class FindAffectedCodeTests(TestCase):
    def test_finds_source_referencing_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "payment")
            write_source_module(
                root,
                "src/specspine/payment.py",
                "# payment module\ndef process_payment(): pass  # for payment feature\n",
            )
            result = _find_affected_code("payment", root)
            self.assertEqual(len(result), 1)
            self.assertIn("payment", result[0].id)

    def test_finds_source_from_spec_reference(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "data")
            write_source_module(
                root,
                "src/specspine/data.py",
                "def process(): pass\n",
            )
            (root / "specs" / "features" / "data.md").write_text(
                "# Data\n\nFeature ID: data\n\nsrc/specspine/data.py\n",
                encoding="utf-8",
            )
            result = _find_affected_code("data", root)
            ids = {item.id for item in result}
            self.assertTrue(any("data" in i for i in ids))

    def test_no_source_returns_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "orphan")
            result = _find_affected_code("orphan", root)
            self.assertEqual(result, [])

    def test_code_severity_is_medium_for_slug_ref(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "svc")
            write_source_module(
                root,
                "src/specspine/svc.py",
                "# svc feature module\n",
            )
            result = _find_affected_code("svc", root)
            self.assertEqual(result[0].severity, SEVERITY_MEDIUM)

    def test_code_severity_is_low_for_path_ref(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "mod")
            write_source_module(
                root,
                "src/specspine/mod.py",
                "def x(): pass\n",
            )
            (root / "specs" / "features" / "mod.md").write_text(
                "# Mod\n\nFeature ID: mod\n\nsrc/specspine/mod.py\n",
                encoding="utf-8",
            )
            result = _find_affected_code("mod", root)
            path_items = [item for item in result if item.severity == SEVERITY_LOW]
            self.assertTrue(len(path_items) >= 1)


class ModuleNameTests(TestCase):
    def test_regular_module(self) -> None:
        root = Path("/tmp/test")
        source = root / "src" / "specspine" / "features.py"
        result = _module_name(source, root)
        self.assertEqual(result, "src.specspine.features")

    def test_init_module(self) -> None:
        root = Path("/tmp/test")
        source = root / "src" / "specspine" / "__init__.py"
        result = _module_name(source, root)
        self.assertEqual(result, "src.specspine.__init__")


class ComputeRiskScoreTests(TestCase):
    def test_no_impact_zero_score(self) -> None:
        score = _compute_risk_score((), (), ())
        self.assertEqual(score, 0)

    def test_high_severity_feature_increases_score(self) -> None:
        items = (
            ImpactItem(
                type=IMPACT_TYPE_FEATURE,
                id="feat",
                path="specs/features/feat.md",
                severity=SEVERITY_HIGH,
                reason="test",
            ),
        )
        score = _compute_risk_score(items, (), ())
        self.assertGreater(score, 0)

    def test_many_features_increase_score(self) -> None:
        items = tuple(
            ImpactItem(
                type=IMPACT_TYPE_FEATURE,
                id=f"feat-{i}",
                path=f"specs/features/feat-{i}.md",
                severity=SEVERITY_MEDIUM,
                reason="test",
            )
            for i in range(5)
        )
        score = _compute_risk_score(items, (), ())
        self.assertGreater(score, 10)

    def test_many_tests_increase_score(self) -> None:
        items = tuple(
            ImpactItem(
                type=IMPACT_TYPE_TEST,
                id=f"test-{i}",
                path=f"tests/test_{i}.py",
                severity=SEVERITY_MEDIUM,
                reason="test",
            )
            for i in range(6)
        )
        score = _compute_risk_score((), items, ())
        self.assertGreater(score, 8)

    def test_many_code_modules_increase_score(self) -> None:
        items = tuple(
            ImpactItem(
                type=IMPACT_TYPE_CODE,
                id=f"mod-{i}",
                path=f"src/mod_{i}.py",
                severity=SEVERITY_MEDIUM,
                reason="test",
            )
            for i in range(6)
        )
        score = _compute_risk_score((), (), items)
        self.assertGreater(score, 5)

    def test_score_capped_at_100(self) -> None:
        items = tuple(
            ImpactItem(
                type=IMPACT_TYPE_FEATURE,
                id=f"feat-{i}",
                path=f"specs/features/feat-{i}.md",
                severity=SEVERITY_HIGH,
                reason="test",
            )
            for i in range(20)
        )
        score = _compute_risk_score(items, (), ())
        self.assertLessEqual(score, 100)

    def test_mixed_severity_scoring(self) -> None:
        features = (
            ImpactItem(
                type=IMPACT_TYPE_FEATURE,
                id="f1",
                path="p",
                severity=SEVERITY_HIGH,
                reason="r",
            ),
        )
        tests = (
            ImpactItem(
                type=IMPACT_TYPE_TEST,
                id="t1",
                path="p",
                severity=SEVERITY_MEDIUM,
                reason="r",
            ),
        )
        code = (
            ImpactItem(
                type=IMPACT_TYPE_CODE,
                id="c1",
                path="p",
                severity=SEVERITY_LOW,
                reason="r",
            ),
        )
        score = _compute_risk_score(features, tests, code)
        self.assertGreater(score, 0)


class GenerateMitigationStepsTests(TestCase):
    def test_has_steps_when_features_impacted(self) -> None:
        analysis = ImpactAnalysis(
            feature_id="test",
            total_affected=1,
            impacted_features=(
                ImpactItem(
                    type=IMPACT_TYPE_FEATURE,
                    id="dep",
                    path="p",
                    severity=SEVERITY_MEDIUM,
                    reason="r",
                ),
            ),
            impacted_tests=(),
            impacted_code=(),
            risk_score=10,
            mitigation_steps=(),
            safety_notes=(),
            recommended_commands=(),
        )
        steps = _generate_mitigation_steps(analysis)
        self.assertTrue(len(steps) >= 2)

    def test_has_steps_when_tests_impacted(self) -> None:
        analysis = ImpactAnalysis(
            feature_id="test",
            total_affected=1,
            impacted_features=(),
            impacted_tests=(
                ImpactItem(
                    type=IMPACT_TYPE_TEST,
                    id="t1",
                    path="tests/t.py",
                    severity=SEVERITY_MEDIUM,
                    reason="r",
                ),
            ),
            impacted_code=(),
            risk_score=10,
            mitigation_steps=(),
            safety_notes=(),
            recommended_commands=(),
        )
        steps = _generate_mitigation_steps(analysis)
        self.assertTrue(any("test" in s.lower() for s in steps))

    def test_has_steps_when_code_impacted(self) -> None:
        analysis = ImpactAnalysis(
            feature_id="test",
            total_affected=1,
            impacted_features=(),
            impacted_tests=(),
            impacted_code=(
                ImpactItem(
                    type=IMPACT_TYPE_CODE,
                    id="mod",
                    path="src/mod.py",
                    severity=SEVERITY_MEDIUM,
                    reason="r",
                ),
            ),
            risk_score=10,
            mitigation_steps=(),
            safety_notes=(),
            recommended_commands=(),
        )
        steps = _generate_mitigation_steps(analysis)
        self.assertTrue(any("code" in s.lower() or "module" in s.lower() for s in steps))

    def test_high_risk_has_break_down_suggestion(self) -> None:
        analysis = ImpactAnalysis(
            feature_id="test",
            total_affected=10,
            impacted_features=(),
            impacted_tests=(),
            impacted_code=(),
            risk_score=50,
            mitigation_steps=(),
            safety_notes=(),
            recommended_commands=(),
        )
        steps = _generate_mitigation_steps(analysis)
        self.assertTrue(any("smaller" in s.lower() or "breaking" in s.lower() for s in steps))

    def test_critical_risk_has_review_suggestion(self) -> None:
        analysis = ImpactAnalysis(
            feature_id="test",
            total_affected=10,
            impacted_features=(),
            impacted_tests=(),
            impacted_code=(),
            risk_score=75,
            mitigation_steps=(),
            safety_notes=(),
            recommended_commands=(),
        )
        steps = _generate_mitigation_steps(analysis)
        self.assertTrue(any("review" in s.lower() for s in steps))

    def test_always_has_validate_step(self) -> None:
        analysis = ImpactAnalysis(
            feature_id="test",
            total_affected=0,
            impacted_features=(),
            impacted_tests=(),
            impacted_code=(),
            risk_score=0,
            mitigation_steps=(),
            safety_notes=(),
            recommended_commands=(),
        )
        steps = _generate_mitigation_steps(analysis)
        self.assertTrue(any("validate" in s.lower() for s in steps))


class ImpactItemTests(TestCase):
    def test_as_dict(self) -> None:
        item = ImpactItem(
            type=IMPACT_TYPE_FEATURE,
            id="my-feature",
            path="specs/features/my-feature.md",
            severity=SEVERITY_HIGH,
            reason="test reason",
            affected_acs=("AC001",),
        )
        d = item.as_dict()
        self.assertEqual(d["type"], IMPACT_TYPE_FEATURE)
        self.assertEqual(d["id"], "my-feature")
        self.assertEqual(d["severity"], SEVERITY_HIGH)
        self.assertEqual(d["affected_acs"], ["AC001"])

    def test_as_dict_empty_affected_acs(self) -> None:
        item = ImpactItem(
            type=IMPACT_TYPE_TEST,
            id="t1",
            path="p",
            severity=SEVERITY_LOW,
            reason="r",
        )
        d = item.as_dict()
        self.assertEqual(d["affected_acs"], [])


class ImpactAnalysisTests(TestCase):
    def test_as_dict(self) -> None:
        analysis = ImpactAnalysis(
            feature_id="test",
            total_affected=1,
            impacted_features=(),
            impacted_tests=(),
            impacted_code=(),
            risk_score=0,
            mitigation_steps=("step1",),
            safety_notes=("note1",),
            recommended_commands=("cmd1",),
        )
        d = analysis.as_dict()
        self.assertEqual(d["feature_id"], "test")
        self.assertEqual(d["total_affected"], 1)
        self.assertEqual(d["risk_score"], 0)
        self.assertEqual(d["mitigation_steps"], ["step1"])
        self.assertEqual(d["safety_notes"], ["note1"])
        self.assertEqual(d["recommended_commands"], ["cmd1"])


class AnalyzeFeatureImpactTests(TestCase):
    def test_analyze_existing_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "my-feature")
            analysis = analyze_feature_impact(root, "my-feature")
            self.assertEqual(analysis.feature_id, "my-feature")
            self.assertIsInstance(analysis.total_affected, int)
            self.assertIsInstance(analysis.risk_score, int)
            self.assertGreaterEqual(analysis.risk_score, 0)
            self.assertLessEqual(analysis.risk_score, 100)

    def test_missing_feature_raises_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with self.assertRaises(FeatureBundleNotFoundError):
                analyze_feature_impact(root, "nonexistent")

    def test_invalid_slug_raises_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with self.assertRaises(InvalidFeatureSlug):
                analyze_feature_impact(root, "Bad_Slug")

    def test_analysis_has_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            self.assertTrue(len(analysis.safety_notes) >= 1)

    def test_analysis_has_recommended_commands(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            self.assertTrue(len(analysis.recommended_commands) >= 1)

    def test_analysis_has_mitigation_steps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            self.assertTrue(len(analysis.mitigation_steps) >= 1)

    def test_with_dependencies(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "core")
            write_feature_bundle(
                root,
                "app",
                extra_content="depends on core",
            )
            analysis = analyze_feature_impact(root, "core")
            self.assertEqual(len(analysis.impacted_features), 1)
            self.assertEqual(analysis.impacted_features[0].id, "app")

    def test_with_tests(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "svc")
            write_test_file(
                root,
                "tests/test_svc.py",
                "# svc tests\n",
            )
            analysis = analyze_feature_impact(root, "svc")
            test_ids = {item.id for item in analysis.impacted_tests}
            self.assertIn("test_svc", test_ids)

    def test_with_source_code(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "mod")
            write_source_module(
                root,
                "src/specspine/mod.py",
                "# mod feature\n",
            )
            analysis = analyze_feature_impact(root, "mod")
            code_ids = {item.id for item in analysis.impacted_code}
            self.assertTrue(any("mod" in i for i in code_ids))

    def test_total_affected_counts_all(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "core")
            write_feature_bundle(
                root,
                "dep",
                extra_content="depends on core",
            )
            write_test_file(
                root,
                "tests/test_core.py",
                "# core tests\n",
            )
            write_source_module(
                root,
                "src/specspine/core.py",
                "# core module\n",
            )
            analysis = analyze_feature_impact(root, "core")
            expected = (
                len(analysis.impacted_features)
                + len(analysis.impacted_tests)
                + len(analysis.impacted_code)
            )
            self.assertEqual(analysis.total_affected, expected)

    def test_read_only_no_subprocess(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "safe")

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
                            analysis = analyze_feature_impact(root, "safe")
            self.assertEqual(analysis.feature_id, "safe")


class RenderImpactJsonTests(TestCase):
    def test_valid_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            json_str = render_impact_json(analysis)
            parsed = json.loads(json_str)
            self.assertEqual(parsed["feature_id"], "test")

    def test_json_is_sorted_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            json_str = render_impact_json(analysis)
            parsed = json.loads(json_str)
            keys = list(parsed.keys())
            self.assertEqual(keys, sorted(keys))

    def test_json_contains_impacted_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "base")
            write_feature_bundle(
                root,
                "dep",
                extra_content="depends on base",
            )
            analysis = analyze_feature_impact(root, "base")
            json_str = render_impact_json(analysis)
            parsed = json.loads(json_str)
            self.assertTrue(len(parsed["impacted_features"]) >= 1)


class RenderImpactTextTests(TestCase):
    def test_text_contains_header(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            text = render_impact_text(analysis)
            self.assertIn("Feature impact analysis:", text)

    def test_text_contains_risk_score(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            text = render_impact_text(analysis)
            self.assertIn("Risk score:", text)

    def test_text_contains_total_affected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            text = render_impact_text(analysis)
            self.assertIn("Total affected items:", text)

    def test_text_contains_impacted_features_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            text = render_impact_text(analysis)
            self.assertIn("Impacted features", text)

    def test_text_contains_impacted_tests_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            text = render_impact_text(analysis)
            self.assertIn("Impacted tests", text)

    def test_text_contains_impacted_code_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            text = render_impact_text(analysis)
            self.assertIn("Impacted code", text)

    def test_text_contains_mitigation_steps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            text = render_impact_text(analysis)
            self.assertIn("Mitigation steps:", text)

    def test_text_contains_recommended_commands(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            text = render_impact_text(analysis)
            self.assertIn("Recommended commands:", text)

    def test_text_contains_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            analysis = analyze_feature_impact(root, "test")
            text = render_impact_text(analysis)
            self.assertIn("Safety notes:", text)

    def test_text_shows_none_when_no_impact(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "isolated")
            analysis = analyze_feature_impact(root, "isolated")
            text = render_impact_text(analysis)
            self.assertIn("(none)", text)


class ImpactCLITests(TestCase):
    def test_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "my-feature")
            code, stdout, stderr = run_cli(
                ["impact", "analyze", "my-feature", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["feature_id"], "my-feature")

    def test_text_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "my-feature")
            code, stdout, stderr = run_cli(
                ["impact", "analyze", "my-feature", str(root)]
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Feature impact analysis:", stdout)

    def test_invalid_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, _stdout, stderr = run_cli(
                ["impact", "analyze", "Bad_Slug", str(root), "--json"]
            )
            self.assertEqual(code, 2)
            self.assertIn("Invalid feature slug", stderr)

    def test_missing_feature_returns_one(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, _stdout, stderr = run_cli(
                ["impact", "analyze", "nonexistent", str(root), "--json"]
            )
            self.assertEqual(code, 1)
            self.assertIn("No feature files found", stderr)

    def test_help_does_not_crash(self) -> None:
        code, stdout, stderr = run_cli(
            ["impact", "analyze", "--help"]
        )
        self.assertEqual(code, 0)
        self.assertIn("--json", stdout)
        self.assertIn("--changes", stdout)

    def test_with_dependencies_cli(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "core")
            write_feature_bundle(
                root,
                "app",
                extra_content="depends on core",
            )
            code, stdout, stderr = run_cli(
                ["impact", "analyze", "core", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertTrue(len(payload["impacted_features"]) >= 1)

    def test_deterministic_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            code1, out1, _ = run_cli(
                ["impact", "analyze", "test", str(root), "--json"]
            )
            code2, out2, _ = run_cli(
                ["impact", "analyze", "test", str(root), "--json"]
            )
            self.assertEqual(code1, code2)
            self.assertEqual(out1, out2)

    def test_json_full_structure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "test")
            code, stdout, stderr = run_cli(
                ["impact", "analyze", "test", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertIn("feature_id", payload)
            self.assertIn("total_affected", payload)
            self.assertIn("impacted_features", payload)
            self.assertIn("impacted_tests", payload)
            self.assertIn("impacted_code", payload)
            self.assertIn("risk_score", payload)
            self.assertIn("mitigation_steps", payload)
            self.assertIn("safety_notes", payload)
            self.assertIn("recommended_commands", payload)


class ImpactAnalysisIntegrationTests(TestCase):
    def test_full_chain_impact(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "layer1", effort="S")
            write_feature_bundle(
                root,
                "layer2",
                effort="M",
                extra_content="depends on layer1",
            )
            write_feature_bundle(
                root,
                "layer3",
                effort="L",
                extra_content="depends on layer2",
            )
            analysis = analyze_feature_impact(root, "layer1")
            impacted_ids = {item.id for item in analysis.impacted_features}
            self.assertIn("layer2", impacted_ids)

    def test_no_false_positives_for_unrelated_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            write_feature_bundle(root, "gamma")
            analysis = analyze_feature_impact(root, "alpha")
            impacted_ids = {item.id for item in analysis.impacted_features}
            self.assertNotIn("beta", impacted_ids)
            self.assertNotIn("gamma", impacted_ids)

    def test_impact_with_tests_and_code(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "full")
            write_test_file(
                root,
                "tests/test_full.py",
                "# full feature tests\n",
            )
            write_source_module(
                root,
                "src/specspine/full.py",
                "# full module for full feature\n",
            )
            analysis = analyze_feature_impact(root, "full")
            self.assertTrue(len(analysis.impacted_tests) >= 1)
            self.assertTrue(len(analysis.impacted_code) >= 1)
