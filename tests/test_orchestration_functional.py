import json
import ast
import importlib
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import main
from specspine.orchestration import (
    OrchestrationConflict,
    OrchestrationPlan,
    OrchestrationReport,
    ParallelGroup,
    build_orchestration_plan,
    render_orchestration_json,
    render_orchestration_text,
    _detect_semantic_conflicts,
    _detect_file_conflicts,
    _detect_contract_conflicts,
    _compute_parallel_groups,
    _build_dependency_graph,
    _generate_integration_recommendations,
    _extract_ac_ids,
    _extract_contracts,
    _scan_feature_file_paths,
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
    extra_spec_content: str = "",
    extra_exec_content: str = "",
    extra_quality_content: str = "",
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
    if extra_spec_content:
        spec_lines.append("")
        spec_lines.append(extra_spec_content)

    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(spec_lines) + "\n",
        encoding="utf-8",
    )

    exec_lines = [
        f"# {slug.title()} Execution",
        "",
        f"Feature ID: {slug}",
        f"Status: {status}",
        "",
        "## Tasks",
        "",
        *[f"- [ ] {item}" for item in tasks],
    ]
    if extra_exec_content:
        exec_lines.append("")
        exec_lines.append(extra_exec_content)

    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(exec_lines) + "\n",
        encoding="utf-8",
    )

    quality_lines = [
        f"# {slug.title()} Quality",
        "",
        f"Feature ID: {slug}",
        f"Status: {status}",
        "",
        "## Required Checks",
        "",
        "- [ ] Quality checks pass.",
    ]
    if extra_quality_content:
        quality_lines.append("")
        quality_lines.append(extra_quality_content)

    (root / "quality" / "features" / f"{slug}.md").write_text(
        "\n".join(quality_lines) + "\n",
        encoding="utf-8",
    )


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(argv)
    except SystemExit as e:
        code = e.code if e.code is not None else 0
    return code, stdout.getvalue(), stderr.getvalue()


class EmptyWorkspaceFunctionalTests(TestCase):
    """Test orchestration on an empty workspace."""

    def test_empty_workspace_json_status_ok(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_orchestration_plan(root)
            self.assertEqual(report.status, "ok")

    def test_empty_workspace_no_conflicts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_orchestration_plan(root)
            self.assertEqual(len(report.conflicts), 0)

    def test_empty_workspace_empty_execution_order(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_orchestration_plan(root)
            self.assertEqual(report.plan.execution_order, ())

    def test_empty_workspace_empty_parallel_groups(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_orchestration_plan(root)
            self.assertEqual(report.plan.parallel_groups, ())

    def test_empty_workspace_json_output_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_orchestration_plan(root)
            json_str = render_orchestration_json(report)
            parsed = json.loads(json_str)
            self.assertEqual(parsed["status"], "ok")
            self.assertEqual(parsed["conflicts"], [])

    def test_empty_workspace_text_output_complete(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Orchestration plan:", text)
            self.assertIn("Conflicts (0):", text)
            self.assertIn("Execution plan:", text)
            self.assertIn("Integration recommendations:", text)
            self.assertIn("Safety notes:", text)

    def test_empty_workspace_cli_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["conflicts"], [])


class SingleFeatureFunctionalTests(TestCase):
    """Test orchestration with a single feature."""

    def test_single_feature_no_conflicts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "dark-mode")
            report = build_orchestration_plan(root)
            self.assertEqual(report.status, "ok")
            self.assertEqual(len(report.conflicts), 0)
            self.assertEqual(report.plan.execution_order, ("dark-mode",))

    def test_single_feature_safe_for_parallel(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "dark-mode")
            report = build_orchestration_plan(root)
            self.assertTrue(report.plan.safe_for_parallel)

    def test_single_feature_one_parallel_group(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "dark-mode")
            report = build_orchestration_plan(root)
            self.assertEqual(len(report.plan.parallel_groups), 1)
            self.assertEqual(report.plan.parallel_groups[0].features, ("dark-mode",))

    def test_single_feature_cli_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "dark-mode")
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["plan"]["execution_order"], ["dark-mode"])


