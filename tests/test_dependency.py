import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import main
from specspine.dependency import (
    build_dependency_graph,
    compute_critical_path,
    detect_cycles,
    render_dependency_json,
    render_dependency_text,
    topological_sort,
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
            ]
        )
        + "\n",
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


class BuildDependencyGraphTests(TestCase):
    def test_empty_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            result = build_dependency_graph(root)
            self.assertEqual(result["root"], str(root.resolve()))
            self.assertEqual(result["nodes"], [])
            self.assertEqual(result["edges"], [])
            self.assertIsNone(result["topological_order"])
            self.assertEqual(result["cycles"], [])
            self.assertEqual(result["critical_path"]["path"], [])

    def test_single_feature_no_deps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha", effort="S")
            result = build_dependency_graph(root)
            self.assertEqual(len(result["nodes"]), 1)
            self.assertEqual(result["nodes"][0]["slug"], "alpha")
            self.assertEqual(result["edges"], [])
            self.assertEqual(result["topological_order"], ["alpha"])
            self.assertEqual(result["cycles"], [])

    def test_two_features_no_deps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha", effort="S")
            write_feature_bundle(root, "beta", effort="M")
            result = build_dependency_graph(root)
            self.assertEqual(len(result["nodes"]), 2)
            slugs = [n["slug"] for n in result["nodes"]]
            self.assertIn("alpha", slugs)
            self.assertIn("beta", slugs)
            self.assertEqual(result["topological_order"], ["alpha", "beta"])

    def test_explicit_dependency_via_feature_id(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "base-feature")
            write_feature_bundle(
                root,
                "dependent-feature",
                extra_content="## Dependencies\n\nThis depends on Feature ID: base-feature for setup.",
            )
            result = build_dependency_graph(root)
            edges = result["edges"]
            explicit = [e for e in edges if e["inference"] == "explicit"]
            self.assertEqual(len(explicit), 1)
            self.assertEqual(explicit[0]["from"], "dependent-feature")
            self.assertEqual(explicit[0]["to"], "base-feature")

    def test_explicit_dependency_via_depends_on(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "auth")
            write_feature_bundle(
                root,
                "admin-panel",
                extra_content="## Dependencies\n\nThis depends on auth for user verification.",
            )
            result = build_dependency_graph(root)
            explicit = [e for e in result["edges"] if e["inference"] == "explicit"]
            self.assertTrue(any(e["from"] == "admin-panel" and e["to"] == "auth" for e in explicit))

    def test_explicit_dependency_via_after(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "db-setup")
            write_feature_bundle(
                root,
                "migrations",
                extra_content="Run this after db-setup is complete.",
            )
            result = build_dependency_graph(root)
            explicit = [e for e in result["edges"] if e["inference"] == "explicit"]
            self.assertTrue(any(e["from"] == "migrations" and e["to"] == "db-setup" for e in explicit))

    def test_explicit_dependency_via_blocked_by(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "api")
            write_feature_bundle(
                root,
                "frontend",
                extra_content="Blocked by api until endpoints are ready.",
            )
            result = build_dependency_graph(root)
            explicit = [e for e in result["edges"] if e["inference"] == "explicit"]
            self.assertTrue(any(e["from"] == "frontend" and e["to"] == "api" for e in explicit))

    def test_explicit_dependency_via_requires(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "core")
            write_feature_bundle(
                root,
                "plugin",
                extra_content="This feature requires core functionality.",
            )
            result = build_dependency_graph(root)
            explicit = [e for e in result["edges"] if e["inference"] == "explicit"]
            self.assertTrue(any(e["from"] == "plugin" and e["to"] == "core" for e in explicit))

    def test_explicit_dependency_via_prerequisite(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "infra")
            write_feature_bundle(
                root,
                "app",
                extra_content="Prerequisite: infra",
            )
            result = build_dependency_graph(root)
            explicit = [e for e in result["edges"] if e["inference"] == "explicit"]
            self.assertTrue(any(e["from"] == "app" and e["to"] == "infra" for e in explicit))

    def test_no_implicit_dependency_shared_milestone(self) -> None:
        """Implicit dependencies are not created to avoid O(n^2) edge explosion."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "feat-a", milestone="v1.0")
            write_feature_bundle(root, "feat-b", milestone="v1.0")
            result = build_dependency_graph(root)
            implicit = [e for e in result["edges"] if e["inference"] == "implicit"]
            self.assertEqual(len(implicit), 0, "Implicit dependencies should not be created")

    def test_no_implicit_dependency_for_unassigned_milestone(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "feat-a")
            write_feature_bundle(root, "feat-b")
            result = build_dependency_graph(root)
            implicit = [e for e in result["edges"] if e["inference"] == "implicit"]
            milestone_edges = [e for e in implicit if "Shared milestone" in e["reason"]]
            self.assertEqual(len(milestone_edges), 0)

    def test_feature_filter_single(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            write_feature_bundle(root, "gamma")
            result = build_dependency_graph(root, feature_slugs=["beta"])
            self.assertEqual(result["feature_filter"], "beta")
            self.assertEqual(len(result["nodes"]), 1)
            self.assertEqual(result["nodes"][0]["slug"], "beta")

    def test_feature_filter_multiple(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            write_feature_bundle(root, "gamma")
            result = build_dependency_graph(root, feature_slugs=["alpha", "gamma"])
            self.assertIsNone(result["feature_filter"])
            self.assertEqual(len(result["nodes"]), 2)
            slugs = [n["slug"] for n in result["nodes"]]
            self.assertIn("alpha", slugs)
            self.assertIn("gamma", slugs)

    def test_feature_filter_with_nonexistent_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            result = build_dependency_graph(root, feature_slugs=["nonexistent"])
            self.assertEqual(result["nodes"], [])

    def test_node_dep_count(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "base")
            write_feature_bundle(root, "mid")
            write_feature_bundle(
                root,
                "top",
                extra_content="Feature ID: base depends on mid for integration.",
            )
            result = build_dependency_graph(root)
            nodes_by_slug = {n["slug"]: n for n in result["nodes"]}
            self.assertGreaterEqual(nodes_by_slug["top"]["dep_count"], 1)

    def test_node_effort_and_milestone(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "big", effort="L", milestone="m1")
            result = build_dependency_graph(root)
            self.assertEqual(result["nodes"][0]["effort"], "L")
            self.assertEqual(result["nodes"][0]["milestone"], "m1")

    def test_recommended_commands_present(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            result = build_dependency_graph(root)
            self.assertTrue(len(result["recommended_commands"]) > 0)
            self.assertTrue(
                any("specspine feature handoff alpha" in cmd for cmd in result["recommended_commands"])
            )

    def test_deterministic_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            first = build_dependency_graph(root)
            second = build_dependency_graph(root)
            self.assertEqual(first, second)

    def test_dependency_edge_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "base")
            write_feature_bundle(
                root,
                "dep",
                extra_content="depends on base",
            )
            result = build_dependency_graph(root)
            edges = [e for e in result["edges"] if e["inference"] == "explicit"]
            self.assertEqual(len(edges), 1)
            edge = edges[0]
            self.assertEqual(edge["from"], "dep")
            self.assertEqual(edge["to"], "base")
            self.assertEqual(edge["inference"], "explicit")
            self.assertIn("Explicit reference", edge["reason"])


class TopologicalSortTests(TestCase):
    def test_linear_chain(self) -> None:
        nodes = [
            {"slug": "a"},
            {"slug": "b"},
            {"slug": "c"},
        ]
        edges = [
            {"from": "a", "to": "b"},
            {"from": "b", "to": "c"},
        ]
        result = topological_sort(nodes, edges)
        self.assertEqual(result, ["a", "b", "c"])

    def test_diamond(self) -> None:
        nodes = [
            {"slug": "a"},
            {"slug": "b"},
            {"slug": "c"},
            {"slug": "d"},
        ]
        edges = [
            {"from": "a", "to": "b"},
            {"from": "a", "to": "c"},
            {"from": "b", "to": "d"},
            {"from": "c", "to": "d"},
        ]
        result = topological_sort(nodes, edges)
        self.assertEqual(result[0], "a")
        self.assertEqual(result[-1], "d")
        self.assertIn("b", result)
        self.assertIn("c", result)

    def test_cycle_returns_none(self) -> None:
        nodes = [
            {"slug": "a"},
            {"slug": "b"},
        ]
        edges = [
            {"from": "a", "to": "b"},
            {"from": "b", "to": "a"},
        ]
        result = topological_sort(nodes, edges)
        self.assertIsNone(result)

    def test_no_edges(self) -> None:
        nodes = [
            {"slug": "x"},
            {"slug": "y"},
            {"slug": "z"},
        ]
        result = topological_sort(nodes, [])
        self.assertEqual(result, ["x", "y", "z"])

    def test_single_node(self) -> None:
        nodes = [{"slug": "solo"}]
        result = topological_sort(nodes, [])
        self.assertEqual(result, ["solo"])

    def test_empty(self) -> None:
        result = topological_sort([], [])
        self.assertEqual(result, [])


class DetectCyclesTests(TestCase):
    def test_simple_cycle(self) -> None:
        nodes = [
            {"slug": "a"},
            {"slug": "b"},
        ]
        edges = [
            {"from": "a", "to": "b"},
            {"from": "b", "to": "a"},
        ]
        cycles = detect_cycles(nodes, edges)
        self.assertEqual(len(cycles), 1)
        self.assertIn("a", cycles[0])
        self.assertIn("b", cycles[0])

    def test_no_cycles(self) -> None:
        nodes = [
            {"slug": "a"},
            {"slug": "b"},
            {"slug": "c"},
        ]
        edges = [
            {"from": "a", "to": "b"},
            {"from": "b", "to": "c"},
        ]
        cycles = detect_cycles(nodes, edges)
        self.assertEqual(cycles, [])

    def test_three_node_cycle(self) -> None:
        nodes = [
            {"slug": "a"},
            {"slug": "b"},
            {"slug": "c"},
        ]
        edges = [
            {"from": "a", "to": "b"},
            {"from": "b", "to": "c"},
            {"from": "c", "to": "a"},
        ]
        cycles = detect_cycles(nodes, edges)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(len(cycles[0]), 4)

    def test_empty(self) -> None:
        cycles = detect_cycles([], [])
        self.assertEqual(cycles, [])

    def test_self_cycle(self) -> None:
        nodes = [{"slug": "a"}]
        edges = [{"from": "a", "to": "a"}]
        cycles = detect_cycles(nodes, edges)
        self.assertEqual(len(cycles), 1)


class ComputeCriticalPathTests(TestCase):
    def test_linear_chain_effort(self) -> None:
        nodes = [
            {"slug": "a", "effort": "S"},
            {"slug": "b", "effort": "M"},
            {"slug": "c", "effort": "L"},
        ]
        edges = [
            {"from": "a", "to": "b"},
            {"from": "b", "to": "c"},
        ]
        topo = ["a", "b", "c"]
        result = compute_critical_path(nodes, edges, topo)
        self.assertEqual(result["path"], ["a", "b", "c"])
        self.assertEqual(result["total_effort"], 1 + 2 + 4)

    def test_branching_path(self) -> None:
        nodes = [
            {"slug": "start", "effort": "S"},
            {"slug": "short", "effort": "S"},
            {"slug": "long", "effort": "XL"},
        ]
        edges = [
            {"from": "start", "to": "short"},
            {"from": "start", "to": "long"},
        ]
        topo = ["start", "long", "short"]
        result = compute_critical_path(nodes, edges, topo)
        self.assertEqual(result["total_effort"], 1 + 8)
        self.assertIn("long", result["path"])

    def test_empty(self) -> None:
        result = compute_critical_path([], [], [])
        self.assertEqual(result["path"], [])
        self.assertEqual(result["total_effort"], 0)

    def test_single_node(self) -> None:
        nodes = [{"slug": "a", "effort": "M"}]
        result = compute_critical_path(nodes, [], ["a"])
        self.assertEqual(result["path"], ["a"])
        self.assertEqual(result["total_effort"], 2)

    def test_unknown_effort_defaults_to_3(self) -> None:
        nodes = [
            {"slug": "a", "effort": "unknown"},
            {"slug": "b", "effort": "unknown"},
        ]
        edges = [{"from": "a", "to": "b"}]
        result = compute_critical_path(nodes, edges, ["a", "b"])
        self.assertEqual(result["total_effort"], 6)


class RenderDependencyTests(TestCase):
    def test_json_render_is_valid_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            result = build_dependency_graph(root)
            json_str = render_dependency_json(result)
            parsed = json.loads(json_str)
            self.assertEqual(parsed["nodes"][0]["slug"], "alpha")

    def test_text_render_contains_header(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            result = build_dependency_graph(root)
            text = render_dependency_text(result)
            self.assertIn("Dependency graph for", text)

    def test_text_render_contains_nodes_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            result = build_dependency_graph(root)
            text = render_dependency_text(result)
            self.assertIn("Nodes (1):", text)

    def test_text_render_contains_edges_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            result = build_dependency_graph(root)
            text = render_dependency_text(result)
            self.assertIn("Edges (0):", text)

    def test_text_render_contains_topological_order(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            result = build_dependency_graph(root)
            text = render_dependency_text(result)
            self.assertIn("Topological order:", text)

    def test_text_render_contains_cycles_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            result = build_dependency_graph(root)
            text = render_dependency_text(result)
            self.assertIn("Cycles:", text)

    def test_text_render_contains_critical_path_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            result = build_dependency_graph(root)
            text = render_dependency_text(result)
            self.assertIn("Critical path", text)


class DependencyCLITests(TestCase):
    def test_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            code, stdout, stderr = run_cli(
                ["feature", "dependency", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["nodes"][0]["slug"], "alpha")

    def test_text_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            code, stdout, stderr = run_cli(
                ["feature", "dependency", str(root)]
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Dependency graph for", stdout)

    def test_single_feature_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            code, stdout, stderr = run_cli(
                ["feature", "dependency", str(root), "--feature", "alpha", "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(len(payload["nodes"]), 1)
            self.assertEqual(payload["nodes"][0]["slug"], "alpha")

    def test_multiple_features_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "alpha")
            write_feature_bundle(root, "beta")
            write_feature_bundle(root, "gamma")
            code, stdout, stderr = run_cli(
                ["feature", "dependency", str(root), "--features", "alpha,beta", "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(len(payload["nodes"]), 2)
            slugs = [n["slug"] for n in payload["nodes"]]
            self.assertIn("alpha", slugs)
            self.assertIn("beta", slugs)

    def test_empty_workspace_cli(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, stderr = run_cli(
                ["feature", "dependency", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["nodes"], [])

    def test_help_does_not_crash(self) -> None:
        code, stdout, stderr = run_cli(
            ["feature", "dependency", "--help"]
        )
        self.assertEqual(code, 0)
        self.assertIn("--json", stdout)
        self.assertIn("--feature", stdout)
        self.assertIn("--features", stdout)


class DependencyGraphIntegrationTests(TestCase):
    def test_chain_dependency_computes_correct_order(self) -> None:
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
            result = build_dependency_graph(root)
            self.assertEqual(result["topological_order"], ["layer3", "layer2", "layer1"])
            self.assertEqual(len(result["critical_path"]["path"]), 3)
            self.assertIn("layer1", result["critical_path"]["path"])
            self.assertIn("layer2", result["critical_path"]["path"])
            self.assertIn("layer3", result["critical_path"]["path"])
            self.assertEqual(result["critical_path"]["total_effort"], 1 + 2 + 4)
            self.assertEqual(result["cycles"], [])

    def test_multiple_dependencies_same_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "auth")
            write_feature_bundle(root, "db")
            write_feature_bundle(
                root,
                "app",
                extra_content="Feature ID: auth depends on db",
            )
            result = build_dependency_graph(root)
            explicit = [e for e in result["edges"] if e["inference"] == "explicit"]
            from_app = [e for e in explicit if e["from"] == "app"]
            self.assertGreaterEqual(len(from_app), 1)

    def test_no_false_positives_for_own_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "self-ref", extra_content="Feature ID: self-ref")
            result = build_dependency_graph(root, feature_slugs=["self-ref"])
            self.assertEqual(result["edges"], [])

    def test_cycle_detection_in_graph(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "a",
                extra_content="depends on b",
            )
            write_feature_bundle(
                root,
                "b",
                extra_content="depends on a",
            )
            result = build_dependency_graph(root)
            self.assertIsNotNone(result["cycles"])
            self.assertGreater(len(result["cycles"]), 0)
            self.assertIsNone(result["topological_order"])
            self.assertEqual(result["critical_path"]["path"], [])

    def test_root_is_resolved_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            result = build_dependency_graph(root)
            self.assertTrue(Path(result["root"]).is_absolute())

    def test_feature_filter_missing_feature_in_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(root, "exists")
            result = build_dependency_graph(root, feature_slugs=["missing"])
            self.assertEqual(result["nodes"], [])
            self.assertEqual(result["edges"], [])

    def test_dependency_not_to_nonexistent_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_feature_bundle(
                root,
                "alone",
                extra_content="depends on nonexistent-feature",
            )
            result = build_dependency_graph(root)
            explicit = [e for e in result["edges"] if e["inference"] == "explicit"]
            self.assertEqual(len(explicit), 0)
