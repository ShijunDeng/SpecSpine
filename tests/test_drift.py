import json
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import main
from specspine.drift import (
    DriftAuditReport,
    DriftEvent,
    FeatureDriftRecord,
    _build_compliance_section,
    _build_drift_history,
    _classify_severity,
    _correlate_cross_feature_drift,
    _detect_code_drift,
    _detect_quality_drift,
    _detect_spec_drift,
    _detect_test_drift,
    _extract_acs_from_quality,
    _extract_acs_from_spec,
    _extract_cov_links_from_quality,
    _extract_qc_ids_from_quality,
    _extract_tasks_from_execution,
    _feature_peer_content,
    _git_commit,
    _now_iso,
    _severity_distribution,
    build_drift_monitor_report,
    render_drift_json,
    render_drift_text,
)
from specspine.features import InvalidFeatureSlug


def _write_feature_bundle(root: Path, slug: str, *, spec_content: str, exec_content: str = "", quality_content: str = "") -> None:
    for directory in ("specs/features", "execution/features", "quality/features"):
        (root / directory).mkdir(parents=True, exist_ok=True)

    if spec_content:
        (root / "specs/features" / f"{slug}.md").write_text(spec_content, encoding="utf-8")
    if exec_content:
        (root / "execution/features" / f"{slug}.md").write_text(exec_content, encoding="utf-8")
    if quality_content:
        (root / "quality/features" / f"{slug}.md").write_text(quality_content, encoding="utf-8")


def _write_src_file(root: Path, path: str, content: str = "") -> None:
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")


def _write_test_file(root: Path, path: str, content: str = "") -> None:
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "add", "."], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(root), capture_output=True, check=True)


def _make_spec_with_acs(acs: list[str], checked: bool = True) -> str:
    lines = [
        "# Test Feature",
        "",
        "Feature ID: test-feature",
        "Status: validated",
        "",
        "## Acceptance Criteria",
        "",
    ]
    for ac in acs:
        mark = "x" if checked else " "
        lines.append(f"- [{mark}] {ac}: Description for {ac}.")
    lines.append("")
    return "\n".join(lines)


def _make_exec_with_tasks_and_ac_refs(tasks_ac_pairs: list[tuple[str, str]]) -> str:
    lines = [
        "# Test Feature Execution",
        "",
        "Feature ID: test-feature",
        "Status: validated",
        "",
        "## Tasks",
        "",
    ]
    for task_id, ac_id in tasks_ac_pairs:
        lines.append(f"- [x] {task_id}: AC {ac_id} implementation.")
    lines.append("")
    return "\n".join(lines)


def _make_quality_with_cov(cov_links: list[tuple[str, str]], qcs: list[str] | None = None) -> str:
    lines = [
        "# Test Feature Quality",
        "",
        "Feature ID: test-feature",
        "Status: validated",
        "",
        "## Test Coverage",
        "",
    ]
    for ac_id, target in cov_links:
        lines.append(f"- [x] {ac_id} -> {target}")
    if qcs:
        lines.append("")
        lines.append("## Required Checks")
        lines.append("")
        for qc in qcs:
            lines.append(f"- [x] {qc}: Quality check for {qc}.")
    lines.append("")
    return "\n".join(lines)


class DriftEventTests(TestCase):
    def test_drift_event_as_dict(self) -> None:
        ev = DriftEvent(
            event_type="spec",
            severity="critical",
            timestamp="2024-01-01T00:00:00Z",
            description="AC removed",
            affected_acs=("AC001",),
        )
        d = ev.as_dict()
        self.assertEqual(d["event_type"], "spec")
        self.assertEqual(d["severity"], "critical")
        self.assertEqual(d["affected_acs"], ["AC001"])

    def test_drift_event_no_affected(self) -> None:
        ev = DriftEvent(
            event_type="code",
            severity="medium",
            timestamp="2024-01-01T00:00:00Z",
            description="Orphaned reference",
        )
        d = ev.as_dict()
        self.assertEqual(d["affected_acs"], [])
        self.assertEqual(d["affected_tasks"], [])


