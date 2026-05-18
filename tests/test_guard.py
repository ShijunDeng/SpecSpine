from __future__ import annotations
import json
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from specspine.cli import main
from specspine.features import InvalidFeatureSlug
from specspine.guard import (
    GUARD_CACHE_DIR, STATUS_MISSING, STATUS_PARTIAL, STATUS_VERIFIED, VERIFICATION_STATUSES,
    ConsistencyCheck, ConsistencyResult, DriftEntry, DriftResult, FeatureHealthEntry,
    GuardAcceptanceCriterion, GuardTask, SpecParseResult, WorkspaceHealthResult,
    _classify_ac, _collect_implementation_files, _compute_file_hashes, _extract_expected_artifacts,
    _extract_task_files, _load_cache, _save_cache, _score_ac_evidence,
    check_spec_consistency, compute_workspace_health, detect_drift, parse_feature_spec,
    render_check_json, render_check_text, render_drift_json, render_drift_text,
    render_guard_json, render_guard_text, render_score_json, render_score_text,
)

def wf(root, slug="test-feature", ac_lines=None, task_lines=None, impl_files=None):
    (root/"specs/features").mkdir(parents=True, exist_ok=True)
    (root/"execution/features").mkdir(parents=True, exist_ok=True)
    (root/"quality/features").mkdir(parents=True, exist_ok=True)
    ac = "\n".join(ac_lines or ["- [ ] User can create an account."])
    (root/"specs/features"/f"{slug}.md").write_text(f"# Test Feature\n\nFeature ID: {slug}\nStatus: in-progress\n\n## Acceptance Criteria\n\n{ac}\n", encoding="utf-8")
    tk = "\n".join(task_lines or ["- [ ] Implement user creation."])
    (root/"execution/features"/f"{slug}.md").write_text(f"# Test Feature Execution\n\nFeature ID: {slug}\nStatus: in-progress\n\n## Tasks\n\n{tk}\n", encoding="utf-8")
    (root/"quality/features"/f"{slug}.md").write_text(f"# Test Feature Quality\n\nFeature ID: {slug}\nStatus: in-progress\n\n## Required Checks\n\n- [ ] Acceptance criteria reviewed.\n\n## Test Coverage\n\n- [ ] AC001 -> tests/test_feature.py\n\n## Test Plan\n\n- Run tests.\n\n## Release Readiness\n\n- [ ] Ready.\n", encoding="utf-8")
    if impl_files:
        for rp, ct in impl_files.items():
            fp = root / rp; fp.parent.mkdir(parents=True, exist_ok=True); fp.write_text(ct, encoding="utf-8")

def wfi(root, slug="user-auth"):
    wf(root, slug=slug, ac_lines=["- [x] Users can create an account with email and password.", "- [x] Users can log in with valid credentials.", "- [ ] Users can reset their password."], task_lines=["- [x] Implement user creation endpoint.", "- [x] Implement login endpoint.", "- [ ] Implement password reset flow."], impl_files={"src/auth/user.py": "\nclass User:\n    def __init__(self, email, password):\n        self.email = email\n        self.password = password\n    def create_account(self, email, password):\n        return User(email, password)\n    def login(self, email, password):\n        return email == self.email and password == self.password\n", "src/auth/service.py": "\ndef handle_login(request):\n    email = request.get('email')\n    password = request.get('password')\n    user = find_user(email)\n    return create_session(user) if user else None\n\ndef create_account(email, password):\n    validate_email(email)\n    user = User(email, password)\n    user.save()\n    return user\n", "tests/test_auth.py": "\ndef test_create_account():\n    user = create_account('test@example.com', 'password123')\n    assert user.email == 'test@example.com'\n\ndef test_login():\n    assert True\n"})

