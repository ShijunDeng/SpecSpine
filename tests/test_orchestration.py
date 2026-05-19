import json
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
    _build_dependency_graph,
    _compute_parallel_groups,
    _detect_contract_conflicts,
    _detect_file_conflicts,
    _extract_ac_ids,
    _extract_contracts,
    _generate_integration_recommendations,
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


class OrchestrationConflictTests(TestCase):
    def test_conflict_as_dict(self) -> None:
        c = OrchestrationConflict(
            conflict_type="file",
            affected_files=("src/app.py",),
            affected_ac_ids=("AC001",),
            features_involved=("alpha", "beta"),
            severity="high",
            description="test",
        )
        d = c.as_dict()
        self.assertEqual(d["conflict_type"], "file")
        self.assertEqual(d["severity"], "high")
        self.assertEqual(d["features_involved"], ["alpha", "beta"])

    def test_conflict_frozen(self) -> None:
        c = OrchestrationConflict(
            conflict_type="contract",
            affected_files=(),
            affected_ac_ids=(),
            features_involved=("a", "b"),
            severity="critical",
            description="desc",
        )
        with self.assertRaises(AttributeError):
            c.conflict_type = "file"


class ParallelGroupTests(TestCase):
    def test_group_as_dict(self) -> None:
        g = ParallelGroup(group_id=1, features=("a", "b"))
        d = g.as_dict()
        self.assertEqual(d["group_id"], 1)
        self.assertEqual(d["features"], ["a", "b"])

    def test_group_frozen(self) -> None:
        g = ParallelGroup(group_id=1, features=("a",))
        with self.assertRaises(AttributeError):
            g.group_id = 2


class OrchestrationPlanTests(TestCase):
    def test_plan_as_dict(self) -> None:
        g = ParallelGroup(group_id=1, features=("a",))
        p = OrchestrationPlan(
            execution_order=("a", "b"),
            parallel_groups=(g,),
            blocked_features=("c",),
            safe_for_parallel=False,
        )
        d = p.as_dict()
        self.assertEqual(d["execution_order"], ["a", "b"])
        self.assertEqual(d["safe_for_parallel"], False)

    def test_plan_frozen(self) -> None:
        p = OrchestrationPlan(
            execution_order=("a",),
            parallel_groups=(),
            blocked_features=(),
            safe_for_parallel=True,
        )
        with self.assertRaises(AttributeError):
            p.safe_for_parallel = False


class OrchestrationReportTests(TestCase):
    def test_report_as_dict(self) -> None:
        g = ParallelGroup(group_id=1, features=("a",))
        p = OrchestrationPlan(
            execution_order=("a",),
            parallel_groups=(g,),
            blocked_features=(),
            safe_for_parallel=True,
        )
        r = OrchestrationReport(
            root="/tmp",
            feature_filter=None,
            conflicts=(),
            plan=p,
            integration_recommendations=("rec1",),
            status="ok",
            blocking_items=(),
            safety_notes=("note",),
        )
        d = r.as_dict()
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["root"], "/tmp")
        self.assertIsNone(d["feature_filter"])

    def test_report_frozen(self) -> None:
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
            integration_recommendations=(),
            status="ok",
            blocking_items=(),
            safety_notes=(),
        )
        with self.assertRaises(AttributeError):
            r.status = "blocked"


class ScanFeatureFilePathsTests(TestCase):
    def test_returns_paths_from_feature_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(root, "alpha", extra_spec_content="src/app.py\n")
            paths = _scan_feature_file_paths(root, "alpha")
            self.assertIn("src/app.py", paths)

    def test_empty_when_no_feature_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = _scan_feature_file_paths(root, "nonexistent")
            self.assertEqual(len(paths), 0)


class ExtractAcIdsTests(TestCase):
    def test_extracts_ac_ids(self) -> None:
        ids = _extract_ac_ids("AC001 do something and AC002 do other")
        self.assertEqual(ids, ["AC001", "AC002"])

    def test_deduplicates(self) -> None:
        ids = _extract_ac_ids("AC001 and AC001 again")
        self.assertEqual(ids, ["AC001"])

    def test_empty_string(self) -> None:
        ids = _extract_ac_ids("no acceptance criteria here")
        self.assertEqual(ids, [])


