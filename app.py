from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import os
import re
import urllib.request
import urllib.parse
import random

app = FastAPI(title="AI Phdam Gemini Clone")

CONFIG_FILE = "ai_config.json"

def get_api_key():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                return d.get("gemini_key", "").strip()
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY", "").strip()

def save_api_key(key: str):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"gemini_key": key.strip()}, f, ensure_ascii=False, indent=2)

MASTER_PERSONA = (
    "Bạn là SIÊU NHÂN AI PHDAM - bản sao trí tuệ hoàn hảo của Google Gemini. "
    "Bạn xưng hô thân mật là 'mình' hoặc 'tôi' và gọi người dùng là 'bồ'. "
    "Bạn sở hữu toàn bộ kho tàng tri thức khổng lồ của nhân loại: khoa học tự nhiên, sinh học động thực vật, cơ điện tử, tự động hóa, biến tần VFD, kỹ thuật và đời sống. "
    "Phong cách: Siêu thông thái, tư duy logic đa chiều, giải thích bản chất, phân tích ưu nhược điểm, đưa ra giải pháp tối ưu và hướng dẫn từng bước. "
    "Khi người dùng gửi ảnh: Soi thật kỹ từng pixel, đọc đúng con số, con chữ, nhận dạng chính xác thiết bị, con vật, hiện tượng. Tuyệt đối không trả lời chung chung máy móc."
)

def ask_gemini_brain(prompt: str, base64_image: str = None, api_key: str = None):
    """Gọi trực tiếp siêu não bộ Google Gemini API chính hãng"""
    key = api_key if api_key else get_api_key()
    if not key:
        return None

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
        headers = {"Content-Type": "application/json"}
        
        parts = []
        if base64_image:
            # Tách header base64 nếu có
            clean_b64 = re.sub(r'^data:image\/[a-zA-Z]+;base64,', '', base64_image)
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": clean_b64
                }
            })
            
        task_prompt = prompt if prompt else "Hãy quan sát thật kỹ bức ảnh này và phân tích chi tiết bằng tiếng Việt: đọc rõ từng con số, con chữ, linh kiện hoặc đối tượng bạn thấy."
        parts.append({"text": task_prompt})

        payload = {
            "contents": [{"parts": parts}],
            "system_instruction": {
                "parts": [{"text": MASTER_PERSONA}]
            },
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048
            }
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=20) as res:
            res_json = json.loads(res.read().decode("utf-8"))
            candidates = res_json.get("candidates", [])
            if candidates:
                content_parts = candidates[0].get("content", {}).get("parts", [])
                if content_parts:
                    return content_parts[0].get("text", "").strip()
    except Exception as e:
        print("Gemini API Error:", e)
        pass

    return None

def fallback_brain(prompt: str):
    """Kênh dự phòng nếu chưa cài khóa Gemini"""
    p_clean = re.sub(r'[\r\n\t]+', ' ', prompt).strip()
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(p_clean[:400])}?model=openai"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as res:
            out = res.read().decode("utf-8").strip()
            if out and len(out) > 10 and not out.startswith("<"):
                return out
    except Exception:
        pass
    return None