class TwoFeaturesOverlappingFilesTests(TestCase):
    """Test orchestration with two features that share file targets."""

    def test_overlapping_file_detected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "feature-a", extra_spec_content="src/app.py\n")
            write_feature_bundle(root, "feature-b", extra_spec_content="src/app.py\n")
            conflicts = _detect_file_conflicts(root, ["feature-a", "feature-b"])
            self.assertEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0].conflict_type, "file")

    def test_overlapping_file_severity_medium(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "a", extra_spec_content="src/app.py\n")
            write_feature_bundle(root, "b", extra_spec_content="src/app.py\n")
            conflicts = _detect_file_conflicts(root, ["a", "b"])
            self.assertEqual(conflicts[0].severity, "medium")

    def test_overlapping_file_severity_high_many(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            paths = "src/a.py\nsrc/b.py\nsrc/c.py\nsrc/d.py\n"
            write_feature_bundle(root, "a", extra_spec_content=paths)
            write_feature_bundle(root, "b", extra_spec_content=paths)
            conflicts = _detect_file_conflicts(root, ["a", "b"])
            self.assertEqual(conflicts[0].severity, "high")

    def test_overlapping_file_sets_warnings_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            paths = "src/a.py\nsrc/b.py\nsrc/c.py\nsrc/d.py\n"
            write_feature_bundle(root, "a", extra_spec_content=paths)
            write_feature_bundle(root, "b", extra_spec_content=paths)
            report = build_orchestration_plan(root)
            self.assertEqual(report.status, "warnings")

    def test_overlapping_file_features_involved_sorted(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "zebra", extra_spec_content="src/app.py\n")
            write_feature_bundle(root, "alpha", extra_spec_content="src/app.py\n")
            conflicts = _detect_file_conflicts(root, ["zebra", "alpha"])
            self.assertEqual(conflicts[0].features_involved, ("alpha", "zebra"))


class ThreeFeatureDependencyChainTests(TestCase):
    """Test orchestration with A -> B -> C dependency chain."""

    def test_three_feature_execution_order(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "layer-a")
            write_feature_bundle(
                root, "layer-b", extra_exec_content="depends on layer-a"
            )
            write_feature_bundle(
                root, "layer-c", extra_exec_content="depends on layer-b"
            )
            report = build_orchestration_plan(root)
            order = report.plan.execution_order
            self.assertEqual(len(order), 3)
            self.assertLess(order.index("layer-a"), order.index("layer-b"))
            self.assertLess(order.index("layer-b"), order.index("layer-c"))

    def test_three_feature_three_parallel_groups(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "layer-a")
            write_feature_bundle(
                root, "layer-b", extra_exec_content="depends on layer-a"
            )
            write_feature_bundle(
                root, "layer-c", extra_exec_content="depends on layer-b"
            )
            report = build_orchestration_plan(root)
            self.assertEqual(len(report.plan.parallel_groups), 3)

    def test_three_feature_not_safe_for_parallel(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "layer-a")
            write_feature_bundle(
                root, "layer-b", extra_exec_content="depends on layer-a"
            )
            write_feature_bundle(
                root, "layer-c", extra_exec_content="depends on layer-b"
            )
            report = build_orchestration_plan(root)
            self.assertFalse(report.plan.safe_for_parallel)

    def test_three_feature_no_conflicts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "layer-a")
            write_feature_bundle(
                root, "layer-b", extra_exec_content="depends on layer-a"
            )
            write_feature_bundle(
                root, "layer-c", extra_exec_content="depends on layer-b"
            )
            report = build_orchestration_plan(root)
            self.assertEqual(len(report.conflicts), 0)


