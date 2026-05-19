import json
import os
import subprocess
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.health import (
    ConsistencyDrift,
    CoverageDebt,
    DependencyHealth,
    FeaturePipeline,
    HealthReport,
    QualityGates,
    ReadinessGates,
    RetrospectiveTheme,
    SecuritySummary,
    ValidationHealth,
    WorkspaceHealth,
    build_health_report,
    compute_health_score,
    generate_recommended_actions,
    render_health_json,
    render_health_text,
)
from specspine.workspace import init_workspace


class WorkspaceHealthTests(TestCase):
    def test_workspace_health_initialized(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertTrue(report.workspace.complete)
            self.assertEqual(len(report.workspace.missing), 0)
            self.assertGreater(len(report.workspace.present), 0)

    def test_workspace_health_missing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_health_report(root)
            self.assertFalse(report.workspace.complete)
            self.assertGreater(len(report.workspace.missing), 0)

    def test_workspace_health_as_dict(self) -> None:
        wh = WorkspaceHealth(
            complete=True,
            present=("a", "b"),
            missing=(),
        )
        d = wh.as_dict()
        self.assertTrue(d["complete"])
        self.assertEqual(d["present"], ["a", "b"])
        self.assertEqual(d["missing"], [])


class FeaturePipelineTests(TestCase):
    def test_feature_pipeline_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertEqual(report.feature_pipeline.features_total, 0)
            self.assertEqual(report.feature_pipeline.by_status, {})

    def test_feature_pipeline_with_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            spec_dir = root / "specs" / "features"
            spec_dir.mkdir(parents=True, exist_ok=True)
            (spec_dir / "test-feat.md").write_text(
                "# Spec\n\nFeature ID: test-feat\nStatus: proposed\n",
                encoding="utf-8",
            )
            exec_dir = root / "execution" / "features"
            exec_dir.mkdir(parents=True, exist_ok=True)
            (exec_dir / "test-feat.md").write_text(
                "# Execution\n\nFeature ID: test-feat\nStatus: proposed\n",
                encoding="utf-8",
            )
            qual_dir = root / "quality" / "features"
            qual_dir.mkdir(parents=True, exist_ok=True)
            (qual_dir / "test-feat.md").write_text(
                "# Quality\n\nFeature ID: test-feat\nStatus: proposed\n",
                encoding="utf-8",
            )
            report = build_health_report(root)
            self.assertEqual(report.feature_pipeline.features_total, 1)
            self.assertEqual(report.feature_pipeline.by_status.get("proposed"), 1)

    def test_feature_pipeline_as_dict(self) -> None:
        fp = FeaturePipeline(features_total=5, by_status={"proposed": 2, "validated": 3})
        d = fp.as_dict()
        self.assertEqual(d["features_total"], 5)
        self.assertEqual(d["by_status"], {"proposed": 2, "validated": 3})


class ValidationHealthTests(TestCase):
    def test_validation_health_passing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertGreater(report.validation_health.pass_count, 0)
            self.assertGreater(report.validation_health.total, 0)

    def test_validation_health_as_dict(self) -> None:
        vh = ValidationHealth(
            ok=True,
            pass_count=10,
            fail_count=2,
            warn_count=1,
            skip_count=0,
            total=13,
            top_failing_rules=({"id": "WC001", "message": "test"},),
        )
        d = vh.as_dict()
        self.assertTrue(d["ok"])
        self.assertEqual(d["fail_count"], 2)
        self.assertEqual(len(d["top_failing_rules"]), 1)
        self.assertEqual(d["top_failing_rules"][0]["id"], "WC001")


class CoverageDebtTests(TestCase):
    def test_coverage_debt_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertEqual(report.coverage_debt.features_with_debt, 0)
            self.assertEqual(report.coverage_debt.acceptance_criteria_total, 0)

    def test_coverage_debt_as_dict(self) -> None:
        cd = CoverageDebt(
            features_with_debt=3,
            missing_acceptance_criteria=10,
            covered_acceptance_criteria=20,
            acceptance_criteria_total=30,
            top_features_with_uncovered_ac=({"feature_id": "x", "missing": 5, "status": "proposed"},),
        )
        d = cd.as_dict()
        self.assertEqual(d["features_with_debt"], 3)
        self.assertEqual(d["missing_acceptance_criteria"], 10)


class ConsistencyDriftTests(TestCase):
    def test_consistency_drift_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertEqual(report.consistency_drift.features_scanned, 0)
            self.assertEqual(report.consistency_drift.checks_fail, 0)

    def test_consistency_drift_as_dict(self) -> None:
        cs = ConsistencyDrift(
            features_scanned=5,
            checks_pass=10,
            checks_fail=2,
            checks_warn=3,
            checks_total=15,
            top_failing_features=({"feature_id": "x", "fail_count": 1, "status": "proposed"},),
        )
        d = cs.as_dict()
        self.assertEqual(d["features_scanned"], 5)
        self.assertEqual(d["checks_fail"], 2)


class ReadinessGatesTests(TestCase):
    def test_readiness_gates_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertEqual(report.readiness_gates.features_total, 0)
            self.assertEqual(report.readiness_gates.ready, 0)

    def test_readiness_gates_as_dict(self) -> None:
        rg = ReadinessGates(
            features_total=10,
            ready=7,
            not_ready=3,
            blocking_checks_total=5,
            gaps_total=2,
            top_blockers=({"feature_id": "x", "blocking_checks": 2, "gaps": 1, "missing_files_count": 0},),
        )
        d = rg.as_dict()
        self.assertEqual(d["features_total"], 10)
        self.assertEqual(d["ready"], 7)


class QualityGatesTests(TestCase):
    def test_quality_gates_initialized(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertGreater(report.quality_gates.required_total, 0)
            self.assertEqual(report.quality_gates.required_done, 0)

    def test_quality_gates_missing_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_health_report(root)
            self.assertEqual(report.quality_gates.required_total, 0)

    def test_quality_gates_as_dict(self) -> None:
        qg = QualityGates(
            required_total=5,
            required_done=3,
            required_open=2,
            definition_total=1,
        )
        d = qg.as_dict()
        self.assertEqual(d["required_total"], 5)
        self.assertEqual(d["required_done"], 3)


class DependencyHealthTests(TestCase):
    def test_dependency_health_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertEqual(report.dependency_health.features_total, 0)
            self.assertEqual(report.dependency_health.cycles, [])

    def test_dependency_health_as_dict(self) -> None:
        dh = DependencyHealth(
            features_total=5,
            cycles=[["a", "b", "a"]],
            critical_path=["a", "b"],
            critical_path_effort=10,
        )
        d = dh.as_dict()
        self.assertEqual(d["features_total"], 5)
        self.assertEqual(len(d["cycles"]), 1)


class SecuritySummaryTests(TestCase):
    def test_security_summary_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertEqual(report.security_summary.cues_total, 0)

    def test_security_summary_as_dict(self) -> None:
        ss = SecuritySummary(cues_total=5, high=1, medium=2, low=2)
        d = ss.as_dict()
        self.assertEqual(d["cues_total"], 5)
        self.assertEqual(d["high"], 1)


class RetrospectiveThemeTests(TestCase):
    def test_retrospective_theme_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertEqual(report.retrospective_theme.top_blocker_theme, "none")

    def test_retrospective_theme_as_dict(self) -> None:
        rt = RetrospectiveTheme(
            top_blocker_theme="feature.test_coverage",
            blocking_checks={"x": 2},
            gaps={"y": 1},
            coverage_states={"complete": 3},
            open_tasks={"total": 5, "features": 2},
        )
        d = rt.as_dict()
        self.assertEqual(d["top_blocker_theme"], "feature.test_coverage")


class HealthScoreTests(TestCase):
    def test_score_zero_on_missing_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_health_report(root)
            self.assertEqual(report.health_score, 0)

    def test_score_nonzero_on_initialized_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertGreater(report.health_score, 0)

    def test_score_perfect_when_all_pass(self) -> None:
        ws = WorkspaceHealth(complete=True, present=("a",), missing=())
        fp = FeaturePipeline(features_total=2, by_status={"validated": 2})
        vh = ValidationHealth(ok=True, pass_count=10, fail_count=0, warn_count=0, skip_count=0, total=10, top_failing_rules=())
        cd = CoverageDebt(features_with_debt=0, missing_acceptance_criteria=0, covered_acceptance_criteria=10, acceptance_criteria_total=10, top_features_with_uncovered_ac=())
        cs = ConsistencyDrift(features_scanned=2, checks_pass=5, checks_fail=0, checks_warn=0, checks_total=5, top_failing_features=())
        rg = ReadinessGates(features_total=2, ready=2, not_ready=0, blocking_checks_total=0, gaps_total=0, top_blockers=())
        qg = QualityGates(required_total=5, required_done=5, required_open=0, definition_total=1)
        score = compute_health_score(ws, fp, vh, cd, cs, rg, qg)
        self.assertEqual(score, 100)

    def test_score_edge_case_zero(self) -> None:
        ws = WorkspaceHealth(complete=False, present=(), missing=("a",))
        fp = FeaturePipeline(features_total=0, by_status={})
        vh = ValidationHealth(ok=False, pass_count=0, fail_count=5, warn_count=0, skip_count=0, total=5, top_failing_rules=())
        cd = CoverageDebt(features_with_debt=2, missing_acceptance_criteria=10, covered_acceptance_criteria=0, acceptance_criteria_total=10, top_features_with_uncovered_ac=())
        cs = ConsistencyDrift(features_scanned=2, checks_pass=0, checks_fail=5, checks_warn=0, checks_total=5, top_failing_features=())
        rg = ReadinessGates(features_total=2, ready=0, not_ready=2, blocking_checks_total=5, gaps_total=2, top_blockers=())
        qg = QualityGates(required_total=5, required_done=0, required_open=5, definition_total=0)
        score = compute_health_score(ws, fp, vh, cd, cs, rg, qg)
        self.assertEqual(score, 0)

    def test_score_clamped_to_100(self) -> None:
        ws = WorkspaceHealth(complete=True, present=("a",), missing=())
        fp = FeaturePipeline(features_total=2, by_status={"validated": 2})
        vh = ValidationHealth(ok=True, pass_count=100, fail_count=0, warn_count=0, skip_count=0, total=100, top_failing_rules=())
        cd = CoverageDebt(features_with_debt=0, missing_acceptance_criteria=0, covered_acceptance_criteria=100, acceptance_criteria_total=100, top_features_with_uncovered_ac=())
        cs = ConsistencyDrift(features_scanned=2, checks_pass=100, checks_fail=0, checks_warn=0, checks_total=100, top_failing_features=())
        rg = ReadinessGates(features_total=2, ready=2, not_ready=0, blocking_checks_total=0, gaps_total=0, top_blockers=())
        qg = QualityGates(required_total=10, required_done=10, required_open=0, definition_total=1)
        score = compute_health_score(ws, fp, vh, cd, cs, rg, qg)
        self.assertLessEqual(score, 100)


class RecommendedActionsTests(TestCase):
    def test_actions_empty_on_healthy(self) -> None:
        ws = WorkspaceHealth(complete=True, present=("a",), missing=())
        fp = FeaturePipeline(features_total=0, by_status={})
        vh = ValidationHealth(ok=True, pass_count=10, fail_count=0, warn_count=0, skip_count=0, total=10, top_failing_rules=())
        cd = CoverageDebt(features_with_debt=0, missing_acceptance_criteria=0, covered_acceptance_criteria=10, acceptance_criteria_total=10, top_features_with_uncovered_ac=())
        cs = ConsistencyDrift(features_scanned=0, checks_pass=0, checks_fail=0, checks_warn=0, checks_total=0, top_failing_features=())
        rg = ReadinessGates(features_total=0, ready=0, not_ready=0, blocking_checks_total=0, gaps_total=0, top_blockers=())
        qg = QualityGates(required_total=0, required_done=0, required_open=0, definition_total=0)
        dh = DependencyHealth(features_total=0, cycles=[], critical_path=[], critical_path_effort=0)
        ss = SecuritySummary(cues_total=0, high=0, medium=0, low=0)
        rt = RetrospectiveTheme(top_blocker_theme="none", blocking_checks={}, gaps={}, coverage_states={}, open_tasks={})
        report = HealthReport(
            root="/tmp",
            workspace=ws,
            feature_pipeline=fp,
            validation_health=vh,
            coverage_debt=cd,
            consistency_drift=cs,
            readiness_gates=rg,
            quality_gates=qg,
            dependency_health=dh,
            security_summary=ss,
            retrospective_theme=rt,
            health_score=100,
            recommended_actions=(),
            recommended_commands=(),
            safety_notes=(),
        )
        actions = generate_recommended_actions(report)
        self.assertEqual(len(actions), 0)

    def test_actions_workspace_missing(self) -> None:
        ws = WorkspaceHealth(complete=False, present=(), missing=("spine.yaml",))
        fp = FeaturePipeline(features_total=0, by_status={})
        vh = ValidationHealth(ok=False, pass_count=0, fail_count=0, warn_count=0, skip_count=0, total=0, top_failing_rules=())
        cd = CoverageDebt(features_with_debt=0, missing_acceptance_criteria=0, covered_acceptance_criteria=0, acceptance_criteria_total=0, top_features_with_uncovered_ac=())
        cs = ConsistencyDrift(features_scanned=0, checks_pass=0, checks_fail=0, checks_warn=0, checks_total=0, top_failing_features=())
        rg = ReadinessGates(features_total=0, ready=0, not_ready=0, blocking_checks_total=0, gaps_total=0, top_blockers=())
        qg = QualityGates(required_total=0, required_done=0, required_open=0, definition_total=0)
        dh = DependencyHealth(features_total=0, cycles=[], critical_path=[], critical_path_effort=0)
        ss = SecuritySummary(cues_total=0, high=0, medium=0, low=0)
        rt = RetrospectiveTheme(top_blocker_theme="none", blocking_checks={}, gaps={}, coverage_states={}, open_tasks={})
        report = HealthReport(
            root="/tmp",
            workspace=ws,
            feature_pipeline=fp,
            validation_health=vh,
            coverage_debt=cd,
            consistency_drift=cs,
            readiness_gates=rg,
            quality_gates=qg,
            dependency_health=dh,
            security_summary=ss,
            retrospective_theme=rt,
            health_score=0,
            recommended_actions=(),
            recommended_commands=(),
            safety_notes=(),
        )
        actions = generate_recommended_actions(report)
        self.assertGreater(len(actions), 0)
        self.assertIn("workspace", actions[0].lower())

    def test_actions_validation_failures(self) -> None:
        ws = WorkspaceHealth(complete=True, present=("a",), missing=())
        fp = FeaturePipeline(features_total=0, by_status={})
        vh = ValidationHealth(ok=False, pass_count=5, fail_count=3, warn_count=0, skip_count=0, total=8, top_failing_rules=({"id": "WC001", "message": "test"},))
        cd = CoverageDebt(features_with_debt=0, missing_acceptance_criteria=0, covered_acceptance_criteria=5, acceptance_criteria_total=5, top_features_with_uncovered_ac=())
        cs = ConsistencyDrift(features_scanned=0, checks_pass=0, checks_fail=0, checks_warn=0, checks_total=0, top_failing_features=())
        rg = ReadinessGates(features_total=0, ready=0, not_ready=0, blocking_checks_total=0, gaps_total=0, top_blockers=())
        qg = QualityGates(required_total=0, required_done=0, required_open=0, definition_total=0)
        dh = DependencyHealth(features_total=0, cycles=[], critical_path=[], critical_path_effort=0)
        ss = SecuritySummary(cues_total=0, high=0, medium=0, low=0)
        rt = RetrospectiveTheme(top_blocker_theme="none", blocking_checks={}, gaps={}, coverage_states={}, open_tasks={})
        report = HealthReport(
            root="/tmp",
            workspace=ws,
            feature_pipeline=fp,
            validation_health=vh,
            coverage_debt=cd,
            consistency_drift=cs,
            readiness_gates=rg,
            quality_gates=qg,
            dependency_health=dh,
            security_summary=ss,
            retrospective_theme=rt,
            health_score=50,
            recommended_actions=(),
            recommended_commands=(),
            safety_notes=(),
        )
        actions = generate_recommended_actions(report)
        self.assertGreater(len(actions), 0)
        self.assertIn("validation", actions[0].lower())

    def test_actions_max_five(self) -> None:
        ws = WorkspaceHealth(complete=False, present=(), missing=("a", "b", "c"))
        fp = FeaturePipeline(features_total=0, by_status={})
        vh = ValidationHealth(ok=False, pass_count=0, fail_count=5, warn_count=0, skip_count=0, total=5, top_failing_rules=({"id": "WC001", "message": "t"}, {"id": "WC002", "message": "t"},))
        cd = CoverageDebt(features_with_debt=3, missing_acceptance_criteria=20, covered_acceptance_criteria=0, acceptance_criteria_total=20, top_features_with_uncovered_ac=())
        cs = ConsistencyDrift(features_scanned=3, checks_pass=0, checks_fail=5, checks_warn=0, checks_total=5, top_failing_features=())
        rg = ReadinessGates(features_total=3, ready=0, not_ready=3, blocking_checks_total=10, gaps_total=5, top_blockers=())
        qg = QualityGates(required_total=0, required_done=0, required_open=0, definition_total=0)
        dh = DependencyHealth(features_total=0, cycles=[], critical_path=[], critical_path_effort=0)
        ss = SecuritySummary(cues_total=0, high=0, medium=0, low=0)
        rt = RetrospectiveTheme(top_blocker_theme="none", blocking_checks={}, gaps={}, coverage_states={}, open_tasks={})
        report = HealthReport(
            root="/tmp",
            workspace=ws,
            feature_pipeline=fp,
            validation_health=vh,
            coverage_debt=cd,
            consistency_drift=cs,
            readiness_gates=rg,
            quality_gates=qg,
            dependency_health=dh,
            security_summary=ss,
            retrospective_theme=rt,
            health_score=0,
            recommended_actions=(),
            recommended_commands=(),
            safety_notes=(),
        )
        actions = generate_recommended_actions(report)
        self.assertLessEqual(len(actions), 5)


class JsonOutputTests(TestCase):
    def test_json_parses(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_json(report)
            data = json.loads(output)
            self.assertIn("health_score", data)
            self.assertIn("workspace", data)
            self.assertIn("feature_pipeline", data)

    def test_json_sorted_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_json(report)
            data = json.loads(output)
            keys = list(data.keys())
            self.assertEqual(keys, sorted(keys))

    def test_json_has_all_sections(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_json(report)
            data = json.loads(output)
            required_keys = {
                "root", "workspace", "feature_pipeline", "validation_health",
                "coverage_debt", "consistency_drift", "readiness_gates",
                "quality_gates", "dependency_health", "security_summary",
                "retrospective_theme", "health_score", "recommended_actions",
                "recommended_commands", "safety_notes",
            }
            self.assertTrue(required_keys.issubset(set(data.keys())))

    def test_json_health_score_is_int(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_json(report)
            data = json.loads(output)
            self.assertIsInstance(data["health_score"], int)
            self.assertGreaterEqual(data["health_score"], 0)
            self.assertLessEqual(data["health_score"], 100)

    def test_json_recommended_actions_is_list(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_json(report)
            data = json.loads(output)
            self.assertIsInstance(data["recommended_actions"], list)


class TextOutputTests(TestCase):
    def test_text_contains_health_score(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_text(report)
            self.assertIn("Health Score:", output)

    def test_text_contains_workspace_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_text(report)
            self.assertIn("Workspace:", output)

    def test_text_contains_recommended_actions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_text(report)
            self.assertIn("Recommended Actions:", output)

    def test_text_contains_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_text(report)
            self.assertIn("Safety Notes:", output)

    def test_text_under_80_lines(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_text(report)
            lines = output.split("\n")
            self.assertLess(len(lines), 80)

    def test_text_missing_workspace_shows_marker(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_health_report(root)
            output = render_health_text(report)
            self.assertIn("INCOMPLETE", output)

    def test_text_healthy_workspace_shows_ok(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_text(report)
            self.assertIn("[OK]", output)


class CliTests(TestCase):
    def test_status_health_help(self) -> None:
        stdout = StringIO()
        with redirect_stdout(stdout):
            try:
                main(["status", "--help"])
            except SystemExit:
                pass
        output = stdout.getvalue()
        self.assertIn("--health", output)

    def test_status_health_json_on_empty_dir(self) -> None:
        with TemporaryDirectory() as tmp:
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", tmp, "--health", "--json"])
            self.assertEqual(exit_code, 0)
            data = json.loads(stdout.getvalue())
            self.assertIn("health_score", data)
            self.assertEqual(data["health_score"], 0)

    def test_status_health_json_on_initialized(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "health", "--json"])
            self.assertEqual(exit_code, 0)
            data = json.loads(stdout.getvalue())
            self.assertGreater(data["health_score"], 0)

    def test_status_health_text_on_initialized(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "health"])
            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Health Dashboard:", output)
            self.assertIn("Health Score:", output)

    def test_status_health_flag_on_initialized(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", str(root), "--health", "--json"])
            self.assertEqual(exit_code, 0)
            data = json.loads(stdout.getvalue())
            self.assertIn("health_score", data)

    def test_status_default_still_works(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            data = json.loads(stdout.getvalue())
            self.assertIn("workspace", data)

    def test_status_health_path_optional(self) -> None:
        with TemporaryDirectory() as tmp:
            orig_cwd = os.getcwd()
            os.chdir(tmp)
            init_workspace(Path(tmp))
            try:
                stdout = StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["status", "health", "--json"])
                self.assertEqual(exit_code, 0)
                data = json.loads(stdout.getvalue())
                self.assertIn("health_score", data)
            finally:
                os.chdir(orig_cwd)


class GracefulDegradationTests(TestCase):
    def test_health_report_no_features_dir(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".specspine").mkdir()
            (root / "specs").mkdir()
            (root / "execution").mkdir()
            (root / "quality").mkdir()
            (root / ".specspine" / "spine.yaml").write_text(
                "name: test\nversion: 0.1\n",
                encoding="utf-8",
            )
            (root / "specs" / "intent.md").write_text("# Intent\n", encoding="utf-8")
            (root / "specs" / "product.md").write_text("# Product\n", encoding="utf-8")
            (root / "specs" / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
            (root / "execution" / "plan.md").write_text("# Plan\n", encoding="utf-8")
            (root / "execution" / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
            (root / "quality" / "checklist.md").write_text("# Quality\n", encoding="utf-8")
            (root / "quality" / "review.md").write_text("# Review\n", encoding="utf-8")
            report = build_health_report(root)
            self.assertIsInstance(report.health_score, int)

    def test_health_report_empty_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_health_report(root)
            self.assertEqual(report.health_score, 0)
            self.assertFalse(report.workspace.complete)


class SafetyNotesTests(TestCase):
    def test_safety_notes_present(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            self.assertGreater(len(report.safety_notes), 0)

    def test_safety_notes_in_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_json(report)
            data = json.loads(output)
            self.assertIsInstance(data["safety_notes"], list)
            self.assertGreater(len(data["safety_notes"]), 0)

    def test_safety_notes_in_text(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_health_report(root)
            output = render_health_text(report)
            for note in report.safety_notes:
                self.assertIn(note, output)


class NoSubprocessNetworkTests(TestCase):
    def test_health_module_no_subprocess_import(self) -> None:
        from specspine import health
        source = Path(health.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import subprocess", source)
        self.assertNotIn("from subprocess", source)

    def test_health_module_no_network_imports(self) -> None:
        from specspine import health
        source = Path(health.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import requests", source)
        self.assertNotIn("import urllib", source)
        self.assertNotIn("import socket", source)
        self.assertNotIn("import http", source)

    def test_health_module_no_token_imports(self) -> None:
        from specspine import health
        source = Path(health.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import token", source)
        self.assertNotIn("from token", source)
