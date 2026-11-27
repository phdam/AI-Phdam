import os, re, json, time, shutil, subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STG_ROOT = os.path.join(BASE_DIR, "_staging")
EXT_DIR = os.path.join(BASE_DIR, "extensions")
BAK_DIR = os.path.expanduser("~/ai_backups")
os.makedirs(STG_ROOT, exist_ok=True)
os.makedirs(EXT_DIR, exist_ok=True)
os.makedirs(BAK_DIR, exist_ok=True)

ALLOWED_ROOTS = ("app.py", "brain_core.py", "skill_creator.py", "templates/index.html")

def is_self_upgrade(msg):
    m = (msg or "").lower()
    if re.search(r'(tạo skill|nâng cấp skill|cải tiến skill|viết skill|tự học)', m):
        return False
    return bool(re.search(r'(tự nâng cấp|nâng cấp ai-phdam|nâng cấp chính mình|nâng cấp app|cải tiến app|nâng cấp hệ thống|thêm tính năng vào app|thêm nút|sửa giao diện app)', m))

def _apply_patches(stg_dir, text):
    changed = []
    # 1. File moi (uu tien extensions/ hoac file duoc phep)
    for m in re.finditer(r'===FILE:\s*([^\n=]+?)===\s*\n(.*?)===END_FILE===', text or "", re.DOTALL):
        rel = m.group(1).strip().replace("\\", "/").lstrip("/")
        if ".." in rel or (not rel.startswith("extensions/") and rel not in ALLOWED_ROOTS):
            continue
        fp = os.path.join(stg_dir, rel)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "w", encoding="utf-8").write(m.group(2).rstrip() + "\n")
        changed.append(rel)

    # 2. Sua chinh xac tung doan trong file hien co (an toan, khong xoa nham code cu)
    for m in re.finditer(r'===PATCH:\s*([^\n=]+?)===\s*\n(.*?)===END_PATCH===', text or "", re.DOTALL):
        rel = m.group(1).strip().replace("\\", "/").lstrip("/")
        if rel not in ALLOWED_ROOTS:
            continue
        fp = os.path.join(stg_dir, rel)
        if not os.path.exists(fp):
            continue
        src = open(fp, encoding="utf-8").read()
        ok_any = False
        for blk in re.finditer(r'<<<FIND>>>\n(.*?)\n<<<REPLACE>>>\n(.*?)\n<<<END>>>', m.group(2), re.DOTALL):
            find_s, rep_s = blk.group(1), blk.group(2)
            if find_s in src:
                src = src.replace(find_s, rep_s, 1)
                ok_any = True
        if ok_any:
            open(fp, "w", encoding="utf-8").write(src)
            if rel not in changed:
                changed.append(rel)
    return changed

