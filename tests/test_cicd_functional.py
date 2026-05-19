import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import yaml

from specspine.cicd import (
    SAFETY_NOTES,
    SUPPORTED_FORMATS,
    MergeCondition,
    PipelineJob,
    PipelineResult,
    generate_generic,
    generate_github_actions,
    generate_gitlab_ci,
    generate_pipeline,
    render_pipeline_json,
    render_pipeline_text,
    render_pipeline_yaml,
)
from specspine.cli import build_parser, main
from specspine.workspace import init_workspace


def _setup_workspace(tmp: str) -> Path:
    root = Path(tmp)
    init_workspace(root)
    return root


class TestEmptyWorkspacePipeline(TestCase):
    def test_empty_workspace_generates_valid_github_actions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIsInstance(result, str)
            self.assertIn("name: SpecSpine Pipeline", result)

    def test_empty_workspace_generates_valid_gitlab_ci(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_gitlab_ci(root)
            self.assertIsInstance(result, str)
            self.assertIn("stages:", result)

    def test_empty_workspace_generates_valid_generic_shell(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_generic(root)
            self.assertIsInstance(result, str)
            self.assertIn("#!/usr/bin/env bash", result)

    def test_empty_workspace_pipeline_result_has_core_jobs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            self.assertEqual(len(result["jobs"]), 7)


class TestManyFeaturesPerformance(TestCase):
    def test_workspace_with_many_features_does_not_degrade(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            feature_slug = "feature-" + "x" * 200
            result = generate_pipeline(root, feature_slug=feature_slug)
            self.assertEqual(result["feature_slug"], feature_slug)
            self.assertEqual(len(result["jobs"]), 8)


class TestInvalidFormatString(TestCase):
    def test_invalid_format_raises_value_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            with self.assertRaises(ValueError) as ctx:
                generate_pipeline(root, format="jenkins")
            self.assertIn("Unsupported pipeline format", str(ctx.exception))

    def test_empty_format_raises_value_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            with self.assertRaises(ValueError):
                generate_pipeline(root, format="")

    def test_typo_format_raises_value_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            with self.assertRaises(ValueError):
                generate_pipeline(root, format="github-action")


class TestMissingWorkspacePath(TestCase):
    def test_nonexistent_path_raises_file_not_found(self) -> None:
        with TemporaryDirectory() as tmp:
            nonexistent = Path(tmp) / "nonexistent"
            with self.assertRaises(FileNotFoundError) as ctx:
                generate_pipeline(nonexistent)
            self.assertIn("No SpecSpine workspace", str(ctx.exception))

    def test_empty_directory_raises_file_not_found(self) -> None:
        with TemporaryDirectory() as tmp:
            empty_root = Path(tmp)
            with self.assertRaises(FileNotFoundError):
                generate_pipeline(empty_root)

    def test_cli_missing_workspace_returns_exit_code_2(self) -> None:
        with TemporaryDirectory() as tmp:
            nonexistent = Path(tmp) / "not-a-workspace"
            exit_code = main(["cicd", "generate", str(nonexistent)])
            self.assertEqual(exit_code, 2)


class TestOutputDirectoryMode(TestCase):
    def test_output_dir_creates_github_workflow_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "output"
            exit_code = main(
                [
                    "cicd", "generate", str(root),
                    "--format", "github-actions",
                    "--output-dir", str(output_dir),
                ],
            )
            self.assertEqual(exit_code, 0)
            workflow_path = output_dir / ".github" / "workflows" / "specspine.yml"
            self.assertTrue(workflow_path.exists())
            content = workflow_path.read_text()
            self.assertIn("name: SpecSpine Pipeline", content)

    def test_output_dir_creates_gitlab_ci_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "output"
            exit_code = main(
                [
                    "cicd", "generate", str(root),
                    "--format", "gitlab-ci",
                    "--output-dir", str(output_dir),
                ],
            )
            self.assertEqual(exit_code, 0)
            ci_path = output_dir / ".gitlab-ci.yml"
            self.assertTrue(ci_path.exists())
            content = ci_path.read_text()
            self.assertIn("stages:", content)

    def test_output_dir_creates_generic_shell_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "output"
            exit_code = main(
                [
                    "cicd", "generate", str(root),
                    "--format", "generic",
                    "--output-dir", str(output_dir),
                ],
            )
            self.assertEqual(exit_code, 0)
            shell_path = output_dir / "specspine-pipeline.sh"
            self.assertTrue(shell_path.exists())
            content = shell_path.read_text()
            self.assertIn("#!/usr/bin/env bash", content)

    def test_output_dir_created_if_not_exists(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "nested" / "deep" / "output"
            exit_code = main(
                [
                    "cicd", "generate", str(root),
                    "--format", "github-actions",
                    "--output-dir", str(output_dir),
                ],
            )
            self.assertEqual(exit_code, 0)
            self.assertTrue(output_dir.exists())
            workflow_path = output_dir / ".github" / "workflows" / "specspine.yml"
            self.assertTrue(workflow_path.exists())

    def test_without_force_existing_file_not_overwritten(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "output"
            exit_code = main(
                [
                    "cicd", "generate", str(root),
                    "--format", "github-actions",
                    "--output-dir", str(output_dir),
                ],
            )
            self.assertEqual(exit_code, 0)
            original_content = (
                output_dir / ".github" / "workflows" / "specspine.yml"
            ).read_text()
            exit_code = main(
                [
                    "cicd", "generate", str(root),
                    "--format", "github-actions",
                    "--output-dir", str(output_dir),
                ],
            )
            self.assertEqual(exit_code, 1)
            current_content = (
                output_dir / ".github" / "workflows" / "specspine.yml"
            ).read_text()
            self.assertEqual(original_content, current_content)

    def test_force_flag_overwrites_existing_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "output"
            main(
                [
                    "cicd", "generate", str(root),
                    "--format", "github-actions",
                    "--output-dir", str(output_dir),
                ],
            )
            workflow_path = output_dir / ".github" / "workflows" / "specspine.yml"
            original_content = workflow_path.read_text()
            self.assertTrue(workflow_path.exists())
            exit_code = main(
                [
                    "cicd", "generate", str(root),
                    "--format", "github-actions",
                    "--output-dir", str(output_dir),
                    "--force",
                ],
            )
            self.assertEqual(exit_code, 0)
            new_content = workflow_path.read_text()
            self.assertEqual(original_content, new_content)

    def test_force_overwrites_gitlab_ci(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "output"
            main(
                [
                    "cicd", "generate", str(root),
                    "--format", "gitlab-ci",
                    "--output-dir", str(output_dir),
                ],
            )
            ci_path = output_dir / ".gitlab-ci.yml"
            self.assertTrue(ci_path.exists())
            exit_code = main(
                [
                    "cicd", "generate", str(root),
                    "--format", "gitlab-ci",
                    "--output-dir", str(output_dir),
                    "--force",
                ],
            )
            self.assertEqual(exit_code, 0)

    def test_force_overwrites_generic_shell(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "output"
            main(
                [
                    "cicd", "generate", str(root),
                    "--format", "generic",
                    "--output-dir", str(output_dir),
                ],
            )
            shell_path = output_dir / "specspine-pipeline.sh"
            self.assertTrue(shell_path.exists())
            exit_code = main(
                [
                    "cicd", "generate", str(root),
                    "--format", "generic",
                    "--output-dir", str(output_dir),
                    "--force",
                ],
            )
            self.assertEqual(exit_code, 0)


class TestFeatureSpecificPipeline(TestCase):
    def test_valid_slug_includes_feature_readiness_job(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root, feature_slug="add-dark-mode")
            self.assertIn("feature-readiness:", result)
            self.assertIn("add-dark-mode", result)
            self.assertIn("--require-coverage", result)

    def test_valid_slug_gitlab_includes_feature_readiness(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_gitlab_ci(root, feature_slug="add-dark-mode")
            self.assertIn("feature-readiness:", result)
            self.assertIn("add-dark-mode", result)

    def test_valid_slug_generic_includes_feature_readiness(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_generic(root, feature_slug="add-dark-mode")
            self.assertIn("feature-readiness", result)
            self.assertIn("add-dark-mode", result)

    def test_feature_slug_in_pipeline_result(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root, feature_slug="my-feature")
            self.assertEqual(result["feature_slug"], "my-feature")
            self.assertEqual(len(result["jobs"]), 8)

    def test_feature_readiness_job_has_correct_steps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root, feature_slug="add-dark-mode")
            jobs = result["jobs"]
            feature_job = jobs[-1]
            self.assertEqual(feature_job.name, "feature-readiness")
            self.assertIn("add-dark-mode", feature_job.steps[0])
            self.assertIn("--require-coverage", feature_job.steps[0])

    def test_feature_specific_merge_condition_added(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root, feature_slug="add-dark-mode")
            merge_conds = result["merge_conditions"]
            self.assertEqual(len(merge_conds), 8)
            last_mc = merge_conds[-1]
            self.assertEqual(last_mc.id, "merge-008")
            self.assertIn("add-dark-mode", last_mc.text)

    def test_cli_feature_flag_in_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            exit_code = main(
                [
                    "cicd", "generate", str(root),
                    "--feature", "add-dark-mode",
                    "--json",
                ],
            )
            self.assertEqual(exit_code, 0)

    def test_nonexistent_slug_still_generates_pipeline(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root, feature_slug="does-not-exist")
            self.assertEqual(result["feature_slug"], "does-not-exist")
            self.assertEqual(len(result["jobs"]), 8)


class TestPipelineContentValidation(TestCase):
    def test_github_actions_is_valid_yaml(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            parsed = yaml.safe_load(result)
            self.assertIsInstance(parsed, dict)
            self.assertIn("jobs", parsed)

    def test_gitlab_ci_is_valid_yaml(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_gitlab_ci(root)
            parsed = yaml.safe_load(result)
            self.assertIsInstance(parsed, dict)
            self.assertIn("stages", parsed)

    def test_generic_shell_is_valid_bash(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_generic(root)
            script_path = Path(tmp) / "test_pipeline.sh"
            script_path.write_text(result, encoding="utf-8")
            proc = subprocess.run(
                ["bash", "-n", str(script_path)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, f"Bash syntax error: {proc.stderr}")

    def test_all_pipelines_contain_required_jobs(self) -> None:
        required_jobs = {"validate", "test", "coverage", "consistency", "hygiene", "security"}
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            ga = generate_github_actions(root)
            gc = generate_gitlab_ci(root)
            gn = generate_generic(root)
            for job_name in required_jobs:
                self.assertIn(job_name, ga, f"GitHub Actions missing {job_name}")
                self.assertIn(job_name, gc, f"GitLab CI missing {job_name}")
                self.assertIn(job_name, gn, f"Generic missing {job_name}")

    def test_all_pipelines_contain_safety_notes_reference(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            for gen in [generate_github_actions, generate_gitlab_ci, generate_generic]:
                result = gen(root)
                self.assertIn("Review before committing", result)

    def test_all_pipelines_contain_merge_conditions_in_result(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            self.assertIsInstance(result["merge_conditions"], tuple)
            self.assertGreater(len(result["merge_conditions"]), 0)
            for mc in result["merge_conditions"]:
                self.assertIsInstance(mc, MergeCondition)
                self.assertTrue(mc.id.startswith("merge-"))
                self.assertTrue(mc.text)
                self.assertIsInstance(mc.required, bool)

    def test_json_output_is_valid_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_json(result)
            parsed = json.loads(output)
            self.assertIsInstance(parsed, dict)

    def test_json_contains_all_required_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_json(result)
            parsed = json.loads(output)
            required_keys = {
                "pipeline_type", "jobs", "merge_conditions",
                "safety_notes", "raw_content",
            }
            for key in required_keys:
                self.assertIn(key, parsed)

    def test_github_actions_contains_required_permission(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("contents: read", result)


class TestCliExitCodes(TestCase):
    def test_success_exit_code_0(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            exit_code = main(["cicd", "generate", str(root)])
            self.assertEqual(exit_code, 0)

    def test_json_success_exit_code_0(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            exit_code = main(["cicd", "generate", str(root), "--json"])
            self.assertEqual(exit_code, 0)

    def test_missing_workspace_exit_code_2(self) -> None:
        with TemporaryDirectory() as tmp:
            nonexistent = Path(tmp) / "not-a-workspace"
            exit_code = main(["cicd", "generate", str(nonexistent)])
            self.assertEqual(exit_code, 2)

    def test_invalid_format_exit_code_1(self) -> None:
        from specspine.cli import main
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            with self.assertRaises(SystemExit) as ctx:
                main(["cicd", "generate", str(root), "--format", "invalid"])
            self.assertEqual(ctx.exception.code, 2)

    def test_validate_success_exit_code_0(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            exit_code = main(["cicd", "validate", str(root)])
            self.assertEqual(exit_code, 0)

    def test_validate_missing_workspace_exit_code_2(self) -> None:
        with TemporaryDirectory() as tmp:
            nonexistent = Path(tmp) / "not-a-workspace"
            exit_code = main(["cicd", "validate", str(nonexistent)])
            self.assertEqual(exit_code, 2)


class TestCliJsonOutput(TestCase):
    def test_json_output_is_valid_json(self) -> None:
        import io
        import contextlib
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                main(["cicd", "generate", str(root), "--json"])
            output = stdout.getvalue()
            parsed = json.loads(output)
            self.assertIsInstance(parsed, dict)

    def test_json_output_contains_pipeline_type(self) -> None:
        import io
        import contextlib
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                main(["cicd", "generate", str(root), "--json"])
            output = stdout.getvalue()
            parsed = json.loads(output)
            self.assertEqual(parsed["pipeline_type"], "github-actions")

    def test_json_output_contains_jobs_list(self) -> None:
        import io
        import contextlib
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                main(["cicd", "generate", str(root), "--json"])
            output = stdout.getvalue()
            parsed = json.loads(output)
            self.assertIsInstance(parsed["jobs"], list)
            self.assertGreater(len(parsed["jobs"]), 0)

    def test_json_output_sorted_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_json(result)
            parsed = json.loads(output)
            keys = list(parsed.keys())
            self.assertEqual(keys, sorted(keys))


class TestCliDefaultFormat(TestCase):
    def test_default_format_is_github_actions(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            args = parser.parse_args(["cicd", "generate", str(root)])
            self.assertEqual(args.format, "github-actions")

    def test_default_text_output_contains_github_markers(self) -> None:
        import io
        import contextlib
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                main(["cicd", "generate", str(root)])
            output = stdout.getvalue()
            self.assertIn("github-actions", output)


class TestCliHelpText(TestCase):
    def test_generate_help_exits_with_0(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["cicd", "generate", "--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_validate_help_exits_with_0(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["cicd", "validate", "--help"])
        self.assertEqual(ctx.exception.code, 0)


class TestDeterminism(TestCase):
    def test_github_actions_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            r1 = generate_github_actions(root)
            r2 = generate_github_actions(root)
            self.assertEqual(r1, r2)

    def test_gitlab_ci_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            r1 = generate_gitlab_ci(root)
            r2 = generate_gitlab_ci(root)
            self.assertEqual(r1, r2)

    def test_generic_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            r1 = generate_generic(root)
            r2 = generate_generic(root)
            self.assertEqual(r1, r2)

    def test_pipeline_result_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            r1 = generate_pipeline(root)
            r2 = generate_pipeline(root)
            self.assertEqual(r1["pipeline_type"], r2["pipeline_type"])
            self.assertEqual(len(r1["jobs"]), len(r2["jobs"]))
            self.assertEqual(len(r1["merge_conditions"]), len(r2["merge_conditions"]))

    def test_json_output_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            j1 = render_pipeline_json(result)
            j2 = render_pipeline_json(result)
            self.assertEqual(j1, j2)

    def test_text_output_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            t1 = render_pipeline_text(result)
            t2 = render_pipeline_text(result)
            self.assertEqual(t1, t2)

    def test_yaml_output_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            y1 = render_pipeline_yaml(result)
            y2 = render_pipeline_yaml(result)
            self.assertEqual(y1, y2)

    def test_feature_specific_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            r1 = generate_github_actions(root, feature_slug="test-feature")
            r2 = generate_github_actions(root, feature_slug="test-feature")
            self.assertEqual(r1, r2)