class ExtractContractsTests(TestCase):
    def test_extracts_endpoint_contracts(self) -> None:
        c = _extract_contracts("endpoint: /api/users")
        self.assertIn("/api/users", c.get("endpoint", []))

    def test_extracts_schema_contracts(self) -> None:
        c = _extract_contracts("schema: User")
        self.assertIn("User", c.get("schema", []))

    def test_extracts_config_contracts(self) -> None:
        c = _extract_contracts("config: DATABASE_URL")
        self.assertIn("DATABASE_URL", c.get("config", []))

    def test_extracts_api_contracts(self) -> None:
        c = _extract_contracts("api: v1")
        self.assertIn("v1", c.get("api", []))

    def test_extracts_http_method_routes(self) -> None:
        c = _extract_contracts("GET /api/items")
        self.assertIn("/api/items", c.get("endpoint", []))

    def test_extracts_route_pattern(self) -> None:
        c = _extract_contracts("route: /health")
        self.assertIn("/health", c.get("endpoint", []))

    def test_extracts_model_pattern(self) -> None:
        c = _extract_contracts("class UserModel(BaseModel)")
        self.assertIn("UserModel", c.get("schema", []))

    def test_extracts_env_variable(self) -> None:
        c = _extract_contracts("env: SECRET_KEY")
        self.assertIn("SECRET_KEY", c.get("config", []))

    def test_returns_sorted_unique(self) -> None:
        c = _extract_contracts("schema: Zebra\nschema: Alpha\nschema: Alpha")
        self.assertEqual(c["schema"], ["Alpha", "Zebra"])

    def test_empty_content(self) -> None:
        c = _extract_contracts("")
        for key in c:
            self.assertEqual(len(c[key]), 0)


