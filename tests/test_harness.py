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
from specspine.harness import (
    HarnessFeedbackReport,
    HarnessFeedbackSensor,
    HarnessQualityReport,
    RepairStrategy,
    _classify_root_causes,
    _collect_gaps_from_sensors,
    _extract_ac_ids,
    _generate_repair_strategies,
    _read_feature_contents,
    _run_computational_sensors,
    _run_inferential_sensors,
    build_harness_feedback,
    build_harness_quality,
    render_harness_feedback_json,
    render_harness_feedback_text,
    render_harness_quality_json,
    render_harness_quality_text,
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


class HarnessFeedbackSensorTests(TestCase):
    def test_sensor_as_dict(self) -> None:
        sensor = HarnessFeedbackSensor(
            sensor_type="computational",
            name="verification_matrix",
            status="pass",
            output={"verified": 1},
            ac_ids=("AC001",),
        )
        result = sensor.as_dict()
        self.assertEqual(result["sensor_type"], "computational")
        self.assertEqual(result["name"], "verification_matrix")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["output"], {"verified": 1})
        self.assertEqual(result["ac_ids"], ["AC001"])

    def test_sensor_as_dict_empty_ac_ids(self) -> None:
        sensor = HarnessFeedbackSensor(
            sensor_type="inferential",
            name="consistency_scan",
            status="pass",
            output={},
        )
        result = sensor.as_dict()
        self.assertEqual(result["ac_ids"], [])


class RepairStrategyTests(TestCase):
    def test_strategy_as_dict(self) -> None:
        strategy = RepairStrategy(
            ac_id="AC001",
            target_file="specs/features/test.md",
            edit_description="Fix AC001",
            verification_command="specspine verify matrix test . --json",
            success_criteria="AC001 passes",
        )
        result = strategy.as_dict()
        self.assertEqual(result["ac_id"], "AC001")
        self.assertEqual(result["target_file"], "specs/features/test.md")
        self.assertEqual(result["edit_description"], "Fix AC001")
        self.assertEqual(
            result["verification_command"],
            "specspine verify matrix test . --json",
        )
        self.assertEqual(result["success_criteria"], "AC001 passes")


class HarnessQualityReportTests(TestCase):
    def test_quality_as_dict(self) -> None:
        report = HarnessQualityReport(
            feature_id="test",
            governed_dimensions=("verification", "coverage"),
            sensor_count=2,
            harness_coverage_pct=50.0,
            dimension_scores={"verification": 100.0, "coverage": 0.0},
        )
        result = report.as_dict()
        self.assertEqual(result["feature_id"], "test")
        self.assertEqual(result["sensor_count"], 2)
        self.assertAlmostEqual(result["harness_coverage_pct"], 50.0)
        self.assertEqual(result["dimension_scores"]["verification"], 100.0)


class HarnessFeedbackReportTests(TestCase):
    def test_report_as_dict(self) -> None:
        report = HarnessFeedbackReport(
            feature_id="test",
            status="healthy",
            sensors=(),
            repair_strategies=(),
            root_causes={},
            steering_summary={},
            harness_quality=None,
            safety_notes=(),
        )
        result = report.as_dict()
        self.assertEqual(result["feature_id"], "test")
        self.assertEqual(result["status"], "healthy")
        self.assertNotIn("harness_quality", result)

    def test_report_as_dict_with_quality(self) -> None:
        quality = HarnessQualityReport(
            feature_id="test",
            governed_dimensions=(),
            sensor_count=0,
            harness_coverage_pct=0.0,
            dimension_scores={},
        )
        report = HarnessFeedbackReport(
            feature_id="test",
            status="healthy",
            sensors=(),
            repair_strategies=(),
            root_causes={},
            steering_summary={},
            harness_quality=quality,
            safety_notes=(),
        )
        result = report.as_dict()
        self.assertIn("harness_quality", result)


class ReadFeatureContentsTests(TestCase):
    def test_reads_existing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            contents = _read_feature_contents(root, "test-feature")
            self.assertIn("spec", contents)
            self.assertIn("execution", contents)
            self.assertIn("quality", contents)

    def test_returns_empty_when_no_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            contents = _read_feature_contents(root, "nonexistent")
            self.assertEqual(contents, {})


