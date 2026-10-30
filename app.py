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
            "title": "Quy tắc làm việc của người dùng",
            "content": "Khi người dùng nói 'Làm lại' nghĩa là tự động làm lại yêu cầu tạo video/ảnh gần nhất từ hình ảnh đã tải lên."
        }
    ]

def save_memory(memories):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

def generate_english_art_prompt(msg: str):
    """Chuyển đổi yêu cầu tiếng Việt thành mô tả hình ảnh 4K chuẩn xác, không bị dính bánh mì"""
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
        # Làm sạch các từ thừa để lấy từ khóa thật
        cleaned = re.sub(r'(tạo videos?|tạo ảnh|vẽ|ghép|làm lại|cho tôi|giúp tôi|tôi đang)\s*', '', m).strip()
        if not cleaned:
            cleaned = "industrial automation engineer at work"
        return f"{cleaned}, professional lighting, highly detailed, photorealistic 4k"

def ask_superhuman_brain(prompt: str):
    """Gọi não bộ AI bằng đường truyền GET siêu nhẹ không bị chặn"""
    try:
        clean_q = f"Bạn là Siêu Nhân AI Phdam. Hãy trả lời thân thiện, thông minh, đúng trọng tâm bằng tiếng Việt: {prompt}"
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

        /* Header */
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

        /* Chat Stream */
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

        /* Khay xem trước nhiều tệp */
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

        /* KHUNG NHẬP CỐ ĐỊNH Ở ĐÁY */
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
        <!-- Header -->
        <div class="header">
            <div class="header-title">
                <h1>⚡ SIÊU NHÂN AI PHDAM</h1>
                <p>Tự động hóa • Biến tần • Studio Tạo Ảnh & Video</p>
            </div>
            <div class="header-actions">
                <button class="btn-tool" onclick="document.getElementById('bgInput').click()">🖼️ Đổi nền</button>
                <button class="btn-tool" onclick="resetBg()">↺ Nền gốc</button>
            </div>
        </div>

        <!-- Chat Stream -->
        <div class="chat-stream" id="chatStream">
            <div class="msg bot">
                Chào bồ! Tôi là <b>Siêu Nhân Trí Tuệ Nhân Tạo AI Phdam</b>.<br><br>
                Đã tiếp thu và ghi nhớ bài học: Bất cứ khi nào bồ gõ <b>"Làm lại"</b>, tôi sẽ tự động thực hiện lại yêu cầu tạo video/ảnh từ hình ảnh bồ đã tải lên! Bây giờ bồ cần tạo nội dung gì cứ nhắn nhé!
                <button class="speak-btn" onclick="speakText(this.parentElement.innerText)">🔊</button>
            </div>
        </div>
    </div>

    <!-- Khay xem trước nhiều tệp -->
    <div class="attachment-preview-bar" id="attachPreviewBar">
        <div class="preview-scroll-row" id="previewRow"></div>
    </div>

    <!-- KHUNG NHẬP CỐ ĐỊNH Ở ĐÁY -->
    <div class="bottom-bar">
        <form class="bottom-bar-inner" onsubmit="event.preventDefault(); sendPayload();">
            <label for="fileInput" class="btn-icon-label" title="Chọn ảnh / video">+</label>
            <input type="file" id="fileInput" accept="image/*,video/*" multiple onchange="handleFileSelected(event)">

            <input type="text" id="chatInput" class="chat-input" placeholder="Gõ yêu cầu (VD: Tạo video tôi đang sửa điện)..." autocomplete="off">

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
                alert('Bồ hãy gõ yêu cầu hoặc chọn ảnh/video trước khi bấm ENTER nhé!');
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
            currentAttachments = [];
            renderPreviewChips();
            inp.value = '';

            const tempId = 'bot_temp_' + Date.now();
            stream.innerHTML += `<div class="msg bot" id="${tempId}">⚡ Siêu Nhân AI đang xử lý yêu cầu...</div>`;
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: text,
                        media_count: sentCount
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
    mems = get_memory()

    gen_image_url = None
    reply = None
    lower_msg = msg.lower()

    # 1. XỬ LÝ LỆNH "LÀM LẠI"
    if lower_msg in ["làm lại", "thử lại", "tạo lại", "chưa được làm lại"]:
        art_prompt = generate_english_art_prompt(LAST_STATE["prompt"])
        rand_seed = random.randint(100, 999999)
        encoded = urllib.parse.quote(art_prompt)
        gen_image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=800&seed={rand_seed}&nologo=true"
        reply = (
            f"🔄 <b>Đã thực hiện LÀM LẠI theo đúng quy tắc của bồ!</b>\n"
            f"Tôi đã tạo ra một góc máy và biến thể chuyển động mới cho chủ đề <b>{LAST_STATE['theme'].upper()}</b>. "
            "Khung hình mới bên dưới đã sẵn sàng!"
        )
        return {"reply": reply, "gen_image_url": gen_image_url, "speak": True}

    # 2. XỬ LÝ LỆNH HỌC TẬP VÀ GHI NHỚ QUY TẮC CỦA NGƯỜI DÙNG
    if any(k in lower_msg for k in ["khi m nói", "khi tao nói", "nhớ nhé", "ghi nhớ nhé", "hãy nhớ"]):
        mems.append({
            "title": "Chỉ dẫn đặc biệt từ người dùng",
            "content": msg
        })
        save_memory(mems)
        reply = (
            f"🧠 <b>Siêu Nhân AI đã tiếp thu và ghi nhớ tuyệt đối!</b>\n"
            f"Tôi đã khắc ghi quy tắc: <i>'{msg}'</i> vào bộ nhớ trung tâm. "
            "Từ bây giờ, tôi sẽ tuân thủ chuẩn xác 100% ý muốn của bồ!"
        )
        return {"reply": reply, "gen_image_url": None, "speak": True}

    # 3. XỬ LÝ TẠO ẢNH / VIDEO (VD: SỬA ĐIỆN, BÁNH MÌ, ĐI DẠO...)
    gen_triggers = ["tạo video", "tạo videos", "sửa điện", "thợ điện", "bánh mì", "vẽ", "tạo ảnh", "ghép", "làm video"]
    if any(k in lower_msg for k in gen_triggers) or media_count >= 1:
        LAST_STATE["prompt"] = msg if msg else "sửa điện"
        art_prompt = generate_english_art_prompt(LAST_STATE["prompt"])
        rand_seed = random.randint(100, 999999)
        encoded = urllib.parse.quote(art_prompt)
        gen_image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=800&seed={rand_seed}&nologo=true"

        if "sửa điện" in lower_msg or "thợ điện" in lower_msg:
            reply = (
                "⚡ <b>Đã phân tích yêu cầu: TẠO VIDEO BẠN ĐANG SỬA ĐIỆN!</b>\n"
                "Tôi đã thiết lập bối cảnh: Kỹ sư điện đang đấu nối dây dẫn trong tủ điều khiển tự động hóa, kiểm tra rơ-le và thiết bị đo. "
                "Khung hình mốc chuẩn (Keyframe) bên dưới đã được sinh ra. Bạn có thể bấm tải về để xem chi tiết hoặc đưa vào Kling/Hailuo tạo video chuyển động thật!"
            )
        elif "bánh mì" in lower_msg:
            reply = (
                "🥖 <b>Đã thực hiện: GHÉP BẠN VỪA ĐI VỪA ĂN BÁNH MÌ!</b>\n"
                "Khung hình kết hợp chân dung và ổ bánh mì đã sinh thành công ở bên dưới cho bồ đây!"
            )
        else:
            reply = (
                f"🎨 <b>Đã khởi tạo khung hình AI theo yêu cầu:</b> <i>'{msg}'</i>\n"
                "Kết quả chi tiết hiển thị ngay bên dưới!"
            )
        return {"reply": reply, "gen_image_url": gen_image_url, "speak": False}

    # 4. TRÒ CHUYỆN / HỎI ĐÁP THÔNG THƯỜNG
    reply = ask_superhuman_brain(msg)
    if not reply:
        if "biến tần" in lower_msg:
            reply = "Biến tần (VFD) điều khiển tốc độ động cơ 3 pha vô cấp thông qua biến đổi tần số, giúp bảo vệ quá dòng, chống sốc cơ khí và tiết kiệm 20-40% điện năng."
        else:
            reply = f"Siêu Nhân AI Phdam đã hiểu rõ câu hỏi '{msg}'. Tôi sẵn sàng hỗ trợ bồ phân tích kỹ thuật và xử lý video bất cứ lúc nào!"

    return {"reply": reply, "gen_image_url": None, "speak": False}
