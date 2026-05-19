import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

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
from specspine.cli import build_parser
from specspine.workspace import init_workspace


def _setup_workspace(tmp: str) -> Path:
    root = Path(tmp)
    init_workspace(root)
    return root


class TestSupportedFormats(TestCase):
    def test_supported_formats_contains_three_entries(self) -> None:
        self.assertEqual(len(SUPPORTED_FORMATS), 3)

    def test_github_actions_in_supported_formats(self) -> None:
        self.assertIn("github-actions", SUPPORTED_FORMATS)

    def test_gitlab_ci_in_supported_formats(self) -> None:
        self.assertIn("gitlab-ci", SUPPORTED_FORMATS)

    def test_generic_in_supported_formats(self) -> None:
        self.assertIn("generic", SUPPORTED_FORMATS)


class TestPipelineJob(TestCase):
    def test_pipeline_job_as_dict(self) -> None:
        job = PipelineJob(
            name="test",
            steps=("echo hello",),
            description="Test job",
        )
        d = job.as_dict()
        self.assertEqual(d["name"], "test")
        self.assertEqual(d["steps"], ["echo hello"])
        self.assertEqual(d["description"], "Test job")

    def test_pipeline_job_as_dict_without_optional(self) -> None:
        job = PipelineJob(
            name="test",
            steps=("echo hello",),
        )
        d = job.as_dict()
        self.assertEqual(d["name"], "test")
        self.assertNotIn("description", d)
        self.assertNotIn("condition", d)

    def test_pipeline_job_as_dict_with_condition(self) -> None:
        job = PipelineJob(
            name="test",
            steps=("echo hello",),
            condition="always()",
        )
        d = job.as_dict()
        self.assertEqual(d["condition"], "always()")


class TestMergeCondition(TestCase):
    def test_merge_condition_as_dict(self) -> None:
        mc = MergeCondition(id="mc-001", text="test passes", required=True)
        d = mc.as_dict()
        self.assertEqual(d["id"], "mc-001")
        self.assertEqual(d["text"], "test passes")
        self.assertTrue(d["required"])

    def test_merge_condition_optional(self) -> None:
        mc = MergeCondition(id="mc-002", text="optional check", required=False)
        d = mc.as_dict()
        self.assertFalse(d["required"])


class TestSafetyNotes(TestCase):
    def test_safety_notes_is_tuple(self) -> None:
        self.assertIsInstance(SAFETY_NOTES, tuple)

    def test_safety_notes_not_empty(self) -> None:
        self.assertGreater(len(SAFETY_NOTES), 0)

    def test_safety_notes_contains_read_only_note(self) -> None:
        self.assertTrue(
            any("read-only" in note for note in SAFETY_NOTES),
        )

    def test_safety_notes_mentions_acceptance_criteria(self) -> None:
        self.assertTrue(
            any("acceptance criteria" in note.lower() for note in SAFETY_NOTES),
        )


