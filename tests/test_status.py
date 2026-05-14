import json
import os
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.adapters import ADAPTER_SPECS, AdapterStatus
from specspine.cli import main
from specspine.fusion import init_fusion_workspace
from specspine.status import build_status, render_status_text
from specspine.workspace import init_workspace


def write_status_feature_bundle(
    root: Path,
    slug: str = "add-dark-mode",
    *,
    status: str = "validated",
    include_quality: bool = True,
    include_coverage: bool = False,
    open_task: bool = False,
    priority: str | None = None,
    owner: str | None = None,
) -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    spec_metadata_lines = []
    if priority is not None:
        spec_metadata_lines.append(f"Priority: {priority}")
    if owner is not None:
        spec_metadata_lines.append(f"Owner: {owner}")
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Add dark mode",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                *spec_metadata_lines,
                "",
                "## Acceptance Criteria",
                "",
                "- [x] Users can enable dark mode.",
                "- [x] Users can return to light mode.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    task_marker = " " if open_task else "x"
    (root / "execution" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Add dark mode Execution",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
                "",
                "## Tasks",
                "",
                "- [x] Implement theme storage.",
                f"- [{task_marker}] Add theme tests.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    if include_quality:
        coverage_lines: list[str] = []
        if include_coverage:
            target = root / "tests" / "status_coverage.py"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# status coverage target\n", encoding="utf-8")
            coverage_lines = [
                "",
                "## Test Coverage",
                "",
                "- [x] AC001 -> tests/status_coverage.py::test_enable_dark_mode",
                "- [x] AC002 -> tests/status_coverage.py::test_return_to_light_mode",
            ]
        (root / "quality" / "features" / f"{slug}.md").write_text(
            "\n".join(
                [
                    "# Add dark mode Quality",
                    "",
                    f"Feature ID: {slug}",
                    f"Status: {status}",
                    "",
                    "## Required Checks",
                    "",
                    "- [x] Unit tests pass.",
                    "- [x] Documentation updated.",
                    "",
                    "## Test Plan",
                    "",
                    "- Run `python -m unittest`.",
                    "",
                    "## Release Readiness",
                    "",
                    "- [x] Reviewer gate passes.",
                    "- [x] No release blockers remain.",
                    *coverage_lines,
                ]
            )
            + "\n",
            encoding="utf-8",
        )


def fake_available_adapters() -> list[AdapterStatus]:
    return [
        AdapterStatus(
            key="openspec",
            display_name="OpenSpec",
            available=True,
            detail="fake openspec available",
            version="1.0.0",
            command="openspec",
            install_hint="install openspec",
            upstream_url="https://example.test/openspec",
        ),
        AdapterStatus(
            key="speckit",
            display_name="Spec Kit",
            available=True,
            detail="fake speckit available",
            version="2.0.0",
            command="specify",
            install_hint="install speckit",
            upstream_url="https://example.test/speckit",
        ),
        AdapterStatus(
            key="superpowers",
            display_name="Superpowers",
            available=True,
            detail="fake superpowers available",
            version="3.0.0",
            command=None,
            install_hint="install superpowers",
            upstream_url="https://example.test/superpowers",
        ),
    ]


def fake_available_adapter_probe(keys: list[str]) -> list[AdapterStatus]:
    return [
        AdapterStatus(
            key=key,
            display_name=ADAPTER_SPECS[key].display_name,
            available=True,
            detail=f"fake {key} available",
            version="1.0.0",
            command=ADAPTER_SPECS[key].command,
            install_hint=ADAPTER_SPECS[key].install_hint,
            upstream_url=ADAPTER_SPECS[key].upstream_url,
        )
        for key in keys
    ]


def write_status_feature_filter_set(root: Path) -> None:
    write_status_feature_bundle(
        root,
        slug="zeta-planned",
        status="planned",
        priority="low",
        owner="Dana",
    )
    write_status_feature_bundle(
        root,
        slug="alpha-validated",
        status="validated",
        priority="high",
        owner="Ada",
    )
    write_status_feature_bundle(
        root,
        slug="middle-implemented",
        status="implemented",
        include_quality=False,
        open_task=True,
        priority="medium",
        owner="Dana",
    )


def feature_summary_slugs(payload: dict[str, object]) -> list[str]:
    summaries = payload["feature_summaries"]
    assert isinstance(summaries, list)
    return [str(summary["slug"]) for summary in summaries]


class StatusTests(TestCase):
    def test_status_for_plain_workspace_does_not_probe_adapters(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            def fail_probe() -> list[AdapterStatus]:
                raise AssertionError("adapter probe should not run")

            status = build_status(root, adapter_probe=fail_probe)

            self.assertTrue(status["workspace"]["complete"])
            self.assertFalse(status["fusion"]["complete"])
            self.assertNotIn("adapters", status)
            self.assertFalse(status["upstreams"]["openspec"]["enabled"])

    def test_plain_workspace_recommendations_point_to_fuse(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            status = build_status(root)

            self.assertTrue(status["workspace"]["complete"])
            self.assertFalse(status["fusion"]["complete"])
            self.assertTrue(
                any("specspine fuse" in item for item in status["recommendations"])
            )
            self.assertFalse(
                any("compact context packet" in item for item in status["recommendations"])
            )

    def test_status_for_fusion_workspace_records_enabled_upstreams(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex", include_speckit=False)

            status = build_status(root)

            self.assertTrue(status["workspace"]["complete"])
            self.assertTrue(status["fusion"]["complete"])
            self.assertTrue(status["upstreams"]["openspec"]["enabled"])
            self.assertFalse(status["upstreams"]["speckit"]["enabled"])
            self.assertTrue(status["upstreams"]["superpowers"]["enabled"])
            self.assertTrue(status["artifacts"][".specspine/fusion.yaml"]["exists"])

    def test_status_json_cli_output_is_parseable(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["root"], str(root.resolve()))
            self.assertTrue(payload["workspace"]["complete"])
            self.assertIn("artifacts", payload)
            self.assertIn("recommendations", payload)
            self.assertNotIn("adapters", payload)
            self.assertNotIn("validation", payload)
            self.assertNotIn("feature_summaries", payload)

    def test_status_json_cli_can_include_feature_summaries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--json", "--feature-summaries"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertIn("feature_summaries", payload)
            self.assertEqual(len(payload["feature_summaries"]), 1)
            summary = payload["feature_summaries"][0]
            self.assertEqual(
                set(summary),
                {
                    "blocking_checks",
                    "complete",
                    "feature_id",
                    "gaps",
                    "missing_files",
                    "next_actions",
                    "owner",
                    "priority",
                    "ready",
                    "ready_summary",
                    "recommended_commands",
                    "slug",
                    "status",
                    "tasks_summary",
                },
            )
            self.assertEqual(summary["feature_id"], "add-dark-mode")
            self.assertEqual(summary["slug"], "add-dark-mode")
            self.assertEqual(summary["status"], "validated")
            self.assertEqual(summary["priority"], "unknown")
            self.assertEqual(summary["owner"], "unassigned")
            self.assertTrue(summary["complete"])
            self.assertTrue(summary["ready"])
            self.assertEqual(summary["missing_files"], [])
            self.assertEqual(summary["tasks_summary"], {"done": 2, "open": 0, "total": 2})
            self.assertEqual(summary["ready_summary"], {"fail": 0, "pass": 9, "total": 9})
            self.assertEqual(summary["gaps"], 0)
            self.assertEqual(summary["blocking_checks"], 0)
            self.assertEqual(
                summary["next_actions"],
                ["Review, merge, or archive the ready feature bundle."],
            )
            self.assertIn(
                "specspine feature handoff add-dark-mode . --json",
                summary["recommended_commands"],
            )

    def test_status_json_feature_summaries_can_require_coverage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-require-coverage",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            summary = payload["feature_summaries"][0]
            self.assertTrue(summary["coverage_required"])
            self.assertFalse(summary["ready"])
            self.assertEqual(summary["ready_summary"], {"fail": 1, "pass": 9, "total": 10})
            self.assertEqual(summary["blocking_checks"], 1)
            self.assertTrue(
                any(
                    "feature.test_coverage" in action
                    for action in summary["next_actions"]
                )
            )

    def test_status_feature_require_coverage_ready_filter_uses_coverage_gate(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(
                root,
                slug="covered-feature",
                include_coverage=True,
            )
            write_status_feature_bundle(root, slug="missing-coverage")
            default_ready_output = StringIO()
            ready_output = StringIO()
            not_ready_output = StringIO()

            with redirect_stdout(default_ready_output):
                default_ready_returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-ready",
                        "yes",
                        "--feature-sort",
                        "slug",
                    ]
                )
            with redirect_stdout(ready_output):
                ready_returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-require-coverage",
                        "--feature-ready",
                        "yes",
                        "--feature-sort",
                        "slug",
                    ]
                )
            with redirect_stdout(not_ready_output):
                not_ready_returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-require-coverage",
                        "--feature-ready",
                        "no",
                        "--feature-sort",
                        "slug",
                    ]
                )

            self.assertEqual(default_ready_returncode, 0)
            self.assertEqual(ready_returncode, 0)
            self.assertEqual(not_ready_returncode, 0)
            self.assertEqual(
                feature_summary_slugs(json.loads(default_ready_output.getvalue())),
                ["covered-feature", "missing-coverage"],
            )
            self.assertEqual(
                feature_summary_slugs(json.loads(ready_output.getvalue())),
                ["covered-feature"],
            )
            self.assertEqual(
                feature_summary_slugs(json.loads(not_ready_output.getvalue())),
                ["missing-coverage"],
            )

    def test_status_json_cli_validate_includes_validation_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            output = StringIO()

            def fail_probe(keys: list[str]) -> list[AdapterStatus]:
                raise AssertionError("adapter probe should not run")

            with patch("specspine.cli.probe_adapters", side_effect=fail_probe):
                with redirect_stdout(output):
                    returncode = main(["status", str(root), "--json", "--validate"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertIn("validation", payload)
            validation = payload["validation"]
            self.assertTrue(validation["ok"])
            self.assertIn("summary", validation)
            self.assertIn("failed_checks", validation)
            self.assertNotIn("warning_checks", validation)
            self.assertEqual(validation["failed_checks"], [])
            self.assertEqual(
                validation["included"],
                {
                    "workspace": True,
                    "fusion": True,
                    "features": True,
                    "adapters": False,
                },
            )

    def test_status_json_cli_validate_preserves_feature_summaries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--validate",
                        "--feature-summaries",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertIn("validation", payload)
            self.assertIn("feature_summaries", payload)
            self.assertEqual(payload["feature_summaries"][0]["slug"], "add-dark-mode")

    def test_status_json_cli_validate_can_include_warning_checks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            output = StringIO()

            def fail_probe(keys: list[str]) -> list[AdapterStatus]:
                raise AssertionError("adapter probe should not run")

            with patch("specspine.cli.probe_adapters", side_effect=fail_probe):
                with redirect_stdout(output):
                    returncode = main(
                        [
                            "status",
                            str(root),
                            "--json",
                            "--validate",
                            "--validation-warnings",
                        ]
                    )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            warning_checks = payload["validation"]["warning_checks"]
            self.assertTrue(warning_checks)
            self.assertIn(
                "workspace.placeholder:specs/product.md",
                {check["id"] for check in warning_checks},
            )
            self.assertTrue(
                all(check["status"] == "warn" for check in warning_checks)
            )

    def test_status_json_validation_warnings_empty_when_no_warnings(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            replacements = {
                "specs/intent.md": "# Intent\n\nRepository-specific intent is documented.\n",
                "specs/product.md": "# Product Spec\n\nRepository-specific scope is documented.\n",
                "specs/architecture.md": "# Architecture\n\nRepository-specific design is documented.\n",
                "execution/plan.md": "# Execution Plan\n\nRepository-specific plan is documented.\n",
                "execution/tasks.md": "# Tasks\n\n- [x] Repository-specific task is complete.\n",
                "quality/checklist.md": "# Quality Checklist\n\n- [x] Repository-specific gate is complete.\n",
                "quality/review.md": "# Review Notes\n\nRepository-specific review is documented.\n",
            }
            for relative_path, content in replacements.items():
                (root / relative_path).write_text(content, encoding="utf-8")
            output = StringIO()

            def fail_probe(keys: list[str]) -> list[AdapterStatus]:
                raise AssertionError("adapter probe should not run")

            with patch("specspine.cli.probe_adapters", side_effect=fail_probe):
                with redirect_stdout(output):
                    returncode = main(
                        [
                            "status",
                            str(root),
                            "--json",
                            "--validate",
                            "--validation-warnings",
                        ]
                    )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["validation"]["warning_checks"], [])

    def test_status_validation_warnings_requires_validate(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()
            errors = StringIO()

            with redirect_stdout(output), redirect_stderr(errors):
                returncode = main(["status", str(root), "--validation-warnings"])

            self.assertEqual(returncode, 2)
            self.assertEqual(output.getvalue(), "")
            self.assertIn("--validation-warnings requires --validate.", errors.getvalue())

    def test_status_text_cli_validate_includes_brief_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--validate"])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("Validation:", text)
            self.assertIn("Result: failed", text)
            self.assertIn("Summary: pass=", text)
            self.assertIn("fusion.required_file:.specspine/fusion.yaml", text)
            self.assertNotIn("workspace.required_file:.specspine/spine.yaml", text)
            self.assertNotIn("fusion.integration_mode", text)
            self.assertNotIn("Warning checks:", text)

    def test_status_text_validation_warnings_show_warning_ids_only_with_flag(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            default_output = StringIO()
            warnings_output = StringIO()

            with redirect_stdout(default_output):
                default_returncode = main(["status", str(root), "--validate"])
            with redirect_stdout(warnings_output):
                warnings_returncode = main(
                    ["status", str(root), "--validate", "--validation-warnings"]
                )

            self.assertEqual(default_returncode, 0)
            self.assertEqual(warnings_returncode, 0)
            self.assertNotIn("Warning checks:", default_output.getvalue())
            text = warnings_output.getvalue()
            self.assertIn("Warning checks:", text)
            self.assertIn("workspace.placeholder:specs/product.md", text)

    def test_status_text_feature_summaries_are_opt_in(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(root)
            default_output = StringIO()
            summary_output = StringIO()

            with redirect_stdout(default_output):
                default_returncode = main(["status", str(root)])
            with redirect_stdout(summary_output):
                summary_returncode = main(["status", str(root), "--feature-summaries"])

            self.assertEqual(default_returncode, 0)
            self.assertEqual(summary_returncode, 0)
            self.assertNotIn("Feature summaries:", default_output.getvalue())
            text = summary_output.getvalue()
            self.assertIn("Feature summaries:", text)
            self.assertIn(
                "add-dark-mode - status=validated priority=unknown "
                "owner=unassigned ready=yes tasks=2/0 gaps=0 blocking=0",
                text,
            )
            self.assertNotIn("coverage=", text)
            self.assertNotIn("feature.test_coverage", text)
            self.assertIn("next: Review, merge, or archive the ready feature bundle.", text)

    def test_status_text_feature_summaries_show_coverage_requirement(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "status",
                        str(root),
                        "--feature-summaries",
                        "--feature-require-coverage",
                    ]
                )

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn(
                "add-dark-mode - status=validated priority=unknown "
                "owner=unassigned ready=no coverage=yes tasks=2/0 gaps=0 blocking=1",
                text,
            )
            self.assertIn("feature.test_coverage", text)


    def test_status_feature_summary_reports_partial_bundle_actions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(
                root,
                status="implemented",
                include_quality=False,
                open_task=True,
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--json", "--feature-summaries"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            summary = payload["feature_summaries"][0]
            self.assertFalse(summary["complete"])
            self.assertFalse(summary["ready"])
            self.assertEqual(summary["tasks_summary"], {"done": 1, "open": 1, "total": 2})
            self.assertIn("quality/features/add-dark-mode.md", summary["missing_files"])
            self.assertGreater(summary["gaps"], 0)
            self.assertGreater(summary["blocking_checks"], 0)
            self.assertTrue(
                any("Add missing peer file(s)" in action for action in summary["next_actions"])
            )

    def test_status_feature_summary_handles_invalid_slug_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
            (root / "specs" / "features" / "BadSlug.md").write_text(
                "# Bad slug\n\nFeature ID: BadSlug\nStatus: proposed\n",
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--json", "--feature-summaries"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            summary = payload["feature_summaries"][0]
            self.assertEqual(summary["slug"], "BadSlug")
            self.assertEqual(summary["status"], "invalid")
            self.assertFalse(summary["ready"])
            self.assertEqual(summary["blocking_checks"], 1)
            self.assertIn("Invalid feature slug", summary["next_actions"][0])

    def test_status_feature_status_filter_accepts_invalid_and_unknown(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
            (root / "specs" / "features" / "BadSlug.md").write_text(
                "# Bad slug\n\nFeature ID: BadSlug\nStatus: proposed\n",
                encoding="utf-8",
            )
            (root / "specs" / "features" / "no-status.md").write_text(
                "# No status\n\nFeature ID: no-status\n\n## Acceptance Criteria\n\n- [x] Exists.\n",
                encoding="utf-8",
            )

            for status_filter, expected in (
                ("invalid", ["BadSlug"]),
                ("unknown", ["no-status"]),
            ):
                with self.subTest(status_filter=status_filter):
                    output = StringIO()
                    with redirect_stdout(output):
                        returncode = main(
                            [
                                "status",
                                str(root),
                                "--json",
                                "--feature-summaries",
                                "--feature-status",
                                status_filter,
                            ]
                        )

                    self.assertEqual(returncode, 0)
                    self.assertEqual(
                        feature_summary_slugs(json.loads(output.getvalue())),
                        expected,
                    )

    def test_status_feature_status_filter_single_and_multiple_values(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_filter_set(root)
            single_output = StringIO()
            multiple_output = StringIO()

            with redirect_stdout(single_output):
                single_returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-status",
                        "validated",
                    ]
                )
            with redirect_stdout(multiple_output):
                multiple_returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-status",
                        "validated",
                        "--feature-status",
                        "implemented",
                    ]
                )

            self.assertEqual(single_returncode, 0)
            self.assertEqual(multiple_returncode, 0)
            self.assertEqual(
                feature_summary_slugs(json.loads(single_output.getvalue())),
                ["alpha-validated"],
            )
            self.assertEqual(
                feature_summary_slugs(json.loads(multiple_output.getvalue())),
                ["alpha-validated", "middle-implemented"],
            )

    def test_status_feature_ready_filter_accepts_aliases(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_filter_set(root)

            for ready_value, expected in (
                ("yes", ["alpha-validated"]),
                ("ready", ["alpha-validated"]),
                ("no", ["middle-implemented", "zeta-planned"]),
                ("not-ready", ["middle-implemented", "zeta-planned"]),
                ("true", ["alpha-validated"]),
                ("false", ["middle-implemented", "zeta-planned"]),
            ):
                with self.subTest(ready_value=ready_value):
                    output = StringIO()
                    with redirect_stdout(output):
                        returncode = main(
                            [
                                "status",
                                str(root),
                                "--json",
                                "--feature-summaries",
                                "--feature-ready",
                                ready_value,
                            ]
                        )

                    self.assertEqual(returncode, 0)
                    self.assertEqual(
                        feature_summary_slugs(json.loads(output.getvalue())),
                        expected,
                    )

    def test_status_feature_priority_and_owner_filters(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_filter_set(root)
            write_status_feature_bundle(
                root,
                slug="unowned-unknown",
                status="planned",
                priority="urgent",
                owner="",
            )

            cases = (
                (
                    ["--feature-priority", "high"],
                    ["alpha-validated"],
                ),
                (
                    ["--feature-priority", "medium", "--feature-priority", "unknown"],
                    ["middle-implemented", "unowned-unknown"],
                ),
                (
                    ["--feature-priority", "high", "--feature-priority", "HIGH"],
                    ["alpha-validated"],
                ),
                (
                    ["--feature-owner", "dana"],
                    ["middle-implemented", "zeta-planned"],
                ),
                (
                    ["--feature-owner", "dana", "--feature-owner", "ADA"],
                    ["alpha-validated", "middle-implemented", "zeta-planned"],
                ),
                (
                    ["--feature-owner", "ADA"],
                    ["alpha-validated"],
                ),
                (
                    ["--feature-owner", "unassigned"],
                    ["unowned-unknown"],
                ),
            )

            for options, expected in cases:
                with self.subTest(options=options):
                    output = StringIO()
                    with redirect_stdout(output):
                        returncode = main(
                            [
                                "status",
                                str(root),
                                "--json",
                                "--feature-summaries",
                                *options,
                            ]
                        )

                    self.assertEqual(returncode, 0)
                    self.assertEqual(
                        feature_summary_slugs(json.loads(output.getvalue())),
                        expected,
                    )

    def test_status_feature_sort_keys_and_descending_order(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_filter_set(root)

            expected_by_key = {
                "slug": [
                    "alpha-validated",
                    "middle-implemented",
                    "zeta-planned",
                ],
                "status": [
                    "zeta-planned",
                    "middle-implemented",
                    "alpha-validated",
                ],
                "ready": [
                    "middle-implemented",
                    "zeta-planned",
                    "alpha-validated",
                ],
                "gaps": [
                    "alpha-validated",
                    "zeta-planned",
                    "middle-implemented",
                ],
                "blocking": [
                    "alpha-validated",
                    "zeta-planned",
                    "middle-implemented",
                ],
                "tasks-open": [
                    "alpha-validated",
                    "zeta-planned",
                    "middle-implemented",
                ],
                "priority": [
                    "alpha-validated",
                    "middle-implemented",
                    "zeta-planned",
                ],
            }
            for sort_key, expected in expected_by_key.items():
                with self.subTest(sort_key=sort_key):
                    output = StringIO()
                    with redirect_stdout(output):
                        returncode = main(
                            [
                                "status",
                                str(root),
                                "--json",
                                "--feature-summaries",
                                "--feature-sort",
                                sort_key,
                            ]
                        )

                    self.assertEqual(returncode, 0)
                    self.assertEqual(
                        feature_summary_slugs(json.loads(output.getvalue())),
                        expected,
                    )

            desc_output = StringIO()
            with redirect_stdout(desc_output):
                desc_returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-sort",
                        "slug",
                        "--feature-sort-desc",
                    ]
                )

            self.assertEqual(desc_returncode, 0)
            self.assertEqual(
                feature_summary_slugs(json.loads(desc_output.getvalue())),
                ["zeta-planned", "middle-implemented", "alpha-validated"],
            )

    def test_status_feature_priority_sort_covers_unknown_and_descending(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_bundle(
                root,
                slug="delta-high",
                status="planned",
                priority="high",
            )
            write_status_feature_bundle(
                root,
                slug="alpha-medium",
                status="planned",
                priority="medium",
            )
            write_status_feature_bundle(
                root,
                slug="bravo-low",
                status="planned",
                priority="low",
            )
            write_status_feature_bundle(
                root,
                slug="charlie-unknown",
                status="planned",
            )
            output = StringIO()
            desc_output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-sort",
                        "priority",
                    ]
                )
            with redirect_stdout(desc_output):
                desc_returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-sort",
                        "priority",
                        "--feature-sort-desc",
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertEqual(desc_returncode, 0)
            self.assertEqual(
                feature_summary_slugs(json.loads(output.getvalue())),
                ["delta-high", "alpha-medium", "bravo-low", "charlie-unknown"],
            )
            self.assertEqual(
                feature_summary_slugs(json.loads(desc_output.getvalue())),
                ["charlie-unknown", "bravo-low", "alpha-medium", "delta-high"],
            )

    def test_status_text_feature_summaries_apply_filters_and_sorting(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_filter_set(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "status",
                        str(root),
                        "--feature-summaries",
                        "--feature-ready",
                        "no",
                        "--feature-sort",
                        "status",
                    ]
                )

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("Feature summaries:", text)
            feature_summary_text = text.split("Feature summaries:", 1)[1]
            self.assertNotIn("alpha-validated -", feature_summary_text)
            self.assertLess(
                feature_summary_text.index("zeta-planned -"),
                feature_summary_text.index("middle-implemented -"),
            )

    def test_status_feature_summary_filter_no_matches_text_and_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_filter_set(root)
            json_output = StringIO()
            text_output = StringIO()

            with redirect_stdout(json_output):
                json_returncode = main(
                    [
                        "status",
                        str(root),
                        "--json",
                        "--feature-summaries",
                        "--feature-status",
                        "archived",
                    ]
                )
            with redirect_stdout(text_output):
                text_returncode = main(
                    [
                        "status",
                        str(root),
                        "--feature-summaries",
                        "--feature-status",
                        "archived",
                    ]
                )

            payload = json.loads(json_output.getvalue())
            self.assertEqual(json_returncode, 0)
            self.assertEqual(text_returncode, 0)
            self.assertEqual(payload["feature_summaries"], [])
            self.assertIn("Feature summaries:\n  none\n", text_output.getvalue())

    def test_status_feature_summaries_do_not_call_gh_network_or_read_tokens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_status_feature_filter_set(root)
            output = StringIO()
            token_names = {
                "GH_TOKEN",
                "GITHUB_API_TOKEN",
                "GITHUB_PAT",
                "GITHUB_TOKEN",
            }
            environ_type = os.environ.__class__
            original_get = environ_type.get
            original_getitem = environ_type.__getitem__
            original_contains = environ_type.__contains__

            def guarded_get(environ, key, default=None):
                if key in token_names:
                    raise AssertionError(f"token read: {key}")
                return original_get(environ, key, default)

            def guarded_getitem(environ, key):
                if key in token_names:
                    raise AssertionError(f"token read: {key}")
                return original_getitem(environ, key)

            def guarded_contains(environ, key):
                if key in token_names:
                    raise AssertionError(f"token read: {key}")
                return original_contains(environ, key)

            with patch.dict(
                "os.environ",
                {
                    "GH_TOKEN": "secret-gh-token",
                    "GITHUB_API_TOKEN": "secret-github-api-token",
                    "GITHUB_PAT": "secret-github-pat",
                    "GITHUB_TOKEN": "secret-github-token",
                    "PATH": "",
                },
            ):
                with (
                    patch.object(environ_type, "get", guarded_get),
                    patch.object(environ_type, "__getitem__", guarded_getitem),
                    patch.object(environ_type, "__contains__", guarded_contains),
                    patch(
                        "subprocess.run",
                        side_effect=AssertionError("subprocess called"),
                    ) as subprocess_run,
                    patch(
                        "subprocess.Popen",
                        side_effect=AssertionError("subprocess called"),
                    ) as subprocess_popen,
                    patch(
                        "urllib.request.urlopen",
                        side_effect=AssertionError("network called"),
                    ) as urlopen,
                    patch(
                        "socket.create_connection",
                        side_effect=AssertionError("network called"),
                    ) as create_connection,
                    patch(
                        "socket.socket.connect",
                        side_effect=AssertionError("network called"),
                    ) as socket_connect,
                    redirect_stdout(output),
                ):
                    returncode = main(
                        [
                            "status",
                            str(root),
                            "--json",
                            "--validate",
                            "--validation-warnings",
                            "--feature-summaries",
                            "--feature-status",
                            "validated",
                            "--feature-ready",
                            "yes",
                            "--feature-sort",
                            "slug",
                        ]
                    )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(feature_summary_slugs(payload), ["alpha-validated"])
            self.assertIn("warning_checks", payload["validation"])
            subprocess_run.assert_not_called()
            subprocess_popen.assert_not_called()
            urlopen.assert_not_called()
            create_connection.assert_not_called()
            socket_connect.assert_not_called()
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-api-token", output.getvalue())
            self.assertNotIn("secret-github-pat", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())

    def test_status_feature_summary_options_require_feature_summaries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            cases = (
                ["--feature-status", "validated"],
                ["--feature-ready", "yes"],
                ["--feature-priority", "high"],
                ["--feature-owner", "Dana"],
                ["--feature-sort", "slug"],
                ["--feature-sort-desc"],
                ["--feature-require-coverage"],
            )

            for options in cases:
                with self.subTest(options=options):
                    stdout = StringIO()
                    stderr = StringIO()
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        returncode = main(["status", str(root), *options])

                    self.assertEqual(returncode, 2)
                    self.assertEqual(stdout.getvalue(), "")
                    self.assertIn("require --feature-summaries", stderr.getvalue())
                    self.assertIn("--feature-require-coverage", stderr.getvalue())

    def test_status_feature_summary_invalid_options_return_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            cases = (
                (["--feature-status", "blocked"], "Invalid feature summary status"),
                (["--feature-ready", "maybe"], "Invalid feature summary readiness"),
                (["--feature-priority", "urgent"], "Invalid feature summary priority"),
                (["--feature-sort", "deadline"], "Invalid feature summary sort key"),
            )

            for options, expected_error in cases:
                with self.subTest(options=options):
                    stdout = StringIO()
                    stderr = StringIO()
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        returncode = main(
                            ["status", str(root), "--feature-summaries", *options]
                        )

                    self.assertEqual(returncode, 2)
                    self.assertEqual(stdout.getvalue(), "")
                    self.assertIn(expected_error, stderr.getvalue())

    def test_status_validate_reports_failed_checks_but_returns_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            (root / "quality" / "checklist.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["status", str(root), "--json", "--validate"])

            payload = json.loads(output.getvalue())
            failed_ids = {
                check["id"]
                for check in payload["validation"]["failed_checks"]
            }
            self.assertEqual(returncode, 0)
            self.assertFalse(payload["validation"]["ok"])
            self.assertIn("workspace.required_file:quality/checklist.md", failed_ids)
            self.assertNotIn("fusion.integration_mode", failed_ids)
            for check in payload["validation"]["failed_checks"]:
                self.assertEqual(check["status"], "fail")
                self.assertGreaterEqual(
                    set(check),
                    {"id", "message", "severity", "status"},
                )

    def test_status_validate_with_adapters_uses_mock_probe(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            output = StringIO()
            probed: list[str] = []

            def build_status_with_fake_probe(
                path: Path,
                *,
                include_adapters: bool = False,
                include_feature_summaries: bool = False,
                feature_summary_statuses: tuple[str, ...] = (),
                feature_summary_ready: bool | None = None,
                feature_summary_priorities: tuple[str, ...] = (),
                feature_summary_owners: tuple[str, ...] = (),
                feature_summary_sort: str | None = None,
                feature_summary_sort_desc: bool = False,
                feature_summary_require_coverage: bool = False,
            ) -> dict[str, object]:
                return build_status(
                    path,
                    include_adapters=include_adapters,
                    include_feature_summaries=include_feature_summaries,
                    feature_summary_statuses=feature_summary_statuses,
                    feature_summary_ready=feature_summary_ready,
                    feature_summary_priorities=feature_summary_priorities,
                    feature_summary_owners=feature_summary_owners,
                    feature_summary_sort=feature_summary_sort,
                    feature_summary_sort_desc=feature_summary_sort_desc,
                    feature_summary_require_coverage=feature_summary_require_coverage,
                    adapter_probe=fake_available_adapters,
                )

            def fake_probe(keys: list[str]) -> list[AdapterStatus]:
                probed.extend(keys)
                return fake_available_adapter_probe(keys)

            with patch(
                "specspine.cli.build_status",
                side_effect=build_status_with_fake_probe,
            ), patch("specspine.cli.probe_adapters", side_effect=fake_probe):
                with redirect_stdout(output):
                    returncode = main(
                        ["status", str(root), "--adapters", "--json", "--validate"]
                    )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(sorted(probed), ["openspec", "speckit", "superpowers"])
            self.assertIn("adapters", payload)
            self.assertTrue(payload["validation"]["included"]["adapters"])
            self.assertEqual(payload["validation"]["summary"]["fail"], 0)

    def test_status_validate_with_adapters_preserves_feature_summaries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            write_status_feature_bundle(root)
            output = StringIO()
            probed: list[str] = []

            def build_status_with_fake_probe(
                path: Path,
                *,
                include_adapters: bool = False,
                include_feature_summaries: bool = False,
                feature_summary_statuses: tuple[str, ...] = (),
                feature_summary_ready: bool | None = None,
                feature_summary_priorities: tuple[str, ...] = (),
                feature_summary_owners: tuple[str, ...] = (),
                feature_summary_sort: str | None = None,
                feature_summary_sort_desc: bool = False,
                feature_summary_require_coverage: bool = False,
            ) -> dict[str, object]:
                return build_status(
                    path,
                    include_adapters=include_adapters,
                    include_feature_summaries=include_feature_summaries,
                    feature_summary_statuses=feature_summary_statuses,
                    feature_summary_ready=feature_summary_ready,
                    feature_summary_priorities=feature_summary_priorities,
                    feature_summary_owners=feature_summary_owners,
                    feature_summary_sort=feature_summary_sort,
                    feature_summary_sort_desc=feature_summary_sort_desc,
                    feature_summary_require_coverage=feature_summary_require_coverage,
                    adapter_probe=fake_available_adapters,
                )

            def fake_probe(keys: list[str]) -> list[AdapterStatus]:
                probed.extend(keys)
                return fake_available_adapter_probe(keys)

            with patch(
                "specspine.cli.build_status",
                side_effect=build_status_with_fake_probe,
            ), patch("specspine.cli.probe_adapters", side_effect=fake_probe):
                with redirect_stdout(output):
                    returncode = main(
                        [
                            "status",
                            str(root),
                            "--adapters",
                            "--json",
                            "--validate",
                            "--feature-summaries",
                        ]
                    )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(sorted(probed), ["openspec", "speckit", "superpowers"])
            self.assertIn("adapters", payload)
            self.assertIn("validation", payload)
            self.assertTrue(payload["validation"]["included"]["adapters"])
            self.assertIn("feature_summaries", payload)
            self.assertEqual(len(payload["feature_summaries"]), 1)
            self.assertEqual(payload["feature_summaries"][0]["slug"], "add-dark-mode")

    def test_status_json_cli_output_can_include_adapter_probe_results(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")
            output = StringIO()

            def build_status_with_fake_probe(
                path: Path,
                *,
                include_adapters: bool = False,
                include_feature_summaries: bool = False,
                feature_summary_statuses: tuple[str, ...] = (),
                feature_summary_ready: bool | None = None,
                feature_summary_priorities: tuple[str, ...] = (),
                feature_summary_owners: tuple[str, ...] = (),
                feature_summary_sort: str | None = None,
                feature_summary_sort_desc: bool = False,
                feature_summary_require_coverage: bool = False,
            ) -> dict[str, object]:
                return build_status(
                    path,
                    include_adapters=include_adapters,
                    include_feature_summaries=include_feature_summaries,
                    feature_summary_statuses=feature_summary_statuses,
                    feature_summary_ready=feature_summary_ready,
                    feature_summary_priorities=feature_summary_priorities,
                    feature_summary_owners=feature_summary_owners,
                    feature_summary_sort=feature_summary_sort,
                    feature_summary_sort_desc=feature_summary_sort_desc,
                    feature_summary_require_coverage=feature_summary_require_coverage,
                    adapter_probe=fake_available_adapters,
                )

            with patch(
                "specspine.cli.build_status",
                side_effect=build_status_with_fake_probe,
            ):
                with redirect_stdout(output):
                    returncode = main(["status", str(root), "--adapters", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertIn("adapters", payload)
            self.assertNotIn("validation", payload)
            self.assertEqual(
                sorted(payload["adapters"]),
                ["openspec", "speckit", "superpowers"],
            )
            self.assertTrue(payload["adapters"]["openspec"]["available"])
            self.assertTrue(payload["adapters"]["speckit"]["available"])
            self.assertTrue(payload["adapters"]["superpowers"]["available"])

    def test_status_reports_missing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            (root / "quality" / "checklist.md").unlink()

            status = build_status(root)

            self.assertFalse(status["workspace"]["complete"])
            self.assertFalse(status["fusion"]["complete"])
            self.assertIn("quality/checklist.md", status["workspace"]["missing"])
            self.assertFalse(status["artifacts"]["quality/checklist.md"]["exists"])
            self.assertTrue(
                any("specspine init" in item for item in status["recommendations"])
            )

    def test_status_text_includes_required_sections(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            text = render_status_text(build_status(root))

            self.assertIn("Workspace: complete", text)
            self.assertIn("Fusion: incomplete", text)
            self.assertIn("Artifacts:", text)
            self.assertIn("Enabled upstreams:", text)
            self.assertIn("Recommended next actions:", text)
            self.assertNotIn("Feature summaries:", text)

    def test_fusion_workspace_with_available_adapters_recommends_context_packet(
        self,
    ) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")

            status = build_status(
                root,
                include_adapters=True,
                adapter_probe=fake_available_adapters,
            )

            self.assertTrue(status["fusion"]["complete"])
            self.assertEqual(
                status["recommendations"],
                [
                    "Use `specspine status --json` as the compact context packet for agents."
                ],
            )

    def test_status_can_include_adapter_probe_results(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_fusion_workspace(root, agent="codex")

            def fake_probe() -> list[AdapterStatus]:
                return [
                    AdapterStatus(
                        key="openspec",
                        display_name="OpenSpec",
                        available=True,
                        detail="fake openspec",
                        version="1.0.0",
                        command="openspec",
                        install_hint="install openspec",
                        upstream_url="https://example.test/openspec",
                    ),
                    AdapterStatus(
                        key="speckit",
                        display_name="Spec Kit",
                        available=False,
                        detail="fake speckit missing",
                        version=None,
                        command="specify",
                        install_hint="install speckit",
                        upstream_url="https://example.test/speckit",
                    ),
                ]

            status = build_status(root, include_adapters=True, adapter_probe=fake_probe)

            self.assertIn("adapters", status)
            self.assertTrue(status["adapters"]["openspec"]["available"])
            self.assertFalse(status["adapters"]["speckit"]["available"])
            self.assertTrue(
                any("Install Spec Kit" in item for item in status["recommendations"])
            )
