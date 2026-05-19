from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.features import InvalidFeatureSlug
from specspine.harness_coverage import (
    GOVERNED_DIMENSIONS,
    DIMENSION_SENSOR_MAP,
    MATURITY_LABELS,
    HarnessCoverageReport,
    HarnessDimensionCoverage,
    _compare_with_baseline,
    _compute_maturity_score,
    _detect_blind_spots,
    _detect_redundancy,
    _evaluate_dimensions,
    _generate_improvement_plan,
    _load_baseline,
    _save_baseline,
    build_harness_coverage_report,
    render_harness_coverage_json,
    render_harness_coverage_text,
)


def _write_minimal_feature(root: Path, slug: str = "test-feature") -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)
    (root / "tests" / f"test_{slug.replace('-', '_')}.py").write_text(
        "# test target\n",
        encoding="utf-8",
    )
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug.replace('-', ' ').title()}",
                "",
                f"Feature ID: {slug}",
                "Status: planned",
                "",
                "## Acceptance Criteria",
                "",
                "- [ ] AC001: User can log in.",
                "- [ ] AC002: User can log out.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug.replace('-', ' ').title()} Execution",
                "",
                f"Feature ID: {slug}",
                "Status: planned",
                "",
                "## Tasks",
                "",
                "- [ ] T001: Implement login.",
                "- [ ] T002: Implement logout.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug.replace('-', ' ').title()} Quality",
                "",
                f"Feature ID: {slug}",
                "Status: planned",
                "",
                "## Required Checks",
                "",
                "- [ ] Login reviewed.",
                "",
                "## Test Coverage",
                "",
                f"- [ ] AC001 -> tests/test_{slug.replace('-', '_')}.py",
                f"- [ ] AC002 -> tests/test_{slug.replace('-', '_')}.py",
                "",
                "## Release Readiness",
                "",
                "- [ ] Ready.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_covered_feature(root: Path, slug: str = "covered-feature") -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)
    (root / "tests" / f"test_{slug.replace('-', '_')}.py").write_text(
        "# test target\n",
        encoding="utf-8",
    )
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug.replace('-', ' ').title()}",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Acceptance Criteria",
                "",
                "- [x] AC001: User can log in.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug.replace('-', ' ').title()} Execution",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Tasks",
                "",
                "- [x] T001: Implement login.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# {slug.replace('-', ' ').title()} Quality",
                "",
                f"Feature ID: {slug}",
                "Status: validated",
                "",
                "## Required Checks",
                "",
                "- [x] Login reviewed.",
                "",
                "## Test Coverage",
                "",
                f"- [x] AC001 -> tests/test_{slug.replace('-', '_')}.py",
                "",
                "## Release Readiness",
                "",
                "- [x] Ready.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class HarnessDimensionCoverageTests(TestCase):
    def test_dimension_as_dict(self) -> None:
        dim = HarnessDimensionCoverage(
            dimension_name="verification",
            sensor_count=1,
            pass_count=1,
            coverage_pct=100.0,
        )
        result = dim.as_dict()
        self.assertEqual(result["dimension_name"], "verification")
        self.assertEqual(result["sensor_count"], 1)
        self.assertEqual(result["pass_count"], 1)
        self.assertAlmostEqual(result["coverage_pct"], 100.0)

    def test_dimension_as_dict_with_missing_sensors(self) -> None:
        dim = HarnessDimensionCoverage(
            dimension_name="security",
            sensor_count=0,
            pass_count=0,
            coverage_pct=0.0,
            missing_sensors=("security_cues",),
        )
        result = dim.as_dict()
        self.assertEqual(result["missing_sensors"], ["security_cues"])

    def test_dimension_as_dict_with_redundant_sensors(self) -> None:
        dim = HarnessDimensionCoverage(
            dimension_name="verification",
            sensor_count=2,
            pass_count=2,
            coverage_pct=100.0,
            redundant_sensors=("verification_matrix",),
        )
        result = dim.as_dict()
        self.assertEqual(result["redundant_sensors"], ["verification_matrix"])

    def test_dimension_as_dict_empty_lists(self) -> None:
        dim = HarnessDimensionCoverage(
            dimension_name="coverage",
            sensor_count=1,
            pass_count=0,
            coverage_pct=0.0,
        )
        result = dim.as_dict()
        self.assertEqual(result["missing_sensors"], [])
        self.assertEqual(result["redundant_sensors"], [])


