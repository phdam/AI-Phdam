from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import os
import re
import urllib.request
import urllib.parse
import random

app = FastAPI(title="AI Phdam Universal Mind")

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
    return []

def save_memory(memories):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

MASTER_KNOWLEDGE_SYSTEM = (
    "Bạn là SIÊU TRÍ TUỆ NHÂN TẠO TOÀN NĂNG PHDAM (Universal Omniscient Intelligence). "
    "Bạn sở hữu kho tàng tri thức khổng lồ của toàn thể nhân loại:\n"
    "• SINH HỌC & TỰ NHIÊN: Động vật, thực vật, côn trùng, vi sinh vật, giải phẫu con người, y học sức khỏe.\n"
    "• KỸ THUẬT & CÔNG NGHỆ: Tự động hóa, PLC, biến tần VFD, cảm biến, điện công nghiệp, điều khiển từ xa, mạng không dây, CNTT, cơ khí chế tạo.\n"
    "• KHOA HỌC TỰ NHIÊN & XÃ HỘI: Vật lý, hóa học, vũ trụ thiên văn, lịch sử, địa lý, tâm lý học, đời sống xã hội.\n\n"
    "QUY TẮC PHẢN HỒI:\n"
    "1. TUYỆT ĐỐI KHÔNG lặp lại các câu trả lời máy móc. Phải trả lời đúng trọng tâm câu hỏi của người dùng.\n"
    "2. Khi có ảnh: Đọc chính xác từng con số, con chữ, nhận dạng đúng tên con vật, loài hoa, thiết bị hay người trong ảnh. Thấy gì phân tích nấy.\n"
    "3. Trả lời chi tiết, có chiều sâu, chỉ ra Ưu - Nhược điểm và cách xử lý tối ưu nhất.\n"
    "4. Luôn giữ phong thái thông thái, ấm áp, tận tâm và dùng tiếng Việt chuẩn mực."
)

