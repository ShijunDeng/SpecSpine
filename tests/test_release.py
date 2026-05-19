import json
import os
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import main
from specspine.features import FEATURE_FILE_PATHS
from specspine.release import (
    BreakingChange,
    ReleaseEntry,
    ReleaseNotesReport,
    _collect_release_features,
    _count_validation_evidence,
    _detect_breaking_changes,
    _extract_ac_summary,
    _extract_title,
    _group_features,
    _safety_notes,
    build_release_notes_report,
    render_release_notes_json,
    render_release_notes_json_lines,
    render_release_notes_text,
)
from specspine.workspace import init_workspace


def _write_feature_bundle(
    root: Path,
    slug: str = "add-dark-mode",
    *,
    title: str = "# Add Dark Mode",
    status: str = "validated",
    priority: str = "high",
    project: str = "frontend",
    effort: str = "m",
    ac_content: str | None = None,
    breaking_content: str = "",
    quality_checked_count: int = 0,
) -> None:
    for kind in FEATURE_FILE_PATHS:
        path = root / FEATURE_FILE_PATHS[kind].format(slug=slug)
        path.parent.mkdir(parents=True, exist_ok=True)

    spec_metadata = (
        f"Priority: {priority}\n"
        f"Project: {project}\n"
        f"Effort: {effort}\n"
    )
    ac_block = ac_content or "- [ ] AC001 Users can toggle dark mode.\n- [ ] AC002 Default theme persists."
    (root / FEATURE_FILE_PATHS["spec"].format(slug=slug)).write_text(
        f"{title}\n\n"
        f"Feature ID: {slug}\n"
        f"Status: {status}\n"
        f"{spec_metadata}\n"
        f"## Acceptance Criteria\n\n"
        f"{ac_block}\n"
        f"{breaking_content}\n",
        encoding="utf-8",
    )
    (root / FEATURE_FILE_PATHS["execution"].format(slug=slug)).write_text(
        f"# {slug.replace('-', ' ').title()} Execution\n\n"
        f"Feature ID: {slug}\n"
        f"Status: {status}\n\n"
        "## Tasks\n\n"
        "- [x] Implement toggle.\n",
        encoding="utf-8",
    )
    quality_checks = "\n".join(
        [f"- [x] Check {i}." for i in range(quality_checked_count)]
    )
    (root / FEATURE_FILE_PATHS["quality"].format(slug=slug)).write_text(
        f"# {slug.replace('-', ' ').title()} Quality\n\n"
        f"Feature ID: {slug}\n"
        f"Status: {status}\n\n"
        "## Required Checks\n\n"
        f"{quality_checks}\n",
        encoding="utf-8",
    )


class TestReleaseEntry(TestCase):
    def test_as_dict_contains_all_fields(self) -> None:
        entry = ReleaseEntry(
            slug="test-feature",
            title="Test Feature",
            priority="high",
            status_transition="newly validated",
            ac_summary="2 acceptance criterion/criteria defined",
            validation_evidence_count=3,
            project="core",
            effort="s",
        )
        d = entry.as_dict()
        self.assertEqual(d["slug"], "test-feature")
        self.assertEqual(d["title"], "Test Feature")
        self.assertEqual(d["priority"], "high")
        self.assertEqual(d["status_transition"], "newly validated")
        self.assertEqual(d["ac_summary"], "2 acceptance criterion/criteria defined")
        self.assertEqual(d["validation_evidence_count"], 3)
        self.assertEqual(d["project"], "core")
        self.assertEqual(d["effort"], "s")

    def test_as_dict_is_sorted(self) -> None:
        entry = ReleaseEntry(
            slug="a",
            title="A",
            priority="low",
            status_transition="unknown",
            ac_summary="",
            validation_evidence_count=0,
            project="x",
            effort="unknown",
        )
        keys = list(entry.as_dict().keys())
        self.assertEqual(keys, sorted(keys))


