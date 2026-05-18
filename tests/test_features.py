import json
import os
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from specspine.cli import main
from specspine.features import (
    FEATURE_STATUSES,
    FEATURE_TRANSITIONS,
    FeatureBundleExistsError,
    InvalidFeatureSlug,
    build_feature_handoff_report,
    build_feature_ready_report,
    build_feature_sync_plan,
    build_feature_task_issues_report,
    build_feature_tests_report,
    build_feature_trace_report,
    build_issue_draft,
    build_pull_request_draft,
    build_feature_tasks_report,
    create_feature_bundle,
    parse_acceptance_criteria,
    parse_feature_tasks,
    parse_quality_checks,
    parse_release_readiness,
    parse_test_coverage,
    parse_test_plan,
    read_feature_metadata,
    set_feature_status,
)
from specspine.status import build_status
from specspine.validation import build_validation_report, validation_exit_code
from specspine.workspace import init_workspace


EXPECTED_FEATURE_FILES = {
    "specs/features/add-dark-mode.md",
    "execution/features/add-dark-mode.md",
    "quality/features/add-dark-mode.md",
}

REPO_ROOT = Path(__file__).resolve().parents[1]


def write_ready_feature_bundle(
    root: Path,
    slug: str = "add-dark-mode",
    *,
    status: str = "validated",
) -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)
    (root / "specs" / "features" / f"{slug}.md").write_text(
        "\n".join(
            [
                "# Add dark mode",
                "",
                f"Feature ID: {slug}",
                f"Status: {status}",
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
                "- [x] Add theme tests.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
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
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_coverage_target(
    root: Path,
    relative_path: str = "tests/test_feature_ready_coverage.py",
) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# local coverage target\n", encoding="utf-8")


def insert_test_coverage(
    root: Path,
    lines: list[str],
    slug: str = "add-dark-mode",
) -> None:
    quality = root / "quality" / "features" / f"{slug}.md"
    content = quality.read_text(encoding="utf-8")
    section = "## Test Coverage\n\n" + "\n".join(lines) + "\n\n## Test Plan"
    quality.write_text(
        content.replace("## Test Plan", section, 1),
        encoding="utf-8",
    )


def add_feature_metadata(
    root: Path,
    slug: str = "add-dark-mode",
    *,
    priority: str = "high",
    owner: str = "Platform Team",
    milestone: str = "Beta",
    target_release: str = "2026.2",
    project: str = "Triage Board",
    effort: str = "M",
) -> None:
    spec = root / "specs" / "features" / f"{slug}.md"
    content = spec.read_text(encoding="utf-8")
    content = content.replace(
        f"Feature ID: {slug}\n",
        (
            f"Feature ID: {slug}\n"
            f"Priority: {priority}\n"
            f"Owner: {owner}\n"
            f"Milestone: {milestone}\n"
            f"Target Release: {target_release}\n"
            f"Project: {project}\n"
            f"Effort: {effort}\n"
        ),
        1,
    )
    spec.write_text(content, encoding="utf-8")


def add_legacy_priority_owner_metadata(
    root: Path,
    slug: str = "add-dark-mode",
    *,
    priority: str = "high",
    owner: str = "Platform Team",
) -> None:
    spec = root / "specs" / "features" / f"{slug}.md"
    content = spec.read_text(encoding="utf-8")
    content = content.replace(
        f"Feature ID: {slug}\n",
        (
            f"Feature ID: {slug}\n"
            f"Priority: {priority}\n"
            f"Owner: {owner}\n"
        ),
        1,
    )
    spec.write_text(content, encoding="utf-8")


class FeatureBundleTests(TestCase):
    def test_create_feature_bundle_in_plain_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            written = create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
            )

            self.assertEqual(
                {str(path.relative_to(root)) for path in written},
                EXPECTED_FEATURE_FILES,
            )
            for relative_path in EXPECTED_FEATURE_FILES:
                content = (root / relative_path).read_text(encoding="utf-8")
                self.assertIn("Add dark mode", content)
                self.assertIn("Reduce eye strain", content)
                self.assertIn("Feature ID: add-dark-mode", content)
                self.assertIn("Status: proposed", content)

            spec = (root / "specs" / "features" / "add-dark-mode.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Priority: medium", spec)
            self.assertIn("Owner: unassigned", spec)
            self.assertIn("Milestone: unassigned", spec)
            self.assertIn("Target Release: unassigned", spec)
            self.assertIn("Project: unassigned", spec)
            self.assertIn("Effort: unknown", spec)
            self.assertIn("## Why", spec)
            self.assertIn("## Users", spec)
            self.assertIn("## Scope", spec)
            self.assertIn("## Non-Goals", spec)
            self.assertIn("## Acceptance Criteria", spec)
            self.assertIn("## Edge Cases", spec)
            self.assertIn("## Constraints", spec)
            self.assertIn("## Traceability Notes", spec)
            self.assertIn(
                "- [ ] TODO: Define one observable outcome",
                spec,
            )

            execution = (
                root / "execution" / "features" / "add-dark-mode.md"
            ).read_text(encoding="utf-8")
            self.assertIn("## Milestones", execution)
            self.assertIn("## Tasks", execution)
            self.assertIn("## Dependencies", execution)
            self.assertIn("## Open Questions", execution)
            self.assertIn("## Agent Handoff", execution)
            for command in (
                "specspine feature handoff add-dark-mode . --json",
                "specspine feature tasks add-dark-mode . --json",
                "specspine feature task-issues add-dark-mode . --json",
                "specspine feature trace add-dark-mode . --json",
                "specspine feature tests add-dark-mode . --json",
                "specspine tests impact . --feature add-dark-mode --json",
                "specspine change risk . --feature add-dark-mode --json",
                "specspine security cues . --feature add-dark-mode --json",
                "specspine review packet . --feature add-dark-mode --json",
                "specspine feature ready add-dark-mode . --json",
                "specspine feature pr add-dark-mode . --json",
                "specspine feature sync-plan add-dark-mode . --json",
                "specspine feature archive add-dark-mode . --json",
                "specspine validate . --fusion --features",
            ):
                with self.subTest(command=command):
                    self.assertIn(command, execution)

            quality = (root / "quality" / "features" / "add-dark-mode.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## Required Checks", quality)
            self.assertIn("## Test Coverage", quality)
            self.assertIn("## Test Plan", quality)
            self.assertIn("## Review Notes", quality)
            self.assertIn("## Release Readiness", quality)
            self.assertIn("Acceptance criteria are reviewed", quality)
            self.assertIn("Test coverage proves", quality)
            self.assertIn("Documentation, release notes, or PR draft", quality)
            self.assertIn("specspine tests impact . --feature add-dark-mode --json", quality)
            self.assertIn("specspine change risk . --feature add-dark-mode --json", quality)
            self.assertIn("specspine security cues . --feature add-dark-mode --json", quality)
            self.assertIn("specspine review packet . --feature add-dark-mode --json", quality)
            self.assertIn("specspine feature sync-plan add-dark-mode . --json", quality)
            self.assertIn("specspine feature archive add-dark-mode . --json", quality)
            self.assertIn("specspine feature ready add-dark-mode . --json", quality)
            self.assertIn("specspine validate . --fusion --features", quality)
            self.assertIn("specspine feature pr add-dark-mode . --json", quality)
            self.assertIn("link existing local test files", quality)
            self.assertIn("- [ ] AC001 -> tests/...", quality)
            quality_source = "quality/features/add-dark-mode.md"
            quality_checks = parse_quality_checks(quality, source_file=quality_source)
            test_coverage = parse_test_coverage(
                quality,
                source_file=quality_source,
                root=root,
            )
            release_readiness = parse_release_readiness(
                quality,
                source_file=quality_source,
            )
            self.assertEqual(len(quality_checks), 5)
            self.assertEqual(len(test_coverage), 1)
            self.assertEqual(test_coverage[0].acceptance_criterion_id, "AC001")
            self.assertEqual(test_coverage[0].target, "tests/...")
            self.assertFalse(test_coverage[0].target_exists)
            self.assertEqual(len(release_readiness), 10)
            self.assertTrue(all(not check.done for check in quality_checks))
            self.assertTrue(all(not check.done for check in release_readiness))

            report = build_validation_report(root, include_features=True)
            self.assertTrue(report["ok"])
            self.assertEqual(validation_exit_code(report), 0)

    def test_read_feature_metadata_defaults_for_old_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)

            metadata = read_feature_metadata(root, "add-dark-mode")

            self.assertEqual(
                metadata.as_dict(),
                {
                    "effort": "unknown",
                    "milestone": "unassigned",
                    "owner": "unassigned",
                    "priority": "unknown",
                    "project": "unassigned",
                    "target_release": "unassigned",
                },
            )

    def test_read_feature_metadata_parses_extended_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            add_feature_metadata(root)

            metadata = read_feature_metadata(root, "add-dark-mode")

            self.assertEqual(
                metadata.as_dict(),
                {
                    "effort": "M",
                    "milestone": "Beta",
                    "owner": "Platform Team",
                    "priority": "high",
                    "project": "Triage Board",
                    "target_release": "2026.2",
                },
            )

    def test_read_feature_metadata_is_case_and_whitespace_stable(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                "\n".join(
                    [
                        "# Add dark mode",
                        "",
                        "feature id: add-dark-mode",
                        "STATUS: validated",
                        "  priority  :  HIGH  ",
                        "\tOwner\t:\t Platform Team  ",
                        "milestone:   Beta  ",
                        "TARGET RELEASE :  2026.2 ",
                        "Project:   Triage Board",
                        "effort :   M  ",
                        "",
                        "## Acceptance Criteria",
                        "",
                        "- [x] Users can enable dark mode.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            metadata = read_feature_metadata(root, "add-dark-mode")

            self.assertEqual(
                metadata.as_dict(),
                {
                    "effort": "M",
                    "milestone": "Beta",
                    "owner": "Platform Team",
                    "priority": "high",
                    "project": "Triage Board",
                    "target_release": "2026.2",
                },
            )

    def test_legacy_priority_owner_outputs_default_extended_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            add_legacy_priority_owner_metadata(root)

            expected = {
                "effort": "unknown",
                "milestone": "unassigned",
                "owner": "Platform Team",
                "priority": "high",
                "project": "unassigned",
                "target_release": "unassigned",
            }

            issue = build_issue_draft(root, "add-dark-mode")
            pr = build_pull_request_draft(root, "add-dark-mode")
            sync_plan = build_feature_sync_plan(root, "add-dark-mode")
            handoff = build_feature_handoff_report(root, "add-dark-mode")
            tests = build_feature_tests_report(root, "add-dark-mode")

            for payload in (
                issue.as_dict(),
                pr.as_dict(),
                sync_plan.as_dict(),
                handoff.as_dict(),
                tests.as_dict(),
            ):
                with self.subTest(output=payload["feature_id"]):
                    self.assertEqual(payload["metadata"], expected)

            for body in (
                issue.body,
                pr.body,
                *(command.body for command in sync_plan.commands),
            ):
                self.assertIn("- Milestone: unassigned", body)
                self.assertIn("- Target Release: unassigned", body)
                self.assertIn("- Project: unassigned", body)
                self.assertIn("- Effort: unknown", body)

    def test_new_feature_bundle_validates_but_is_not_ready(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")

            validation = build_validation_report(root, include_features=True)
            ready = build_feature_ready_report(root, "add-dark-mode")

            blocking_ids = {check.id for check in ready.blocking_checks}
            self.assertTrue(validation["ok"])
            self.assertEqual(validation_exit_code(validation), 0)
            self.assertFalse(ready.ready)
            self.assertEqual(ready.status, "proposed")
            self.assertEqual(ready.missing_files, ())
            self.assertEqual(ready.gaps, ())
            self.assertIn("feature.lifecycle_status", blocking_ids)
            self.assertIn("feature.acceptance_criteria", blocking_ids)
            self.assertIn("feature.tasks", blocking_ids)
            self.assertIn("feature.required_checks", blocking_ids)
            self.assertIn("feature.release_readiness", blocking_ids)

    def test_new_feature_bundle_trace_and_tests_extract_placeholders(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")

            trace = build_feature_trace_report(root, "add-dark-mode")
            tests = build_feature_tests_report(root, "add-dark-mode")

            self.assertEqual(trace.gaps, ())
            self.assertEqual([item.id for item in trace.acceptance_criteria], ["AC001"])
            self.assertEqual([task.id for task in trace.tasks], ["T001"])
            self.assertEqual(
                [check.id for check in trace.quality_checks],
                ["Q001", "Q002", "Q003", "Q004", "Q005"],
            )
            self.assertEqual([item.id for item in trace.test_plan], ["TP001"])
            self.assertFalse(tests.ready)
            self.assertEqual([test_case.id for test_case in tests.test_cases], ["TC001"])
            self.assertEqual(tests.test_cases[0].acceptance_criterion_id, "AC001")
            self.assertEqual(tests.test_cases[0].status, "planned")
            self.assertEqual([link.id for link in tests.test_coverage], ["COV001"])

    def test_create_feature_bundle_does_not_overwrite_existing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            existing = root / "specs" / "features" / "add-dark-mode.md"
            existing.write_text("custom spec\n", encoding="utf-8")

            with self.assertRaises(FeatureBundleExistsError):
                create_feature_bundle(root, "add-dark-mode")

            self.assertEqual(existing.read_text(encoding="utf-8"), "custom spec\n")
            self.assertFalse(
                (root / "execution" / "features" / "add-dark-mode.md").exists()
            )
            self.assertFalse(
                (root / "quality" / "features" / "add-dark-mode.md").exists()
            )

    def test_create_feature_bundle_force_overwrites_existing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text("custom spec\n", encoding="utf-8")

            create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
                force=True,
            )

            content = spec.read_text(encoding="utf-8")
            self.assertNotEqual(content, "custom spec\n")
            self.assertIn("Add dark mode", content)
            self.assertIn("Reduce eye strain", content)

    def test_invalid_feature_slug_is_rejected(self) -> None:
        invalid_slugs = ["Add-dark-mode", "-bad", "bad-", "bad_slug", "bad.slug"]

        for slug in invalid_slugs:
            with self.subTest(slug=slug):
                with self.assertRaises(InvalidFeatureSlug):
                    create_feature_bundle(Path("."), slug)

    def test_single_character_feature_slug_is_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            written = create_feature_bundle(root, "a")

            self.assertEqual(
                {str(path.relative_to(root)) for path in written},
                {
                    "specs/features/a.md",
                    "execution/features/a.md",
                    "quality/features/a.md",
                },
            )
            self.assertIn(
                "Feature ID: a",
                (root / "specs" / "features" / "a.md").read_text(encoding="utf-8"),
            )

    def test_feature_slug_allows_consecutive_hyphens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            written = create_feature_bundle(root, "add--dark-mode")

            self.assertEqual(len(written), 3)
            self.assertTrue((root / "specs" / "features" / "add--dark-mode.md").exists())

    def test_feature_new_cli_creates_bundle_and_returns_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "new",
                        "add-dark-mode",
                        str(root),
                        "--title",
                        "Add dark mode",
                        "--why",
                        "Reduce eye strain",
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Created SpecSpine feature bundle", output.getvalue())
            for relative_path in EXPECTED_FEATURE_FILES:
                self.assertTrue((root / relative_path).exists())

    def test_feature_new_cli_rejects_invalid_slug_with_nonzero_return_code(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "new", "BadSlug", str(root)])

            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_feature_new_cli_does_not_overwrite_without_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "new", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 1)
            self.assertIn("Use --force", stderr.getvalue())
            self.assertIn(
                "existing specs/features/add-dark-mode.md",
                stderr.getvalue(),
            )
            self.assertIn(
                "existing execution/features/add-dark-mode.md",
                stderr.getvalue(),
            )
            self.assertIn(
                "existing quality/features/add-dark-mode.md",
                stderr.getvalue(),
            )

    def test_feature_new_cli_force_overwrites(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text("custom spec\n", encoding="utf-8")

            with redirect_stdout(StringIO()):
                returncode = main(
                    [
                        "feature",
                        "new",
                        "add-dark-mode",
                        str(root),
                        "--title",
                        "Add dark mode",
                        "--force",
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Add dark mode", spec.read_text(encoding="utf-8"))

    def test_parse_feature_tasks_preserves_order_lines_and_done_flags(self) -> None:
        content = "\n".join(
            [
                "# Add dark mode Execution",
                "",
                "Feature ID: add-dark-mode",
                "Status: planned",
                "",
                "## Tasks",
                "",
                "- [ ] Implement theme storage.",
                "* [x] Add system preference detection.",
                "- [X] Update docs.",
                "- plain bullet ignored",
                "notes ignored",
                "",
                "## Dependencies",
                "",
                "- [ ] Not part of tasks.",
            ]
        )

        tasks = parse_feature_tasks(
            content,
            source_file="execution/features/add-dark-mode.md",
        )

        self.assertEqual([task.id for task in tasks], ["T001", "T002", "T003"])
        self.assertEqual(
            [task.text for task in tasks],
            [
                "Implement theme storage.",
                "Add system preference detection.",
                "Update docs.",
            ],
        )
        self.assertEqual([task.done for task in tasks], [False, True, True])
        self.assertEqual([task.line for task in tasks], [8, 9, 10])
        self.assertEqual(
            {task.source_file for task in tasks},
            {"execution/features/add-dark-mode.md"},
        )

    def test_parse_feature_tasks_keeps_lower_heading_tasks_and_markdown_text(self) -> None:
        content = "\n".join(
            [
                "# Add dark mode Execution",
                "",
                "## Tasks",
                "",
                "- [ ] Keep inline `mode: dark` value: unchanged.",
                "- not a checklist",
                "### Follow-up",
                "",
                "* [X] Preserve `cli --flag`: output text.",
                "",
                "## Dependencies",
                "",
                "- [ ] Not part of tasks.",
            ]
        )

        tasks = parse_feature_tasks(
            content,
            source_file="execution/features/add-dark-mode.md",
        )

        self.assertEqual([task.id for task in tasks], ["T001", "T002"])
        self.assertEqual(
            [task.text for task in tasks],
            [
                "Keep inline `mode: dark` value: unchanged.",
                "Preserve `cli --flag`: output text.",
            ],
        )
        self.assertEqual([task.done for task in tasks], [False, True])
        self.assertEqual([task.line for task in tasks], [5, 9])

    def test_trace_parsers_extract_checklists_and_test_plan(self) -> None:
        spec_content = "\n".join(
            [
                "# Add dark mode",
                "",
                "## Acceptance Criteria",
                "",
                "- [ ] Users can enable dark mode.",
                "* [x] The setting persists.",
                "- plain bullet ignored",
                "",
                "## Scope",
                "",
                "- [ ] Not acceptance.",
            ]
        )
        quality_content = "\n".join(
            [
                "# Add dark mode Quality",
                "",
                "## Required Checks",
                "",
                "- [x] Unit tests cover theme selection.",
                "* [ ] Documentation names the setting.",
                "",
                "## Test Plan",
                "",
                "- Run unit tests.",
                "Manual check in a browser.",
                "",
                "## Review Notes",
                "",
                "- Not part of test plan.",
            ]
        )

        acceptance_criteria = parse_acceptance_criteria(
            spec_content,
            source_file="specs/features/add-dark-mode.md",
        )
        quality_checks = parse_quality_checks(
            quality_content,
            source_file="quality/features/add-dark-mode.md",
        )
        test_plan = parse_test_plan(
            quality_content,
            source_file="quality/features/add-dark-mode.md",
        )

        self.assertEqual(
            [item.id for item in acceptance_criteria],
            ["AC001", "AC002"],
        )
        self.assertEqual(
            [item.text for item in acceptance_criteria],
            ["Users can enable dark mode.", "The setting persists."],
        )
        self.assertEqual([item.done for item in acceptance_criteria], [False, True])
        self.assertEqual([item.line for item in acceptance_criteria], [5, 6])
        self.assertEqual([item.id for item in quality_checks], ["Q001", "Q002"])
        self.assertEqual([item.done for item in quality_checks], [True, False])
        self.assertEqual([item.id for item in test_plan], ["TP001", "TP002"])
        self.assertEqual(
            [item.text for item in test_plan],
            ["- Run unit tests.", "Manual check in a browser."],
        )
        self.assertEqual([item.line for item in test_plan], [10, 11])

    def test_parse_test_coverage_extracts_links_and_target_existence(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "test_features.py").write_text(
                "def test_name():\n    pass\n",
                encoding="utf-8",
            )
            content = "\n".join(
                [
                    "# Add dark mode Quality",
                    "",
                    "## Test Coverage",
                    "",
                    "- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_name",
                    "- [ ] AC002 -> tests/missing.py",
                    "- [x] Existing smoke test without AC -> tests/test_features.py",
                    "- plain bullet ignored",
                    "",
                    "## Test Plan",
                    "",
                    "- [ ] AC003 -> tests/not-coverage.py",
                ]
            )

            links = parse_test_coverage(
                content,
                source_file="quality/features/add-dark-mode.md",
                root=root,
            )

            self.assertEqual([link.id for link in links], ["COV001", "COV002", "COV003"])
            self.assertEqual(
                [link.acceptance_criterion_id for link in links],
                ["AC001", "AC002", "unknown"],
            )
            self.assertEqual(
                links[0].target,
                "tests/test_features.py::FeatureBundleTests::test_name",
            )
            self.assertEqual(links[0].target_path, "tests/test_features.py")
            self.assertTrue(links[0].target_exists)
            self.assertFalse(links[1].target_exists)
            self.assertEqual(links[2].target_path, "tests/test_features.py")
            self.assertEqual([link.done for link in links], [True, False, True])
            self.assertEqual([link.line for link in links], [5, 6, 7])

    def test_feature_tasks_cli_text_and_json_outputs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            execution = root / "execution" / "features" / "add-dark-mode.md"
            execution.write_text(
                "\n".join(
                    [
                        "# Add dark mode Execution",
                        "",
                        "Feature ID: add-dark-mode",
                        "Status: planned",
                        "",
                        "## Tasks",
                        "- [ ] Implement theme storage.",
                        "- [x] Add theme tests.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            text_output = StringIO()
            with redirect_stdout(text_output):
                text_returncode = main(
                    ["feature", "tasks", "add-dark-mode", str(root)]
                )

            self.assertEqual(text_returncode, 0)
            text = text_output.getvalue()
            self.assertIn("Feature tasks: add-dark-mode", text)
            self.assertIn("Status: mixed", text)
            self.assertIn("Summary: total=2 done=1 open=1", text)
            self.assertIn(
                "- [ ] T001 execution/features/add-dark-mode.md:7 Implement theme storage.",
                text,
            )
            self.assertIn(
                "- [x] T002 execution/features/add-dark-mode.md:8 Add theme tests.",
                text,
            )

            json_output = StringIO()
            with redirect_stdout(json_output):
                json_returncode = main(
                    ["feature", "tasks", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(json_output.getvalue())
            self.assertEqual(json_returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["source_file"], "execution/features/add-dark-mode.md")
            self.assertFalse(payload["source_missing"])
            self.assertEqual(payload["summary"], {"done": 1, "open": 1, "total": 2})
            self.assertEqual(
                payload["tasks"],
                [
                    {
                        "done": False,
                        "id": "T001",
                        "line": 7,
                        "source_file": "execution/features/add-dark-mode.md",
                        "text": "Implement theme storage.",
                    },
                    {
                        "done": True,
                        "id": "T002",
                        "line": 8,
                        "source_file": "execution/features/add-dark-mode.md",
                        "text": "Add theme tests.",
                    },
                ],
            )

    def test_feature_tasks_cli_reports_no_tasks_found(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            execution = root / "execution" / "features" / "add-dark-mode.md"
            execution.write_text(
                "\n".join(
                    [
                        "# Add dark mode Execution",
                        "",
                        "Feature ID: add-dark-mode",
                        "Status: planned",
                        "",
                        "## Tasks",
                        "",
                        "- plain bullet",
                        "implementation notes",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "tasks", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 0)
            self.assertIn("Summary: total=0 done=0 open=0", output.getvalue())
            self.assertIn(
                "No checklist tasks found in execution/features/add-dark-mode.md.",
                output.getvalue(),
            )

    def test_feature_tasks_cli_handles_missing_execution_partial_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "execution" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "tasks", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["source_missing"])
            self.assertEqual(payload["tasks"], [])
            self.assertEqual(payload["summary"], {"done": 0, "open": 0, "total": 0})
            self.assertEqual(
                payload["missing_files"],
                ["execution/features/add-dark-mode.md"],
            )

    def test_feature_tasks_cli_text_reports_missing_execution_source(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "execution" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "tasks", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 0)
            self.assertIn("Source: execution/features/add-dark-mode.md", output.getvalue())
            self.assertIn(
                "No tasks found because source file is missing: "
                "execution/features/add-dark-mode.md",
                output.getvalue(),
            )

    def test_feature_tasks_cli_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "tasks", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 1)
            self.assertIn("No feature files found", stderr.getvalue())
            self.assertIn(
                "missing execution/features/add-dark-mode.md",
                stderr.getvalue(),
            )

    def test_feature_tasks_cli_all_files_missing_does_not_call_gh_or_leak_tokens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            stderr = StringIO()

            with patch.dict(
                os.environ,
                {
                    "PATH": "",
                    "GH_TOKEN": "secret-gh-token",
                    "GITHUB_TOKEN": "secret-github-token",
                },
            ):
                with patch("subprocess.run", side_effect=AssertionError("gh called")):
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        returncode = main(
                            ["feature", "tasks", "add-dark-mode", str(root)]
                        )

            combined = stdout.getvalue() + stderr.getvalue()
            self.assertEqual(returncode, 1)
            self.assertNotIn("secret-gh-token", combined)
            self.assertNotIn("secret-github-token", combined)

    def test_feature_tasks_cli_output_file_overwrite_force_and_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output_file = root / "tasks.txt"
            output_file.write_text("existing\n", encoding="utf-8")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "tasks",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("Output file already exists", stderr.getvalue())
            self.assertEqual(output_file.read_text(encoding="utf-8"), "existing\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "tasks",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--output",
                        str(output_file),
                        "--force",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertIn("Feature tasks: add-dark-mode", output_file.read_text(encoding="utf-8"))
            self.assertNotIn("Wrote feature task list", stdout.getvalue())

    def test_feature_tasks_cli_output_creates_missing_parent_directories(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output_file = root / "nested" / "reports" / "tasks.txt"
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "tasks",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertTrue(output_file.exists())
            self.assertIn("Wrote feature task list", output.getvalue())
            self.assertIn(
                "Feature tasks: add-dark-mode",
                output_file.read_text(encoding="utf-8"),
            )

    def test_feature_tasks_cli_does_not_require_gh_or_github_tokens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()
            fake_token = "secret-test-token"

            with patch.dict(os.environ, {"PATH": "", "GITHUB_TOKEN": fake_token}):
                with redirect_stdout(output):
                    returncode = main(
                        ["feature", "tasks", "add-dark-mode", str(root), "--json"]
                    )

            self.assertEqual(returncode, 0)
            self.assertNotIn(fake_token, output.getvalue())

    def test_build_feature_tasks_report_matches_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")

            report = build_feature_tasks_report(root, "add-dark-mode")

            self.assertEqual(report.summary["total"], 1)
            self.assertEqual(report.tasks[0].id, "T001")

    def test_feature_task_issues_cli_text_and_json_outputs_ready_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)

            text_output = StringIO()
            with redirect_stdout(text_output):
                text_returncode = main(
                    ["feature", "task-issues", "add-dark-mode", str(root)]
                )

            text = text_output.getvalue()
            self.assertEqual(text_returncode, 0)
            self.assertIn("Feature task issue drafts: add-dark-mode", text)
            self.assertIn("Summary: tasks=2 done=2 open=0 issues=2", text)
            self.assertIn("Title: [add-dark-mode] T001: Implement theme storage.", text)
            self.assertIn("## Acceptance Criteria", text)
            self.assertIn("- [x] AC001 specs/features/add-dark-mode.md:8 Users can enable dark mode.", text)
            self.assertIn("## Key Commands", text)
            self.assertIn("specspine feature task-issues add-dark-mode . --json", text)

            json_output = StringIO()
            with redirect_stdout(json_output):
                json_returncode = main(
                    ["feature", "task-issues", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(json_output.getvalue())
            self.assertEqual(json_returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["status"], "validated")
            self.assertFalse(payload["source_missing"])
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(payload["summary"], {"done": 2, "issue_total": 2, "open": 0, "total": 2})
            self.assertEqual(len(payload["issues"]), 2)
            self.assertEqual(payload["issues"][0]["task_id"], "T001")
            self.assertEqual(payload["issues"][0]["task_text"], "Implement theme storage.")
            self.assertTrue(payload["issues"][0]["task_done"])
            self.assertEqual(payload["issues"][0]["source_file"], "execution/features/add-dark-mode.md")
            self.assertEqual(payload["issues"][0]["line"], 8)
            self.assertIn("## Source", payload["issues"][0]["body"])
            self.assertIn(
                "specspine feature trace add-dark-mode . --json",
                payload["recommended_commands"],
            )

    def test_feature_task_issues_handles_missing_execution_partial_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            (root / "execution" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "task-issues", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["source_missing"])
            self.assertEqual(payload["issues"], [])
            self.assertEqual(payload["summary"], {"done": 0, "issue_total": 0, "open": 0, "total": 0})
            self.assertEqual(
                payload["missing_files"],
                ["execution/features/add-dark-mode.md"],
            )

    def test_feature_task_issues_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    ["feature", "task-issues", "add-dark-mode", str(root)]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("No feature files found", stderr.getvalue())
            self.assertIn("missing execution/features/add-dark-mode.md", stderr.getvalue())

    def test_feature_task_issues_invalid_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "task-issues", "BadSlug", str(root)])

            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_feature_task_issues_output_file_overwrite_force_and_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output_file = root / "task-issues.md"
            output_file.write_text("existing\n", encoding="utf-8")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "task-issues",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("Output file already exists", stderr.getvalue())
            self.assertEqual(output_file.read_text(encoding="utf-8"), "existing\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "task-issues",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--output",
                        str(output_file),
                        "--force",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertIn(
                "Feature task issue drafts: add-dark-mode",
                output_file.read_text(encoding="utf-8"),
            )
            self.assertNotIn("Wrote feature task issue draft package", stdout.getvalue())

    def test_feature_task_issues_does_not_require_gh_tokens_network_or_subprocess(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            add_feature_metadata(root)
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
                        ["feature", "task-issues", "add-dark-mode", str(root), "--json"]
                    )

            self.assertEqual(returncode, 0)
            subprocess_run.assert_not_called()
            subprocess_popen.assert_not_called()
            urlopen.assert_not_called()
            create_connection.assert_not_called()
            socket_connect.assert_not_called()
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-api-token", output.getvalue())
            self.assertNotIn("secret-github-pat", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["summary"]["issue_total"], 2)

    def test_feature_sync_plan_cli_json_outputs_reviewable_github_commands(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            add_feature_metadata(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "sync-plan", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(
                set(payload),
                {
                    "blocking_checks",
                    "commands",
                    "feature_id",
                    "gaps",
                    "metadata",
                    "missing_files",
                    "notes",
                    "ready",
                    "recommended_commands",
                    "source_files",
                    "status",
                    "summary",
                },
            )
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["status"], "validated")
            self.assertTrue(payload["ready"])
            self.assertEqual(
                payload["metadata"],
                {
                    "effort": "M",
                    "milestone": "Beta",
                    "owner": "Platform Team",
                    "priority": "high",
                    "project": "Triage Board",
                    "target_release": "2026.2",
                },
            )
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(payload["gaps"], [])
            self.assertEqual(payload["blocking_checks"], [])
            self.assertEqual(
                payload["summary"],
                {
                    "commands_total": 4,
                    "issue_commands": 1,
                    "notes_total": 7,
                    "pull_request_commands": 1,
                    "task_issue_commands": 2,
                },
            )
            self.assertEqual(
                [command["kind"] for command in payload["commands"]],
                ["issue", "task-issue", "task-issue", "pull-request"],
            )
            expected_command_keys = {
                "argv",
                "body",
                "body_source",
                "creates_remote",
                "description",
                "id",
                "kind",
                "requires_network",
                "requires_token",
                "safe_to_auto_run",
            }
            for command in payload["commands"]:
                self.assertEqual(set(command), expected_command_keys)
                self.assertTrue(command["body"].strip())
                self.assertIn("## Metadata", command["body"])
                self.assertIn("- Target Release: 2026.2", command["body"])
                self.assertTrue(
                    command["body_source"].startswith(
                        ".specspine/sync-plan/add-dark-mode/"
                    )
                )
                self.assertTrue(command["creates_remote"])
                self.assertTrue(command["requires_token"])
                self.assertTrue(command["requires_network"])
                self.assertFalse(command["safe_to_auto_run"])

            feature_issue = payload["commands"][0]
            self.assertEqual(feature_issue["id"], "github.issue.feature")
            self.assertEqual(
                feature_issue["argv"],
                [
                    "gh",
                    "issue",
                    "create",
                    "--title",
                    "Add dark mode",
                    "--body-file",
                    ".specspine/sync-plan/add-dark-mode/feature-issue.md",
                    "--label",
                    "specspine",
                    "--label",
                    "feature:add-dark-mode",
                    "--label",
                    "status:validated",
                    "--label",
                    "priority:high",
                ],
            )
            self.assertEqual(feature_issue["body_source"], ".specspine/sync-plan/add-dark-mode/feature-issue.md")
            self.assertIn("## Acceptance Criteria", feature_issue["body"])
            self.assertTrue(feature_issue["creates_remote"])
            self.assertTrue(feature_issue["requires_token"])
            self.assertTrue(feature_issue["requires_network"])
            self.assertFalse(feature_issue["safe_to_auto_run"])

            task_issue = payload["commands"][1]
            self.assertEqual(task_issue["id"], "github.task_issue.T001")
            self.assertEqual(task_issue["kind"], "task-issue")
            self.assertEqual(
                task_issue["body_source"],
                ".specspine/sync-plan/add-dark-mode/task-issues/T001.md",
            )
            self.assertIn("## Source", task_issue["body"])
            self.assertTrue(
                any("[add-dark-mode] T001" in arg for arg in task_issue["argv"])
            )
            self.assertIn("task", task_issue["argv"])
            self.assertIn(".specspine/sync-plan/add-dark-mode/task-issues/T001.md", task_issue["argv"])
            self.assertEqual(
                task_issue["argv"][-8:],
                [
                    "--label",
                    "specspine",
                    "--label",
                    "feature:add-dark-mode",
                    "--label",
                    "task",
                    "--label",
                    "status:validated",
                ],
            )

            pull_request = payload["commands"][-1]
            self.assertEqual(pull_request["id"], "github.pull_request")
            self.assertEqual(pull_request["kind"], "pull-request")
            self.assertEqual(
                pull_request["argv"],
                [
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    "Implement Add dark mode",
                    "--body-file",
                    ".specspine/sync-plan/add-dark-mode/pull-request.md",
                    "--draft",
                    "--label",
                    "specspine",
                    "--label",
                    "feature:add-dark-mode",
                    "--label",
                    "status:validated",
                ],
            )
            self.assertNotIn("--dry-run", pull_request["argv"])
            self.assertEqual(pull_request["body_source"], ".specspine/sync-plan/add-dark-mode/pull-request.md")
            self.assertIn("## Summary", pull_request["body"])

            flat_argv = [
                arg
                for command in payload["commands"]
                for arg in command["argv"]
            ]
            self.assertNotIn("--assignee", flat_argv)
            self.assertNotIn("--milestone", flat_argv)
            self.assertNotIn("--project", flat_argv)
            self.assertNotIn("--field", flat_argv)
            self.assertNotIn("Beta", flat_argv)
            self.assertNotIn("2026.2", flat_argv)
            self.assertNotIn("Triage Board", flat_argv)
            self.assertNotIn("M", flat_argv)
            notes_text = "\n".join(payload["notes"])
            self.assertIn("did not execute gh", notes_text)
            self.assertIn("authenticate GitHub CLI", notes_text)
            self.assertIn("project scope", notes_text)
            self.assertIn("dry-run may still push", notes_text)
            self.assertIn("priority:high", notes_text)
            self.assertIn("Owner 'Platform Team'", notes_text)
            self.assertIn("not automatically mapped to --assignee", notes_text)
            self.assertIn(
                "specspine feature issue add-dark-mode . --json",
                payload["recommended_commands"],
            )
            self.assertIn(
                "specspine feature task-issues add-dark-mode . --json",
                payload["recommended_commands"],
            )
            self.assertIn(
                "specspine feature pr add-dark-mode . --json",
                payload["recommended_commands"],
            )
            self.assertIn(
                "specspine feature ready add-dark-mode . --json",
                payload["recommended_commands"],
            )
            self.assertIn("specspine adapters lifecycle . --json", payload["recommended_commands"])

    def test_feature_sync_plan_default_unassigned_owner_is_not_assigned(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "sync-plan", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            flat_argv = [
                arg
                for command in payload["commands"]
                for arg in command["argv"]
            ]
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["metadata"]["owner"], "unassigned")
            self.assertNotIn("--assignee", flat_argv)
            self.assertTrue(
                any(
                    "not automatically mapped to --assignee" in note
                    for note in payload["notes"]
                )
            )

    def test_feature_sync_plan_cli_text_output_contains_safe_command_lines_and_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            add_feature_metadata(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "sync-plan", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("# GitHub Sync Plan: add-dark-mode", text)
            self.assertIn("## Summary", text)
            self.assertIn("- Priority: high", text)
            self.assertIn("- Owner: Platform Team", text)
            self.assertIn("did not execute gh", text)
            self.assertIn("authenticate GitHub CLI", text)
            self.assertIn("project scope", text)
            self.assertIn("dry-run may still push", text)
            self.assertIn("not automatically mapped to --assignee", text)
            self.assertIn("Creates remote: yes", text)
            self.assertIn("Requires token: yes", text)
            self.assertIn("Requires network: yes", text)
            self.assertIn("Safe to auto-run: no", text)
            self.assertIn("Command: `gh issue create --title 'Add dark mode'", text)
            self.assertIn("Command: `gh pr create --title 'Implement Add dark mode'", text)
            self.assertIn("--draft", text)
            for line in text.splitlines():
                if line.startswith("- Command:"):
                    self.assertNotIn("--dry-run", line)
            self.assertIn("specspine feature sync-plan add-dark-mode . --json", text)

    def test_feature_sync_plan_output_file_overwrite_force_and_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            add_feature_metadata(root)
            output_file = root / "reports" / "sync-plan.md"
            output_file.parent.mkdir(parents=True)
            output_file.write_text("existing\n", encoding="utf-8")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "sync-plan",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("Output file already exists", stderr.getvalue())
            self.assertEqual(output_file.read_text(encoding="utf-8"), "existing\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "sync-plan",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--output",
                        str(output_file),
                        "--force",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertIn(
                "# GitHub Sync Plan: add-dark-mode",
                output_file.read_text(encoding="utf-8"),
            )
            self.assertNotIn("Wrote feature sync plan", stdout.getvalue())

            text_output_file = root / "reports" / "sync-plan-text.md"
            stdout = StringIO()
            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "sync-plan",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(text_output_file),
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Wrote feature sync plan to", stdout.getvalue())
            self.assertIn(str(text_output_file.resolve()), stdout.getvalue())
            self.assertIn(
                "# GitHub Sync Plan: add-dark-mode",
                text_output_file.read_text(encoding="utf-8"),
            )

    def test_feature_sync_plan_output_dir_writes_reviewable_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            add_feature_metadata(root)
            output_dir = root / "sync-artifacts"
            stdout = StringIO()

            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "sync-plan",
                        "add-dark-mode",
                        str(root),
                        "--output-dir",
                        str(output_dir),
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Wrote feature sync plan artifacts", stdout.getvalue())
            expected_files = {
                "manifest.json",
                "feature-issue.md",
                "task-issues/T001.md",
                "task-issues/T002.md",
                "pull-request.md",
                "commands.sh",
            }
            self.assertEqual(
                {
                    str(path.relative_to(output_dir))
                    for path in output_dir.rglob("*")
                    if path.is_file()
                },
                expected_files,
            )

            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["feature_id"], "add-dark-mode")
            self.assertEqual(manifest["metadata"]["milestone"], "Beta")
            self.assertEqual(manifest["metadata"]["target_release"], "2026.2")
            self.assertIn(
                "- Project: Triage Board",
                (output_dir / "feature-issue.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "- Effort: M",
                (output_dir / "pull-request.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(manifest["artifact_version"], 1)
            self.assertEqual(manifest["artifact_root"], ".")
            self.assertEqual(manifest["artifacts"]["manifest"], "manifest.json")
            self.assertEqual(manifest["artifacts"]["feature_issue"], "feature-issue.md")
            self.assertEqual(manifest["artifacts"]["pull_request"], "pull-request.md")
            self.assertEqual(
                manifest["artifacts"]["task_issues"],
                [
                    {
                        "command_id": "github.task_issue.T001",
                        "path": "task-issues/T001.md",
                        "task_id": "T001",
                    },
                    {
                        "command_id": "github.task_issue.T002",
                        "path": "task-issues/T002.md",
                        "task_id": "T002",
                    },
                ],
            )

            commands_by_id = {
                command["id"]: command
                for command in manifest["commands"]
            }
            self.assertEqual(
                commands_by_id["github.issue.feature"]["body_file"],
                "feature-issue.md",
            )
            self.assertEqual(
                commands_by_id["github.task_issue.T001"]["artifact_path"],
                "task-issues/T001.md",
            )
            self.assertEqual(
                commands_by_id["github.pull_request"]["body_file"],
                "pull-request.md",
            )
            self.assertIn(
                "## Acceptance Criteria",
                (output_dir / "feature-issue.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "Implement theme storage.",
                (output_dir / "task-issues" / "T001.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "## Summary",
                (output_dir / "pull-request.md").read_text(encoding="utf-8"),
            )

            commands_sh = (output_dir / "commands.sh").read_text(encoding="utf-8")
            self.assertIn("review-only / do not run blindly", commands_sh)
            self.assertIn("gh issue create --title 'Add dark mode' --body-file feature-issue.md", commands_sh)
            self.assertIn("gh issue create --title '[add-dark-mode] T001:", commands_sh)
            self.assertIn("--body-file task-issues/T001.md", commands_sh)
            self.assertIn("gh pr create --title 'Implement Add dark mode'", commands_sh)
            self.assertIn("--body-file pull-request.md", commands_sh)
            self.assertIn("--draft", commands_sh)
            self.assertNotIn("--dry-run", commands_sh)
            self.assertNotIn("--dry-run", json.dumps(manifest))
            self.assertNotIn("--assignee", commands_sh)
            for command in manifest["commands"]:
                self.assertTrue(command["creates_remote"])
                self.assertTrue(command["requires_token"])
                self.assertTrue(command["requires_network"])
                self.assertFalse(command["safe_to_auto_run"])

    def test_feature_sync_plan_json_stdout_and_output_dir_both_work(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output_dir = root / "sync-artifacts"
            stdout = StringIO()

            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "sync-plan",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--output-dir",
                        str(output_dir),
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertNotIn("artifact_version", payload)
            expected_command_keys = {
                "argv",
                "body",
                "body_source",
                "creates_remote",
                "description",
                "id",
                "kind",
                "requires_network",
                "requires_token",
                "safe_to_auto_run",
            }
            for command in payload["commands"]:
                self.assertEqual(set(command), expected_command_keys)
                self.assertNotIn("artifact_path", command)
                self.assertNotIn("body_file", command)
            self.assertTrue((output_dir / "manifest.json").exists())
            self.assertTrue((output_dir / "commands.sh").exists())

    def test_feature_sync_plan_output_dir_overwrite_requires_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output_dir = root / "sync-artifacts"
            output_dir.mkdir()
            unknown_file = output_dir / "keep-local-note.txt"
            unknown_file.write_text("keep me\n", encoding="utf-8")
            manifest = output_dir / "manifest.json"
            manifest.write_text("existing\n", encoding="utf-8")
            feature_issue = output_dir / "feature-issue.md"
            feature_issue.write_text("stale feature issue\n", encoding="utf-8")
            commands_sh = output_dir / "commands.sh"
            commands_sh.write_text("stale command script\n", encoding="utf-8")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "sync-plan",
                        "add-dark-mode",
                        str(root),
                        "--output-dir",
                        str(output_dir),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("Sync plan artifact files already exist", stderr.getvalue())
            self.assertEqual(manifest.read_text(encoding="utf-8"), "existing\n")
            self.assertEqual(feature_issue.read_text(encoding="utf-8"), "stale feature issue\n")
            self.assertEqual(commands_sh.read_text(encoding="utf-8"), "stale command script\n")
            self.assertEqual(unknown_file.read_text(encoding="utf-8"), "keep me\n")

            with redirect_stdout(StringIO()):
                returncode = main(
                    [
                        "feature",
                        "sync-plan",
                        "add-dark-mode",
                        str(root),
                        "--output-dir",
                        str(output_dir),
                        "--force",
                    ]
                )

            self.assertEqual(returncode, 0)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertIn(
                "## Acceptance Criteria",
                feature_issue.read_text(encoding="utf-8"),
            )
            self.assertIn(
                "review-only / do not run blindly",
                commands_sh.read_text(encoding="utf-8"),
            )
            self.assertEqual(unknown_file.read_text(encoding="utf-8"), "keep me\n")

    def test_feature_sync_plan_output_dir_does_not_read_tokens_call_network_or_subprocess(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output_dir = root / "sync-artifacts"
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
                            "feature",
                            "sync-plan",
                            "add-dark-mode",
                            str(root),
                            "--json",
                            "--output-dir",
                            str(output_dir),
                        ]
                    )

            self.assertEqual(returncode, 0)
            subprocess_run.assert_not_called()
            subprocess_popen.assert_not_called()
            urlopen.assert_not_called()
            create_connection.assert_not_called()
            socket_connect.assert_not_called()
            combined = output.getvalue() + (output_dir / "commands.sh").read_text(encoding="utf-8")
            self.assertNotIn("secret-gh-token", combined)
            self.assertNotIn("secret-github-api-token", combined)
            self.assertNotIn("secret-github-pat", combined)
            self.assertNotIn("secret-github-token", combined)

    def test_feature_sync_plan_partial_bundle_returns_zero_with_missing_info(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root, status="implemented")
            add_feature_metadata(root)
            (root / "execution" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "sync-plan", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            gap_ids = {gap["id"] for gap in payload["gaps"]}
            self.assertEqual(returncode, 0)
            self.assertFalse(payload["ready"])
            self.assertEqual(
                payload["missing_files"],
                ["execution/features/add-dark-mode.md"],
            )
            self.assertIn("missing_file", gap_ids)
            self.assertEqual(payload["summary"]["commands_total"], 2)
            self.assertEqual(payload["summary"]["issue_commands"], 1)
            self.assertEqual(payload["summary"]["task_issue_commands"], 0)
            self.assertEqual(payload["summary"]["pull_request_commands"], 1)
            self.assertEqual(
                [command["kind"] for command in payload["commands"]],
                ["issue", "pull-request"],
            )
            self.assertTrue(payload["blocking_checks"])

    def test_feature_sync_plan_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                returncode = main(["feature", "sync-plan", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("No feature files found", stderr.getvalue())
            self.assertIn("missing specs/features/add-dark-mode.md", stderr.getvalue())

    def test_feature_sync_plan_invalid_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "sync-plan", "bad_slug", str(root)])

            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_feature_sync_plan_does_not_read_tokens_call_network_or_subprocess(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            add_feature_metadata(root)
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
                        "subprocess.call",
                        side_effect=AssertionError("subprocess called"),
                    ) as subprocess_call,
                    patch(
                        "subprocess.check_call",
                        side_effect=AssertionError("subprocess called"),
                    ) as subprocess_check_call,
                    patch(
                        "subprocess.check_output",
                        side_effect=AssertionError("subprocess called"),
                    ) as subprocess_check_output,
                    patch(
                        "os.system",
                        side_effect=AssertionError("subprocess called"),
                    ) as os_system,
                    patch(
                        "shutil.which",
                        side_effect=AssertionError("gh lookup called"),
                    ) as shutil_which,
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
                        ["feature", "sync-plan", "add-dark-mode", str(root), "--json"]
                    )

            self.assertEqual(returncode, 0)
            subprocess_run.assert_not_called()
            subprocess_popen.assert_not_called()
            subprocess_call.assert_not_called()
            subprocess_check_call.assert_not_called()
            subprocess_check_output.assert_not_called()
            os_system.assert_not_called()
            shutil_which.assert_not_called()
            urlopen.assert_not_called()
            create_connection.assert_not_called()
            socket_connect.assert_not_called()
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-api-token", output.getvalue())
            self.assertNotIn("secret-github-pat", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())
            payload = json.loads(output.getvalue())
            self.assertFalse(any(command["safe_to_auto_run"] for command in payload["commands"]))

    def test_feature_trace_cli_text_and_json_outputs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            set_feature_status(root, "add-dark-mode", "validated")
            (root / "specs" / "features" / "add-dark-mode.md").write_text(
                "\n".join(
                    [
                        "# Add dark mode",
                        "",
                        "Feature ID: add-dark-mode",
                        "Status: validated",
                        "",
                        "## Acceptance Criteria",
                        "- [x] Users can enable dark mode.",
                        "- [ ] Users can return to light mode.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "execution" / "features" / "add-dark-mode.md").write_text(
                "\n".join(
                    [
                        "# Add dark mode Execution",
                        "",
                        "Feature ID: add-dark-mode",
                        "Status: validated",
                        "",
                        "## Tasks",
                        "- [x] Implement theme storage.",
                        "- [ ] Add theme tests.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "quality" / "features" / "add-dark-mode.md").write_text(
                "\n".join(
                    [
                        "# Add dark mode Quality",
                        "",
                        "Feature ID: add-dark-mode",
                        "Status: validated",
                        "",
                        "## Required Checks",
                        "- [x] Unit tests pass.",
                        "- [ ] Documentation updated.",
                        "",
                        "## Test Plan",
                        "- Run `python -m unittest`.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            text_output = StringIO()
            with redirect_stdout(text_output):
                text_returncode = main(
                    ["feature", "trace", "add-dark-mode", str(root)]
                )

            text = text_output.getvalue()
            self.assertEqual(text_returncode, 0)
            self.assertIn("Feature trace: add-dark-mode", text)
            self.assertIn("Status: validated", text)
            self.assertIn("Summary: total=6 done=3 open=3", text)
            self.assertIn("Counts: ac=2 tasks=2 quality=2 test_plan=1", text)
            self.assertIn(
                "- [x] AC001 specs/features/add-dark-mode.md:7 Users can enable dark mode.",
                text,
            )
            self.assertIn(
                "- [ ] T002 execution/features/add-dark-mode.md:8 Add theme tests.",
                text,
            )
            self.assertIn(
                "- [ ] Q002 quality/features/add-dark-mode.md:8 Documentation updated.",
                text,
            )
            self.assertIn(
                "- TP001 quality/features/add-dark-mode.md:11 - Run `python -m unittest`.",
                text,
            )
            self.assertIn("- None.", text)

            json_output = StringIO()
            with redirect_stdout(json_output):
                json_returncode = main(
                    ["feature", "trace", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(json_output.getvalue())
            self.assertEqual(json_returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["status"], "validated")
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(payload["gaps"], [])
            self.assertEqual(payload["summary"]["total"], 6)
            self.assertEqual(payload["summary"]["done"], 3)
            self.assertEqual(payload["summary"]["open"], 3)
            self.assertEqual(payload["summary"]["test_plan"], {"total": 1})
            self.assertEqual(payload["acceptance_criteria"][0]["id"], "AC001")
            self.assertEqual(payload["tasks"][1]["id"], "T002")
            self.assertEqual(payload["quality_checks"][0]["id"], "Q001")
            self.assertEqual(payload["test_plan"][0]["id"], "TP001")
            self.assertEqual(
                payload["sources"]["spec"],
                {"exists": True, "path": "specs/features/add-dark-mode.md"},
            )

    def test_feature_trace_cli_reports_partial_bundle_gaps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            (root / "specs" / "features" / "add-dark-mode.md").write_text(
                "# Add dark mode\n\nFeature ID: add-dark-mode\nStatus: proposed\n",
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "trace", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            gap_ids = {gap["id"] for gap in payload["gaps"]}
            self.assertEqual(returncode, 0)
            self.assertEqual(
                payload["missing_files"],
                ["quality/features/add-dark-mode.md"],
            )
            self.assertIn("missing_file", gap_ids)
            self.assertIn("missing_acceptance_criteria", gap_ids)
            self.assertIn("missing_required_checks", gap_ids)
            self.assertIn("missing_test_plan", gap_ids)

    def test_feature_trace_cli_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "trace", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 1)
            self.assertIn("No feature files found", stderr.getvalue())
            self.assertIn("missing specs/features/add-dark-mode.md", stderr.getvalue())

    def test_feature_trace_cli_output_file_overwrite_force_and_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output_file = root / "trace.txt"
            output_file.write_text("existing\n", encoding="utf-8")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "trace",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("Output file already exists", stderr.getvalue())
            self.assertEqual(output_file.read_text(encoding="utf-8"), "existing\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "trace",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--output",
                        str(output_file),
                        "--force",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertIn("Feature trace: add-dark-mode", output_file.read_text(encoding="utf-8"))
            self.assertNotIn("Wrote feature trace handoff", stdout.getvalue())

    def test_feature_trace_cli_output_file_text_mode_writes_handoff(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output_file = root / "artifacts" / "trace.txt"
            stdout = StringIO()

            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "trace",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertEqual(
                stdout.getvalue(),
                f"Wrote feature trace handoff to {output_file.resolve()}\n",
            )
            text = output_file.read_text(encoding="utf-8")
            self.assertIn("Feature trace: add-dark-mode", text)
            self.assertIn("Sources:", text)
            self.assertNotIn("Feature trace: add-dark-mode", stdout.getvalue())

    def test_feature_trace_cli_does_not_require_gh_or_github_tokens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()

            with patch.dict(
                os.environ,
                {
                    "GH_TOKEN": "secret-gh-token",
                    "GITHUB_TOKEN": "secret-github-token",
                    "PATH": "",
                },
            ):
                with patch("subprocess.run", side_effect=AssertionError("gh called")):
                    with redirect_stdout(output):
                        returncode = main(
                            ["feature", "trace", "add-dark-mode", str(root), "--json"]
                        )

            self.assertEqual(returncode, 0)
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())

    def test_parse_release_readiness_extracts_checklist_items(self) -> None:
        content = "\n".join(
            [
                "# Add dark mode Quality",
                "",
                "## Required Checks",
                "- [x] Unit tests pass.",
                "",
                "## Release Readiness",
                "",
                "- [x] Reviewer signed off.",
                "* [ ] Rollout notes are published.",
                "- plain bullet ignored",
            ]
        )

        items = parse_release_readiness(
            content,
            source_file="quality/features/add-dark-mode.md",
        )

        self.assertEqual([item.id for item in items], ["RR001", "RR002"])
        self.assertEqual([item.done for item in items], [True, False])
        self.assertEqual([item.line for item in items], [8, 9])

    def test_parse_release_readiness_stops_at_next_heading(self) -> None:
        content = "\n".join(
            [
                "# Add dark mode Quality",
                "",
                "## Release Readiness",
                "",
                "- [x] Reviewer signed off.",
                "",
                "## Review Notes",
                "",
                "- [ ] This review note is not release readiness.",
            ]
        )

        items = parse_release_readiness(
            content,
            source_file="quality/features/add-dark-mode.md",
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, "RR001")
        self.assertEqual(items[0].text, "Reviewer signed off.")

    def test_feature_ready_cli_returns_zero_for_ready_bundle_text_and_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)

            text_output = StringIO()
            with redirect_stdout(text_output):
                text_returncode = main(["feature", "ready", "add-dark-mode", str(root)])

            self.assertEqual(text_returncode, 0)
            self.assertIn("Feature readiness: add-dark-mode", text_output.getvalue())
            self.assertIn("Ready: yes", text_output.getvalue())
            self.assertIn("Summary: pass=9 fail=0 total=9", text_output.getvalue())
            self.assertIn("- None.", text_output.getvalue())

            json_output = StringIO()
            with redirect_stdout(json_output):
                json_returncode = main(
                    ["feature", "ready", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(json_output.getvalue())
            self.assertEqual(json_returncode, 0)
            self.assertTrue(payload["ready"])
            self.assertEqual(payload["status"], "validated")
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(payload["gaps"], [])
            self.assertEqual(payload["blocking_checks"], [])
            self.assertNotIn("coverage_required", payload)
            self.assertEqual(payload["summary"], {"fail": 0, "pass": 9, "total": 9})
            self.assertEqual(
                [check["id"] for check in payload["checks"]],
                [
                    "feature.bundle_files",
                    "feature.status_consistency",
                    "feature.lifecycle_status",
                    "feature.trace_gaps",
                    "feature.acceptance_criteria",
                    "feature.tasks",
                    "feature.required_checks",
                    "feature.test_plan",
                    "feature.release_readiness",
                ],
            )

    def test_feature_ready_default_does_not_require_coverage_links(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)

            output = StringIO()
            with redirect_stdout(output):
                returncode = main(
                    ["feature", "ready", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["ready"])
            self.assertNotIn("coverage_required", payload)
            self.assertNotIn(
                "feature.test_coverage",
                [check["id"] for check in payload["checks"]],
            )

    def test_feature_ready_require_coverage_passes_with_checked_existing_targets(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            write_coverage_target(root)
            insert_test_coverage(
                root,
                [
                    "- [x] AC001 -> tests/test_feature_ready_coverage.py::test_enable_dark",
                    "- [x] AC002 -> tests/test_feature_ready_coverage.py",
                ],
            )

            text_output = StringIO()
            with redirect_stdout(text_output):
                text_returncode = main(
                    [
                        "feature",
                        "ready",
                        "add-dark-mode",
                        str(root),
                        "--require-coverage",
                    ]
                )

            text = text_output.getvalue()
            self.assertEqual(text_returncode, 0)
            self.assertIn("Ready: yes", text)
            self.assertIn("Summary: pass=10 fail=0 total=10", text)
            self.assertIn("- None.", text)

            json_output = StringIO()
            with redirect_stdout(json_output):
                json_returncode = main(
                    [
                        "feature",
                        "ready",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--require-coverage",
                    ]
                )

            payload = json.loads(json_output.getvalue())
            checks = {check["id"]: check for check in payload["checks"]}
            self.assertEqual(json_returncode, 0)
            self.assertTrue(payload["ready"])
            self.assertTrue(payload["coverage_required"])
            self.assertEqual(payload["summary"], {"fail": 0, "pass": 10, "total": 10})
            self.assertEqual(checks["feature.test_coverage"]["status"], "pass")
            self.assertEqual(
                checks["feature.test_coverage"]["message"],
                "Completed local test coverage links exist for all acceptance criteria.",
            )

    def test_feature_ready_require_coverage_fails_for_missing_open_or_missing_target_links(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            write_coverage_target(root)
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace(
                    "- [x] Users can return to light mode.",
                    "- [x] Users can return to light mode.\n"
                    "- [x] Users can preview contrast before saving.",
                ),
                encoding="utf-8",
            )
            insert_test_coverage(
                root,
                [
                    "- [ ] AC001 -> tests/test_feature_ready_coverage.py",
                    "- [x] AC002 -> tests/missing_feature_ready_coverage.py",
                ],
            )

            json_output = StringIO()
            with redirect_stdout(json_output):
                json_returncode = main(
                    [
                        "feature",
                        "ready",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--require-coverage",
                    ]
                )

            payload = json.loads(json_output.getvalue())
            blocking = {check["id"]: check for check in payload["blocking_checks"]}
            self.assertEqual(json_returncode, 1)
            self.assertFalse(payload["ready"])
            self.assertEqual(payload["summary"], {"fail": 1, "pass": 9, "total": 10})
            self.assertIn("feature.test_coverage", blocking)
            self.assertIn("AC001", blocking["feature.test_coverage"]["message"])
            self.assertIn("AC002", blocking["feature.test_coverage"]["message"])
            self.assertIn("AC003", blocking["feature.test_coverage"]["message"])

            text_output = StringIO()
            with redirect_stdout(text_output):
                text_returncode = main(
                    [
                        "feature",
                        "ready",
                        "add-dark-mode",
                        str(root),
                        "--require-coverage",
                    ]
                )

            text = text_output.getvalue()
            self.assertEqual(text_returncode, 1)
            self.assertIn("Ready: no", text)
            self.assertIn("feature.test_coverage", text)
            self.assertIn("AC001, AC002, AC003", text)

    def test_feature_ready_require_coverage_fails_for_absolute_target_and_wrong_ac_id(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            write_coverage_target(root)
            absolute_target = root / "tests" / "test_feature_ready_coverage.py"
            insert_test_coverage(
                root,
                [
                    f"- [x] AC001 -> {absolute_target}",
                    "- [x] AC999 -> tests/test_feature_ready_coverage.py",
                ],
            )

            output = StringIO()
            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "ready",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--require-coverage",
                    ]
                )

            payload = json.loads(output.getvalue())
            blocking = {check["id"]: check for check in payload["blocking_checks"]}
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ready"])
            self.assertEqual(payload["summary"], {"fail": 1, "pass": 9, "total": 10})
            self.assertIn("feature.test_coverage", blocking)
            self.assertIn("AC001", blocking["feature.test_coverage"]["message"])
            self.assertIn("AC002", blocking["feature.test_coverage"]["message"])
            self.assertNotIn("AC999", blocking["feature.test_coverage"]["message"])

    def test_feature_ready_require_coverage_missing_bundle_does_not_crash(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "ready",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--require-coverage",
                    ]
                )

            payload = json.loads(output.getvalue())
            checks = {check["id"]: check for check in payload["checks"]}
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ready"])
            self.assertTrue(payload["coverage_required"])
            self.assertIn("feature.bundle_files", checks)
            self.assertIn("feature.test_coverage", checks)

    def test_feature_ready_require_coverage_partial_bundle_does_not_crash(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "ready",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--require-coverage",
                    ]
                )

            payload = json.loads(output.getvalue())
            checks = {check["id"]: check for check in payload["checks"]}
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ready"])
            self.assertTrue(payload["coverage_required"])
            self.assertIn("quality/features/add-dark-mode.md", payload["missing_files"])
            self.assertIn("feature.bundle_files", checks)
            self.assertIn("feature.test_coverage", checks)

    def test_feature_ready_require_coverage_does_not_read_tokens_or_call_network(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            write_coverage_target(root)
            insert_test_coverage(
                root,
                [
                    "- [x] AC001 -> tests/test_feature_ready_coverage.py",
                    "- [x] AC002 -> tests/test_feature_ready_coverage.py",
                ],
            )
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
                            "feature",
                            "ready",
                            "add-dark-mode",
                            str(root),
                            "--json",
                            "--require-coverage",
                        ]
                    )

            self.assertEqual(returncode, 0)
            subprocess_run.assert_not_called()
            subprocess_popen.assert_not_called()
            urlopen.assert_not_called()
            create_connection.assert_not_called()
            socket_connect.assert_not_called()
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-api-token", output.getvalue())
            self.assertNotIn("secret-github-pat", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())

    def test_feature_handoff_cli_text_and_json_outputs_ready_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)

            text_output = StringIO()
            with redirect_stdout(text_output):
                text_returncode = main(
                    ["feature", "handoff", "add-dark-mode", str(root)]
                )

            text = text_output.getvalue()
            self.assertEqual(text_returncode, 0)
            self.assertIn("Feature handoff: add-dark-mode", text)
            self.assertIn("Status: validated", text)
            self.assertIn("Ready: yes", text)
            self.assertIn(
                "Counts: trace=6/6/0 ready=9/0/9 tasks=2/2/0 gaps=0 blocking=0",
                text,
            )
            self.assertIn("Next actions:", text)
            self.assertIn("Review, merge, or archive", text)
            self.assertIn("Open tasks:\n- None.", text)
            self.assertIn("Blocking checks:\n- None.", text)
            self.assertIn("specspine feature handoff add-dark-mode . --json", text)

            json_output = StringIO()
            with redirect_stdout(json_output):
                json_returncode = main(
                    ["feature", "handoff", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(json_output.getvalue())
            self.assertEqual(json_returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["status"], "validated")
            self.assertTrue(payload["ready"])
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(payload["gaps"], [])
            self.assertEqual(payload["blocking_checks"], [])
            self.assertEqual(payload["summary"]["trace"]["total"], 6)
            self.assertEqual(payload["summary"]["trace"]["done"], 6)
            self.assertEqual(payload["summary"]["trace"]["open"], 0)
            self.assertEqual(payload["summary"]["ready"], {"fail": 0, "pass": 9, "total": 9})
            self.assertEqual(payload["summary"]["tasks"], {"done": 2, "open": 0, "total": 2})
            self.assertEqual(payload["summary"]["gaps"], {"total": 0})
            self.assertEqual(payload["summary"]["blocking_checks"], {"total": 0})
            self.assertEqual(payload["acceptance_criteria"][0]["id"], "AC001")
            self.assertEqual(payload["tasks"][0]["id"], "T001")
            self.assertEqual(payload["quality_checks"][0]["id"], "Q001")
            self.assertEqual(payload["test_plan"][0]["id"], "TP001")
            self.assertEqual(payload["release_readiness"][0]["id"], "RR001")
            self.assertEqual(
                payload["recommended_commands"],
                [
                    "specspine feature handoff add-dark-mode . --json",
                    "specspine feature tasks add-dark-mode . --json",
                    "specspine feature task-issues add-dark-mode . --json",
                    "specspine feature trace add-dark-mode . --json",
                    "specspine feature tests add-dark-mode . --json",
                    "specspine feature ready add-dark-mode . --json",
                    "specspine feature pr add-dark-mode . --json",
                    "specspine validate . --fusion --features",
                ],
            )

    def test_feature_handoff_cli_reports_partial_bundle_actions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root, status="implemented")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            execution = root / "execution" / "features" / "add-dark-mode.md"
            execution.write_text(
                execution.read_text(encoding="utf-8").replace(
                    "- [x] Add theme tests.",
                    "- [ ] Add theme tests.",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "handoff", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertFalse(payload["ready"])
            self.assertEqual(
                payload["missing_files"],
                ["quality/features/add-dark-mode.md"],
            )
            self.assertEqual(payload["summary"]["tasks"], {"done": 1, "open": 1, "total": 2})
            self.assertEqual(payload["summary"]["gaps"], {"total": 3})
            self.assertEqual(payload["summary"]["blocking_checks"]["total"], 6)
            self.assertEqual(
                payload["next_actions"],
                [
                    "Add missing peer file(s): quality/features/add-dark-mode.md",
                    "Fill missing trace section(s): missing_required_checks, missing_test_plan",
                    "Complete open task(s): T002",
                    (
                        "Resolve blocking readiness check(s): feature.bundle_files, "
                        "feature.trace_gaps, feature.tasks, "
                        "feature.required_checks, feature.test_plan, "
                        "feature.release_readiness"
                    ),
                ],
            )

    def test_feature_handoff_cli_text_reports_open_tasks_and_blocking_checks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root, status="implemented")
            execution = root / "execution" / "features" / "add-dark-mode.md"
            execution.write_text(
                execution.read_text(encoding="utf-8").replace(
                    "- [x] Add theme tests.",
                    "- [ ] Add theme tests.",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "handoff", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("Ready: no", text)
            self.assertIn("Open tasks:\n- T002 execution/features/add-dark-mode.md:9 Add theme tests.", text)
            self.assertIn("Blocking checks:\n- feature.tasks:", text)
            self.assertIn("Resolve blocking readiness check(s): feature.tasks", text)

    def test_feature_handoff_cli_missing_bundle_returns_packet_and_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "handoff", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertEqual(payload["status"], "unknown")
            self.assertFalse(payload["ready"])
            self.assertEqual(
                payload["missing_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            self.assertEqual(payload["summary"]["trace"]["total"], 0)
            self.assertEqual(payload["summary"]["tasks"], {"done": 0, "open": 0, "total": 0})
            self.assertEqual(
                payload["next_actions"],
                [
                    (
                        "Create or restore the native feature bundle: "
                        "specspine feature new add-dark-mode . --title \"...\" --why \"...\""
                    )
                ],
            )

    def test_feature_handoff_cli_invalid_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "handoff", "BadSlug", str(root)])

            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_feature_handoff_cli_output_file_overwrite_force_and_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output_file = root / "handoff.txt"
            output_file.write_text("existing\n", encoding="utf-8")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "handoff",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("Output file already exists", stderr.getvalue())
            self.assertEqual(output_file.read_text(encoding="utf-8"), "existing\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "handoff",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--output",
                        str(output_file),
                        "--force",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertIn("Feature handoff: add-dark-mode", output_file.read_text(encoding="utf-8"))
            self.assertNotIn("Wrote feature handoff packet", stdout.getvalue())

    def test_feature_handoff_cli_text_output_writes_packet(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output_file = root / "nested" / "handoff.txt"
            stdout = StringIO()

            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "handoff",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Wrote feature handoff packet", stdout.getvalue())
            self.assertIn(
                "Feature handoff: add-dark-mode",
                output_file.read_text(encoding="utf-8"),
            )

    def test_feature_handoff_does_not_require_gh_or_github_tokens(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output = StringIO()

            with patch.dict(
                os.environ,
                {
                    "GH_TOKEN": "secret-gh-token",
                    "GITHUB_TOKEN": "secret-github-token",
                    "PATH": "",
                },
            ):
                with patch("subprocess.run", side_effect=AssertionError("gh called")):
                    with redirect_stdout(output):
                        returncode = main(
                            ["feature", "handoff", "add-dark-mode", str(root), "--json"]
                        )

            self.assertEqual(returncode, 0)
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())

    def test_feature_tests_cli_text_and_json_outputs_ready_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)

            text_output = StringIO()
            with redirect_stdout(text_output):
                text_returncode = main(
                    ["feature", "tests", "add-dark-mode", str(root)]
                )

            text = text_output.getvalue()
            self.assertEqual(text_returncode, 0)
            self.assertIn("Feature test packet: add-dark-mode", text)
            self.assertIn("Feature: add-dark-mode", text)
            self.assertIn("Status: validated", text)
            self.assertIn("Ready: yes", text)
            self.assertIn("Sources:", text)
            self.assertIn("- [ok] specs/features/add-dark-mode.md", text)
            self.assertIn(
                "Summary: acceptance_criteria=2 test_cases=2 "
                "test_coverage=0 test_plan=1 quality_checks=2 gaps=0 blocking=0",
                text,
            )
            self.assertIn("Test Cases:", text)
            self.assertIn(
                "- [ ] TC001 -> AC001 [pending; links=None linked] "
                "specs/features/add-dark-mode.md:8 "
                "Pending behavior to test: Users can enable dark mode.",
                text,
            )
            self.assertIn("Test Coverage:\n- None linked.", text)
            self.assertIn("Existing Test Plan:", text)
            self.assertIn(
                "- TP001 quality/features/add-dark-mode.md:13 "
                "- Run `python -m unittest`.",
                text,
            )
            self.assertIn("Quality Checks:", text)
            self.assertIn(
                "- [x] Q001 quality/features/add-dark-mode.md:8 Unit tests pass.",
                text,
            )
            self.assertIn("Gaps:\n- None.", text)
            self.assertIn("Blocking Checks:\n- None.", text)
            self.assertIn("specspine feature tests add-dark-mode . --json", text)

            json_output = StringIO()
            with redirect_stdout(json_output):
                json_returncode = main(
                    ["feature", "tests", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(json_output.getvalue())
            self.assertEqual(json_returncode, 0)
            self.assertEqual(
                set(payload),
                {
                    "acceptance_criteria",
                    "blocking_checks",
                    "feature_id",
                    "gaps",
                    "metadata",
                    "missing_files",
                    "quality_checks",
                    "ready",
                    "recommended_commands",
                    "source_files",
                    "status",
                    "summary",
                    "test_cases",
                    "test_coverage",
                    "test_plan",
                },
            )
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["status"], "validated")
            self.assertTrue(payload["ready"])
            self.assertEqual(
                payload["source_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(payload["gaps"], [])
            self.assertEqual(payload["blocking_checks"], [])
            self.assertEqual(payload["acceptance_criteria"][0]["id"], "AC001")
            self.assertEqual(payload["test_plan"][0]["id"], "TP001")
            self.assertEqual(payload["quality_checks"][0]["id"], "Q001")
            self.assertEqual(
                len(payload["test_cases"]),
                len(payload["acceptance_criteria"]),
            )
            self.assertEqual(
                payload["test_cases"][0],
                {
                    "acceptance_criterion_id": "AC001",
                    "acceptance_criterion_text": "Users can enable dark mode.",
                    "behavior": (
                        "Pending behavior to test: Users can enable dark mode."
                    ),
                    "coverage": [],
                    "id": "TC001",
                    "line": 8,
                    "source_file": "specs/features/add-dark-mode.md",
                    "status": "pending",
                },
            )
            for test_case in payload["test_cases"]:
                self.assertEqual(
                    set(test_case),
                    {
                        "acceptance_criterion_id",
                        "acceptance_criterion_text",
                        "behavior",
                        "coverage",
                        "id",
                        "line",
                        "source_file",
                        "status",
                    },
                )
                self.assertTrue(
                    test_case["behavior"].startswith("Pending behavior to test: ")
                )
            self.assertEqual(
                payload["summary"]["test_cases"],
                {"total": 2},
            )
            self.assertEqual(
                payload["summary"]["test_coverage"],
                {"done": 0, "open": 0, "total": 0},
            )
            self.assertEqual(payload["test_coverage"], [])
            self.assertNotIn("tasks", payload)

    def test_build_feature_tests_report_maps_one_test_case_per_acceptance_criterion(
        self,
    ) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)

            report = build_feature_tests_report(root, "add-dark-mode")

            self.assertEqual(
                [test_case.id for test_case in report.test_cases],
                ["TC001", "TC002"],
            )
            self.assertEqual(
                [test_case.acceptance_criterion_id for test_case in report.test_cases],
                ["AC001", "AC002"],
            )
            self.assertEqual(
                [test_case.acceptance_criterion_text for test_case in report.test_cases],
                [
                    "Users can enable dark mode.",
                    "Users can return to light mode.",
                ],
            )
            self.assertEqual(
                {test_case.status for test_case in report.test_cases},
                {"pending"},
            )

    def test_feature_tests_report_links_coverage_to_matching_acceptance_criteria(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            (root / "tests").mkdir()
            (root / "tests" / "test_features.py").write_text(
                "class FeatureBundleTests:\n"
                "    def test_users_can_enable_dark_mode(self):\n"
                "        pass\n",
                encoding="utf-8",
            )
            quality = root / "quality" / "features" / "add-dark-mode.md"
            quality.write_text(
                quality.read_text(encoding="utf-8").replace(
                    "## Test Plan",
                    "\n".join(
                        [
                            "## Test Coverage",
                            "",
                            (
                                "- [x] AC001 -> "
                                "tests/test_features.py::FeatureBundleTests::"
                                "test_users_can_enable_dark_mode"
                            ),
                            "- [ ] AC002 -> tests/missing_theme_tests.py",
                            "",
                            "## Test Plan",
                        ]
                    ),
                ),
                encoding="utf-8",
            )

            report = build_feature_tests_report(root, "add-dark-mode")

            self.assertEqual(report.summary["test_coverage"], {"done": 1, "open": 1, "total": 2})
            self.assertEqual([link.id for link in report.test_coverage], ["COV001", "COV002"])
            self.assertEqual(report.test_coverage[0].target_path, "tests/test_features.py")
            self.assertTrue(report.test_coverage[0].target_exists)
            self.assertFalse(report.test_coverage[1].target_exists)
            self.assertEqual([test_case.status for test_case in report.test_cases], ["covered", "planned"])
            self.assertEqual([link.id for link in report.test_cases[0].coverage], ["COV001"])
            self.assertEqual([link.id for link in report.test_cases[1].coverage], ["COV002"])

    def test_feature_tests_cli_json_and_text_include_coverage_links(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            (root / "tests").mkdir()
            (root / "tests" / "test_features.py").write_text("", encoding="utf-8")
            quality = root / "quality" / "features" / "add-dark-mode.md"
            quality.write_text(
                quality.read_text(encoding="utf-8").replace(
                    "## Test Plan",
                    (
                        "## Test Coverage\n\n"
                        "- [x] AC001 -> tests/test_features.py::test_enable\n"
                        "- [ ] AC002 -> tests/missing.py\n\n"
                        "## Test Plan"
                    ),
                ),
                encoding="utf-8",
            )

            text_output = StringIO()
            with redirect_stdout(text_output):
                text_returncode = main(["feature", "tests", "add-dark-mode", str(root)])

            text = text_output.getvalue()
            self.assertEqual(text_returncode, 0)
            self.assertIn("test_coverage=2", text)
            self.assertIn(
                "- [ ] TC001 -> AC001 [covered; links=tests/test_features.py::test_enable]",
                text,
            )
            self.assertIn(
                "- [x] COV001 -> AC001 tests/test_features.py::test_enable (exists)",
                text,
            )
            self.assertIn(
                "- [ ] COV002 -> AC002 tests/missing.py (missing)",
                text,
            )

            json_output = StringIO()
            with redirect_stdout(json_output):
                json_returncode = main(
                    ["feature", "tests", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(json_output.getvalue())
            self.assertEqual(json_returncode, 0)
            self.assertEqual(payload["summary"]["test_coverage"], {"done": 1, "open": 1, "total": 2})
            self.assertEqual(payload["test_cases"][0]["status"], "covered")
            self.assertEqual(payload["test_cases"][1]["status"], "planned")
            self.assertEqual(payload["test_cases"][0]["coverage"][0]["id"], "COV001")
            self.assertEqual(payload["test_coverage"][0]["target_path"], "tests/test_features.py")
            self.assertTrue(payload["test_coverage"][0]["target_exists"])
            self.assertFalse(payload["test_coverage"][1]["target_exists"])

    def test_feature_tests_cli_reports_partial_bundle_gaps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root, status="implemented")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "tests", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            gap_ids = {gap["id"] for gap in payload["gaps"]}
            blocking_ids = {check["id"] for check in payload["blocking_checks"]}
            self.assertEqual(returncode, 0)
            self.assertFalse(payload["ready"])
            self.assertEqual(
                payload["source_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                ],
            )
            self.assertEqual(
                payload["missing_files"],
                ["quality/features/add-dark-mode.md"],
            )
            self.assertEqual([test_case["id"] for test_case in payload["test_cases"]], ["TC001", "TC002"])
            self.assertEqual(payload["test_plan"], [])
            self.assertEqual(payload["quality_checks"], [])
            self.assertIn("missing_file", gap_ids)
            self.assertIn("missing_required_checks", gap_ids)
            self.assertIn("missing_test_plan", gap_ids)
            self.assertIn("feature.bundle_files", blocking_ids)
            self.assertIn("feature.test_plan", blocking_ids)

    def test_feature_tests_cli_missing_bundle_returns_packet_and_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "tests", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertEqual(payload["status"], "unknown")
            self.assertFalse(payload["ready"])
            self.assertEqual(payload["source_files"], [])
            self.assertEqual(
                payload["missing_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            self.assertEqual(payload["acceptance_criteria"], [])
            self.assertEqual(payload["test_cases"], [])
            self.assertEqual(
                payload["summary"]["source_files"],
                {"total": 0},
            )

    def test_feature_tests_cli_invalid_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "tests", "BadSlug", str(root)])

            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_feature_tests_cli_output_file_overwrite_force_and_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output_file = root / "tests.txt"
            output_file.write_text("existing\n", encoding="utf-8")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "tests",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("Output file already exists", stderr.getvalue())
            self.assertEqual(output_file.read_text(encoding="utf-8"), "existing\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "tests",
                        "add-dark-mode",
                        str(root),
                        "--json",
                        "--output",
                        str(output_file),
                        "--force",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertIn(
                "Feature test packet: add-dark-mode",
                output_file.read_text(encoding="utf-8"),
            )
            self.assertNotIn("Wrote feature test packet", stdout.getvalue())

    def test_feature_tests_cli_text_output_writes_packet(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output_file = root / "nested" / "tests.txt"
            stdout = StringIO()

            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "tests",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(output_file),
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Wrote feature test packet", stdout.getvalue())
            self.assertIn(
                "Feature test packet: add-dark-mode",
                output_file.read_text(encoding="utf-8"),
            )

    def test_feature_tests_does_not_require_gh_network_tokens_or_dependencies(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output = StringIO()
            pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
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
                            "feature",
                            "tests",
                            "add-dark-mode",
                            str(root),
                            "--json",
                        ]
                    )

            self.assertEqual(returncode, 0)
            subprocess_run.assert_not_called()
            subprocess_popen.assert_not_called()
            urlopen.assert_not_called()
            create_connection.assert_not_called()
            socket_connect.assert_not_called()
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-api-token", output.getvalue())
            self.assertNotIn("secret-github-pat", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())
            self.assertNotIn("dependencies =", pyproject)

    def test_feature_ready_cli_reports_non_releasable_status_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root, status="proposed")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "ready", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            blocking_ids = [check["id"] for check in payload["blocking_checks"]]
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ready"])
            self.assertEqual(payload["status"], "proposed")
            self.assertEqual(payload["summary"], {"fail": 1, "pass": 8, "total": 9})
            self.assertEqual(blocking_ids, ["feature.lifecycle_status"])

    def test_feature_ready_cli_reports_trace_gaps_without_missing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8")
                .replace(
                    "- [x] Users can enable dark mode.",
                    "- Users can enable dark mode.",
                )
                .replace(
                    "- [x] Users can return to light mode.",
                    "- Users can return to light mode.",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "ready", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            blocking_ids = {check["id"] for check in payload["blocking_checks"]}
            gap_ids = {gap["id"] for gap in payload["gaps"]}
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ready"])
            self.assertEqual(payload["missing_files"], [])
            self.assertIn("missing_acceptance_criteria", gap_ids)
            self.assertIn("feature.trace_gaps", blocking_ids)
            self.assertIn("feature.acceptance_criteria", blocking_ids)

    def test_feature_ready_cli_reports_unfinished_required_checklists(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            spec = root / "specs" / "features" / "add-dark-mode.md"
            execution = root / "execution" / "features" / "add-dark-mode.md"
            quality = root / "quality" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace(
                    "- [x] Users can return to light mode.",
                    "- [ ] Users can return to light mode.",
                ),
                encoding="utf-8",
            )
            execution.write_text(
                execution.read_text(encoding="utf-8").replace(
                    "- [x] Add theme tests.",
                    "- [ ] Add theme tests.",
                ),
                encoding="utf-8",
            )
            quality.write_text(
                quality.read_text(encoding="utf-8").replace(
                    "- [x] Documentation updated.",
                    "- [ ] Documentation updated.",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "ready", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            blocking_ids = {check["id"] for check in payload["blocking_checks"]}
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ready"])
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(payload["gaps"], [])
            self.assertIn("feature.acceptance_criteria", blocking_ids)
            self.assertIn("feature.tasks", blocking_ids)
            self.assertIn("feature.required_checks", blocking_ids)

    def test_feature_ready_cli_reports_empty_test_plan(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            quality = root / "quality" / "features" / "add-dark-mode.md"
            quality.write_text(
                quality.read_text(encoding="utf-8").replace(
                    "## Test Plan\n\n- Run `python -m unittest`.\n\n## Release Readiness",
                    "## Test Plan\n\n\n## Release Readiness",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "ready", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            blocking_ids = {check["id"] for check in payload["blocking_checks"]}
            gap_ids = {gap["id"] for gap in payload["gaps"]}
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ready"])
            self.assertIn("missing_test_plan", gap_ids)
            self.assertIn("feature.trace_gaps", blocking_ids)
            self.assertIn("feature.test_plan", blocking_ids)

    def test_feature_ready_cli_reports_core_failures_for_partial_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "execution" / "features" / "add-dark-mode.md").unlink()
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            (root / "specs" / "features" / "add-dark-mode.md").write_text(
                "\n".join(
                    [
                        "# Add dark mode",
                        "",
                        "Feature ID: add-dark-mode",
                        "Status: proposed",
                        "",
                        "## Acceptance Criteria",
                        "",
                        "- [ ] Users can enable dark mode.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "ready", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            blocking_ids = {check["id"] for check in payload["blocking_checks"]}
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ready"])
            self.assertEqual(
                payload["missing_files"],
                [
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            self.assertIn("feature.bundle_files", blocking_ids)
            self.assertIn("feature.lifecycle_status", blocking_ids)
            self.assertIn("feature.trace_gaps", blocking_ids)
            self.assertIn("feature.acceptance_criteria", blocking_ids)
            self.assertIn("feature.tasks", blocking_ids)
            self.assertIn("feature.required_checks", blocking_ids)
            self.assertIn("feature.test_plan", blocking_ids)
            self.assertIn("feature.release_readiness", blocking_ids)

    def test_feature_ready_cli_reports_inconsistent_peer_statuses(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root, status="implemented")
            quality = root / "quality" / "features" / "add-dark-mode.md"
            quality.write_text(
                quality.read_text(encoding="utf-8").replace(
                    "Status: implemented",
                    "Status: validated",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "ready", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            blocking_ids = {check["id"] for check in payload["blocking_checks"]}
            self.assertEqual(returncode, 1)
            self.assertEqual(payload["status"], "mixed")
            self.assertIn("feature.status_consistency", blocking_ids)

    def test_feature_ready_cli_reports_open_release_readiness(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            quality = root / "quality" / "features" / "add-dark-mode.md"
            quality.write_text(
                quality.read_text(encoding="utf-8").replace(
                    "- [x] No release blockers remain.",
                    "- [ ] No release blockers remain.",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "ready", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 1)
            self.assertIn("Ready: no", output.getvalue())
            self.assertIn("feature.release_readiness", output.getvalue())

    def test_feature_ready_cli_invalid_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "ready", "BadSlug", str(root)])

            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_feature_ready_cli_missing_bundle_returns_report_and_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "ready", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ready"])
            self.assertEqual(payload["status"], "unknown")
            self.assertEqual(
                payload["missing_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            self.assertIn(
                "feature.bundle_files",
                {check["id"] for check in payload["blocking_checks"]},
            )

    def test_status_json_lists_feature_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")

            status = build_status(root)

            self.assertEqual(status["features"][0]["slug"], "add-dark-mode")
            self.assertTrue(status["features"][0]["complete"])
            self.assertEqual(status["features"][0]["status"], "proposed")
            self.assertTrue(status["features"][0]["status_consistent"])
            self.assertTrue(
                status["artifacts"]["specs/features/add-dark-mode.md"]["exists"]
            )

    def test_feature_status_cli_json_query_reports_consistent_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "status", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["status"], "proposed")
            self.assertTrue(payload["consistent"])
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(payload["files"]["spec"]["status"], "proposed")

    def test_feature_status_cli_json_query_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()
            stderr = StringIO()

            with redirect_stdout(output), redirect_stderr(stderr):
                returncode = main(
                    ["feature", "status", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIsNone(payload["status"])
            self.assertFalse(payload["consistent"])
            self.assertEqual(
                payload["missing_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            self.assertFalse(any(file["exists"] for file in payload["files"].values()))

    def test_feature_status_cli_text_query_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()
            stderr = StringIO()

            with redirect_stdout(output), redirect_stderr(stderr):
                returncode = main(["feature", "status", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 1)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIn("Feature add-dark-mode status: unknown (mixed/inconsistent)", text)
            self.assertIn("[missing] spec: specs/features/add-dark-mode.md (unknown)", text)

    def test_feature_status_cli_text_reports_mixed_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            execution = root / "execution" / "features" / "add-dark-mode.md"
            execution.write_text(
                execution.read_text(encoding="utf-8").replace(
                    "Status: proposed",
                    "Status: planned",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "status", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 0)
            self.assertIn("mixed/inconsistent", output.getvalue())
            self.assertIn("execution/features/add-dark-mode.md (planned)", output.getvalue())

    def test_feature_status_cli_set_updates_existing_peer_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "implemented",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["status"], "implemented")
            self.assertTrue(payload["consistent"])
            self.assertEqual(
                payload["transition"],
                {
                    "allowed": True,
                    "enforced": False,
                    "from": "proposed",
                    "to": "implemented",
                },
            )
            self.assertEqual(
                payload["updated_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            for relative_path in EXPECTED_FEATURE_FILES:
                content = (root / relative_path).read_text(encoding="utf-8")
                self.assertIn("Status: implemented", content)
                self.assertNotIn("Status: proposed", content)

    def test_feature_status_cli_enforced_allowed_transition_writes_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "planned",
                        "--enforce-transition",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["status"], "planned")
            self.assertEqual(
                payload["transition"],
                {
                    "allowed": True,
                    "enforced": True,
                    "from": "proposed",
                    "to": "planned",
                },
            )
            for relative_path in EXPECTED_FEATURE_FILES:
                self.assertIn(
                    "Status: planned",
                    (root / relative_path).read_text(encoding="utf-8"),
                )

    def test_feature_status_cli_enforced_all_non_archive_allowed_transitions_write(
        self,
    ) -> None:
        allowed_edges = [
            (from_status, to_status)
            for from_status, to_statuses in FEATURE_TRANSITIONS.items()
            for to_status in to_statuses
            if to_status != "archived"
        ]

        for from_status, to_status in allowed_edges:
            with self.subTest(from_status=from_status, to_status=to_status):
                with TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    init_workspace(root)
                    create_feature_bundle(root, "add-dark-mode")
                    set_feature_status(root, "add-dark-mode", from_status)
                    output = StringIO()

                    with redirect_stdout(output):
                        returncode = main(
                            [
                                "feature",
                                "status",
                                "add-dark-mode",
                                str(root),
                                "--set",
                                to_status,
                                "--enforce-transition",
                                "--json",
                            ]
                        )

                    payload = json.loads(output.getvalue())
                    self.assertEqual(returncode, 0)
                    self.assertEqual(payload["status"], to_status)
                    self.assertEqual(
                        payload["transition"],
                        {
                            "allowed": True,
                            "enforced": True,
                            "from": from_status,
                            "to": to_status,
                        },
                    )
                    for relative_path in EXPECTED_FEATURE_FILES:
                        self.assertIn(
                            f"Status: {to_status}",
                            (root / relative_path).read_text(encoding="utf-8"),
                        )

    def test_feature_status_cli_enforced_disallowed_transition_does_not_write(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            before = {
                relative_path: (root / relative_path).read_text(encoding="utf-8")
                for relative_path in EXPECTED_FEATURE_FILES
            }
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "implemented",
                        "--enforce-transition",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertEqual(payload["error"], "transition_not_allowed")
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["transition"]["from"], "proposed")
            self.assertEqual(payload["transition"]["to"], "implemented")
            self.assertTrue(payload["transition"]["enforced"])
            self.assertFalse(payload["transition"]["allowed"])
            after = {
                relative_path: (root / relative_path).read_text(encoding="utf-8")
                for relative_path in EXPECTED_FEATURE_FILES
            }
            self.assertEqual(after, before)

    def test_feature_status_cli_enforced_archived_terminal_does_not_write(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            set_feature_status(root, "add-dark-mode", "archived")
            before = {
                relative_path: (root / relative_path).read_text(encoding="utf-8")
                for relative_path in EXPECTED_FEATURE_FILES
            }
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "implemented",
                        "--enforce-transition",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertEqual(payload["error"], "transition_not_allowed")
            self.assertEqual(payload["transition"]["from"], "archived")
            self.assertIn("terminal", payload["transition"]["reason"])
            self.assertEqual(
                {
                    relative_path: (root / relative_path).read_text(encoding="utf-8")
                    for relative_path in EXPECTED_FEATURE_FILES
                },
                before,
            )

    def test_feature_status_cli_enforced_mixed_status_fails_before_write(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            execution = root / "execution" / "features" / "add-dark-mode.md"
            execution.write_text(
                execution.read_text(encoding="utf-8").replace(
                    "Status: proposed",
                    "Status: planned",
                ),
                encoding="utf-8",
            )
            before = {
                relative_path: (root / relative_path).read_text(encoding="utf-8")
                for relative_path in EXPECTED_FEATURE_FILES
            }
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "in-progress",
                        "--enforce-transition",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertEqual(payload["error"], "current_status_inconsistent")
            self.assertEqual(payload["transition"]["from"], "mixed")
            self.assertFalse(payload["transition"]["allowed"])
            self.assertEqual(
                {
                    relative_path: (root / relative_path).read_text(encoding="utf-8")
                    for relative_path in EXPECTED_FEATURE_FILES
                },
                before,
            )

    def test_feature_status_cli_enforced_missing_status_fails_before_write(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace("Status: proposed\n", ""),
                encoding="utf-8",
            )
            before = {
                relative_path: (root / relative_path).read_text(encoding="utf-8")
                for relative_path in EXPECTED_FEATURE_FILES
            }
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "planned",
                        "--enforce-transition",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertEqual(payload["error"], "current_status_inconsistent")
            self.assertEqual(payload["transition"]["from"], "proposed")
            self.assertEqual(payload["transition"]["to"], "planned")
            self.assertTrue(payload["transition"]["enforced"])
            self.assertFalse(payload["transition"]["allowed"])
            self.assertEqual(
                {
                    relative_path: (root / relative_path).read_text(encoding="utf-8")
                    for relative_path in EXPECTED_FEATURE_FILES
                },
                before,
            )

    def test_feature_status_cli_enforced_archive_requires_ready_gate(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            before = {
                relative_path: (root / relative_path).read_text(encoding="utf-8")
                for relative_path in (
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                )
            }
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "archived",
                        "--enforce-transition",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertEqual(payload["error"], "archive_not_ready")
            self.assertEqual(payload["transition"]["from"], "proposed")
            self.assertEqual(payload["transition"]["to"], "archived")
            self.assertTrue(payload["transition"]["allowed"])
            self.assertIn("blocking_checks", payload)
            self.assertIn("gaps", payload)
            self.assertEqual(
                payload["missing_files"],
                ["quality/features/add-dark-mode.md"],
            )
            self.assertEqual(
                {
                    relative_path: (root / relative_path).read_text(encoding="utf-8")
                    for relative_path in before
                },
                before,
            )

    def test_feature_status_cli_enforced_archive_ready_bundle_succeeds(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root, status="validated")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "archived",
                        "--enforce-transition",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["status"], "archived")
            self.assertEqual(
                payload["transition"],
                {
                    "allowed": True,
                    "enforced": True,
                    "from": "validated",
                    "to": "archived",
                },
            )
            for relative_path in EXPECTED_FEATURE_FILES:
                self.assertIn(
                    "Status: archived",
                    (root / relative_path).read_text(encoding="utf-8"),
                )

    def test_feature_status_cli_set_inserts_missing_status_line(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace("Status: proposed\n", ""),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "validated",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["status"], "validated")
            self.assertTrue(payload["consistent"])
            lines = spec.read_text(encoding="utf-8").splitlines()
            feature_id_index = lines.index("Feature ID: add-dark-mode")
            self.assertEqual(lines[feature_id_index + 1], "Status: validated")

    def test_feature_status_cli_rejects_invalid_status_and_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")

            stderr = StringIO()
            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "done",
                    ]
                )
            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature status", stderr.getvalue())

            stderr = StringIO()
            with redirect_stderr(stderr):
                returncode = main(["feature", "status", "BadSlug", str(root)])
            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

            stderr = StringIO()
            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "done",
                        "--enforce-transition",
                    ]
                )
            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature status", stderr.getvalue())

    def test_feature_status_cli_set_updates_partial_bundle_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "planned",
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["status"], "planned")
            self.assertTrue(payload["consistent"])
            self.assertEqual(
                payload["missing_files"],
                ["quality/features/add-dark-mode.md"],
            )
            self.assertEqual(
                payload["updated_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                ],
            )

    def test_feature_status_cli_set_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "status",
                        "add-dark-mode",
                        str(root),
                        "--set",
                        "planned",
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("No feature files found", stderr.getvalue())

    def test_feature_status_cli_text_reports_lifecycle_value_for_consistent_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            set_feature_status(root, "add-dark-mode", "in-progress")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "status", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("Feature add-dark-mode status: in-progress", text)
            self.assertNotIn("mixed/inconsistent", text)
            self.assertIn("specs/features/add-dark-mode.md (in-progress)", text)
            self.assertIn("execution/features/add-dark-mode.md (in-progress)", text)
            self.assertIn("quality/features/add-dark-mode.md (in-progress)", text)

    def test_dogfood_feature_task_export_is_validated_and_exports_tasks(self) -> None:
        report = build_feature_tasks_report(REPO_ROOT, "feature-task-export")

        self.assertEqual(report.status, "validated")
        self.assertGreater(report.summary["total"], 0)
        self.assertTrue(all(task.source_file == "execution/features/feature-task-export.md" for task in report.tasks))
        self.assertTrue(all("TODO" not in task.text for task in report.tasks))

    def test_dogfood_feature_traceability_export_is_validated_and_complete(self) -> None:
        report = build_feature_trace_report(REPO_ROOT, "feature-traceability-export")

        self.assertEqual(report.status, "validated")
        self.assertEqual(report.missing_files, ())
        self.assertEqual(report.gaps, ())
        self.assertGreater(report.summary["acceptance_criteria"]["total"], 0)
        self.assertGreater(report.summary["tasks"]["total"], 0)
        self.assertGreater(report.summary["quality_checks"]["total"], 0)
        self.assertGreater(report.summary["test_plan"]["total"], 0)
        self.assertTrue(
            all(
                item.source_file == "specs/features/feature-traceability-export.md"
                for item in report.acceptance_criteria
            )
        )
        self.assertTrue(all("TODO" not in task.text for task in report.tasks))

    def test_dogfood_feature_readiness_gate_is_validated_and_ready(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "feature-readiness-gate")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.missing_files, ())
        self.assertEqual(report.gaps, ())
        self.assertEqual(report.summary["fail"], 0)

    def test_dogfood_feature_coverage_readiness_is_validated_and_coverage_ready(self) -> None:
        default_report = build_feature_ready_report(REPO_ROOT, "feature-coverage-readiness")
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "feature-coverage-readiness",
            require_coverage=True,
        )
        validation = build_validation_report(REPO_ROOT, include_features=True)

        self.assertTrue(default_report.ready)
        self.assertTrue(coverage_report.ready)
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.status, "validated")
        self.assertEqual(coverage_report.missing_files, ())
        self.assertEqual(coverage_report.gaps, ())
        self.assertEqual(coverage_report.summary["fail"], 0)
        self.assertTrue(validation["ok"])
        self.assertEqual(validation_exit_code(validation), 0)

    def test_dogfood_feature_handoff_packet_is_validated_and_ready(self) -> None:
        report = build_feature_handoff_report(REPO_ROOT, "feature-handoff-packet")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.missing_files, ())
        self.assertEqual(report.gaps, ())
        self.assertGreater(report.summary["trace"]["total"], 0)
        self.assertGreater(report.summary["tasks"]["total"], 0)
        self.assertEqual(report.summary["blocking_checks"], {"total": 0})
        self.assertIn(
            "Review, merge, or archive the ready feature bundle.",
            report.next_actions,
        )

    def test_dogfood_status_feature_summaries_is_validated_and_ready(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "status-feature-summaries")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.missing_files, ())
        self.assertEqual(report.gaps, ())
        self.assertEqual(report.summary["fail"], 0)

    def test_dogfood_status_coverage_readiness_summaries_is_validated_and_coverage_ready(self) -> None:
        default_report = build_feature_ready_report(
            REPO_ROOT,
            "status-coverage-readiness-summaries",
        )
        coverage_report = build_feature_ready_report(
            REPO_ROOT,
            "status-coverage-readiness-summaries",
            require_coverage=True,
        )

        self.assertTrue(default_report.ready)
        self.assertTrue(coverage_report.ready)
        self.assertTrue(coverage_report.coverage_required)
        self.assertEqual(coverage_report.status, "validated")
        self.assertEqual(coverage_report.missing_files, ())
        self.assertEqual(coverage_report.gaps, ())
        self.assertEqual(coverage_report.summary["fail"], 0)

    def test_dogfood_feature_transition_policy_is_validated_and_ready(self) -> None:
        report = build_feature_ready_report(REPO_ROOT, "feature-transition-policy")

        self.assertTrue(report.ready)
        self.assertEqual(report.status, "validated")
        self.assertEqual(report.missing_files, ())
        self.assertEqual(report.gaps, ())
        self.assertEqual(report.summary["fail"], 0)

    def test_dogfood_feature_pr_draft_is_validated_and_ready(self) -> None:
        draft = build_pull_request_draft(REPO_ROOT, "feature-pr-draft")

        self.assertEqual(draft.status, "validated")
        self.assertTrue(draft.ready)
        self.assertEqual(draft.missing_files, ())
        self.assertEqual(draft.gaps, ())
        self.assertEqual(draft.blocking_checks, ())
        self.assertIn("specspine feature pr feature-pr-draft . --json", draft.body)

    def test_dogfood_feature_task_issue_drafts_is_validated_and_ready(self) -> None:
        ready = build_feature_ready_report(REPO_ROOT, "feature-task-issue-drafts")
        report = build_feature_task_issues_report(REPO_ROOT, "feature-task-issue-drafts")

        self.assertTrue(ready.ready)
        self.assertEqual(report.status, "validated")
        self.assertFalse(report.source_missing)
        self.assertEqual(report.missing_files, ())
        self.assertGreater(report.summary["issue_total"], 0)
        self.assertEqual(report.summary["issue_total"], report.summary["total"])
        self.assertTrue(
            all(
                issue.source_file == "execution/features/feature-task-issue-drafts.md"
                for issue in report.issues
            )
        )
        self.assertIn(
            "specspine feature task-issues feature-task-issue-drafts . --json",
            report.issues[0].body,
        )

    def test_dogfood_github_sync_plan_is_validated_and_ready(self) -> None:
        ready = build_feature_ready_report(REPO_ROOT, "github-sync-plan")
        plan = build_feature_sync_plan(REPO_ROOT, "github-sync-plan")
        validation = build_validation_report(REPO_ROOT, include_features=True)

        self.assertTrue(ready.ready)
        self.assertTrue(validation["ok"])
        self.assertEqual(validation_exit_code(validation), 0)
        self.assertEqual(plan.status, "validated")
        self.assertTrue(plan.ready)
        self.assertEqual(plan.metadata.priority, "high")
        self.assertEqual(plan.metadata.owner, "SpecSpine maintainers")
        self.assertEqual(plan.missing_files, ())
        self.assertEqual(plan.gaps, ())
        self.assertEqual(plan.blocking_checks, ())
        self.assertGreater(plan.summary["task_issue_commands"], 0)
        self.assertTrue(all(not command.safe_to_auto_run for command in plan.commands))
        self.assertTrue(any("dry-run may still push" in note for note in plan.notes))
        self.assertIn(
            "specspine feature sync-plan github-sync-plan . --json",
            plan.recommended_commands,
        )

    def test_dogfood_sync_plan_artifacts_is_validated_and_ready(self) -> None:
        ready = build_feature_ready_report(REPO_ROOT, "sync-plan-artifacts")
        plan = build_feature_sync_plan(REPO_ROOT, "sync-plan-artifacts")
        validation = build_validation_report(REPO_ROOT, include_features=True)

        self.assertTrue(ready.ready)
        self.assertTrue(validation["ok"])
        self.assertEqual(validation_exit_code(validation), 0)
        self.assertEqual(plan.status, "validated")
        self.assertTrue(plan.ready)
        self.assertEqual(plan.metadata.priority, "high")
        self.assertEqual(plan.metadata.owner, "SpecSpine maintainers")
        self.assertEqual(plan.missing_files, ())
        self.assertEqual(plan.gaps, ())
        self.assertEqual(plan.blocking_checks, ())
        self.assertGreater(plan.summary["task_issue_commands"], 0)
        self.assertTrue(all(not command.safe_to_auto_run for command in plan.commands))
        self.assertIn(
            "specspine feature sync-plan sync-plan-artifacts . --json",
            plan.recommended_commands,
        )

    def test_validate_cli_can_check_feature_bundles(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--features", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.id:add-dark-mode:spec"
                    and check["status"] == "pass"
                    for check in payload["checks"]
                )
            )
            self.assertTrue(
                any(
                    check["id"] == "feature.status_consistency:add-dark-mode"
                    and check["status"] == "pass"
                    for check in payload["checks"]
                )
            )

    def test_validate_features_accepts_all_allowed_statuses(self) -> None:
        for status in FEATURE_STATUSES:
            with self.subTest(status=status):
                with TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    init_workspace(root)
                    create_feature_bundle(root, "add-dark-mode")
                    set_feature_status(root, "add-dark-mode", status)

                    report = build_validation_report(root, include_features=True)

                    self.assertTrue(report["ok"])

    def test_validate_features_rejects_illegal_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace(
                    "Status: proposed",
                    "Status: done",
                ),
                encoding="utf-8",
            )

            report = build_validation_report(root, include_features=True)

            self.assertFalse(report["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.status:add-dark-mode:spec"
                    and check["status"] == "fail"
                    for check in report["checks"]
                )
            )

    def test_validate_features_rejects_missing_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace("Status: proposed\n", ""),
                encoding="utf-8",
            )

            report = build_validation_report(root, include_features=True)

            self.assertFalse(report["ok"])
            checks = {(check["id"], check["status"]) for check in report["checks"]}
            self.assertIn(("feature.status:add-dark-mode:spec", "fail"), checks)
            self.assertIn(("feature.status_consistency:add-dark-mode", "fail"), checks)

    def test_validate_features_rejects_mixed_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            execution = root / "execution" / "features" / "add-dark-mode.md"
            execution.write_text(
                execution.read_text(encoding="utf-8").replace(
                    "Status: proposed",
                    "Status: planned",
                ),
                encoding="utf-8",
            )

            report = build_validation_report(root, include_features=True)

            self.assertFalse(report["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.status_consistency:add-dark-mode"
                    and check["status"] == "fail"
                    for check in report["checks"]
                )
            )

    def test_validate_features_skips_when_no_feature_bundles_exist(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--features", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.discovery"
                    and check["status"] == "skip"
                    for check in payload["checks"]
                )
            )

    def test_validate_features_fails_when_feature_id_does_not_match_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            spec = root / "specs" / "features" / "add-dark-mode.md"
            spec.write_text(
                spec.read_text(encoding="utf-8").replace(
                    "Feature ID: add-dark-mode",
                    "Feature ID: wrong-feature",
                ),
                encoding="utf-8",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["validate", str(root), "--features", "--json"])

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 1)
            self.assertFalse(payload["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.id:add-dark-mode:spec"
                    and check["status"] == "fail"
                    for check in payload["checks"]
                )
            )

    def test_feature_validation_fails_incomplete_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "execution" / "features" / "add-dark-mode.md").unlink()

            report = build_validation_report(root, include_features=True)

            self.assertFalse(report["ok"])
            self.assertTrue(
                any(
                    check["id"] == "feature.required_file:add-dark-mode:execution"
                    and check["status"] == "fail"
                    for check in report["checks"]
                )
            )

    def test_feature_issue_cli_generates_text_for_complete_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "issue", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("Title: Add dark mode", text)
            self.assertIn("- Feature ID: `add-dark-mode`", text)
            self.assertIn("- Status: proposed", text)
            self.assertIn("## Why", text)
            self.assertIn("Reduce eye strain", text)
            self.assertIn("## Acceptance Criteria", text)
            self.assertIn("## Tasks", text)
            self.assertIn("## Test Plan", text)
            self.assertIn("## Source Files", text)
            self.assertIn("specs/features/add-dark-mode.md", text)
            self.assertIn("execution/features/add-dark-mode.md", text)
            self.assertIn("quality/features/add-dark-mode.md", text)
            self.assertIn("## Missing Files\n\nNone.", text)

    def test_feature_issue_cli_reflects_current_non_proposed_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            set_feature_status(root, "add-dark-mode", "validated")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "issue", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertIn("- Status: validated", payload["body"])
            self.assertNotIn("- Status: proposed", payload["body"])

    def test_feature_issue_cli_json_output_is_parseable(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
            )
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "issue", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["title"], "Add dark mode")
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(
                payload["source_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            self.assertIn("Reduce eye strain", payload["body"])

    def test_feature_issue_title_falls_back_to_slug_title_without_spec_h1(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "specs" / "features" / "add-dark-mode.md").write_text(
                "\n".join(
                    [
                        "Feature ID: add-dark-mode",
                        "Status: proposed",
                        "",
                        "## Why",
                        "",
                        "Make evening use comfortable.",
                        "",
                        "## Acceptance Criteria",
                        "",
                        "- [ ] Users can switch to a dark color scheme.",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            draft = build_issue_draft(root, "add-dark-mode")

            self.assertEqual(draft.title, "Add Dark Mode")
            self.assertIn("Make evening use comfortable.", draft.body)

    def test_feature_issue_partial_bundle_marks_missing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "issue", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(
                payload["missing_files"],
                ["quality/features/add-dark-mode.md"],
            )
            self.assertEqual(
                payload["source_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                ],
            )
            self.assertIn("quality/features/add-dark-mode.md", payload["body"])
            self.assertIn(
                "TODO: Add `quality/features/add-dark-mode.md` with a `## Test Plan` section.",
                payload["body"],
            )

    def test_feature_issue_and_pr_include_extended_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            add_feature_metadata(root)

            issue = build_issue_draft(root, "add-dark-mode")
            pr = build_pull_request_draft(root, "add-dark-mode")

            expected = {
                "effort": "M",
                "milestone": "Beta",
                "owner": "Platform Team",
                "priority": "high",
                "project": "Triage Board",
                "target_release": "2026.2",
            }
            self.assertEqual(issue.as_dict()["metadata"], expected)
            self.assertEqual(pr.as_dict()["metadata"], expected)
            for body in (issue.body, pr.body):
                self.assertIn("## Metadata", body)
                self.assertIn("- Milestone: Beta", body)
                self.assertIn("- Target Release: 2026.2", body)
                self.assertIn("- Project: Triage Board", body)
                self.assertIn("- Effort: M", body)

    def test_feature_issue_partial_bundle_text_lists_missing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "issue", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("## Missing Files", text)
            self.assertIn(
                "This draft was generated from an incomplete feature bundle.",
                text,
            )
            self.assertIn("- quality/features/add-dark-mode.md", text)
            self.assertIn(
                "TODO: Add `quality/features/add-dark-mode.md` with a `## Test Plan` section.",
                text,
            )

    def test_feature_issue_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                returncode = main(["feature", "issue", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("No feature files found", stderr.getvalue())
            self.assertIn("missing specs/features/add-dark-mode.md", stderr.getvalue())
            self.assertIn(
                "missing execution/features/add-dark-mode.md",
                stderr.getvalue(),
            )
            self.assertIn(
                "missing quality/features/add-dark-mode.md",
                stderr.getvalue(),
            )

    def test_feature_issue_output_file_does_not_overwrite_by_default(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            target = root / "issue.md"
            target.write_text("existing draft\n", encoding="utf-8")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "issue",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(target),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("Output file already exists", stderr.getvalue())
            self.assertEqual(target.read_text(encoding="utf-8"), "existing draft\n")

    def test_feature_issue_output_file_force_overwrites(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            target = root / "issue.md"
            target.write_text("existing draft\n", encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "issue",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(target),
                        "--force",
                    ]
                )

            content = target.read_text(encoding="utf-8")
            self.assertEqual(returncode, 0)
            self.assertIn("Wrote GitHub issue draft body", output.getvalue())
            self.assertNotIn("Title:", content)
            self.assertIn("- Feature ID: `add-dark-mode`", content)

    def test_feature_issue_output_creates_missing_parent_directories(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            target = root / "drafts" / "github" / "issue.md"
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "issue",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(target),
                    ]
                )

            self.assertEqual(returncode, 0)
            self.assertIn("Wrote GitHub issue draft body", output.getvalue())
            self.assertTrue(target.exists())
            self.assertIn(
                "- Feature ID: `add-dark-mode`",
                target.read_text(encoding="utf-8"),
            )

    def test_feature_issue_json_with_output_writes_body_and_prints_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(
                root,
                "add-dark-mode",
                title="Add dark mode",
                why="Reduce eye strain",
            )
            target = root / "issue.md"
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    [
                        "feature",
                        "issue",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(target),
                        "--json",
                    ]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["title"], "Add dark mode")
            self.assertEqual(target.read_text(encoding="utf-8"), payload["body"])
            self.assertNotIn("Wrote GitHub issue draft body", output.getvalue())

    def test_feature_issue_does_not_need_gh_or_token(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            output = StringIO()

            with patch.dict(
                "os.environ",
                {
                    "GH_TOKEN": "secret-gh-token",
                    "GITHUB_TOKEN": "secret-github-token",
                    "PATH": "",
                },
            ):
                with redirect_stdout(output):
                    returncode = main(
                        ["feature", "issue", "add-dark-mode", str(root), "--json"]
                    )

            self.assertEqual(returncode, 0)
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["feature_id"], "add-dark-mode")

    def test_feature_issue_section_missing_uses_placeholders(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "specs" / "features" / "add-dark-mode.md").write_text(
                "# Add dark mode\n\nFeature ID: add-dark-mode\nStatus: proposed\n",
                encoding="utf-8",
            )
            (root / "execution" / "features" / "add-dark-mode.md").write_text(
                "# Add dark mode Execution\n\nFeature ID: add-dark-mode\nStatus: proposed\n",
                encoding="utf-8",
            )
            (root / "quality" / "features" / "add-dark-mode.md").write_text(
                "# Add dark mode Quality\n\nFeature ID: add-dark-mode\nStatus: proposed\n",
                encoding="utf-8",
            )

            draft = build_issue_draft(root, "add-dark-mode")

            self.assertEqual(draft.title, "Add dark mode")
            self.assertIn(
                "TODO: Add a `## Why` section to `specs/features/add-dark-mode.md`.",
                draft.body,
            )
            self.assertIn(
                "TODO: Add a `## Acceptance Criteria` section to `specs/features/add-dark-mode.md`.",
                draft.body,
            )
            self.assertIn(
                "TODO: Add a `## Tasks` section to `execution/features/add-dark-mode.md`.",
                draft.body,
            )
            self.assertIn(
                "TODO: Add a `## Test Plan` section to `quality/features/add-dark-mode.md`.",
                draft.body,
            )

    def test_feature_pr_cli_generates_text_for_ready_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(["feature", "pr", "add-dark-mode", str(root)])

            text = output.getvalue()
            self.assertEqual(returncode, 0)
            self.assertIn("Title: Implement Add dark mode", text)
            self.assertIn("## Summary", text)
            self.assertIn("- Feature ID: `add-dark-mode`", text)
            self.assertIn("- Status: validated", text)
            self.assertIn("- Ready: yes", text)
            self.assertIn("## Feature", text)
            self.assertIn("## Why", text)
            self.assertIn("## Acceptance Criteria", text)
            self.assertIn("- [x] AC001", text)
            self.assertIn("## Tasks", text)
            self.assertIn("- [x] T001", text)
            self.assertIn("## Test Plan", text)
            self.assertIn("## Release Readiness", text)
            self.assertIn("## Readiness / Blocking Checks", text)
            self.assertIn("- [x] feature.bundle_files", text)
            self.assertIn("## Source Files", text)
            self.assertIn("specs/features/add-dark-mode.md", text)
            self.assertIn("## Missing Files\n\n- [x] None.", text)
            self.assertIn("## Key Commands", text)
            self.assertIn("specspine feature pr add-dark-mode . --json", text)

    def test_feature_pr_cli_json_output_is_parseable(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "pr", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["title"], "Implement Add dark mode")
            self.assertEqual(payload["feature_id"], "add-dark-mode")
            self.assertEqual(payload["status"], "validated")
            self.assertTrue(payload["ready"])
            self.assertEqual(payload["missing_files"], [])
            self.assertEqual(payload["gaps"], [])
            self.assertEqual(payload["blocking_checks"], [])
            self.assertEqual(
                payload["source_files"],
                [
                    "specs/features/add-dark-mode.md",
                    "execution/features/add-dark-mode.md",
                    "quality/features/add-dark-mode.md",
                ],
            )
            self.assertIn("summary", payload)
            self.assertIn("recommended_commands", payload)
            self.assertIn(
                "specspine feature ready add-dark-mode . --json",
                payload["recommended_commands"],
            )
            self.assertIn("## Release Readiness", payload["body"])

    def test_feature_pr_partial_bundle_marks_missing_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            (root / "quality" / "features" / "add-dark-mode.md").unlink()
            output = StringIO()

            with redirect_stdout(output):
                returncode = main(
                    ["feature", "pr", "add-dark-mode", str(root), "--json"]
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(returncode, 0)
            self.assertFalse(payload["ready"])
            self.assertEqual(
                payload["missing_files"],
                ["quality/features/add-dark-mode.md"],
            )
            self.assertIn(
                "quality/features/add-dark-mode.md",
                payload["body"],
            )
            self.assertTrue(payload["blocking_checks"])
            self.assertTrue(
                any(gap["id"] == "missing_file" for gap in payload["gaps"])
            )

    def test_feature_pr_all_files_missing_returns_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                returncode = main(["feature", "pr", "add-dark-mode", str(root)])

            self.assertEqual(returncode, 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("No feature files found", stderr.getvalue())
            self.assertIn("missing specs/features/add-dark-mode.md", stderr.getvalue())
            self.assertIn(
                "missing execution/features/add-dark-mode.md",
                stderr.getvalue(),
            )
            self.assertIn(
                "missing quality/features/add-dark-mode.md",
                stderr.getvalue(),
            )

    def test_feature_pr_invalid_slug_returns_two(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(["feature", "pr", "bad_slug", str(root)])

            self.assertEqual(returncode, 2)
            self.assertIn("Invalid feature slug", stderr.getvalue())

    def test_feature_pr_output_file_overwrite_force_and_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            target = root / "drafts" / "pull-request.md"
            target.parent.mkdir(parents=True)
            target.write_text("existing draft\n", encoding="utf-8")
            stderr = StringIO()

            with redirect_stderr(stderr):
                returncode = main(
                    [
                        "feature",
                        "pr",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(target),
                    ]
                )

            self.assertEqual(returncode, 1)
            self.assertIn("Output file already exists", stderr.getvalue())
            self.assertEqual(target.read_text(encoding="utf-8"), "existing draft\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                returncode = main(
                    [
                        "feature",
                        "pr",
                        "add-dark-mode",
                        str(root),
                        "--output",
                        str(target),
                        "--force",
                        "--json",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(returncode, 0)
            self.assertEqual(payload["title"], "Implement Add dark mode")
            self.assertEqual(target.read_text(encoding="utf-8"), payload["body"])
            self.assertNotIn("Wrote GitHub Pull Request draft body", stdout.getvalue())

    def test_feature_pr_does_not_need_gh_api_or_token(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
            output = StringIO()

            with patch.dict(
                "os.environ",
                {
                    "GH_TOKEN": "secret-gh-token",
                    "GITHUB_TOKEN": "secret-github-token",
                    "PATH": "",
                },
            ):
                with patch("subprocess.run") as subprocess_run:
                    with redirect_stdout(output):
                        returncode = main(
                            ["feature", "pr", "add-dark-mode", str(root), "--json"]
                        )

            self.assertEqual(returncode, 0)
            subprocess_run.assert_not_called()
            self.assertNotIn("secret-gh-token", output.getvalue())
            self.assertNotIn("secret-github-token", output.getvalue())
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["feature_id"], "add-dark-mode")

    def test_feature_pr_does_not_read_tokens_or_call_network(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            write_ready_feature_bundle(root)
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
                        "socket.create_connection",
                        side_effect=AssertionError("network called"),
                    ) as create_connection,
                    patch(
                        "socket.socket.connect",
                        side_effect=AssertionError("network called"),
                    ) as socket_connect,
                    patch(
                        "urllib.request.urlopen",
                        side_effect=AssertionError("network called"),
                    ) as urlopen,
                    redirect_stdout(output),
                ):
                    returncode = main(
                        ["feature", "pr", "add-dark-mode", str(root), "--json"]
                    )

            self.assertEqual(returncode, 0)
            subprocess_run.assert_not_called()
            subprocess_popen.assert_not_called()
            create_connection.assert_not_called()
            socket_connect.assert_not_called()
            urlopen.assert_not_called()
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["feature_id"], "add-dark-mode")

    def test_build_pull_request_draft_uses_slug_title_without_spec_h1(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "add-dark-mode")
            (root / "specs" / "features" / "add-dark-mode.md").write_text(
                "\n".join(
                    [
                        "Feature ID: add-dark-mode",
                        "Status: implemented",
                        "",
                        "## Why",
                        "",
                        "Make evening use comfortable.",
                        "",
                        "## Acceptance Criteria",
                        "",
                        "- [x] Users can switch to a dark color scheme.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            draft = build_pull_request_draft(root, "add-dark-mode")

            self.assertEqual(draft.title, "Implement Add Dark Mode")
            self.assertIn("Make evening use comfortable.", draft.body)