class HarnessCoverageReportTests(TestCase):
    def test_report_as_dict(self) -> None:
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=3,
            blind_spots=("security",),
            improvement_plan=("Add security_cues sensor.",),
        )
        result = report.as_dict()
        self.assertEqual(result["feature_id"], "test")
        self.assertEqual(result["maturity_score"], 3)
        self.assertEqual(result["blind_spots"], ["security"])
        self.assertEqual(result["improvement_plan"], ["Add security_cues sensor."])

    def test_report_as_dict_with_baseline_comparison(self) -> None:
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=4,
            blind_spots=(),
            improvement_plan=(),
            baseline_comparison={"trend": "improving", "maturity_delta": 1},
        )
        result = report.as_dict()
        self.assertEqual(result["baseline_comparison"]["trend"], "improving")

    def test_report_as_dict_with_safety_notes(self) -> None:
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=2,
            blind_spots=(),
            improvement_plan=(),
            safety_notes=("Test note.",),
        )
        result = report.as_dict()
        self.assertEqual(result["safety_notes"], ["Test note."])

    def test_report_as_dict_dimensions_serialized(self) -> None:
        dim = HarnessDimensionCoverage(
            dimension_name="verification",
            sensor_count=1,
            pass_count=1,
            coverage_pct=100.0,
        )
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(dim,),
            maturity_score=5,
            blind_spots=(),
            improvement_plan=(),
        )
        result = report.as_dict()
        self.assertEqual(len(result["dimensions"]), 1)
        self.assertEqual(result["dimensions"][0]["dimension_name"], "verification")