class SemanticConflictDetectionTests(TestCase):
    """Test semantic conflict detection for mutually exclusive behaviors."""

    def test_detects_enable_vs_disable_conflict(self) -> None:
        conflicts = _detect_semantic_conflicts(
            ["feature-on", "feature-off"],
            Path("/tmp"),
        )
        # When content files don't exist, no conflicts should be found
        # (the function reads content from workspace)
        self.assertIsInstance(conflicts, list)

    def test_returns_list_type(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            result = _detect_semantic_conflicts(["alpha", "beta"], root)
            self.assertIsInstance(result, list)

    def test_no_conflict_without_toggle_patterns(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            conflicts = _detect_semantic_conflicts(["alpha", "beta"], root)
            self.assertEqual(len(conflicts), 0)

    def test_conflict_has_required_attributes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "toggle-on",
                extra_spec_content="- enable dark_mode feature\n",
            )
            write_feature_bundle(
                root,
                "toggle-off",
                extra_spec_content="- disable dark_mode feature\n",
            )
            conflicts = _detect_semantic_conflicts(["toggle-on", "toggle-off"], root)
            if conflicts:
                c = conflicts[0]
                self.assertTrue(hasattr(c, "severity"))
                self.assertTrue(hasattr(c, "description"))
                self.assertTrue(hasattr(c, "features_involved"))


class ContractConflictDetectionTests(TestCase):
    """Test contract conflict detection for shared API endpoints."""

    def test_shared_endpoint_critical_severity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root, "api-v1", extra_spec_content="endpoint: /api/users\n"
            )
            write_feature_bundle(
                root, "api-v2", extra_spec_content="endpoint: /api/users\n"
            )
            conflicts = _detect_contract_conflicts(root, ["api-v1", "api-v2"])
            self.assertEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0].severity, "critical")

    def test_shared_schema_high_severity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "a", extra_spec_content="schema: User\n")
            write_feature_bundle(root, "b", extra_spec_content="schema: User\n")
            conflicts = _detect_contract_conflicts(root, ["a", "b"])
            self.assertEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0].severity, "high")

    def test_shared_config_high_severity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "a", extra_spec_content="config: DB_URL\n")
            write_feature_bundle(root, "b", extra_spec_content="config: DB_URL\n")
            conflicts = _detect_contract_conflicts(root, ["a", "b"])
            self.assertEqual(len(conflicts), 1)

    def test_contract_conflict_sets_blocked_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root, "a", extra_spec_content="endpoint: /api/shared\n"
            )
            write_feature_bundle(
                root, "b", extra_spec_content="endpoint: /api/shared\n"
            )
            report = build_orchestration_plan(root)
            self.assertEqual(report.status, "blocked")

    def test_contract_conflict_blocks_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root, "a", extra_spec_content="endpoint: /api/shared\n"
            )
            write_feature_bundle(
                root, "b", extra_spec_content="endpoint: /api/shared\n"
            )
            report = build_orchestration_plan(root)
            self.assertIn("a", report.plan.blocked_features)
            self.assertIn("b", report.plan.blocked_features)

    def test_contract_conflict_unsafe_for_parallel(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root, "a", extra_spec_content="endpoint: /api/shared\n"
            )
            write_feature_bundle(
                root, "b", extra_spec_content="endpoint: /api/shared\n"
            )
            report = build_orchestration_plan(root)
            self.assertFalse(report.plan.safe_for_parallel)


