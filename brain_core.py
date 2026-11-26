import os, re, ast, json, time, zipfile, shutil, subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "brain_db.json")
WS_ROOT = os.path.join(BASE_DIR, "_workspaces")
os.makedirs(WS_ROOT, exist_ok=True)
DEFAULT_DB = {"working": [], "episodic": [], "semantic": [], "procedural": [], "project": []}

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
        for k in DEFAULT_DB: db[k] = db.get(k, [])[-40:]
        json.dump(db, open(DB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except Exception: pass

def retrieve_memories(query, k=4):
    db = load_db()
    words = set(re.findall(r'[a-zA-ZÀ-ỹ0-9_]{2,}', (query or "").lower()))
    if not words: return ""
    scored = []
    for mtype in ("procedural", "episodic", "project", "semantic"):
        for item in db.get(mtype, []):
            txt = (item.get("title", "") + " " + item.get("body", "")).lower()
            hit = sum(1 for w in words if w in txt)
            if hit > 0:
                scored.append((hit + (1 if mtype in ("procedural", "episodic") else 0), mtype.upper(), item))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored: return ""
    lines = ["[KINH NGHIỆM & KỸ NĂNG ĐÃ KIỂM CHỨNG]"]
    for _, mt, it in scored[:k]:
        lines.append(f"- ({mt}) {it.get('title','')}: {it.get('body','')[:260]}")
    return "\n".join(lines)

def add_memory(mtype, title, body):
    db = load_db()
    arr = db.setdefault(mtype, [])
    tc, bc = (title or "").strip()[:100], (body or "").strip()[:700]
    if not tc or not bc: return
    arr = [x for x in arr if x.get("title") != tc]
    arr.append({"title": tc, "body": bc, "ts": int(time.time())})
    db[mtype] = arr[-40:]
    save_db(db)

def classify_role(msg, has_media=False):
    m = (msg or "").lower()
    if re.search(r'(code|python|html|js|css|api|flask|sql|bug|lỗi|sửa lỗi|lập trình|script|app|web|tool|phần mềm|ứng dụng|chương trình|dự án)', m):
        return "coding", "AI Architect + Programmer + Tester", 0.2
    if re.search(r'(kiến trúc|hệ thống|thiết kế|mô hình|kế hoạch|tối ưu|bảo mật|security|database)', m):
        return "architect", "System Architect & Security Reviewer", 0.25
    if re.search(r'(nghiên cứu|tìm hiểu|so sánh|phân tích|tài liệu|nguyên lý|khoa học|toán|vật lý|điện)', m) or has_media:
        return "research", "Researcher & Technical Analyst", 0.3
    return "general", "Trợ lý AI chuyên sâu", 0.4

def is_project_build(msg):
    m = (msg or "").lower()
    return bool(re.search(r'(xây dựng|tạo ứng dụng|viết ứng dụng|viết app|tạo app|làm app|tạo web|làm web|tạo tool|viết phần mềm|viết chương trình|dự án|quản lý bán hàng|quản lý)', m))

def verify_python_blocks(text):
    blocks = re.findall(r'```python\s*(.*?)```', text or "", re.DOTALL | re.IGNORECASE)
    if not blocks: return True, ""
    errs = []
    for idx, blk in enumerate(blocks, 1):
        try: ast.parse(blk)
        except SyntaxError as e: errs.append(f"Block #{idx} dòng {e.lineno}: {e.msg}")
    return (len(errs) == 0), "; ".join(errs)

def call_gemini_once(session, key, sys_p, prompt, temp=0.2, mdl_list=("gemini-3.5-flash-lite", "gemini-3.6-flash")):
    body = {
        "systemInstruction": {"parts": [{"text": sys_p}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 8192, "temperature": temp}
    }
    for mdl in mdl_list:
        try:
            r = session.post(f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent", headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=body, timeout=(8, 60))
            if r.status_code != 200: continue
            parts = (((r.json().get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
            txt = "".join(p.get("text", "") for p in parts if not p.get("thought"))
            if txt.strip(): return txt.strip()
        except Exception: pass
    return ""

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
        if re.search(r'AIza[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z]{20,}', content):
            warns.append(f"{fn}: Có dấu hiệu lộ API key cứng trong code")
        if re.search(r'shell\s*=\s*True|\beval\s*\(|\bexec\s*\(', content):
            warns.append(f"{fn}: Dùng hàm thực thi rủi ro (shell=True/eval/exec)")
    return warns

def clean_old_ws():
    now = time.time()
    for n in os.listdir(WS_ROOT):
        p = os.path.join(WS_ROOT, n)
        try:
            if now - os.path.getmtime(p) > 7200:
                if os.path.isdir(p): shutil.rmtree(p, ignore_errors=True)
                else: os.remove(p)
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
    py_files = [os.path.join(ws, r) for r in files if r.endswith(".py")]
    for pf in py_files:
        try:
            ast.parse(open(pf, encoding="utf-8").read())
        except SyntaxError as e:
            return pid, False, f"Lỗi cú pháp tại {os.path.relpath(pf, ws)} dòng {e.lineno}: {e.msg}"

    test_target = "test_app.py" if "test_app.py" in files else next((r for r in files if "test" in r and r.endswith(".py")), "")
    if test_target:
        try:
            res = subprocess.run(["python3", test_target], cwd=ws, env=safe_env, capture_output=True, text=True, timeout=12)
            out = (res.stdout + "\n" + res.stderr).strip()
            if res.returncode != 0:
                return pid, False, f"Test thất bại (exit {res.returncode}):\n{out[-1200:]}"
            return pid, True, out[-600:] or "Tất cả kiểm thử đều ĐẠT!"
        except subprocess.TimeoutExpired:
            return pid, False, "Lỗi: Chương trình chạy quá 12 giây (treo vòng lặp hoặc mở server chưa thoát trong test)."
        except Exception as e:
            return pid, False, str(e)
    return pid, True, "Đã kiểm tra cú pháp toàn bộ file Python thành công."

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

def run_programmer_pipeline(session, key, msg, base_sys):
    mem_ctx = retrieve_memories(msg, k=4)
    arch_p = f"Yêu cầu: {msg}\n{mem_ctx}\nHãy thiết kế ngắn gọn: (1) Kiến trúc & công nghệ phù hợp, (2) Danh sách file cần tạo, (3) Các ca kiểm thử bắt buộc trong test_app.py."
    plan = call_gemini_once(session, key, "Bạn là AI Architect chuyên nghiệp.", arch_p, temp=0.2)
    if not plan: return "", "", []

    prog_sys = (
        f"{base_sys}\nBạn là AI Programmer cấp chuyên gia. Hãy xuất TOÀN BỘ mã nguồn dự án hoàn chỉnh theo đúng định dạng bắt buộc:\n"
        "===FILE: duong_dan/ten_file===\nnội dung code\n===END_FILE===\n"
        "LUẬT BẮT BUỘC:\n"
        "- Luôn tạo file `README.md` (hướng dẫn chạy) và `test_app.py` (dùng unittest/assert tự động test toàn bộ chức năng chính, tự thoát sau khi test xong, không treo vòng lặp vô hạn).\n"
        "- Code sạch, không hardcode API key, xử lý lỗi đầy đủ."
    )
    code_out = call_gemini_once(session, key, prog_sys, f"YÊU CẦU:\n{msg}\n\nBẢN THIẾT KẾ:\n{plan}", temp=0.2)
    files = parse_project_files(code_out)
    if not files:
        return code_out, "", []

    pid, ok_test, test_log = run_workspace_tests(files)
    rounds = 0
    while not ok_test and rounds < 2:
        rounds += 1
        dbg_p = (
            f"Dự án bị lỗi khi chạy kiểm thử thật:\n{test_log}\n\n"
            "CÁC FILE HIỆN TẠI:\n" + "\n".join(f"===FILE: {k}===\n{v}===END_FILE===" for k, v in files.items()) +
            "\n\nHãy sửa triệt để nguyên nhân lỗi và xuất lại CÁC FILE BỊ LỖI theo đúng định dạng ===FILE: ...=== ... ===END_FILE===."
        )
        fix_out = call_gemini_once(session, key, "Bạn là AI Debugger, chỉ sửa đúng nguyên nhân gốc từ Traceback thật.", dbg_p, temp=0.15)
        fixed = parse_project_files(fix_out)
        if fixed:
            files.update(fixed)
            pid, ok_test, test_log = run_workspace_tests(files)
        else:
            break

    sec_warns = security_scan(files)
    if ok_test:
        zip_workspace(pid)
        add_memory("project", f"Dự án: {msg[:60]}", f"Files: {', '.join(list(files.keys())[:8])}. Test PASS.")

    summary = [
        f"📐 **Kiến trúc & Kế hoạch:**\n{plan}\n",
        f"📁 **Các file đã tạo ({len(files)} file):** " + ", ".join(f"`{k}`" for k in files.keys()),
        f"🧪 **Kết quả chạy kiểm thử thật ({rounds} lần tự sửa):** {'✅ ĐẠT' if ok_test else '⚠️ CÒN LỖI'}\n```text\n{test_log}\n```"
    ]
    if sec_warns:
        summary.append("🛡️ **Cảnh báo bảo mật (`AI Security`):**\n" + "\n".join(f"- {w}" for w in sec_warns))
    else:
        summary.append("🛡️ **AI Security:** Không phát hiện lộ key cứng hay hàm thực thi nguy hiểm.")
    return "\n\n".join(summary), (pid if ok_test else ""), list(files.keys())

def run_verified_pipeline(session, key, msg, base_sys, role_name, temp):
    if is_project_build(msg):
        ans, pid, flist = run_programmer_pipeline(session, key, msg, base_sys)
        if ans:
            if pid:
                ans += f"\n\n📦 **[Tải toàn bộ dự án .zip tại đây](/api/download-project/{pid})**"
            return ans, True, ""

    mem_ctx = retrieve_memories(msg, k=4)
    spec_sys = f"{base_sys}\n[VAI TRÒ CHUYÊN GIA]: {role_name}.\n{mem_ctx}\nYêu cầu: Phân tích logic từng bước, code/giải pháp phải chạy được ngay."
    draft = call_gemini_once(session, key, spec_sys, msg, temp=temp)
    if not draft: return "", False, ""
    ok_py, py_err = verify_python_blocks(draft)
    rev_p = f"YÊU CẦU:\n{msg}\n\nBẢN NHÁP:\n{draft}\n\nKIỂM TRA PYTHON: {'Đạt' if ok_py else py_err}\nNếu đạt trả lời đúng chữ: VERIFIED_OK. Nếu có lỗi viết lại bản hoàn chỉnh."
    rev = call_gemini_once(session, key, "Bạn là AI Reviewer độc lập.", rev_p, temp=0.15)
    final_ans = draft if (not rev or "VERIFIED_OK" in rev) else rev
    ok_final, _ = verify_python_blocks(final_ans)
    if ok_final and len(final_ans) > 120:
        sk = call_gemini_once(session, key, "Trích xuất kỹ năng JSON.", f"Từ câu hỏi '{msg[:160]}' và lời giải:\n{final_ans[:1000]}\nTrả 1 dòng JSON {{\"type\":\"procedural\",\"title\":\"...\",\"body\":\"...\"}} hoặc SKIP", temp=0.1)
        if sk and "SKIP" not in sk:
            m = re.search(r'\{.*\}', sk, re.DOTALL)
            if m:
                try:
                    o = json.loads(m.group(0))
                    add_memory(o.get("type", "episodic") if o.get("type") in DEFAULT_DB else "episodic", o.get("title", ""), o.get("body", ""))
                except Exception: pass
    return final_ans, ok_final, py_err
