import brain_core as _bc
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

# === PIN_LOCK_START ===
import hashlib as _hl, hmac as _hm
def _pin_token(pin): return _hl.sha256((pin + "|ai-phdam-lock").encode()).hexdigest()
@app.before_request
def _check_app_pin():
    pin = os.getenv("APP_PIN", "").strip()
    if not pin: return None
    p = request.path
    if p in ("/manifest.json", "/sw.js", "/icon.png", "/favicon.ico", "/unlock", "/privacy") or p.startswith("/.well-known/"): return None
    if _hm.compare_digest(request.cookies.get("phdam_auth", ""), _pin_token(pin)): return None
    if p.startswith("/api/"): return jsonify({"status": "error", "message": "Chưa mở khóa PIN"}), 401
    return """<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI-Phdam Studio</title><link rel="manifest" href="/manifest.json"><link rel="icon" href="/icon.png"><style>body{font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#f1f5f9}.box{background:#fff;padding:24px;border-radius:16px;box-shadow:0 6px 24px rgba(0,0,0,.08);width:90%;max-width:320px;text-align:center}input{width:100%;box-sizing:border-box;padding:12px;border:1px solid #cbd5e1;border-radius:10px;font-size:16px;margin:12px 0;text-align:center}button{width:100%;padding:12px;border:none;border-radius:10px;background:#2563eb;color:#fff;font-size:16px;font-weight:600}</style></head><body><form class="box" method="post" action="/unlock"><h3>🔒 AI-Phdam Studio</h3><input type="password" name="pin" inputmode="numeric" placeholder="Nhập mã PIN..." autofocus required><button type="submit">Mở khóa</button></form></body></html>"""
@app.route("/unlock", methods=["POST"])
def _unlock_app():
    pin = os.getenv("APP_PIN", "").strip()
    if pin and _hm.compare_digest((request.form.get("pin") or "").strip(), pin):
        r = app.make_response('<script>location.replace("/")</script>')
        r.set_cookie("phdam_auth", _pin_token(pin), max_age=2592000, httponly=True, samesite="Lax")
        return r
    return '<script>alert("Sai mã PIN!");location.replace("/")</script>', 403
