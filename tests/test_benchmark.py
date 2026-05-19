import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.benchmark import (
    VALID_GROUP_BY,
    BenchmarkReport,
    FeatureMetrics,
    _aggregate_metrics,
    _compute_feature_metrics,
    _compute_trends,
    _generate_recommendations,
    _identify_improvement_areas,
    _identify_top_performers,
    _median,
    _percentile,
    _primary_issue,
    build_benchmark_report,
    render_benchmark_json,
    render_benchmark_text,
)
from specspine.cli import main
from specspine.workspace import init_workspace


def _create_feature(root: Path, slug: str, *, status: str = "proposed", priority: str = "medium", effort: str = "unknown", project: str = "unassigned", ac_ids: list[str] | None = None, task_ids: list[str] | None = None, cov_links: list[tuple[str, bool]] | None = None) -> None:
    spec_dir = root / "specs" / "features"
    spec_dir.mkdir(parents=True, exist_ok=True)
    ac_lines = ""
    if ac_ids:
        ac_lines = "\n".join(f"- [ ] {ac_id}: Verify the behavior." for ac_id in ac_ids)
    else:
        ac_lines = "- [ ] AC001: Basic behavior."
    (spec_dir / f"{slug}.md").write_text(
        f"# {slug.replace('-', ' ').title()}\n\n"
        f"Feature ID: {slug}\n"
        f"Status: {status}\n"
        f"Priority: {priority}\n"
        f"Effort: {effort}\n"
        f"Project: {project}\n\n"
        f"## Acceptance Criteria\n\n{ac_lines}\n",
        encoding="utf-8",
    )

    exec_dir = root / "execution" / "features"
    exec_dir.mkdir(parents=True, exist_ok=True)
    task_lines = ""
    if task_ids:
        task_lines = "\n".join(f"- [ ] {tid}: Implementation step." for tid in task_ids)
    else:
        task_lines = "- [ ] TASK001: Basic task."
    (exec_dir / f"{slug}.md").write_text(
        f"# {slug.replace('-', ' ').title()} Execution\n\n"
        f"Feature ID: {slug}\n"
        f"Status: {status}\n\n"
        f"## Tasks\n\n{task_lines}\n",
        encoding="utf-8",
    )

    qual_dir = root / "quality" / "features"
    qual_dir.mkdir(parents=True, exist_ok=True)
    cov_lines = ""
    if cov_links is not None:
        cov_lines = "\n".join(
            f"- [{'x' if done else ' '}] {ac_id} -> tests/test_{slug}.py::{ac_id}"
            for ac_id, done in cov_links
        )
    else:
        cov_lines = f"- [ ] AC001 -> tests/test_{slug}.py"
    (qual_dir / f"{slug}.md").write_text(
        f"# {slug.replace('-', ' ').title()} Quality\n\n"
        f"Feature ID: {slug}\n"
        f"Status: {status}\n\n"
        f"## Test Coverage\n\n{cov_lines}\n",
        encoding="utf-8",
    )


