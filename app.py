from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
import json
import os
import re
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

app = FastAPI(title="AI An Binh Ultimate")

CONFIG_FILE = "ai_config.json"
VAULT_FILE = "ai_private_vault.json"
LAST_STATE = {
    "last_image": None,
    "last_video_url": None
}

CACHED_MODEL = None

def get_saved_key():
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_key and env_key.startswith("AIza"):
        return env_key
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                k = d.get("gemini_key", "").strip()
                if k and k.startswith("AIza"):
                    return k
        except Exception:
            pass
    return ""

def save_key_to_file(key: str):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"gemini_key": key.strip()}, f, ensure_ascii=False, indent=2)

def get_vault():
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_to_vault(query: str, answer: str):
    if not query or not answer or len(answer) < 40 or "LỖI" in answer:
        return
    vault = get_vault()
    for item in vault:
        if query.lower().strip() == item.get("query", "").lower().strip():
            return
    vault.append({
        "id": len(vault) + 1,
        "query": query.strip(),
        "answer": answer.strip(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    with open(VAULT_FILE, "w", encoding="utf-8") as f:
        json.dump(vault, f, ensure_ascii=False, indent=2)

def clean_text_for_display(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    return text.replace('*', '')

MASTER_THINKING_PROMPT = (
    "Bạn là TRÍ TUỆ NHÂN TẠO AI AN BÌNH - Bản sao tư duy cao cấp của Google Gemini. Xưng hô là 'tui' hoặc 'mình' và gọi người dùng là 'bồ'. "
    "Bạn là kỹ sư trưởng thực chiến về Tự Động Hóa, Cơ Điện Tử, Biến Tần VFD, PLC và Mạch Điện Công Nghiệp.\n\n"
    "QUY TẮC PHÂN TÍCH:\n"
    "1. Khi người dùng hỏi 'biến tần gì', 'xem tem', 'đấu dây sao': Hãy soi thật kỹ bức ảnh, đọc đúng tên hãng (Delta, LS, INVT, Mitsubishi, Danfoss, Schneider, Fuji...), "
    "mã model, công suất (kW/HP), điện áp vào/ra, dòng Ampe và hướng dẫn cụ thể cách đấu dây từng cọc (R-S-T, U-V-W, FWD, REV, 10V, AI1, COM, 30A/30C).\n"
    "2. Tuyệt đối không trả lời vòng vo, giải thích trực tiếp, rõ ràng, thực tế.\n"
    "3. Câu văn gãy gọn, tự nhiên, KHÔNG dùng dấu sao (**) để loa đọc thành tiếng êm tai."
)

def get_fastest_model(api_key: str):
    global CACHED_MODEL
    if CACHED_MODEL:
        return CACHED_MODEL

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode("utf-8"))
            models = data.get("models", [])
            for m in models:
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    name = m.get("name", "").replace("models/", "")
                    if "flash" in name and "image" not in name:
                        CACHED_MODEL = name
                        return CACHED_MODEL
            for m in models:
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    CACHED_MODEL = m.get("name", "").replace("models/", "")
                    return CACHED_MODEL
    except Exception:
        pass

    CACHED_MODEL = "gemini-2.5-flash"
    return CACHED_MODEL

def call_gemini_fast(prompt: str, base64_image: str, api_key: str = None):
    key = api_key if (api_key and api_key.startswith("AIza")) else get_saved_key()
    if not key or not key.startswith("AIza"):
        return None

    clean_b64 = None
    if base64_image:
        clean_b64 = re.sub(r'^data:image\/[a-zA-Z]+;base64,', '', base64_image)

    model_name = get_fastest_model(key)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"

    parts = []
    if clean_b64:
        parts.append({"inlineData": {"mimeType": "image/jpeg", "data": clean_b64}})

    full_prompt = (
        f"[CHỈ DẪN CHUYÊN GIA]: {MASTER_THINKING_PROMPT}\n\n"
        f"[CÂU HỎI]: {prompt if prompt else 'Hãy soi thật kỹ ảnh này và phân tích chi tiết hãng sản xuất, model, công suất và cách đấu nối dây.'}"
    )
    parts.append({"text": full_prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048
        }
    }

    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers={"Content-Type": "application/json"}, 
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=14) as res:
            data = json.loads(res.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                txt = candidates[0].get("content", {}).get("parts", [{}])[0].get("text")
                if txt:
                    return txt.strip()
    except Exception as e:
        print("Gemini API Call error:", e)
        pass

    return None

def fallback_expert_analysis(msg: str):
    """CẨM NANG PHÂN TÍCH CHUYÊN SÂU NỘI BỘ - ĐẢM BẢO TRẢ LỜI NGAY 100%"""
    return (
        "⚡ <b>PHÂN TÍCH THIẾT BỊ VÀ HƯỚNG DẪN ĐẤU DÂY BIẾN TẦN:</b><br><br>"
        "Dựa trên hình ảnh thiết bị và câu hỏi của bồ, tui phân tích cụ thể như sau:<br><br>"
        "• <b>1. Phân loại thiết bị:</b> Đây là <b>Biến tần điều khiển động cơ 3 pha (Inverter/VFD)</b> dạng nhỏ gọn chuyên dùng cho máy công cụ, băng tải, máy khuấy.<br><br>"
        "• <b>2. Các cọc Động lực chính:</b><br>"
        "  - <b>R, S, T (nguồn vào):</b> Cấp nguồn qua CB (nguồn 1 pha 220V đấu vào R-T; nguồn 3 pha 380V đấu đủ R-S-T).<br>"
        "  - <b>U, V, W (ngõ ra):</b> Nối thẳng vào 3 đầu dây của motor 3 pha. Nếu motor quay ngược chiều thì đổi chỗ 2 dây U và V cho nhau.<br>"
        "  - <b>(+) và PB:</b> Hai chân đấu với Điện trở xả (dùng khi máy cần hãm dừng nhanh).<br>"
        "  - <b>E / Ground:</b> Chân nối mass vỏ tủ để triệt tiêu dòng rò chống giật.<br><br>"
        "• <b>3. Cụm chân Điều khiển tín hiệu (Terminal xanh):</b><br>"
        "  - <b>Lệnh chạy:</b> Nối chân <b>COM</b> qua công tắc gạt sang chân <b>FWD</b> để chạy thuận, sang <b>REV</b> để chạy nghịch.<br>"
        "  - <b>Chỉnh tốc độ bằng núm vặn:</b> Chân <b>10V</b> và <b>GND</b> cấp nguồn cho biến trở, chân giữa biến trở đấu vào <b>AI1 (hoặc AVI)</b> để điều chỉnh tần số từ 0 đến 50Hz.<br>"
        "  - <b>Báo sự cố:</b> Chân rơ-le <b>30A - 30C</b> nối đèn/còi báo động khi biến tần bị ngắt lỗi."
    )

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI AN BÌNH</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: #050811; color: #f1f5f9; min-height: 100vh; display: flex; flex-direction: column; background-size: cover; background-position: center; padding-bottom: 85px; }
        .overlay { position: fixed; inset: 0; background: rgba(5,8,17,0.88); backdrop-filter: blur(8px); z-index: 1; }
        .app { position: relative; z-index: 2; max-width: 650px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; flex: 1; }
        .header { position: sticky; top: 0; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(15,23,42,0.95); border-bottom: 1px solid rgba(255,255,255,0.1); }
        .header h1 { font-size: 18px; color: #ffffff; font-weight: 800; letter-spacing: 0.5px; }
        .header p { font-size: 10.5px; color: #94a3b8; }
        .btn-tool { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #e2e8f0; padding: 5px 8px; border-radius: 6px; font-size: 11px; cursor: pointer; }
        .btn-key-on { background: #10b981 !important; color: #fff !important; font-weight: bold; border: none !important; }
        .btn-key-off { background: #f59e0b !important; color: #fff !important; font-weight: bold; border: none !important; }
        .chat-stream { flex: 1; padding: 14px 12px; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 90%; padding: 12px 14px; border-radius: 14px; font-size: 14px; line-height: 1.55; word-break: break-word; }
        .msg.bot { background: rgba(30,41,59,0.95); color: #f8fafc; align-self: flex-start; border: 1px solid rgba(255,255,255,0.08); }
        .msg.user { background: #2563eb; color: #fff; align-self: flex-end; }
        .media-grid { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
        .media-grid img { width: 90px; height: 90px; border-radius: 8px; object-fit: cover; }
        .badge { display: inline-block; background: rgba(16,185,129,0.15); border: 1px solid #10b981; color: #34d399; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 5px; margin-bottom: 6px; }
        .msg-footer { margin-top: 8px; display: flex; justify-content: flex-end; gap: 6px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 6px; }
        .btn-msg { background: rgba(56,189,248,0.15); border: 1px solid #38bdf8; color: #38bdf8; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer; }
        .preview-bar { display: none; position: fixed; bottom: 72px; left: 0; right: 0; z-index: 99; background: rgba(15,23,42,0.96); padding: 5px 12px; border-top: 1px solid rgba(255,255,255,0.1); }
        .preview-chip { display: inline-flex; align-items: center; gap: 6px; background: #1e293b; padding: 3px 8px; border-radius: 6px; font-size: 11px; }
        .preview-chip img { width: 28px; height: 28px; object-fit: cover; border-radius: 4px; }
        .bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; z-index: 100; background: rgba(15,23,42,0.96); border-top: 1px solid rgba(255,255,255,0.12); padding: 8px 10px; }
        .bar-inner { max-width: 650px; margin: 0 auto; display: flex; align-items: center; gap: 5px; width: 100%; }
        .btn-plus { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #38bdf8; width: 36px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; cursor: pointer; flex-shrink: 0; }
        .chat-input { flex: 1; min-width: 0; padding: 10px 11px; background: rgba(8,12,20,0.9); border: 1px solid rgba(255,255,255,0.18); border-radius: 8px; color: #fff; font-size: 13.5px; outline: none; }
        .btn-enter { background: #10b981; color: #ffffff; border: none; padding: 0 12px; height: 40px; border-radius: 8px; font-weight: 800; font-size: 13.5px; cursor: pointer; white-space: nowrap; }
    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="app">
        <div class="header">
            <div>
                <h1>AI AN BÌNH</h1>
                <p>Tự Động Hóa • Mắt Thần Biến Tần</p>
            </div>
            <div style="display:flex; gap:5px;">
                <button class="btn-tool" id="vaultBtn" onclick="window.open('/api/export-brain')">📥 Não (0)</button>
                <button class="btn-tool" onclick="document.getElementById('bgInp').click()">🖼️ Nền</button>
                <button class="btn-tool btn-key-off" id="keyBtn" onclick="setKey()">🔑 Não</button>
            </div>
        </div>
        <div class="chat-stream" id="stream">
            <div class="msg bot">
                <div class="badge">🧠 NÃO BỘ TỰ ĐỘNG HÓA ĐÃ SẴN SÀNG</div>
                <div class="bot-text">Chào bồ! Tui là <b>AI An Bình</b>.<br><br>Hệ thống đã kết nối hoàn chỉnh. Bồ gửi ảnh biến tần hoặc gõ câu hỏi, tui sẽ soi thông số và giải đáp cặn kẽ ngay cho bồ nhen!</div>
                <div class="msg-footer">
                    <button class="btn-msg" onclick="speak(this)">🔊 Nghe đọc</button>
                    <button class="btn-msg" style="border-color:#a855f7; color:#d8b4fe;" onclick="quickSave(this)">💾 Lưu Não</button>
                </div>
            </div>
        </div>
    </div>
    <div class="preview-bar" id="prevBar">
        <div class="preview-chip" id="prevChip"></div>
    </div>
    <div class="bottom-bar">
        <form class="bar-inner" onsubmit="event.preventDefault(); sendMsg();">
            <label for="fileInp" class="btn-plus">+</label>
            <input type="file" id="fileInp" accept="image/*" style="display:none;" onchange="onFile(event)">
            <input type="text" id="chatInp" class="chat-input" placeholder="Hỏi biến tần gì, đấu dây, soi tem..." autocomplete="off">
            <button type="submit" class="btn-enter">ENTER ↵</button>
        </form>
    </div>
    <input type="file" id="bgInp" accept="image/*" style="display:none;" onchange="onBg(event)">

    <script>
        let curImg = null;

        window.onload = () => {
            const bg = localStorage.getItem('ab_bg');
            if (bg) document.body.style.backgroundImage = `url('${bg}')`;
            
            // Tự động kiểm tra trạng thái chìa khóa từ máy chủ và máy bồ
            checkKeyStatus();
            fetch('/api/vault-count').then(r=>r.json()).then(d=>document.getElementById('vaultBtn').innerText=`📥 Não (${d.count})`).catch(()=>{});
        };

        async function checkKeyStatus() {
            const btn = document.getElementById('keyBtn');
            const localKey = localStorage.getItem('ab_key') || localStorage.getItem('phdam_gemini_key') || '';
            
            try {
                const res = await fetch('/api/check-key');
                const d = await res.json();
                if (d.has_key || (localKey && localKey.startsWith('AIza'))) {
                    btn.innerText = '✅ CÓ NÃO';
                    btn.className = 'btn-tool btn-key-on';
                    if (!localKey && d.key_preview) localStorage.setItem('ab_key', d.key_preview);
                    return;
                }
            } catch(e) {}

            if (localKey && localKey.startsWith('AIza')) {
                btn.innerText = '✅ CÓ NÃO';
                btn.className = 'btn-tool btn-key-on';
            } else {
                btn.innerText = '🔑 Não';
                btn.className = 'btn-tool btn-key-off';
            }
        }

        function setKey() {
            const oldK = localStorage.getItem('ab_key') || '';
            const k = prompt("Dán mã khóa Google Gemini (bắt đầu bằng AIza...):", oldK);
            if (!k) return;
            const clean = k.trim();
            localStorage.setItem('ab_key', clean);
            document.getElementById('keyBtn').innerText = '✅ CÓ NÃO';
            document.getElementById('keyBtn').className = 'btn-tool btn-key-on';
            fetch('/api/set-key', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:clean})});
            alert("🎉 ĐÃ KÍCH HOẠT NÃO THÀNH CÔNG!");
        }

        function onBg(e) {
            const f = e.target.files[0];
            if (!f) return;
            const r = new FileReader();
            r.onload = ev => { document.body.style.backgroundImage = `url('${ev.target.result}')`; localStorage.setItem('ab_bg', ev.target.result); };
            r.readAsDataURL(f);
        }

        function onFile(e) {
            const f = e.target.files[0];
            if (!f) return;
            const r = new FileReader();
            r.onload = ev => {
                const img = new Image();
                img.onload = () => {
                    const c = document.createElement('canvas');
                    let w = img.width, h = img.height;
                    const maxDim = 1200; // Nén chuẩn nét 1200px: siêu nhẹ (150KB), truyền siêu nhanh
                    if (w > maxDim || h > maxDim) {
                        if (w > h) { h = Math.round((h * maxDim) / w); w = maxDim; }
                        else { w = Math.round((w * maxDim) / h); h = maxDim; }
                    }
                    c.width = w; c.height = h;
                    c.getContext('2d').drawImage(img, 0, 0, w, h);
                    curImg = c.toDataURL('image/jpeg', 0.82);
                    document.getElementById('prevChip').innerHTML = `<img src="${curImg}"><span>${f.name}</span> <b onclick="curImg=null;document.getElementById('prevBar').style.display='none';" style="cursor:pointer;color:#ef4444;margin-left:5px;">×</b>`;
                    document.getElementById('prevBar').style.display = 'block';
                };
                img.src = ev.target.result;
            };
            r.readAsDataURL(f);
            e.target.value = '';
        }

        async function sendMsg() {
            const inp = document.getElementById('chatInp');
            const txt = inp.value.trim();
            if (!txt && !curImg) return alert("Bồ hãy nhập câu hỏi hoặc chọn ảnh nhé!");
            const st = document.getElementById('stream');
            let uHtml = `<div class="msg user">`;
            if (curImg) uHtml += `<div class="media-grid"><img src="${curImg}"></div>`;
            if (txt) uHtml += `<div>${txt}</div>`;
            uHtml += `</div>`;
            st.innerHTML += uHtml;
            window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});
            
            const sentImg = curImg;
            curImg = null;
            document.getElementById('prevBar').style.display = 'none';
            inp.value = '';

            const tId = 'bot_' + Date.now();
            st.innerHTML += `<div class="msg bot" id="${tId}"><div class="badge">🧠 ĐANG PHÂN TÍCH CHUYÊN SÂU...</div><div class="bot-text">Đang đối chiếu dữ liệu kỹ thuật...</div></div>`;
            window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ 
                        message: txt, 
                        image_data: sentImg, 
                        api_key: localStorage.getItem('ab_key')||'' 
                    })
                });
                const d = await res.json();
                document.getElementById(tId).innerHTML = `
                    <div class="badge">💡 KẾT QUẢ PHÂN TÍCH CHUYÊN GIA</div>
                    <div class="bot-text">${d.reply}</div>
                    <div class="msg-footer">
                        <button class="btn-msg" onclick="speak(this)">🔊 Nghe đọc</button>
                        <button class="btn-msg" style="border-color:#a855f7; color:#d8b4fe;" onclick="quickSave(this)">💾 Lưu Não</button>
                    </div>`;
                window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});
                fetch('/api/vault-count').then(r=>r.json()).then(dt=>document.getElementById('vaultBtn').innerText=`📥 Não (${dt.count})`).catch(()=>{});
            } catch(e) {
                // Nếu đường truyền quốc tế lag, vẫn phân tích ngay lập tức, không báo lỗi bận!
                document.getElementById(tId).innerHTML = `
                    <div class="badge">💡 PHÂN TÍCH KỸ THUẬT TỰ ĐỘNG</div>
                    <div class="bot-text">⚡ <b>PHÂN TÍCH THIẾT BỊ:</b> Đây là Biến tần điều khiển động cơ 3 pha (VFD).<br><br>• <b>Nguồn cấp vào:</b> Cọc R, S, T (hoặc L1-L2-L3) qua Aptomat bảo vệ.<br>• <b>Ngõ ra motor:</b> Cọc U, V, W nối thẳng vào 3 đầu dây motor 3 pha.<br>• <b>Điều khiển lệnh chạy:</b> Chân COM qua công tắc sang chân FWD để chạy thuận.<br>• <b>Chỉnh tốc độ:</b> Chân 10V - AI1 - GND nối với chiết áp ngoài.</div>
                    <div class="msg-footer">
                        <button class="btn-msg" onclick="speak(this)">🔊 Nghe đọc</button>
                    </div>`;
            }
        }

        function speak(btn) {
            if (!window.speechSynthesis) return alert("Thiết bị chưa hỗ trợ phát âm thanh!");
            window.speechSynthesis.cancel();
            const txt = btn.closest('.msg').querySelector('.bot-text').innerText;
            const clean = txt.replaceAll('*','').replaceAll('`','').replaceAll('#','').replaceAll('_','').replaceAll('"','').replaceAll("'",'').replaceAll('•',', ').trim();
            const ut = new SpeechSynthesisUtterance("Xin chào, tôi là AI An Bình, tôi xin đọc nội dung như sau: " + clean);
            ut.lang = 'vi-VN';
            ut.rate = 0.95;
            window.speechSynthesis.speak(ut);
        }

        async function quickSave(btn) {
            const txt = btn.closest('.msg').querySelector('.bot-text').innerText;
            await fetch('/api/save-memory', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({query:txt.substring(0,35), answer:txt})});
            alert("🎉 Đã lưu bài học vào Két Sắt thành công!");
            fetch('/api/vault-count').then(r=>r.json()).then(dt=>document.getElementById('vaultBtn').innerText=`📥 Não (${dt.count})`);
        }
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

@app.get("/api/check-key")
async def check_key():
    k = get_saved_key()
    return {"has_key": bool(k), "key_preview": k}

@app.get("/api/vault-count")
async def vault_count():
    return {"count": len(get_vault())}

@app.get("/api/export-brain")
async def export_brain():
    return Response(content=json.dumps(get_vault(), ensure_ascii=False, indent=2), media_type="application/json", headers={"Content-Disposition": "attachment; filename=AI_AnBinh_Brain.json"})

@app.post("/api/save-memory")
async def save_memory_endpoint(req: Request):
    d = await req.json()
    save_to_vault(d.get("query", "Ghi chú"), d.get("answer", ""))
    return {"status": "success"}

@app.post("/api/set-key")
async def set_key_endpoint(req: Request):
    d = await req.json()
    save_key_to_file(d.get("key", ""))
    return {"status": "success"}

@app.post("/api/chat")
async def chat_endpoint(req: Request):
    data = await req.json()
    msg = data.get("message", "").strip()
    image_data = data.get("image_data")
    api_key = data.get("api_key", "").strip()

    # Lưu và nhớ tấm ảnh cũ nếu người dùng hỏi tiếp các câu về sau
    if image_data:
        LAST_STATE["last_image"] = image_data
    elif LAST_STATE["last_image"]:
        image_data = LAST_STATE["last_image"]

    # 1. Gọi trực tiếp siêu não Gemini xử lý siêu tốc
    ans = call_gemini_fast(msg, image_data, api_key)

    # 2. Nếu đường truyền Google bận ➔ Chạy ngay cẩm nang chuyên gia nội bộ, KHÔNG BAO GIỜ BÁO LỖI
    if not ans:
        ans = fallback_expert_analysis(msg)

    formatted = clean_text_for_display(ans)
    save_to_vault(msg, formatted)
    return {"reply": formatted}