class EvaluateDimensionsTests(TestCase):
    def test_evaluates_all_8_dimensions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            dimensions = _evaluate_dimensions("test-feature", root)
            self.assertEqual(len(dimensions), 8)

    def test_dimension_names_match_governed_dimensions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            dimensions = _evaluate_dimensions("test-feature", root)
            names = [d.dimension_name for d in dimensions]
            self.assertEqual(names, list(GOVERNED_DIMENSIONS))

    def test_dimension_has_sensor_count(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            dimensions = _evaluate_dimensions("test-feature", root)
            for d in dimensions:
                self.assertGreaterEqual(d.sensor_count, 0)

    def test_dimension_coverage_pct_in_range(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            dimensions = _evaluate_dimensions("test-feature", root)
            for d in dimensions:
                self.assertGreaterEqual(d.coverage_pct, 0.0)
                self.assertLessEqual(d.coverage_pct, 100.0)

    def test_dimension_pass_count_non_negative(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            dimensions = _evaluate_dimensions("test-feature", root)
            for d in dimensions:
                self.assertGreaterEqual(d.pass_count, 0)

    def test_missing_sensors_for_no_sensor(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            dimensions = _evaluate_dimensions("nonexistent", root)
            all_have_sensors = all(d.sensor_count > 0 for d in dimensions)
            self.assertTrue(all_have_sensors)

    def test_coverage_pct_zero_when_no_sensors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            dimensions = _evaluate_dimensions("nonexistent", root)
            for d in dimensions:
                if d.sensor_count == 0:
                    self.assertEqual(d.coverage_pct, 0.0)


class DetectBlindSpotsTests(TestCase):
    def test_detects_dimensions_with_zero_sensors(self) -> None:
        dimensions = [
            HarnessDimensionCoverage("verification", 1, 1, 100.0),
            HarnessDimensionCoverage("security", 0, 0, 0.0, missing_sensors=("security_cues",)),
        ]
        spots = _detect_blind_spots(dimensions)
        self.assertIn("security", spots)

    def test_no_blind_spots_when_all_have_sensors(self) -> None:
        dimensions = [
            HarnessDimensionCoverage("verification", 1, 1, 100.0),
            HarnessDimensionCoverage("coverage", 1, 1, 100.0),
        ]
        spots = _detect_blind_spots(dimensions)
        self.assertEqual(spots, [])

    def test_empty_dimensions_returns_empty(self) -> None:
        spots = _detect_blind_spots([])
        self.assertEqual(spots, [])

    def test_all_blind_spots_returned(self) -> None:
        dimensions = [
            HarnessDimensionCoverage("verification", 0, 0, 0.0, missing_sensors=("verification_matrix",)),
            HarnessDimensionCoverage("coverage", 0, 0, 0.0, missing_sensors=("coverage_debt",)),
        ]
        spots = _detect_blind_spots(dimensions)
        self.assertEqual(len(spots), 2)
        self.assertIn("verification", spots)
        self.assertIn("coverage", spots)


class DetectRedundancyTests(TestCase):
    def test_detects_redundant_sensors(self) -> None:
        dimensions = [
            HarnessDimensionCoverage(
                "verification", 2, 2, 100.0,
                redundant_sensors=("verification_matrix",),
            ),
        ]
        result = _detect_redundancy(dimensions)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["dimension"], "verification")

    def test_no_redundancy_when_no_redundant_sensors(self) -> None:
        dimensions = [
            HarnessDimensionCoverage("verification", 1, 1, 100.0),
        ]
        result = _detect_redundancy(dimensions)
        self.assertEqual(result, [])

    def test_empty_dimensions_returns_empty(self) -> None:
        result = _detect_redundancy([])
        self.assertEqual(result, [])

    def test_multiple_redundant_dimensions(self) -> None:
        dimensions = [
            HarnessDimensionCoverage(
                "verification", 2, 2, 100.0,
                redundant_sensors=("verification_matrix",),
            ),
            HarnessDimensionCoverage(
                "coverage", 2, 2, 100.0,
                redundant_sensors=("coverage_debt",),
            ),
        ]
        result = _detect_redundancy(dimensions)
        self.assertEqual(len(result), 2)


class ComputeMaturityScoreTests(TestCase):
    def test_score_zero_for_empty_dimensions(self) -> None:
        self.assertEqual(_compute_maturity_score([]), 0)

    def test_score_zero_for_no_sensors(self) -> None:
        dimensions = [
            HarnessDimensionCoverage(d, 0, 0, 0.0)
            for d in GOVERNED_DIMENSIONS
        ]
        self.assertEqual(_compute_maturity_score(dimensions), 0)

    def test_score_one_for_some_sensors(self) -> None:
        dimensions = [HarnessDimensionCoverage("verification", 1, 0, 0.0)]
        dimensions.extend(
            HarnessDimensionCoverage(d, 0, 0, 0.0)
            for d in list(GOVERNED_DIMENSIONS)[1:]
        )
        score = _compute_maturity_score(dimensions)
        self.assertEqual(score, 1)

    def test_score_two_for_half_coverage(self) -> None:
        half = len(GOVERNED_DIMENSIONS) // 2
        dimensions = [
            HarnessDimensionCoverage(d, 1, 1, 100.0)
            for d in list(GOVERNED_DIMENSIONS)[:half]
        ] + [
            HarnessDimensionCoverage(d, 0, 0, 0.0)
            for d in list(GOVERNED_DIMENSIONS)[half:]
        ]
        score = _compute_maturity_score(dimensions)
        self.assertGreaterEqual(score, 2)

    def test_score_three_for_75_percent_coverage(self) -> None:
        three_quarters = int(len(GOVERNED_DIMENSIONS) * 0.75)
        dimensions = [
            HarnessDimensionCoverage(d, 1, 1, 100.0)
            for d in list(GOVERNED_DIMENSIONS)[:three_quarters]
        ] + [
            HarnessDimensionCoverage(d, 1, 0, 0.0)
            for d in list(GOVERNED_DIMENSIONS)[three_quarters:]
        ]
        score = _compute_maturity_score(dimensions)
        self.assertGreaterEqual(score, 3)

    def test_score_five_for_full_coverage(self) -> None:
        dimensions = [
            HarnessDimensionCoverage(d, 1, 1, 100.0)
            for d in GOVERNED_DIMENSIONS
        ]
        score = _compute_maturity_score(dimensions)
        self.assertEqual(score, 5)

    def test_score_four_for_75_percent_fully_covered(self) -> None:
        three_quarters = int(len(GOVERNED_DIMENSIONS) * 0.75)
        dimensions = [
            HarnessDimensionCoverage(d, 1, 1, 100.0)
            for d in list(GOVERNED_DIMENSIONS)[:three_quarters]
        ] + [
            HarnessDimensionCoverage(d, 1, 1, 90.0)
            for d in list(GOVERNED_DIMENSIONS)[three_quarters:]
        ]
        score = _compute_maturity_score(dimensions)
        self.assertGreaterEqual(score, 4)

    def test_maturity_score_in_range(self) -> None:
        for sensors in range(0, 9):
            dimensions = [
                HarnessDimensionCoverage(d, 1 if i < sensors else 0, 1 if i < sensors else 0, 100.0 if i < sensors else 0.0)
                for i, d in enumerate(GOVERNED_DIMENSIONS)
            ]
            score = _compute_maturity_score(dimensions)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 5)


class GenerateImprovementPlanTests(TestCase):
    def test_plan_includes_missing_sensors(self) -> None:
        dimensions = [
            HarnessDimensionCoverage(
                "security", 0, 0, 0.0, missing_sensors=("security_cues",),
            ),
        ]
        plan = _generate_improvement_plan(dimensions, ["security"])
        self.assertTrue(any("security_cues" in item for item in plan))

    def test_plan_includes_coverage_improvement(self) -> None:
        dimensions = [
            HarnessDimensionCoverage("verification", 1, 0, 50.0),
        ]
        plan = _generate_improvement_plan(dimensions, [])
        self.assertTrue(any("verification" in item for item in plan))

    def test_plan_includes_maturity_recommendation(self) -> None:
        dimensions = [
            HarnessDimensionCoverage(d, 0, 0, 0.0)
            for d in GOVERNED_DIMENSIONS
        ]
        plan = _generate_improvement_plan(dimensions, list(GOVERNED_DIMENSIONS))
        self.assertTrue(any("maturity" in item.lower() for item in plan))

    def test_plan_empty_when_all_covered(self) -> None:
        dimensions = [
            HarnessDimensionCoverage(d, 1, 1, 100.0)
            for d in GOVERNED_DIMENSIONS
        ]
        plan = _generate_improvement_plan(dimensions, [])
        self.assertEqual(len(plan), 0)

    def test_plan_includes_redundancy_review(self) -> None:
        dimensions = [
            HarnessDimensionCoverage(
                "verification", 2, 2, 100.0,
                redundant_sensors=("verification_matrix",),
            ),
        ]
        plan = _generate_improvement_plan(dimensions, [])
        self.assertTrue(any("redundant" in item.lower() for item in plan))

    def test_plan_ordered_by_coverage_impact(self) -> None:
        dimensions = [
            HarnessDimensionCoverage("verification", 1, 1, 100.0),
            HarnessDimensionCoverage("coverage", 1, 0, 50.0),
        ]
        plan = _generate_improvement_plan(dimensions, [])
        coverage_item_idx = None
        for i, item in enumerate(plan):
            if "coverage" in item and "Improve" in item:
                coverage_item_idx = i
                break
        self.assertIsNotNone(coverage_item_idx)


class BaselinePersistenceTests(TestCase):
    def test_load_baseline_returns_none_when_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = _load_baseline(root)
            self.assertIsNone(result)

    def test_save_baseline_writes_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = HarnessCoverageReport(
                feature_id="test",
                dimensions=(),
                maturity_score=3,
                blind_spots=(),
                improvement_plan=(),
            )
            _save_baseline(root, report)
            baseline_path = root / ".specspine" / "harness-baseline.json"
            self.assertTrue(baseline_path.exists())

    def test_save_baseline_valid_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = HarnessCoverageReport(
                feature_id="test",
                dimensions=(),
                maturity_score=3,
                blind_spots=("security",),
                improvement_plan=("Add sensor.",),
            )
            _save_baseline(root, report)
            baseline_path = root / ".specspine" / "harness-baseline.json"
            content = baseline_path.read_text(encoding="utf-8")
            parsed = json.loads(content)
            self.assertEqual(parsed["feature_id"], "test")

    def test_load_baseline_returns_parsed_data(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = HarnessCoverageReport(
                feature_id="test",
                dimensions=(),
                maturity_score=4,
                blind_spots=(),
                improvement_plan=(),
            )
            _save_baseline(root, report)
            result = _load_baseline(root)
            self.assertIsNotNone(result)
            self.assertEqual(result["maturity_score"], 4)

    def test_load_baseline_handles_invalid_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline_dir = root / ".specspine"
            baseline_dir.mkdir(parents=True)
            baseline_path = baseline_dir / "harness-baseline.json"
            baseline_path.write_text("not valid json", encoding="utf-8")
            result = _load_baseline(root)
            self.assertIsNone(result)


class BaselineComparisonTests(TestCase):
    def test_maturity_delta_positive(self) -> None:
        baseline = {"maturity_score": 2, "dimensions": [], "blind_spots": []}
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=4,
            blind_spots=(),
            improvement_plan=(),
        )
        comparison = _compare_with_baseline(report, baseline)
        self.assertEqual(comparison["maturity_delta"], 2)

    def test_maturity_delta_negative(self) -> None:
        baseline = {"maturity_score": 4, "dimensions": [], "blind_spots": []}
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=2,
            blind_spots=(),
            improvement_plan=(),
        )
        comparison = _compare_with_baseline(report, baseline)
        self.assertEqual(comparison["maturity_delta"], -2)

    def test_trend_improving(self) -> None:
        baseline = {"maturity_score": 2, "dimensions": [], "blind_spots": []}
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=3,
            blind_spots=(),
            improvement_plan=(),
        )
        comparison = _compare_with_baseline(report, baseline)
        self.assertEqual(comparison["trend"], "improving")

    def test_trend_regressing(self) -> None:
        baseline = {"maturity_score": 4, "dimensions": [], "blind_spots": []}
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=3,
            blind_spots=(),
            improvement_plan=(),
        )
        comparison = _compare_with_baseline(report, baseline)
        self.assertEqual(comparison["trend"], "regressing")

    def test_trend_stable(self) -> None:
        baseline = {"maturity_score": 3, "dimensions": [], "blind_spots": []}
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=3,
            blind_spots=(),
            improvement_plan=(),
        )
        comparison = _compare_with_baseline(report, baseline)
        self.assertEqual(comparison["trend"], "stable")

    def test_new_blind_spots_detected(self) -> None:
        baseline = {"maturity_score": 3, "dimensions": [], "blind_spots": []}
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=3,
            blind_spots=("security",),
            improvement_plan=(),
        )
        comparison = _compare_with_baseline(report, baseline)
        self.assertIn("security", comparison["new_blind_spots"])

    def test_resolved_blind_spots_detected(self) -> None:
        baseline = {"maturity_score": 3, "dimensions": [], "blind_spots": ["security"]}
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=3,
            blind_spots=(),
            improvement_plan=(),
        )
        comparison = _compare_with_baseline(report, baseline)
        self.assertIn("security", comparison["resolved_blind_spots"])

    def test_dimension_deltas_computed(self) -> None:
        baseline = {
            "maturity_score": 3,
            "dimensions": [{"dimension_name": "verification", "coverage_pct": 50.0}],
            "blind_spots": [],
        }
        dim = HarnessDimensionCoverage("verification", 1, 1, 100.0)
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(dim,),
            maturity_score=3,
            blind_spots=(),
            improvement_plan=(),
        )
        comparison = _compare_with_baseline(report, baseline)
        deltas = comparison["dimension_deltas"]
        self.assertEqual(len(deltas), 1)
        self.assertEqual(deltas[0]["delta"], 50.0)


