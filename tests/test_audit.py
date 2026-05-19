import json
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from specspine.cli import main
from specspine.audit import (
    AuditEvent,
    AuditTrail,
    ComplianceReport,
    _build_drift_history,
    _build_lifecycle_transitions,
    _collect_audit_events,
    _feature_peer_content,
    _gather_validation_evidence,
    _generate_compliance_summary,
    _hash_content,
    _now_iso,
    build_compliance_report,
    render_compliance_json,
    render_compliance_text,
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


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "add", "."], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(root), capture_output=True, check=True)


def _git_commit(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=str(root), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=str(root), capture_output=True, check=True)


def _make_spec(acs: list[str], status: str = "validated") -> str:
    lines = [
        "# Test Feature",
        "",
        "Feature ID: test-feature",
        f"Status: {status}",
        "",
        "## Acceptance Criteria",
        "",
    ]
    for ac in acs:
        lines.append(f"- [x] {ac}: Description here.")
    lines.append("")
    return "\n".join(lines)


def _make_exec(tasks: list[str]) -> str:
    lines = [
        "# Test Feature Execution",
        "",
        "Feature ID: test-feature",
        "Status: validated",
        "",
        "## Tasks",
        "",
    ]
    for task in tasks:
        lines.append(f"- [x] {task}: Implementation task.")
    lines.append("")
    return "\n".join(lines)


def _make_quality(cov_links: list[tuple[str, str]], qcs: list[str] | None = None) -> str:
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


class AuditEventTests(TestCase):
    def test_audit_event_as_dict(self) -> None:
        ev = AuditEvent(
            event_type="lifecycle",
            timestamp="2024-01-01T00:00:00Z",
            feature_id="test-feature",
            description="Status changed",
            evidence_hash="abc123",
            actor="test-user",
        )
        d = ev.as_dict()
        self.assertEqual(d["event_type"], "lifecycle")
        self.assertEqual(d["feature_id"], "test-feature")
        self.assertEqual(d["evidence_hash"], "abc123")
        self.assertEqual(d["actor"], "test-user")

    def test_audit_event_minimal(self) -> None:
        ev = AuditEvent(
            event_type="file_change",
            timestamp="2024-01-01T00:00:00Z",
            feature_id="test",
            description="Changed file",
        )
        d = ev.as_dict()
        self.assertEqual(d["evidence_hash"], "")
        self.assertEqual(d["actor"], "")

    def test_audit_event_frozen(self) -> None:
        ev = AuditEvent(
            event_type="test",
            timestamp="2024-01-01T00:00:00Z",
            feature_id="test",
            description="desc",
        )
        with self.assertRaises(AttributeError):
            ev.event_type = "new"


class AuditTrailTests(TestCase):
    def test_audit_trail_as_dict(self) -> None:
        ev = AuditEvent(
            event_type="lifecycle",
            timestamp="2024-01-01T00:00:00Z",
            feature_id="test",
            description="desc",
        )
        trail = AuditTrail(
            feature_id="test",
            events=(ev,),
            lifecycle_transitions=({"from_status": "proposed", "to_status": "planned"},),
            validation_evidence={"spec": {"exists": True}},
            drift_history=({"date": "2024-01-01", "event_type": "spec"},),
        )
        d = trail.as_dict()
        self.assertEqual(d["feature_id"], "test")
        self.assertEqual(len(d["events"]), 1)
        self.assertEqual(len(d["lifecycle_transitions"]), 1)
        self.assertTrue(d["validation_evidence"]["spec"]["exists"])
        self.assertEqual(len(d["drift_history"]), 1)

    def test_audit_trail_empty(self) -> None:
        trail = AuditTrail(feature_id="test")
        d = trail.as_dict()
        self.assertEqual(d["events"], [])
        self.assertEqual(d["lifecycle_transitions"], [])
        self.assertEqual(d["drift_history"], [])

    def test_audit_trail_frozen(self) -> None:
        trail = AuditTrail(feature_id="test")
        with self.assertRaises(AttributeError):
            trail.feature_id = "new"