def _smoke_test_staging(stg_dir):
    # Kiem tra cu phap tat ca file .py
    for root, _, fns in os.walk(stg_dir):
        for fn in fns:
            if fn.endswith(".py"):
                fp = os.path.join(root, fn)
                r = subprocess.run(["python3", "-m", "py_compile", fp], capture_output=True, text=True)
                if r.returncode != 0:
                    return False, f"Lỗi cú pháp {os.path.relpath(fp, stg_dir)}:\n{r.stderr}"

    # Kiem tra cac thanh phan loi khong duoc phep mat
    ap_txt = open(os.path.join(stg_dir, "app.py"), encoding="utf-8").read()
    hp_txt = open(os.path.join(stg_dir, "templates/index.html"), encoding="utf-8").read()
    for req in ("/api/chat-stream", "/api/brain-db", "/api/apply-upgrade", "APP_PIN"):
        if req not in ap_txt:
            return False, f"Vi phạm an toàn: Thiếu thành phần lõi `{req}` trong app.py"
    for req in ('id="fIn"', 'id="txt"', 'id="bSend"', "CLEAN_UI_START"):
        if req not in hp_txt:
            return False, f"Vi phạm an toàn: Thiếu giao diện lõi `{req}` trong index.html"

    # Chay thu Flask app trong tien trinh co lap
    test_code = (
        "import sys, os; os.environ['APP_PIN']=''; sys.path.insert(0, os.getcwd()); "
        "from app import app; c = app.test_client(); "
        "r1 = c.get('/'); assert r1.status_code == 200 and b'bSend' in r1.data, f'Home {r1.status_code}'; "
        "r2 = c.get('/manifest.json'); assert r2.status_code == 200, f'Manifest {r2.status_code}'; "
        "r3 = c.get('/api/brain-db'); assert r3.status_code == 200, f'BrainDB {r3.status_code}'; "
        "print('SMOKE_TEST_PASS')"
    )
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1"}
    res = subprocess.run(["python3", "-c", test_code], cwd=stg_dir, env=env, capture_output=True, text=True, timeout=12)
    out = (res.stdout + "\n" + res.stderr).strip()
    if res.returncode != 0 or "SMOKE_TEST_PASS" not in out:
        return False, f"Chạy thử app thất bại:\n{out[-1000:]}"
    return True, "Đạt toàn bộ kiểm tra cú pháp, bảo mật lõi và chạy thử Flask (200 OK)."

def _clean_old_staging():
    now = time.time()
    for n in os.listdir(STG_ROOT):
        p = os.path.join(STG_ROOT, n)
        try:
            if now - os.path.getmtime(p) > 7200:
                shutil.rmtree(p, ignore_errors=True)
        except Exception: pass

def prepare_self_upgrade(session, key, msg, bc):
    _clean_old_staging()
    uid = f"u_{int(time.time())}"
    stg = os.path.join(STG_ROOT, uid)
    os.makedirs(os.path.join(stg, "templates"), exist_ok=True)
    os.makedirs(os.path.join(stg, "extensions"), exist_ok=True)
    os.makedirs(os.path.join(stg, "static"), exist_ok=True)
    for rel in ALLOWED_ROOTS:
        src = os.path.join(BASE_DIR, rel)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(stg, rel))

    ap_now = open(os.path.join(stg, "app.py"), encoding="utf-8").read()
    hp_now = open(os.path.join(stg, "templates/index.html"), encoding="utf-8").read()
    sys_p = (
        "Bạn là AI Master Architect & Self-Upgrader của hệ thống AI-Phdam.\n"
        "NHIỆM VỤ: Tạo bản nâng cấp AN TOÀN cho AI-Phdam theo đúng yêu cầu người dùng.\n"
        "QUY TẮC BẮT BUỘC:\n"
        "1. KHÔNG ĐƯỢC XÓA các route/tính năng lõi (/api/chat-stream, /api/brain-db, /api/apply-upgrade, APP_PIN, #fIn, #txt, #bSend, CLEAN_UI_START).\n"
        "2. Với logic mới hoặc API mới, ưu tiên tạo module trong `extensions/` bằng ===FILE: extensions/ten_module.py=== ... ===END_FILE=== rồi nối nhẹ vào `app.py`.\n"
        "3. Khi sửa `app.py` hoặc `templates/index.html`, BẮT BUỘC dùng định dạng tìm-và-thay chính xác:\n"
        "===PATCH: duong_dan_file===\n<<<FIND>>>\nđoạn code gốc chính xác tuyệt đối\n<<<REPLACE>>>\nđoạn code mới\n<<<END>>>\n===END_PATCH===\n"
    )
    prompt = f"YÊU CẦU NÂNG CẤP:\n{msg}\n\n--- app.py hiện tại ---\n{ap_now}\n\n--- templates/index.html hiện tại ---\n{hp_now}"
    out, mdl = bc.call_gemini_once(session, key, sys_p, prompt, temp=0.15)
    if not out:
        return f"⚠️ Không gọi được AI Self-Upgrader ({mdl})", "", False

    changed = _apply_patches(stg, out)
    if not changed:
        shutil.rmtree(stg, ignore_errors=True)
        return f"⚠️ AI chưa tạo được bản vá khớp cấu trúc file hiện tại. Thử mô tả cụ thể hơn nhé!\n\n{out[:800]}", "", False

    ok, log = _smoke_test_staging(stg)
    if not ok:
        dbg_out, _ = bc.call_gemini_once(session, key, sys_p, f"Bản nâng cấp bị lỗi khi chạy thử:\n{log}\n\nHãy sửa lại bằng ===PATCH:...=== hoặc ===FILE:...===.", temp=0.1)
        if dbg_out:
            c2 = _apply_patches(stg, dbg_out)
            changed = list(dict.fromkeys(changed + c2))
            ok, log = _smoke_test_staging(stg)

    if not ok:
        shutil.rmtree(stg, ignore_errors=True)
        return f"❌ **TỰ NÂNG CẤP BỊ CHẶN DO CHƯA ĐẠT KIỂM THỬ** (App đang chạy vẫn an toàn 100%):\n```text\n{log}\n```", "", False

    meta = {"uid": uid, "msg": msg[:200], "changed": changed, "model": mdl, "ts": int(time.time())}
    json.dump(meta, open(os.path.join(stg, "_meta.json"), "w", encoding="utf-8"), ensure_ascii=False)
    rep = (
        f"🛠️ **BẢN NÂNG CẤP THỬ NGHIỆM ĐÃ SẴN SÀNG** (`{mdl}`)\n"
        f"📁 **File thay đổi:** " + ", ".join(f"`{c}`" for c in changed) + "\n"
        f"🧪 **Kiểm thử tự động:** ✅ {log}\n"
        f"🔒 **Trạng thái:** Chưa ghi đè vào app chính — bấm nút bên dưới để **Phê duyệt & Nạp** (có tự động sao lưu dự phòng).\n"
        f"/api/apply-upgrade/{uid}"
    )
    return rep, uid, True