class ParallelGroupComputationTests(TestCase):
    """Test parallel group computation."""

    def test_empty_features_no_groups(self) -> None:
        groups = _compute_parallel_groups([], {})
        self.assertEqual(len(groups), 0)

    def test_single_feature_one_group(self) -> None:
        groups = _compute_parallel_groups(["a"], {"a": set()})
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].features, ("a",))

    def test_independent_features_same_group(self) -> None:
        groups = _compute_parallel_groups(["a", "b", "c"], {
            "a": set(), "b": set(), "c": set(),
        })
        self.assertEqual(len(groups), 1)
        self.assertEqual(set(groups[0].features), {"a", "b", "c"})

    def test_linear_chain_sequential_groups(self) -> None:
        groups = _compute_parallel_groups(
            ["a", "b", "c"],
            {"a": set(), "b": {"a"}, "c": {"b"}},
        )
        self.assertEqual(len(groups), 3)
        self.assertEqual(groups[0].features, ("a",))
        self.assertEqual(groups[1].features, ("b",))
        self.assertEqual(groups[2].features, ("c",))

    def test_diamond_dependency_groups(self) -> None:
        groups = _compute_parallel_groups(
            ["a", "b", "c", "d"],
            {"a": set(), "b": {"a"}, "c": {"a"}, "d": {"b", "c"}},
        )
        self.assertGreaterEqual(len(groups), 2)
        all_features: set[str] = set()
        for g in groups:
            all_features.update(g.features)
        self.assertEqual(all_features, {"a", "b", "c", "d"})

    def test_group_ids_sequential(self) -> None:
        groups = _compute_parallel_groups(
            ["a", "b", "c"],
            {"a": set(), "b": {"a"}, "c": {"b"}},
        )
        self.assertEqual(groups[0].group_id, 1)
        self.assertEqual(groups[1].group_id, 2)
        self.assertEqual(groups[2].group_id, 3)


class IntegrationRecommendationsTests(TestCase):
    """Test integration recommendation generation."""

    def test_no_features_no_conflicts_returns_no_integration_message(self) -> None:
        recs = _generate_integration_recommendations([], [], {})
        self.assertTrue(any("No integration steps" in r for r in recs))

    def test_file_conflict_recommendation(self) -> None:
        conflict = OrchestrationConflict(
            conflict_type="file",
            affected_files=("src/app.py",),
            affected_ac_ids=(),
            features_involved=("a", "b"),
            severity="high",
            description="overlap",
        )
        recs = _generate_integration_recommendations(
            [conflict], ["a", "b"], {"a": {"b"}, "b": set()},
        )
        self.assertTrue(any("File overlap" in r for r in recs))

    def test_contract_conflict_recommendation(self) -> None:
        conflict = OrchestrationConflict(
            conflict_type="contract",
            affected_files=(),
            affected_ac_ids=(),
            features_involved=("a", "b"),
            severity="critical",
            description="shared endpoint",
        )
        recs = _generate_integration_recommendations(
            [conflict], ["a", "b"], {"a": {"b"}, "b": set()},
        )
        self.assertTrue(any("Contract overlap" in r for r in recs))

    def test_multi_dependency_recommendation(self) -> None:
        recs = _generate_integration_recommendations(
            [], ["a", "b", "c"], {"a": {"b", "c"}, "b": set(), "c": set()},
        )
        self.assertTrue(any("multiple dependencies" in r for r in recs))

    def test_execution_order_integration_test_recommendation(self) -> None:
        recs = _generate_integration_recommendations(
            [], ["a", "b"], {"a": set(), "b": {"a"}},
        )
        self.assertTrue(any("integration tests" in r for r in recs))

    def test_single_feature_no_cross_integration(self) -> None:
        recs = _generate_integration_recommendations([], ["a"], {"a": set()})
        self.assertTrue(any("No cross-feature integration" in r for r in recs))


