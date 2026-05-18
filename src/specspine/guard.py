from __future__ import annotations
import hashlib, json, os, re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from .features import (
    FEATURE_FILE_PATHS, FeatureBundleNotFoundError, InvalidFeatureSlug,
    feature_bundle_paths, list_feature_bundles, parse_acceptance_criteria,
    parse_feature_tasks, validate_feature_slug,
)
KEYWORD_WEIGHT = {"class": 3, "function": 2, "method": 2, "import": 1, "return": 1, "error": 2, "handle": 2, "validate": 2, "check": 1, "create": 1, "update": 1, "delete": 1, "save": 1, "load": 1, "render": 2, "display": 1, "show": 1, "hide": 1, "toggle": 2, "enable": 1, "disable": 1, "configure": 1, "setup": 1, "init": 1, "start": 1, "stop": 1, "run": 1, "execute": 1, "process": 1, "compute": 1, "calculate": 1, "send": 1, "receive": 1, "fetch": 1, "store": 1, "cache": 2, "queue": 1, "schedule": 1, "notify": 2, "alert": 2, "log": 1, "track": 1, "monitor": 2, "report": 1, "export": 1, "parse": 1, "format": 1, "transform": 1, "convert": 1, "filter": 1, "search": 1, "find": 1, "sort": 1, "order": 1, "group": 1, "aggregate": 1, "auth": 3, "login": 3, "logout": 3, "permission": 3, "role": 2, "admin": 2, "user": 1, "session": 2, "token": 2, "password": 3, "encrypt": 3, "decrypt": 3, "hash": 2, "secure": 2, "protect": 2, "guard": 2, "shield": 2, "block": 1, "allow": 1, "deny": 1, "reject": 1, "accept": 1, "verify": 2, "confirm": 1, "approve": 1, "review": 1, "audit": 2, "compliance": 2, "policy": 2, "rule": 1, "constraint": 1, "limit": 1, "bound": 1, "max": 1, "min": 1, "threshold": 1, "timeout": 2, "retry": 2, "fallback": 2, "backup": 1, "restore": 1, "recover": 1, "migrate": 1, "deploy": 1, "release": 1, "version": 1, "upgrade": 1, "downgrade": 1, "rollback": 2, "feature": 1, "flag": 1, "switch": 1, "dark": 2, "theme": 2, "color": 1, "light": 1, "mode": 1, "layout": 1, "style": 1, "css": 2, "component": 1, "widget": 1, "element": 1, "node": 1, "tree": 1, "list": 1, "table": 1, "grid": 1, "form": 1, "input": 1, "button": 1, "click": 1, "hover": 1, "scroll": 1, "drag": 1, "drop": 1, "upload": 1, "download": 1, "file": 1, "path": 1, "directory": 1, "folder": 1, "name": 1, "title": 1, "description": 1, "summary": 1, "detail": 1, "page": 1, "screen": 1, "view": 1, "route": 1, "url": 1, "link": 1, "redirect": 1, "navigate": 1, "history": 1, "state": 1, "data": 1, "model": 1, "schema": 2, "field": 1, "column": 1, "row": 1, "record": 1, "entity": 1, "object": 1, "array": 1, "map": 1, "set": 1, "json": 1, "yaml": 1, "xml": 1, "csv": 1, "text": 1, "string": 1, "number": 1, "int": 1, "float": 1, "bool": 1, "date": 1, "time": 1, "duration": 1, "period": 1, "range": 1, "interval": 1, "zone": 1, "locale": 1, "language": 1, "translation": 1, "i18n": 2, "l10n": 2, "accessibility": 2, "a11y": 2, "responsive": 1, "mobile": 1, "desktop": 1, "browser": 1, "server": 1, "client": 1, "api": 2, "endpoint": 2, "request": 1, "response": 1, "header": 1, "body": 1, "payload": 1, "status": 1, "code": 1, "exception": 2, "warning": 1, "info": 1, "debug": 1, "trace": 1, "metric": 1, "counter": 1, "gauge": 1, "histogram": 1, "dashboard": 1, "chart": 1, "graph": 1, "plot": 1, "visualization": 1, "annotation": 1, "comment": 1, "note": 1, "tag": 1, "label": 1, "badge": 1, "icon": 1, "image": 1, "photo": 1, "video": 1, "audio": 1, "media": 1, "stream": 1, "buffer": 1, "pipe": 1, "channel": 1, "socket": 1, "connection": 1, "network": 1, "dns": 1, "http": 1, "https": 1, "tcp": 1, "udp": 1, "ssl": 2, "tls": 2, "cert": 2, "key": 1, "secret": 2, "env": 1, "config": 1, "setting": 1, "option": 1, "param": 1, "argument": 1, "control": 1, "manage": 1, "organize": 1, "arrange": 1, "structure": 1, "hierarchy": 1, "nest": 1, "wrap": 1, "embed": 1, "inline": 1, "flex": 1, "align": 1, "justify": 1, "center": 1, "margin": 1, "padding": 1, "border": 1, "shadow": 1, "opacity": 1, "visibility": 1, "animation": 2, "transition": 1, "motion": 1, "effect": 1, "blur": 1, "brightness": 1, "contrast": 1, "saturation": 1, "hue": 1}
STATUS_VERIFIED, STATUS_PARTIAL, STATUS_MISSING, STATUS_ORPHANED = "verified", "partial", "missing", "orphaned"
VERIFICATION_STATUSES = (STATUS_VERIFIED, STATUS_PARTIAL, STATUS_MISSING, STATUS_ORPHANED)
GUARD_CACHE_DIR = Path(".specspine") / "guard-cache"