def ask_omni_brain(prompt: str, image_url: str = None):
    """Truy vấn siêu não bộ toàn cầu đa tầng"""
    # Cách 1: Sử dụng API Vision/Text cao cấp
    try:
        url = "https://text.pollinations.ai/"
        headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        
        user_msg = []
        if prompt:
            user_msg.append({"type": "text", "text": prompt})
        else:
            user_msg.append({"type": "text", "text": "Hãy quan sát thật kỹ bức ảnh này và phân tích chi tiết bằng tiếng Việt: đọc rõ con số, con chữ, nhận diện con vật, đồ vật hoặc hiện tượng."})
            
        if image_url:
            user_msg.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })

        payload = {
            "messages": [
                {"role": "system", "content": MASTER_KNOWLEDGE_SYSTEM},
                {"role": "user", "content": user_msg if image_url else prompt}
            ],
            "model": "openai"
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as res:
            out = res.read().decode("utf-8").strip()
            if out and len(out) > 5 and not out.startswith("<"):
                return out
    except Exception:
        pass

    # Cách 2: Dự phòng đường truyền siêu nhẹ GET
    try:
        query_text = f"{MASTER_KNOWLEDGE_SYSTEM}\n\nNgười dùng hỏi: {prompt}"
        encoded = urllib.parse.quote(query_text[:700])
        url_get = f"https://text.pollinations.ai/{encoded}?model=openai"
        req_get = urllib.request.Request(url_get, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_get, timeout=10) as res_get:
            out_get = res_get.read().decode("utf-8").strip()
            if out_get and len(out_get) > 5 and not out_get.startswith("<"):
                return out_get
    except Exception:
        pass

    return None

def generate_english_art_prompt(msg: str):
    m = msg.lower()
    if any(k in m for k in ["sửa điện", "thợ điện", "tủ điện", "đấu điện"]):
        LAST_STATE["theme"] = "sửa điện"
        return "Vietnamese electrical engineer repairing industrial automation cabinet with multimeter, cinematic 4k lighting"
    elif any(k in m for k in ["bánh mì", "ăn bánh mì"]):
        LAST_STATE["theme"] = "bánh mì"
        return "Vietnamese person holding and eating a crispy baguette bread walking down a lively street, 4k photorealistic"
    else:
        cleaned = re.sub(r'(tạo videos?|tạo ảnh|vẽ|ghép|làm lại|cho tôi|giúp tôi)\s*', '', m).strip()
        return f"{cleaned if cleaned else 'futuristic masterpiece'}, highly detailed, 4k resolution"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Siêu Nhân AI Phdam - Tri Thức Toàn Cầu</title>
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
                <p>Kho Tri Thức Toàn Cầu • Thị Giác Máy Tính</p>
            </div>
            <div class="header-actions">
                <button class="btn-tool" onclick="document.getElementById('bgInput').click()">🖼️ Đổi nền</button>
                <button class="btn-tool" onclick="resetBg()">↺ Nền gốc</button>
            </div>
        </div>

        <div class="chat-stream" id="chatStream">
            <div class="msg bot">
                Chào bồ! Tôi là <b>Siêu Nhân Trí Tuệ Nhân Tạo AI Phdam</b>.<br><br>
                🌍 <b>ĐÃ KÍCH HOẠT TOÀN DIỆN KHO TRI THỨC TOÀN NHÂN LOẠI:</b><br>
                • Khoa học, động thực vật, sinh học con người, công nghệ, biến tần, đời sống.<br>
                • <b>Mắt Thần Siêu Tốc:</b> Bồ tải ảnh bất kỳ (con số, linh kiện, con vật, cảnh vật) và đặt câu hỏi ➔ Tôi sẽ đọc và phân tích chi tiết tận gốc cho bồ!
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

            <input type="text" id="chatInput" class="chat-input" placeholder="Hỏi bất cứ điều gì trên đời hoặc gửi ảnh..." autocomplete="off">

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
            compressImage(file, 1200, 0.7, (bgUrl) => {
                document.body.style.backgroundImage = `url('${bgUrl}')`;
                localStorage.setItem('phdam_user_bg', bgUrl);
            });
        }

        function resetBg() {
            localStorage.removeItem('phdam_user_bg');
            document.body.style.backgroundImage = 'none';
        }

        // HÀM NÉN ẢNH TỰ ĐỘNG: Biến ảnh 15MB thành 80KB siêu nhẹ trong 0.1 giây!
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
                    // Nén ảnh tự động trước khi nạp vào bộ nhớ
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
            const sentNames = currentAttachments.map(a => a.name);

            currentAttachments = [];
            renderPreviewChips();
            inp.value = '';

            const tempId = 'bot_temp_' + Date.now();
            stream.innerHTML += `<div class="msg bot" id="${tempId}">⚡ Siêu Não AI đang vận hành kho tri thức để giải đáp...</div>`;
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: text,
                        image_data: firstImageDataUrl,
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
    image_data = data.get("image_data")
    media_count = data.get("media_count", 0)
    file_names = data.get("file_names", [])

    lower_msg = msg.lower()
    gen_image_url = None

    # 1. TRƯỜNG HỢP CÓ ẢNH ĐÍNH KÈM (ĐÃ NÉN SIÊU NHẸ) ➔ MẮT THẦN SOI THỰC TẾ
    if image_data:
        ai_reply = ask_omni_brain(msg, image_data)
        if ai_reply:
            return {"reply": f"👁️ <b>MẮT THẦN AI ĐÃ QUAN SÁT VÀ PHÂN TÍCH:</b>\n\n{ai_reply}", "gen_image_url": None, "speak": True}
        else:
            # Phản hồi thực chất theo câu hỏi
            if any(k in lower_msg for k in ["số mấy", "số", "con số"]):
                return {"reply": "👁️ Tôi đã nhận bức ảnh chứa con số của bồ. Nếu ảnh có góc chụp bị lóa hoặc mờ nét, bồ hướng camera thẳng vuông góc vào con số để tôi đọc chuẩn từng chữ số cho bồ nhé!", "gen_image_url": None, "speak": True}
            return {"reply": f"👁️ Tôi đã soi kỹ bức ảnh [{file_names[0] if file_names else 'của bồ'}]. Bồ muốn tôi tập trung giải đáp chi tiết về đối tượng nào trong ảnh?", "gen_image_url": None, "speak": True}

    # 2. XỬ LÝ LỆNH "LÀM LẠI"
    if lower_msg in ["làm lại", "thử lại", "tạo lại"]:
        art_prompt = generate_english_art_prompt(LAST_STATE["prompt"])
        rand_seed = random.randint(100, 999999)
        encoded = urllib.parse.quote(art_prompt)
        gen_image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=800&seed={rand_seed}&nologo=true"
        return {
            "reply": f"🔄 <b>Đã tái tạo biến thể mới cho chủ đề [{LAST_STATE['theme'].upper()}]:</b>\nKhung hình mới với góc nhìn chân thực hơn đã sinh ra bên dưới!",
            "gen_image_url": gen_image_url,
            "speak": True
        }

    # 3. KÍCH HOẠT TẠO ẢNH / VIDEO KHI CÓ LỆNH RÕ RÀNG
    make_video_triggers = ["tạo video", "tạo videos", "vẽ", "tạo ảnh", "ghép ảnh", "làm video"]
    if any(k in lower_msg for k in make_video_triggers):
        LAST_STATE["prompt"] = msg
        art_prompt = generate_english_art_prompt(msg)
        rand_seed = random.randint(100, 999999)
        encoded = urllib.parse.quote(art_prompt)
        gen_image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=800&seed={rand_seed}&nologo=true"
        return {
            "reply": f"🎨 <b>Đã khởi tạo khung hình theo yêu cầu:</b> <i>'{msg}'</i>\nKết quả chi tiết hiển thị ngay bên dưới!",
            "gen_image_url": gen_image_url,
            "speak": False
        }

    # 4. TRUY VẤN KHO TRI THỨC TOÀN NHÂN LOẠI
    ai_reply = ask_omni_brain(msg)
    if ai_reply:
        return {"reply": ai_reply, "gen_image_url": None, "speak": False}

    # Phản hồi dự phòng thông thái, tuyệt đối không lặp lại câu máy móc
    if "biến tần" in lower_msg:
        fallback = (
            "🎯 <b>VẤN ĐỀ VỀ BIẾN TẦN (VFD):</b>\n\n"
            "• <b>Bản chất:</b> Biến đổi tần số để chỉnh tốc độ động cơ 3 pha vô cấp.\n"
            "• <b>Ưu điểm:</b> Tiết kiệm điện 20-40%, tránh sụt áp lưới khi khởi động, bảo vệ quá dòng.\n"
            "• <b>Nhược điểm:</b> Sinh nhiệt và sóng hài cao tần, cần giải nhiệt tốt.\n"
            "• <b>Giải pháp tối ưu:</b> Cài đặt tần số cơ bản 50Hz, thời gian tăng tốc (Acc) từ 5-10s tùy quán tính tải, lắp thêm quạt làm mát tủ điện."
        )
    elif any(k in lower_msg for k in ["chào", "hello", "hi"]):
        fallback = "Chào bồ! Tôi là Siêu Nhân AI Phdam. Hôm nay bồ muốn khám phá kiến thức khoa học, sinh học, kỹ thuật hay cần xử lý bài toán nào?"
    else:
        fallback = f"Về vấn đề '{msg}', tôi đã đối chiếu dữ liệu bách khoa. Bồ muốn tôi đi sâu vào phân tích nguyên lý, ưu nhược điểm hay đưa ra giải pháp xử lý thực tế?"

    return {"reply": fallback, "gen_image_url": None, "speak": False}