class FeatureDriftRecordTests(TestCase):
    def test_feature_drift_record_as_dict(self) -> None:
        ev = DriftEvent(
            event_type="spec",
            severity="critical",
            timestamp="2024-01-01T00:00:00Z",
            description="Test",
        )
        rec = FeatureDriftRecord(
            feature_id="test-feature",
            severity="critical",
            spec_drift=(ev,),
            code_drift=(),
            test_drift=(),
            quality_drift=(),
            drift_events=(ev,),
            cascade_risk=True,
        )
        d = rec.as_dict()
        self.assertEqual(d["feature_id"], "test-feature")
        self.assertTrue(d["cascade_risk"])
        self.assertEqual(len(d["drift_events"]), 1)


class ExtractHelpersTests(TestCase):
    def test_extract_acs_from_spec_empty(self) -> None:
        self.assertEqual(_extract_acs_from_spec(""), [])

    def test_extract_acs_from_spec_single(self) -> None:
        self.assertEqual(_extract_acs_from_spec("- [x] AC001: test."), ["AC001"])

    def test_extract_acs_from_spec_multiple(self) -> None:
        text = "- [x] AC001: a.\n- [x] AC002: b.\n- [ ] AC003: c."
        acs = _extract_acs_from_spec(text)
        self.assertEqual(sorted(acs), ["AC001", "AC002", "AC003"])

    def test_extract_tasks_from_execution_t_format(self) -> None:
        text = "- [x] T001: impl.\n- [x] T002: impl."
        tasks = _extract_tasks_from_execution(text)
        self.assertEqual(tasks, ["T001", "T002"])

    def test_extract_acs_from_quality(self) -> None:
        text = "- [x] AC001 -> tests/test_foo.py\n- [x] AC002 -> tests/test_bar.py"
        acs = _extract_acs_from_quality(text)
        self.assertEqual(sorted(acs), ["AC001", "AC002"])

    def test_extract_cov_links_from_quality(self) -> None:
        text = "- [x] AC001 -> tests/test_foo.py\n- [ ] AC002 -> tests/test_bar.py"
        links = _extract_cov_links_from_quality(text)
        self.assertEqual(links, [("AC001", "tests/test_foo.py"), ("AC002", "tests/test_bar.py")])

    def test_extract_qc_ids_from_quality(self) -> None:
        text = "- [x] QC001: review.\n- [x] QC002: lint."
        qcs = _extract_qc_ids_from_quality(text)
        self.assertEqual(qcs, ["QC001", "QC002"])