@dataclass(frozen=True)
class GuardAcceptanceCriterion:
    id: str; text: str; expected_artifacts: list[str] = field(default_factory=list); source_file: str = ""; line: int = 0
    def as_dict(self) -> dict[str, object]: return {"expected_artifacts": list(self.expected_artifacts), "id": self.id, "line": self.line, "source_file": self.source_file, "text": self.text}

@dataclass(frozen=True)
class GuardTask:
    id: str; text: str; done: bool; files: list[str] = field(default_factory=list); source_file: str = ""; line: int = 0
    def as_dict(self) -> dict[str, object]: return {"done": self.done, "files": list(self.files), "id": self.id, "line": self.line, "source_file": self.source_file, "text": self.text}

@dataclass(frozen=True)
class SpecParseResult:
    feature_id: str; acceptance_criteria: tuple[GuardAcceptanceCriterion, ...]; tasks: tuple[GuardTask, ...]; status: str = ""; has_native_files: bool = False; missing_files: tuple[str, ...] = ()
    def as_dict(self) -> dict[str, object]: return {"acceptance_criteria": [ac.as_dict() for ac in self.acceptance_criteria], "feature_id": self.feature_id, "has_native_files": self.has_native_files, "missing_files": list(self.missing_files), "status": self.status, "tasks": [t.as_dict() for t in self.tasks]}

@dataclass(frozen=True)
class ConsistencyCheck:
    ac_id: str; ac_text: str; status: str; evidence: list[str] = field(default_factory=list); files: list[str] = field(default_factory=list)
    def as_dict(self) -> dict[str, object]: return {"ac_id": self.ac_id, "ac_text": self.ac_text, "evidence": list(self.evidence), "files": list(self.files), "status": self.status}

@dataclass(frozen=True)
class ConsistencyResult:
    feature_id: str; status: str; checks: tuple[ConsistencyCheck, ...]; score: int
    def as_dict(self) -> dict[str, object]: return {"checks": [c.as_dict() for c in self.checks], "feature_id": self.feature_id, "score": self.score, "status": self.status}

@dataclass(frozen=True)
class DriftEntry:
    ac_id: str; previous_status: str; current_status: str; changed_files: list[str] = field(default_factory=list)
    def as_dict(self) -> dict[str, object]: return {"ac_id": self.ac_id, "changed_files": list(self.changed_files), "current_status": self.current_status, "previous_status": self.previous_status}

@dataclass(frozen=True)
class DriftResult:
    feature_id: str; drift: tuple[DriftEntry, ...]; has_drift: bool
    def as_dict(self) -> dict[str, object]: return {"drift": [e.as_dict() for e in self.drift], "feature_id": self.feature_id, "has_drift": self.has_drift}

@dataclass(frozen=True)
class FeatureHealthEntry:
    slug: str; score: int; status: str; drift_count: int = 0; verified_count: int = 0; missing_count: int = 0; partial_count: int = 0; orphaned_count: int = 0
    def as_dict(self) -> dict[str, object]: return {"drift_count": self.drift_count, "missing_count": self.missing_count, "orphaned_count": self.orphaned_count, "partial_count": self.partial_count, "score": self.score, "slug": self.slug, "status": self.status, "verified_count": self.verified_count}

