from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
)
from specspine.executor import (
    build_execution_plan,
    build_grading_rubric,
    render_grade_json,
    render_grade_text,
    render_loop_json,
    render_loop_text,
    render_plan_json,
    render_plan_text,
    run_execution_loop,
)
from specspine.workspace import init_workspace


def write_full_feature(
    root: Path,
    slug: str = "test-feature",
    *,
    status: str = "validated",
    ac_done: bool = True,
    tasks_done: bool = True,
    coverage_done: bool = True,
    quality_done: bool = True,
    with_deps: bool = False,
) -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)

    ac_marker = "x" if ac_done else " "
    task_marker = "x" if tasks_done else " "
    quality_marker = "x" if quality_done else " "

    ac1_text = "Users can see the dashboard."
    ac2_text = "Data is exported as CSV."
    task1_text = "Implement dashboard UI."
    task2_text = "Implement CSV export."

    if with_deps:
        task2_text = "Implement CSV export after T001."

    spec_content = "\n".join([
        f"# {slug.title()}",
        "",
        f"Feature ID: {slug}",
        f"Status: {status}",
        "Priority: high",
        "Owner: test-owner",
        "Milestone: v1",
        "Target Release: unassigned",
        "Project: unassigned",
        "Effort: M",
        "",
        "## Acceptance Criteria",
        "",
        f"- [{ac_marker}] AC001 {ac1_text}",
        f"- [{ac_marker}] AC002 {ac2_text}",
    ]) + "\n"
    (root / "specs" / "features" / f"{slug}.md").write_text(spec_content, encoding="utf-8")

    execution_content = "\n".join([
        f"# {slug.title()} Execution",
        "",
        f"Feature ID: {slug}",
        f"Status: {status}",
        "",
        "## Tasks",
        "",
        f"- [{task_marker}] T001 {task1_text}",
        f"- [{task_marker}] T002 {task2_text}",
    ]) + "\n"
    (root / "execution" / "features" / f"{slug}.md").write_text(execution_content, encoding="utf-8")

    coverage_target = "tests/test_dashboard.py"
    coverage_marker = "x" if coverage_done else " "
    quality_content = "\n".join([
        f"# {slug.title()} Quality",
        "",
        f"Feature ID: {slug}",
        f"Status: {status}",
        "",
        "## Required Checks",
        "",
        f"- [{quality_marker}] Dashboard reviewed.",
        f"- [{quality_marker}] Export tested.",
        "",
        "## Test Coverage",
        "",
        f"- [{coverage_marker}] AC001 -> {coverage_target}",
        f"- [{coverage_marker}] AC002 -> {coverage_target}",
        "",
        "## Test Plan",
        "",
        "- Run dashboard and export tests.",
    ]) + "\n"
    (root / "quality" / "features" / f"{slug}.md").write_text(quality_content, encoding="utf-8")

    if coverage_done:
        (root / "tests").mkdir(exist_ok=True)
        (root / "tests" / "test_dashboard.py").write_text("# test\n", encoding="utf-8")


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(argv)
    except SystemExit as e:
        code = e.code if e.code is not None else 0
    return code, stdout.getvalue(), stderr.getvalue()


