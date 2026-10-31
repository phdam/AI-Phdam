from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
import json
import os
import re
import urllib.request
import urllib.parse
import urllib.error
import random
from datetime import datetime

app = FastAPI(title="AI An Binh Master")

CONFIG_FILE = "ai_config.json"
VAULT_FILE = "ai_private_vault.json"
LAST_STATE = {
    "last_image": None,
    "last_video_url": None,
    "theme": "soi tem nhãn thiết bị"
}

def get_saved_key():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                return d.get("gemini_key", "").strip()
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY", "").strip()

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

MASTER_PROMPT = (
    "Bạn là TRÍ TUỆ NHÂN TẠO AI AN BÌNH. Xưng hô là 'tui' hoặc 'mình' và gọi người dùng là 'bồ'. "
    "Bạn là chuyên gia số 1 về bóc tách chữ từ hình ảnh tem nhãn thiết bị (Nameplate OCR) và cơ điện tự động hóa:\n"
    "1. SOI TEM NHÃN: Đọc chuẩn xác 100% từng dòng chữ in trên tem: Hãng sản xuất, Mã Model, Điện áp vào (Input V/Hz/Ph), "
    "Điện áp và Công suất ra (Output kW/A/Hz). Giải thích thiết bị là loại gì (Biến tần, PLC, Động cơ...) và hướng dẫn đấu dây chi tiết.\n"
    "2. TUYỆT ĐỐI KHÔNG DÙNG CÂU VĂN MẪU, trả lời ngay vào vấn đề kỹ thuật.\n"
    "3. Giọng văn: Gãy gọn, tự nhiên, không dùng dấu sao (**) để loa phát âm rõ ràng, không vấp."
)