class ComplianceReportTests(TestCase):
    def test_compliance_report_as_dict(self) -> None:
        trail = AuditTrail(feature_id="test")
        report = ComplianceReport(
            root=Path("/tmp"),
            audit_date="2024-01-01T00:00:00Z",
            scope="workspace",
            features=(trail,),
            compliance_summary={"total_features": 1},
            evidence_hashes=("hash1",),
            recommendations=("rec1",),
            safety_notes=("note1",),
        )
        d = report.as_dict()
        self.assertEqual(d["audit_date"], "2024-01-01T00:00:00Z")
        self.assertEqual(d["scope"], "workspace")
        self.assertEqual(len(d["features"]), 1)
        self.assertEqual(d["evidence_hashes"], ["hash1"])

    def test_compliance_report_frozen(self) -> None:
        report = ComplianceReport(
            root=Path("/tmp"),
            audit_date="2024-01-01",
            scope="workspace",
            features=(),
            compliance_summary={},
            evidence_hashes=(),
            recommendations=(),
            safety_notes=(),
        )
        with self.assertRaises(AttributeError):
            report.audit_date = "new"


class HelperTests(TestCase):
    def test_now_iso_returns_iso_format(self) -> None:
        result = _now_iso()
        self.assertRegex(result, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_hash_content_deterministic(self) -> None:
        h1 = _hash_content("hello")
        h2 = _hash_content("hello")
        self.assertEqual(h1, h2)

    def test_hash_content_different(self) -> None:
        h1 = _hash_content("hello")
        h2 = _hash_content("world")
        self.assertNotEqual(h1, h2)

    def test_hash_content_is_sha256(self) -> None:
        h = _hash_content("test")
        self.assertEqual(len(h), 64)

    def test_feature_peer_content_existing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            content = _feature_peer_content(root, "test", "spec")
            self.assertIsNotNone(content)
            self.assertIn("Feature ID: test", content)

    def test_feature_peer_content_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = _feature_peer_content(root, "test", "spec")
            self.assertIsNone(content)

    def test_feature_peer_content_invalid_kind(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = _feature_peer_content(root, "test", "invalid")
            self.assertIsNone(content)


class CollectAuditEventsTests(TestCase):
    def test_collect_no_peer_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            events = _collect_audit_events("test", root, None)
            self.assertEqual(events, [])

    def test_collect_without_git(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test")
            events = _collect_audit_events("test", root, None)
            self.assertEqual(events, [])

    def test_collect_with_git(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            events = _collect_audit_events("test", root, None)
            self.assertGreaterEqual(len(events), 1)

    def test_collect_event_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            events = _collect_audit_events("test", root, None)
            self.assertGreater(len(events), 0)
            ev = events[0]
            self.assertEqual(ev.feature_id, "test")
            self.assertTrue(ev.timestamp)
            self.assertTrue(ev.description)

    def test_collect_since_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            events = _collect_audit_events("test", root, "2099-01-01")
            self.assertEqual(events, [])

    def test_collect_since_allows_events(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            events = _collect_audit_events("test", root, "2000-01-01")
            self.assertGreaterEqual(len(events), 1)


class LifecycleTransitionTests(TestCase):
    def test_no_peer_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            transitions = _build_lifecycle_transitions("test", root)
            self.assertEqual(transitions, [])

    def test_single_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test\nStatus: proposed")
            _init_git_repo(root)
            transitions = _build_lifecycle_transitions("test", root)
            self.assertGreaterEqual(len(transitions), 1)

    def test_transition_records_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test\nStatus: proposed")
            _init_git_repo(root)
            transitions = _build_lifecycle_transitions("test", root)
            self.assertGreater(len(transitions), 0)
            t = transitions[0]
            self.assertIn("from_status", t)
            self.assertIn("to_status", t)
            self.assertIn("date", t)
            self.assertIn("author", t)

    def test_status_change_detected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test\nStatus: proposed")
            _init_git_repo(root)
            spec_path = root / "specs/features" / "test.md"
            spec_path.write_text("# Test\n\nFeature ID: test\nStatus: validated", encoding="utf-8")
            _git_commit(root, "change status to validated")
            transitions = _build_lifecycle_transitions("test", root)
            statuses = [t["to_status"] for t in transitions]
            self.assertIn("validated", statuses)


class ValidationEvidenceTests(TestCase):
    def test_no_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = _gather_validation_evidence("test", root)
            self.assertFalse(evidence["spec"]["exists"])
            self.assertFalse(evidence["execution"]["exists"])
            self.assertFalse(evidence["quality"]["exists"])

    def test_spec_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content=_make_spec(["AC001"]))
            evidence = _gather_validation_evidence("test", root)
            self.assertTrue(evidence["spec"]["exists"])
            self.assertEqual(evidence["spec"]["ac_count"], 1)
            self.assertFalse(evidence["execution"]["exists"])

    def test_full_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(
                root, "test",
                spec_content=_make_spec(["AC001", "AC002"]),
                exec_content=_make_exec(["T001", "T002"]),
                quality_content=_make_quality([("AC001", "tests/test_a.py"), ("AC002", "tests/test_b.py")]),
            )
            evidence = _gather_validation_evidence("test", root)
            self.assertTrue(evidence["spec"]["exists"])
            self.assertEqual(evidence["spec"]["ac_count"], 2)
            self.assertTrue(evidence["execution"]["exists"])
            self.assertEqual(evidence["execution"]["task_count"], 2)
            self.assertTrue(evidence["quality"]["exists"])
            self.assertEqual(evidence["quality"]["coverage_links"], 2)

    def test_uncovered_acs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(
                root, "test",
                spec_content=_make_spec(["AC001", "AC002"]),
                quality_content=_make_quality([("AC001", "tests/test_a.py")]),
            )
            evidence = _gather_validation_evidence("test", root)
            checks = evidence["validation_checks"]
            ac_check = [c for c in checks if c["check"] == "ac_coverage"]
            self.assertEqual(len(ac_check), 1)
            self.assertEqual(ac_check[0]["status"], "fail")

    def test_all_covered(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(
                root, "test",
                spec_content=_make_spec(["AC001"]),
                quality_content=_make_quality([("AC001", "tests/test_a.py")]),
            )
            evidence = _gather_validation_evidence("test", root)
            checks = evidence["validation_checks"]
            ac_check = [c for c in checks if c["check"] == "ac_coverage"]
            self.assertEqual(ac_check[0]["status"], "pass")

    def test_missing_execution_check(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content=_make_spec(["AC001"]))
            evidence = _gather_validation_evidence("test", root)
            checks = evidence["validation_checks"]
            exec_check = [c for c in checks if c["check"] == "execution_present"]
            self.assertEqual(exec_check[0]["status"], "fail")

    def test_missing_quality_check(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content=_make_spec(["AC001"]))
            evidence = _gather_validation_evidence("test", root)
            checks = evidence["validation_checks"]
            qual_check = [c for c in checks if c["check"] == "quality_present"]
            self.assertEqual(qual_check[0]["status"], "fail")


class DriftHistoryTests(TestCase):
    def test_no_peer_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            history = _build_drift_history("test", root, None)
            self.assertEqual(history, [])

    def test_without_git(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test")
            history = _build_drift_history("test", root, None)
            self.assertEqual(history, [])

    def test_with_git(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            history = _build_drift_history("test", root, None)
            self.assertGreaterEqual(len(history), 1)

    def test_drift_entry_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            history = _build_drift_history("test", root, None)
            self.assertGreater(len(history), 0)
            entry = history[0]
            self.assertIn("commit", entry)
            self.assertIn("date", entry)
            self.assertIn("event_type", entry)
            self.assertIn("severity", entry)

    def test_since_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            history = _build_drift_history("test", root, "2099-01-01")
            self.assertEqual(history, [])

    def test_since_allows(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            history = _build_drift_history("test", root, "2000-01-01")
            self.assertGreaterEqual(len(history), 1)


class ComplianceSummaryTests(TestCase):
    def test_empty_trails(self) -> None:
        summary = _generate_compliance_summary([])
        self.assertEqual(summary["total_features"], 0)
        self.assertEqual(summary["compliant_features"], 0)
        self.assertEqual(summary["compliance_rate"], 0.0)

    def test_single_compliant_feature(self) -> None:
        trail = AuditTrail(
            feature_id="test",
            lifecycle_transitions=({"from_status": "proposed", "to_status": "planned"},),
            validation_evidence={
                "spec": {"exists": True, "ac_count": 1, "acs": ["AC001"]},
                "execution": {"exists": True, "task_count": 1, "tasks": ["T001"]},
                "quality": {"exists": True, "qc_count": 0, "coverage_links": 1, "qcs": []},
                "validation_checks": [
                    {"check": "ac_coverage", "status": "pass", "detail": "All ACs have coverage links"},
                    {"check": "execution_present", "status": "pass", "detail": "Execution file exists"},
                    {"check": "quality_present", "status": "pass", "detail": "Quality file exists"},
                ],
            },
        )
        summary = _generate_compliance_summary([trail])
        self.assertEqual(summary["total_features"], 1)
        self.assertEqual(summary["compliant_features"], 1)
        self.assertEqual(summary["compliance_rate"], 1.0)

    def test_single_non_compliant_feature(self) -> None:
        trail = AuditTrail(
            feature_id="test",
            validation_evidence={
                "spec": {"exists": False, "ac_count": 0, "acs": []},
                "execution": {"exists": False, "task_count": 0, "tasks": []},
                "quality": {"exists": False, "qc_count": 0, "coverage_links": 0, "qcs": []},
                "validation_checks": [],
            },
        )
        summary = _generate_compliance_summary([trail])
        self.assertEqual(summary["compliant_features"], 0)
        self.assertGreater(len(summary["gaps"]), 0)

    def test_compliance_rate_calculation(self) -> None:
        compliant = AuditTrail(
            feature_id="pass",
            lifecycle_transitions=({"from_status": "a", "to_status": "b"},),
            validation_evidence={
                "spec": {"exists": True},
                "execution": {"exists": True},
                "quality": {"exists": True},
                "validation_checks": [],
            },
        )
        non_compliant = AuditTrail(
            feature_id="fail",
            validation_evidence={
                "spec": {"exists": False},
                "execution": {"exists": False},
                "quality": {"exists": False},
                "validation_checks": [],
            },
        )
        summary = _generate_compliance_summary([compliant, non_compliant])
        self.assertEqual(summary["total_features"], 2)
        self.assertEqual(summary["compliant_features"], 1)
        self.assertAlmostEqual(summary["compliance_rate"], 0.5)

    def test_gaps_populated(self) -> None:
        trail = AuditTrail(
            feature_id="test",
            validation_evidence={
                "spec": {"exists": False},
                "execution": {"exists": False},
                "quality": {"exists": False},
                "validation_checks": [],
            },
        )
        summary = _generate_compliance_summary([trail])
        gaps = summary["gaps"]
        self.assertTrue(any("missing spec" in g for g in gaps))
        self.assertTrue(any("missing execution" in g for g in gaps))
        self.assertTrue(any("missing quality" in g for g in gaps))

    def test_lifecycle_check(self) -> None:
        trail = AuditTrail(
            feature_id="test",
            validation_evidence={
                "spec": {"exists": True},
                "execution": {"exists": True},
                "quality": {"exists": True},
                "validation_checks": [],
            },
        )
        summary = _generate_compliance_summary([trail])
        pf = summary["pass_fail_per_dimension"]
        self.assertEqual(pf.get("test_lifecycle"), "fail")


class BuildComplianceReportTests(TestCase):
    def test_empty_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_compliance_report(root)
            self.assertEqual(len(report.features), 0)
            self.assertEqual(report.scope, "workspace")

    def test_single_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            report = build_compliance_report(root, feature_filter="test")
            self.assertEqual(len(report.features), 1)
            self.assertEqual(report.features[0].feature_id, "test")

    def test_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(InvalidFeatureSlug):
                build_compliance_report(root, feature_filter="INVALID")

    def test_multiple_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "alpha", spec_content="# Alpha\n\nFeature ID: alpha")
            _write_feature_bundle(root, "beta", spec_content="# Beta\n\nFeature ID: beta")
            _init_git_repo(root)
            report = build_compliance_report(root)
            self.assertEqual(len(report.features), 2)

    def test_features_sorted(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "beta", spec_content="# Beta\n\nFeature ID: beta")
            _write_feature_bundle(root, "alpha", spec_content="# Alpha\n\nFeature ID: alpha")
            _init_git_repo(root)
            report = build_compliance_report(root)
            slugs = [f.feature_id for f in report.features]
            self.assertEqual(slugs, sorted(slugs))

    def test_recommendations_generated(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_compliance_report(root)
            self.assertGreater(len(report.recommendations), 0)

    def test_safety_notes_present(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_compliance_report(root)
            self.assertGreater(len(report.safety_notes), 0)

    def test_evidence_hashes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            report = build_compliance_report(root, feature_filter="test")
            self.assertEqual(len(report.evidence_hashes), 1)
            self.assertEqual(len(report.evidence_hashes[0]), 64)

    def test_scope_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            report = build_compliance_report(root, feature_filter="test")
            self.assertEqual(report.scope, "feature")

    def test_scope_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            report = build_compliance_report(root)
            self.assertEqual(report.scope, "workspace")


class RenderJsonTests(TestCase):
    def test_json_output_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_compliance_report(root)
            output = render_compliance_json(report)
            parsed = json.loads(output)
            self.assertIn("features", parsed)
            self.assertIn("compliance_summary", parsed)

    def test_json_output_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_compliance_report(root)
            output = render_compliance_json(report)
            parsed = json.loads(output)
            for key in ("audit_date", "scope", "features", "compliance_summary", "evidence_hashes", "recommendations", "safety_notes", "root"):
                self.assertIn(key, parsed)

    def test_json_sorted_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_compliance_report(root)
            output = render_compliance_json(report)
            parsed = json.loads(output)
            keys = list(parsed.keys())
            self.assertEqual(keys, sorted(keys))


class RenderTextTests(TestCase):
    def test_text_output_not_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_compliance_report(root)
            output = render_compliance_text(report)
            self.assertGreater(len(output), 0)

    def test_text_contains_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_compliance_report(root)
            output = render_compliance_text(report)
            self.assertIn("Summary:", output)

    def test_text_contains_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_compliance_report(root)
            output = render_compliance_text(report)
            self.assertIn("Features:", output)

    def test_text_contains_recommendations(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_compliance_report(root)
            output = render_compliance_text(report)
            self.assertIn("Recommendations:", output)

    def test_text_contains_safety(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_compliance_report(root)
            output = render_compliance_text(report)
            self.assertIn("Safety notes:", output)

    def test_text_with_feature(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            report = build_compliance_report(root, feature_filter="test")
            output = render_compliance_text(report)
            self.assertIn("test", output)

    def test_text_compliance_dimensions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            report = build_compliance_report(root, feature_filter="test")
            output = render_compliance_text(report)
            self.assertIn("Compliance dimensions:", output)


class CliReportTests(TestCase):
    def test_audit_report_help(self) -> None:
        out = StringIO()
        err = StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = main(["audit", "report", "--help"])
            except SystemExit as e:
                code = e.code
        self.assertEqual(code, 0)

    def test_audit_report_json(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = main(["audit", "report", str(root), "--json"])
            self.assertEqual(code, 0)
            result = json.loads(out.getvalue())
            self.assertIn("features", result)

    def test_audit_report_text(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = main(["audit", "report", str(root)])
            self.assertEqual(code, 0)
            output = out.getvalue()
            self.assertIn("Compliance audit report:", output)

    def test_audit_report_feature_filter(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _write_feature_bundle(root, "other", spec_content="# Other\n\nFeature ID: other")
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = main(["audit", "report", str(root), "--json", "--feature", "test"])
            self.assertEqual(code, 0)
            result = json.loads(out.getvalue())
            slugs = [f["feature_id"] for f in result["features"]]
            self.assertEqual(slugs, ["test"])

    def test_audit_report_since(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            _init_git_repo(root)
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = main(["audit", "report", str(root), "--json", "--since", "2099-01-01"])
            self.assertEqual(code, 0)
            result = json.loads(out.getvalue())
            self.assertEqual(result["scope"], "workspace")

    def test_audit_report_output_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "test", spec_content="# Test\n\nFeature ID: test")
            output_file = root / "report.json"
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = main(["audit", "report", str(root), "--json", "--output", str(output_file)])
            self.assertEqual(code, 0)
            self.assertTrue(output_file.exists())
            result = json.loads(output_file.read_text())
            self.assertIn("features", result)

    def test_audit_report_invalid_slug(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = main(["audit", "report", str(root), "--json", "--feature", "INVALID"])
            self.assertEqual(code, 2)

    def test_audit_report_empty_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = main(["audit", "report", str(root), "--json"])
            self.assertEqual(code, 0)
            result = json.loads(out.getvalue())
            self.assertEqual(result["features"], [])

    def test_audit_report_multiple_features(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_feature_bundle(root, "alpha", spec_content="# Alpha\n\nFeature ID: alpha")
            _write_feature_bundle(root, "beta", spec_content="# Beta\n\nFeature ID: beta")
            out = StringIO()
            err = StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = main(["audit", "report", str(root), "--json"])
            self.assertEqual(code, 0)
            result = json.loads(out.getvalue())
            slugs = [f["feature_id"] for f in result["features"]]
            self.assertIn("alpha", slugs)
            self.assertIn("beta", slugs)
