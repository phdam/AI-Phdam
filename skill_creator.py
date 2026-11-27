import os, re, json, time, shutil

SKILLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")
os.makedirs(SKILLS_DIR, exist_ok=True)

def _slug(txt):
    s = re.sub(r'[^a-z0-9]+', '_', (txt or "").lower()).strip('_')
    return s[:36] or f"skill_{int(time.time())}"

def _find_existing_skill(bc, topic):
    db = bc.load_db()
    words = set(re.findall(r'[a-zA-ZÀ-ỹ0-9_]{2,}', (topic or "").lower()))
    best, best_hit = None, 0
    for it in db.get("procedural", []):
        txt = (it.get("title", "") + " " + it.get("slug", "")).lower()
        hit = sum(1 for w in words if w in txt)
        if hit > best_hit and hit >= 2:
            best_hit, best = hit, it
    return best

def create_or_evolve_skill(session, key, msg, bc):
    existing = _find_existing_skill(bc, msg)
    prev_ver = int(existing.get("version", 1)) if existing else 0
    prev_score = int(existing.get("score", 0)) if existing else 0
    new_ver = prev_ver + 1 if existing else 1
    mode_lbl = f"Nâng cấp v{prev_ver} → v{new_ver}" if existing else "Tạo mới v1"

    # 1-5. Gop Nghien cuu + Thiet ke + Coding vao 1 luot (tiet kiem 50% quota)
    arch_sys = (
        "Bạn là AI Master Skill Creator (Nghiên cứu + Kiến trúc + Lập trình).\n"
        "Hãy nghiên cứu thực tế rồi xuất ĐÚNG 3 file theo định dạng:\n"
        "===FILE: SKILL.md===\n...\n===END_FILE===\n"
        "===FILE: skill_tool.py===\n...\n===END_FILE===\n"
        "===FILE: test_skill.py===\n...\n===END_FILE===\n"
        "QUY TẮC: SKILL.md ghi rõ Tên, Phiên bản v" + str(new_ver) + ", Mục tiêu, Cách dùng, Ví dụ. "
        "skill_tool.py viết Python sạch (thư viện chuẩn hoặc requests/flask), không lộ key. "
        "test_skill.py tự test ít nhất 3 ca rồi tự thoát."
    )
    prev_note = f"Nâng cấp từ v{prev_ver} ({prev_score}đ): {existing.get('body','')}\n" if existing else ""
    gen_out, mdl2 = bc.call_gemini_once(session, key, arch_sys, f"Yêu cầu ({mode_lbl}): {msg}\n{prev_note}", temp=0.2, use_search=True)
    files = bc.parse_project_files(gen_out)
    if "skill_tool.py" not in files or "test_skill.py" not in files:
        return (gen_out or f"⚠️ Lỗi tạo Skill ({mdl2})"), "", False
    if "SKILL.md" not in files:
        files["SKILL.md"] = f"# Skill: {msg[:60]}\nPhiên bản: v{new_ver}\n"
    research = files["SKILL.md"][:300]

    # 6-7. Testing & Debugging Gate (toi da 2 vong sua theo Traceback that)
    pid, ok_test, test_log = bc.run_workspace_tests(files)
    rounds = 0
    while not ok_test and rounds < 2:
        rounds += 1
        dbg_p = (
            f"Chạy test_skill.py bị lỗi thật:\n{test_log}\n\n"
            + "\n".join(f"===FILE: {k}===\n{v}===END_FILE===" for k, v in files.items())
            + "\nHãy sửa đúng nguyên nhân gốc và xuất lại file bị lỗi theo format ===FILE: ...=== ... ===END_FILE===."
        )
        fix_out, _ = bc.call_gemini_once(session, key, "Bạn là AI Debugger, sửa dứt điểm theo Traceback thật.", dbg_p, temp=0.15)
        fixed = bc.parse_project_files(fix_out)
        if fixed:
            files.update(fixed)
            pid, ok_test, test_log = bc.run_workspace_tests(files)
        else:
            break

    # 8. Security & Independent Quality Evaluation Gate
    warns = bc.security_scan(files)
    eval_p = (
        f"Yêu cầu: {msg}\nKết quả chạy test_skill.py: {'ĐẠT' if ok_test else 'THẤT BẠI'}\n"
        f"Cảnh báo bảo mật: {warns or 'Không'}\n\n"
        f"SKILL.md:\n{files.get('SKILL.md','')[:1200]}\n\nskill_tool.py:\n{files.get('skill_tool.py','')[:1500]}\n\n"
        'Hãy chấm điểm độc lập 0-100 và trả ĐÚNG 1 dòng JSON: {"score": 85, "verdict": "PASS hoặc FAIL", "notes": "nhận xét ngắn gọn"}'
    )
    ev_raw, _ = bc.call_gemini_once(session, key, "Bạn là AI Reviewer & Quality Evaluator khắt khe.", eval_p, temp=0.1, mdl_list=("gemini-3.5-flash-lite", "gemini-3.6-flash"))
    score, verdict, notes = (80 if ok_test else 30), ("PASS" if ok_test else "FAIL"), ""
    m = re.search(r'\{.*\}', ev_raw or "", re.DOTALL)
    if m:
        try:
            eo = json.loads(m.group(0))
            score = int(eo.get("score", score))
            verdict = str(eo.get("verdict", verdict)).upper()
            notes = str(eo.get("notes", ""))
        except Exception: pass

    passed_gate = ok_test and not warns and score >= 70 and verdict == "PASS" and (not existing or score >= prev_score)

    # 9-10. Dong goi & Luu vao Thu vien Skill (CHI LUU KHI DAT GATE!)
    slug = (existing.get("slug") if existing else "") or _slug(msg)
    if passed_gate:
        bc.zip_workspace(pid)
        sdir = os.path.join(SKILLS_DIR, slug, f"v{new_ver}")
        os.makedirs(sdir, exist_ok=True)
        for fn, body in files.items():
            fp = os.path.join(sdir, os.path.basename(fn))
            open(fp, "w", encoding="utf-8").write(body)
        db = bc.load_db()
        arr = [x for x in db.get("procedural", []) if x.get("slug") != slug and x.get("title") != msg[:80]]
        title_line = next((l.replace("#", "").strip() for l in files["SKILL.md"].splitlines() if l.strip()), msg[:60])
        arr.append({
            "slug": slug,
            "version": new_ver,
            "score": score,
            "title": f"{title_line[:70]} (v{new_ver} · {score}đ)",
            "body": (notes or research[:240])[:320],
            "skill_md": files["SKILL.md"][:2500],
            "ts": int(time.time())
        })
        db["procedural"] = arr[-50:]
        bc.save_db(db)

    status_txt = "✅ ĐẠT CỔNG KIỂM CHỨNG — ĐÃ LƯU VÀO THƯ VIỆN SKILL" if passed_gate else "❌ CHƯA ĐẠT CỔNG KIỂM THỬ — TỪ CHỐI LƯU SKILL"
    if existing and ok_test and score < prev_score:
        status_txt = f"⚠️ Bản v{new_ver} ({score}đ) chưa vượt bản v{prev_ver} ({prev_score}đ) — Giữ nguyên v{prev_ver}"

    rep = [
        f"🏭 **MASTER SKILL CREATOR** ({mode_lbl} · Model `{mdl2}`)",
        f"**Trạng thái:** {status_txt}",
        f"📊 **Đánh giá chất lượng:** `{score}/100` — {notes or 'OK'}",
        f"🧪 **Kiểm thử thật `test_skill.py` ({rounds} lần tự sửa):** {'✅ ĐẠT' if ok_test else '❌ LỖI'}\n```text\n{test_log}\n```",
        f"🛡️ **Bảo mật:** {', '.join(warns) if warns else 'An toàn'}",
        f"📄 **Tóm tắt `SKILL.md`:**\n{files.get('SKILL.md','')[:900]}"
    ]
    if passed_gate and pid:
        rep.append(f"📦 **[Tải gói Skill (.zip) tại đây](/api/download-project/{pid})**")
    return "\n\n".join(rep), (pid if passed_gate else ""), passed_gate