class FeatureMetricsTests(TestCase):
    def test_feature_metrics_as_dict(self) -> None:
        m = FeatureMetrics(
            feature_id="test-feat",
            status="proposed",
            priority="high",
            effort="small",
            project="core",
            ac_count=3,
            task_count=5,
            test_count=3,
            coverage_pct=100.0,
            validation_pass=10,
            validation_fail=0,
            consistency_fail=0,
            drift_events=0,
            lifecycle_duration_days=0.0,
        )
        d = m.as_dict()
        self.assertEqual(d["feature_id"], "test-feat")
        self.assertEqual(d["ac_count"], 3)
        self.assertEqual(d["coverage_pct"], 100.0)
        self.assertEqual(d["status"], "proposed")

    def test_feature_metrics_from_scratch(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "basic", ac_ids=["AC001", "AC002"], task_ids=["TASK001"])
            m = _compute_feature_metrics("basic", root)
            self.assertEqual(m.feature_id, "basic")
            self.assertEqual(m.ac_count, 2)
            self.assertEqual(m.task_count, 1)
            self.assertEqual(m.status, "proposed")

    def test_feature_metrics_empty_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "empty")
            m = _compute_feature_metrics("empty", root)
            self.assertEqual(m.feature_id, "empty")
            self.assertGreaterEqual(m.ac_count, 1)
            self.assertGreaterEqual(m.task_count, 0)

    def test_feature_metrics_full_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(
                root,
                "covered",
                ac_ids=["AC001", "AC002", "AC003"],
                cov_links=[("AC001", True), ("AC002", True), ("AC003", True)],
            )
            m = _compute_feature_metrics("covered", root)
            self.assertEqual(m.ac_count, 3)
            self.assertEqual(m.test_count, 3)
            self.assertEqual(m.coverage_pct, 100.0)

    def test_feature_metrics_partial_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(
                root,
                "partial",
                ac_ids=["AC001", "AC002"],
                cov_links=[("AC001", True), ("AC002", False)],
            )
            m = _compute_feature_metrics("partial", root)
            self.assertEqual(m.ac_count, 2)
            self.assertEqual(m.test_count, 2)
            self.assertEqual(m.coverage_pct, 50.0)

    def test_feature_metrics_zero_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(
                root,
                "uncovered",
                ac_ids=["AC001"],
                cov_links=[("AC001", False)],
            )
            m = _compute_feature_metrics("uncovered", root)
            self.assertEqual(m.coverage_pct, 0.0)

    def test_feature_metrics_priority(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "high-p", priority="high")
            m = _compute_feature_metrics("high-p", root)
            self.assertEqual(m.priority, "high")

    def test_feature_metrics_effort(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "big", effort="large")
            m = _compute_feature_metrics("big", root)
            self.assertEqual(m.effort, "large")

    def test_feature_metrics_project(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "proj", project="platform")
            m = _compute_feature_metrics("proj", root)
            self.assertEqual(m.project, "platform")

    def test_feature_metrics_status_inconsistent(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "mixed", status="proposed")
            exec_path = root / "execution" / "features" / "mixed.md"
            content = exec_path.read_text(encoding="utf-8")
            content = content.replace("Status: proposed", "Status: implemented")
            exec_path.write_text(content, encoding="utf-8")
            m = _compute_feature_metrics("mixed", root)
            self.assertEqual(m.status, "mixed")

    def test_feature_metrics_missing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            spec_dir = root / "specs" / "features"
            spec_dir.mkdir(parents=True, exist_ok=True)
            (spec_dir / "partial.md").write_text(
                "# Partial\n\nFeature ID: partial\nStatus: proposed\n",
                encoding="utf-8",
            )
            m = _compute_feature_metrics("partial", root)
            self.assertEqual(m.feature_id, "partial")
            self.assertGreaterEqual(m.ac_count, 0)

    def test_feature_metrics_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with self.assertRaises(Exception):
                _compute_feature_metrics("INVALID SLUG", root)

    def test_feature_metrics_multiple_tasks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(
                root,
                "multi-task",
                task_ids=["TASK001", "TASK002", "TASK003", "TASK004"],
            )
            m = _compute_feature_metrics("multi-task", root)
            self.assertEqual(m.task_count, 4)


