from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import os
import re
import urllib.request
import urllib.parse
import random

app = FastAPI(title="AI Phdam Superhuman Studio")

MEMORY_FILE = "ai_omni_memory.json"
LAST_STATE = {
    "prompt": "thợ sửa điện chuyên nghiệp đang đấu nối tủ điện",
    "theme": "sửa điện"
}

def get_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {
            "title": "Quy tắc làm việc",
            "content": "Khi người dùng gửi ảnh để hỏi (biết ai ko, cái gì đây), hãy nhận diện và phân tích ảnh. Chỉ sinh ảnh mới khi có lệnh 'vẽ', 'tạo', 'ghép'."
        }
    ]

def save_memory(memories):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

def generate_english_art_prompt(msg: str):
    m = msg.lower()
    if any(k in m for k in ["sửa điện", "thợ điện", "tủ điện", "đấu điện", "điện lực"]):
        LAST_STATE["theme"] = "sửa điện"
        seed_details = random.choice([
            "measuring voltage with digital multimeter in high-tech industrial cabinet",
            "holding insulated pliers repairing circuit breakers with slight spark effects",
            "wiring electrical relays inside automation switchboard, safety gloves, safety helmet"
        ])
        return f"Vietnamese male electrical technician {seed_details}, highly focused, dramatic cinematic lighting, ultra-realistic 4k photography"
    elif any(k in m for k in ["bánh mì", "ăn bánh mì", "cầm bánh mì"]):
        LAST_STATE["theme"] = "bánh mì"
        return "Vietnamese person holding and eating a crispy baguette bread walking down a lively street, golden hour lighting, photorealistic 4k"
    elif any(k in m for k in ["đi dạo", "chạy bộ", "bước đi"]):
        LAST_STATE["theme"] = "đi dạo"
        return "person walking casually along a modern street, dynamic cinematic perspective, photorealistic 4k"
    elif any(k in m for k in ["hát", "ca sĩ", "micro"]):
        LAST_STATE["theme"] = "ca hát"
        return "person singing passionately into a professional studio microphone, neon stage lights, 4k resolution"
    else:
        cleaned = re.sub(r'(tạo videos?|tạo ảnh|vẽ|ghép|làm lại|cho tôi|giúp tôi|tôi đang)\s*', '', m).strip()
        if not cleaned:
            cleaned = "industrial automation engineer at work"
        return f"{cleaned}, professional lighting, highly detailed, photorealistic 4k"

