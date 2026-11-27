import sys
import os, re, ast, json, time, zipfile, shutil, subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "brain_db.json")
WS_ROOT = os.path.join(BASE_DIR, "_workspaces")
os.makedirs(WS_ROOT, exist_ok=True)
DEFAULT_DB = {"working": [], "episodic": [], "semantic": [], "procedural": [], "project": []}
PRO_MODELS = ("gemini-3.1-pro-preview", "gemini-2.5-pro", "gemini-3.6-flash", "gemini-3-flash-preview", "gemini-3.5-flash-lite")

def load_db():
    try:
        if os.path.exists(DB_PATH):
            d = json.load(open(DB_PATH, encoding="utf-8"))
            for k in DEFAULT_DB: d.setdefault(k, [])
            return d
    except Exception: pass
    return {k: [] for k in DEFAULT_DB}

def save_db(db):
    try:
        for k in DEFAULT_DB: db[k] = db.get(k, [])[-50:]
        json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except Exception: pass

def retrieve_memories(query, k=5):
    db = load_db()
    words = set(re.findall(r'[a-zA-ZÀ-ỹ0-9_]{2,}', (query or "").lower()))
    if not words: return ""
    scored = []
    for mtype in ("procedural", "episodic", "project", "semantic"):
        for item in db.get(mtype, []):
            txt = (item.get("title", "") + " " + item.get("body", "")).lower()
            hit = sum(1 for w in words if w in txt)
            if hit > 0:
                scored.append((hit + (2 if mtype == "procedural" else 0), mtype.upper(), item))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored: return ""
    lines = ["[KỸ NĂNG & KINH NGHIỆM ĐÃ KIỂM CHỨNG]"]
    for _, mt, it in scored[:k]:
        lines.append(f"- ({mt}) {it.get('title','')}: {it.get('body','')[:300]}")
    return "\n".join(lines)

def add_memory(mtype, title, body):
    db = load_db()
    arr = db.setdefault(mtype, [])
    tc, bc = (title or "").strip()[:120], (body or "").strip()[:800]
    if not tc or not bc: return ""
    arr = [x for x in arr if x.get("title") != tc]
    arr.append({"title": tc, "body": bc, "ts": int(time.time())})
    db[mtype] = arr[-50:]
    save_db(db)
    return tc

def classify_role(msg, has_media=False):
    m = (msg or "").lower()
    if re.search(r'(code|python|html|js|ts|css|api|flask|sql|bug|lỗi|sửa lỗi|lập trình|script|app|web|tool|phần mềm|ứng dụng|chương trình|dự án|kotlin|java|c\+\+)', m):
        return "coding", "AI Architect + Programmer + Debugger", 0.2
    if re.search(r'(kiến trúc|hệ thống|thiết kế|mô hình|kế hoạch|tối ưu|bảo mật|security|database)', m):
        return "architect", "System Architect & Security", 0.25
    if re.search(r'(tự học|nghiên cứu|tìm hiểu|so sánh|phân tích|tài liệu|nguyên lý|khoa học|skill|kỹ năng)', m) or has_media:
        return "research", "AI Researcher & Self-Learning", 0.3
    return "general", "Trợ lý AI chuyên sâu", 0.35

def is_project_build(msg):
    m = (msg or "").lower()
    return bool(re.search(r'(xây dựng|tạo ứng dụng|viết ứng dụng|viết app|tạo app|làm app|tạo web|làm web|tạo tool|viết phần mềm|viết chương trình|dự án|quản lý bán hàng|quản lý)', m))

def is_research_learn(msg):
    m = (msg or "").lower()
    return bool(re.search(r'(tự học|học kỹ năng|tạo skill|nâng cấp skill|cải tiến skill|viết skill|nghiên cứu|tìm hiểu công nghệ|cập nhật kiến thức)', m))

def verify_python_blocks(text):
    blocks = re.findall(r'```python\s*(.*?)```', text or "", re.DOTALL | re.IGNORECASE)
    if not blocks: return True, ""
    errs = []
    for idx, blk in enumerate(blocks, 1):
        try: ast.parse(blk)
        except SyntaxError as e: errs.append(f"Block #{idx} dòng {e.lineno}: {e.msg}")
    return (len(errs) == 0), "; ".join(errs)