class AggregateMetricsTests(TestCase):
    def test_aggregate_empty(self) -> None:
        result = _aggregate_metrics([], "priority")
        self.assertEqual(result["overall"]["total_features"], 0)
        self.assertEqual(result["overall"]["avg_ac_count"], 0.0)

    def test_aggregate_single(self) -> None:
        m = FeatureMetrics(
            feature_id="a", status="proposed", priority="high", effort="small",
            project="core", ac_count=5, task_count=3, test_count=2,
            coverage_pct=80.0, validation_pass=10, validation_fail=1,
            consistency_fail=0, drift_events=1, lifecycle_duration_days=5.0,
        )
        result = _aggregate_metrics([m], "priority")
        self.assertEqual(result["overall"]["total_features"], 1)
        self.assertEqual(result["overall"]["avg_ac_count"], 5.0)
        self.assertEqual(result["overall"]["avg_coverage"], 80.0)

    def test_aggregate_multiple(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="proposed", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=2,
                coverage_pct=80.0, validation_pass=10, validation_fail=1,
                consistency_fail=0, drift_events=1, lifecycle_duration_days=5.0,
            ),
            FeatureMetrics(
                feature_id="b", status="validated", priority="low", effort="large",
                project="core", ac_count=3, task_count=1, test_count=3,
                coverage_pct=100.0, validation_pass=8, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=10.0,
            ),
        ]
        result = _aggregate_metrics(metrics, "priority")
        self.assertEqual(result["overall"]["total_features"], 2)
        self.assertEqual(result["overall"]["avg_ac_count"], 4.0)
        self.assertAlmostEqual(result["overall"]["avg_coverage"], 90.0)

    def test_aggregate_groups_by_priority(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="proposed", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=2,
                coverage_pct=80.0, validation_pass=10, validation_fail=1,
                consistency_fail=0, drift_events=1, lifecycle_duration_days=5.0,
            ),
            FeatureMetrics(
                feature_id="b", status="validated", priority="low", effort="large",
                project="core", ac_count=3, task_count=1, test_count=3,
                coverage_pct=100.0, validation_pass=8, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=10.0,
            ),
        ]
        result = _aggregate_metrics(metrics, "priority")
        self.assertIn("high", result["groups"])
        self.assertIn("low", result["groups"])
        self.assertEqual(result["groups"]["high"]["count"], 1)

    def test_aggregate_groups_by_status(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="proposed", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=2,
                coverage_pct=80.0, validation_pass=10, validation_fail=1,
                consistency_fail=0, drift_events=1, lifecycle_duration_days=5.0,
            ),
            FeatureMetrics(
                feature_id="b", status="validated", priority="low", effort="large",
                project="core", ac_count=3, task_count=1, test_count=3,
                coverage_pct=100.0, validation_pass=8, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=10.0,
            ),
        ]
        result = _aggregate_metrics(metrics, "status")
        self.assertIn("proposed", result["groups"])
        self.assertIn("validated", result["groups"])

    def test_aggregate_groups_by_project(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="proposed", priority="high", effort="small",
                project="alpha", ac_count=5, task_count=3, test_count=2,
                coverage_pct=80.0, validation_pass=10, validation_fail=1,
                consistency_fail=0, drift_events=1, lifecycle_duration_days=5.0,
            ),
            FeatureMetrics(
                feature_id="b", status="validated", priority="low", effort="large",
                project="beta", ac_count=3, task_count=1, test_count=3,
                coverage_pct=100.0, validation_pass=8, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=10.0,
            ),
        ]
        result = _aggregate_metrics(metrics, "project")
        self.assertIn("alpha", result["groups"])
        self.assertIn("beta", result["groups"])

    def test_aggregate_groups_by_effort(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="proposed", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=2,
                coverage_pct=80.0, validation_pass=10, validation_fail=1,
                consistency_fail=0, drift_events=1, lifecycle_duration_days=5.0,
            ),
            FeatureMetrics(
                feature_id="b", status="validated", priority="low", effort="large",
                project="core", ac_count=3, task_count=1, test_count=3,
                coverage_pct=100.0, validation_pass=8, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=10.0,
            ),
        ]
        result = _aggregate_metrics(metrics, "effort")
        self.assertIn("small", result["groups"])
        self.assertIn("large", result["groups"])

    def test_aggregate_median(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="proposed", priority="high", effort="small",
                project="core", ac_count=2, task_count=3, test_count=2,
                coverage_pct=60.0, validation_pass=10, validation_fail=1,
                consistency_fail=0, drift_events=1, lifecycle_duration_days=5.0,
            ),
            FeatureMetrics(
                feature_id="b", status="validated", priority="low", effort="large",
                project="core", ac_count=8, task_count=1, test_count=3,
                coverage_pct=100.0, validation_pass=8, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=10.0,
            ),
        ]
        result = _aggregate_metrics(metrics, "priority")
        self.assertEqual(result["overall"]["median_ac_count"], 5.0)
        self.assertEqual(result["overall"]["median_coverage"], 80.0)

    def test_aggregate_percentiles(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="proposed", priority="high", effort="small",
                project="core", ac_count=2, task_count=3, test_count=2,
                coverage_pct=60.0, validation_pass=10, validation_fail=1,
                consistency_fail=0, drift_events=1, lifecycle_duration_days=5.0,
            ),
            FeatureMetrics(
                feature_id="b", status="validated", priority="low", effort="large",
                project="core", ac_count=8, task_count=1, test_count=3,
                coverage_pct=100.0, validation_pass=8, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=10.0,
            ),
        ]
        result = _aggregate_metrics(metrics, "priority")
        self.assertGreaterEqual(result["overall"]["p95_coverage"], 90.0)

    def test_aggregate_group_stats(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="proposed", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=2,
                coverage_pct=80.0, validation_pass=10, validation_fail=1,
                consistency_fail=0, drift_events=1, lifecycle_duration_days=5.0,
            ),
            FeatureMetrics(
                feature_id="b", status="proposed", priority="high", effort="small",
                project="core", ac_count=3, task_count=1, test_count=3,
                coverage_pct=60.0, validation_pass=8, validation_fail=0,
                consistency_fail=0, drift_events=2, lifecycle_duration_days=10.0,
            ),
        ]
        result = _aggregate_metrics(metrics, "priority")
        high = result["groups"]["high"]
        self.assertEqual(high["count"], 2)
        self.assertAlmostEqual(high["avg_coverage"], 70.0)
        self.assertIn("a", high["features"])
        self.assertIn("b", high["features"])