class TestBreakingChange(TestCase):
    def test_as_dict(self) -> None:
        bc = BreakingChange(
            feature_id="rm-flag",
            description="[CLI argument removed] Remove flag",
            severity="high",
            affected_commands=("--verbose",),
        )
        d = bc.as_dict()
        self.assertEqual(d["feature_id"], "rm-flag")
        self.assertEqual(d["severity"], "high")
        self.assertEqual(d["affected_commands"], ["--verbose"])

    def test_as_dict_empty_commands(self) -> None:
        bc = BreakingChange(
            feature_id="x",
            description="desc",
            severity="low",
            affected_commands=(),
        )
        self.assertEqual(bc.as_dict()["affected_commands"], [])


class TestReleaseNotesReport(TestCase):
    def test_as_dict_structure(self) -> None:
        report = ReleaseNotesReport(
            version="1",
            date_range="v1.0..v2.0",
            grouped_features={"high": []},
            breaking_changes=[],
            summary={"features_total": 0},
            safety_notes=("note1",),
        )
        d = report.as_dict()
        self.assertEqual(d["version"], "1")
        self.assertEqual(d["date_range"], "v1.0..v2.0")
        self.assertEqual(d["grouped_features"], {"high": []})
        self.assertEqual(d["breaking_changes"], [])
        self.assertIn("features_total", d["summary"])
        self.assertEqual(d["safety_notes"], ["note1"])


class TestExtractTitle(TestCase):
    def test_from_feature_id_scalar(self) -> None:
        content = "Feature ID: my-feature\nStatus: validated\n"
        self.assertEqual(_extract_title(content), "my-feature")

    def test_from_heading(self) -> None:
        content = "# Add Dark Mode\n\nFeature ID: x\n"
        self.assertEqual(_extract_title(content), "Add Dark Mode")

    def test_empty_content(self) -> None:
        self.assertEqual(_extract_title(""), "")


class TestExtractAcSummary(TestCase):
    def test_counts_checked_items(self) -> None:
        spec = "## Acceptance Criteria\n\n- [x] AC1\n- [ ] AC2\n"
        result = _extract_ac_summary(spec, "")
        self.assertIn("2", result)

    def test_missing_section(self) -> None:
        result = _extract_ac_summary("no section", "")
        self.assertEqual(result, "No acceptance criteria section found")


class TestCountValidationEvidence(TestCase):
    def test_counts_checked_boxes(self) -> None:
        content = "- [x] check1\n- [X] check2\n- [ ] check3\n"
        self.assertEqual(_count_validation_evidence(content), 2)

    def test_empty_content(self) -> None:
        self.assertEqual(_count_validation_evidence(""), 0)

    def test_all_unchecked(self) -> None:
        content = "- [ ] a\n- [ ] b\n"
        self.assertEqual(_count_validation_evidence(content), 0)


class TestCollectReleaseFeatures(TestCase):
    def test_collects_validated_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="feat-a", status="validated")
            entries = _collect_release_features(root)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].slug, "feat-a")

    def test_collects_archived_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="feat-b", status="archived")
            entries = _collect_release_features(root)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].status_transition, "released (archived)")

    def test_excludes_non_release_statuses(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="feat-c", status="in-progress")
            entries = _collect_release_features(root)
            self.assertEqual(len(entries), 0)

    def test_excludes_proposed_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="feat-d", status="proposed")
            entries = _collect_release_features(root)
            self.assertEqual(len(entries), 0)

    def test_excludes_planned_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="feat-e", status="planned")
            entries = _collect_release_features(root)
            self.assertEqual(len(entries), 0)

    def test_excludes_implemented_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="feat-f", status="implemented")
            entries = _collect_release_features(root)
            self.assertEqual(len(entries), 0)

    def test_multiple_features_collected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="alpha", status="validated")
            _write_feature_bundle(root, slug="beta", status="archived")
            _write_feature_bundle(root, slug="gamma", status="proposed")
            entries = _collect_release_features(root)
            self.assertEqual(len(entries), 2)
            slugs = [e.slug for e in entries]
            self.assertIn("alpha", slugs)
            self.assertIn("beta", slugs)

    def test_sorted_by_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="zebra", status="validated")
            _write_feature_bundle(root, slug="apple", status="validated")
            entries = _collect_release_features(root)
            self.assertEqual(entries[0].slug, "apple")
            self.assertEqual(entries[1].slug, "zebra")

    def test_empty_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            entries = _collect_release_features(root)
            self.assertEqual(len(entries), 0)

    def test_metadata_extracted(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(
                root,
                slug="meta-test",
                priority="low",
                project="backend",
                effort="xl",
                status="validated",
            )
            entries = _collect_release_features(root)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].priority, "low")
            self.assertEqual(entries[0].project, "backend")
            self.assertEqual(entries[0].effort, "xl")