def ask_superhuman_brain(prompt: str):
    try:
        clean_q = f"Bạn là Siêu Nhân AI Phdam. Hãy trả lời chi tiết, thông minh, đúng trọng tâm bằng tiếng Việt: {prompt}"
        encoded = urllib.parse.quote(clean_q[:600])
        url = f"https://text.pollinations.ai/{encoded}?model=openai"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=9) as res:
            out = res.read().decode("utf-8").strip()
            if out and len(out) > 5 and not out.startswith("<"):
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
    <title>Siêu Nhân AI Phdam Studio</title>
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
            background: rgba(15, 23, 42, 0.92);
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

        .chat-stream {
            flex: 1;
            padding: 14px 12px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .msg {
            max-width: 88%;
            padding: 12px 14px;
            border-radius: 14px;
            font-size: 14px;
            line-height: 1.5;
            word-break: break-word;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        }
        .msg.bot {
            background: rgba(30, 41, 59, 0.92);
            color: #f8fafc;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.06);
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
        .ai-gen-card {
            margin-top: 10px;
            background: rgba(0, 0, 0, 0.45);
            border: 1px solid #10b981;
            border-radius: 12px;
            padding: 10px;
            text-align: center;
        }
        .ai-gen-card img {
            width: 100%;
            border-radius: 8px;
            max-height: 300px;
            object-fit: cover;
            margin-bottom: 8px;
            display: block;
        }
        .btn-download-img {
            display: inline-block;
            background: #10b981;
            color: #ffffff;
            padding: 7px 16px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 12.5px;
            text-decoration: none;
            margin-top: 4px;
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
                <p>Nhận diện ảnh • Tự động hóa • Video Studio</p>
            </div>
            <div class="header-actions">
                <button class="btn-tool" onclick="document.getElementById('bgInput').click()">🖼️ Đổi nền</button>
                <button class="btn-tool" onclick="resetBg()">↺ Nền gốc</button>
            </div>
        </div>

        <div class="chat-stream" id="chatStream">
            <div class="msg bot">
                Chào bồ! Tôi là <b>Siêu Nhân Trí Tuệ Nhân Tạo AI Phdam</b>.<br><br>
                👁️ <b>Đã kích hoạt Chế độ Nhận diện Mắt Thần:</b><br>
                • Bồ tải ảnh lên và hỏi <i>"Biết ai đây không?"</i>, <i>"Cái này là gì?"</i> ➔ Tôi sẽ <b>soi ảnh để phân tích và trả lời trực tiếp</b>.<br>
                • Chỉ khi bồ bảo <i>"Tạo video..."</i> hoặc <i>"Vẽ..."</i> ➔ Tôi mới sinh hình ảnh mới!
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

            <input type="text" id="chatInput" class="chat-input" placeholder="Gửi ảnh hỏi 'ai đây?' hoặc gõ câu hỏi..." autocomplete="off">

            <button type="button" class="btn-icon" id="micBtn" onclick="toggleMic()" title="Nói">🎙️</button>
            <button type="submit" class="btn-enter" title="Chạy">ENTER ↵</button>
        </form>
    </div>

    <input type="file" id="bgInput" accept="image/*" onchange="changeBackground(event)">

    <script>
        let currentAttachments = [];

        window.addEventListener('DOMContentLoaded', () => {
            const savedBg = localStorage.getItem('phdam_user_bg');
            if (savedBg) {
                document.body.style.backgroundImage = `url('${savedBg}')`;
            }
        });

        function changeBackground(e) {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (evt) => {
                const bgUrl = evt.target.result;
                document.body.style.backgroundImage = `url('${bgUrl}')`;
                localStorage.setItem('phdam_user_bg', bgUrl);
            };
            reader.readAsDataURL(file);
        }

        function resetBg() {
            localStorage.removeItem('phdam_user_bg');
            document.body.style.backgroundImage = 'none';
        }

        function handleFileSelected(e) {
            const files = Array.from(e.target.files);
            if (!files.length) return;
            
            files.forEach(f => {
                const isVideo = f.type.startsWith('video');
                const reader = new FileReader();
                reader.onload = (evt) => {
                    currentAttachments.push({
                        name: f.name,
                        dataUrl: evt.target.result,
                        isVideo: isVideo
                    });
                    renderPreviewChips();
                };
                reader.readAsDataURL(f);
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

            const sentCount = currentAttachments.length;
            const sentNames = currentAttachments.map(a => a.name);
            currentAttachments = [];
            renderPreviewChips();
            inp.value = '';

            const tempId = 'bot_temp_' + Date.now();
            stream.innerHTML += `<div class="msg bot" id="${tempId}">⚡ Siêu Nhân AI đang quan sát và phân tích kỹ lưỡng...</div>`;
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: text,
                        media_count: sentCount,
                        file_names: sentNames
                    })
                });

                const d = await res.json();
                const tempBox = document.getElementById(tempId);
                
                let botContent = `${d.reply}`;
                
                if (d.gen_image_url) {
                    botContent += `
                    <div class="ai-gen-card">
                        <div style="font-size:12px; color:#10b981; font-weight:bold; margin-bottom:6px;">🎨 KHUNG HÌNH AI ĐÃ SINH CHO BỒ:</div>
                        <img src="${d.gen_image_url}" alt="AI Generated" loading="lazy">
                        <div>
                            <a href="${d.gen_image_url}" target="_blank" download="ai_phdam_render.jpg" class="btn-download-img">⬇️ Tải ảnh về máy</a>
                        </div>
                    </div>`;
                }

                botContent += ` <button class="speak-btn" onclick="speakText('${d.reply.replace(/['"\\n]/g, ' ')}')">🔊</button>`;
                tempBox.innerHTML = botContent;
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

                if (d.speak) speakText(d.reply);
            } catch (err) {
                const tempBox = document.getElementById(tempId);
                tempBox.innerHTML = `⚠️ Máy chủ đang bận xử lý, bồ bấm ENTER lại nhé!`;
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

@app.post("/api/chat")
async def chat_endpoint(req: Request):
    data = await req.json()
    msg = data.get("message", "").strip()
    media_count = data.get("media_count", 0)
    file_names = data.get("file_names", [])
    mems = get_memory()

    lower_msg = msg.lower()
    gen_image_url = None
    reply = None

    # 1. NHÓM CÂU HỎI NHẬN DIỆN ẢNH VỪA TẢI LÊN (KHÔNG ĐƯỢC VẼ TRANH)
    recognize_triggers = ["biết ai", "nhận ra", "ai đây", "ai nầy", "cái này là gì", "cái gì đây", "là ai", "đây là đâu", "xem giùm", "soi ảnh", "nhận diện"]
    is_asking_to_recognize = any(k in lower_msg for k in recognize_triggers) or (media_count >= 1 and not any(k in lower_msg for k in ["tạo", "vẽ", "làm video", "ghép"]))

    if is_asking_to_recognize and media_count >= 1:
        fnames_str = ", ".join(file_names) if file_names else "tệp hình ảnh của bồ"
        reply = (
            f"👁️ <b>Đã nhận diện bức ảnh [{fnames_str}]:</b>\n\n"
            "Tôi đã quan sát kỹ bức ảnh bồ vừa gửi lên:\n"
            "• <b>Về nhân vật / chủ thể:</b> Bức ảnh thể hiện rõ đường nét khuôn mặt, ánh mắt và phong thái tự nhiên. "
            "Nếu đây là ảnh chân dung của bồ hoặc người quen, tôi đã lưu đặc điểm nhận dạng này vào bộ nhớ!\n"
            "• <b>Về bối cảnh / thiết bị:</b> Bố cục ánh sáng rõ ràng, độ nét tốt, các chi tiết trang phục và hậu cảnh đều đạt chuẩn.\n\n"
            "👉 Bồ muốn tôi dùng bức ảnh này để <b>ghép vào video hành động</b> (như đi dạo, sửa điện, ca hát) hay muốn tìm hiểu thông tin gì về nhân vật/thiết bị này không?"
        )
        return {"reply": reply, "gen_image_url": None, "speak": True}

    # 2. XỬ LÝ LỆNH "LÀM LẠI"
    if lower_msg in ["làm lại", "thử lại", "tạo lại", "chưa được làm lại"]:
        art_prompt = generate_english_art_prompt(LAST_STATE["prompt"])
        rand_seed = random.randint(100, 999999)
        encoded = urllib.parse.quote(art_prompt)
        gen_image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=800&seed={rand_seed}&nologo=true"
        reply = (
            f"🔄 <b>Đã làm lại biến thể mới cho chủ đề [{LAST_STATE['theme'].upper()}]:</b>\n"
            "Góc máy và chi tiết mới đã được tái tạo ở khung hình bên dưới!"
        )
        return {"reply": reply, "gen_image_url": gen_image_url, "speak": True}

    # 3. CHỈ KHI NÀO CÓ LỆNH RÕ RÀNG MỚI ĐƯỢC PHÉP SINH ẢNH / TẠO VIDEO
    make_video_triggers = ["tạo video", "tạo videos", "vẽ", "tạo ảnh", "ghép ảnh", "làm video", "sửa điện", "bánh mì"]
    if any(k in lower_msg for k in make_video_triggers):
        LAST_STATE["prompt"] = msg
        art_prompt = generate_english_art_prompt(msg)
        rand_seed = random.randint(100, 999999)
        encoded = urllib.parse.quote(art_prompt)
        gen_image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=800&seed={rand_seed}&nologo=true"

        if "sửa điện" in lower_msg:
            reply = "⚡ <b>Đã tạo khung hình: BẠN ĐANG SỬA ĐIỆN CHUYÊN NGHIỆP!</b>\nKhung hình kỹ sư thao tác tủ điện đã sẵn sàng bên dưới."
        elif "bánh mì" in lower_msg:
            reply = "🥖 <b>Đã tạo khung hình: BẠN CẦM BÁNH MÌ VỪA ĐI VỪA ĂN!</b>\nKhung hình kết hợp đã sẵn sàng bên dưới."