class TopPerformersTests(TestCase):
    def test_empty(self) -> None:
        self.assertEqual(_identify_top_performers([]), [])

    def test_single(self) -> None:
        m = FeatureMetrics(
            feature_id="good", status="validated", priority="high", effort="small",
            project="core", ac_count=5, task_count=3, test_count=5,
            coverage_pct=100.0, validation_pass=10, validation_fail=0,
            consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
        )
        top = _identify_top_performers([m])
        self.assertEqual(len(top), 1)
        self.assertEqual(top[0]["feature_id"], "good")
        self.assertGreater(top[0]["score"], 0)

    def test_multiple_sorted(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="bad", status="proposed", priority="low", effort="large",
                project="core", ac_count=1, task_count=1, test_count=0,
                coverage_pct=0.0, validation_pass=0, validation_fail=5,
                consistency_fail=3, drift_events=5, lifecycle_duration_days=20.0,
            ),
            FeatureMetrics(
                feature_id="good", status="validated", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=5,
                coverage_pct=100.0, validation_pass=10, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            ),
        ]
        top = _identify_top_performers(metrics)
        self.assertEqual(top[0]["feature_id"], "good")

    def test_top_five_limit(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id=f"feat-{i}", status="proposed", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=5,
                coverage_pct=100.0 - i * 5, validation_pass=10, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            )
            for i in range(10)
        ]
        top = _identify_top_performers(metrics)
        self.assertLessEqual(len(top), 5)


class ImprovementAreasTests(TestCase):
    def test_empty(self) -> None:
        self.assertEqual(_identify_improvement_areas([]), [])

    def test_single(self) -> None:
        m = FeatureMetrics(
            feature_id="needs-work", status="proposed", priority="low", effort="large",
            project="core", ac_count=5, task_count=1, test_count=0,
            coverage_pct=0.0, validation_pass=0, validation_fail=5,
            consistency_fail=2, drift_events=3, lifecycle_duration_days=15.0,
        )
        areas = _identify_improvement_areas([m])
        self.assertEqual(len(areas), 1)
        self.assertEqual(areas[0]["feature_id"], "needs-work")
        self.assertIn("primary_issue", areas[0])

    def test_primary_issue_low_coverage(self) -> None:
        m = FeatureMetrics(
            feature_id="low-cov", status="proposed", priority="medium", effort="small",
            project="core", ac_count=5, task_count=1, test_count=1,
            coverage_pct=20.0, validation_pass=5, validation_fail=0,
            consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
        )
        areas = _identify_improvement_areas([m])
        self.assertEqual(areas[0]["primary_issue"], "low_coverage")

    def test_primary_issue_high_drift(self) -> None:
        m = FeatureMetrics(
            feature_id="drifty", status="proposed", priority="medium", effort="small",
            project="core", ac_count=5, task_count=1, test_count=5,
            coverage_pct=80.0, validation_pass=5, validation_fail=0,
            consistency_fail=0, drift_events=5, lifecycle_duration_days=5.0,
        )
        areas = _identify_improvement_areas([m])
        self.assertEqual(areas[0]["primary_issue"], "high_drift")

    def test_primary_issue_consistency_failures(self) -> None:
        m = FeatureMetrics(
            feature_id="inconsistent", status="proposed", priority="medium", effort="small",
            project="core", ac_count=5, task_count=1, test_count=5,
            coverage_pct=80.0, validation_pass=5, validation_fail=0,
            consistency_fail=2, drift_events=0, lifecycle_duration_days=5.0,
        )
        areas = _identify_improvement_areas([m])
        self.assertEqual(areas[0]["primary_issue"], "consistency_failures")

    def test_primary_issue_no_test_links(self) -> None:
        m = FeatureMetrics(
            feature_id="no-tests", status="proposed", priority="medium", effort="small",
            project="core", ac_count=5, task_count=1, test_count=0,
            coverage_pct=0.0, validation_pass=5, validation_fail=0,
            consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
        )
        areas = _identify_improvement_areas([m])
        self.assertEqual(areas[0]["primary_issue"], "low_coverage")

    def test_multiple_sorted_by_score(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="good", status="validated", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=5,
                coverage_pct=100.0, validation_pass=10, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            ),
            FeatureMetrics(
                feature_id="bad", status="proposed", priority="low", effort="large",
                project="core", ac_count=1, task_count=1, test_count=0,
                coverage_pct=0.0, validation_pass=0, validation_fail=5,
                consistency_fail=3, drift_events=5, lifecycle_duration_days=20.0,
            ),
        ]
        areas = _identify_improvement_areas(metrics)
        self.assertEqual(areas[0]["feature_id"], "bad")

    def test_improvement_five_limit(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id=f"feat-{i}", status="proposed", priority="low", effort="large",
                project="core", ac_count=1, task_count=1, test_count=0,
                coverage_pct=float(i * 5), validation_pass=0, validation_fail=5,
                consistency_fail=3, drift_events=5, lifecycle_duration_days=20.0,
            )
            for i in range(10)
        ]
        areas = _identify_improvement_areas(metrics)
        self.assertLessEqual(len(areas), 5)


