import os, re, io, json, base64, socket, tarfile, requests
from flask import Flask, render_template, request, jsonify, Response, stream_with_context, send_file

try:
    import urllib3.util.connection as _uc
    _uc.allowed_gai_family = lambda: socket.AF_INET
except Exception:
    pass

BASE = os.path.dirname(os.path.abspath(__file__))
ENV_P = os.path.join(BASE, ".env")
ICON_P = os.path.join(BASE, "static", "icon.png")
SESSION = requests.Session()

def load_env():
    if os.path.exists(ENV_P):
        with open(ENV_P, encoding="utf-8") as f:
            for l in f:
                s = l.strip()
                if s and not s.startswith("#") and "=" in s:
                    k, v = s.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"'))

def save_env(up):
    cur = {}
    if os.path.exists(ENV_P):
        with open(ENV_P, encoding="utf-8") as f:
            for l in f:
                s = l.strip()
                if "=" in s and not s.startswith("#"):
                    k, v = s.split("=", 1); cur[k.strip()] = v.strip()
    for k, v in up.items():
        v = (v or "").strip()
        if v: cur[k] = v; os.environ[k] = v
        else: cur.pop(k, None); os.environ.pop(k, None)
    with open(ENV_P, "w", encoding="utf-8") as f:
        for k, v in cur.items(): f.write(f"{k}={v}\n")

load_env()
app = Flask(__name__)

import hashlib as _hl, hmac as _hm

def _pin_token(pin):
    return _hl.sha256((pin + "|ai-phdam-lock").encode("utf-8")).hexdigest()

@app.before_request
def _check_app_pin():
    pin = os.getenv("APP_PIN", "").strip()
    if not pin:
        return None
    p = request.path
    if p in ("/manifest.json", "/sw.js", "/icon.png", "/favicon.ico", "/unlock"):
        return None
    if _hm.compare_digest(request.cookies.get("phdam_auth", ""), _pin_token(pin)):
        return None
    if p.startswith("/api/"):
        return jsonify({"status": "error", "message": "Chưa mở khóa PIN"}), 401
    return """<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI-Phdam Studio</title><link rel="manifest" href="/manifest.json"><link rel="icon" href="/icon.png">
<style>body{font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#f1f5f9}
.box{background:#fff;padding:24px;border-radius:16px;box-shadow:0 6px 24px rgba(0,0,0,.08);width:90%;max-width:320px;text-align:center}
input{width:100%;box-sizing:border-box;padding:12px;border:1px solid #cbd5e1;border-radius:10px;font-size:16px;margin:12px 0;text-align:center}
button{width:100%;padding:12px;border:none;border-radius:10px;background:#2563eb;color:#fff;font-size:16px;font-weight:600;cursor:pointer}</style>
</head><body><form class="box" method="post" action="/unlock"><h3>🔒 AI-Phdam Studio</h3>
<p style="color:#64748b;font-size:14px;margin:0">Nhập mã PIN để sử dụng</p>
<input type="password" name="pin" inputmode="numeric" placeholder="Nhập mã PIN..." autofocus required>
<button type="submit">Mở khóa</button></form></body></html>"""

@app.route("/unlock", methods=["POST"])
def _unlock_app():
    pin = os.getenv("APP_PIN", "").strip()
    entered = (request.form.get("pin") or "").strip()
    if pin and _hm.compare_digest(entered, pin):
        resp = app.make_response('<script>location.replace("/")</script>')
        resp.set_cookie("phdam_auth", _pin_token(pin), max_age=2592000, httponly=True, samesite="Lax")
        return resp
    return '<script>alert("Sai mã PIN!");location.replace("/")</script>', 403

app.json.ensure_ascii = False
STYLES = {"auto": "Tự động", "tan_co": "Tân Cổ Miền Tây", "vong_co": "Vọng Cổ / Cải Lương", "dieu_ly": "Điệu Lý & Dân Ca", "bolero": "Bolero / Nhạc Vàng", "vpop": "Nhạc Trẻ V-Pop", "quoc_te": "Nhạc Quốc Tế"}