class TestGroupFeatures(TestCase):
    def test_group_by_priority(self) -> None:
        features = [
            ReleaseEntry("a", "A", "high", "new", "", 0, "p", "s"),
            ReleaseEntry("b", "B", "low", "new", "", 0, "p", "s"),
            ReleaseEntry("c", "C", "high", "new", "", 0, "p", "s"),
        ]
        groups = _group_features(features, "priority")
        self.assertEqual(len(groups), 2)
        self.assertEqual(len(groups["high"]), 2)
        self.assertEqual(len(groups["low"]), 1)

    def test_group_by_project(self) -> None:
        features = [
            ReleaseEntry("a", "A", "high", "new", "", 0, "frontend", "s"),
            ReleaseEntry("b", "B", "high", "new", "", 0, "backend", "s"),
        ]
        groups = _group_features(features, "project")
        self.assertEqual(len(groups), 2)
        self.assertIn("frontend", groups)
        self.assertIn("backend", groups)

    def test_group_by_status(self) -> None:
        features = [
            ReleaseEntry("a", "A", "high", "newly validated", "", 0, "p", "s"),
            ReleaseEntry("b", "B", "high", "released (archived)", "", 0, "p", "s"),
        ]
        groups = _group_features(features, "status")
        self.assertEqual(len(groups), 2)

    def test_group_by_effort(self) -> None:
        features = [
            ReleaseEntry("a", "A", "high", "new", "", 0, "p", "s"),
            ReleaseEntry("b", "B", "high", "new", "", 0, "p", "l"),
        ]
        groups = _group_features(features, "effort")
        self.assertEqual(len(groups), 2)

    def test_empty_features(self) -> None:
        groups = _group_features([], "priority")
        self.assertEqual(groups, {})

    def test_entries_sorted_within_groups(self) -> None:
        features = [
            ReleaseEntry("z", "Z", "high", "new", "", 0, "p", "s"),
            ReleaseEntry("a", "A", "high", "new", "", 0, "p", "s"),
        ]
        groups = _group_features(features, "priority")
        high = groups["high"]
        self.assertEqual(high[0].slug, "a")
        self.assertEqual(high[1].slug, "z")