class BuildDependencyGraphTests(TestCase):
    def test_empty_slugs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            adj = _build_dependency_graph(root, [])
            self.assertEqual(adj, {})

    def test_single_feature_no_deps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(root, "alpha")
            adj = _build_dependency_graph(root, ["alpha"])
            self.assertEqual(adj, {"alpha": set()})

    def test_explicit_dependency(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(root, "base")
            write_feature_bundle(
                root, "dependent", extra_exec_content="depends on base"
            )
            adj = _build_dependency_graph(root, ["base", "dependent"])
            self.assertIn("base", adj["dependent"])


class DetectFileConflictsTests(TestCase):
    def test_no_conflict_when_no_overlapping_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(root, "alpha", extra_spec_content="src/alpha.py\n")
            write_feature_bundle(root, "beta", extra_spec_content="src/beta.py\n")
            conflicts = _detect_file_conflicts(root, ["alpha", "beta"])
            self.assertEqual(len(conflicts), 0)

    def test_detects_overlapping_file_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(root, "alpha", extra_spec_content="src/app.py\n")
            write_feature_bundle(root, "beta", extra_spec_content="src/app.py\n")
            conflicts = _detect_file_conflicts(root, ["alpha", "beta"])
            self.assertEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0].conflict_type, "file")
            self.assertIn("alpha", conflicts[0].features_involved)
            self.assertIn("beta", conflicts[0].features_involved)

    def test_severity_based_on_overlap_count(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(
                root,
                "alpha",
                extra_spec_content="src/a.py\nsrc/b.py\nsrc/c.py\nsrc/d.py\n",
            )
            write_feature_bundle(
                root,
                "beta",
                extra_spec_content="src/a.py\nsrc/b.py\nsrc/c.py\nsrc/d.py\n",
            )
            conflicts = _detect_file_conflicts(root, ["alpha", "beta"])
            self.assertEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0].severity, "high")

    def test_single_feature_no_conflicts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(root, "alpha")
            conflicts = _detect_file_conflicts(root, ["alpha"])
            self.assertEqual(len(conflicts), 0)

    def test_empty_features_list(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            conflicts = _detect_file_conflicts(root, [])
            self.assertEqual(len(conflicts), 0)


class DetectContractConflictsTests(TestCase):
    def test_no_conflict_when_no_shared_contracts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(root, "alpha", extra_spec_content="endpoint: /api/a\n")
            write_feature_bundle(root, "beta", extra_spec_content="endpoint: /api/b\n")
            conflicts = _detect_contract_conflicts(root, ["alpha", "beta"])
            self.assertEqual(len(conflicts), 0)

    def test_detects_shared_endpoint(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(root, "alpha", extra_spec_content="endpoint: /api/users\n")
            write_feature_bundle(root, "beta", extra_spec_content="endpoint: /api/users\n")
            conflicts = _detect_contract_conflicts(root, ["alpha", "beta"])
            self.assertEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0].conflict_type, "contract")
            self.assertEqual(conflicts[0].severity, "critical")

    def test_detects_shared_schema(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(root, "alpha", extra_spec_content="schema: User\n")
            write_feature_bundle(root, "beta", extra_spec_content="schema: User\n")
            conflicts = _detect_contract_conflicts(root, ["alpha", "beta"])
            self.assertEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0].severity, "high")

    def test_detects_shared_config(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(root, "alpha", extra_spec_content="config: DB_HOST\n")
            write_feature_bundle(root, "beta", extra_spec_content="config: DB_HOST\n")
            conflicts = _detect_contract_conflicts(root, ["alpha", "beta"])
            self.assertEqual(len(conflicts), 1)

    def test_single_feature_no_contract_conflicts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_feature_bundle(root, "alpha")
            conflicts = _detect_contract_conflicts(root, ["alpha"])
            self.assertEqual(len(conflicts), 0)

    def test_empty_features_list(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            conflicts = _detect_contract_conflicts(root, [])
            self.assertEqual(len(conflicts), 0)


class ComputeParallelGroupsTests(TestCase):
    def test_no_features(self) -> None:
        groups = _compute_parallel_groups([], {})
        self.assertEqual(len(groups), 0)

    def test_single_feature(self) -> None:
        groups = _compute_parallel_groups(["a"], {"a": set()})
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].features, ("a",))

    def test_independent_features_same_group(self) -> None:
        groups = _compute_parallel_groups(
            ["a", "b"],
            {"a": set(), "b": set()},
        )
        self.assertEqual(len(groups), 1)
        self.assertEqual(set(groups[0].features), {"a", "b"})

    def test_linear_chain_sequential_groups(self) -> None:
        groups = _compute_parallel_groups(
            ["a", "b", "c"],
            {"a": set(), "b": {"a"}, "c": {"b"}},
        )
        self.assertEqual(len(groups), 3)
        self.assertEqual(groups[0].features, ("a",))
        self.assertEqual(groups[1].features, ("b",))
        self.assertEqual(groups[2].features, ("c",))

    def test_diamond_parallel_groups(self) -> None:
        groups = _compute_parallel_groups(
            ["a", "b", "c", "d"],
            {
                "a": set(),
                "b": {"a"},
                "c": {"a"},
                "d": {"b", "c"},
            },
        )
        self.assertGreaterEqual(len(groups), 2)
        all_features = set()
        for g in groups:
            all_features.update(g.features)
        self.assertEqual(all_features, {"a", "b", "c", "d"})


