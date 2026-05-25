from __future__ import annotations

import json
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from specspine.cli import main
from specspine.evolution import (
    ClassifiedChange,
    ClassificationResult,
    DiffFileHunk,
    DiffResult,
    EvolutionEntry,
    GitDiffError,
    ImpactEntry,
    ImpactResult,
    InvalidGitBaseError,
    RemediationAction,
    build_evolution_timeline,
    calculate_risk_level,
    classify_changes,
    generate_remediation_plan,
    get_git_diff,
    render_diff_json,
    render_diff_text,
    render_evolution_json,
    render_evolution_text,
    resolve_impact,
)
from specspine.features import (
    InvalidFeatureSlug,
    create_feature_bundle,
    validate_feature_slug,
)
from specspine.workspace import init_workspace


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(argv)
    except SystemExit as e:
        code = e.code if e.code is not None else 0
    return code, stdout.getvalue(), stderr.getvalue()


def write_feature_with_content(
    root: Path,
    slug: str,
    spec_content: str | None = None,
    execution_content: str | None = None,
    quality_content: str | None = None,
) -> None:
    (root / "specs" / "features").mkdir(parents=True, exist_ok=True)
    (root / "execution" / "features").mkdir(parents=True, exist_ok=True)
    (root / "quality" / "features").mkdir(parents=True, exist_ok=True)

    if spec_content:
        (root / "specs" / "features" / f"{slug}.md").write_text(
            spec_content, encoding="utf-8"
        )
    if execution_content:
        (root / "execution" / "features" / f"{slug}.md").write_text(
            execution_content, encoding="utf-8"
        )
    if quality_content:
        (root / "quality" / "features" / f"{slug}.md").write_text(
            quality_content, encoding="utf-8"
        )


def setup_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(root), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(root), capture_output=True, check=True,
    )