class TrendsTests(TestCase):
    def test_empty(self) -> None:
        trends = _compute_trends([])
        self.assertEqual(trends["coverage_trend"], "stable")
        self.assertEqual(trends["validation_pass_rate_trend"], "stable")
        self.assertEqual(trends["drift_frequency_trend"], "stable")

    def test_healthy_coverage(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="validated", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=5,
                coverage_pct=90.0, validation_pass=10, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            ),
        ]
        trends = _compute_trends(metrics)
        self.assertEqual(trends["coverage_trend"], "healthy")

    def test_declining_coverage(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="proposed", priority="low", effort="large",
                project="core", ac_count=5, task_count=1, test_count=0,
                coverage_pct=10.0, validation_pass=0, validation_fail=5,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            ),
        ]
        trends = _compute_trends(metrics)
        self.assertEqual(trends["coverage_trend"], "declining")

    def test_coverage_by_status(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="validated", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=5,
                coverage_pct=100.0, validation_pass=10, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            ),
            FeatureMetrics(
                feature_id="b", status="proposed", priority="low", effort="large",
                project="core", ac_count=3, task_count=1, test_count=1,
                coverage_pct=50.0, validation_pass=5, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=10.0,
            ),
        ]
        trends = _compute_trends(metrics)
        self.assertIn("validated", trends["coverage_by_status"])
        self.assertIn("proposed", trends["coverage_by_status"])
        self.assertEqual(trends["coverage_by_status"]["validated"], 100.0)

    def test_drift_by_priority(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="proposed", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=5,
                coverage_pct=80.0, validation_pass=10, validation_fail=0,
                consistency_fail=0, drift_events=3, lifecycle_duration_days=5.0,
            ),
            FeatureMetrics(
                feature_id="b", status="validated", priority="low", effort="large",
                project="core", ac_count=3, task_count=1, test_count=3,
                coverage_pct=100.0, validation_pass=8, validation_fail=0,
                consistency_fail=0, drift_events=1, lifecycle_duration_days=10.0,
            ),
        ]
        trends = _compute_trends(metrics)
        self.assertIn("high", trends["drift_by_priority"])
        self.assertIn("low", trends["drift_by_priority"])

    def test_drift_increasing(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id=f"feat-{i}", status="proposed", priority="low", effort="large",
                project="core", ac_count=1, task_count=1, test_count=0,
                coverage_pct=0.0, validation_pass=0, validation_fail=5,
                consistency_fail=0, drift_events=10, lifecycle_duration_days=20.0,
            )
            for i in range(5)
        ]
        trends = _compute_trends(metrics)
        self.assertEqual(trends["drift_frequency_trend"], "increasing")

    def test_drift_improving(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id=f"feat-{i}", status="validated", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=5,
                coverage_pct=100.0, validation_pass=10, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            )
            for i in range(5)
        ]
        trends = _compute_trends(metrics)
        self.assertEqual(trends["drift_frequency_trend"], "improving")

    def test_validation_healthy(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="validated", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=5,
                coverage_pct=90.0, validation_pass=90, validation_fail=5,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            ),
        ]
        trends = _compute_trends(metrics)
        self.assertEqual(trends["validation_pass_rate_trend"], "healthy")

    def test_validation_declining(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="proposed", priority="low", effort="large",
                project="core", ac_count=1, task_count=1, test_count=0,
                coverage_pct=10.0, validation_pass=2, validation_fail=8,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            ),
        ]
        trends = _compute_trends(metrics)
        self.assertEqual(trends["validation_pass_rate_trend"], "declining")


class RecommendationsTests(TestCase):
    def test_no_recommendations_healthy(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="a", status="validated", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=5,
                coverage_pct=90.0, validation_pass=10, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            ),
        ]
        recs = _generate_recommendations(
            metrics,
            {"overall": {"avg_coverage": 90.0, "avg_drift_events": 0.0}},
            [],
            [],
            {"coverage_trend": "healthy"},
        )
        self.assertEqual(len(recs), 1)
        self.assertIn("No critical", recs[0])

    def test_low_coverage_recommendation(self) -> None:
        metrics = []
        recs = _generate_recommendations(
            metrics,
            {"overall": {"avg_coverage": 30.0, "avg_drift_events": 0.0}},
            [],
            [],
            {"coverage_trend": "stable"},
        )
        self.assertTrue(any("coverage" in r.lower() for r in recs))

    def test_high_drift_recommendation(self) -> None:
        recs = _generate_recommendations(
            [],
            {"overall": {"avg_coverage": 80.0, "avg_drift_events": 5.0}},
            [],
            [],
            {"coverage_trend": "stable"},
        )
        self.assertTrue(any("drift" in r.lower() for r in recs))

    def test_low_coverage_features_recommendation(self) -> None:
        recs = _generate_recommendations(
            [],
            {"overall": {"avg_coverage": 40.0, "avg_drift_events": 0.0}},
            [],
            [{"feature_id": "bad", "coverage_pct": 10.0}],
            {"coverage_trend": "stable"},
        )
        self.assertTrue(any("30" in r for r in recs))

    def test_declining_trend_recommendation(self) -> None:
        recs = _generate_recommendations(
            [],
            {"overall": {"avg_coverage": 60.0, "avg_drift_events": 0.0}},
            [],
            [],
            {"coverage_trend": "declining"},
        )
        self.assertTrue(any("declining" in r.lower() for r in recs))

    def test_max_five_recommendations(self) -> None:
        recs = _generate_recommendations(
            [],
            {"overall": {"avg_coverage": 10.0, "avg_drift_events": 10.0}},
            [{"feature_id": f"bad-{i}", "coverage_pct": 5.0} for i in range(10)],
            [],
            {"coverage_trend": "declining"},
        )
        self.assertLessEqual(len(recs), 5)