def intent_of(msg, mode, has_img):
    if mode in ("music", "video", "image_edit"): return mode
    t = msg.lower()
    if any(k in t for k in ["video", "clip", "hoạt hình"]): return "video"
    if has_img or any(k in t for k in ["thay nền", "đổi nền", "đổi áo", "quần áo", "sửa ảnh", "chỉnh ảnh", "vẽ ảnh", "tạo ảnh"]): return "image_edit"
    if any(k in t for k in ["sáng tác", "bài hát", "tân cổ", "vọng cổ", "cải lương", "điệu lý", "bolero", "nhạc", "hát", "rap", "bài mới", "remix", "remex", "edm", "pop", "đàn", "nhịp"]): return "music"
    return "chat"

def synth_of(sk, msg):
    t = msg.lower()
    if sk in ("tan_co", "vong_co", "dieu_ly") or any(k in t for k in ["tân cổ", "vọng cổ", "cải lương", "lý ", "miền tây"]): return "ngu_cung"
    if sk == "bolero" or "bolero" in t: return "bolero"
    if any(k in t for k in ["remix", "remex", "edm", "vinahouse", "dj"]): return "remix"
    return "pop"

def sse(obj): return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"
BRAIN_PROMPT = (
    "Bạn là AI-Phdam Studio (trợ lý Meta AI tiếng Việt). "
    "Am hiểu nhạc cụ Việt Nam (Ghi-ta phím lõm, Đàn Tranh, Đàn Kìm, Đàn Cò, Đàn Bầu, Sáo trúc, Song lang) & Quốc tế (Piano, Guitar, Bass, Trống, Violin, Saxophone). "
    "Khi SÁNG TÁC NHẠC: viết lời + [Hợp âm] + nhạc cụ, dòng cuối ghi 'SUNO_TAG: <mô tả tiếng Anh>'. "
    "Khi SỬA ẢNH / ĐỔI ĐỒ / TẠO VIDEO: nếu chưa nối Key Fal.ai, KHÔNG được nói dối đã làm xong; hãy viết dòng cuối 'MEDIA_PROMPT: <lệnh tiếng Anh>' để hệ thống dùng hoặc hướng dẫn dùng công cụ bên dưới."
)

def offline_compose(intent, sk, msg):
    t = msg or "Quê hương miền Tây"
    if intent == "video": return f"[TẠO VIDEO TỪ ẢNH]\nYêu cầu: \"{t}\".\nBấm nút 'Tạo Video' bên dưới để xuất video chuyển động từ ảnh và lưu lên Drive!"
    if intent == "image_edit": return f"[CHỈNH ẢNH]\nYêu cầu: \"{t}\".\nDùng các nút chỉnh ảnh bên dưới và bấm 'Lưu Drive'!"
    if synth_of(sk, t) == "ngu_cung": return f"TÂN CỔ / ĐIỆU LÝ ({t})\n\nChiều buông trên bến sông quê, nhớ câu chuyện cũ: {t}.\nHò ơi... Sông Hậu con nước lớn ròng, nghe tiếng đàn kìm theo nhịp song lang...\nSUNO_TAG: Southern Vietnamese Tan Co, Dan Tranh, concave-fret guitar"
    return f"CA KHÚC MẪU ({t})\n\n[Am] Chiều nay nghe gió khẽ [Dm] đưa, nhắc lại kỷ [E7] niệm về {t}...\nSUNO_TAG: Vietnamese Bolero, nylon guitar, bass, violin"