HTML_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Siêu Nhân AI Phdam - Bản Sao Gemini</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        
        body { 
            background: #060911; 
            color: #f1f5f9; 
            min-height: 100vh; 
            display: flex; 
            flex-direction: column; 
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            padding-bottom: 90px;
        }

        .backdrop-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(6, 9, 17, 0.88);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            z-index: 1;
        }

        .app-container {
            position: relative;
            z-index: 2;
            display: flex;
            flex-direction: column;
            max-width: 650px;
            width: 100%;
            margin: 0 auto;
            flex: 1;
        }

        .header {
            position: sticky;
            top: 0;
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            background: rgba(15, 23, 42, 0.94);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        .header-title h1 {
            font-size: 17px;
            background: linear-gradient(135deg, #00f2fe, #4facfe, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        .header-title p {
            font-size: 11px;
            color: #94a3b8;
        }
        .header-actions {
            display: flex;
            gap: 6px;
        }
        .btn-tool {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #e2e8f0;
            padding: 5px 9px;
            border-radius: 8px;
            font-size: 11px;
            cursor: pointer;
        }
        .btn-key {
            background: linear-gradient(135deg, #f59e0b, #ef4444);
            color: #fff;
            border: none;
            font-weight: bold;
        }

        .chat-stream {
            flex: 1;
            padding: 14px 12px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .msg {
            max-width: 90%;
            padding: 12px 15px;
            border-radius: 14px;
            font-size: 14px;
            line-height: 1.55;
            word-break: break-word;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        }
        .msg.bot {
            background: rgba(30, 41, 59, 0.95);
            color: #f8fafc;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .msg.user {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #fff;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }
        .user-media-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 6px;
        }
        .user-media-grid img, .user-media-grid video {
            width: 90px;
            height: 90px;
            border-radius: 8px;
            object-fit: cover;
        }
        .speak-btn {
            background: none;
            border: none;
            font-size: 14px;
            cursor: pointer;
            margin-left: 6px;
            vertical-align: middle;
        }

        .attachment-preview-bar {
            display: none;
            position: fixed;
            bottom: 74px;
            left: 0; right: 0;
            z-index: 99;
            background: rgba(15, 23, 42, 0.96);
            padding: 6px 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        .preview-scroll-row {
            max-width: 650px;
            margin: 0 auto;
            display: flex;
            gap: 8px;
            overflow-x: auto;
        }
        .preview-item-chip {
            display: flex;
            align-items: center;
            gap: 6px;
            background: #1e293b;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 11px;
            flex-shrink: 0;
        }
        .preview-item-chip img, .preview-item-chip video {
            width: 32px;
            height: 32px;
            object-fit: cover;
            border-radius: 4px;
        }
        .btn-chip-remove {
            background: none;
            border: none;
            color: #ef4444;
            font-weight: bold;
            font-size: 14px;
            cursor: pointer;
        }

        .bottom-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 100;
            background: rgba(15, 23, 42, 0.96);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border-top: 1px solid rgba(255, 255, 255, 0.12);
            padding: 8px 10px calc(8px + env(safe-area-inset-bottom, 8px));
        }
        .bottom-bar-inner {
            max-width: 650px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            gap: 6px;
            width: 100%;
        }
        
        .btn-icon-label {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #38bdf8;
            width: 36px;
            height: 42px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            font-weight: bold;
            cursor: pointer;
            flex-shrink: 0;
        }

        .btn-icon {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #38bdf8;
            width: 36px;
            height: 42px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            cursor: pointer;
            flex-shrink: 0;
        }
        
        .chat-input {
            flex: 1;
            min-width: 0;
            padding: 10px 12px;
            background: rgba(8, 12, 20, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            outline: none;
        }
        .chat-input::placeholder {
            color: #64748b;
        }

        .btn-enter {
            background: linear-gradient(135deg, #10b981, #06b6d4);
            color: #ffffff;
            border: none;
            padding: 0 12px;
            height: 42px;
            border-radius: 8px;
            font-weight: 800;
            font-size: 13.5px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 3px;
            flex-shrink: 0;
            white-space: nowrap;
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
        }

        #fileInput, #bgInput {
            display: none;
        }
    </style>
</head>
<body>
    <div class="backdrop-overlay"></div>

    <div class="app-container">
        <div class="header">
            <div class="header-title">
                <h1>⚡ SIÊU NHÂN AI PHDAM</h1>
                <p>Bản Sao Google Gemini • Mắt Thần Siêu Cấp</p>
            </div>
            <div class="header-actions">
                <button class="btn-tool btn-key" onclick="setupApiKey()">🔑 Cài Não Gemini</button>
                <button class="btn-tool" onclick="document.getElementById('bgInput').click()">🖼️ Đổi nền</button>
            </div>
        </div>

        <div class="chat-stream" id="chatStream">
            <div class="msg bot">
                Chào bồ! Tôi chính là <b>Bản Sao Trí Tuệ của Google Gemini</b>.<br><br>
                ✨ Để mở khóa 100% năng lực soi ảnh đọc số và tư duy bách khoa y hệt như đang chat với chuyên gia: Bồ bấm vào nút <b>[🔑 Cài Não Gemini]</b> ở góc trên dán mã khóa Google vào là tôi thức tỉnh vĩnh viễn nhé!
                <button class="speak-btn" onclick="speakText(this.parentElement.innerText)">🔊</button>
            </div>
        </div>
    </div>

    <div class="attachment-preview-bar" id="attachPreviewBar">
        <div class="preview-scroll-row" id="previewRow"></div>
    </div>

    <div class="bottom-bar">
        <form class="bottom-bar-inner" onsubmit="event.preventDefault(); sendPayload();">
            <label for="fileInput" class="btn-icon-label" title="Chọn ảnh / video">+</label>
            <input type="file" id="fileInput" accept="image/*,video/*" multiple onchange="handleFileSelected(event)">

            <input type="text" id="chatInput" class="chat-input" placeholder="Hỏi bách khoa hoặc gửi ảnh đọc số..." autocomplete="off">

            <button type="button" class="btn-icon" id="micBtn" onclick="toggleMic()" title="Nói">🎙️</button>
            <button type="submit" class="btn-enter" title="Chạy">ENTER ↵</button>
        </form>
    </div>

    <input type="file" id="bgInput" accept="image/*" onchange="changeBackground(event)">

    <script>
        let currentAttachments = [];

        window.addEventListener('DOMContentLoaded', () => {
            const savedBg = localStorage.getItem('phdam_user_bg');
            if (savedBg) document.body.style.backgroundImage = `url('${savedBg}')`;
        });

        async function setupApiKey() {
            const current = prompt("Dán mã khóa Google Gemini API (bắt đầu bằng AIza...) vào đây để mở khóa bản sao 100%:");
            if (!current) return;
            const res = await fetch('/api/set-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ key: current.trim() })
            });
            const d = await res.json();
            alert("🎉 CHÚC MỪNG BỒ! Siêu Não Bộ Google Gemini đã được kích hoạt thành công trên web của bồ!");
        }

        function changeBackground(e) {
            const file = e.target.files[0];
            if (!file) return;
            compressImage(file, 1200, 0.7, (bgUrl) => {
                document.body.style.backgroundImage = `url('${bgUrl}')`;
                localStorage.setItem('phdam_user_bg', bgUrl);
            });
        }

        function compressImage(file, maxWidth, quality, callback) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    let w = img.width;
                    let h = img.height;
                    if (w > maxWidth) {
                        h = Math.round((h * maxWidth) / w);
                        w = maxWidth;
                    }
                    canvas.width = w;
                    canvas.height = h;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, w, h);
                    callback(canvas.toDataURL('image/jpeg', quality));
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }

        function handleFileSelected(e) {
            const files = Array.from(e.target.files);
            if (!files.length) return;
            
            files.forEach(f => {
                const isVideo = f.type.startsWith('video');
                if (isVideo) {
                    const reader = new FileReader();
                    reader.onload = (evt) => {
                        currentAttachments.push({ name: f.name, dataUrl: evt.target.result, isVideo: true });
                        renderPreviewChips();
                    };
                    reader.readAsDataURL(f);
                } else {
                    compressImage(f, 800, 0.75, (compressedDataUrl) => {
                        currentAttachments.push({ name: f.name, dataUrl: compressedDataUrl, isVideo: false });
                        renderPreviewChips();
                    });
                }
            });
            e.target.value = '';
        }

        function renderPreviewChips() {
            const bar = document.getElementById('attachPreviewBar');
            const row = document.getElementById('previewRow');
            if (!currentAttachments.length) {
                bar.style.display = 'none';
                return;
            }
            bar.style.display = 'block';
            row.innerHTML = currentAttachments.map((att, i) => `
                <div class="preview-item-chip">
                    ${att.isVideo ? `<video src="${att.dataUrl}" muted></video>` : `<img src="${att.dataUrl}">`}
                    <span style="max-width:85px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${att.name}</span>
                    <button type="button" class="btn-chip-remove" onclick="removeAttachItem(${i})">×</button>
                </div>
            `).join('');
        }

        function removeAttachItem(index) {
            currentAttachments.splice(index, 1);
            renderPreviewChips();
        }

        async function sendPayload() {
            const inp = document.getElementById('chatInput');
            const text = inp.value.trim();

            if (!text && !currentAttachments.length) {
                alert('Bồ hãy gõ câu hỏi hoặc chọn ảnh trước khi bấm ENTER nhé!');
                return;
            }

            const stream = document.getElementById('chatStream');

            let userHtml = `<div class="msg user">`;
            if (currentAttachments.length) {
                userHtml += `<div class="user-media-grid">`;
                currentAttachments.forEach(att => {
                    if (att.isVideo) {
                        userHtml += `<video src="${att.dataUrl}" controls playsinline></video>`;
                    } else {
                        userHtml += `<img src="${att.dataUrl}">`;
                    }
                });
                userHtml += `</div>`;
            }
            if (text) userHtml += `<div>${text}</div>`;
            userHtml += `</div>`;
            stream.innerHTML += userHtml;
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            const firstImage = currentAttachments.find(a => !a.isVideo);
            const firstImageDataUrl = firstImage ? firstImage.dataUrl : null;
            const sentCount = currentAttachments.length;

            currentAttachments = [];
            renderPreviewChips();
            inp.value = '';

            const tempId = 'bot_temp_' + Date.now();
            stream.innerHTML += `<div class="msg bot" id="${tempId}">⚡ Bản Sao Gemini đang vận hành kho tri thức phân tích...</div>`;
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: text,
                        image_data: firstImageDataUrl,
                        media_count: sentCount
                    })
                });

                const d = await res.json();
                const tempBox = document.getElementById(tempId);
                tempBox.innerHTML = `${d.reply} <button class="speak-btn" onclick="speakText('${d.reply.replace(/['"\\n]/g, ' ')}')">🔊</button>`;
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

                if (d.speak) speakText(d.reply);
            } catch (err) {
                const tempBox = document.getElementById(tempId);
                tempBox.innerHTML = `⚠️ Máy chủ đang xử lý dữ liệu lớn, bồ bấm ENTER lại nhé!`;
            }
        }

        function speakText(txt) {
            if (!window.speechSynthesis) return;
            window.speechSynthesis.cancel();
            const clean = txt.replace(/<[^>]*>/g, '').replace(/🔊/g, '');
            const u = new SpeechSynthesisUtterance(clean);
            u.lang = 'vi-VN';
            u.rate = 1.0;
            window.speechSynthesis.speak(u);
        }

        let recognition;
        function toggleMic() {
            const mic = document.getElementById('micBtn');
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) return alert('Trình duyệt chưa hỗ trợ micro trực tiếp, bồ gõ phím nhé!');
            if (recognition) { recognition.stop(); recognition = null; mic.style.color = '#38bdf8'; return; }
            recognition = new SpeechRec();
            recognition.lang = 'vi-VN';
            recognition.start();
            mic.style.color = '#ef4444';
            recognition.onresult = (e) => {
                document.getElementById('chatInput').value = e.results[0][0].transcript;
                recognition.stop();
                recognition = null;
                mic.style.color = '#38bdf8';
                sendPayload();
            };
            recognition.onerror = () => { recognition = null; mic.style.color = '#38bdf8'; };
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