class BuildBenchmarkReportTests(TestCase):
    def test_empty_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_benchmark_report(root)
            self.assertEqual(report.feature_count, 0)
            self.assertEqual(len(report.metrics), 0)

    def test_single_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "single", ac_ids=["AC001", "AC002"])
            report = build_benchmark_report(root)
            self.assertEqual(report.feature_count, 1)
            self.assertEqual(report.metrics[0].feature_id, "single")

    def test_multiple_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "alpha", priority="high")
            _create_feature(root, "beta", priority="low")
            _create_feature(root, "gamma", priority="medium")
            report = build_benchmark_report(root)
            self.assertEqual(report.feature_count, 3)

    def test_feature_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "alpha")
            _create_feature(root, "beta")
            report = build_benchmark_report(root, feature_filter="alpha")
            self.assertEqual(report.feature_count, 1)
            self.assertEqual(report.metrics[0].feature_id, "alpha")

    def test_feature_filter_invalid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "alpha")
            report = build_benchmark_report(root, feature_filter="nonexistent")
            self.assertEqual(report.feature_count, 0)

    def test_group_by_priority(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "a", priority="high")
            _create_feature(root, "b", priority="low")
            report = build_benchmark_report(root, group_by="priority")
            self.assertIn("high", report.aggregates["groups"])
            self.assertIn("low", report.aggregates["groups"])

    def test_group_by_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "a", status="proposed")
            _create_feature(root, "b", status="validated")
            report = build_benchmark_report(root, group_by="status")
            self.assertIn("proposed", report.aggregates["groups"])

    def test_group_by_project(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "a", project="alpha")
            _create_feature(root, "b", project="beta")
            report = build_benchmark_report(root, group_by="project")
            self.assertIn("alpha", report.aggregates["groups"])

    def test_group_by_effort(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "a", effort="small")
            _create_feature(root, "b", effort="large")
            report = build_benchmark_report(root, group_by="effort")
            self.assertIn("small", report.aggregates["groups"])

    def test_invalid_group_by_defaults_to_priority(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "a", priority="high")
            report = build_benchmark_report(root, group_by="invalid")
            self.assertIn("high", report.aggregates["groups"])

    def test_report_has_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_benchmark_report(root)
            self.assertGreater(len(report.safety_notes), 0)

    def test_report_root_is_absolute(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_benchmark_report(root)
            self.assertTrue(report.root.startswith("/"))


class RenderTests(TestCase):
    def test_json_rendering(self) -> None:
        report = BenchmarkReport(
            root="/tmp",
            feature_count=0,
            metrics=(),
            aggregates={"overall": {}, "groups": {}},
            top_performers=(),
            improvement_areas=(),
            trends={},
            recommendations=(),
            safety_notes=SAFETY_NOTES if "SAFETY_NOTES" in dir() else ("test",),
        )
        json_str = render_benchmark_json(report)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["feature_count"], 0)

    def test_json_sorted_keys(self) -> None:
        report = BenchmarkReport(
            root="/tmp",
            feature_count=1,
            metrics=(),
            aggregates={"overall": {}, "groups": {}},
            top_performers=(),
            improvement_areas=(),
            trends={},
            recommendations=(),
            safety_notes=("test",),
        )
        json_str = render_benchmark_json(report)
        keys = list(json.loads(json_str).keys())
        self.assertEqual(keys, sorted(keys))

    def test_text_rendering(self) -> None:
        report = BenchmarkReport(
            root="/tmp",
            feature_count=0,
            metrics=(),
            aggregates={"overall": {}, "groups": {}},
            top_performers=(),
            improvement_areas=(),
            trends={},
            recommendations=(),
            safety_notes=("test",),
        )
        text = render_benchmark_text(report)
        self.assertIn("Benchmark Report", text)
        self.assertIn("Features Analyzed: 0", text)

    def test_text_with_data(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="feat", status="proposed", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=5,
                coverage_pct=100.0, validation_pass=10, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            ),
        ]
        report = BenchmarkReport(
            root="/tmp",
            feature_count=1,
            metrics=tuple(metrics),
            aggregates={"overall": {"avg_ac_count": 5.0, "avg_coverage": 100.0}, "groups": {}},
            top_performers=({"feature_id": "feat", "score": 100.0, "coverage_pct": 100.0, "drift_events": 0, "consistency_fail": 0},),
            improvement_areas=(),
            trends={"coverage_trend": "healthy"},
            recommendations=("Good job",),
            safety_notes=("test",),
        )
        text = render_benchmark_text(report)
        self.assertIn("feat", text)
        self.assertIn("Good job", text)

    def test_text_with_groups(self) -> None:
        report = BenchmarkReport(
            root="/tmp",
            feature_count=1,
            metrics=(),
            aggregates={
                "overall": {},
                "groups": {
                    "high": {
                        "count": 1,
                        "avg_coverage": 80.0,
                        "avg_ac_count": 5.0,
                        "avg_drift_events": 0.0,
                        "features": ["a"],
                    },
                },
            },
            top_performers=(),
            improvement_areas=(),
            trends={},
            recommendations=(),
            safety_notes=("test",),
        )
        text = render_benchmark_text(report)
        self.assertIn("high", text)

    def test_text_with_trends(self) -> None:
        report = BenchmarkReport(
            root="/tmp",
            feature_count=1,
            metrics=(),
            aggregates={"overall": {}, "groups": {}},
            top_performers=(),
            improvement_areas=(),
            trends={
                "coverage_trend": "healthy",
                "validation_pass_rate_trend": "stable",
                "drift_frequency_trend": "improving",
                "coverage_by_status": {"validated": 90.0},
            },
            recommendations=(),
            safety_notes=("test",),
        )
        text = render_benchmark_text(report)
        self.assertIn("healthy", text)
        self.assertIn("validated", text)

    def test_text_with_improvement_areas(self) -> None:
        report = BenchmarkReport(
            root="/tmp",
            feature_count=1,
            metrics=(),
            aggregates={"overall": {}, "groups": {}},
            top_performers=(),
            improvement_areas=({"feature_id": "bad", "score": 50.0, "coverage_pct": 10.0, "drift_events": 0, "consistency_fail": 0, "primary_issue": "low_coverage"},),
            trends={},
            recommendations=(),
            safety_notes=("test",),
        )
        text = render_benchmark_text(report)
        self.assertIn("Improvement Areas", text)
        self.assertIn("bad", text)

    def test_json_roundtrip(self) -> None:
        metrics = [
            FeatureMetrics(
                feature_id="feat", status="proposed", priority="high", effort="small",
                project="core", ac_count=5, task_count=3, test_count=5,
                coverage_pct=100.0, validation_pass=10, validation_fail=0,
                consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
            ),
        ]
        report = BenchmarkReport(
            root="/tmp",
            feature_count=1,
            metrics=tuple(metrics),
            aggregates={"overall": {"avg_ac_count": 5.0}, "groups": {}},
            top_performers=(),
            improvement_areas=(),
            trends={},
            recommendations=(),
            safety_notes=("test",),
        )
        json_str = render_benchmark_json(report)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["feature_count"], 1)
        self.assertEqual(parsed["metrics"][0]["feature_id"], "feat")