@dataclass(frozen=True)
class WorkspaceHealthResult:
    features: tuple[FeatureHealthEntry, ...]; workspace_score: int; total_features: int
    def as_dict(self) -> dict[str, object]: return {"features": [f.as_dict() for f in self.features], "total_features": self.total_features, "workspace_score": self.workspace_score}

def _extract_expected_artifacts(ac_text: str, execution_content: str | None) -> list[str]:
    if execution_content is None: return []
    return [f"keyword:{w}" for w in set(re.findall(r"[a-zA-Z]{3,}", ac_text.lower())) if w in KEYWORD_WEIGHT and re.search(rf"\b{re.escape(w)}\b", execution_content, re.IGNORECASE)]

def _extract_task_files(task_text: str, root: Path) -> list[str]:
    return [m.group(1) for m in re.finditer(r"([a-zA-Z0-9_.\-]+(?:/[a-zA-Z0-9_.\-]+)*\.(?:py|js|ts|tsx|jsx|go|rs|java|rb|md|yaml|yml|json|css|html))", task_text) if (root / m.group(1)).exists()]

def parse_feature_spec(slug: str, root: Path) -> SpecParseResult:
    fid = validate_feature_slug(slug); rr = root.expanduser().resolve(); paths = feature_bundle_paths(rr, fid)
    mf, contents = [], {}
    for k in FEATURE_FILE_PATHS:
        p = paths[k]
        if p.exists(): contents[k] = p.read_text(encoding="utf-8")
        else: mf.append(str(p.relative_to(rr)))
    hnf = bool(contents); spec = contents.get("spec", ""); exec_c = contents.get("execution", ""); status = ""
    for c in contents.values():
        for l in c.splitlines():
            s = l.strip()
            if s.startswith("Status:"): status = s.split(":", 1)[1].strip(); break
        if status: break
    acs = [GuardAcceptanceCriterion(id=a.id, text=a.text, expected_artifacts=_extract_expected_artifacts(a.text, exec_c or None), source_file=a.source_file, line=a.line) for a in (parse_acceptance_criteria(spec, source_file=f"specs/features/{fid}.md") if spec else [])]
    tasks = [GuardTask(id=t.id, text=t.text, done=t.done, files=_extract_task_files(t.text, rr), source_file=t.source_file, line=t.line) for t in (parse_feature_tasks(exec_c, source_file=f"execution/features/{fid}.md") if exec_c else [])]
    return SpecParseResult(feature_id=fid, acceptance_criteria=tuple(acs), tasks=tuple(tasks), status=status, has_native_files=hnf, missing_files=tuple(mf))

def _collect_implementation_files(root: Path) -> list[Path]:
    sd, se, files = {".git", ".specspine", "__pycache__", "node_modules", ".venv", "venv"}, {".pyc", ".pyo", ".pyd", ".so", ".dylib", ".dll", ".exe"}, []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in sd]; p = Path(dp)
        try: rel = str(p.relative_to(root))
        except: continue
        if rel == "." or rel.split(os.sep)[0] in {"src", "lib", "app", "pkg"} or rel.startswith("src"):
            for fn in fns:
                if Path(fn).suffix not in se: files.append(p / fn)
    return files

def _score_ac_evidence(ac_text: str, fc: str) -> int:
    aw = re.findall(r"[a-zA-Z]{3,}", ac_text.lower())
    if not aw: return 0
    fl, ts, mp = fc.lower(), 0, 0
    for w in aw:
        wt = KEYWORD_WEIGHT.get(w, 1); mp += wt
        if re.search(rf"\b{re.escape(w)}\b", fl): ts += wt
    return int((ts / mp) * 100) if mp else 0

def _classify_ac(ac_id: str, ac_text: str, impl_files: list[Path], td: bool) -> ConsistencyCheck:
    ev, fs, bs = [], [], 0
    for fp in impl_files:
        try: c = fp.read_text(encoding="utf-8", errors="ignore")
        except: continue
        s = _score_ac_evidence(ac_text, c)
        if s > 0:
            r = str(fp); fs.append(r)
            ev.append(f"{r}: {'strong' if s >= 50 else 'weak'} match (score={s})")
            if s > bs: bs = s
    st = STATUS_VERIFIED if bs >= 60 else STATUS_PARTIAL if bs >= 20 or td else STATUS_MISSING
    if td and bs < 20: ev.append("task marked done but no strong code evidence")
    return ConsistencyCheck(ac_id=ac_id, ac_text=ac_text, status=st, evidence=ev, files=fs)

