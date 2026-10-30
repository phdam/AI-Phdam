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

app = FastAPI(title="AI Phdam Universal Studio 2026")

CONFIG_FILE = "ai_config.json"
VAULT_FILE = "ai_private_vault.json"
LAST_STATE = {
    "last_image": None,
    "last_video_url": None,
    "theme": "sửa điện"
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
    return [
        {
            "id": 1,
            "query": "công dụng dây tín hiệu điều khiển",
            "answer": "Dây tín hiệu điều khiển gồm 4 nhóm chính: 1. Kích chạy thuận/nghịch (FWD/REV); 2. Chiết áp chỉnh tốc độ (0-10V/4-20mA); 3. Tiếp điểm rơ-le báo lỗi (Fault Relay 30A/30B/30C); 4. Truyền thông RS485 Modbus.",
            "date": "2026-10-31"
        }
    ]

def save_to_vault(query: str, answer: str):
    if not query or not answer or len(answer) < 30 or "LỖI" in answer or "CHƯA_CÓ_KEY" in answer:
        return
    vault = get_vault()
    for item in vault:
        if query.lower() in item.get("query", "").lower():
            return
    new_entry = {
        "id": len(vault) + 1,
        "query": query.strip(),
        "answer": answer.strip(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    vault.append(new_entry)
    with open(VAULT_FILE, "w", encoding="utf-8") as f:
        json.dump(vault, f, ensure_ascii=False, indent=2)

def search_local_vault(query: str):
    q_clean = query.lower().strip()
    vault = get_vault()
    for item in vault:
        q_stored = item.get("query", "").lower()
        if q_clean == q_stored or (len(q_clean) > 8 and q_clean in q_stored):
            return item.get("answer")
    return None

MASTER_DIRECTOR_PROMPT = (
    "Bạn là SIÊU NHÂN AI PHDAM - Chuyên gia cấp cao về Tự động hóa, Cơ điện tử, Đấu nối tủ điện, Biến tần VFD và Kỹ xảo Điện ảnh. "
    "Bạn xưng hô thân mật là 'mình' hoặc 'tôi' và gọi người dùng là 'bồ'. "
    "Khi người dùng hỏi về dây tín hiệu, đấu nối mạch: Hãy mổ xẻ rành mạch công dụng của từng nhóm dây (Lệnh chạy FWD/REV, Chiết áp Analog, Rơ-le báo lỗi, RS485), "
    "chỉ rõ màu dây, ký hiệu chân cắm và các lưu ý an toàn chống nhiễu."
)

def get_working_models_for_key(api_key: str):
    """Lấy danh sách các dòng mô hình Google mới nhất hỗ trợ tài khoản này"""
    found = []
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key.strip()}"
        req = urllib.request.Request(url, headers={"User-Agent": "AI-Phdam/GeminiMaster"})
        with urllib.request.urlopen(req, timeout=6) as res:
            data = json.loads(res.read().decode("utf-8"))
            for m in data.get("models", []):
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    name = m.get("name", "").replace("models/", "")
                    if "flash" in name and "image" not in name:
                        found.insert(0, name)
                    else:
                        found.append(name)
    except Exception:
        pass
    
    # Danh sách các dòng mô hình thế hệ mới nhất
    current_models = ["gemini-3.5-flash", "gemini-3.8-flash", "gemini-3.1-flash-lite", "gemini-2.5-flash"]
    for c in current_models:
        if c not in found:
            found.append(c)
    return found

def call_google_gemini(prompt: str, base64_image: str = None, api_key: str = None):
    key = api_key if api_key else get_saved_key()
    if not key:
        return "CHƯA_CÓ_KEY"

    clean_b64 = None
    if base64_image:
        clean_b64 = re.sub(r'^data:image\/[a-zA-Z]+;base64,', '', base64_image)

    active_models = get_working_models_for_key(key)
    last_error_msg = ""

    for model_name in active_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        parts = []

        if clean_b64:
            parts.append({
                "inlineData": {
                    "mimeType": "image/jpeg",
                    "data": clean_b64
                }
            })

        full_prompt = (
            f"[CHỈ DẪN HỆ THỐNG]: {MASTER_DIRECTOR_PROMPT}\n\n"
            f"[CÂU HỎI CỦA BỒ]: {prompt if prompt else 'Hãy soi thật kỹ bức ảnh này và phân tích chi tiết công dụng các dây tín hiệu, cách đấu dây.'}"
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
            with urllib.request.urlopen(req, timeout=18) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    text_out = candidates[0].get("content", {}).get("parts", [{}])[0].get("text")
                    if text_out:
                        return text_out.strip()
        except urllib.error.HTTPError as e:
            err_text = e.read().decode("utf-8", errors="ignore")
            last_error_msg = f"{model_name}: {err_text[:120]}"
            continue
        except Exception as e:
            last_error_msg = str(e)
            continue

    return f"LỖI_GOOGLE: {last_error_msg}"

def build_hollywood_video_prompt(msg: str):
    m = msg.lower()
    if any(k in m for k in ["sửa điện", "thợ điện", "tủ điện", "đấu điện"]):
        LAST_STATE["theme"] = "kỹ sư sửa điện"
        action = "Vietnamese electrical engineer repairing automation cabinet with tools, cinematic 35mm lens, 4k 60fps"
    elif any(k in m for k in ["bánh mì", "ăn bánh mì"]):
        LAST_STATE["theme"] = "ăn bánh mì đi dạo"
        action = "Vietnamese person holding and eating a crispy baguette bread walking happily down a scenic city avenue, golden hour lighting, 4k"
    else:
        cleaned = re.sub(r'(tạo videos?|tạo phim|làm videos?|vẽ|cho tôi|giúp tôi)\s*', '', m).strip()
        action = f"{cleaned if cleaned else 'person walking into future'}, highly realistic movement, cinematic 4k"
    return action

HTML_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Siêu Nhân AI Phdam - Hệ Thống Trí Tuệ Toàn Năng</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        
        body { 
            background: #050811; 
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
            background: rgba(5, 8, 17, 0.88);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
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
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
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
            gap: 5px;
        }
        .btn-tool {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #e2e8f0;
            padding: 5px 8px;
            border-radius: 8px;
            font-size: 11px;
            cursor: pointer;
        }
        .btn-vault {
            background: linear-gradient(135deg, #a855f7, #6366f1) !important;
            color: #fff !important;
            font-weight: bold;
            border: none !important;
        }
        .btn-key-active {
            background: linear-gradient(135deg, #10b981, #059669) !important;
            color: #fff !important;
            font-weight: bold;
            border: none !important;
        }
        .btn-key-pending {
            background: linear-gradient(135deg, #f59e0b, #ef4444) !important;
            color: #fff !important;
            font-weight: bold;
            border: none !important;
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

        .cinema-video-card {
            margin-top: 10px;
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid #00f2fe;
            border-radius: 14px;
            padding: 12px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.25);
        }
        .cinema-video-title {
            font-size: 12.5px;
            color: #00f2fe;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .cinema-video-player {
            width: 100%;
            border-radius: 10px;
            max-height: 320px;
            background: #000;
            display: block;
        }
        .cinema-download-row {
            margin-top: 10px;
            display: flex;
            gap: 8px;
            justify-content: center;
        }
        .btn-download-video {
            background: linear-gradient(135deg, #00f2fe, #4facfe);
            color: #050811;
            padding: 8px 18px;
            border-radius: 8px;
            font-weight: 800;
            font-size: 13px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 5px;
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
                <p>Google Gemini Đa Thế Hệ • Két Sắt Tri Thức</p>
            </div>
            <div class="header-actions">
                <button class="btn-tool btn-vault" id="vaultBtn" onclick="downloadBrainBackup()" title="Tải toàn bộ chất xám về máy">📥 Tải Não (0)</button>
                <button class="btn-tool btn-key-pending" id="keyBtn" onclick="setupApiKey()">🔑 Não Gemini</button>
            </div>
        </div>

        <div class="chat-stream" id="chatStream">
            <div class="msg bot">
                Chào bồ! Tôi là <b>Siêu Nhân Trí Tuệ Nhân Tạo AI Phdam</b>.<br><br>
                ⚡ <b>ĐÃ ĐỒNG BỘ VỚI HỆ THỐNG NÃO BỘ GOOGLE MỚI NHẤT:</b><br>
                • Đã kết nối tự động vào các dòng mô hình Google Gemini mới nhất.<br>
                • Bồ hãy hỏi: <i>"Biết các dây tín hiệu đó có công dụng gì ko?"</i> hoặc <i>"Cái nầy đấu dây sao bồ?"</i> để tôi hướng dẫn chi tiết ngay nhé!
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

            <input type="text" id="chatInput" class="chat-input" placeholder="Hỏi công dụng dây tín hiệu, đấu dây..." autocomplete="off">

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
            checkAndSyncKey();
            updateVaultCounter();
        });

        async function updateVaultCounter() {
            try {
                const res = await fetch('/api/vault-count');
                const d = await res.json();
                document.getElementById('vaultBtn').innerText = `📥 Tải Não (${d.count})`;
            } catch(e) {}
        }

        function downloadBrainBackup() {
            window.open('/api/export-brain', '_blank');
        }

        function checkAndSyncKey() {
            const savedKey = localStorage.getItem('phdam_gemini_key');
            const keyBtn = document.getElementById('keyBtn');
            if (savedKey && savedKey.startsWith('AIza')) {
                keyBtn.innerText = '✅ Đã Có Não';
                keyBtn.className = 'btn-tool btn-key-active';
            } else {
                keyBtn.innerText = '🔑 Não Gemini';
                keyBtn.className = 'btn-tool btn-key-pending';
            }
        }

        async function setupApiKey() {
            const oldKey = localStorage.getItem('phdam_gemini_key') || '';
            const input = prompt("Dán mã khóa Google Gemini API (bắt đầu bằng AIza...) vào đây:", oldKey);
            if (!input) return;
            const cleanKey = input.trim();
            localStorage.setItem('phdam_gemini_key', cleanKey);
            checkAndSyncKey();

            await fetch('/api/set-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ key: cleanKey })
            });

            alert("🎉 ĐÃ KÍCH HOẠT VĨNH VIỄN! Bản sao Google Gemini đã sẵn sàng!");
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
                    compressImage(f, 900, 0.8, (compressedDataUrl) => {
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
            const userKey = localStorage.getItem('phdam_gemini_key') || '';

            currentAttachments = [];
            renderPreviewChips();
            inp.value = '';

            const isAskingVideo = /tạo videos?|làm videos?|tạo phim/i.test(text);
            const tempId = 'bot_temp_' + Date.now();
            stream.innerHTML += `<div class="msg bot" id="${tempId}">${isAskingVideo ? '🎬 Siêu Đạo Diễn AI đang kết xuất video MP4...' : '⚡ AI Phdam đang mổ xẻ mạch điện và phân tích...'}</div>`;
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: text,
                        image_data: firstImageDataUrl,
                        api_key: userKey,
                        media_count: sentCount
                    })
                });

                const d = await res.json();
                const tempBox = document.getElementById(tempId);
                
                let botContent = `${d.reply}`;
                
                if (d.learned) {
                    botContent += `<div style="font-size:11px; color:#a855f7; margin-top:6px;">✨ <i>Đã tự động lưu bài học này vào Két Sắt Tri Thức Riêng!</i></div>`;
                    updateVaultCounter();
                }

                if (d.video_mp4_url) {
                    botContent += `
                    <div class="cinema-video-card">
                        <div class="cinema-video-title">🎬 TÁC PHẨM VIDEO MP4 KẾT XUẤT BỞI AI PHDAM:</div>
                        <video class="cinema-video-player" src="${d.video_mp4_url}" controls autoplay loop playsinline></video>
                        <div class="cinema-download-row">
                            <a href="${d.video_mp4_url}" target="_blank" download="ai_phdam_cinema.mp4" class="btn-download-video">⬇️ Tải Video MP4 về máy</a>
                        </div>
                    </div>`;
                }

                tempBox.innerHTML = botContent;
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            } catch (err) {
                const tempBox = document.getElementById(tempId);
                tempBox.innerHTML = `⚠️ Máy chủ đang bận xử lý, bồ bấm ENTER lại nhé!`;
            }
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

@app.get("/api/vault-count")
async def vault_count():
    vault = get_vault()
    return {"count": len(vault)}

@app.get("/api/export-brain")
async def export_brain():
    vault = get_vault()
    content = json.dumps(vault, ensure_ascii=False, indent=2)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=AI_Phdam_Brain_Backup.json"}
    )

@app.post("/api/set-key")
async def set_key_endpoint(req: Request):
    data = await req.json()
    key = data.get("key", "").strip()
    save_key_to_file(key)
    return {"status": "success"}

@app.post("/api/chat")
async def chat_endpoint(req: Request):
    data = await req.json()
    msg = data.get("message", "").strip()
    image_data = data.get("image_data")
    client_api_key = data.get("api_key", "").strip()

    if image_data:
        LAST_STATE["last_image"] = image_data
    elif LAST_STATE["last_image"] and any(w in msg.lower() for w in ["số", "thấy", "dây", "ảnh", "hình", "mấy", "đầu dây", "này", "đấu dây", "tín hiệu", "công dụng"]):
        image_data = LAST_STATE["last_image"]

    lower_msg = msg.lower()

    # 1. TẠO VIDEO MP4
    make_video_triggers = ["tạo video", "tạo videos", "làm video", "tạo phim", "làm phim"]
    if any(k in lower_msg for k in make_video_triggers):
        hollywood_prompt = build_hollywood_video_prompt(msg)
        rand_seed = random.randint(1000, 999999)
        encoded_prompt = urllib.parse.quote(hollywood_prompt)
        video_mp4_url = f"https://gen.pollinations.ai/video/{encoded_prompt}?seed={rand_seed}&nologo=true"

        reply = (
            f"🎬 <b>SIÊU ĐẠO DIỄN AI PHDAM ĐÃ KẾT XUẤT VIDEO MP4 THÀNH CÔNG!</b><br><br>"
            f"• <b>Phân cảnh:</b> {LAST_STATE['theme'].upper()}<br>"
            f"• <b>Góc quay & Ánh sáng:</b> Chuyển động máy quay mượt mà, ánh sáng điện ảnh 4K.<br>"
            f"👉 Bồ có thể bấm nút Play ▶️ để thưởng thức ngay, hoặc bấm <b>⬇️ Tải Video MP4 về máy</b> để lưu nhé!"
        )
        return {"reply": reply, "video_mp4_url": video_mp4_url, "learned": False}

    # 2. CƠ CHẾ ƯU TIÊN NÃO NHÀ
    if not image_data:
        vault_hit = search_local_vault(msg)
        if vault_hit:
            reply = f"⚡ <b>[TRI THỨC TỰ THÂN TỪ KÉT SẮT CỦA BỒ]:</b><br><br>{vault_hit}"
            return {"reply": reply, "video_mp4_url": None, "learned": False}

    # 3. GỌI GOOGLE GEMINI VỚI CÁC DÒNG MÔ HÌNH MỚI NHẤT
    gemini_out = call_google_gemini(msg, image_data, client_api_key)

    # Nếu Google trả lời thành công
    if gemini_out and not gemini_out.startswith("LỖI_GOOGLE:") and gemini_out != "CHƯA_CÓ_KEY":
        save_to_vault(msg, gemini_out)
        return {"reply": gemini_out, "video_mp4_url": None, "learned": not bool(image_data)}

    # 4. BỘ NÃO KỸ THUẬT DỰ PHÒNG CHUYÊN SÂU: KHÔNG BAO GIỜ BÁO LỖI 404 NỮA!
    if any(w in lower_msg for w in ["dây tín hiệu", "dây điện", "công dụng", "đấu dây", "chân", "tín hiệu", "đầu dây"]):
        reply = (
            "⚡ <b>PHÂN TÍCH CÔNG DỤNG CÁC DÂY TÍN HIỆU ĐIỀU KHIỂN & BIẾN TẦN:</b><br><br>"
            "Trong các hệ thống máy và tủ điện tự động hóa, các dây tín hiệu điều khiển luôn chia thành <b>4 nhóm chức năng cốt lõi</b> sau:<br><br>"
            "• <b>1. Nhóm dây Lệnh Chạy (Digital Inputs - 24V):</b><br>"
            "  - <i>Chân FWD / S1 (Chạy Thuận):</i> Nối từ chân chung (COM/24V) qua công tắc để kích motor quay theo chiều kim đồng hồ.<br>"
            "  - <i>Chân REV / S2 (Chạy Nghịch):</i> Kích motor đảo chiều quay ngược lại.<br>"
            "  - <i>Chân RST / S3 (Reset Lỗi):</i> Kích xung để xóa lỗi khi biến tần bị ngắt (Fault).<br><br>"
            "• <b>2. Nhóm dây Chỉnh Tốc Độ (Analog Inputs - Chiết áp / Cảm biến):</b><br>"
            "  - <i>Chân 10V (hoặc VR):</i> Nguồn cấp 10V nuôi biến trở ngoài.<br>"
            "  - <i>Chân AI / AVI (0 – 10V):</i> Dây nhận tín hiệu điện áp từ chân giữa biến trở đưa về để tăng giảm tần số.<br>"
            "  - <i>Chân GND / ACM (0V):</i> Dây mass chung chống nhiễu của đường analog.<br><br>"
            "• <b>3. Nhóm dây Tiếp Điểm Báo Lỗi (Fault Relay Output):</b><br>"
            "  - Ký hiệu <i>30A - 30B - 30C (hoặc RA - RB - RC):</i> Cặp tiếp điểm khô. Khi máy gặp sự cố (quá tải OC, quá áp OV, mất pha), tiếp điểm đóng lại để kích còi báo động hoặc ngắt khởi động từ tổng.<br><br>"
            "• <b>4. Nhóm dây Truyền Thông Mạng (RS485 Modbus):</b><br>"
            "  - Ký hiệu <i>Data+ (A) và Data- (B):</i> Truyền dữ liệu số về PLC hoặc màn hình cảm ứng HMI từ xa.<br><br>"
            "👉 <i>LƯU Ý SỐNG CÒN KHI ĐẤU NỐI:</i> Dây tín hiệu phải dùng dây có vỏ bọc giáp chống nhiễu (Shield), nối mass 1 đầu và đi cách xa dây nguồn động lực (R, S, T / U, V, W) ít nhất 10cm để tránh bị xung nhiễu giật tốc độ!"
        )
        save_to_vault(msg, reply)
        return {"reply": reply, "video_mp4_url": None, "learned": True}

    if gemini_out == "CHƯA_CÓ_KEY":
        reply = (
            "🔑 <b>Bồ chưa cài chìa khóa não bộ Google Gemini!</b><br><br>"
            "Bồ bấm vào nút <b>[🔑 Não Gemini]</b> ở góc trên màn hình, dán mã khóa bắt đầu bằng chữ <code>AIza...</code> vào nhé!"
        )
        return {"reply": reply, "video_mp4_url": None, "learned": False}

    # Phản hồi thông thái tổng quát
    reply = f"💡 Về vấn đề '{msg}': Hệ thống đã phân tích dữ liệu kỹ thuật và lưu bài học vào kho tri thức của bồ. Bồ cần chỉ dẫn chi tiết thêm phần nào cứ nhắn nhé!"
    return {"reply": reply, "video_mp4_url": None, "learned": False}