class HelperTests(TestCase):
    def test_median_odd(self) -> None:
        self.assertEqual(_median([1.0, 3.0, 5.0]), 3.0)

    def test_median_even(self) -> None:
        self.assertEqual(_median([1.0, 2.0, 3.0, 4.0]), 2.5)

    def test_median_single(self) -> None:
        self.assertEqual(_median([42.0]), 42.0)

    def test_median_empty(self) -> None:
        self.assertEqual(_median([]), 0.0)

    def test_percentile_p50(self) -> None:
        self.assertAlmostEqual(_percentile([1.0, 2.0, 3.0, 4.0, 5.0], 50), 3.0)

    def test_percentile_p95(self) -> None:
        result = _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 95)
        self.assertGreaterEqual(result, 4.0)

    def test_percentile_empty(self) -> None:
        self.assertEqual(_percentile([], 50), 0.0)

    def test_percentile_single(self) -> None:
        self.assertEqual(_percentile([10.0], 50), 10.0)

    def test_primary_issue_needs_review(self) -> None:
        m = FeatureMetrics(
            feature_id="ok", status="validated", priority="high", effort="small",
            project="core", ac_count=5, task_count=3, test_count=5,
            coverage_pct=80.0, validation_pass=10, validation_fail=0,
            consistency_fail=0, drift_events=0, lifecycle_duration_days=5.0,
        )
        self.assertEqual(_primary_issue(m), "needs_review")