class TestGenerateGithubActions(TestCase):
    def test_returns_string(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIsInstance(result, str)

    def test_contains_workflow_name(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("name: SpecSpine Pipeline", result)

    def test_contains_validate_job(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("validate:", result)

    def test_contains_test_job(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("test:", result)

    def test_contains_coverage_job(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("coverage:", result)

    def test_contains_quality_gates_job(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("quality-gates:", result)

    def test_contains_consistency_job(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("consistency:", result)

    def test_contains_hygiene_job(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("hygiene:", result)

    def test_contains_security_job(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("security:", result)

    def test_validate_step_contains_fusion(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("specspine validate --fusion --features", result)

    def test_test_step_contains_unittest(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("python3 -m unittest discover -s tests", result)

    def test_coverage_step_contains_policy(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("specspine coverage debt . --json --policy", result)

    def test_uses_ubuntu_latest(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("runs-on: ubuntu-latest", result)

    def test_uses_checkout_action(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("actions/checkout@v4", result)

    def test_uses_setup_python_action(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("actions/setup-python@v5", result)

    def test_contains_pull_request_trigger(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("pull_request:", result)

    def test_feature_readiness_job_when_feature_specified(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root, feature_slug="add-dark-mode")
            self.assertIn("feature-readiness:", result)
            self.assertIn("add-dark-mode", result)
            self.assertIn("--require-coverage", result)

    def test_no_feature_readiness_job_when_no_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertNotIn("feature-readiness:", result)

    def test_generated_comment_mentions_review(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_github_actions(root)
            self.assertIn("Review before committing", result)

    def test_deterministic_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result1 = generate_github_actions(root)
            result2 = generate_github_actions(root)
            self.assertEqual(result1, result2)


class TestGenerateGitlabCI(TestCase):
    def test_returns_string(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_gitlab_ci(root)
            self.assertIsInstance(result, str)

    def test_contains_stages(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_gitlab_ci(root)
            self.assertIn("stages:", result)

    def test_contains_validate_job(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_gitlab_ci(root)
            self.assertIn("validate:", result)

    def test_contains_test_job(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_gitlab_ci(root)
            self.assertIn("test:", result)

    def test_contains_coverage_job(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_gitlab_ci(root)
            self.assertIn("coverage:", result)

    def test_uses_python_312_image(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_gitlab_ci(root)
            self.assertIn("python:3.12", result)

    def test_feature_readiness_job_when_feature_specified(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_gitlab_ci(root, feature_slug="add-dark-mode")
            self.assertIn("feature-readiness:", result)
            self.assertIn("add-dark-mode", result)

    def test_deterministic_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result1 = generate_gitlab_ci(root)
            result2 = generate_gitlab_ci(root)
            self.assertEqual(result1, result2)

    def test_contains_script_keyword(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_gitlab_ci(root)
            self.assertIn("script:", result)


class TestGenerateGeneric(TestCase):
    def test_returns_string(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_generic(root)
            self.assertIsInstance(result, str)

    def test_shebang_line(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_generic(root)
            self.assertIn("#!/usr/bin/env bash", result)

    def test_set_euo_pipefail(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_generic(root)
            self.assertIn("set -euo pipefail", result)

    def test_contains_validate_stage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_generic(root)
            self.assertIn("validate", result)

    def test_contains_test_stage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_generic(root)
            self.assertIn("test", result)

    def test_feature_readiness_when_feature_specified(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_generic(root, feature_slug="add-dark-mode")
            self.assertIn("feature-readiness", result)
            self.assertIn("add-dark-mode", result)

    def test_no_feature_readiness_when_no_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_generic(root)
            self.assertNotIn("feature-readiness", result)

    def test_deterministic_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result1 = generate_generic(root)
            result2 = generate_generic(root)
            self.assertEqual(result1, result2)


class TestGeneratePipeline(TestCase):
    def test_returns_dict(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            self.assertIsInstance(result, dict)

    def test_pipeline_type_key(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root, format="github-actions")
            self.assertEqual(result["pipeline_type"], "github-actions")

    def test_pipeline_type_gitlab(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root, format="gitlab-ci")
            self.assertEqual(result["pipeline_type"], "gitlab-ci")

    def test_pipeline_type_generic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root, format="generic")
            self.assertEqual(result["pipeline_type"], "generic")

    def test_jobs_is_tuple(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            self.assertIsInstance(result["jobs"], tuple)

    def test_merge_conditions_is_tuple(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            self.assertIsInstance(result["merge_conditions"], tuple)

    def test_safety_notes_is_tuple(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            self.assertIsInstance(result["safety_notes"], tuple)

    def test_raw_content_is_string(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            self.assertIsInstance(result["raw_content"], str)

    def test_jobs_count_without_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            self.assertEqual(len(result["jobs"]), 7)

    def test_jobs_count_with_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root, feature_slug="add-dark-mode")
            self.assertEqual(len(result["jobs"]), 8)

    def test_merge_conditions_count_without_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            self.assertEqual(len(result["merge_conditions"]), 7)

    def test_merge_conditions_count_with_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root, feature_slug="add-dark-mode")
            self.assertEqual(len(result["merge_conditions"]), 8)

    def test_feature_slug_in_result(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root, feature_slug="my-feature")
            self.assertEqual(result["feature_slug"], "my-feature")

    def test_feature_slug_none_when_not_specified(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            self.assertIsNone(result["feature_slug"])

    def test_invalid_format_raises_value_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            with self.assertRaises(ValueError) as ctx:
                generate_pipeline(root, format="jenkins")
            self.assertIn("Unsupported pipeline format", str(ctx.exception))

    def test_missing_workspace_raises_file_not_found(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(FileNotFoundError):
                generate_pipeline(root)

    def test_default_format_is_github_actions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            self.assertEqual(result["pipeline_type"], "github-actions")


class TestRenderPipelineJson(TestCase):
    def test_returns_valid_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_json(result)
            parsed = json.loads(output)
            self.assertIsInstance(parsed, dict)

    def test_contains_pipeline_type(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_json(result)
            parsed = json.loads(output)
            self.assertIn("pipeline_type", parsed)

    def test_contains_jobs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_json(result)
            parsed = json.loads(output)
            self.assertIn("jobs", parsed)
            self.assertIsInstance(parsed["jobs"], list)

    def test_contains_merge_conditions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_json(result)
            parsed = json.loads(output)
            self.assertIn("merge_conditions", parsed)

    def test_contains_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_json(result)
            parsed = json.loads(output)
            self.assertIn("safety_notes", parsed)

    def test_contains_raw_content(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_json(result)
            parsed = json.loads(output)
            self.assertIn("raw_content", parsed)

    def test_sorted_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_json(result)
            parsed = json.loads(output)
            keys = list(parsed.keys())
            self.assertEqual(keys, sorted(keys))


class TestRenderPipelineYaml(TestCase):
    def test_returns_raw_content_when_available(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_yaml(result)
            self.assertIn("SpecSpine Pipeline", output)

    def test_returns_fallback_when_no_raw_content(self) -> None:
        result = {
            "pipeline_type": "test",
            "jobs": (),
            "merge_conditions": (),
            "safety_notes": (),
        }
        output = render_pipeline_yaml(result)
        self.assertIn("No raw content available", output)


class TestRenderPipelineText(TestCase):
    def test_returns_string(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_text(result)
            self.assertIsInstance(output, str)

    def test_contains_pipeline_type(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_text(result)
            self.assertIn("github-actions", output)

    def test_contains_jobs_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_text(result)
            self.assertIn("Jobs:", output)

    def test_contains_merge_conditions_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_text(result)
            self.assertIn("Merge Conditions:", output)

    def test_contains_safety_notes_section(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_text(result)
            self.assertIn("Safety Notes:", output)

    def test_shows_required_marker(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_text(result)
            self.assertIn("[REQUIRED]", output)

    def test_shows_feature_when_specified(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root, feature_slug="my-feature")
            output = render_pipeline_text(result)
            self.assertIn("Feature: my-feature", output)

    def test_no_feature_line_when_not_specified(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            output = render_pipeline_text(result)
            self.assertNotIn("Feature:", output)


class TestCliGenerate(TestCase):
    def test_generate_help(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["cicd", "generate", "--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_generate_defaults(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            args = parser.parse_args(["cicd", "generate", tmp])
            self.assertEqual(args.format, "github-actions")
            self.assertIsNone(args.feature)
            self.assertIsNone(args.output_dir)
            self.assertFalse(args.json)

    def test_generate_with_format(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            args = parser.parse_args(
                ["cicd", "generate", tmp, "--format", "gitlab-ci"],
            )
            self.assertEqual(args.format, "gitlab-ci")

    def test_generate_with_feature(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            args = parser.parse_args(
                ["cicd", "generate", tmp, "--feature", "add-dark-mode"],
            )
            self.assertEqual(args.feature, "add-dark-mode")

    def test_generate_with_output_dir(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            args = parser.parse_args(
                ["cicd", "generate", tmp, "--output-dir", tmp + "/output"],
            )
            self.assertEqual(args.output_dir, tmp + "/output")

    def test_generate_with_json(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            args = parser.parse_args(
                ["cicd", "generate", tmp, "--json"],
            )
            self.assertTrue(args.json)


class TestCliValidate(TestCase):
    def test_validate_help(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["cicd", "validate", "--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_validate_defaults(self) -> None:
        parser = build_parser()
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            args = parser.parse_args(["cicd", "validate", tmp])
            self.assertFalse(args.json)


class TestCliExitCodes(TestCase):
    def test_generate_success_exit_code(self) -> None:
        from specspine.cli import main
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            exit_code = main(["cicd", "generate", tmp])
            self.assertEqual(exit_code, 0)

    def test_generate_json_exit_code(self) -> None:
        from specspine.cli import main
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            exit_code = main(["cicd", "generate", tmp, "--json"])
            self.assertEqual(exit_code, 0)

    def test_validate_success_exit_code(self) -> None:
        from specspine.cli import main
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            exit_code = main(["cicd", "validate", tmp])
            self.assertEqual(exit_code, 0)

    def test_generate_missing_workspace_exit_code(self) -> None:
        from specspine.cli import main
        with TemporaryDirectory() as tmp:
            exit_code = main(["cicd", "generate", tmp])
            self.assertEqual(exit_code, 2)

    def test_generate_invalid_format_exit_code(self) -> None:
        from specspine.cli import main
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            with self.assertRaises(SystemExit) as ctx:
                main(["cicd", "generate", tmp, "--format", "invalid"])
            self.assertEqual(ctx.exception.code, 2)

    def test_validate_missing_workspace_exit_code(self) -> None:
        from specspine.cli import main
        with TemporaryDirectory() as tmp:
            exit_code = main(["cicd", "validate", tmp])
            self.assertEqual(exit_code, 2)


class TestOutputDirWriting(TestCase):
    def test_writes_github_actions_workflow(self) -> None:
        from specspine.cli import main
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "output"
            exit_code = main(
                [
                    "cicd", "generate", tmp,
                    "--format", "github-actions",
                    "--output-dir", str(output_dir),
                ],
            )
            self.assertEqual(exit_code, 0)
            workflow_path = output_dir / ".github" / "workflows" / "specspine.yml"
            self.assertTrue(workflow_path.exists())

    def test_writes_gitlab_ci(self) -> None:
        from specspine.cli import main
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "output"
            exit_code = main(
                [
                    "cicd", "generate", tmp,
                    "--format", "gitlab-ci",
                    "--output-dir", str(output_dir),
                ],
            )
            self.assertEqual(exit_code, 0)
            ci_path = output_dir / ".gitlab-ci.yml"
            self.assertTrue(ci_path.exists())

    def test_writes_generic_shell(self) -> None:
        from specspine.cli import main
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "output"
            exit_code = main(
                [
                    "cicd", "generate", tmp,
                    "--format", "generic",
                    "--output-dir", str(output_dir),
                ],
            )
            self.assertEqual(exit_code, 0)
            shell_path = output_dir / "specspine-pipeline.sh"
            self.assertTrue(shell_path.exists())

    def test_force_overwrites(self) -> None:
        from specspine.cli import main
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            output_dir = Path(tmp) / "output"
            main(
                [
                    "cicd", "generate", tmp,
                    "--format", "github-actions",
                    "--output-dir", str(output_dir),
                ],
            )
            exit_code = main(
                [
                    "cicd", "generate", tmp,
                    "--format", "github-actions",
                    "--output-dir", str(output_dir),
                    "--force",
                ],
            )
            self.assertEqual(exit_code, 0)


class TestReadOnlySafety(TestCase):
    def test_generate_no_network_calls(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            generate_github_actions(root)
            generate_gitlab_ci(root)
            generate_generic(root)

    def test_generate_no_subprocess(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            generate_pipeline(root, format="github-actions")
            generate_pipeline(root, format="gitlab-ci")
            generate_pipeline(root, format="generic")

    def test_generate_no_token_reads(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _setup_workspace(tmp)
            result = generate_pipeline(root)
            raw = result.get("raw_content", "")
            self.assertNotIn("GITHUB_TOKEN", raw)
            self.assertNotIn("CI_TOKEN", raw)