def apply_staged_upgrade(uid):
    if not re.fullmatch(r'u_\d+', uid or ""):
        return False, "Mã bản nâng cấp không hợp lệ."
    stg = os.path.join(STG_ROOT, uid)
    meta_p = os.path.join(stg, "_meta.json")
    if not os.path.exists(meta_p):
        return False, "Bản nâng cấp không tồn tại hoặc đã hết hạn."
    meta = json.load(open(meta_p, encoding="utf-8"))
    ok, log = _smoke_test_staging(stg)
    if not ok:
        return False, f"Kiểm thử lại thất bại: {log}"

    # Sao luu truoc khi nap
    snap = os.path.join(BAK_DIR, f"snap_{uid}")
    os.makedirs(os.path.join(snap, "templates"), exist_ok=True)
    os.makedirs(os.path.join(snap, "extensions"), exist_ok=True)
    for rel in ALLOWED_ROOTS:
        sp = os.path.join(BASE_DIR, rel)
        if os.path.exists(sp):
            shutil.copy2(sp, os.path.join(snap, rel))

    try:
        for rel in meta.get("changed", []):
            src = os.path.join(stg, rel)
            dst = os.path.join(BASE_DIR, rel)
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
        ok2, log2 = _smoke_test_staging(BASE_DIR)
        if not ok2:
            raise RuntimeError(log2)
    except Exception as e:
        for rel in ALLOWED_ROOTS:
            sp = os.path.join(snap, rel)
            if os.path.exists(sp):
                shutil.copy2(sp, os.path.join(BASE_DIR, rel))
        return False, f"Lỗi khi nạp, đã tự khôi phục bản cũ an toàn: {e}"

    shutil.rmtree(stg, ignore_errors=True)
    return True, f"Đã nạp thành công {len(meta.get('changed',[]))} file (Bản sao lưu: snap_{uid})."