class ValidGroupByTests(TestCase):
    def test_valid_group_by_values(self) -> None:
        self.assertIn("priority", VALID_GROUP_BY)
        self.assertIn("status", VALID_GROUP_BY)
        self.assertIn("project", VALID_GROUP_BY)
        self.assertIn("effort", VALID_GROUP_BY)
        self.assertEqual(len(VALID_GROUP_BY), 4)


class CliTests(TestCase):
    def test_benchmark_help(self) -> None:
        out = StringIO()
        with redirect_stdout(out):
            try:
                main(["benchmark", "--help"])
            except SystemExit:
                pass
        output = out.getvalue()
        self.assertIn("benchmark", output.lower())

    def test_benchmark_json_empty_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            out = StringIO()
            with redirect_stdout(out):
                rc = main(["benchmark", tmp, "--json"])
            output = out.getvalue()
            self.assertEqual(rc, 0)
            parsed = json.loads(output)
            self.assertEqual(parsed["feature_count"], 0)

    def test_benchmark_json_with_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "test", ac_ids=["AC001"])
            out = StringIO()
            with redirect_stdout(out):
                rc = main(["benchmark", tmp, "--json", "--feature", "test"])
            output = out.getvalue()
            self.assertEqual(rc, 0)
            parsed = json.loads(output)
            self.assertEqual(parsed["feature_count"], 1)

    def test_benchmark_text(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "test")
            out = StringIO()
            with redirect_stdout(out):
                rc = main(["benchmark", tmp])
            output = out.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn("Benchmark Report", output)

    def test_benchmark_group_by(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "a", priority="high")
            _create_feature(root, "b", priority="low")
            out = StringIO()
            with redirect_stdout(out):
                rc = main(["benchmark", tmp, "--json", "--group-by", "priority"])
            output = out.getvalue()
            self.assertEqual(rc, 0)
            parsed = json.loads(output)
            self.assertIn("high", parsed["aggregates"]["groups"])

    def test_benchmark_invalid_feature_slug(self) -> None:
        out = StringIO()
        err = StringIO()
        import sys
        old_err = sys.stderr
        sys.stderr = err
        try:
            with redirect_stdout(out):
                rc = main(["benchmark", ".", "--feature", "INVALID SLUG"])
        finally:
            sys.stderr = old_err
        self.assertEqual(rc, 2)

    def test_benchmark_output_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "test")
            output_path = root / "benchmark.txt"
            out = StringIO()
            with redirect_stdout(out):
                rc = main(["benchmark", tmp, "--output", str(output_path)])
            output = out.getvalue()
            self.assertEqual(rc, 0)
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("Benchmark Report", content)

    def test_benchmark_feature_not_found(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            out = StringIO()
            with redirect_stdout(out):
                rc = main(["benchmark", tmp, "--json", "--feature", "nonexistent"])
            output = out.getvalue()
            self.assertEqual(rc, 0)
            parsed = json.loads(output)
            self.assertEqual(parsed["feature_count"], 0)

    def test_benchmark_group_by_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "a", status="proposed")
            _create_feature(root, "b", status="validated")
            out = StringIO()
            with redirect_stdout(out):
                rc = main(["benchmark", tmp, "--json", "--group-by", "status"])
            output = out.getvalue()
            self.assertEqual(rc, 0)
            parsed = json.loads(output)
            self.assertIn("proposed", parsed["aggregates"]["groups"])

    def test_benchmark_group_by_project(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "a", project="alpha")
            out = StringIO()
            with redirect_stdout(out):
                rc = main(["benchmark", tmp, "--json", "--group-by", "project"])
            output = out.getvalue()
            self.assertEqual(rc, 0)
            parsed = json.loads(output)
            self.assertIn("alpha", parsed["aggregates"]["groups"])

    def test_benchmark_group_by_effort(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _create_feature(root, "a", effort="small")
            out = StringIO()
            with redirect_stdout(out):
                rc = main(["benchmark", tmp, "--json", "--group-by", "effort"])
            output = out.getvalue()
            self.assertEqual(rc, 0)
            parsed = json.loads(output)
            self.assertIn("small", parsed["aggregates"]["groups"])

    def test_no_subprocess_imports(self) -> None:
        import specspine.benchmark as benchmark_mod
        source = Path(benchmark_mod.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import subprocess", source)
        self.assertNotIn("subprocess.", source)

    def test_no_network_imports(self) -> None:
        import specspine.benchmark as benchmark_mod
        source = Path(benchmark_mod.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import urllib", source)
        self.assertNotIn("import requests", source)
        self.assertNotIn("import http", source)

    def test_no_token_reads(self) -> None:
        import specspine.benchmark as benchmark_mod
        source = Path(benchmark_mod.__file__).read_text(encoding="utf-8")
        self.assertNotIn("os.environ", source)
        self.assertNotIn("os.getenv", source)
        self.assertNotIn("environ[", source)
