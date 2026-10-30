from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import os
import re
import urllib.request
import urllib.parse
import random

app = FastAPI(title="AI Phdam Universal Polymath")

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

MASTER_SYSTEM_PROMPT = (
    "Bạn là SIÊU TRÍ TUỆ NHÂN TẠO PHDAM (Universal Polymath & Senior Consultant). "
    "Bạn nắm giữ kho tàng tri thức khổng lồ của nhân loại về: Tự động hóa, Cơ điện tử, Biến tần, Viễn thông, IoT, Công nghệ AI, Vật lý, Toán học và Đời sống.\n\n"
    "NGUYÊN TẮC TƯ DUY 4 BƯỚC BẮT BUỘC KHI TRẢ LỜI:\n"
    "1. 🎯 NHẬN DIỆN CHÍNH XÁC: Nhìn nhận thẳng vào đối tượng/hình ảnh/câu hỏi, đọc đúng số liệu, chỉ rõ bản chất sự việc.\n"
    "2. ⚖️ PHÂN TÍCH ƯU - NHƯỢC ĐIỂM / NGUYÊN NHÂN: Mổ xẻ chi tiết mặt mạnh, mặt yếu, rủi ro tiềm ẩn hoặc nguyên nhân gốc rễ.\n"
    "3. 💡 PHƯƠNG ÁN XỬ LÝ TỐI ƯU NHẤT: Đưa ra giải pháp xuất sắc nhất (hiệu quả cao nhất, chi phí thấp nhất, an toàn và bền vững nhất).\n"
    "4. 🛠️ HƯỚNG DẪN THỰC THI TỪNG BƯỚC: Hướng dẫn người dùng thao tác cụ thể, rõ ràng, thực tế và chuẩn xác từng thông số.\n\n"
    "Phong thái: Đẳng cấp chuyên gia đầu ngành, tư duy sắc bén, dùng tiếng Việt trong sáng, mạch lạc, tôn trọng và tận tâm với người dùng."
)

def ask_vision_ai(prompt: str, image_data_url: str = None):
    """Mắt Thần Thị Giác kết hợp Kho Tri Thức Toàn Cầu"""
    try:
        url = "https://text.pollinations.ai/"
        headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        
        user_content = []
        task_instruction = (
            f"Quan sát thật kỹ bức ảnh này và áp dụng kho tri thức để trả lời câu hỏi: '{prompt}'.\n"
            "Nếu có con số/chữ viết, hãy đọc thật chuẩn xác từng ký tự. "
            "Sau đó phân tích sâu sắc ưu nhược điểm và đưa ra giải pháp tốt nhất."
        )
        user_content.append({"type": "text", "text": task_instruction})
            
        if image_data_url:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": image_data_url}
            })

        payload = {
            "messages": [
                {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                {"role": "user", "content": user_content if image_data_url else prompt}
            ],
            "model": "openai"
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=18) as res:
            out = res.read().decode("utf-8").strip()
            if out and len(out) > 5 and not out.startswith("<"):
                return out
    except Exception:
        pass
    return None

def ask_superhuman_brain(prompt: str):
    """Gọi Não Bộ Toàn Cầu tư duy phân tích đa tầng"""
    try:
        url = "https://text.pollinations.ai/"
        headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        payload = {
            "messages": [
                {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "model": "openai"
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=18) as res:
            out = res.read().decode("utf-8").strip()
            if out and len(out) > 5 and not out.startswith("<"):
                return out
    except Exception:
        pass
    
    # Dự phòng đường truyền GET
    try:
        encoded = urllib.parse.quote(prompt[:500])
        url_get = f"https://text.pollinations.ai/{encoded}?model=openai"
        req_get = urllib.request.Request(url_get, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_get, timeout=9) as res_get:
            out_get = res_get.read().decode("utf-8").strip()
            if out_get and len(out_get) > 5 and not out_get.startswith("<"):
                return out_get
    except Exception:
        pass
    return None

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
    else:
        cleaned = re.sub(r'(tạo videos?|tạo ảnh|vẽ|ghép|làm lại|cho tôi|giúp tôi|tôi đang)\s*', '', m).strip()
        if not cleaned:
            cleaned = "industrial automation engineer at work"
        return f"{cleaned}, professional lighting, highly detailed, photorealistic 4k"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Siêu Nhân AI Phdam - Kho Tri Thức Toàn Cầu</title>
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
            max-width: 90%;
            padding: 12px 14px;
            border-radius: 14px;
            font-size: 14px;
            line-height: 1.55;
            word-break: break-word;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        }
        .msg.bot {
            background: rgba(30, 41, 59, 0.94);
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
                <p>Kho Tri Thức Toàn Cầu • Phân Tích Đa Chiều</p>
            </div>
            <div class="header-actions">
                <button class="btn-tool" onclick="document.getElementById('bgInput').click()">🖼️ Đổi nền</button>
                <button class="btn-tool" onclick="resetBg()">↺ Nền gốc</button>
            </div>
        </div>

        <div class="chat-stream" id="chatStream">
            <div class="msg bot">
                Chào bồ! Tôi là <b>Siêu Nhân Trí Tuệ Nhân Tạo AI Phdam</b>.<br><br>
                🌐 <b>ĐÃ KÍCH HOẠT KHO TRI THỨC TOÀN CẦU & TƯ DUY 4 BƯỚC:</b><br>
                • Bồ có thể hỏi bất cứ vấn đề kỹ thuật, cơ điện, đời sống hoặc gửi ảnh lên.<br>
                • Tôi sẽ <b>nhận diện bản chất ➔ phân tích ưu nhược điểm ➔ đưa ra giải pháp xử lý tốt nhất và hướng dẫn từng bước</b> cho bồ!
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

            <input type="text" id="chatInput" class="chat-input" placeholder="Hỏi giải pháp kỹ thuật, phân tích ưu nhược điểm..." autocomplete="off">

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