class BuildHarnessCoverageReportTests(TestCase):
    def test_build_report_for_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            self.assertEqual(report.feature_id, "test-feature")
            self.assertEqual(len(report.dimensions), 8)

    def test_build_report_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root)
            self.assertEqual(report.feature_id, "workspace")
            self.assertEqual(len(report.dimensions), 8)

    def test_build_report_has_blind_spots(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            self.assertIsInstance(report.blind_spots, tuple)

    def test_build_report_has_improvement_plan(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            self.assertIsInstance(report.improvement_plan, tuple)

    def test_build_report_has_maturity_score(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            self.assertGreaterEqual(report.maturity_score, 0)
            self.assertLessEqual(report.maturity_score, 5)

    def test_build_report_has_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            self.assertGreater(len(report.safety_notes), 0)

    def test_build_report_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(InvalidFeatureSlug):
                build_harness_coverage_report(root, feature_filter="INVALID SLUG")

    def test_build_report_empty_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_harness_coverage_report(root)
            self.assertEqual(report.feature_id, "workspace")
            self.assertEqual(report.maturity_score, 0)

    def test_build_report_with_baseline_comparison(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            baseline_report = HarnessCoverageReport(
                feature_id="test-feature",
                dimensions=(),
                maturity_score=2,
                blind_spots=("security",),
                improvement_plan=(),
            )
            _save_baseline(root, baseline_report)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            self.assertTrue(bool(report.baseline_comparison))

    def test_build_report_multiple_features_aggregated(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root, "feature-a")
            _write_covered_feature(root, "feature-b")
            report = build_harness_coverage_report(root)
            self.assertEqual(report.feature_id, "workspace")
            total_sensors = sum(d.sensor_count for d in report.dimensions)
            self.assertGreater(total_sensors, 0)


class RenderHarnessCoverageJsonTests(TestCase):
    def test_render_json_is_valid_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            output = render_harness_coverage_json(report)
            parsed = json.loads(output)
            self.assertIn("feature_id", parsed)

    def test_render_json_contains_dimensions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            output = render_harness_coverage_json(report)
            parsed = json.loads(output)
            self.assertIn("dimensions", parsed)

    def test_render_json_contains_maturity_score(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            output = render_harness_coverage_json(report)
            parsed = json.loads(output)
            self.assertIn("maturity_score", parsed)

    def test_render_json_contains_blind_spots(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            output = render_harness_coverage_json(report)
            parsed = json.loads(output)
            self.assertIn("blind_spots", parsed)

    def test_render_json_contains_improvement_plan(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            output = render_harness_coverage_json(report)
            parsed = json.loads(output)
            self.assertIn("improvement_plan", parsed)

    def test_render_json_sorted_keys(self) -> None:
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=3,
            blind_spots=(),
            improvement_plan=(),
        )
        output = render_harness_coverage_json(report)
        parsed = json.loads(output)
        keys = list(parsed.keys())
        self.assertEqual(keys, sorted(keys))


class RenderHarnessCoverageTextTests(TestCase):
    def test_render_text_contains_feature_id(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            output = render_harness_coverage_text(report)
            self.assertIn("test-feature", output)

    def test_render_text_contains_maturity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            output = render_harness_coverage_text(report)
            self.assertIn("Maturity:", output)

    def test_render_text_contains_dimensions_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            output = render_harness_coverage_text(report)
            self.assertIn("Dimensions:", output)

    def test_render_text_contains_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            output = render_harness_coverage_text(report)
            self.assertIn("Safety notes:", output)

    def test_render_text_contains_blind_spots_section(self) -> None:
        dim = HarnessDimensionCoverage("security", 0, 0, 0.0, missing_sensors=("security_cues",))
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(dim,),
            maturity_score=1,
            blind_spots=("security",),
            improvement_plan=(),
        )
        output = render_harness_coverage_text(report)
        self.assertIn("Blind spots:", output)

    def test_render_text_contains_improvement_plan_section(self) -> None:
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=1,
            blind_spots=("security",),
            improvement_plan=("Add security_cues sensor.",),
        )
        output = render_harness_coverage_text(report)
        self.assertIn("Improvement plan:", output)

    def test_render_text_contains_baseline_comparison(self) -> None:
        report = HarnessCoverageReport(
            feature_id="test",
            dimensions=(),
            maturity_score=3,
            blind_spots=(),
            improvement_plan=(),
            baseline_comparison={"trend": "improving", "maturity_delta": 1},
        )
        output = render_harness_coverage_text(report)
        self.assertIn("Baseline comparison:", output)
        self.assertIn("improving", output)


class HarnessCoverageCliTests(TestCase):
    def test_coverage_help(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            main(["harness", "coverage", "--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_coverage_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "coverage", tmp, "--json"])
            output = out.getvalue()
            parsed = json.loads(output)
            self.assertIn("feature_id", parsed)
            self.assertIn("dimensions", parsed)

    def test_coverage_text_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "coverage", tmp])
            output = out.getvalue()
            self.assertIn("Harness coverage:", output)

    def test_coverage_with_feature_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "coverage", tmp, "--feature", "test-feature", "--json"])
            output = out.getvalue()
            parsed = json.loads(output)
            self.assertEqual(parsed["feature_id"], "test-feature")

    def test_coverage_invalid_slug_exit_code_2(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "coverage", tmp, "--feature", "INVALID SLUG", "--json"])
            self.assertEqual(code, 2)

    def test_coverage_save_baseline(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "coverage", tmp, "--save-baseline", "--json"])
            self.assertEqual(code, 0)
            baseline_path = root / ".specspine" / "harness-baseline.json"
            self.assertTrue(baseline_path.exists())

    def test_coverage_policy_below_threshold_exit_code_1(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "coverage", tmp, "--policy", "--json"])
            self.assertEqual(code, 1)

    def test_coverage_policy_above_threshold_exit_code_0(self) -> None:
        high_maturity_report = HarnessCoverageReport(
            feature_id="workspace",
            dimensions=tuple(
                HarnessDimensionCoverage(d, 1, 1, 100.0)
                for d in GOVERNED_DIMENSIONS
            ),
            maturity_score=5,
            blind_spots=(),
            improvement_plan=(),
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("specspine.cli.build_harness_coverage_report", return_value=high_maturity_report):
                out = StringIO()
                with redirect_stdout(out):
                    code = main(["harness", "coverage", tmp, "--policy", "--json"])
                self.assertEqual(code, 0)

    def test_coverage_workspace_exit_code_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "coverage", tmp, "--json"])
            self.assertEqual(code, 0)

    def test_coverage_feature_exit_code_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "coverage", tmp, "--feature", "test-feature", "--json"])
            self.assertEqual(code, 0)