def git_add_and_commit(root: Path, message: str = "commit") -> str:
    subprocess.run(["git", "add", "-A"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=str(root), capture_output=True, check=True,
    )
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(root), capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


class GitDiffIntegrationTests(TestCase):
    def test_no_changes_returns_empty_diff(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            result = get_git_diff("test-feature", root)
            self.assertEqual(result.slug, "test-feature")
            # Files exist but have no diff hunks
            self.assertEqual(len(result.files), 3)
            for f in result.files:
                self.assertEqual(f.added_lines, 0)
                self.assertEqual(f.removed_lines, 0)

    def test_diff_detects_changes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            spec_path = root / "specs" / "features" / "test-feature.md"
            content = spec_path.read_text(encoding="utf-8")
            content = content.replace(
                "TODO: Define one observable outcome",
                "AC001: User can login with email",
            )
            spec_path.write_text(content, encoding="utf-8")

            result = get_git_diff("test-feature", root, unstaged=True)
            self.assertEqual(result.slug, "test-feature")
            changed = [f for f in result.files if f.added_lines > 0 or f.removed_lines > 0]
            self.assertGreater(len(changed), 0)

    def test_diff_against_base_commit(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            initial_commit = git_add_and_commit(root)

            spec_path = root / "specs" / "features" / "test-feature.md"
            content = spec_path.read_text(encoding="utf-8")
            content = content.replace("TODO:", "Done:")
            spec_path.write_text(content, encoding="utf-8")
            git_add_and_commit(root, "second commit")

            result = get_git_diff("test-feature", root, base=initial_commit)
            self.assertEqual(result.slug, "test-feature")

    def test_invalid_base_raises_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            with self.assertRaises(InvalidGitBaseError):
                get_git_diff("test-feature", root, base="nonexistent-commit")

    def test_missing_feature_returns_empty_result(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            result = get_git_diff("missing-feature", root)
            self.assertEqual(result.slug, "missing-feature")
            self.assertEqual(result.files, [])

    def test_invalid_slug_raises_error(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(InvalidFeatureSlug):
                get_git_diff("Bad Slug", root)

    def test_summary_counts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            spec_path = root / "specs" / "features" / "test-feature.md"
            content = spec_path.read_text(encoding="utf-8")
            content += "\n## New Section\n\nAC001: Added criterion\n"
            spec_path.write_text(content, encoding="utf-8")

            result = get_git_diff("test-feature", root, unstaged=True)
            summary = result.summary
            self.assertIn("files_changed", summary)
            self.assertIn("total_added", summary)
            self.assertIn("total_removed", summary)

    def test_diff_file_hunk_as_dict(self) -> None:
        hunk = DiffFileHunk(
            path="specs/features/test.md",
            diff_hunks=["@@ -1,3 +1,4 @@"],
            added_lines=1,
            removed_lines=0,
            modified_lines=1,
        )
        d = hunk.as_dict()
        self.assertEqual(d["path"], "specs/features/test.md")
        self.assertEqual(d["added_lines"], 1)
        self.assertEqual(d["removed_lines"], 0)

    def test_diff_result_as_dict(self) -> None:
        result = DiffResult(
            slug="test",
            files=[
                DiffFileHunk(
                    path="specs/features/test.md",
                    diff_hunks=[],
                    added_lines=0,
                    removed_lines=0,
                    modified_lines=0,
                )
            ],
        )
        d = result.as_dict()
        self.assertEqual(d["slug"], "test")
        self.assertEqual(len(d["files"]), 1)


class SemanticChangeClassificationTests(TestCase):
    def test_classify_no_changes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            diff_result = DiffResult(slug="test-feature", files=[])
            result = classify_changes(diff_result, "test-feature", root)
            self.assertEqual(result.slug, "test-feature")

    def test_classify_ac_added(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            spec_before = """# Test Feature
Feature ID: test-feature
Status: proposed
Priority: medium

## Acceptance Criteria

- [ ] TODO: placeholder
"""
            spec_after = """# Test Feature
Feature ID: test-feature
Status: proposed
Priority: medium

## Acceptance Criteria

- [ ] AC001: User can login
- [ ] AC002: User can logout
"""
            write_feature_with_content(
                root, "test-feature",
                spec_content=spec_after,
                execution_content="# Test Feature\nFeature ID: test-feature\n",
                quality_content="# Test Feature\nFeature ID: test-feature\n",
            )

            diff_result = DiffResult(slug="test-feature", files=[])
            root_mock = mock.patch(
                "specspine.evolution_content_loader._build_versioned_content",
                return_value={
                    "spec": spec_before,
                    "execution": "# Test Feature\nFeature ID: test-feature\n",
                    "quality": "# Test Feature\nFeature ID: test-feature\n",
                },
            )
            with root_mock:
                result = classify_changes(diff_result, "test-feature", root)

            ac_added = [c for c in result.changes if c.category == "ac" and c.change_type == "added"]
            self.assertGreater(len(ac_added), 0)

    def test_classify_ac_removed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            spec_before = """# Test Feature
Feature ID: test-feature
Status: proposed

## Acceptance Criteria

- [ ] AC001: Old criterion
- [ ] AC002: Another criterion
"""
            spec_after = """# Test Feature
Feature ID: test-feature
Status: proposed

## Acceptance Criteria

- [ ] AC001: Old criterion
"""
            write_feature_with_content(root, "test-feature", spec_content=spec_after)

            with mock.patch(
                "specspine.evolution_content_loader._build_versioned_content",
                return_value={
                    "spec": spec_before,
                    "execution": None,
                    "quality": None,
                },
            ):
                result = classify_changes(DiffResult(slug="test-feature", files=[]), "test-feature", root)

            ac_removed = [c for c in result.changes if c.category == "ac" and c.change_type == "removed"]
            self.assertGreater(len(ac_removed), 0)
            self.assertEqual(ac_removed[0].before, "AC002")

    def test_classify_task_added(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            exec_before = """# Test Execution
Feature ID: test-feature

## Tasks

- [ ] TODO: placeholder
"""
            exec_after = """# Test Execution
Feature ID: test-feature

## Tasks

- [ ] T001: Implement login
- [ ] T002: Implement logout
"""
            write_feature_with_content(
                root, "test-feature",
                spec_content="# Test\nFeature ID: test-feature\n",
                execution_content=exec_after,
            )

            with mock.patch(
                "specspine.evolution_content_loader._build_versioned_content",
                return_value={
                    "spec": "# Test\nFeature ID: test-feature\n",
                    "execution": exec_before,
                    "quality": None,
                },
            ):
                result = classify_changes(DiffResult(slug="test-feature", files=[]), "test-feature", root)

            task_added = [c for c in result.changes if c.category == "task" and c.change_type == "added"]
            self.assertGreater(len(task_added), 0)

    def test_classify_task_removed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            exec_before = """# Test Execution
Feature ID: test-feature

## Tasks

- [ ] T001: Old task
- [ ] T002: Another task
"""
            exec_after = """# Test Execution
Feature ID: test-feature

## Tasks

- [ ] T001: Old task
"""
            write_feature_with_content(
                root, "test-feature",
                spec_content="# Test\nFeature ID: test-feature\n",
                execution_content=exec_after,
            )

            with mock.patch(
                "specspine.evolution_content_loader._build_versioned_content",
                return_value={
                    "spec": "# Test\nFeature ID: test-feature\n",
                    "execution": exec_before,
                    "quality": None,
                },
            ):
                result = classify_changes(DiffResult(slug="test-feature", files=[]), "test-feature", root)

            task_removed = [c for c in result.changes if c.category == "task" and c.change_type == "removed"]
            self.assertGreater(len(task_removed), 0)

    def test_classify_metadata_changed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            spec_before = """# Test Feature
Feature ID: test-feature
Status: proposed
Priority: low
"""
            spec_after = """# Test Feature
Feature ID: test-feature
Status: planned
Priority: high
"""
            write_feature_with_content(root, "test-feature", spec_content=spec_after)

            with mock.patch(
                "specspine.evolution_content_loader._build_versioned_content",
                return_value={
                    "spec": spec_before,
                    "execution": None,
                    "quality": None,
                },
            ):
                result = classify_changes(DiffResult(slug="test-feature", files=[]), "test-feature", root)

            metadata_changes = [c for c in result.changes if c.category == "metadata"]
            self.assertGreater(len(metadata_changes), 0)

    def test_classify_file_new(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            spec_content = """# Test Feature
Feature ID: test-feature

## Acceptance Criteria

- [ ] AC001: New criterion
"""
            write_feature_with_content(root, "test-feature", spec_content=spec_content)

            with mock.patch(
                "specspine.evolution_content_loader._build_versioned_content",
                return_value={"spec": None, "execution": None, "quality": None},
            ):
                result = classify_changes(DiffResult(slug="test-feature", files=[]), "test-feature", root)

            self.assertGreater(len(result.changes), 0)

    def test_classify_file_removed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            with mock.patch(
                "specspine.evolution_content_loader._build_versioned_content",
                return_value={
                    "spec": "# Test\nFeature ID: test-feature\n## Acceptance Criteria\n\n- [ ] AC001: old\n",
                    "execution": "# Exec\nFeature ID: test-feature\n## Tasks\n\n- [ ] T001: old\n",
                    "quality": "# Quality\nFeature ID: test-feature\n",
                },
            ):
                result = classify_changes(DiffResult(slug="test-feature", files=[]), "test-feature", root)

            self.assertGreater(len(result.changes), 0)

    def test_classify_modified_file_with_hunks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)

            spec_before = """# Test Feature
Feature ID: test-feature
"""
            spec_after = """# Test Feature
Feature ID: test-feature
Status: updated
"""
            write_feature_with_content(root, "test-feature", spec_content=spec_after)

            diff_result = DiffResult(
                slug="test-feature",
                files=[
                    DiffFileHunk(
                        path="specs/features/test-feature.md",
                        diff_hunks=["@@ -1,2 +1,3 @@"],
                        added_lines=1,
                        removed_lines=0,
                        modified_lines=1,
                    )
                ],
            )

            with mock.patch(
                "specspine.evolution_content_loader._build_versioned_content",
                return_value={
                    "spec": spec_before,
                    "execution": None,
                    "quality": None,
                },
            ):
                result = classify_changes(diff_result, "test-feature", root)

            modified = [c for c in result.changes if c.change_type == "modified"]
            self.assertGreater(len(modified), 0)

    def test_classification_result_summary(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="added", category="ac",
                file="spec.md", line=1, before=None, after="AC001",
            ),
            ClassifiedChange(
                change_id="CHG002", change_type="removed", category="ac",
                file="spec.md", line=2, before="AC002", after=None,
            ),
            ClassifiedChange(
                change_id="CHG003", change_type="added", category="task",
                file="exec.md", line=1, before=None, after="T001",
            ),
        ]
        result = ClassificationResult(slug="test", changes=changes)
        summary = result.summary
        self.assertIn("ac_added", summary)
        self.assertIn("ac_removed", summary)
        self.assertIn("task_added", summary)

    def test_classified_change_as_dict(self) -> None:
        change = ClassifiedChange(
            change_id="CHG001", change_type="added", category="ac",
            file="spec.md", line=5, before=None, after="AC001",
        )
        d = change.as_dict()
        self.assertEqual(d["change_id"], "CHG001")
        self.assertEqual(d["category"], "ac")
        self.assertNotIn("before", d)
        self.assertIn("after", d)


class DownstreamImpactResolutionTests(TestCase):
    def test_no_downstream_references(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")

            changes = [
                ClassifiedChange(
                    change_id="CHG001", change_type="removed", category="ac",
                    file="specs/features/test-feature.md", line=1,
                    before="AC001", after=None,
                )
            ]
            result = resolve_impact(changes, "test-feature", root)
            self.assertEqual(result.slug, "test-feature")

    def test_impact_for_removed_ac(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="removed", category="ac",
                file="specs/features/test-feature.md", line=1,
                before="AC001", after=None,
            )
        ]
        result = resolve_impact(changes, "test-feature", Path("/tmp"))
        self.assertGreater(len(result.impacts), 0)

    def test_impact_for_added_ac(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="added", category="ac",
                file="specs/features/test-feature.md", line=1,
                before=None, after="AC004",
            )
        ]
        result = resolve_impact(changes, "test-feature", Path("/tmp"))
        info_impacts = [i for i in result.impacts if i.severity == "info"]
        self.assertGreater(len(info_impacts), 0)

    def test_impact_for_modified_ac(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="modified", category="ac",
                file="specs/features/test-feature.md", line=1,
                before="AC001", after="AC001",
            )
        ]
        result = resolve_impact(changes, "test-feature", Path("/tmp"))
        self.assertGreater(len(result.impacts), 0)

    def test_impact_for_removed_task(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="removed", category="task",
                file="execution/features/test-feature.md", line=1,
                before="T001", after=None,
            )
        ]
        result = resolve_impact(changes, "test-feature", Path("/tmp"))
        warning_impacts = [i for i in result.impacts if i.severity == "warning"]
        self.assertGreater(len(warning_impacts), 0)

    def test_impact_for_metadata_change(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="modified", category="metadata",
                file="specs/features/test-feature.md", line=0,
                before="{'Priority': 'low'}", after="{'Priority': 'high'}",
            )
        ]
        result = resolve_impact(changes, "test-feature", Path("/tmp"))
        info_impacts = [i for i in result.impacts if i.severity == "info"]
        self.assertGreater(len(info_impacts), 0)

    def test_impact_result_summary(self) -> None:
        impacts = [
            ImpactEntry(change_id="CHG001", affected_type="feature", affected_id="feat-a", severity="breaking"),
            ImpactEntry(change_id="CHG002", affected_type="ac", affected_id="AC001", severity="warning"),
            ImpactEntry(change_id="CHG003", affected_type="task", affected_id="T001", severity="info"),
        ]
        result = ImpactResult(slug="test", impacts=impacts)
        summary = result.summary
        self.assertEqual(summary["breaking"], 1)
        self.assertEqual(summary["warning"], 1)
        self.assertEqual(summary["info"], 1)
        self.assertEqual(summary["total"], 3)

    def test_impact_entry_as_dict(self) -> None:
        entry = ImpactEntry(
            change_id="CHG001", affected_type="feature",
            affected_id="feat-a", severity="breaking",
        )
        d = entry.as_dict()
        self.assertEqual(d["change_id"], "CHG001")
        self.assertEqual(d["severity"], "breaking")


class RiskLevelCalculatorTests(TestCase):
    def test_breaking_for_removed_ac_with_warning_impact(self) -> None:
        change = ClassifiedChange(
            change_id="CHG001", change_type="removed", category="ac",
            file="spec.md", line=1, before="AC001", after=None,
        )
        impact = ImpactEntry(
            change_id="CHG001", affected_type="feature",
            affected_id="feat-a", severity="warning",
        )
        self.assertEqual(calculate_risk_level(change, impact), "breaking")

    def test_breaking_for_removed_ac_with_breaking_impact(self) -> None:
        change = ClassifiedChange(
            change_id="CHG001", change_type="removed", category="ac",
            file="spec.md", line=1, before="AC001", after=None,
        )
        impact = ImpactEntry(
            change_id="CHG001", affected_type="coverage",
            affected_id="COV001", severity="breaking",
        )
        self.assertEqual(calculate_risk_level(change, impact), "breaking")

    def test_warning_for_modified_ac(self) -> None:
        change = ClassifiedChange(
            change_id="CHG001", change_type="modified", category="ac",
            file="spec.md", line=1, before="AC001", after="AC001",
        )
        impact = ImpactEntry(
            change_id="CHG001", affected_type="feature",
            affected_id="feat-a", severity="warning",
        )
        self.assertEqual(calculate_risk_level(change, impact), "warning")

    def test_info_for_added_ac(self) -> None:
        change = ClassifiedChange(
            change_id="CHG001", change_type="added", category="ac",
            file="spec.md", line=1, before=None, after="AC004",
        )
        impact = ImpactEntry(
            change_id="CHG001", affected_type="ac",
            affected_id="AC004", severity="info",
        )
        self.assertEqual(calculate_risk_level(change, impact), "info")

    def test_info_for_metadata_change(self) -> None:
        change = ClassifiedChange(
            change_id="CHG001", change_type="modified", category="metadata",
            file="spec.md", line=0, before="{}", after="{}",
        )
        impact = ImpactEntry(
            change_id="CHG001", affected_type="metadata",
            affected_id="test", severity="info",
        )
        self.assertEqual(calculate_risk_level(change, impact), "info")

    def test_warning_for_removed_task(self) -> None:
        change = ClassifiedChange(
            change_id="CHG001", change_type="removed", category="task",
            file="exec.md", line=1, before="T001", after=None,
        )
        impact = ImpactEntry(
            change_id="CHG001", affected_type="task",
            affected_id="T001", severity="info",
        )
        self.assertEqual(calculate_risk_level(change, impact), "warning")

    def test_breaking_for_removed_task_with_breaking_impact(self) -> None:
        change = ClassifiedChange(
            change_id="CHG001", change_type="removed", category="task",
            file="exec.md", line=1, before="T001", after=None,
        )
        impact = ImpactEntry(
            change_id="CHG001", affected_type="feature",
            affected_id="feat-a", severity="breaking",
        )
        self.assertEqual(calculate_risk_level(change, impact), "breaking")


class RemediationPlanGeneratorTests(TestCase):
    def test_plan_for_removed_ac(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="removed", category="ac",
                file="specs/features/test-feature.md", line=1,
                before="AC001", after=None,
            )
        ]
        impacts = [
            ImpactEntry(
                change_id="CHG001", affected_type="feature",
                affected_id="dependent-feature", severity="breaking",
            )
        ]
        plan = generate_remediation_plan(changes, impacts)
        self.assertGreater(len(plan), 0)
        self.assertIn("AC001", plan[0].description)

    def test_plan_for_removed_ac_with_coverage(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="removed", category="ac",
                file="specs/features/test-feature.md", line=1,
                before="AC001", after=None,
            )
        ]
        impacts = [
            ImpactEntry(
                change_id="CHG001", affected_type="coverage",
                affected_id="COV001", severity="breaking",
            )
        ]
        plan = generate_remediation_plan(changes, impacts)
        coverage_actions = [a for a in plan if "coverage link" in a.description.lower()]
        self.assertGreater(len(coverage_actions), 0)

    def test_plan_for_modified_ac(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="modified", category="ac",
                file="specs/features/test-feature.md", line=1,
                before="AC001", after="AC001-updated",
            )
        ]
        impacts = [
            ImpactEntry(
                change_id="CHG001", affected_type="feature",
                affected_id="dependent-feature", severity="warning",
            )
        ]
        plan = generate_remediation_plan(changes, impacts)
        self.assertGreater(len(plan), 0)
        self.assertIn("re-validate", plan[0].description.lower())

    def test_plan_for_removed_task(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="removed", category="task",
                file="execution/features/test-feature.md", line=1,
                before="T001", after=None,
            )
        ]
        impacts = [
            ImpactEntry(
                change_id="CHG001", affected_type="task",
                affected_id="T001", severity="warning",
            )
        ]
        plan = generate_remediation_plan(changes, impacts)
        self.assertGreater(len(plan), 0)
        self.assertIn("T001", plan[0].description)

    def test_plan_for_added_task(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="added", category="task",
                file="execution/features/test-feature.md", line=1,
                before=None, after="T004",
            )
        ]
        impacts = [
            ImpactEntry(
                change_id="CHG001", affected_type="task",
                affected_id="T004", severity="info",
            )
        ]
        plan = generate_remediation_plan(changes, impacts)
        self.assertEqual(len(plan), 0)

    def test_plan_sorted_by_priority(self) -> None:
        changes = [
            ClassifiedChange(
                change_id="CHG001", change_type="removed", category="ac",
                file="specs/features/test-feature.md", line=1,
                before="AC001", after=None,
            ),
            ClassifiedChange(
                change_id="CHG002", change_type="removed", category="task",
                file="execution/features/test-feature.md", line=1,
                before="T001", after=None,
            ),
        ]
        impacts = [
            ImpactEntry(
                change_id="CHG001", affected_type="feature",
                affected_id="feat-a", severity="breaking",
            ),
            ImpactEntry(
                change_id="CHG002", affected_type="task",
                affected_id="T001", severity="warning",
            ),
        ]
        plan = generate_remediation_plan(changes, impacts)
        priorities = [a.priority for a in plan]
        self.assertEqual(priorities, sorted(priorities))

    def test_remediation_action_as_dict(self) -> None:
        action = RemediationAction(
            action_id="ACT001", description="Test action",
            priority=1, target_file="spec.md",
        )
        d = action.as_dict()
        self.assertEqual(d["action_id"], "ACT001")
        self.assertEqual(d["priority"], 1)