@app.post("/api/set-key")
async def set_key(req: Request):
    data = await req.json()
    save_api_key(data.get("key", ""))
    return {"status": "success"}

@app.post("/api/chat")
async def chat_endpoint(req: Request):
    data = await req.json()
    msg = data.get("message", "").strip()
    image_data = data.get("image_data")

    # 1. GỌI SIÊU NÃO GOOGLE GEMINI CHÍNH HÃNG (BẢN SAO 100%)
    gemini_reply = ask_gemini_brain(msg, image_data)
    if gemini_reply:
        return {"reply": gemini_reply, "speak": True}

    # 2. NẾU CHƯA CÀI KEY ➔ DÙNG BỘ NÃO TỰ THÂN CHUYÊN SÂU
    m = msg.lower()
    if any(k in m for k in ["tốc độ", "rpm", "nhanh chậm"]):
        reply = (
            "⚡ <b>PHÂN TÍCH TỐC ĐỘ ĐỘNG CƠ & MÁY MÓC:</b><br><br>"
            "• <b>Tốc độ chuẩn:</b> Motor 3 pha 4 cực chạy ở 50Hz đạt ~1450 vòng/phút. Qua hộp số giảm tốc sẽ cho tốc độ kéo tải ổn định.<br>"
            "• <b>Đánh giá:</b> Tốc độ ổn định khi tần số dao động không quá ±0.2Hz, dòng Ampe không nhảy vọt. Nếu motor rung gắt hoặc phát tiếng rít, cần kiểm tra lại bạc đạn và thông số bù mô-men xoắn trên biến tần!"
        )
    elif any(k in m for k in ["nguyên lý", "nguyen ly"]):
        reply = (
            "⚙️ <b>NGUYÊN LÝ HOẠT ĐỘNG CỐT LÕI:</b><br><br>"
            "Dòng điện 3 pha tạo từ trường quay trong Stator, cảm ứng lực điện từ Lorentz làm quay Rotor. Tốc độ được biến tần điều biến mượt mà theo công thức n = 60f/p, vừa bảo vệ chống giật cơ khí vừa tối ưu hóa điện năng tiêu thụ."
        )
    elif any(k in m for k in ["tất cả", "tất cả đi", "phân tích hết"]):
        reply = (
            "🌐 <b>TỔNG QUAN TẤT CẢ TỪ A ĐẾN Z:</b><br><br>"
            "• <b>1. Bản chất:</b> Hệ thống máy truyền động tự động hóa tối tân.<br>"
            "• <b>2. Ưu điểm:</b> Tiết kiệm điện, khởi động êm, kiểm soát tốc độ chính xác.<br>"
            "• <b>3. Nhược điểm:</b> Sinh nhiệt cao khi chạy chậm, cần thông gió tốt.<br>"
            "• <b>4. Giải pháp tối ưu:</b> Cài đặt tần số trong dải an toàn 25 – 50Hz, gắn thêm quạt cưỡng bức nếu làm việc liên tục 24/7!"
        )
    else:
        alt = fallback_brain(msg)
        if alt:
            reply = alt
        else:
            reply = (
                f"💡 <b>Về vấn đề '{msg}':</b><br>"
                "Bồ bấm vào nút màu cam <b>[🔑 Cài Não Gemini]</b> ở góc trên để dán mã khóa Google vào nhé! Khi có chìa khóa, tôi sẽ trở thành bản sao 100% của Gemini, nhìn thấu từng con số và trả lời xuất sắc mọi câu hỏi!"
            )

    return {"reply": reply, "speak": True}