class SpecParseTests(TestCase):
    def test_extracts_acs(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = parse_feature_spec("test-feature", r)
            self.assertEqual(res.feature_id, "test-feature"); self.assertEqual(len(res.acceptance_criteria), 1); self.assertEqual(res.acceptance_criteria[0].id, "AC001")
    def test_extracts_multiple_acs(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r, ac_lines=["- [ ] User can create an account.", "- [ ] User can log in.", "- [ ] User can reset password."])
            res = parse_feature_spec("test-feature", r); self.assertEqual(len(res.acceptance_criteria), 3)
    def test_extracts_tasks(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = parse_feature_spec("test-feature", r); self.assertEqual(len(res.tasks), 1); self.assertEqual(res.tasks[0].id, "T001"); self.assertFalse(res.tasks[0].done)
    def test_extracts_done_tasks(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r, task_lines=["- [x] Implement user creation.", "- [ ] Implement login."])
            res = parse_feature_spec("test-feature", r); self.assertTrue(res.tasks[0].done); self.assertFalse(res.tasks[1].done)
    def test_extracts_status(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = parse_feature_spec("test-feature", r); self.assertEqual(res.status, "in-progress")
    def test_has_native_files_true(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = parse_feature_spec("test-feature", r); self.assertTrue(res.has_native_files)
    def test_has_native_files_false(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); res = parse_feature_spec("test-feature", r); self.assertFalse(res.has_native_files)
    def test_missing_files(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); res = parse_feature_spec("test-feature", r); self.assertGreater(len(res.missing_files), 0)
    def test_invalid_slug(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp)
            with self.assertRaises(InvalidFeatureSlug): parse_feature_spec("INVALID SLUG", r)
    def test_expected_artifacts(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r, ac_lines=["- [ ] Users can create an account with email and password."])
            res = parse_feature_spec("test-feature", r); self.assertIsInstance(res.acceptance_criteria[0].expected_artifacts, list)
    def test_as_dict(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = parse_feature_spec("test-feature", r); d = res.as_dict(); self.assertEqual(d["feature_id"], "test-feature"); self.assertIn("acceptance_criteria", d)
    def test_with_all_files(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wfi(r); res = parse_feature_spec("user-auth", r)
            self.assertEqual(res.feature_id, "user-auth"); self.assertEqual(len(res.acceptance_criteria), 3); self.assertEqual(len(res.tasks), 3)

class CodeToSpecMappingTests(TestCase):
    def test_returns_result(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wfi(r); res = check_spec_consistency("user-auth", r)
            self.assertIn(res.status, ("all_verified", "partially_verified", "partial_evidence")); self.assertGreater(res.score, 0)
    def test_no_impl_files(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = check_spec_consistency("test-feature", r); self.assertEqual(res.status, "no_evidence"); self.assertEqual(res.score, 0)
    def test_no_feature_files(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); res = check_spec_consistency("test-feature", r); self.assertEqual(res.status, "missing"); self.assertEqual(res.score, 0)
    def test_invalid_slug(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp)
            with self.assertRaises(InvalidFeatureSlug): check_spec_consistency("INVALID", r)
    def test_checks_have_ac_id(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = check_spec_consistency("test-feature", r)
            self.assertGreater(len(res.checks), 0); self.assertEqual(res.checks[0].ac_id, "AC001")
    def test_checks_have_status(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = check_spec_consistency("test-feature", r)
            self.assertIn(res.checks[0].status, (STATUS_MISSING, STATUS_PARTIAL, STATUS_VERIFIED))
    def test_score_range(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = check_spec_consistency("test-feature", r)
            self.assertGreaterEqual(res.score, 0); self.assertLessEqual(res.score, 100)
    def test_as_dict(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = check_spec_consistency("test-feature", r); d = res.as_dict()
            self.assertIn("feature_id", d); self.assertIn("status", d); self.assertIn("score", d); self.assertIn("checks", d)

class ConsistencyClassificationTests(TestCase):
    def test_classify_returns_check(self):
        c = _classify_ac("AC001", "Users can create an account", [Path("test.py")], True)
        self.assertIsInstance(c, ConsistencyCheck); self.assertEqual(c.ac_id, "AC001")
    def test_classify_returns_status(self):
        c = _classify_ac("AC001", "handle user creation with validation", [Path("test.py")], True)
        self.assertIn(c.status, VERIFICATION_STATUSES)
    def test_classify_no_files(self):
        c = _classify_ac("AC001", "something", [], False); self.assertEqual(c.status, STATUS_MISSING)
    def test_classify_done_task(self):
        c = _classify_ac("AC001", "something", [], True); self.assertEqual(c.status, STATUS_PARTIAL)

class ScoreAcEvidenceTests(TestCase):
    def test_zero_for_no_match(self):
        self.assertEqual(_score_ac_evidence("something", "completely different text"), 0)
    def test_positive_for_match(self):
        self.assertGreater(_score_ac_evidence("create account user", "def create_account(user): pass"), 0)
    def test_returns_int(self):
        self.assertIsInstance(_score_ac_evidence("create", "create"), int)
    def test_max_100(self):
        self.assertLessEqual(_score_ac_evidence("create", "create"), 100)
    def test_empty_ac(self):
        self.assertEqual(_score_ac_evidence("", "anything"), 0)
    def test_empty_file(self):
        self.assertEqual(_score_ac_evidence("create account", ""), 0)

class DriftDetectionTests(TestCase):
    def test_first_run_no_drift(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = detect_drift("test-feature", r); self.assertFalse(res.has_drift); self.assertEqual(len(res.drift), 0)
    def test_returns_drift_result(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = detect_drift("test-feature", r); self.assertIsInstance(res, DriftResult)
    def test_feature_id(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = detect_drift("test-feature", r); self.assertEqual(res.feature_id, "test-feature")
    def test_as_dict(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = detect_drift("test-feature", r); d = res.as_dict()
            self.assertIn("feature_id", d); self.assertIn("has_drift", d); self.assertIn("drift", d)
    def test_invalid_slug(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp)
            with self.assertRaises(InvalidFeatureSlug): detect_drift("INVALID", r)

class CacheTests(TestCase):
    def test_save_and_load(self):
        with TemporaryDirectory() as tmp:
            cd = Path(tmp) / "cache"; _save_cache(cd, "test", {"key": "value", "score": 50})
            self.assertEqual(_load_cache(cd, "test"), {"key": "value", "score": 50})
    def test_load_missing(self):
        with TemporaryDirectory() as tmp:
            self.assertIsNone(_load_cache(Path(tmp) / "cache", "test"))
    def test_load_invalid_json(self):
        with TemporaryDirectory() as tmp:
            cd = Path(tmp) / "cache"; cd.mkdir(parents=True); (cd / "test.json").write_text("not json", encoding="utf-8")
            self.assertIsNone(_load_cache(cd, "test"))

class WorkspaceHealthTests(TestCase):
    def test_no_features(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); res = compute_workspace_health(r)
            self.assertEqual(res.workspace_score, 100); self.assertEqual(res.total_features, 0)
    def test_with_feature(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = compute_workspace_health(r); self.assertGreater(res.total_features, 0)
    def test_as_dict(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = compute_workspace_health(r); d = res.as_dict()
            self.assertIn("workspace_score", d); self.assertIn("total_features", d); self.assertIn("features", d)
    def test_score_range(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = compute_workspace_health(r)
            self.assertGreaterEqual(res.workspace_score, 0); self.assertLessEqual(res.workspace_score, 100)

class CollectImplFilesTests(TestCase):
    def test_finds_files(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); (r/"src").mkdir(); (r/"src/main.py").write_text("x", encoding="utf-8")
            self.assertGreater(len(_collect_implementation_files(r)), 0)
    def test_skips_pycache(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); (r/"__pycache__").mkdir(); (r/"__pycache__/mod.pyc").write_text("x", encoding="utf-8")
            self.assertEqual(len(_collect_implementation_files(r)), 0)
    def test_empty(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(len(_collect_implementation_files(Path(tmp))), 0)

class ComputeFileHashesTests(TestCase):
    def test_returns_hashes(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); (r/"file.txt").write_text("hello", encoding="utf-8"); h = _compute_file_hashes(r)
            self.assertIn("file.txt", h); self.assertIsInstance(h["file.txt"], str)
    def test_deterministic(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); (r/"file.txt").write_text("hello", encoding="utf-8")
            self.assertEqual(_compute_file_hashes(r), _compute_file_hashes(r))

class ExtractExpectedArtifactsTests(TestCase):
    def test_finds_keywords(self):
        self.assertIsInstance(_extract_expected_artifacts("handle user creation", "def handle_user_creation(): pass"), list)
    def test_empty_when_no_exec(self):
        self.assertEqual(_extract_expected_artifacts("something", None), [])
    def test_empty_when_no_match(self):
        self.assertEqual(_extract_expected_artifacts("something unrelated", "def foo(): pass"), [])

class ExtractTaskFilesTests(TestCase):
    def test_finds_existing_files(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); (r/"src").mkdir(parents=True); (r/"src/main.py").write_text("", encoding="utf-8")
            self.assertIn("src/main.py", _extract_task_files("Implement src/main.py", r))
    def test_empty_when_not_found(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(_extract_task_files("Implement something", Path(tmp)), [])

class RenderGuardTests(TestCase):
    def test_render_guard_json(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = parse_feature_spec("test-feature", r); p = json.loads(render_guard_json(res))
            self.assertEqual(p["feature_id"], "test-feature")
    def test_render_guard_text(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = parse_feature_spec("test-feature", r); self.assertIn("Spec parse: test-feature", render_guard_text(res))
    def test_render_check_json(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = check_spec_consistency("test-feature", r); p = json.loads(render_check_json(res))
            self.assertIn("feature_id", p)
    def test_render_check_text(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = check_spec_consistency("test-feature", r); self.assertIn("Consistency check: test-feature", render_check_text(res))
    def test_render_drift_json(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = detect_drift("test-feature", r); p = json.loads(render_drift_json(res))
            self.assertIn("feature_id", p)
    def test_render_drift_text(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = detect_drift("test-feature", r); self.assertIn("Drift detection: test-feature", render_drift_text(res))
    def test_render_score_json(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = compute_workspace_health(r); p = json.loads(render_score_json(res))
            self.assertIn("workspace_score", p)
    def test_render_score_text(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); res = compute_workspace_health(r); self.assertIn("Workspace health:", render_score_text(res))

class DataclassTests(TestCase):
    def test_guard_ac_as_dict(self):
        d = GuardAcceptanceCriterion(id="AC001", text="test").as_dict()
        self.assertEqual(d["id"], "AC001"); self.assertEqual(d["text"], "test")
    def test_guard_task_as_dict(self):
        d = GuardTask(id="T001", text="test", done=True).as_dict()
        self.assertEqual(d["id"], "T001"); self.assertTrue(d["done"])
    def test_spec_parse_result_as_dict(self):
        d = SpecParseResult(feature_id="test", acceptance_criteria=(), tasks=()).as_dict()
        self.assertEqual(d["feature_id"], "test")
    def test_consistency_check_as_dict(self):
        d = ConsistencyCheck(ac_id="AC001", ac_text="test", status=STATUS_VERIFIED).as_dict()
        self.assertEqual(d["ac_id"], "AC001")
    def test_consistency_result_as_dict(self):
        d = ConsistencyResult(feature_id="test", status="ok", checks=(), score=100).as_dict()
        self.assertEqual(d["score"], 100)
    def test_drift_entry_as_dict(self):
        d = DriftEntry(ac_id="AC001", previous_status=STATUS_VERIFIED, current_status=STATUS_MISSING).as_dict()
        self.assertEqual(d["ac_id"], "AC001")
    def test_drift_result_as_dict(self):
        d = DriftResult(feature_id="test", drift=(), has_drift=False).as_dict()
        self.assertFalse(d["has_drift"])
    def test_feature_health_entry_as_dict(self):
        d = FeatureHealthEntry(slug="test", score=80, status="ok").as_dict()
        self.assertEqual(d["score"], 80)
    def test_workspace_health_result_as_dict(self):
        d = WorkspaceHealthResult(features=(), workspace_score=75, total_features=0).as_dict()
        self.assertEqual(d["workspace_score"], 75)

class GuardCLITests(TestCase):
    def test_guard_parse_text(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): rc = main(["guard", "parse", "test-feature", str(r)])
            self.assertEqual(rc, 0); self.assertIn("Spec parse:", out.getvalue())
    def test_guard_parse_json(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): rc = main(["guard", "parse", "test-feature", str(r), "--json"])
            self.assertEqual(rc, 0); self.assertEqual(json.loads(out.getvalue())["feature_id"], "test-feature")
    def test_guard_check_text(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): main(["guard", "check", "test-feature", str(r)])
            self.assertIn("Consistency check:", out.getvalue())
    def test_guard_check_json(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): main(["guard", "check", "test-feature", str(r), "--json"])
            self.assertIn("feature_id", json.loads(out.getvalue()))
    def test_guard_drift_text(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): rc = main(["guard", "drift", str(r)])
            self.assertEqual(rc, 0); self.assertIn("Drift detection:", out.getvalue())
    def test_guard_drift_json(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): rc = main(["guard", "drift", str(r), "--json"])
            self.assertEqual(rc, 0); self.assertIn("has_drift", json.loads(out.getvalue()))
    def test_guard_score_text(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): main(["guard", "score", str(r)])
            self.assertIn("Workspace health:", out.getvalue())
    def test_guard_score_json(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); wf(r); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): main(["guard", "score", str(r), "--json"])
            self.assertIn("workspace_score", json.loads(out.getvalue()))
    def test_guard_gate_pass(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): rc = main(["guard", "gate", str(r), "--threshold", "0"])
            self.assertEqual(rc, 0); self.assertIn("PASS", out.getvalue())
    def test_guard_gate_fail(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): rc = main(["guard", "gate", str(r), "--threshold", "101"])
            self.assertEqual(rc, 1); self.assertIn("FAIL", out.getvalue())
    def test_guard_gate_json(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): rc = main(["guard", "gate", str(r), "--threshold", "0", "--json"])
            self.assertEqual(rc, 0); self.assertTrue(json.loads(out.getvalue())["passed"])
    def test_guard_parse_invalid_slug(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): rc = main(["guard", "parse", "INVALID", str(r)])
            self.assertEqual(rc, 2)
    def test_guard_check_invalid_slug(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): rc = main(["guard", "check", "INVALID", str(r)])
            self.assertEqual(rc, 2)
    def test_guard_parse_no_files(self):
        with TemporaryDirectory() as tmp:
            r = Path(tmp); out, err = StringIO(), StringIO()
            with redirect_stdout(out), redirect_stderr(err): rc = main(["guard", "parse", "test-feature", str(r)])
            self.assertEqual(rc, 1)