def check_spec_consistency(slug: str, root: Path) -> ConsistencyResult:
    fid = validate_feature_slug(slug); rr = root.expanduser().resolve()
    try: spec = parse_feature_spec(fid, rr)
    except InvalidFeatureSlug: return ConsistencyResult(feature_id=fid, status="error", checks=(), score=0)
    if not spec.has_native_files: return ConsistencyResult(feature_id=fid, status="missing", checks=(), score=0)
    impl = _collect_implementation_files(rr); td = any(t.done for t in spec.tasks)
    checks = [_classify_ac(ac.id, ac.text, impl, td) for ac in spec.acceptance_criteria]
    v = sum(1 for c in checks if c.status == STATUS_VERIFIED); p = sum(1 for c in checks if c.status == STATUS_PARTIAL); t = len(checks)
    if t == 0: sc, st = 0, "no_acceptance_criteria"
    else:
        sc = int((v * 100 + p * 50) / t)
        st = "all_verified" if v == t else "partially_verified" if v > 0 else "partial_evidence" if p > 0 else "no_evidence"
    return ConsistencyResult(feature_id=fid, status=st, checks=tuple(checks), score=sc)

def _cache_path(cd: Path, s: str) -> Path: return cd / f"{s}.json"
def _load_cache(cd: Path, s: str) -> dict[str, Any] | None:
    p = _cache_path(cd, s)
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except: return None
    return None
def _save_cache(cd: Path, s: str, d: dict[str, Any]) -> None:
    cd.mkdir(parents=True, exist_ok=True); _cache_path(cd, s).write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def _compute_file_hashes(root: Path) -> dict[str, str]:
    h, sd = {}, {".git", ".specspine", "__pycache__", "node_modules", ".venv", "venv"}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in sd]
        for fn in sorted(fns):
            fp = Path(dp) / fn
            try: h[str(fp.relative_to(root))] = hashlib.sha256(fp.read_bytes()).hexdigest()[:16]
            except: continue
    return h

def detect_drift(slug: str, root: Path, cache_dir: Path | None = None) -> DriftResult:
    fid = validate_feature_slug(slug); rr = root.expanduser().resolve()
    if cache_dir is None: cache_dir = rr / GUARD_CACHE_DIR
    cur = check_spec_consistency(fid, rr); cached = _load_cache(cache_dir, fid)
    if cached is None:
        _save_cache(cache_dir, fid, {"feature_id": fid, "score": cur.score, "status": cur.status, "checks": [c.as_dict() for c in cur.checks], "file_hashes": _compute_file_hashes(rr)})
        return DriftResult(feature_id=fid, drift=(), has_drift=False)
    pc, cc = {c["ac_id"]: c for c in cached.get("checks", [])}, {c.ac_id: c for c in cur.checks}
    ph, ch, de = cached.get("file_hashes", {}), _compute_file_hashes(rr), []
    cf = [f for f in set(list(ph.keys()) + list(ch.keys())) if ph.get(f) != ch.get(f)]
    for aid in sorted(set(list(pc.keys()) + list(cc.keys()))):
        pv, cu = pc.get(aid), cc.get(aid); ps = pv["status"] if pv else "unknown"; cs = cu.status if cu else "unknown"
        if ps != cs:
            af = (cu.files if cu else pv.get("files", [])) if cu or pv else []
            de.append(DriftEntry(ac_id=aid, previous_status=ps, current_status=cs, changed_files=[f for f in cf if f in af] or cf[:5]))
    _save_cache(cache_dir, fid, {"feature_id": fid, "score": cur.score, "status": cur.status, "checks": [c.as_dict() for c in cur.checks], "file_hashes": ch})
    return DriftResult(feature_id=fid, drift=tuple(de), has_drift=bool(de))

