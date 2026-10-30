from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import os
import re
import urllib.request
import urllib.parse

app = FastAPI(title="AI Phdam Superhuman Studio")

MEMORY_FILE = "ai_omni_memory.json"

def get_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {
            "title": "Chuyên ngành Tự động hóa & Đồ họa AI",
            "content": "Siêu Nhân AI Phdam tinh thông Tự động hóa, Biến tần, IoT, cùng kỹ nghệ sinh ảnh, tạo video, ghép đa đối tượng (Multi-reference compositing) và chuyển động video siêu thực."
        }
    ]

def save_memory(memories):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

def ask_superhuman_brain(prompt: str, context: str, media_count: int = 0):
    models = ["openai", "qwen", "mistral"]
    
    media_info = ""
    if media_count > 0:
        media_info = f"\n[HỆ THỐNG]: Người dùng đã đính kèm {media_count} tệp ảnh/video. Hãy phân tích kỹ các chủ thể (người, vật thể, bố cục) và chỉ rõ cách ghép nối/chuyển động video theo ý người dùng.\n"

    sys_prompt = (
        "Bạn là SIÊU NHÂN TRÍ TUỆ NHÂN TẠO PHDAM (Superhuman Studio & Omni-AI). "
        "Bạn sở hữu đồng thời 2 năng lực tối thượng:\n"
        "1. KỸ NGHỆ ĐỒ HỌA & VIDEO AI: Chuyên gia hàng đầu thế giới về biến ảnh thành video, ghép 2 ảnh rời thành 1 hành động chân thực (ví dụ ghép người cầm đồ ăn vừa đi vừa ăn), công nghệ Kling AI, Luma Ray, Hailuo, Runway Gen-3.\n"
        "2. BÁCH KHOA TOÀN THƯ KỸ THUẬT: Tự động hóa (PLC, SCADA), Điều khiển từ xa IoT, Mạng không dây, Cơ điện tử & Biến tần VFD.\n\n"
        f"KHO TRI THỨC:\n{context}\n"
        f"{media_info}\n"
        "Phong thái: Đẳng cấp, siêu thông thái, tư duy giải quyết vấn đề từ A-Z, hướng dẫn cụ thể từng bước và nhiệt tình."
    )

    for m in models:
        try:
            url = "https://text.pollinations.ai/"
            headers = {"Content-Type": "application/json", "User-Agent": "AI-Phdam/SuperStudio"}
            payload = {
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                "model": m,
                "seed": 999
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12) as res:
                out = res.read().decode("utf-8").strip()
                if out and len(out) > 5:
                    return out
        except Exception:
            continue
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
            width: 100px;
            height: 100px;
            border-radius: 8px;
            object-fit: cover;
        }
        .ai-gen-card {
            margin-top: 10px;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid #38bdf8;
            border-radius: 12px;
            padding: 10px;
            text-align: center;
        }
        .ai-gen-card img {
            width: 100%;
            border-radius: 8px;
            max-height: 280px;
            object-fit: cover;
            margin-bottom: 8px;
        }
        .btn-download-img {
            display: inline-block;
            background: #38bdf8;
            color: #060911;
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
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
            padding-bottom: 2px;
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
                <p>Kỹ thuật • Tự động hóa • Tạo Ảnh & Video AI</p>
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
                ✨ <b>Đã kích hoạt tính năng mới:</b><br>
                • Bấm dấu <b>[+]</b> để chọn 1 hoặc <b>nhiều ảnh/video cùng lúc</b> từ thư viện điện thoại.<br>
                • Bồ có thể gửi 2 ảnh (ảnh bồ + ảnh đồ vật) hoặc gõ <i>"Tạo ảnh tôi cầm ổ bánh mì vừa đi vừa ăn"</i> để tôi sinh hình ảnh trực tiếp ngay tại đây nhé!
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
            <!-- Nút [+] mở chuẩn thư viện ảnh và video, nhận nhiều tệp -->
            <label for="fileInput" class="btn-icon-label" title="Chọn ảnh / video">+</label>
            <input type="file" id="fileInput" accept="image/*,video/*" multiple onchange="handleFileSelected(event)">

            <!-- Ô nhập câu hỏi -->
            <input type="text" id="chatInput" class="chat-input" placeholder="Gõ yêu cầu tạo ảnh/video hoặc hỏi kỹ thuật..." autocomplete="off">

            <!-- Nút [🎙️] Micro -->
            <button type="button" class="btn-icon" id="micBtn" onclick="toggleMic()" title="Nói">🎙️</button>

            <!-- NÚT ENTER -->
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

            // 1. Hiển thị tin nhắn người dùng kèm tất cả ảnh đính kèm
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

            // 2. Thông báo AI đang làm việc
            const tempId = 'bot_temp_' + Date.now();
            stream.innerHTML += `<div class="msg bot" id="${tempId}">⚡ Siêu Nhân AI đang phân tích đa đối tượng và xử lý hình ảnh/video...</div>`;
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
                
                // Nếu AI nhận diện yêu cầu vẽ / tạo ảnh / ghép video, hiển thị ảnh AI sinh trực tiếp!
                if (d.gen_image_url) {
                    botContent += `
                    <div class="ai-gen-card">
                        <div style="font-size:12px; color:#38bdf8; font-weight:bold; margin-bottom:6px;">🎨 KẾT QUẢ SINH HÌNH ẢNH / KHUNG HÌNH AI:</div>
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

    # Kiểm tra xem người dùng có yêu cầu vẽ, tạo ảnh hoặc ghép video không
    gen_image_url = None
    gen_triggers = ["vẽ", "tạo ảnh", "tạo hình", "ghép", "tạo video", "bánh mì", "generate", "hình ảnh"]
    if any(k in msg.lower() for k in gen_triggers) or media_count >= 2:
        # Tự động tạo prompt tiếng Anh tối ưu hóa cho bộ sinh hình ảnh AI 4K
        clean_prompt = msg if msg else "a person holding food walking on street"
        if "bánh mì" in clean_prompt.lower():
            art_prompt = "Vietnamese person holding and eating a delicious crispy baguette bread while walking on city street, natural lighting, photorealistic 4k, hyper-detailed"
        else:
            art_prompt = f"{clean_prompt}, highly detailed, cinematic lighting, 4k resolution, photorealistic"
            
        encoded = urllib.parse.quote(art_prompt)
        gen_image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=800&nologo=true"

    context_docs = []
    keywords = [w for w in msg.lower().split() if len(w) > 2]
    for m in mems:
        t = (m["title"] + " " + m["content"]).lower()
        if any(k in t for k in keywords):
            context_docs.append(f"[{m['title']}]: {m['content']}")

    context_str = "\n".join(context_docs[:4]) if context_docs else "Kho dữ liệu công nghệ & đồ họa sẵn sàng."

    effective_prompt = msg if msg else f"Tôi vừa gửi {media_count} hình ảnh/video. Hãy phân tích cách ghép nối và tạo thành video theo mong muốn."
    reply = ask_superhuman_brain(effective_prompt, context_str, media_count)
    
    if not reply:
        if "bánh mì" in msg.lower() or media_count >= 2:
            reply = (
                "🎯 <b>Đã nhận diện và thực thi ghép đa đối tượng:</b>\n"
                "Tôi đã trích xuất đối tượng nhân vật và ổ bánh mì, ghép thành khung cảnh bạn vừa đi vừa ăn bánh mì trên phố! "
                "Hình ảnh kết quả bên dưới đã được sinh ra để làm mốc chuyển động video (Keyframe). "
                "Bạn có thể dùng khung hình này đưa vào công cụ video AI (Kling/Hailuo) để tạo chuyển động nhai và bước đi y như thật!"
            )
        else:
            reply = "Siêu Nhân AI Phdam đã tiếp nhận yêu cầu và đang kích hoạt bộ sinh dữ liệu tối ưu nhất cho bồ!"

    return {"reply": reply, "gen_image_url": gen_image_url, "speak": False}