class ExtractAcIdsTests(TestCase):
    def test_extracts_ac_ids_from_spec(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            contents = _read_feature_contents(root, "test-feature")
            ac_ids = _extract_ac_ids(contents)
            self.assertIn("AC001", ac_ids)
            self.assertIn("AC002", ac_ids)

    def test_returns_empty_when_no_spec(self) -> None:
        ac_ids = _extract_ac_ids({})
        self.assertEqual(ac_ids, ())


class ComputationalSensorsTests(TestCase):
    def test_runs_all_computational_sensors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            sensors = _run_computational_sensors("test-feature", root)
            names = [s.name for s in sensors]
            self.assertIn("verification_matrix", names)
            self.assertIn("coverage_debt", names)
            self.assertIn("grading_rubric", names)
            self.assertIn("validation_contract", names)

    def test_computational_sensors_count(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            sensors = _run_computational_sensors("test-feature", root)
            self.assertEqual(len(sensors), 4)

    def test_computational_sensor_types(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            sensors = _run_computational_sensors("test-feature", root)
            for sensor in sensors:
                self.assertEqual(sensor.sensor_type, "computational")

    def test_computational_sensors_for_missing_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            sensors = _run_computational_sensors("nonexistent", root)
            self.assertEqual(len(sensors), 4)
            fail_warn = [s for s in sensors if s.status in ("fail", "warn")]
            self.assertEqual(len(fail_warn), 4)


class InferentialSensorsTests(TestCase):
    def test_runs_all_inferential_sensors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            sensors = _run_inferential_sensors("test-feature", root)
            names = [s.name for s in sensors]
            self.assertIn("consistency_scan", names)
            self.assertIn("hygiene_scan", names)
            self.assertIn("security_cues", names)
            self.assertIn("change_risk", names)

    def test_inferential_sensors_count(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            sensors = _run_inferential_sensors("test-feature", root)
            self.assertEqual(len(sensors), 4)

    def test_inferential_sensor_types(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            sensors = _run_inferential_sensors("test-feature", root)
            for sensor in sensors:
                self.assertEqual(sensor.sensor_type, "inferential")

    def test_inferential_sensors_for_missing_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            sensors = _run_inferential_sensors("nonexistent", root)
            self.assertEqual(len(sensors), 4)


class RepairStrategyGenerationTests(TestCase):
    def test_generates_strategies_for_failed_acs(self) -> None:
        sensor = HarnessFeedbackSensor(
            sensor_type="computational",
            name="coverage_debt",
            status="fail",
            output={},
            ac_ids=("AC001",),
        )
        report = HarnessFeedbackReport(
            feature_id="test",
            status="unhealthy",
            sensors=(sensor,),
            repair_strategies=(),
            root_causes={},
            steering_summary={},
            harness_quality=None,
            safety_notes=(),
        )
        strategies = _generate_repair_strategies(report)
        self.assertEqual(len(strategies), 1)
        self.assertEqual(strategies[0].ac_id, "AC001")

    def test_no_strategies_when_all_pass(self) -> None:
        sensor = HarnessFeedbackSensor(
            sensor_type="computational",
            name="verification_matrix",
            status="pass",
            output={},
            ac_ids=("AC001",),
        )
        report = HarnessFeedbackReport(
            feature_id="test",
            status="healthy",
            sensors=(sensor,),
            repair_strategies=(),
            root_causes={},
            steering_summary={},
            harness_quality=None,
            safety_notes=(),
        )
        strategies = _generate_repair_strategies(report)
        self.assertEqual(len(strategies), 0)

    def test_strategy_targets_quality_file_for_coverage_debt(self) -> None:
        sensor = HarnessFeedbackSensor(
            sensor_type="computational",
            name="coverage_debt",
            status="fail",
            output={},
            ac_ids=("AC001",),
        )
        report = HarnessFeedbackReport(
            feature_id="test",
            status="unhealthy",
            sensors=(sensor,),
            repair_strategies=(),
            root_causes={},
            steering_summary={},
            harness_quality=None,
            safety_notes=(),
        )
        strategies = _generate_repair_strategies(report)
        self.assertIn("quality/features/test.md", strategies[0].target_file)

    def test_strategy_targets_spec_file_for_other_failures(self) -> None:
        sensor = HarnessFeedbackSensor(
            sensor_type="computational",
            name="verification_matrix",
            status="fail",
            output={},
            ac_ids=("AC001",),
        )
        report = HarnessFeedbackReport(
            feature_id="test",
            status="unhealthy",
            sensors=(sensor,),
            repair_strategies=(),
            root_causes={},
            steering_summary={},
            harness_quality=None,
            safety_notes=(),
        )
        strategies = _generate_repair_strategies(report)
        self.assertIn("specs/features/test.md", strategies[0].target_file)

    def test_strategy_verification_command(self) -> None:
        sensor = HarnessFeedbackSensor(
            sensor_type="computational",
            name="coverage_debt",
            status="fail",
            output={},
            ac_ids=("AC001",),
        )
        report = HarnessFeedbackReport(
            feature_id="test",
            status="unhealthy",
            sensors=(sensor,),
            repair_strategies=(),
            root_causes={},
            steering_summary={},
            harness_quality=None,
            safety_notes=(),
        )
        strategies = _generate_repair_strategies(report)
        self.assertIn("verify matrix", strategies[0].verification_command)

    def test_deduplicates_ac_ids(self) -> None:
        sensor1 = HarnessFeedbackSensor(
            sensor_type="computational",
            name="coverage_debt",
            status="fail",
            output={},
            ac_ids=("AC001",),
        )
        sensor2 = HarnessFeedbackSensor(
            sensor_type="computational",
            name="grading_rubric",
            status="fail",
            output={},
            ac_ids=("AC001",),
        )
        report = HarnessFeedbackReport(
            feature_id="test",
            status="unhealthy",
            sensors=(sensor1, sensor2),
            repair_strategies=(),
            root_causes={},
            steering_summary={},
            harness_quality=None,
            safety_notes=(),
        )
        strategies = _generate_repair_strategies(report)
        self.assertEqual(len(strategies), 1)


class RootCauseClassificationTests(TestCase):
    def test_classifies_missing_spec(self) -> None:
        gaps = [{"id": "missing_file", "message": "Missing spec file"}]
        result = _classify_root_causes(gaps)
        self.assertEqual(len(result["missing_spec"]), 1)

    def test_classifies_missing_code(self) -> None:
        gaps = [{"id": "missing_code", "message": "Not implemented"}]
        result = _classify_root_causes(gaps)
        self.assertEqual(len(result["missing_code"]), 1)

    def test_classifies_missing_test(self) -> None:
        gaps = [{"id": "missing_test", "message": "No test coverage"}]
        result = _classify_root_causes(gaps)
        self.assertEqual(len(result["missing_test"]), 1)

    def test_classifies_stale_coverage(self) -> None:
        gaps = [{"id": "stale_link", "message": "stale reference"}]
        result = _classify_root_causes(gaps)
        self.assertEqual(len(result["stale_coverage"]), 1)

    def test_classifies_contract_violation(self) -> None:
        gaps = [{"id": "unknown", "message": "Unknown issue"}]
        result = _classify_root_causes(gaps)
        self.assertEqual(len(result["contract_violation"]), 1)

    def test_empty_gaps(self) -> None:
        result = _classify_root_causes([])
        for category in result:
            self.assertEqual(len(result[category]), 0)

    def test_multiple_gaps_same_category(self) -> None:
        gaps = [
            {"id": "missing_test", "message": "No test 1"},
            {"id": "missing_test", "message": "No test 2"},
        ]
        result = _classify_root_causes(gaps)
        self.assertEqual(len(result["missing_test"]), 2)


class CollectGapsFromSensorsTests(TestCase):
    def test_collects_gaps_from_failed_sensors(self) -> None:
        sensor = HarnessFeedbackSensor(
            sensor_type="computational",
            name="verification_matrix",
            status="fail",
            output={},
            ac_ids=("AC001",),
        )
        gaps = _collect_gaps_from_sensors([sensor])
        self.assertEqual(len(gaps), 2)

    def test_no_gaps_from_passing_sensors(self) -> None:
        sensor = HarnessFeedbackSensor(
            sensor_type="computational",
            name="verification_matrix",
            status="pass",
            output={},
            ac_ids=("AC001",),
        )
        gaps = _collect_gaps_from_sensors([sensor])
        self.assertEqual(len(gaps), 1)

    def test_no_gaps_from_empty_sensors(self) -> None:
        gaps = _collect_gaps_from_sensors([])
        self.assertEqual(len(gaps), 0)


class BuildHarnessFeedbackTests(TestCase):
    def test_build_feedback_for_valid_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            self.assertEqual(report.feature_id, "test-feature")
            self.assertGreater(len(report.sensors), 0)
            self.assertIsInstance(report.steering_summary, dict)

    def test_build_feedback_sensor_count(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            self.assertEqual(len(report.sensors), 8)

    def test_build_feedback_has_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            self.assertGreater(len(report.safety_notes), 0)

    def test_build_feedback_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(InvalidFeatureSlug):
                build_harness_feedback("INVALID SLUG", root)

    def test_build_feedback_missing_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_harness_feedback("nonexistent", root)
            self.assertEqual(report.feature_id, "nonexistent")
            fail_sensors = sum(1 for s in report.sensors if s.status == "fail")
            self.assertGreater(fail_sensors, 0)

    def test_build_feedback_status_unhealthy_when_failures(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            self.assertIn(report.status, ("healthy", "degraded", "unhealthy"))

    def test_build_feedback_repair_strategies(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            self.assertIsInstance(report.repair_strategies, tuple)

    def test_build_feedback_root_causes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            self.assertIn("missing_test", report.root_causes)
            self.assertIn("missing_spec", report.root_causes)

    def test_build_feedback_harness_quality(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            self.assertIsNotNone(report.harness_quality)


class BuildHarnessQualityTests(TestCase):
    def test_build_quality_for_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_quality(root, "test-feature")
            self.assertEqual(report.feature_id, "test-feature")
            self.assertGreater(len(report.governed_dimensions), 0)

    def test_build_quality_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_quality(root)
            self.assertEqual(report.feature_id, "workspace")

    def test_build_quality_dimension_scores(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_quality(root, "test-feature")
            self.assertIn("verification", report.dimension_scores)
            self.assertIn("coverage", report.dimension_scores)

    def test_build_quality_harness_coverage_pct(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_quality(root, "test-feature")
            self.assertGreaterEqual(report.harness_coverage_pct, 0.0)
            self.assertLessEqual(report.harness_coverage_pct, 100.0)

    def test_build_quality_for_missing_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_harness_quality(root, "nonexistent")
            self.assertEqual(report.feature_id, "nonexistent")
            self.assertGreater(report.sensor_count, 0)
            self.assertGreaterEqual(report.harness_coverage_pct, 0.0)
            self.assertLessEqual(report.harness_coverage_pct, 100.0)


class RenderHarnessFeedbackJsonTests(TestCase):
    def test_render_feedback_json_is_valid_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            output = render_harness_feedback_json(report)
            parsed = json.loads(output)
            self.assertIn("feature_id", parsed)

    def test_render_feedback_json_contains_sensors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            output = render_harness_feedback_json(report)
            parsed = json.loads(output)
            self.assertIn("sensors", parsed)

    def test_render_feedback_json_contains_repair_strategies(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            output = render_harness_feedback_json(report)
            parsed = json.loads(output)
            self.assertIn("repair_strategies", parsed)


class RenderHarnessFeedbackTextTests(TestCase):
    def test_render_feedback_text_contains_feature_id(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            output = render_harness_feedback_text(report)
            self.assertIn("test-feature", output)

    def test_render_feedback_text_contains_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            output = render_harness_feedback_text(report)
            self.assertIn("Status:", output)

    def test_render_feedback_text_contains_sensors_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            output = render_harness_feedback_text(report)
            self.assertIn("Sensors:", output)

    def test_render_feedback_text_contains_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_feedback("test-feature", root)
            output = render_harness_feedback_text(report)
            self.assertIn("Safety notes:", output)


class RenderHarnessQualityJsonTests(TestCase):
    def test_render_quality_json_is_valid_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_quality(root, "test-feature")
            output = render_harness_quality_json(report)
            parsed = json.loads(output)
            self.assertIn("feature_id", parsed)

    def test_render_quality_json_contains_dimensions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_quality(root, "test-feature")
            output = render_harness_quality_json(report)
            parsed = json.loads(output)
            self.assertIn("dimension_scores", parsed)


class RenderHarnessQualityTextTests(TestCase):
    def test_render_quality_text_contains_feature_id(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_quality(root, "test-feature")
            output = render_harness_quality_text(report)
            self.assertIn("test-feature", output)

    def test_render_quality_text_contains_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_quality(root, "test-feature")
            output = render_harness_quality_text(report)
            self.assertIn("Coverage:", output)

    def test_render_quality_text_contains_dimensions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            report = build_harness_quality(root, "test-feature")
            output = render_harness_quality_text(report)
            self.assertIn("Dimensions:", output)


class HarnessCliFeedbackTests(TestCase):
    def test_feedback_help(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            main(["harness", "feedback", "--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_feedback_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "feedback", "test-feature", tmp, "--json"])
            output = out.getvalue()
            parsed = json.loads(output)
            self.assertEqual(parsed["feature_id"], "test-feature")

    def test_feedback_text_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "feedback", "test-feature", tmp])
            output = out.getvalue()
            self.assertIn("Harness feedback:", output)

    def test_feedback_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "feedback", "INVALID SLUG", tmp, "--json"])
            self.assertEqual(code, 2)

    def test_feedback_missing_feature_exit_code(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "feedback", "nonexistent", tmp, "--json"])
            self.assertEqual(code, 1)


class HarnessCliRepairTests(TestCase):
    def test_repair_help(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            main(["harness", "repair", "--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_repair_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "repair", "test-feature", tmp, "--json"])
            output = out.getvalue()
            parsed = json.loads(output)
            self.assertIn("repair_strategies", parsed)

    def test_repair_text_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "repair", "test-feature", tmp])
            output = out.getvalue()
            self.assertIn("Repair strategies:", output)

    def test_repair_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "repair", "INVALID SLUG", tmp, "--json"])
            self.assertEqual(code, 2)


class HarnessCliQualityTests(TestCase):
    def test_quality_help(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            main(["harness", "quality", "--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_quality_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "quality", tmp, "--json"])
            output = out.getvalue()
            parsed = json.loads(output)
            self.assertIn("feature_id", parsed)
            self.assertIn("dimension_scores", parsed)

    def test_quality_text_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "quality", tmp])
            output = out.getvalue()
            self.assertIn("Harness quality:", output)

    def test_quality_exit_code_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            out = StringIO()
            with redirect_stdout(out):
                code = main(["harness", "quality", tmp, "--json"])
            self.assertEqual(code, 0)


class HarnessNoSubprocessNetworkTokenTests(TestCase):
    def test_no_subprocess_import_in_harness(self) -> None:
        from specspine import harness
        source_file = Path(harness.__file__)
        content = source_file.read_text(encoding="utf-8")
        self.assertNotIn("import subprocess", content)
        self.assertNotIn("from subprocess", content)

    def test_no_urllib_import_in_harness(self) -> None:
        from specspine import harness
        source_file = Path(harness.__file__)
        content = source_file.read_text(encoding="utf-8")
        self.assertNotIn("import urllib", content)
        self.assertNotIn("from urllib", content)

    def test_no_token_import_in_harness(self) -> None:
        from specspine import harness
        source_file = Path(harness.__file__)
        content = source_file.read_text(encoding="utf-8")
        import_lines = [line for line in content.split("\n") if line.strip().startswith("import ") or line.strip().startswith("from ")]
        import_text = "\n".join(import_lines)
        self.assertNotIn("token", import_text.lower())

    def test_no_network_calls_in_feedback(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            with patch("urllib.request.urlopen") as mock_urlopen:
                build_harness_feedback("test-feature", root)
                mock_urlopen.assert_not_called()

    def test_no_subprocess_calls_in_quality(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_feature(root)
            with patch("subprocess.run") as mock_run:
                build_harness_quality(root, "test-feature")
                mock_run.assert_not_called()