class ExecutionPlanTests(TestCase):
    def test_plan_from_full_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            plan = build_execution_plan("test-feature", root)

            self.assertEqual(plan["feature_id"], "test-feature")
            self.assertEqual(plan["feature_status"], "validated")
            self.assertGreater(len(plan["plan_steps"]), 0)
            self.assertTrue(len(plan["dependency_order"]) > 0)
            self.assertGreater(len(plan["verification_commands"]), 0)
            self.assertIn("rubric_items", plan["grading_rubric"])
            self.assertIn("total_steps", plan["summary"])

    def test_plan_steps_have_required_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            plan = build_execution_plan("test-feature", root)

            for step in plan["plan_steps"]:
                self.assertIn("step_id", step)
                self.assertIn("description", step)
                self.assertIn("mapped_ac_ids", step)
                self.assertIn("dependency_step_ids", step)
                self.assertIn("source_files", step)
                self.assertIn("verification_command", step)
                self.assertIn("acceptance_criteria_text", step)

    def test_plan_dependency_order_includes_all_steps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            plan = build_execution_plan("test-feature", root)
            step_ids = {s["step_id"] for s in plan["plan_steps"]}
            order_ids = set(plan["dependency_order"])
            self.assertEqual(step_ids, order_ids)

    def test_plan_with_blocked_steps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, with_deps=True, tasks_done=False)

            plan = build_execution_plan("test-feature", root)
            blocked = [s for s in plan["plan_steps"] if s.get("blocked")]
            if any("T001" in s.get("dependency_step_ids", []) for s in plan["plan_steps"]):
                self.assertTrue(
                    any(s.get("blocked") for s in plan["plan_steps"]),
                    "Steps with unmet deps should be blocked",
                )

    def test_plan_summary_counts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            plan = build_execution_plan("test-feature", root)
            summary = plan["summary"]
            self.assertIn("total_steps", summary)
            self.assertIn("blocked_steps", summary)
            self.assertIn("completed_steps", summary)
            self.assertIn("acceptance_criteria", summary)
            self.assertGreaterEqual(summary["total_steps"], 0)

    def test_plan_verification_commands(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            plan = build_execution_plan("test-feature", root)
            cmds = plan["verification_commands"]
            self.assertTrue(any("verify matrix" in c for c in cmds))
            self.assertTrue(any("feature trace" in c for c in cmds))

    def test_plan_grading_rubric_structure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            plan = build_execution_plan("test-feature", root)
            rubric = plan["grading_rubric"]
            self.assertEqual(rubric["feature_id"], "test-feature")
            self.assertIn("rubric_items", rubric)
            self.assertIn("pass_count", rubric)
            self.assertIn("total_count", rubric)

    def test_plan_safety_notes_present(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            plan = build_execution_plan("test-feature", root)
            self.assertTrue(len(plan["safety_notes"]) > 0)
            self.assertTrue(any("subprocess" in n for n in plan["safety_notes"]))


class GradingRubricTests(TestCase):
    def test_rubric_with_passing_acs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, ac_done=True, coverage_done=True)

            rubric = build_grading_rubric("test-feature", root)

            self.assertEqual(rubric["feature_id"], "test-feature")
            self.assertGreater(len(rubric["rubric_items"]), 0)

    def test_rubric_items_have_required_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            rubric = build_grading_rubric("test-feature", root)

            for item in rubric["rubric_items"]:
                self.assertIn("ac_id", item)
                self.assertIn("ac_text", item)
                self.assertIn("check_type", item)
                self.assertIn("pass_criteria", item)
                self.assertIn("current_status", item)
                self.assertIn("gap_reason", item)

    def test_rubric_status_fail_when_no_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, ac_done=False, coverage_done=False)

            rubric = build_grading_rubric("test-feature", root)
            ac_items = [i for i in rubric["rubric_items"] if i["check_type"] == "acceptance_criterion"]
            self.assertTrue(
                any(i["current_status"] == "fail" for i in ac_items),
                "ACs without coverage should fail",
            )

    def test_rubric_status_pass_when_ac_done(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, ac_done=True, coverage_done=True)

            rubric = build_grading_rubric("test-feature", root)
            ac_items = [i for i in rubric["rubric_items"] if i["check_type"] == "acceptance_criterion"]
            self.assertTrue(
                all(i["current_status"] == "pass" for i in ac_items),
                "Done ACs with coverage should pass",
            )

    def test_rubric_includes_quality_checks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            rubric = build_grading_rubric("test-feature", root)
            quality_items = [i for i in rubric["rubric_items"] if i["check_type"] == "quality_gates"]
            self.assertGreater(len(quality_items), 0)

    def test_rubric_warns_when_ac_open_with_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, ac_done=False, coverage_done=True)

            rubric = build_grading_rubric("test-feature", root)
            ac_items = [i for i in rubric["rubric_items"] if i["check_type"] == "acceptance_criterion"]
            statuses = {i["current_status"] for i in ac_items}
            self.assertIn("warn", statuses)