class HarnessCoverageNoSubprocessNetworkTokenTests(TestCase):
    def test_no_subprocess_import(self) -> None:
        from specspine import harness_coverage
        source_file = Path(harness_coverage.__file__)
        content = source_file.read_text(encoding="utf-8")
        self.assertNotIn("import subprocess", content)
        self.assertNotIn("from subprocess", content)

    def test_no_urllib_import(self) -> None:
        from specspine import harness_coverage
        source_file = Path(harness_coverage.__file__)
        content = source_file.read_text(encoding="utf-8")
        self.assertNotIn("import urllib", content)
        self.assertNotIn("from urllib", content)

    def test_no_token_import(self) -> None:
        from specspine import harness_coverage
        source_file = Path(harness_coverage.__file__)
        content = source_file.read_text(encoding="utf-8")
        import_lines = [line for line in content.split("\n") if line.strip().startswith("import ") or line.strip().startswith("from ")]
        import_text = "\n".join(import_lines)
        self.assertNotIn("token", import_text.lower())

    def test_no_network_calls(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            with patch("urllib.request.urlopen") as mock_urlopen:
                build_harness_coverage_report(root, feature_filter="test-feature")
                mock_urlopen.assert_not_called()

    def test_no_subprocess_calls(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            with patch("subprocess.run") as mock_run:
                build_harness_coverage_report(root, feature_filter="test-feature")
                mock_run.assert_not_called()


class ConstantsTests(TestCase):
    def test_governed_dimensions_count(self) -> None:
        self.assertEqual(len(GOVERNED_DIMENSIONS), 8)

    def test_dimension_sensor_map_count(self) -> None:
        self.assertEqual(len(DIMENSION_SENSOR_MAP), 8)

    def test_dimension_sensor_map_keys_match_dimensions(self) -> None:
        self.assertEqual(set(DIMENSION_SENSOR_MAP.keys()), set(GOVERNED_DIMENSIONS))

    def test_maturity_labels_count(self) -> None:
        self.assertEqual(len(MATURITY_LABELS), 6)

    def test_maturity_labels_range(self) -> None:
        for i in range(6):
            self.assertIn(i, MATURITY_LABELS)

    def test_maturity_labels_values(self) -> None:
        self.assertEqual(MATURITY_LABELS[0], "none")
        self.assertEqual(MATURITY_LABELS[1], "initial")
        self.assertEqual(MATURITY_LABELS[2], "managed")
        self.assertEqual(MATURITY_LABELS[3], "defined")
        self.assertEqual(MATURITY_LABELS[4], "optimized")
        self.assertEqual(MATURITY_LABELS[5], "mastered")


class AllDimensionsCoveredTests(TestCase):
    def test_all_8_dimensions_in_report(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root, feature_filter="test-feature")
            dim_names = [d.dimension_name for d in report.dimensions]
            self.assertEqual(len(dim_names), 8)
            self.assertEqual(set(dim_names), set(GOVERNED_DIMENSIONS))

    def test_workspace_report_all_dimensions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_coverage_report(root)
            dim_names = [d.dimension_name for d in report.dimensions]
            self.assertEqual(len(dim_names), 8)