class EvolutionTimelineBuilderTests(TestCase):
    def test_empty_timeline_for_no_git(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")

            timeline = build_evolution_timeline("test-feature", root)
            self.assertEqual(timeline, [])

    def test_timeline_with_commits(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root, "initial")

            spec_path = root / "specs" / "features" / "test-feature.md"
            content = spec_path.read_text(encoding="utf-8")
            content += "\n## New Section\n"
            spec_path.write_text(content, encoding="utf-8")
            git_add_and_commit(root, "add section")

            timeline = build_evolution_timeline("test-feature", root)
            self.assertGreater(len(timeline), 0)
            self.assertEqual(timeline[0].message, "add section")

    def test_timeline_respects_limit(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)

            for i in range(5):
                spec_path = root / "specs" / "features" / "test-feature.md"
                content = spec_path.read_text(encoding="utf-8")
                spec_path.write_text(content + f"\n## Section {i}\n", encoding="utf-8")
                git_add_and_commit(root, f"commit {i}")

            timeline = build_evolution_timeline("test-feature", root, limit=2)
            self.assertLessEqual(len(timeline), 2)

    def test_timeline_entry_as_dict(self) -> None:
        entry = EvolutionEntry(
            commit_hash="abc123", date="2024-01-01", author="Test Author",
            message="Test commit", change_count=3, categories=["added", "removed"],
        )
        d = entry.as_dict()
        self.assertEqual(d["commit_hash"], "abc123")
        self.assertEqual(d["categories"], ["added", "removed"])


class CLIDiffTests(TestCase):
    def test_diff_help(self) -> None:
        code, stdout, stderr = run_cli(["spec", "diff", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("--json", stdout)
        self.assertIn("--base", stdout)
        self.assertIn("--unstaged", stdout)

    def test_diff_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            code, stdout, stderr = run_cli(["spec", "diff", "Bad Slug", tmp])
            self.assertEqual(code, 2)
            self.assertIn("Invalid feature slug", stderr)

    def test_diff_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            code, stdout, stderr = run_cli(["spec", "diff", "test-feature", str(root), "--json"])
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["slug"], "test-feature")
            self.assertIn("diff", payload)
            self.assertIn("classification", payload)
            self.assertIn("impact", payload)

    def test_diff_text_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            code, stdout, stderr = run_cli(["spec", "diff", "test-feature", str(root)])
            self.assertEqual(code, 0, stderr)
            self.assertIn("Spec diff for feature", stdout)

    def test_diff_with_invalid_base(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            code, stdout, stderr = run_cli(
                ["spec", "diff", "test-feature", str(root), "--base", "nonexistent"]
            )
            self.assertEqual(code, 2)
            self.assertIn("Invalid git base", stderr)

    def test_diff_output_to_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            output_file = root / "diff_output.txt"
            code, stdout, stderr = run_cli(
                ["spec", "diff", "test-feature", str(root), "--output", str(output_file)]
            )
            self.assertEqual(code, 0, stderr)
            self.assertTrue(output_file.exists())

    def test_diff_output_file_exists_without_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            output_file = root / "diff_output.txt"
            output_file.write_text("existing", encoding="utf-8")

            code, stdout, stderr = run_cli(
                ["spec", "diff", "test-feature", str(root), "--output", str(output_file)]
            )
            self.assertEqual(code, 1)
            self.assertIn("already exists", stderr)

    def test_diff_output_file_overwrite_with_force(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            output_file = root / "diff_output.txt"
            output_file.write_text("existing", encoding="utf-8")

            code, stdout, stderr = run_cli(
                ["spec", "diff", "test-feature", str(root), "--output", str(output_file), "--force"]
            )
            self.assertEqual(code, 0, stderr)
            self.assertTrue(output_file.exists())


class CLIEvolutionTests(TestCase):
    def test_evolution_help(self) -> None:
        code, stdout, stderr = run_cli(["spec", "evolution", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("--json", stdout)
        self.assertIn("--limit", stdout)

    def test_evolution_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            code, stdout, stderr = run_cli(["spec", "evolution", "Bad Slug", tmp])
            self.assertEqual(code, 2)
            self.assertIn("Invalid feature slug", stderr)

    def test_evolution_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            code, stdout, stderr = run_cli(
                ["spec", "evolution", "test-feature", str(root), "--json"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["slug"], "test-feature")
            self.assertIn("timeline", payload)
            self.assertIn("classification", payload)
            self.assertIn("impact", payload)

    def test_evolution_text_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)
            git_add_and_commit(root)

            code, stdout, stderr = run_cli(
                ["spec", "evolution", "test-feature", str(root)]
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Evolution timeline for feature", stdout)

    def test_evolution_with_limit(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            create_feature_bundle(root, "test-feature")
            setup_git_repo(root)

            for i in range(3):
                spec_path = root / "specs" / "features" / "test-feature.md"
                content = spec_path.read_text(encoding="utf-8")
                spec_path.write_text(content + f"\n## Section {i}\n", encoding="utf-8")
                git_add_and_commit(root, f"commit {i}")

            code, stdout, stderr = run_cli(
                ["spec", "evolution", "test-feature", str(root), "--json", "--limit", "2"]
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertLessEqual(len(payload["timeline"]), 2)


class TextAndJSONRenderingTests(TestCase):
    def test_render_diff_json_is_valid(self) -> None:
        result = DiffResult(slug="test", files=[])
        output = render_diff_json(result)
        parsed = json.loads(output)
        self.assertEqual(parsed["slug"], "test")

    def test_render_diff_text_contains_header(self) -> None:
        result = DiffResult(slug="test", files=[])
        output = render_diff_text(result)
        self.assertIn("Spec diff for feature 'test'", output)

    def test_render_diff_text_with_no_changes(self) -> None:
        result = DiffResult(slug="test", files=[])
        output = render_diff_text(result)
        self.assertIn("No changes detected", output)

    def test_render_diff_text_with_changes(self) -> None:
        result = DiffResult(
            slug="test",
            files=[
                DiffFileHunk(
                    path="specs/features/test.md",
                    diff_hunks=["@@ -1,3 +1,4 @@"],
                    added_lines=1,
                    removed_lines=0,
                    modified_lines=1,
                )
            ],
        )
        output = render_diff_text(result)
        self.assertIn("specs/features/test.md", output)

    def test_render_evolution_json_is_valid(self) -> None:
        payload = {"slug": "test", "timeline": []}
        output = render_evolution_json(payload)
        parsed = json.loads(output)
        self.assertEqual(parsed["slug"], "test")

    def test_render_evolution_text_contains_header(self) -> None:
        payload = {"slug": "test", "timeline": [], "classification": {}, "impact": {}}
        output = render_evolution_text(payload)
        self.assertIn("Evolution timeline for feature 'test'", output)

    def test_render_evolution_text_with_diff_summary(self) -> None:
        payload = {
            "slug": "test",
            "diff_summary": {"files_changed": 2, "total_added": 5, "total_removed": 3},
            "timeline": [],
            "classification": {},
            "impact": {},
        }
        output = render_evolution_text(payload)
        self.assertIn("Diff Summary:", output)

    def test_render_evolution_text_with_changes(self) -> None:
        payload = {
            "slug": "test",
            "diff_summary": {},
            "classification": {
                "changes": [
                    {"change_type": "added", "category": "ac", "file": "spec.md"}
                ]
            },
            "impact": {},
            "remediation": [],
            "timeline": [],
        }
        output = render_evolution_text(payload)
        self.assertIn("Changes (1):", output)

    def test_render_evolution_text_with_impact(self) -> None:
        payload = {
            "slug": "test",
            "diff_summary": {},
            "classification": {},
            "impact": {"summary": {"total": 2, "breaking": 1, "warning": 0, "info": 1}},
            "remediation": [],
            "timeline": [],
        }
        output = render_evolution_text(payload)
        self.assertIn("Impact Summary:", output)

    def test_render_evolution_text_with_remediation(self) -> None:
        payload = {
            "slug": "test",
            "diff_summary": {},
            "classification": {},
            "impact": {"summary": {}},
            "remediation": [
                {"priority": 1, "description": "Test action"}
            ],
            "timeline": [],
        }
        output = render_evolution_text(payload)
        self.assertIn("Remediation Actions (1):", output)

    def test_render_evolution_text_with_timeline(self) -> None:
        payload = {
            "slug": "test",
            "diff_summary": {},
            "classification": {},
            "impact": {"summary": {}},
            "remediation": [],
            "timeline": [
                {
                    "commit_hash": "abc123",
                    "date": "2024-01-01",
                    "author": "Test",
                    "message": "Test commit",
                }
            ],
        }
        output = render_evolution_text(payload)
        self.assertIn("Timeline (1 commits):", output)


if __name__ == "__main__":
    import unittest
    unittest.main()