class ExecutionLoopTests(TestCase):
    def test_loop_completes_when_all_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, ac_done=True, coverage_done=True, quality_done=True)

            result = run_execution_loop("test-feature", root, max_iterations=3)

            self.assertEqual(result["feature_id"], "test-feature")
            self.assertGreater(len(result["iterations"]), 0)
            self.assertEqual(result["final_status"], "complete")
            self.assertEqual(result["remaining_gaps"], [])

    def test_loop_reports_gaps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, ac_done=False, coverage_done=False)

            result = run_execution_loop("test-feature", root, max_iterations=2)

            self.assertEqual(result["final_status"], "gaps_remaining")
            self.assertGreater(len(result["remaining_gaps"]), 0)

    def test_loop_iteration_structure(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            result = run_execution_loop("test-feature", root, max_iterations=2)

            for iteration in result["iterations"]:
                self.assertIn("iteration", iteration)
                self.assertIn("plan_steps_completed", iteration)
                self.assertIn("grade_results", iteration)
                self.assertIn("gaps_found", iteration)
                self.assertIn("pass_count", iteration)
                self.assertIn("total_count", iteration)

    def test_loop_max_iterations_respected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, ac_done=False, coverage_done=False)

            result = run_execution_loop("test-feature", root, max_iterations=2)
            self.assertEqual(len(result["iterations"]), 2)

    def test_loop_respects_max_limit_bounds(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            result = run_execution_loop("test-feature", root, max_iterations=20)
            self.assertLessEqual(len(result["iterations"]), 10)

    def test_loop_at_least_one_iteration(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            result = run_execution_loop("test-feature", root, max_iterations=0)
            self.assertGreaterEqual(len(result["iterations"]), 1)


class DependencyOrderingTests(TestCase):
    def test_linear_dependency_order(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, with_deps=True)

            plan = build_execution_plan("test-feature", root)
            order = plan["dependency_order"]

            if len(order) >= 2:
                t001_idx = order.index("T001") if "T001" in order else -1
                t002_idx = order.index("T002") if "T002" in order else -1
                if t001_idx >= 0 and t002_idx >= 0:
                    self.assertLess(t001_idx, t002_idx, "T001 should come before T002")

    def test_no_deps_parallel_order(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, with_deps=False)

            plan = build_execution_plan("test-feature", root)
            order = plan["dependency_order"]
            self.assertIn("T001", order)
            self.assertIn("T002", order)


class ErrorCasesTests(TestCase):
    def test_invalid_slug_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with self.assertRaises(InvalidFeatureSlug):
                build_execution_plan("Bad Slug", root)

    def test_missing_bundle_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with self.assertRaises(FeatureBundleNotFoundError):
                build_execution_plan("nonexistent", root)

    def test_missing_bundle_grade_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with self.assertRaises(FeatureBundleNotFoundError):
                build_grading_rubric("nonexistent", root)

    def test_missing_bundle_loop_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with self.assertRaises(FeatureBundleNotFoundError):
                run_execution_loop("nonexistent", root)

    def test_cli_invalid_slug_exit_code_2(self) -> None:
        with TemporaryDirectory() as tmp:
            code, stdout, stderr = run_cli(
                ["execute", "plan", "Bad Slug", tmp, "--json"]
            )
            self.assertEqual(code, 2)
            self.assertIn("Invalid feature slug", stderr)

    def test_cli_missing_bundle_exit_code_1(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            code, stdout, stderr = run_cli(
                ["execute", "plan", "nonexistent", str(root), "--json"]
            )
            self.assertEqual(code, 1)
            self.assertIn("missing", stderr.lower())


class JSONSchemaTests(TestCase):
    def test_plan_json_is_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            plan = build_execution_plan("test-feature", root)
            json_str = render_plan_json(plan)
            parsed = json.loads(json_str)
            self.assertEqual(parsed["feature_id"], "test-feature")
            self.assertIn("plan_steps", parsed)
            self.assertIn("dependency_order", parsed)

    def test_grade_json_is_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            rubric = build_grading_rubric("test-feature", root)
            json_str = render_grade_json(rubric)
            parsed = json.loads(json_str)
            self.assertEqual(parsed["feature_id"], "test-feature")
            self.assertIn("rubric_items", parsed)

    def test_loop_json_is_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            result = run_execution_loop("test-feature", root)
            json_str = render_loop_json(result)
            parsed = json.loads(json_str)
            self.assertEqual(parsed["feature_id"], "test-feature")
            self.assertIn("iterations", parsed)
            self.assertIn("final_status", parsed)
            self.assertIn("remaining_gaps", parsed)

    def test_deterministic_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            first = build_execution_plan("test-feature", root)
            second = build_execution_plan("test-feature", root)
            self.assertEqual(first, second)


class TextRenderingTests(TestCase):
    def test_plan_text_contains_header(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            plan = build_execution_plan("test-feature", root)
            text = render_plan_text(plan)
            self.assertIn("Execution plan:", text)
            self.assertIn("test-feature", text)

    def test_plan_text_contains_steps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            plan = build_execution_plan("test-feature", root)
            text = render_plan_text(plan)
            self.assertIn("Steps:", text)

    def test_grade_text_contains_score(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            rubric = build_grading_rubric("test-feature", root)
            text = render_grade_text(rubric)
            self.assertIn("Grading rubric:", text)
            self.assertIn("pass", text)

    def test_loop_text_contains_iterations(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            result = run_execution_loop("test-feature", root)
            text = render_loop_text(result)
            self.assertIn("Execution loop:", text)
            self.assertIn("Iteration", text)

    def test_loop_text_shows_final_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            result = run_execution_loop("test-feature", root)
            text = render_loop_text(result)
            self.assertIn(result["final_status"], text)


class CLITests(TestCase):
    def test_execute_plan_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            code, stdout, stderr = run_cli(
                ["execute", "plan", "test-feature", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["feature_id"], "test-feature")

    def test_execute_plan_text(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            code, stdout, stderr = run_cli(
                ["execute", "plan", "test-feature", str(root)]
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Execution plan:", stdout)

    def test_execute_grade_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            code, stdout, stderr = run_cli(
                ["execute", "grade", "test-feature", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["feature_id"], "test-feature")

    def test_execute_grade_text(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            code, stdout, stderr = run_cli(
                ["execute", "grade", "test-feature", str(root)]
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Grading rubric:", stdout)

    def test_execute_loop_json_complete(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, ac_done=True, coverage_done=True, quality_done=True)

            code, stdout, stderr = run_cli(
                ["execute", "loop", "test-feature", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["final_status"], "complete")

    def test_execute_loop_json_incomplete(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root, ac_done=False, coverage_done=False)

            code, stdout, stderr = run_cli(
                ["execute", "loop", "test-feature", str(root), "--json"]
            )
            self.assertEqual(code, 1)
            payload = json.loads(stdout)
            self.assertEqual(payload["final_status"], "gaps_remaining")

    def test_execute_loop_text(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            code, stdout, stderr = run_cli(
                ["execute", "loop", "test-feature", str(root)]
            )
            self.assertIn("Execution loop:", stdout)
            self.assertIn("Iteration", stdout)

    def test_execute_loop_max_iterations(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            code, stdout, stderr = run_cli(
                ["execute", "loop", "test-feature", str(root), "--max-iterations", "5", "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertGreaterEqual(len(payload["iterations"]), 1)

    def test_execute_plan_help(self) -> None:
        code, stdout, stderr = run_cli(["execute", "plan", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("--json", stdout)

    def test_execute_grade_help(self) -> None:
        code, stdout, stderr = run_cli(["execute", "grade", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("--json", stdout)

    def test_execute_loop_help(self) -> None:
        code, stdout, stderr = run_cli(["execute", "loop", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("--max-iterations", stdout)


class NoSubprocessTests(TestCase):
    def test_plan_no_subprocess_or_network(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            with patch.object(
                subprocess,
                "run",
                side_effect=AssertionError("subprocess should not run"),
            ), patch.object(
                urllib.request,
                "urlopen",
                side_effect=AssertionError("network should not run"),
            ), patch.object(
                os,
                "getenv",
                side_effect=AssertionError("env should not be read"),
            ):
                plan = build_execution_plan("test-feature", root)
                render_plan_json(plan)
                render_plan_text(plan)

            self.assertEqual(plan["feature_id"], "test-feature")

    def test_grade_no_subprocess_or_network(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            with patch.object(
                subprocess,
                "run",
                side_effect=AssertionError("subprocess should not run"),
            ), patch.object(
                urllib.request,
                "urlopen",
                side_effect=AssertionError("network should not run"),
            ):
                rubric = build_grading_rubric("test-feature", root)
                render_grade_json(rubric)
                render_grade_text(rubric)

            self.assertEqual(rubric["feature_id"], "test-feature")

    def test_loop_no_subprocess_or_network(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_full_feature(root)

            with patch.object(
                subprocess,
                "run",
                side_effect=AssertionError("subprocess should not run"),
            ), patch.object(
                urllib.request,
                "urlopen",
                side_effect=AssertionError("network should not run"),
            ):
                result = run_execution_loop("test-feature", root)
                render_loop_json(result)
                render_loop_text(result)

            self.assertEqual(result["feature_id"], "test-feature")