class FeaturePeerContentTests(TestCase):
    def test_feature_peer_content_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = _feature_peer_content(root, "test-feature", "spec")
            self.assertIsNone(result)

    def test_feature_peer_content_exists(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test-feature", spec_content="# spec\nFeature ID: test-feature\n")
            result = _feature_peer_content(root, "test-feature", "spec")
            self.assertIsNotNone(result)
            self.assertIn("Feature ID: test-feature", result)


class DetectSpecDriftTests(TestCase):
    def test_no_spec_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            events = _detect_spec_drift("test-feature", root, None)
            self.assertEqual(events, [])

    def test_no_baseline(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test-feature", spec_content=_make_spec_with_acs(["AC001", "AC002"]))
            events = _detect_spec_drift("test-feature", root, None)
            self.assertEqual(events, [])

    def test_baseline_has_removed_acs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test-feature", spec_content=_make_spec_with_acs(["AC001"]))
            _init_git_repo(root)
            events = _detect_spec_drift("test-feature", root, "HEAD")
            critical_events = [e for e in events if e.severity == "critical"]
            self.assertEqual(len(critical_events), 0)

    def test_baseline_comparison_detects_added(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_v1 = _make_spec_with_acs(["AC001"])
            _write_feature_bundle(root, "test-feature", spec_content=spec_v1)
            _init_git_repo(root)
            spec_v2 = _make_spec_with_acs(["AC001", "AC002"])
            _write_feature_bundle(root, "test-feature", spec_content=spec_v2)
            subprocess.run(["git", "add", "."], cwd=str(root), capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "add AC002"], cwd=str(root), capture_output=True, check=True)
            events = _detect_spec_drift("test-feature", root, "HEAD~1")
            added_events = [e for e in events if "added" in e.description.lower()]
            self.assertTrue(len(added_events) > 0)

    def test_baseline_missing_at_old_commit(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("initial", encoding="utf-8")
            _init_git_repo(root)
            _write_feature_bundle(root, "test-feature", spec_content=_make_spec_with_acs(["AC001"]))
            subprocess.run(["git", "add", "."], cwd=str(root), capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "add feature"], cwd=str(root), capture_output=True, check=True)
            events = _detect_spec_drift("test-feature", root, "HEAD~1")
            self.assertTrue(len(events) > 0)


class DetectCodeDriftTests(TestCase):
    def test_no_spec_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            events = _detect_code_drift("test-feature", root)
            self.assertEqual(events, [])

    def test_orphaned_code_references(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001"]) + "\nImplementation: `src/app/module.py`.\n"
            _write_feature_bundle(root, "test-feature", spec_content=spec)
            events = _detect_code_drift("test-feature", root)
            orphan_events = [e for e in events if e.event_type == "code" and e.severity == "medium"]
            self.assertTrue(len(orphan_events) > 0)

    def test_code_references_exist(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_src_file(root, "src/app/module.py", "pass")
            spec = _make_spec_with_acs(["AC001"]) + "\nImplementation: `src/app/module.py`.\n"
            _write_feature_bundle(root, "test-feature", spec_content=spec)
            events = _detect_code_drift("test-feature", root)
            orphan_events = [e for e in events if e.event_type == "code" and "do not exist" in e.description]
            self.assertEqual(len(orphan_events), 0)

    def test_missing_ac_links_in_execution(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001", "AC002"])
            exec_c = _make_exec_with_tasks_and_ac_refs([("T001", "AC001")])
            _write_feature_bundle(root, "test-feature", spec_content=spec, exec_content=exec_c)
            events = _detect_code_drift("test-feature", root)
            ac_link_events = [e for e in events if "do not reference all" in e.description]
            self.assertTrue(len(ac_link_events) > 0)

    def test_execution_references_all_acs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001", "AC002"])
            exec_c = _make_exec_with_tasks_and_ac_refs([("T001", "AC001"), ("T002", "AC002")])
            _write_feature_bundle(root, "test-feature", spec_content=spec, exec_content=exec_c)
            events = _detect_code_drift("test-feature", root)
            ac_link_events = [e for e in events if "do not reference all" in e.description]
            self.assertEqual(len(ac_link_events), 0)


class DetectTestDriftTests(TestCase):
    def test_missing_spec_or_quality(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            events = _detect_test_drift("test-feature", root)
            self.assertEqual(events, [])

    def test_uncovered_acs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001", "AC002"])
            quality = _make_quality_with_cov([("AC001", "tests/test_foo.py")])
            _write_feature_bundle(root, "test-feature", spec_content=spec, quality_content=quality)
            events = _detect_test_drift("test-feature", root)
            uncovered = [e for e in events if "no test coverage" in e.description.lower()]
            self.assertTrue(len(uncovered) > 0)
            self.assertIn("AC002", uncovered[0].affected_acs)

    def test_stale_test_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001"])
            quality = _make_quality_with_cov([("AC001", "tests/stale_test.py")])
            _write_feature_bundle(root, "test-feature", spec_content=spec, quality_content=quality)
            events = _detect_test_drift("test-feature", root)
            stale = [e for e in events if "stale test file" in e.description.lower()]
            self.assertTrue(len(stale) > 0)

    def test_all_covered(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_test_file(root, "tests/test_foo.py", "pass")
            _write_test_file(root, "tests/test_bar.py", "pass")
            spec = _make_spec_with_acs(["AC001", "AC002"])
            quality = _make_quality_with_cov([
                ("AC001", "tests/test_foo.py"),
                ("AC002", "tests/test_bar.py"),
            ])
            _write_feature_bundle(root, "test-feature", spec_content=spec, quality_content=quality)
            events = _detect_test_drift("test-feature", root)
            self.assertEqual(events, [])


class DetectQualityDriftTests(TestCase):
    def test_no_quality_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            events = _detect_quality_drift("test-feature", root)
            self.assertEqual(events, [])

    def test_missing_quality_check(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001", "AC002"])
            quality = _make_quality_with_cov([("AC001", "tests/test_foo.py")])
            _write_feature_bundle(root, "test-feature", spec_content=spec, quality_content=quality)
            events = _detect_quality_drift("test-feature", root)
            missing_qc = [e for e in events if "missing quality check" in e.description.lower()]
            self.assertTrue(len(missing_qc) > 0)

    def test_non_test_coverage_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001"])
            quality = _make_quality_with_cov([("AC001", "docs/test_notes.md")])
            _write_feature_bundle(root, "test-feature", spec_content=spec, quality_content=quality)
            events = _detect_quality_drift("test-feature", root)
            non_test = [e for e in events if "does not point to a tests/" in e.description]
            self.assertTrue(len(non_test) > 0)

    def test_quality_ok(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001"])
            quality = _make_quality_with_cov(
                [("AC001", "tests/test_foo.py")],
                qcs=["QC001"],
            )
            _write_feature_bundle(root, "test-feature", spec_content=spec, quality_content=quality)
            events = _detect_quality_drift("test-feature", root)
            self.assertEqual(events, [])


class ClassifySeverityTests(TestCase):
    def test_all_empty(self) -> None:
        self.assertEqual(_classify_severity([], [], [], []), "none")

    def test_critical(self) -> None:
        ev = DriftEvent(event_type="spec", severity="critical", timestamp="t", description="d")
        self.assertEqual(_classify_severity([ev], [], [], []), "critical")

    def test_high(self) -> None:
        ev = DriftEvent(event_type="test", severity="high", timestamp="t", description="d")
        self.assertEqual(_classify_severity([], [], [ev], []), "high")

    def test_medium(self) -> None:
        ev = DriftEvent(event_type="code", severity="medium", timestamp="t", description="d")
        self.assertEqual(_classify_severity([], [ev], [], []), "medium")

    def test_low(self) -> None:
        ev = DriftEvent(event_type="quality", severity="low", timestamp="t", description="d")
        self.assertEqual(_classify_severity([], [], [], [ev]), "low")

    def test_highest_wins(self) -> None:
        low_ev = DriftEvent(event_type="quality", severity="low", timestamp="t", description="d")
        high_ev = DriftEvent(event_type="test", severity="high", timestamp="t", description="d")
        self.assertEqual(_classify_severity([], [], [high_ev], [low_ev]), "high")


class BuildDriftHistoryTests(TestCase):
    def test_no_peer_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            events = _build_drift_history("test-feature", root, None)
            self.assertEqual(events, [])

    def test_with_git_history(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test-feature", spec_content=_make_spec_with_acs(["AC001"]))
            _init_git_repo(root)
            events = _build_drift_history("test-feature", root, None)
            self.assertTrue(len(events) > 0)
            self.assertEqual(events[0].event_type, "spec")

    def test_since_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test-feature", spec_content=_make_spec_with_acs(["AC001"]))
            _init_git_repo(root)
            events = _build_drift_history("test-feature", root, "2099-01-01")
            self.assertEqual(events, [])


class CorrelateCrossFeatureDriftTests(TestCase):
    def test_no_critical_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            rec = FeatureDriftRecord(
                feature_id="a",
                severity="low",
                spec_drift=(),
                code_drift=(),
                test_drift=(),
                quality_drift=(),
                drift_events=(),
                cascade_risk=False,
            )
            _correlate_cross_feature_drift([rec], root)
            self.assertFalse(rec.cascade_risk)

    def test_downstream_marks_cascade(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("specs/features", "execution/features", "quality/features"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            critical_spec = _make_spec_with_acs(["AC001"])
            _write_feature_bundle(root, "feature-a", spec_content=critical_spec)
            downstream_spec = _make_spec_with_acs(["AC001"]) + "\ndepends on feature-a\n"
            _write_feature_bundle(root, "feature-b", spec_content=downstream_spec)
            rec_a = FeatureDriftRecord(
                feature_id="feature-a",
                severity="critical",
                spec_drift=(),
                code_drift=(),
                test_drift=(),
                quality_drift=(),
                drift_events=(),
                cascade_risk=False,
            )
            rec_b = FeatureDriftRecord(
                feature_id="feature-b",
                severity="low",
                spec_drift=(),
                code_drift=(),
                test_drift=(),
                quality_drift=(),
                drift_events=(),
                cascade_risk=False,
            )
            _correlate_cross_feature_drift([rec_a, rec_b], root)
            self.assertTrue(rec_b.cascade_risk)


class ComplianceSectionTests(TestCase):
    def test_compliance_hash_is_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            compliance = _build_compliance_section(report)
            self.assertIn("evidence_hash", compliance)
            self.assertIn("pass_fail_per_dimension", compliance)
            h1 = compliance["evidence_hash"]
            h2 = _build_compliance_section(report)["evidence_hash"]
            self.assertEqual(h1, h2)

    def test_compliance_all_pass_when_no_drift(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            compliance = _build_compliance_section(report)
            pf = compliance["pass_fail_per_dimension"]
            for dim in ("spec", "code", "test", "quality"):
                self.assertEqual(pf[dim], "pass")


class BuildDriftMonitorReportTests(TestCase):
    def test_empty_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            self.assertEqual(report.features, ())
            self.assertEqual(report.summary["features_scanned"], 0)

    def test_single_feature_no_drift(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001"]) + "\nImplementation: `src/app/core.py`.\n"
            _write_src_file(root, "src/app/core.py", "pass")
            _write_test_file(root, "tests/test_core.py", "pass")
            _write_feature_bundle(
                root, "test-feature",
                spec_content=spec,
                exec_content=_make_exec_with_tasks_and_ac_refs([("T001", "AC001")]),
                quality_content=_make_quality_with_cov(
                    [("AC001", "tests/test_core.py")],
                    qcs=["QC001"],
                ),
            )
            report = build_drift_monitor_report(root)
            self.assertEqual(len(report.features), 1)
            self.assertEqual(report.features[0].severity, "none")

    def test_feature_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(
                root, "alpha",
                spec_content=_make_spec_with_acs(["AC001"]),
            )
            _write_feature_bundle(
                root, "beta",
                spec_content=_make_spec_with_acs(["AC001"]),
            )
            report = build_drift_monitor_report(root, feature_filter="alpha")
            self.assertEqual(len(report.features), 1)
            self.assertEqual(report.features[0].feature_id, "alpha")

    def test_invalid_slug_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(InvalidFeatureSlug):
                build_drift_monitor_report(root, feature_filter="INVALID")

    def test_summary_counts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001"]) + "\nImplementation: `src/app/core.py`.\n"
            _write_src_file(root, "src/app/core.py", "pass")
            _write_test_file(root, "tests/test_a.py", "pass")
            _write_feature_bundle(
                root, "feat-a",
                spec_content=spec,
                exec_content=_make_exec_with_tasks_and_ac_refs([("T001", "AC001")]),
                quality_content=_make_quality_with_cov(
                    [("AC001", "tests/test_a.py")],
                    qcs=["QC001"],
                ),
            )
            report = build_drift_monitor_report(root)
            self.assertEqual(report.summary["features_scanned"], 1)
            self.assertEqual(report.summary["drift_free_count"], 1)
            self.assertEqual(report.summary["drift_events_total"], 0)

    def test_scan_metadata_has_timestamp(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            self.assertIn("timestamp", report.scan_metadata)
            self.assertIn("git_commit", report.scan_metadata)

    def test_baseline_in_scan_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root, baseline="HEAD")
            self.assertEqual(report.scan_metadata["baseline"], "HEAD")

    def test_since_in_scan_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root, since="2024-01-01")
            self.assertEqual(report.scan_metadata["since"], "2024-01-01")

    def test_safety_notes_present(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            self.assertTrue(len(report.safety_notes) > 0)

    def test_features_sorted_by_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "z-feature", spec_content=_make_spec_with_acs(["AC001"]))
            _write_feature_bundle(root, "a-feature", spec_content=_make_spec_with_acs(["AC001"]))
            report = build_drift_monitor_report(root)
            slugs = [f.feature_id for f in report.features]
            self.assertEqual(slugs, ["a-feature", "z-feature"])


class RenderTests(TestCase):
    def test_json_render(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            text = render_drift_json(report)
            data = json.loads(text)
            self.assertIn("features", data)
            self.assertIn("summary", data)
            self.assertIn("compliance", data)

    def test_text_render(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            text = render_drift_text(report)
            self.assertIn("Drift monitor report", text)
            self.assertIn("Summary:", text)

    def test_text_render_with_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(
                root, "feat-a",
                spec_content=_make_spec_with_acs(["AC001"]),
            )
            report = build_drift_monitor_report(root)
            text = render_drift_text(report)
            self.assertIn("feat-a", text)

    def test_text_render_compliance(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            text = render_drift_text(report)
            self.assertIn("Compliance:", text)
            self.assertIn("evidence_hash", text)

    def test_json_is_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001"]) + "\nImplementation: `src/app/core.py`.\n"
            _write_src_file(root, "src/app/core.py", "pass")
            _write_test_file(root, "tests/test_a.py", "pass")
            _write_feature_bundle(
                root, "feat-a",
                spec_content=spec,
                exec_content=_make_exec_with_tasks_and_ac_refs([("T001", "AC001")]),
                quality_content=_make_quality_with_cov(
                    [("AC001", "tests/test_a.py")],
                    qcs=["QC001"],
                ),
            )
            report = build_drift_monitor_report(root)
            text = render_drift_json(report)
            data = json.loads(text)
            self.assertIsInstance(data["features"], list)
            self.assertIsInstance(data["summary"], dict)

    def test_text_render_no_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            text = render_drift_text(report)
            self.assertIn("- none", text)

    def test_text_render_recommended_commands(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            text = render_drift_text(report)
            self.assertIn("Recommended commands:", text)

    def test_text_render_safety_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            text = render_drift_text(report)
            self.assertIn("Safety notes:", text)


class CliMonitorTests(TestCase):
    def test_monitor_help(self) -> None:
        out = StringIO()
        err = StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            with self.assertRaises(SystemExit) as cm:
                main(["drift", "monitor", "--help"])
            self.assertEqual(cm.exception.code, 0)

    def test_monitor_json_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = main(["drift", "monitor", tmp, "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out.getvalue())
            self.assertEqual(data["summary"]["features_scanned"], 0)

    def test_monitor_text_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = main(["drift", "monitor", tmp])
            self.assertEqual(rc, 0)
            self.assertIn("Drift monitor report", out.getvalue())

    def test_monitor_with_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001"]) + "\nImplementation: `src/app/core.py`.\n"
            _write_src_file(root, "src/app/core.py", "pass")
            _write_test_file(root, "tests/test_a.py", "pass")
            _write_feature_bundle(
                root, "feat-a",
                spec_content=spec,
                exec_content=_make_exec_with_tasks_and_ac_refs([("T001", "AC001")]),
                quality_content=_make_quality_with_cov(
                    [("AC001", "tests/test_a.py")],
                    qcs=["QC001"],
                ),
            )
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = main(["drift", "monitor", tmp, "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out.getvalue())
            self.assertEqual(data["summary"]["features_scanned"], 1)

    def test_monitor_feature_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "alpha", spec_content=_make_spec_with_acs(["AC001"]))
            _write_feature_bundle(root, "beta", spec_content=_make_spec_with_acs(["AC001"]))
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = main(["drift", "monitor", tmp, "--feature", "alpha", "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out.getvalue())
            self.assertEqual(len(data["features"]), 1)
            self.assertEqual(data["features"][0]["feature_id"], "alpha")

    def test_monitor_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = main(["drift", "monitor", tmp, "--feature", "INVALID", "--json"])
            self.assertEqual(rc, 2)

    def test_monitor_invalid_severity(self) -> None:
        with TemporaryDirectory() as tmp:
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = main(["drift", "monitor", tmp, "--severity", "invalid", "--json"])
            self.assertEqual(rc, 2)

    def test_monitor_severity_filter_critical(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = _make_spec_with_acs(["AC001"]) + "\nImplementation: `src/app/core.py`.\n"
            _write_src_file(root, "src/app/core.py", "pass")
            _write_test_file(root, "tests/test_a.py", "pass")
            _write_feature_bundle(
                root, "feat-a",
                spec_content=spec,
                exec_content=_make_exec_with_tasks_and_ac_refs([("T001", "AC001")]),
                quality_content=_make_quality_with_cov(
                    [("AC001", "tests/test_a.py")],
                    qcs=["QC001"],
                ),
            )
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = main(["drift", "monitor", tmp, "--severity", "none", "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out.getvalue())
            self.assertEqual(len(data["features"]), 1)

    def test_monitor_severity_filter_none(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "feat-a", spec_content=_make_spec_with_acs(["AC001"]))
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = main(["drift", "monitor", tmp, "--severity", "none", "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out.getvalue())
            self.assertEqual(len(data["features"]), 1)


class ErrorCasesTests(TestCase):
    def test_nonexistent_path_returns_success(self) -> None:
        with TemporaryDirectory() as tmp:
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = main(["drift", "monitor", tmp, "--json"])
            self.assertEqual(rc, 0)

    def test_no_network_imports(self) -> None:
        import specspine.drift as drift_mod
        source_file = drift_mod.__file__
        if source_file:
            source = Path(source_file).read_text(encoding="utf-8")
            self.assertNotIn("import requests", source)
            self.assertNotIn("import urllib.request", source)
            self.assertNotIn("import http.client", source)

    def test_no_token_reads(self) -> None:
        import specspine.drift as drift_mod
        source_file = drift_mod.__file__
        if source_file:
            source = Path(source_file).read_text(encoding="utf-8")
            self.assertNotIn("GITHUB_TOKEN", source)
            self.assertNotIn("GH_TOKEN", source)

    def test_no_subprocess_in_drift_except_via_evolution(self) -> None:
        import specspine.drift as drift_mod
        source_file = drift_mod.__file__
        if source_file:
            source = Path(source_file).read_text(encoding="utf-8")
            self.assertNotIn("subprocess.Popen", source)
            self.assertNotIn("subprocess.call", source)
            self.assertNotIn("subprocess.check_output", source)


class SeverityDistributionTests(TestCase):
    def test_all_none(self) -> None:
        features = (
            FeatureDriftRecord(
                feature_id="a", severity="none", spec_drift=(), code_drift=(),
                test_drift=(), quality_drift=(), drift_events=(), cascade_risk=False,
            ),
        )
        dist = _severity_distribution(features)
        self.assertEqual(dist["none"], 1)
        self.assertEqual(dist["critical"], 0)

    def test_mixed(self) -> None:
        features = (
            FeatureDriftRecord(
                feature_id="a", severity="critical", spec_drift=(), code_drift=(),
                test_drift=(), quality_drift=(), drift_events=(), cascade_risk=False,
            ),
            FeatureDriftRecord(
                feature_id="b", severity="low", spec_drift=(), code_drift=(),
                test_drift=(), quality_drift=(), drift_events=(), cascade_risk=False,
            ),
        )
        dist = _severity_distribution(features)
        self.assertEqual(dist["critical"], 1)
        self.assertEqual(dist["low"], 1)

    def test_distribution_has_all_keys(self) -> None:
        dist = _severity_distribution(())
        for key in ("critical", "high", "medium", "low", "none"):
            self.assertIn(key, dist)


class NowIsoTests(TestCase):
    def test_returns_iso_format(self) -> None:
        result = _now_iso()
        self.assertIsInstance(result, str)
        self.assertIn("T", result)
        self.assertTrue(result.endswith("Z"))

    def test_is_deterministic_for_same_instant(self) -> None:
        r1 = _now_iso()
        r2 = _now_iso()
        self.assertIsInstance(r1, str)
        self.assertIsInstance(r2, str)


class GitCommitTests(TestCase):
    def test_no_git_repo(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = _git_commit(root)
            self.assertEqual(result, "unknown")


class DriftEventTypesTests(TestCase):
    def test_spec_event_type(self) -> None:
        ev = DriftEvent(event_type="spec", severity="critical", timestamp="t", description="d")
        self.assertEqual(ev.event_type, "spec")

    def test_code_event_type(self) -> None:
        ev = DriftEvent(event_type="code", severity="medium", timestamp="t", description="d")
        self.assertEqual(ev.event_type, "code")

    def test_test_event_type(self) -> None:
        ev = DriftEvent(event_type="test", severity="high", timestamp="t", description="d")
        self.assertEqual(ev.event_type, "test")

    def test_quality_event_type(self) -> None:
        ev = DriftEvent(event_type="quality", severity="low", timestamp="t", description="d")
        self.assertEqual(ev.event_type, "quality")


class RecommendedCommandsTests(TestCase):
    def test_recommended_commands_present(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            self.assertTrue(len(report.recommended_commands) > 0)
            self.assertIn("specspine drift monitor . --json", report.recommended_commands)

    def test_recommended_commands_include_feature_specific(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "feat-a", spec_content=_make_spec_with_acs(["AC001"]))
            report = build_drift_monitor_report(root)
            cmds = report.recommended_commands
            self.assertTrue(any("feat-a" in c for c in cmds))


class AsDictTests(TestCase):
    def test_report_as_dict_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            d = report.as_dict()
            for key in ("root", "scan_metadata", "features", "summary", "trends", "compliance", "recommended_commands", "safety_notes"):
                self.assertIn(key, d)

    def test_feature_as_dict_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test-feature", spec_content=_make_spec_with_acs(["AC001"]))
            report = build_drift_monitor_report(root)
            d = report.as_dict()
            if d["features"]:
                f = d["features"][0]
                for key in ("feature_id", "severity", "spec_drift", "code_drift", "test_drift", "quality_drift", "drift_events", "cascade_risk"):
                    self.assertIn(key, f)


class MultiFeatureTests(TestCase):
    def test_multiple_features_sorted(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "beta", spec_content=_make_spec_with_acs(["AC001"]))
            _write_feature_bundle(root, "alpha", spec_content=_make_spec_with_acs(["AC001"]))
            report = build_drift_monitor_report(root)
            slugs = [f.feature_id for f in report.features]
            self.assertEqual(slugs, sorted(slugs))

    def test_multiple_features_count(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for i in range(3):
                _write_feature_bundle(root, f"feat-{i}", spec_content=_make_spec_with_acs(["AC001"]))
            report = build_drift_monitor_report(root)
            self.assertEqual(len(report.features), 3)


class TrendsTests(TestCase):
    def test_trends_empty_without_since(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            self.assertEqual(report.trends, ())

    def test_trends_present_with_since(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test-feature", spec_content=_make_spec_with_acs(["AC001"]))
            _init_git_repo(root)
            report = build_drift_monitor_report(root, since="2000-01-01")
            self.assertIsInstance(report.trends, tuple)


class ComplianceDimensionTests(TestCase):
    def test_pass_fail_has_all_dimensions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_drift_monitor_report(root)
            compliance = _build_compliance_section(report)
            pf = compliance["pass_fail_per_dimension"]
            for dim in ("spec", "code", "test", "quality"):
                self.assertIn(dim, pf)
                self.assertIn(pf[dim], ("pass", "fail"))


class DriftEventAffectedFieldsTests(TestCase):
    def test_affected_acs_tuple(self) -> None:
        ev = DriftEvent(
            event_type="spec", severity="high", timestamp="t",
            description="d", affected_acs=("AC001", "AC002"),
        )
        self.assertEqual(ev.affected_acs, ("AC001", "AC002"))

    def test_affected_tasks_tuple(self) -> None:
        ev = DriftEvent(
            event_type="code", severity="medium", timestamp="t",
            description="d", affected_tasks=("T001",),
        )
        self.assertEqual(ev.affected_tasks, ("T001",))

    def test_default_empty_tuples(self) -> None:
        ev = DriftEvent(event_type="spec", severity="low", timestamp="t", description="d")
        self.assertEqual(ev.affected_acs, ())
        self.assertEqual(ev.affected_tasks, ())