class TestDetectBreakingChanges(TestCase):
    def test_detects_removed_flag(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(
                root,
                slug="rm-flag",
                status="validated",
                breaking_content="removed the `--verbose` flag from CLI",
            )
            entries = _collect_release_features(root)
            breaking = _detect_breaking_changes(entries, root)
            self.assertGreater(len(breaking), 0)
            self.assertEqual(breaking[0].feature_id, "rm-flag")
            self.assertEqual(breaking[0].severity, "high")

    def test_detects_changed_default(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(
                root,
                slug="changed-default",
                status="validated",
                breaking_content="changed the default behavior of validation",
            )
            entries = _collect_release_features(root)
            breaking = _detect_breaking_changes(entries, root)
            self.assertGreater(len(breaking), 0)
            self.assertEqual(breaking[0].severity, "medium")

    def test_detects_deprecation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(
                root,
                slug="deprecate",
                status="validated",
                breaking_content="deprecated the `--old-flag` option",
            )
            entries = _collect_release_features(root)
            breaking = _detect_breaking_changes(entries, root)
            self.assertGreater(len(breaking), 0)
            self.assertEqual(breaking[0].severity, "low")

    def test_no_breaking_changes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="clean", status="validated")
            entries = _collect_release_features(root)
            breaking = _detect_breaking_changes(entries, root)
            self.assertEqual(len(breaking), 0)

    def test_affected_commands_extracted(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(
                root,
                slug="rm-multi",
                status="validated",
                breaking_content="removed the `--json` flag",
            )
            entries = _collect_release_features(root)
            breaking = _detect_breaking_changes(entries, root)
            self.assertGreater(len(breaking), 0)
            cmds = breaking[0].affected_commands
            self.assertIn("--json", cmds)

    def test_sorted_by_severity_then_id(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(
                root,
                slug="z-low",
                status="validated",
                breaking_content="deprecated the `--x` flag",
            )
            _write_feature_bundle(
                root,
                slug="a-high",
                status="validated",
                breaking_content="removed the `--y` flag",
            )
            entries = _collect_release_features(root)
            breaking = _detect_breaking_changes(entries, root)
            # Filter to only unique feature entries (one breaking change per feature type)
            high_bcs = [bc for bc in breaking if bc.severity == "high"]
            low_bcs = [bc for bc in breaking if bc.severity == "low"]
            self.assertGreater(len(high_bcs), 0)
            self.assertGreater(len(low_bcs), 0)
            # High severity should come before low
            high_idx = breaking.index(high_bcs[0])
            low_idx = breaking.index(low_bcs[0])
            self.assertLess(high_idx, low_idx)


class TestBuildReleaseNotesReport(TestCase):
    def test_basic_report(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="feat-1", status="validated")
            report = build_release_notes_report(root)
            self.assertEqual(report.version, "1")
            self.assertIn("features_total", report.summary)
            self.assertEqual(report.summary["features_total"], 1)

    def test_date_range_both(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_release_notes_report(root, since="v1", until="v2")
            self.assertEqual(report.date_range, "v1..v2")

    def test_date_range_since_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_release_notes_report(root, since="v1")
            self.assertEqual(report.date_range, "v1..latest")

    def test_date_range_until_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_release_notes_report(root, until="v2")
            self.assertEqual(report.date_range, "initial..v2")

    def test_date_range_neither(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_release_notes_report(root)
            self.assertEqual(report.date_range, "all")

    def test_summary_counts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="val-1", status="validated")
            _write_feature_bundle(root, slug="val-2", status="validated")
            _write_feature_bundle(root, slug="arch-1", status="archived")
            report = build_release_notes_report(root)
            self.assertEqual(report.summary["features_total"], 3)
            self.assertEqual(report.summary["features_validated"], 2)
            self.assertEqual(report.summary["features_archived"], 1)

    def test_safety_notes_present(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            report = build_release_notes_report(root)
            self.assertGreater(len(report.safety_notes), 0)
            for note in report.safety_notes:
                self.assertIsInstance(note, str)


class TestRenderReleaseNotesJson(TestCase):
    def test_valid_json(self) -> None:
        report = ReleaseNotesReport(
            version="1",
            date_range="all",
            grouped_features={},
            breaking_changes=[],
            summary={"features_total": 0},
            safety_notes=("safe",),
        )
        output = render_release_notes_json(report)
        parsed = json.loads(output)
        self.assertEqual(parsed["version"], "1")

    def test_json_is_sorted(self) -> None:
        report = ReleaseNotesReport(
            version="1",
            date_range="all",
            grouped_features={},
            breaking_changes=[],
            summary={},
            safety_notes=(),
        )
        output = render_release_notes_json(report)
        parsed = json.loads(output)
        self.assertEqual(output, json.dumps(parsed, indent=2, sort_keys=True) + "\n")


class TestRenderReleaseNotesText(TestCase):
    def test_contains_heading(self) -> None:
        report = ReleaseNotesReport(
            version="1",
            date_range="all",
            grouped_features={},
            breaking_changes=[],
            summary={"features_total": 0, "features_validated": 0, "features_archived": 0, "breaking_changes_total": 0, "total_validation_evidence": 0, "priority_counts": {}},
            safety_notes=("safe",),
        )
        output = render_release_notes_text(report)
        self.assertIn("# Release Notes", output)

    def test_contains_summary(self) -> None:
        report = ReleaseNotesReport(
            version="1",
            date_range="v1..v2",
            grouped_features={},
            breaking_changes=[],
            summary={"features_total": 5, "features_validated": 3, "features_archived": 2, "breaking_changes_total": 0, "total_validation_evidence": 10, "priority_counts": {}},
            safety_notes=(),
        )
        output = render_release_notes_text(report)
        self.assertIn("5", output)
        self.assertIn("v1..v2", output)

    def test_contains_features(self) -> None:
        entry = ReleaseEntry("a", "Feature A", "high", "newly validated", "2 ac", 1, "p", "s")
        report = ReleaseNotesReport(
            version="1",
            date_range="all",
            grouped_features={"high": [entry]},
            breaking_changes=[],
            summary={"features_total": 1, "features_validated": 1, "features_archived": 0, "breaking_changes_total": 0, "total_validation_evidence": 1, "priority_counts": {"high": 1}},
            safety_notes=(),
        )
        output = render_release_notes_text(report)
        self.assertIn("Feature A", output)
        self.assertIn("validated", output)

    def test_contains_breaking_changes(self) -> None:
        bc = BreakingChange("f1", "[high] desc", "high", ("--flag",))
        report = ReleaseNotesReport(
            version="1",
            date_range="all",
            grouped_features={},
            breaking_changes=[bc],
            summary={"features_total": 0, "features_validated": 0, "features_archived": 0, "breaking_changes_total": 1, "total_validation_evidence": 0, "priority_counts": {}},
            safety_notes=(),
        )
        output = render_release_notes_text(report)
        self.assertIn("Breaking Changes", output)
        self.assertIn("--flag", output)


class TestRenderReleaseNotesJsonLines(TestCase):
    def test_valid_json_lines(self) -> None:
        report = ReleaseNotesReport(
            version="1",
            date_range="all",
            grouped_features={},
            breaking_changes=[],
            summary={"features_total": 0},
            safety_notes=(),
        )
        output = render_release_notes_json_lines(report)
        lines = output.strip().splitlines()
        self.assertGreater(len(lines), 0)
        first = json.loads(lines[0])
        self.assertEqual(first["type"], "release_notes")

    def test_feature_lines(self) -> None:
        entry = ReleaseEntry("a", "A", "high", "new", "", 0, "p", "s")
        report = ReleaseNotesReport(
            version="1",
            date_range="all",
            grouped_features={"high": [entry]},
            breaking_changes=[],
            summary={"features_total": 1},
            safety_notes=(),
        )
        output = render_release_notes_json_lines(report)
        lines = output.strip().splitlines()
        feature_lines = [l for l in lines if json.loads(l).get("type") == "feature"]
        self.assertEqual(len(feature_lines), 1)
        self.assertEqual(json.loads(feature_lines[0])["slug"], "a")

    def test_breaking_change_lines(self) -> None:
        bc = BreakingChange("f1", "desc", "high", ())
        report = ReleaseNotesReport(
            version="1",
            date_range="all",
            grouped_features={},
            breaking_changes=[bc],
            summary={"features_total": 0},
            safety_notes=(),
        )
        output = render_release_notes_json_lines(report)
        lines = output.strip().splitlines()
        bc_lines = [l for l in lines if json.loads(l).get("type") == "breaking_change"]
        self.assertEqual(len(bc_lines), 1)
        self.assertEqual(json.loads(bc_lines[0])["feature_id"], "f1")


class TestSafetyNotes(TestCase):
    def test_contains_advisory_warning(self) -> None:
        notes = _safety_notes()
        self.assertTrue(any("advisory only" in n for n in notes))

    def test_contains_no_subprocess_note(self) -> None:
        notes = _safety_notes()
        self.assertTrue(any("subprocess" in n for n in notes))

    def test_contains_no_network_note(self) -> None:
        notes = _safety_notes()
        self.assertTrue(any("network" in n for n in notes))


class TestCliReleaseNotes(TestCase):
    def test_help_succeeds(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stdout = StringIO()
            with redirect_stdout(stdout):
                try:
                    main(["release", "notes", str(root), "--help"])
                except SystemExit as e:
                    self.assertEqual(e.code, 0)

    def test_notes_markdown_empty_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            with redirect_stdout(StringIO()) as out:
                result = main(["release", "notes", str(root)])
            self.assertEqual(result, 0)

    def test_notes_json_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="j-1", status="validated")
            stdout = StringIO()
            with redirect_stdout(stdout):
                result = main(["release", "notes", str(root), "--json"])
            self.assertEqual(result, 0)
            output = stdout.getvalue()
            parsed = json.loads(output)
            self.assertEqual(parsed["summary"]["features_total"], 1)

    def test_notes_markdown_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="m-1", status="validated")
            stdout = StringIO()
            with redirect_stdout(stdout):
                result = main(["release", "notes", str(root), "--format", "markdown"])
            self.assertEqual(result, 0)
            output = stdout.getvalue()
            self.assertIn("# Release Notes", output)

    def test_notes_json_lines_output(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="jl-1", status="validated")
            stdout = StringIO()
            with redirect_stdout(stdout):
                result = main(["release", "notes", str(root), "--format", "json-lines"])
            self.assertEqual(result, 0)
            output = stdout.getvalue()
            lines = output.strip().splitlines()
            self.assertTrue(all(json.loads(l) for l in lines))

    def test_invalid_group_by_returns_2(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            stderr = StringIO()
            with redirect_stderr(stderr):
                try:
                    main(["release", "notes", str(root), "--group-by", "invalid"])
                except SystemExit as e:
                    self.assertEqual(e.code, 2)

    def test_valid_group_by_priority(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="gb-p", status="validated", priority="low")
            with redirect_stdout(StringIO()) as out:
                result = main(["release", "notes", str(root), "--group-by", "priority"])
            self.assertEqual(result, 0)

    def test_valid_group_by_project(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="gb-prj", status="validated", project="myproj")
            with redirect_stdout(StringIO()) as out:
                result = main(["release", "notes", str(root), "--group-by", "project"])
            self.assertEqual(result, 0)

    def test_valid_group_by_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="gb-st", status="validated")
            with redirect_stdout(StringIO()) as out:
                result = main(["release", "notes", str(root), "--group-by", "status"])
            self.assertEqual(result, 0)

    def test_valid_group_by_effort(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="gb-ef", status="validated", effort="l")
            with redirect_stdout(StringIO()) as out:
                result = main(["release", "notes", str(root), "--group-by", "effort"])
            self.assertEqual(result, 0)

    def test_since_and_until_options(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="su-1", status="validated")
            stdout = StringIO()
            with redirect_stdout(stdout):
                result = main([
                    "release", "notes", str(root),
                    "--since", "v1.0", "--until", "v2.0", "--json",
                ])
            self.assertEqual(result, 0)
            parsed = json.loads(stdout.getvalue())
            self.assertEqual(parsed["date_range"], "v1.0..v2.0")

    def test_output_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_workspace(root)
            _write_feature_bundle(root, slug="out-1", status="validated")
            output_file = root / "release.md"
            with redirect_stdout(StringIO()) as out:
                result = main([
                    "release", "notes", str(root),
                    "--output", str(output_file),
                ])
            self.assertEqual(result, 0)
            self.assertTrue(output_file.exists())
            content = output_file.read_text(encoding="utf-8")
            self.assertIn("# Release Notes", content)

    def test_no_subprocess_import(self) -> None:
        import specspine.release as rel_module
        source = rel_module.__file__
        with open(source, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertNotIn("import subprocess", code)
        self.assertNotIn("from subprocess", code)

    def test_no_network_import(self) -> None:
        import specspine.release as rel_module
        source = rel_module.__file__
        with open(source, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertNotIn("import urllib", code)
        self.assertNotIn("import http", code)
        self.assertNotIn("import requests", code)

    def test_no_token_read(self) -> None:
        import specspine.release as rel_module
        source = rel_module.__file__
        with open(source, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertNotIn("os.environ", code)
        self.assertNotIn("environ[", code)