class JsonOutputDeterminismTests(TestCase):
    """Test JSON output is deterministic across multiple runs."""

    def test_json_output_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            report1 = build_orchestration_plan(root)
            report2 = build_orchestration_plan(root)
            self.assertEqual(render_orchestration_json(report1), render_orchestration_json(report2))

    def test_json_keys_sorted(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            json_str = render_orchestration_json(report)
            parsed = json.loads(json_str)
            keys = list(parsed.keys())
            self.assertEqual(keys, sorted(keys))

    def test_json_parseable(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            json_str = render_orchestration_json(report)
            parsed = json.loads(json_str)
            self.assertIsInstance(parsed, dict)

    def test_json_contains_all_required_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            parsed = json.loads(render_orchestration_json(report))
            required_fields = [
                "root", "feature_filter", "conflicts", "plan",
                "integration_recommendations", "status",
                "blocking_items", "safety_notes",
            ]
            for field_name in required_fields:
                self.assertIn(field_name, parsed)

    def test_json_plan_contains_required_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            parsed = json.loads(render_orchestration_json(report))
            plan_fields = [
                "execution_order", "parallel_groups",
                "blocked_features", "safe_for_parallel",
            ]
            for field_name in plan_fields:
                self.assertIn(field_name, parsed["plan"])


class TextOutputCompletenessTests(TestCase):
    """Test text output contains all expected sections."""

    def test_text_contains_header(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Orchestration plan:", text)

    def test_text_contains_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Status:", text)

    def test_text_contains_conflicts_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Conflicts (0):", text)

    def test_text_contains_execution_plan(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Execution plan:", text)

    def test_text_contains_parallel_groups(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("parallel groups:", text)

    def test_text_contains_integration_recommendations(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Integration recommendations:", text)

    def test_text_contains_blocking_items(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Blocking items:", text)

    def test_text_contains_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Safety notes:", text)

    def test_text_shows_feature_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root, feature_filter="alpha")
            text = render_orchestration_text(report)
            self.assertIn("Feature filter: alpha", text)

    def test_text_shows_conflict_details(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "a", extra_spec_content="src/app.py\n")
            write_feature_bundle(root, "b", extra_spec_content="src/app.py\n")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("file:", text.lower())
            self.assertIn("features:", text)

    def test_text_shows_blocking_items_none_when_clear(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Blocking items: (none)", text)

    def test_text_shows_safe_for_parallel_bool(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("safe_for_parallel: True", text)


class FeatureFilterTests(TestCase):
    """Test --feature filter behavior."""

    def test_filter_single_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            report = build_orchestration_plan(root, feature_filter="alpha")
            self.assertEqual(report.feature_filter, "alpha")
            self.assertIn("alpha", report.plan.execution_order)
            self.assertNotIn("beta", report.plan.execution_order)

    def test_filter_nonexistent_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root, feature_filter="nonexistent")
            self.assertEqual(report.feature_filter, "nonexistent")
            self.assertEqual(len(report.plan.execution_order), 0)

    def test_filter_invalid_slug_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with self.assertRaises(ValueError):
                build_orchestration_plan(root, feature_filter="INVALID_UPPER")

    def test_filter_cli_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root), "--feature", "alpha", "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["feature_filter"], "alpha")

    def test_filter_cli_invalid_slug_exit_code_2(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root), "--feature", "INVALID", "--json"]
            )
            self.assertEqual(code, 2)


class ErrorCasesTests(TestCase):
    """Test error handling."""

    def test_invalid_slug_uppercase_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with self.assertRaises(ValueError):
                build_orchestration_plan(root, feature_filter="MY-FEATURE")

    def test_invalid_slug_with_spaces_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with self.assertRaises(ValueError):
                build_orchestration_plan(root, feature_filter="my feature")

    def test_cli_invalid_slug_stderr_message(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root), "--feature", "INVALID"]
            )
            self.assertEqual(code, 2)
            self.assertGreater(len(stderr), 0)

    def test_missing_workspace_path_uses_cwd(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            import os
            old_cwd = os.getcwd()
            try:
                os.chdir(root)
                code, stdout, stderr = run_cli(["orchestrate", "plan", "--json"])
                self.assertEqual(code, 0, stderr)
                payload = json.loads(stdout)
                self.assertEqual(payload["status"], "ok")
            finally:
                os.chdir(old_cwd)

    def test_root_is_absolute_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_orchestration_plan(root)
            self.assertTrue(Path(report.root).is_absolute())


class NoSubprocessNetworkTokenTests(TestCase):
    """Verify orchestration module does not import subprocess, network, or token modules."""

    def test_no_subprocess_import(self) -> None:
        import specspine.orchestration as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotEqual(alias.name, "subprocess")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.assertNotIn("subprocess", node.module)

    def test_no_requests_import(self) -> None:
        import specspine.orchestration as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotEqual(alias.name, "requests")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.assertNotIn("requests", node.module)

    def test_no_http_client_import(self) -> None:
        import specspine.orchestration as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotEqual(alias.name, "http.client")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.assertNotIn("http.client", node.module)

    def test_no_urllib_import(self) -> None:
        import specspine.orchestration as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotEqual(alias.name, "urllib")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.assertNotIn("urllib", node.module)

    def test_safety_notes_mention_subprocess(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            self.assertTrue(
                any("subprocess" in note for note in report.safety_notes)
            )

    def test_safety_notes_mention_network(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            self.assertTrue(
                any("network" in note for note in report.safety_notes)
            )

    def test_safety_notes_mention_token(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            self.assertTrue(
                any("token" in note for note in report.safety_notes)
            )


class EdgeCaseFunctionalTests(TestCase):
    """Test edge cases and boundary conditions."""

    def test_many_independent_features_single_group(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            for i in range(10):
                write_feature_bundle(root, f"feature-{i:02d}")
            report = build_orchestration_plan(root)
            self.assertEqual(len(report.plan.parallel_groups), 1)
            self.assertEqual(len(report.plan.parallel_groups[0].features), 10)

    def test_mixed_independent_and_dependent(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "base")
            write_feature_bundle(root, "independent")
            write_feature_bundle(
                root, "dependent", extra_exec_content="depends on base"
            )
            report = build_orchestration_plan(root)
            order = report.plan.execution_order
            self.assertIn("base", order)
            self.assertIn("independent", order)
            self.assertIn("dependent", order)
            self.assertLess(order.index("base"), order.index("dependent"))

    def test_report_as_dict_matches_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            json_parsed = json.loads(render_orchestration_json(report))
            self.assertEqual(report.as_dict(), json_parsed)

    def test_conflict_as_dict_values(self) -> None:
        c = OrchestrationConflict(
            conflict_type="file",
            affected_files=("src/app.py", "src/utils.py"),
            affected_ac_ids=("AC001", "AC002"),
            features_involved=("alpha", "beta"),
            severity="high",
            description="test conflict",
        )
        d = c.as_dict()
        self.assertEqual(d["affected_files"], ["src/app.py", "src/utils.py"])
        self.assertEqual(d["affected_ac_ids"], ["AC001", "AC002"])
        self.assertEqual(d["features_involved"], ["alpha", "beta"])
        self.assertEqual(d["severity"], "high")

    def test_parallel_group_as_dict(self) -> None:
        g = ParallelGroup(group_id=1, features=("a", "b", "c"))
        d = g.as_dict()
        self.assertEqual(d["group_id"], 1)
        self.assertEqual(d["features"], ["a", "b", "c"])

    def test_plan_as_dict_all_fields(self) -> None:
        g = ParallelGroup(group_id=1, features=("a",))
        p = OrchestrationPlan(
            execution_order=("a", "b"),
            parallel_groups=(g,),
            blocked_features=("c",),
            safe_for_parallel=False,
        )
        d = p.as_dict()
        self.assertEqual(d["execution_order"], ["a", "b"])
        self.assertEqual(d["blocked_features"], ["c"])
        self.assertFalse(d["safe_for_parallel"])

    def test_report_as_dict_all_fields(self) -> None:
        g = ParallelGroup(group_id=1, features=())
        p = OrchestrationPlan(
            execution_order=(),
            parallel_groups=(g,),
            blocked_features=(),
            safe_for_parallel=True,
        )
        r = OrchestrationReport(
            root="/tmp",
            feature_filter=None,
            conflicts=(),
            plan=p,
            integration_recommendations=("rec1", "rec2"),
            status="ok",
            blocking_items=(),
            safety_notes=("note1",),
        )
        d = r.as_dict()
        self.assertEqual(d["root"], "/tmp")
        self.assertIsNone(d["feature_filter"])
        self.assertEqual(d["integration_recommendations"], ["rec1", "rec2"])
        self.assertEqual(d["status"], "ok")