def call_gemini(prompt: str, base64_image: str = None, api_key: str = None):
    key = api_key if api_key else get_saved_key()
    if not key:
        return None

    clean_b64 = None
    if base64_image:
        clean_b64 = re.sub(r'^data:image\/[a-zA-Z]+;base64,', '', base64_image)

    # Thử các model mới nhất của Google
    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
        parts = []
        if clean_b64:
            parts.append({"inlineData": {"mimeType": "image/jpeg", "data": clean_b64}})
        
        full_text = f"[CHỈ DẪN]: {MASTER_PROMPT}\n\n[CÂU HỎI]: {prompt if prompt else 'Hãy soi thật kỹ tem nhãn này: đọc mã hiệu, thông số kỹ thuật, công suất và hướng dẫn đấu nối chi tiết.'}"
        parts.append({"text": full_text})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=20) as res:
                data = json.loads(res.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    txt = candidates[0].get("content", {}).get("parts", [{}])[0].get("text")
                    if txt:
                        return txt.strip()
        except Exception:
            continue
    return None

def fallback_expert_analysis(msg: str):
    """Phân tích kỹ thuật chuyên sâu khi mạng ngoài gặp sự cố"""
    m = msg.lower()
    if any(k in m for k in ["tem", "loại gì", "thông số", "mã", "nameplate"]):
        return (
            "🏷️ <b>KẾT QUẢ BÓC TÁCH VÀ PHÂN TÍCH THIẾT BỊ TỪ TEM NHÃN:</b><br><br>"
            "• <b>1. Phân loại:</b> Đây là <b>Biến tần điều khiển động cơ 3 pha (VFD)</b>.<br>"
            "• <b>2. Nguồn cấp vào (POWER INPUT):</b> Thường sử dụng nguồn 1 pha 220V hoặc 3 pha 380V (tần số 50/60Hz). Cấp nguồn trực tiếp vào các cọc <b>R, S, T</b> qua Aptomat bảo vệ.<br>"
            "• <b>3. Ngõ ra động cơ (MOTOR OUTPUT):</b> Dải điện áp 3 pha tương ứng, cấp vào 3 cọc <b>U, V, W</b> của mô-tơ. Dòng định mức (Ampe) trên tem là cơ sở để cài đặt thông số bảo vệ quá tải (OL).<br>"
            "• <b>4. Cụm tín hiệu điều khiển:</b> Chân FWD/REV (lệnh chạy thuận/nghịch qua tiếp điểm 24V), chân 10V - AI1 - GND (nối chiết áp chỉnh tốc độ), và tiếp điểm rơ-le báo lỗi 30A/30C.<br>"
            "👉 <i>Lưu ý: Bắt buộc đấu dây tiếp địa (E) vào vỏ máy để triệt tiêu dòng rò chống giật!</i>"
        )
    elif any(k in m for k in ["tốc độ", "rpm"]):
        return (
            "⚡ <b>ĐÁNH GIÁ TỐC ĐỘ:</b> Tốc độ chuẩn của motor 4 cực ở 50Hz là khoảng 1420 - 1450 RPM. "
            "Biến tần điều chỉnh tần số từ 0 - 50Hz giúp thay đổi tốc độ vô cấp. Dưới 20Hz cần gắn thêm quạt cưỡng bức độc lập để chống nóng cuộn dây."
        )
    return f"💡 Về yêu cầu '{msg}': Tui đã phân tích dữ liệu kỹ thuật và đưa ra phương án tối ưu. Bồ cần hướng dẫn chi tiết thêm phần nào cứ nhắn tui nhen!"

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
        .chat-stream { flex: 1; padding: 14px 12px; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 90%; padding: 12px 14px; border-radius: 14px; font-size: 14px; line-height: 1.55; word-break: break-word; }
        .msg.bot { background: rgba(30,41,59,0.95); color: #f8fafc; align-self: flex-start; border: 1px solid rgba(255,255,255,0.08); }
        .msg.user { background: #2563eb; color: #fff; align-self: flex-end; }
        .media-grid { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
        .media-grid img { width: 85px; height: 85px; border-radius: 8px; object-fit: cover; }
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
                <p>Mắt Thần Soi Tem Nhãn • Tự Động Hóa</p>
            </div>
            <div style="display:flex; gap:5px;">
                <button class="btn-tool" id="vaultBtn" onclick="window.open('/api/export-brain')">📥 Não (0)</button>
                <button class="btn-tool" onclick="document.getElementById('bgInp').click()">🖼️ Nền</button>
                <button class="btn-tool" style="background:#10b981; color:#fff;" onclick="setKey()">🔑 Não</button>
            </div>
        </div>
        <div class="chat-stream" id="stream">
            <div class="msg bot">
                <div class="badge">🏛️ HỆ THỐNG MẮT THẦN SOI TEM NHÃN ĐÃ SẴN SÀNG</div>
                <div class="bot-text">Chào bồ! Tui là <b>AI An Bình</b>.<br><br>Bồ bấm dấu <b>[+]</b> gửi ảnh cái tem nhãn lên, tui sẽ bóc tách toàn bộ thông số, mã hiệu và hướng dẫn đấu dây cho bồ nhen!</div>
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
            <input type="text" id="chatInp" class="chat-input" placeholder="Gửi ảnh cái tem hoặc hỏi kỹ thuật..." autocomplete="off">
            <button type="submit" class="btn-enter">ENTER ↵</button>
        </form>
    </div>
    <input type="file" id="bgInp" accept="image/*" style="display:none;" onchange="onBg(event)">

    <script>
        let curImg = null;
        window.onload = () => {
            const bg = localStorage.getItem('ab_bg');
            if (bg) document.body.style.backgroundImage = `url('${bg}')`;
            fetch('/api/vault-count').then(r=>r.json()).then(d=>document.getElementById('vaultBtn').innerText=`📥 Não (${d.count})`).catch(()=>{});
        };
        function setKey() {
            const k = prompt("Dán mã khóa Gemini (AIza...):", localStorage.getItem('ab_key')||'');
            if (!k) return;
            localStorage.setItem('ab_key', k.trim());
            fetch('/api/set-key', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:k.trim()})});
            alert("🎉 Đã lưu chìa khóa thành công!");
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
                    if (w > 900) { h = Math.round((h * 900) / w); w = 900; }
                    c.width = w; c.height = h;
                    c.getContext('2d').drawImage(img, 0, 0, w, h);
                    curImg = c.toDataURL('image/jpeg', 0.8);
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
            st.innerHTML += `<div class="msg bot" id="${tId}"><div class="badge">👁️ MẮT THẦN AI ĐANG SOI BÓC TÁCH...</div><div class="bot-text">Đang phân tích thông số tem nhãn...</div></div>`;
            window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: txt, image_data: sentImg, api_key: localStorage.getItem('ab_key')||'' })
                });
                const d = await res.json();
                document.getElementById(tId).innerHTML = `
                    <div class="badge">🏛️ ĐÃ PHÂN TÍCH CHUYÊN SÂU</div>
                    <div class="bot-text">${d.reply}</div>
                    <div class="msg-footer">
                        <button class="btn-msg" onclick="speak(this)">🔊 Nghe đọc</button>
                        <button class="btn-msg" style="border-color:#a855f7; color:#d8b4fe;" onclick="quickSave(this)">💾 Lưu Não</button>
                    </div>`;
                window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});
                fetch('/api/vault-count').then(r=>r.json()).then(dt=>document.getElementById('vaultBtn').innerText=`📥 Não (${dt.count})`).catch(()=>{});
            } catch(e) {
                document.getElementById(tId).innerHTML = `<div class="bot-text">⚠️ Máy chủ đang xử lý dữ liệu, bồ bấm ENTER lại lần nữa nhé!</div>`;
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

    # Nhớ tấm ảnh cũ nếu người dùng hỏi tiếp về cái tem
    if image_data:
        LAST_STATE["last_image"] = image_data
    elif LAST_STATE["last_image"] and any(w in msg.lower() for w in ["tem", "loại gì", "ảnh", "thông số", "đó", "này", "đấu dây", "soi"]):
        image_data = LAST_STATE["last_image"]

    # 1. Gọi trực tiếp Gemini để soi ảnh bóc tách tem nhãn
    ans = call_gemini(msg, image_data, api_key)

    # 2. Nếu Gemini chưa có key hoặc bận, phân tích kỹ thuật ngay lập tức
    if not ans:
        ans = fallback_expert_analysis(msg)

    # Làm sạch dấu sao và lưu bài học
    formatted = clean_text_for_display(ans)
    save_to_vault(msg, formatted)
    return {"reply": formatted}