def stream_gemini(key, sys_p, msg, hist, img):
    parts = []
    if img and img.startswith("data:image/") and "," in img:
        h, b64 = img.split(",", 1)
        parts.append({"inline_data": {"mime_type": h.split(";")[0][5:], "data": b64}})
    ht = "\n".join(f"{'User' if m.get('role')=='user' else 'AI'}: {m.get('text','')[:150]}" for m in (hist or [])[-2:])
    parts.append({"text": f"{ht}\nUser: {msg}" if ht else msg})
    body = {"system_instruction": {"parts": [{"text": sys_p}]}, "contents": [{"role": "user", "parts": parts}], "generationConfig": {"maxOutputTokens": 700}}
    code = 0
    for mdl in ("gemini-3.5-flash-lite", "gemini-3.6-flash"):
        try:
            r = SESSION.post(f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:streamGenerateContent?alt=sse", headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=body, stream=True, timeout=(5, 25))
            code = r.status_code
            if code == 200:
                got = False
                for raw in r.iter_lines(chunk_size=1):
                    if not raw: continue
                    line = raw.decode("utf-8", errors="ignore")
                    if not line.startswith("data: "): continue
                    try:
                        ps = ((json.loads(line[6:]).get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
                        t = "".join(p.get("text", "") for p in ps if p.get("text"))
                        if t: got = True; yield t
                    except Exception: pass
                if got: return
            elif code in (400, 401, 403): yield f"__ERR__:Key lỗi ({code})"; return
        except Exception as e: yield f"__ERR__:{e}"; return
    yield f"__ERR__:Gemini HTTP {code}"
def call_fal(intent, prompt_en, img, fk):
    hdr = {"Authorization": f"Key {fk}", "Content-Type": "application/json"}
    try:
        if intent == "video":
            ep = "https://queue.fal.run/fal-ai/kling-video/v2.1/standard/" + ("image-to-video" if img else "text-to-video")
            body = {"prompt": prompt_en, "image_url": img} if img else {"prompt": prompt_en}
            r = SESSION.post(ep, headers=hdr, json=body, timeout=25)
            if r.status_code in (200, 201):
                d = r.json(); return {"status_url": d.get("status_url"), "response_url": d.get("response_url")}, None
            return None, f"Fal Video HTTP {r.status_code}"
        ep = "https://fal.run/google/nano-banana-2.1/edit" if img else "https://fal.run/fal-ai/nano-banana-2"
        body = {"prompt": prompt_en, "image_urls": [img]} if img else {"prompt": prompt_en}
        r = SESSION.post(ep, headers=hdr, json=body, timeout=55)
        if r.status_code == 200 and r.json().get("images"):
            return {"image_url": r.json()["images"][0].get("url")}, None
        return None, f"Fal Ảnh HTTP {r.status_code}"
    except Exception as e: return None, str(e)

@app.route("/manifest.json")
def manifest():
    v=int(os.path.getmtime(ICON_P)) if os.path.exists(ICON_P) else 0
    r=jsonify({"name": "AI-Phdam Studio", "short_name": "AI-Phdam", "start_url": "/", "display": "standalone", "background_color": "#ffffff", "theme_color": "#ffffff", "icons": [{"src": f"/icon.png?v={v}", "sizes": "512x512", "type": "image/png", "purpose": "any"}, {"src": f"/icon.png?v={v}", "sizes": "192x192", "type": "image/png", "purpose": "any"}]})
    r.headers["Cache-Control"]="no-store"; return r

@app.route("/sw.js")
def sw():
    return Response("self.addEventListener('install',()=>self.skipWaiting());self.addEventListener('activate',e=>e.waitUntil(clients.claim()));", mimetype="application/javascript")

@app.route("/icon.png")
@app.route("/favicon.ico")
def app_icon():
    if os.path.exists(ICON_P):
        r = send_file(ICON_P, mimetype="image/png"); r.headers["Cache-Control"] = "no-cache"; return r
    return Response('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="22" fill="#2563eb"/><text x="50" y="62" font-size="44" text-anchor="middle" fill="#fff" font-family="sans-serif">AI</text></svg>', mimetype="image/svg+xml")

@app.route("/api/set-icon", methods=["POST"])
def set_icon():
    img = ((request.get_json(silent=True) or {}).get("image") or "")
    if "," not in img: return jsonify({"status": "error", "message": "Ảnh không hợp lệ"}), 400
    with open(ICON_P, "wb") as f: f.write(base64.b64decode(img.split(",", 1)[1]))
    return jsonify({"status": "ok", "message": "Đã đặt làm Icon App!"})
@app.route("/api/export-installer")
def export_installer():
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for rel in ("app.py", "templates/index.html", "static/icon.png"):
            fp = os.path.join(BASE, rel)
            if os.path.exists(fp): tf.add(fp, arcname=rel)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    lines = "\n".join(b64[i:i+76] for i in range(0, len(b64), 76))
    script = ("#!/data/data/com.termux/files/usr/bin/bash\ncommand -v python3 >/dev/null || (pkg update -y && pkg install -y python)\npython3 -c 'import flask, requests' 2>/dev/null || pip install flask requests\nmkdir -p $HOME/AI-Phdam/templates $HOME/AI-Phdam/static\nbase64 -d <<'__AI__' | tar -xz -C $HOME/AI-Phdam\n" + lines + "\n__AI__\nprintf '#!/data/data/com.termux/files/usr/bin/sh\\ntermux-wake-lock 2>/dev/null\\npkill -9 -f app.py 2>/dev/null\\nexec python3 %s/AI-Phdam/app.py\\n' $HOME > $PREFIX/bin/studio\nchmod +x $PREFIX/bin/studio\necho bWtkaXIgLXAgfi8uc2hvcnRjdXRzCmNhdCA8PCAnRV9SVU4nID4gfi9ydW4tYWkuc2gKIyEvZGF0YS9kYXRhL2NvbS50ZXJtdXgvZmlsZXMvdXNyL2Jpbi9iYXNoCmV4cG9ydCBQQVRIPSIkSE9NRS8ubG9jYWwvYmluOiRQQVRIIgpMT0c9IiRIT01FL2FpLXBoZGFtLmxvZyIKY2hlY2tfcG9ydCgpIHsKICBweXRob24zIC1jICJpbXBvcnQgc29ja2V0OyBzPXNvY2tldC5zb2NrZXQoKTsgcy5zZXR0aW1lb3V0KDAuNSk7IGV4aXQoMCBpZiBzLmNvbm5lY3RfZXgoKCcxMjcuMC4wLjEnLDUwMDApKT09MCBlbHNlIDEpIiAyPi9kZXYvbnVsbAp9Cgp0ZXJtdXgtd2FrZS1sb2NrIDI+L2Rldi9udWxsCgppZiBbICIkMSIgPSAic3RvcCIgXTsgdGhlbgogIHBraWxsIC05IC1mICJhcHBcLnB5IiAyPi9kZXYvbnVsbAogIGVjaG8gIkRhIHRhdCBBSS1QaGRhbS4iCiAgZXhpdCAwCmZpCgppZiBbICIkMSIgIT0gInJlc3RhcnQiIF0gJiYgY2hlY2tfcG9ydDsgdGhlbgogIGVjaG8gIk9LOiBBSS1QaGRhbSBkYW5nIGNoYXkgc2FuIHRhaSBodHRwOi8vMTI3LjAuMC4xOjUwMDAiCiAgZXhpdCAwCmZpCgpwa2lsbCAtOSAtZiAiYXBwXC5weSIgMj4vZGV2L251bGwKc2xlZXAgMQoKaWYgY29tbWFuZCAtdiBzdHVkaW8gPi9kZXYvbnVsbCAyPiYxOyB0aGVuCiAgbm9odXAgc3R1ZGlvID4gIiRMT0ciIDI+JjEgJgplbHNlCiAgY2QgIiRIT01FL0FJLVBoZGFtIiAmJiBub2h1cCBweXRob24zIGFwcC5weSA+ICIkTE9HIiAyPiYxICYKZmkKCmZvciBpIGluIDEgMiAzIDQgNTsgZG8KICBzbGVlcCAxCiAgaWYgY2hlY2tfcG9ydDsgdGhlbgogICAgZWNobyAiT0s6IEFJLVBoZGFtIGRhIGNoYXkhIE1vIGFwcCBBSS1QaGRhbSBob2FjIGh0dHA6Ly8xMjcuMC4wLjE6NTAwMCIKICAgIGV4aXQgMAogIGZpCmRvbmUKCmVjaG8gIkxvaTogQ29uZyA1MDAwIGNodWEgbGVuLiBDaGkgdGlldDoiCnRhaWwgLW4gMTUgIiRMT0ciCgpFX1JVTgpjaG1vZCAreCB+L3J1bi1haS5zaApjYXQgPDwgJ0VfU0MnID4gfi8uc2hvcnRjdXRzL0FJLVBoZGFtCiMhL2RhdGEvZGF0YS9jb20udGVybXV4L2ZpbGVzL3Vzci9iaW4vYmFzaApiYXNoICIkSE9NRS9ydW4tYWkuc2giCnRlcm11eC1vcGVuLXVybCBodHRwOi8vMTI3LjAuMC4xOjUwMDAgMj4vZGV2L251bGwKCkVfU0MKY2htb2QgK3ggfi8uc2hvcnRjdXRzL0FJLVBoZGFtCmNhdCA8PCAnRV9SQycgPiB+Ly5iYXNocmMKYWxpYXMgYWk9J2Jhc2ggfi9ydW4tYWkuc2gnCmFsaWFzIGFpLXJlc3RhcnQ9J2Jhc2ggfi9ydW4tYWkuc2ggcmVzdGFydCcKYWxpYXMgYWktc3RvcD0nYmFzaCB+L3J1bi1haS5zaCBzdG9wJwphbGlhcyBhaS1sb2c9J3RhaWwgLW4gMzAgfi9haS1waGRhbS5sb2cnCmJhc2ggfi9ydW4tYWkuc2gKCkVfUkMKYmFzaCB+L3J1bi1haS5zaCByZXN0YXJ0Cg== | base64 -d | bash\n")
    return Response(script, mimetype="text/plain; charset=utf-8", headers={"Content-Disposition": "attachment; filename=CaiDat-AI-Phdam.txt"})

@app.route("/")
def index():
    k, fk = os.getenv("AI_CHAT_KEY", ""), os.getenv("FAL_API_KEY", "")
    return render_template("index.html", music_styles=STYLES, chat_key=k, fal_key=fk, has_key=bool(k))

@app.route("/api/config", methods=["POST"])
def api_config():
    d = request.get_json(silent=True) or {}
    k, fk = (d.get("chat_key") or "").strip(), (d.get("fal_key") or "").strip()
    save_env({"AI_CHAT_KEY": k, "FAL_API_KEY": fk})
    if not k: return jsonify({"status": "ok", "message": "Đã lưu (Chế độ Độc Lập)", "has_key": False})
    if k.startswith(("AIza", "AQ.")):
        try:
            r = SESSION.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent", headers={"x-goog-api-key": k, "Content-Type": "application/json"}, json={"contents": [{"parts": [{"text": "hi"}]}], "generationConfig": {"maxOutputTokens": 5}}, timeout=10)
            return jsonify({"status": "ok", "message": "OK! Key hoạt động tốt!" if r.status_code == 200 else f"Google báo lỗi {r.status_code}", "has_key": r.status_code == 200})
        except Exception as e: return jsonify({"status": "ok", "message": f"Lỗi mạng: {e}", "has_key": False})
    return jsonify({"status": "ok", "message": "Đã lưu Key!", "has_key": True})

@app.route("/api/chat-stream", methods=["POST"])
def api_chat_stream():
    d = request.get_json(silent=True) or {}
    msg, mode, sk, img, hist = (d.get("message") or "").strip(), d.get("mode") or "auto", d.get("music_style") or "auto", d.get("image_data") or "", d.get("history") or []
    if not msg and not img: return jsonify({"status": "error", "message": "Hãy nhập nội dung!"}), 400
    intent, ck, fk = intent_of(msg, mode, bool(img)), os.getenv("AI_CHAT_KEY", "").strip(), os.getenv("FAL_API_KEY", "").strip()
    sys_p = f"{BRAIN_PROMPT}\nTác vụ: {intent}. Điệu: {STYLES.get(sk,'Tự động')}."
    def gen():
        yield sse({"intent": intent})
        got, err, full = False, "", ""
        if ck.startswith(("AIza", "AQ.")):
            for c in stream_gemini(ck, sys_p, msg or "Phân tích ảnh", hist, img):
                if c.startswith("__ERR__:"): err = c[8:]; break
                got = True; full += c; yield sse({"chunk": c})
        if not got:
            off = offline_compose(intent, sk, msg)
            if err: off = f"[Key lỗi ({err}) -> Chế độ Độc Lập]\n\n" + off
            full = off; yield sse({"chunk": off})
        out = {"done": True, "intent": intent, "synth": synth_of(sk, msg) if intent == "music" else "", "img_tools": bool(img) and intent == "image_edit", "vid_tools": bool(img) and intent == "video"}
        if fk and intent in ("video", "image_edit"):
            m = re.search(r"MEDIA_PROMPT:\s*(.+)", full)
            mp = m.group(1).strip() if m else (msg or "cinematic realistic style")
            mr, me = call_fal(intent, mp, img, fk)
            if mr: out["media"] = mr
            elif me: out["media_note"] = me
        yield sse(out)
    return Response(stream_with_context(gen()), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})

@app.route("/api/media-status", methods=["POST"])
def api_media_status():
    d = request.get_json(silent=True) or {}
    fk, su, ru = os.getenv("FAL_API_KEY", "").strip(), d.get("status_url", ""), d.get("response_url", "")
    if not fk or not su: return jsonify({"status": "error"}), 400
    hdr = {"Authorization": f"Key {fk}"}
    try:
        st = SESSION.get(su, headers=hdr, timeout=15).json()
        if st.get("status") == "COMPLETED" and ru:
            out = SESSION.get(ru, headers=hdr, timeout=20).json()
            return jsonify({"status": "completed", "video_url": (out.get("video") or {}).get("url")})
        return jsonify({"status": "processing"})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, threaded=True)