def call_gemini_once(session, key, sys_p, prompt, temp=0.2, mdl_list=PRO_MODELS, use_search=False):
    base_body = {
        "systemInstruction": {"parts": [{"text": sys_p}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 8192, "temperature": temp}
    }
    last_err = ""
    for mdl in mdl_list:
        for try_search in ([True, False] if use_search else [False]):
            body = dict(base_body)
            if try_search: body["tools"] = [{"google_search": {}}]
            try:
                r = session.post(f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent", headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=body, timeout=(8, 60))
                if r.status_code == 200:
                    parts = (((r.json().get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
                    txt = "".join(p.get("text", "") for p in parts if not p.get("thought"))
                    if txt.strip(): return txt.strip(), mdl
                else:
                    last_err = f"{mdl} HTTP {r.status_code}: {r.text[:140]}"
                    if r.status_code in (401, 403): return "", last_err
                    if r.status_code == 400 and try_search: continue
                    break
            except Exception as e:
                last_err = f"{mdl}: {e}"
                break
    return "", last_err or "Không gọi được model"

def parse_project_files(text):
    files = {}
    for m in re.finditer(r'===FILE:\s*([^\n=]+?)===\s*\n(.*?)===END_FILE===', text or "", re.DOTALL):
        rel = m.group(1).strip().replace("\\", "/").lstrip("/")
        if not rel or ".." in rel or rel.startswith("/"): continue
        files[rel] = m.group(2).rstrip() + "\n"
    return files

def security_scan(files):
    warns = []
    for fn, content in files.items():
        if re.search(r'AIza[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z]{20,}', content): warns.append(f"{fn}: Nguy cơ lộ API key cứng")
        if re.search(r'shell\s*=\s*True|\beval\s*\(|\bexec\s*\(', content): warns.append(f"{fn}: Dùng lệnh rủi ro (shell=True/eval/exec)")
    return warns

def clean_old_ws():
    now = time.time()
    for n in os.listdir(WS_ROOT):
        p = os.path.join(WS_ROOT, n)
        try:
            if now - os.path.getmtime(p) > 7200:
                shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.remove(p)
        except Exception: pass

def run_workspace_tests(files):
    clean_old_ws()
    pid = f"p_{int(time.time())}"
    ws = os.path.join(WS_ROOT, pid)
    os.makedirs(ws, exist_ok=True)
    for rel, body in files.items():
        fp = os.path.join(ws, rel)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "w", encoding="utf-8").write(body)
    safe_env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1"}
    for pf in [os.path.join(ws, r) for r in files if r.endswith(".py")]:
        try: ast.parse(open(pf, encoding="utf-8").read())
        except SyntaxError as e: return pid, False, f"Lỗi cú pháp {os.path.relpath(pf, ws)} dòng {e.lineno}: {e.msg}"
    tt = "test_app.py" if "test_app.py" in files else next((r for r in files if "test" in r and r.endswith(".py")), "")
    if tt:
        try:
            res = subprocess.run(["python3", tt], cwd=ws, env=safe_env, capture_output=True, text=True, timeout=12)
            out = (res.stdout + "\n" + res.stderr).strip()
            if res.returncode != 0: return pid, False, f"Test lỗi (exit {res.returncode}):\n{out[-1200:]}"
            return pid, True, out[-600:] or "ĐẠT toàn bộ kiểm thử!"
        except subprocess.TimeoutExpired: return pid, False, "Lỗi: Test quá 12 giây (treo vòng lặp)."
        except Exception as e: return pid, False, str(e)
    return pid, True, "Kiểm tra cú pháp Python đạt 100%."

def zip_workspace(pid):
    ws = os.path.join(WS_ROOT, pid)
    if not os.path.isdir(ws): return ""
    zp = os.path.join(WS_ROOT, f"{pid}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, fns in os.walk(ws):
            for fn in fns:
                fp = os.path.join(root, fn)
                zf.write(fp, os.path.relpath(fp, ws))
    return zp

def extract_and_save_skill(session, key, msg, final_ans, force=False):
    rule = "Hãy tóm tắt thành 1 JSON Skill có giá trị thực tế." if force else 'Nếu không phải xã giao và có giá trị kỹ thuật/lập trình, tóm tắt thành 1 JSON; nếu xã giao trả lời: SKIP'
    sk_p = f"Câu hỏi: '{msg[:180]}'\nKết quả đã kiểm chứng:\n{final_ans[:1400]}\n\n{rule}\nĐịnh dạng 1 dòng JSON duy nhất: {{\"type\":\"procedural\",\"title\":\"tên kỹ năng ngắn\",\"body\":\"nguyên lý & các bước chuẩn tối đa 300 ký tự\"}}"
    sk, _ = call_gemini_once(session, key, "Trích xuất Skill kỹ thuật súc tích dạng JSON.", sk_p, temp=0.1, mdl_list=("gemini-3.5-flash-lite", "gemini-3.6-flash"))
    if sk and "SKIP" not in sk:
        m = re.search(r'\{.*\}', sk, re.DOTALL)
        if m:
            try:
                o = json.loads(m.group(0))
                mt = o.get("type", "procedural")
                if mt not in DEFAULT_DB: mt = "procedural"
                return add_memory(mt, o.get("title", ""), o.get("body", ""))
            except Exception: pass
    return ""

def run_research_pipeline(session, key, msg):
    mem_ctx = retrieve_memories(msg, k=4)
    res_p = f"Yêu cầu nghiên cứu & tự học kỹ năng:\n{msg}\n{mem_ctx}\nHãy tìm kiếm thông tin kỹ thuật mới nhất, phân tích bản chất, đưa ra quy trình thực hành chuẩn và ví dụ code (nếu liên quan lập trình)."
    study, mdl = call_gemini_once(session, key, "Bạn là AI Researcher chuyên sâu, sử dụng nguồn tin thực tế, kiểm chứng chéo trước khi kết luận.", res_p, temp=0.25, use_search=True)
    if not study: return f"⚠️ Không gọi được AI Researcher ({mdl})", False
    ok_py, py_err = verify_python_blocks(study)
    if not ok_py:
        fix, _ = call_gemini_once(session, key, "Sửa lỗi code Python.", f"Sửa lỗi {py_err} trong bài sau:\n{study}", temp=0.15)
        if fix: study = fix
    saved = extract_and_save_skill(session, key, msg, study, force=True)
    head = f"🔬 **AI Researcher ({mdl})**"
    tail = f"\n\n📚 **Đã tự học & lưu Skill mới:** `{saved}`" if saved else ""
    return f"{head}\n\n{study}{tail}", True

def run_programmer_pipeline(session, key, msg, base_sys):
    mem_ctx = retrieve_memories(msg, k=5)
    plan, mdl = call_gemini_once(session, key, "Bạn là AI Architect chuyên nghiệp.", f"Yêu cầu: {msg}\n{mem_ctx}\nThiết kế ngắn gọn: (1) Kiến trúc & công nghệ, (2) Danh sách file, (3) Ca test trong test_app.py.", temp=0.2, use_search=True)
    if not plan: return f"⚠️ Lỗi Architect ({mdl})", "", []
    prog_sys = f"{base_sys}\nBạn là AI Programmer cấp chuyên gia. Xuất toàn bộ code theo định dạng:\n===FILE: duong_dan/ten_file===\nnội dung\n===END_FILE===\nBắt buộc có README.md và test_app.py (tự thoát sau khi test)."
    code_out, mdl2 = call_gemini_once(session, key, prog_sys, f"YÊU CẦU:\n{msg}\n\nTHIẾT KẾ:\n{plan}", temp=0.2)
    files = parse_project_files(code_out)
    if not files: return (code_out or f"⚠️ Lỗi Programmer ({mdl2})"), "", []
    pid, ok_test, test_log = run_workspace_tests(files)
    rounds = 0
    while not ok_test and rounds < 2:
        rounds += 1
        dbg_p = f"Lỗi khi chạy test thật:\n{test_log}\n\nFILES:\n" + "\n".join(f"===FILE: {k}===\n{v}===END_FILE===" for k, v in files.items()) + "\nSửa dứt điểm lỗi theo format ===FILE: ...=== ... ===END_FILE===."
        fix_out, _ = call_gemini_once(session, key, "Bạn là AI Debugger, sửa đúng lỗi từ Traceback thật.", dbg_p, temp=0.15)
        fixed = parse_project_files(fix_out)
        if fixed: files.update(fixed); pid, ok_test, test_log = run_workspace_tests(files)
        else: break
    warns = security_scan(files)
    saved = ""
    if ok_test:
        zip_workspace(pid)
        add_memory("project", f"Dự án: {msg[:60]}", f"Files: {', '.join(list(files.keys())[:8])}. Test PASS.")
        saved = extract_and_save_skill(session, key, msg, plan + "\n" + test_log, force=True)
    out = [f"⚙️ **Model sử dụng:** `{mdl2}`", f"📐 **Kiến trúc:**\n{plan}", f"📁 **File đã tạo ({len(files)}):** " + ", ".join(f"`{k}`" for k in files), f"🧪 **Kiểm thử thật ({rounds} lần tự sửa):** {'✅ ĐẠT' if ok_test else '⚠️ CÒN LỖI'}\n```text\n{test_log}\n```"]
    out.append("🛡️ **AI Security:** " + (", ".join(warns) if warns else "An toàn, không lộ key/hàm rủi ro."))
    if saved: out.append(f"📚 **Đã tự học Skill mới:** `{saved}`")
    return "\n\n".join(out), (pid if ok_test else ""), list(files.keys())

def run_verified_pipeline(session, key, msg, base_sys, role_name, temp):
    import self_upgrader as _su
    if _su.is_self_upgrade(msg):
        ans, uid, ok = _su.prepare_self_upgrade(session, key, msg, sys.modules[__name__])
        return ans, ok, ""
    if is_project_build(msg):
        ans, pid, _ = run_programmer_pipeline(session, key, msg, base_sys)
        if pid: ans += f"\n\n📦 **[Tải toàn bộ dự án .zip tại đây](/api/download-project/{pid})**"
        return ans, True, ""
    if is_research_learn(msg):
        import skill_creator as _sc
        ans, pid, ok = _sc.create_or_evolve_skill(session, key, msg, sys.modules[__name__])
        return ans, ok, ""
    mem_ctx = retrieve_memories(msg, k=5)
    spec_sys = f"{base_sys}\n[VAI TRÒ]: {role_name}.\n{mem_ctx}\nPhân tích sâu, giải pháp/code chạy được ngay."
    draft, mdl = call_gemini_once(session, key, spec_sys, msg, temp=temp, use_search=True)
    if not draft: return f"⚠️ Không gọi được AI ({mdl})", False, ""
    ok_py, py_err = verify_python_blocks(draft)
    rev_p = f"YÊU CẦU:\n{msg}\n\nBẢN NHÁP:\n{draft}\n\nKIỂM TRA PYTHON: {'Đạt' if ok_py else py_err}\nNếu đạt trả lời đúng chữ: VERIFIED_OK. Nếu có lỗi viết lại bản hoàn chỉnh."
    rev, _ = call_gemini_once(session, key, "Bạn là AI Reviewer độc lập.", rev_p, temp=0.15)
    final_ans = draft if (not rev or "VERIFIED_OK" in rev) else rev
    ok_final, _ = verify_python_blocks(final_ans)
    saved = extract_and_save_skill(session, key, msg, final_ans, force=False) if ok_final and len(final_ans) > 100 else ""
    if saved: final_ans += f"\n\n📚 **Đã tự học Skill mới:** `{saved}`"
    return f"🧠 **{role_name} ({mdl})**\n\n{final_ans}", ok_final, py_err