class GenerateIntegrationRecommendationsTests(TestCase):
    def test_no_features_no_conflicts(self) -> None:
        recs = _generate_integration_recommendations([], [], {})
        self.assertEqual(len(recs), 1)
        self.assertIn("No integration steps required", recs[0])

    def test_file_conflict_recommendation(self) -> None:
        conflict = OrchestrationConflict(
            conflict_type="file",
            affected_files=("src/app.py",),
            affected_ac_ids=(),
            features_involved=("a", "b"),
            severity="high",
            description="overlap",
        )
        recs = _generate_integration_recommendations([conflict], ["a", "b"], {"a": {"b"}, "b": set()})
        self.assertTrue(any("File overlap" in r for r in recs))

    def test_contract_conflict_recommendation(self) -> None:
        conflict = OrchestrationConflict(
            conflict_type="contract",
            affected_files=("specs/features/a.md",),
            affected_ac_ids=(),
            features_involved=("a", "b"),
            severity="critical",
            description="shared endpoint",
        )
        recs = _generate_integration_recommendations([conflict], ["a", "b"], {"a": {"b"}, "b": set()})
        self.assertTrue(any("Contract overlap" in r for r in recs))

    def test_multiple_deps_recommendation(self) -> None:
        recs = _generate_integration_recommendations(
            [],
            ["a", "b", "c"],
            {"a": {"b", "c"}, "b": set(), "c": set()},
        )
        self.assertTrue(any("multiple dependencies" in r for r in recs))

    def test_execution_order_recommendation(self) -> None:
        recs = _generate_integration_recommendations(
            [],
            ["a", "b"],
            {"a": set(), "b": {"a"}},
        )
        self.assertTrue(any("integration tests" in r for r in recs))

    def test_no_conflicts_single_feature(self) -> None:
        recs = _generate_integration_recommendations([], ["a"], {"a": set()})
        self.assertTrue(any("No cross-feature integration" in r for r in recs))


class BuildOrchestrationPlanTests(TestCase):
    def test_empty_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_orchestration_plan(root)
            self.assertEqual(report.status, "ok")
            self.assertEqual(len(report.conflicts), 0)
            self.assertEqual(len(report.plan.execution_order), 0)

    def test_single_feature_no_conflicts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            self.assertEqual(report.status, "ok")
            self.assertEqual(len(report.conflicts), 0)
            self.assertEqual(report.plan.execution_order, ("alpha",))

    def test_two_features_no_conflicts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha", extra_spec_content="src/alpha.py\n")
            write_feature_bundle(root, "beta", extra_spec_content="src/beta.py\n")
            report = build_orchestration_plan(root)
            self.assertEqual(report.status, "ok")
            self.assertEqual(len(report.conflicts), 0)
            self.assertEqual(len(report.plan.parallel_groups), 1)

    def test_two_conflicting_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha", extra_spec_content="src/app.py\n")
            write_feature_bundle(root, "beta", extra_spec_content="src/app.py\n")
            report = build_orchestration_plan(root)
            self.assertEqual(len(report.conflicts), 1)
            self.assertEqual(report.conflicts[0].conflict_type, "file")

    def test_contract_conflict_critical(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "alpha",
                extra_spec_content="endpoint: /api/users\n",
            )
            write_feature_bundle(
                root,
                "beta",
                extra_spec_content="endpoint: /api/users\n",
            )
            report = build_orchestration_plan(root)
            contract_conflicts = [
                c for c in report.conflicts if c.conflict_type == "contract"
            ]
            self.assertGreater(len(contract_conflicts), 0)
            self.assertEqual(contract_conflicts[0].severity, "critical")

    def test_three_feature_dependency_chain(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "layer1")
            write_feature_bundle(
                root,
                "layer2",
                extra_exec_content="depends on layer1",
            )
            write_feature_bundle(
                root,
                "layer3",
                extra_exec_content="depends on layer2",
            )
            report = build_orchestration_plan(root)
            self.assertEqual(len(report.plan.execution_order), 3)
            self.assertEqual(len(report.plan.parallel_groups), 3)

    def test_feature_filter_single(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            report = build_orchestration_plan(root, feature_filter="alpha")
            self.assertEqual(report.feature_filter, "alpha")
            self.assertIn("alpha", report.plan.execution_order)
            self.assertNotIn("beta", report.plan.execution_order)

    def test_feature_filter_nonexistent(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root, feature_filter="nonexistent")
            self.assertEqual(report.feature_filter, "nonexistent")
            self.assertEqual(len(report.plan.execution_order), 0)

    def test_file_conflict_sets_warnings_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root, "a", extra_spec_content="src/app.py\nsrc/b.py\nsrc/c.py\nsrc/d.py\n"
            )
            write_feature_bundle(
                root, "b", extra_spec_content="src/app.py\nsrc/b.py\nsrc/c.py\nsrc/d.py\n"
            )
            report = build_orchestration_plan(root)
            self.assertIn(report.status, ("warnings", "blocked"))

    def test_contract_conflict_sets_blocked_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "a",
                extra_spec_content="endpoint: /api/shared\n",
            )
            write_feature_bundle(
                root,
                "b",
                extra_spec_content="endpoint: /api/shared\n",
            )
            report = build_orchestration_plan(root)
            self.assertEqual(report.status, "blocked")

    def test_blocking_items_present_for_critical_conflict(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "a",
                extra_spec_content="endpoint: /api/shared\n",
            )
            write_feature_bundle(
                root,
                "b",
                extra_spec_content="endpoint: /api/shared\n",
            )
            report = build_orchestration_plan(root)
            self.assertGreater(len(report.blocking_items), 0)

    def test_safety_notes_present(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_orchestration_plan(root)
            self.assertGreater(len(report.safety_notes), 0)
            self.assertTrue(
                any("subprocess" in note for note in report.safety_notes)
            )

    def test_root_is_resolved_absolute_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_orchestration_plan(root)
            self.assertTrue(Path(report.root).is_absolute())

    def test_integration_recommendations_present(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            self.assertGreater(len(report.integration_recommendations), 0)

    def test_parallel_groups_for_independent_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "a")
            write_feature_bundle(root, "b")
            write_feature_bundle(root, "c")
            report = build_orchestration_plan(root)
            self.assertEqual(len(report.plan.parallel_groups), 1)
            self.assertEqual(len(report.plan.parallel_groups[0].features), 3)

    def test_safe_for_parallel_when_no_conflicts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "a", extra_spec_content="src/a.py\n")
            write_feature_bundle(root, "b", extra_spec_content="src/b.py\n")
            report = build_orchestration_plan(root)
            self.assertTrue(report.plan.safe_for_parallel)

    def test_unsafe_for_parallel_with_critical_conflict(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "a",
                extra_spec_content="endpoint: /api/shared\n",
            )
            write_feature_bundle(
                root,
                "b",
                extra_spec_content="endpoint: /api/shared\n",
            )
            report = build_orchestration_plan(root)
            self.assertFalse(report.plan.safe_for_parallel)

    def test_deterministic_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            first = build_orchestration_plan(root)
            second = build_orchestration_plan(root)
            self.assertEqual(first.as_dict(), second.as_dict())

    def test_feature_filter_invalid_slug_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with self.assertRaises(ValueError):
                build_orchestration_plan(root, feature_filter="INVALID")