# === PIN_LOCK_END ===

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
def manifest_json():
    return jsonify({"id":"/","name":"AI-Phdam Studio","short_name":"AI-Phdam","description":"Tro ly AI da nang phan tich nhac, hinh anh va video","start_url":"/","scope":"/","display":"standalone","background_color":"#ffffff","theme_color":"#2563eb","orientation":"portrait","icons":[{"src":"/icon.png","sizes":"512x512","type":"image/png","purpose":"any"},{"src":"/icon.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]})
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
    script = ("#!/data/data/com.termux/files/usr/bin/bash\ncommand -v python3 >/dev/null || (pkg update -y && pkg install -y python)\npython3 -c 'import flask, requests' 2>/dev/null || pip install flask requests\nmkdir -p $HOME/AI-Phdam/templates $HOME/AI-Phdam/static\nbase64 -d <<'__AI__' | tar -xz -C $HOME/AI-Phdam\n" + lines + "\n__AI__\nprintf '#!/data/data/com.termux/files/usr/bin/sh\\ntermux-wake-lock 2>/dev/null\\npkill -9 -f app.py 2>/dev/null\\nexec python3 %s/AI-Phdam/app.py\\n' $HOME > $PREFIX/bin/studio\nchmod +x $PREFIX/bin/studio\nexec studio\n")
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

# === SMART_BRAIN_START ===
import mimetypes as _mt, uuid as _uuid, time as _time
UPLOAD_TMP = os.path.expanduser("~/AI-Phdam/_tmp_uploads")
os.makedirs(UPLOAD_TMP, exist_ok=True)
LOCAL_MEDIA_CACHE = {}
MIME_FB = {".mp3":"audio/mpeg",".m4a":"audio/mp4",".wav":"audio/wav",".ogg":"audio/ogg",".aac":"audio/aac",".flac":"audio/flac",".mp4":"video/mp4",".mov":"video/quicktime",".webm":"video/webm",".mkv":"video/x-matroska",".3gp":"video/3gpp",".jpg":"image/jpeg",".jpeg":"image/jpeg",".png":"image/png",".webp":"image/webp"}
def _guess_mime(fn, rm):
    ext = os.path.splitext(fn or "")[1].lower()
    return MIME_FB[ext] if ext in MIME_FB else (rm if rm and rm != "application/octet-stream" else (_mt.guess_type(fn or "")[0] or "application/octet-stream"))
MEM_PATH = os.path.expanduser("~/AI-Phdam/brain_memory.json")
def _load_mem():
    try:
        if os.path.exists(MEM_PATH): return json.load(open(MEM_PATH, encoding="utf-8"))
    except Exception: pass
    return {"turns": []}
LAST_MEM = _load_mem()
GREETS = ("alo", "alô", "hi", "hello", "chào", "chào bạn", "ê", "tiếp tục", "làm tiếp", "tiếp đi")
def _save_mem(u, a):
    u, a = (u or "").strip(), (a or "").strip()
    if not u or not a or u.lower() in GREETS or len(u) < 4: return
    LAST_MEM.setdefault("turns", []).append({"u": u[:400], "a": a[:600]})
    LAST_MEM["turns"] = LAST_MEM["turns"][-5:]
    try: json.dump(LAST_MEM, open(MEM_PATH, "w", encoding="utf-8"), ensure_ascii=False)
    except Exception: pass
SMART_BRAIN_PROMPT = """Bạn là AI-Phdam — trợ lý AI thông minh, chính xác và có kỷ luật cao.
NGUYÊN TẮC BẮT BUỘC:
1. BÁM SÁT 100% NỘI DUNG NGƯỜI DÙNG HỎI HOẶC NÓI: Chỉ tập trung giải quyết đúng vấn đề, đúng đề tài trong câu hỏi và lịch sử hiện tại. TUYỆT ĐỐI KHÔNG trả lời lan man, không bịa chi tiết ngoài lề, không tự chuyển sang sáng tác nhạc/thơ/kịch bản. Trả lời thẳng trọng tâm, rõ ràng, từng bước cụ thể; thiếu thông tin thì hỏi lại đúng điểm còn thiếu.
2. KHI CHỈ CHÀO NGẮN ("Alo", "Chào", "Hi", "Hello"): Nếu có công việc đang bàn trước đó thì chào ĐÚNG 1 câu ngắn và hỏi tiếp tục đúng việc đó; nếu chưa có thì chào ĐÚNG 1 câu ngắn gọn, không liệt kê dài dòng."""
def smart_intent_of(msg, mode, has_img, media_files):
    m = (msg or "").lower().strip()
    if mode and mode != "auto": return mode
    if any(k in m for k in ("không sáng tác", "ko sáng tác", "đừng sáng tác", "có sáng tác đâu", "không phải nhạc", "ko viết nhạc", "đừng viết nhạc")): return "chat"
    if re.search(r'(sửa ảnh|thay nền|đổi nền|xóa nền|tách nền|ghép nền|đổi đồ|chỉnh ảnh|vẽ ảnh|tạo ảnh|tạo video|làm video|biến thành video|chuyển thành video)', m) and not any(x in m for x in ("phân tích", "xâu chuỗi", "kiểm tra", "đọc")):
        return "video" if "video" in m else "image_edit"
    if media_files: return "chat"
    if re.search(r'(sáng tác|viết lời|viết bài hát|tạo bài hát|phổ nhạc|làm bài nhạc|viết rap|viết bolero|sáng tác nhạc)', m): return "music"
    return "chat"
def build_smart_sys(intent, sk, media_files, has_img, hist, msg):
    if intent == "music": base = f"{BRAIN_PROMPT}\nTác vụ: music. Điệu: {STYLES.get(sk, 'Tự động')}."
    elif intent in ("image_edit", "video"): base = f"{BRAIN_PROMPT}\nTác vụ: {intent}."
    else:
        base = SMART_BRAIN_PROMPT
        turns = LAST_MEM.get("turns") or []
        if not hist and (msg or "").lower().strip() in GREETS and turns:
            base += "\n\n[CÔNG VIỆC ĐANG BÀN TRƯỚC ĐÓ]:\n" + "\n".join(f"- Hỏi: {t['u']}\n- Đáp: {t['a']}" for t in turns[-3:])
    if media_files or has_img:
        mimes = [m.get("mime", "") for m in (media_files or [])]
        ex = ["\n[PHÂN TÍCH ĐA PHƯƠNG TIỆN]"]
        if any(m.startswith("audio/") for m in mimes): ex.append("- Âm thanh/MP3: Nêu rõ nhạc cụ chính/phụ, giai điệu/BPM/cảm xúc/thể loại, cấu trúc theo mốc MM:SS.")
        if any(m.startswith(("image/", "video/")) for m in mimes) or len(mimes) > 1: ex.append("- Nhiều Ảnh/Video kỹ thuật: Đọc nhãn số/màu dây/thiết bị từng tệp -> xâu chuỗi đối chiếu chéo -> kết luận rõ; thiếu góc quay thì báo rõ.")
        base += "\n".join(ex)
    return base
def stream_gemini_mm(key, sys_p, msg, hist, img, media_files):
    contents = []
    for h in (hist or [])[-16:]:
        if not isinstance(h, dict): continue
        role = "model" if h.get("role") in ("assistant", "model", "bot", "ai") else "user"
        ht = (h.get("text") or h.get("content") or h.get("msg") or h.get("message") or "").strip()
        if not ht and isinstance(h.get("parts"), list): ht = " ".join(p.get("text", "") for p in h["parts"] if isinstance(p, dict)).strip()
        if not ht: continue
        if contents and contents[-1]["role"] == role: contents[-1]["parts"].append({"text": ht})
        else: contents.append({"role": role, "parts": [{"text": ht}]})
    parts = []
    for idx, mf in enumerate(media_files or [], 1):
        parts.append({"text": f"[Tệp #{idx}: {mf.get('name','file')} ({mf.get('mime','')})]"})
        if mf.get("uri"): parts.append({"file_data": {"mime_type": mf["mime"], "file_uri": mf["uri"]}})
        elif mf.get("local_id") in LOCAL_MEDIA_CACHE and os.path.exists(LOCAL_MEDIA_CACHE[mf["local_id"]]):
            parts.append({"inline_data": {"mime_type": mf["mime"], "data": base64.b64encode(open(LOCAL_MEDIA_CACHE[mf["local_id"]], "rb").read()).decode("ascii")}})
    if img and isinstance(img, str) and "," in img and not media_files:
        hdr, b64i = img.split(",", 1)
        parts.append({"inline_data": {"mime_type": hdr.split(";")[0].replace("data:", "") or "image/jpeg", "data": b64i}})
    parts.append({"text": msg or "Phân tích và xâu chuỗi chi tiết các tệp đính kèm."})
    if contents and contents[-1]["role"] == "user": contents[-1]["parts"].extend(parts)
    else: contents.append({"role": "user", "parts": parts})
    body = {"systemInstruction": {"parts": [{"text": sys_p}]}, "contents": contents, "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.4}}
    lc, le = 0, ""
    for mdl in ("gemini-3.5-flash-lite", "gemini-3.6-flash"):
        try:
            r = SESSION.post(f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:streamGenerateContent?alt=sse", headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=body, stream=True, timeout=(6, 45))
            r.encoding = "utf-8"; lc = r.status_code
            if lc in (401, 403): yield f"__ERR__:Key lỗi ({lc})"; return
            if lc != 200:
                le = r.text[:120]
                if lc == 400 and "api key" in le.lower(): yield "__ERR__:Key lỗi (400)"; return
                continue
            got = False
            for rb in r.iter_lines(chunk_size=1, decode_unicode=False):
                if not rb: continue
                raw = rb.decode("utf-8", errors="replace")
                if not raw.startswith("data:"): continue
                pl = raw[5:].strip()
                if pl == "[DONE]": break
                done_sse = False
                try:
                    cands = json.loads(pl).get("candidates") or []
                    for c in cands:
                        for p in ((c.get("content") or {}).get("parts") or []):
                            if not p.get("thought") and p.get("text"): got = True; yield p["text"]
                    if got and any(c.get("finishReason") for c in cands): done_sse = True
                except Exception: pass
                if done_sse: break
            if got: return
        except Exception as e: le = str(e)
    yield f"__ERR__:Gemini HTTP {lc} {le}".strip()
@app.route("/api/upload-media", methods=["POST"])
def api_upload_media():
    now = _time.time()
    for fn in os.listdir(UPLOAD_TMP):
        p = os.path.join(UPLOAD_TMP, fn)
        try:
            if os.path.isfile(p) and now - os.path.getmtime(p) > 7200: os.remove(p)
        except Exception: pass
    ck = os.getenv("AI_CHAT_KEY", "").strip()
    files = request.files.getlist("files")
    if not files: return jsonify({"status": "error", "message": "Chưa chọn tệp!"}), 400
    if not ck: return jsonify({"status": "error", "message": "Chưa có Gemini Key!"}), 400
    out = []
    for f in files:
        on = f.filename or f"media_{_uuid.uuid4().hex[:6]}"
        mime = _guess_mime(on, f.mimetype)
        lid = _uuid.uuid4().hex[:12]
        tp = os.path.join(UPLOAD_TMP, f"{lid}_{os.path.basename(on)}")
        f.save(tp); sz = os.path.getsize(tp)
        uri, gname = "", ""
        if ck.startswith("AIza"):
            try:
                r1 = SESSION.post("https://generativelanguage.googleapis.com/upload/v1beta/files", headers={"x-goog-api-key": ck, "X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start", "X-Goog-Upload-Header-Content-Length": str(sz), "X-Goog-Upload-Header-Content-Type": mime, "Content-Type": "application/json"}, json={"file": {"display_name": on}}, timeout=20)
                uu = r1.headers.get("x-goog-upload-url") or r1.headers.get("X-Goog-Upload-URL")
                if r1.status_code == 200 and uu:
                    r2 = SESSION.post(uu, headers={"Content-Length": str(sz), "X-Goog-Upload-Offset": "0", "X-Goog-Upload-Command": "upload, finalize"}, data=open(tp, "rb"), timeout=(15, 300))
                    fo = (r2.json() or {}).get("file") or {}
                    gname, uri, st = fo.get("name", ""), fo.get("uri", ""), fo.get("state", "ACTIVE")
                    for _ in range(45):
                        if st != "PROCESSING" or not gname: break
                        _time.sleep(1.5)
                        rg = SESSION.get(f"https://generativelanguage.googleapis.com/v1beta/{gname}", headers={"x-goog-api-key": ck}, timeout=15).json()
                        st, uri = rg.get("state", "ACTIVE"), rg.get("uri") or uri
                    if st == "FAILED": uri = ""
            except Exception: uri = ""
        if uri:
            try: os.remove(tp)
            except Exception: pass
            out.append({"name": on, "mime": mime, "uri": uri, "gname": gname})
        elif sz <= 15 * 1024 * 1024:
            LOCAL_MEDIA_CACHE[lid] = tp; out.append({"name": on, "mime": mime, "local_id": lid})
        else:
            try: os.remove(tp)
            except Exception: pass
            return jsonify({"status": "error", "message": f"Không tải được {on} (>15MB cần Key AIza...)"}), 400
    return jsonify({"status": "ok", "files": out})
# === SMART_BRAIN_END ===

@app.route("/api/chat-stream", methods=["POST"])
def api_chat_stream():
    d = request.get_json(silent=True) or {}
    msg, mode, sk, img, hist, mf = (d.get("message") or "").strip(), d.get("mode") or "auto", d.get("music_style") or "auto", d.get("image_data") or "", d.get("history") or [], d.get("media_files") or []
    pro_mode = bool(d.get("pro_mode"))
    if not msg and not img and not mf: return jsonify({"status": "error", "message": "Hãy nhập nội dung!"}), 400
    intent, ck, fk = smart_intent_of(msg, mode, bool(img), mf), os.getenv("AI_CHAT_KEY", "").strip(), os.getenv("FAL_API_KEY", "").strip()
    sys_p = build_smart_sys(intent, sk, mf, bool(img), hist, msg)
    if intent == "chat" and (msg or "").lower().strip() not in GREETS:
        mem = _bc.retrieve_memories(msg, k=3)
        if mem: sys_p += "\n\n" + mem
    def gen():
        yield sse({"intent": intent})
        got, err, full = False, "", ""
        if pro_mode and intent == "chat" and not mf and ck.startswith(("AIza", "AQ.")):
            _, rname, rtemp = _bc.classify_role(msg, False)
            yield sse({"chunk": f"🧠 [{rname} + Verifier]\n\n"})
            ans, ok_py, py_err = _bc.run_verified_pipeline(SESSION, ck, msg, SMART_BRAIN_PROMPT, rname, rtemp)
            if ans:
                got = True; full = ans
                yield sse({"chunk": ans})
        if not got and ck.startswith(("AIza", "AQ.")):
            for c in stream_gemini_mm(ck, sys_p, msg, hist, img, mf):
                if c.startswith("__ERR__:"): err = c[8:]; break
                got = True; full += c; yield sse({"chunk": c})
        if not got:
            off = offline_compose(intent, sk, msg) if intent == "music" else f"[Chưa kết nối AI ({err or 'Thiếu Gemini Key'})]"
            full = off; yield sse({"chunk": off})
        if got and intent == "chat": _save_mem(msg, full)
        out = {"done": True, "intent": intent, "synth": synth_of(sk, msg) if intent == "music" else "", "img_tools": bool(img) and intent == "image_edit", "vid_tools": bool(img) and intent == "video"}
        if not fk and intent in ("video", "image_edit"): out["media_note"] = "⚠️ Cần nhập Key Fal.ai (trong ≡ Menu hoặc biến FAL_API_KEY trên Render) để sửa ảnh / làm video!"
        if fk and intent in ("video", "image_edit"):
            m = re.search(r"MEDIA_PROMPT:\s*(.+)", full)
            mr, me = call_fal(intent, m.group(1).strip() if m else (msg or "cinematic realistic style"), img, fk)
            if mr: out["media"] = mr
            elif me: out["media_note"] = me
        yield sse(out)
    return Response(stream_with_context(gen()), mimetype="text/event-stream", headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})
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


@app.route("/.well-known/assetlinks.json")
def _assetlinks_json():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "assetlinks.json")
    if os.path.exists(p):
        return send_file(p, mimetype="application/json")
    return jsonify([])

@app.route("/privacy")
def _privacy_page():
    return """<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Chính sách bảo mật - AI-Phdam</title></head><body style="font-family:sans-serif;max-width:680px;margin:24px auto;padding:0 16px;line-height:1.6"><h2>Chính sách bảo mật - AI-Phdam Studio</h2><p>Ứng dụng không bán hoặc chia sẻ dữ liệu cá nhân của bạn cho bên thứ ba. Nội dung bạn tải lên chỉ được gửi qua Google Gemini API để xử lý theo yêu cầu của chính bạn.</p></body></html>"""


@app.route("/api/brain-db", methods=["GET", "POST"])
def _api_brain_db():
    if request.method == "GET":
        return jsonify(_bc.load_db())
    d = request.get_json(silent=True) or {}
    act = d.get("action")
    if act == "add":
        _bc.add_memory(d.get("type", "semantic"), d.get("title", ""), d.get("body", ""))
    elif act == "clear":
        _bc.save_db({k: [] for k in _bc.DEFAULT_DB})
    elif act == "import" and isinstance(d.get("db"), dict):
        _bc.save_db(d["db"])
    return jsonify({"status": "ok", "db": _bc.load_db()})


@app.route("/api/download-project/<pid>")
def _download_project_zip(pid):
    if not re.fullmatch(r"p_\d+", pid or ""):
        return jsonify({"status": "error", "message": "Invalid ID"}), 400
    zp = os.path.join(_bc.WS_ROOT, f"{pid}.zip")
    if not os.path.exists(zp):
        return jsonify({"status": "error", "message": "File không tồn tại hoặc đã hết hạn"}), 404
    return send_file(zp, as_attachment=True, download_name=f"AI-Phdam-{pid}.zip")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, threaded=True)