def _detect_drift_for_feature(feat: dict[str, object], root: Path, cd: Path) -> FeatureHealthEntry:
    slug = str(feat["slug"])
    try: con = check_spec_consistency(slug, root)
    except: return FeatureHealthEntry(slug=slug, score=0, status="error")
    try: dri = detect_drift(slug, root, cd)
    except: dri = DriftResult(feature_id=slug, drift=(), has_drift=False)
    st = con.status; 
    if dri.has_drift: st = "drift_detected"
    return FeatureHealthEntry(slug=slug, score=con.score, status=st, drift_count=len(dri.drift), verified_count=sum(1 for c in con.checks if c.status == STATUS_VERIFIED), missing_count=sum(1 for c in con.checks if c.status == STATUS_MISSING), partial_count=sum(1 for c in con.checks if c.status == STATUS_PARTIAL))

def compute_workspace_health(root: Path) -> WorkspaceHealthResult:
    rr, cd = root.expanduser().resolve(), root.expanduser().resolve() / GUARD_CACHE_DIR
    feats = list_feature_bundles(rr); entries = [_detect_drift_for_feature(f, rr, cd) for f in feats]
    if not entries: return WorkspaceHealthResult(features=(), workspace_score=100, total_features=0)
    return WorkspaceHealthResult(features=tuple(entries), workspace_score=int(sum(e.score for e in entries) / len(entries)), total_features=len(entries))

def render_guard_json(r: SpecParseResult) -> str: return json.dumps(r.as_dict(), indent=2, sort_keys=True) + "\n"
def render_guard_text(r: SpecParseResult) -> str:
    ls = [f"Spec parse: {r.feature_id}", f"Status: {r.status or 'unknown'}", f"Has native files: {'yes' if r.has_native_files else 'no'}", "", f"Acceptance Criteria ({len(r.acceptance_criteria)}):"]
    if r.acceptance_criteria:
        for a in r.acceptance_criteria: ls.extend([f"- {a.id}: {a.text}", f"    expected artifacts: {', '.join(a.expected_artifacts) or 'none'}"])
    else: ls.append("- None.")
    ls.extend(["", f"Tasks ({len(r.tasks)}):"])
    if r.tasks:
        for t in r.tasks: ls.extend([f"- [{'x' if t.done else ' '}] {t.id}: {t.text}", f"    files: {', '.join(t.files) or 'none'}"])
    else: ls.append("- None.")
    if r.missing_files: ls.extend(["", "Missing files:"] + [f"- {f}" for f in r.missing_files])
    return "\n".join(ls) + "\n"

def render_check_json(r: ConsistencyResult) -> str: return json.dumps(r.as_dict(), indent=2, sort_keys=True) + "\n"
def render_check_text(r: ConsistencyResult) -> str:
    ls = [f"Consistency check: {r.feature_id}", f"Status: {r.status}", f"Score: {r.score}/100", "", f"Checks ({len(r.checks)}):"]
    if r.checks:
        for c in r.checks:
            m = {"verified": "ok", "partial": "~", "missing": "!", "orphaned": "?"}.get(c.status, "?")
            ls.extend([f"- [{m}] {c.ac_id}: {c.status}", f"    {c.ac_text}"] + [f"    evidence: {e}" for e in c.evidence] + ([f"    files: {', '.join(c.files)}"] if c.files else []))
    else: ls.append("- None.")
    return "\n".join(ls) + "\n"

def render_drift_json(r: DriftResult) -> str: return json.dumps(r.as_dict(), indent=2, sort_keys=True) + "\n"
def render_drift_text(r: DriftResult) -> str:
    ls = [f"Drift detection: {r.feature_id}", f"Has drift: {'yes' if r.has_drift else 'no'}", "", f"Drift entries ({len(r.drift)}):"]
    if r.drift:
        for e in r.drift:
            ls.append(f"- {e.ac_id}: {e.previous_status} -> {e.current_status}")
            if e.changed_files: ls.append(f"    changed: {', '.join(e.changed_files)}")
    else: ls.append("- None.")
    return "\n".join(ls) + "\n"

def render_score_json(r: WorkspaceHealthResult) -> str: return json.dumps(r.as_dict(), indent=2, sort_keys=True) + "\n"
def render_score_text(r: WorkspaceHealthResult) -> str:
    ls = [f"Workspace health: {r.workspace_score}/100", f"Total features: {r.total_features}", "", "Features:"]
    if r.features: ls += [f"- {f.slug}: score={f.score} status={f.status} verified={f.verified_count} partial={f.partial_count} missing={f.missing_count} drift={f.drift_count}" for f in r.features]
    else: ls.append("- None.")
    return "\n".join(ls) + "\n"