class RenderOrchestrationTests(TestCase):
    def test_json_render_is_valid_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            json_str = render_orchestration_json(report)
            parsed = json.loads(json_str)
            self.assertEqual(parsed["root"], str(root.resolve()))

    def test_json_render_sort_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            json_str = render_orchestration_json(report)
            parsed = json.loads(json_str)
            keys = list(parsed.keys())
            self.assertEqual(keys, sorted(keys))

    def test_text_render_contains_header(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Orchestration plan:", text)

    def test_text_render_contains_conflicts_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Conflicts (0):", text)

    def test_text_render_contains_execution_plan_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Execution plan:", text)

    def test_text_render_contains_integration_recommendations(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Integration recommendations:", text)

    def test_text_render_contains_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Safety notes:", text)

    def test_text_render_shows_blocking_items_none(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("Blocking items: (none)", text)

    def test_text_render_shows_feature_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root, feature_filter="alpha")
            text = render_orchestration_text(report)
            self.assertIn("Feature filter: alpha", text)

    def test_text_render_shows_conflict_details(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "a", extra_spec_content="src/app.py\n")
            write_feature_bundle(root, "b", extra_spec_content="src/app.py\n")
            report = build_orchestration_plan(root)
            text = render_orchestration_text(report)
            self.assertIn("file:", text)
            self.assertIn("features:", text)


class OrchestrationCLITests(TestCase):
    def test_plan_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["status"], "ok")

    def test_plan_text_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root)]
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Orchestration plan:", stdout)

    def test_plan_with_feature_filter(self) -> None:
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

    def test_plan_invalid_slug_exit_code_2(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root), "--feature", "INVALID", "--json"]
            )
            self.assertEqual(code, 2)

    def test_empty_workspace_cli(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["conflicts"], [])
            self.assertEqual(payload["plan"]["execution_order"], [])

    def test_help_does_not_crash(self) -> None:
        code, stdout, stderr = run_cli(["orchestrate", "plan", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("--json", stdout)
        self.assertIn("--feature", stdout)

    def test_missing_workspace_path_defaults_to_cwd(self) -> None:
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

    def test_two_conflicting_features_cli(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "a", extra_spec_content="src/app.py\n")
            write_feature_bundle(root, "b", extra_spec_content="src/app.py\n")
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertGreater(len(payload["conflicts"]), 0)

    def test_contract_conflict_via_cli(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "a",
                extra_spec_content="endpoint: /api/users\n",
            )
            write_feature_bundle(
                root,
                "b",
                extra_spec_content="endpoint: /api/users\n",
            )
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            contract_conflicts = [
                c for c in payload["conflicts"] if c["conflict_type"] == "contract"
            ]
            self.assertGreater(len(contract_conflicts), 0)

    def test_three_feature_chain_via_cli(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "layer1")
            write_feature_bundle(
                root, "layer2", extra_exec_content="depends on layer1"
            )
            write_feature_bundle(
                root, "layer3", extra_exec_content="depends on layer2"
            )
            code, stdout, stderr = run_cli(
                ["orchestrate", "plan", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(len(payload["plan"]["execution_order"]), 3)
            self.assertEqual(len(payload["plan"]["parallel_groups"]), 3)


class OrchestrationIntegrationTests(TestCase):
    def test_dependency_consistency(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "base")
            write_feature_bundle(
                root, "dep", extra_exec_content="depends on base"
            )
            report = build_orchestration_plan(root)
            self.assertIn("base", report.plan.execution_order)
            self.assertIn("dep", report.plan.execution_order)

    def test_change_risk_consistency(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha", extra_spec_content="src/risky.py\n")
            report = build_orchestration_plan(root)
            self.assertEqual(len(report.conflicts), 0)
            self.assertEqual(report.status, "ok")

    def test_no_subprocess_usage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            self.assertTrue(
                any("subprocess" in note for note in report.safety_notes)
            )

    def test_no_network_calls(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            self.assertTrue(
                any("network" in note for note in report.safety_notes)
            )

    def test_no_token_reads(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            report = build_orchestration_plan(root)
            self.assertTrue(
                any("token" in note for note in report.safety_notes)
            )

    def test_blocked_features_listed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "a",
                extra_spec_content="endpoint: /api/shared\n",
            )
            write_feature_bundle(
                root,
                "b",
                extra_spec_content="endpoint: /api/shared\n",
            )
            report = build_orchestration_plan(root)
            self.assertGreater(len(report.plan.blocked_features), 0)

    def test_execution_order_respects_dependencies(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "base")
            write_feature_bundle(
                root, "mid", extra_exec_content="depends on base"
            )
            write_feature_bundle(
                root, "top", extra_exec_content="depends on mid"
            )
            report = build_orchestration_plan(root)
            order = report.plan.execution_order
            self.assertLess(order.index("base"), order.index("mid"))
            self.assertLess(order.index("mid"), order.index("top"))

    def test_parallel_groups_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "a")
            write_feature_bundle(root, "b")
            write_feature_bundle(root, "c")
            first = build_orchestration_plan(root)
            second = build_orchestration_plan(root)
            self.assertEqual(
                first.plan.parallel_groups,
                second.plan.parallel_groups,
            )

    def test_conflict_affected_files_list(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "a", extra_spec_content="src/app.py\n")
            write_feature_bundle(root, "b", extra_spec_content="src/app.py\n")
            report = build_orchestration_plan(root)
            self.assertGreater(len(report.conflicts[0].affected_files), 0)

    def test_conflict_affected_ac_ids(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "a",
                acceptance_criteria=["AC001 do something"],
                extra_spec_content="src/app.py\n",
            )
            write_feature_bundle(
                root,
                "b",
                acceptance_criteria=["AC002 do other"],
                extra_spec_content="src/app.py\n",
            )
            report = build_orchestration_plan(root)
            self.assertEqual(len(report.conflicts[0].affected_ac_ids), 2)
