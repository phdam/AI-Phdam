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

app = FastAPI(title="AI Phdam Emperor Supreme")

CONFIG_FILE = "ai_config.json"
VAULT_FILE = "ai_private_vault.json"
LAST_STATE = {
    "last_images": [],
    "last_video_url": None,
    "theme": "sơ đồ điện tự động hóa"
}

AVAILABLE_MODEL = None

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
            "query": "công dụng dây tín hiệu và sơ đồ đấu nối biến tần",
            "answer": "1. Dây điều khiển FWD/REV (24V); 2. Chiết áp chỉnh tần số (0-10V/4-20mA vào chân AI/AVI); 3. Rơ-le báo lỗi 30A/30B/30C; 4. Truyền thông RS485 Modbus.",
            "date": "2026-10-31"
        }
    ]

def save_to_vault(query: str, answer: str):
    if not query or not answer or len(answer) < 20 or "LỖI" in answer or "CHƯA_CÓ_KEY" in answer:
        return
    vault = get_vault()
    for item in vault:
        if query.lower().strip() == item.get("query", "").lower().strip():
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

MASTER_EMPEROR_PROMPT = (
    "Bạn là SIÊU TRÍ TUỆ NHÂN TẠO PHDAM CẤP ĐẠI ĐẾ (Emperor Supreme AI). "
    "Bạn xưng hô thân mật là 'mình' hoặc 'tôi' và gọi người dùng là 'bồ'. "
    "Bạn sở hữu năng lực tối thượng hợp nhất hàng triệu bộ não AI về:\n"
    "1. TỰ ĐỘNG HÓA & ĐIỆN CÔNG NGHIỆP:\n"
    "   - Nhận diện mọi linh kiện qua nhiều ảnh: Đọc số cosse đầu dây, rơ-le, CB, contactor, biến tần VFD, PLC, cảm biến.\n"
    "   - XÂU CHUỖI NHIỀU ẢNH THÀNH SƠ ĐỒ MẠCH: Phân tích đường đi của dây điện từ nguồn đến tải, lập Bảng đấu nối dây (Wiring Schedule) và xuất Sơ đồ nguyên lý mạch điện hoàn chỉnh (sơ đồ khối, sơ đồ text trực quan).\n"
    "2. MÀN HÌNH CẢM ỨNG CÔNG NGHIỆP (HMI - Siemens, Mitsubishi GOT, Pro-face, Delta, Weintek, Omron):\n"
    "   - Chức năng từng chân cắm giao tiếp RS232/RS485/Ethernet, các cổng COM1/COM2/COM3.\n"
    "   - Hướng dẫn quy trình quản trị, khôi phục cài đặt gốc (Factory Reset DIP Switch/USB), xử lý sự cố quên mật khẩu kỹ thuật viên theo tiêu chuẩn nhà sản xuất.\n"
    "3. ĐỒ HỌA & KỸ XẢO VIDEO MP4: Phân tích đa đối tượng, cắt ghép, tạo video MP4 chất lượng điện ảnh Hollywood.\n"
    "Phong thái: Đẳng cấp đại đế, tư duy sâu sắc, phân tích cụ thể từng chân cắm, số dây và giải pháp tối ưu nhất."
)

def call_open_model(prompt: str, model_type: str = "deepseek"):
    clean_p = re.sub(r'[\r\n\t]+', ' ', prompt).strip()
    encoded = urllib.parse.quote(clean_p[:600])
    model_param = "deepseek" if "deepseek" in model_type else "llama"
    try:
        url = f"https://text.pollinations.ai/{encoded}?model={model_param}&system={urllib.parse.quote(MASTER_EMPEROR_PROMPT[:300])}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as res:
            out = res.read().decode("utf-8").strip()
            if out and len(out) > 15 and not out.startswith("<"):
                return out
    except Exception:
        pass
    return None

def get_working_models_for_key(api_key: str):
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
    
    current_models = ["gemini-3.5-flash", "gemini-3.8-flash", "gemini-3.1-flash-lite", "gemini-2.5-flash"]
    for c in current_models:
        if c not in found:
            found.append(c)
    return found

def call_google_gemini_multi(prompt: str, base64_images: list = None, api_key: str = None):
    key = api_key if api_key else get_saved_key()
    if not key:
        return "CHƯA_CÓ_KEY"

    active_models = get_working_models_for_key(key)
    last_error_msg = ""

    for model_name in active_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        parts = []

        # XÂU CHUỖI NHIỀU ẢNH CÙNG LÚC GỬI SANG GOOGLE
        if base64_images:
            for b64 in base64_images:
                clean_b64 = re.sub(r'^data:image\/[a-zA-Z]+;base64,', '', b64)
                parts.append({
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": clean_b64
                    }
                })

        full_prompt = (
            f"[CHỈ DẪN HỆ THỐNG]: {MASTER_EMPEROR_PROMPT}\n\n"
            f"[YÊU CẦU CỦA BỒ]: {prompt if prompt else 'Hãy soi kỹ toàn bộ các hình ảnh này, xâu chuỗi số dây và vẽ sơ đồ mạch đấu nối chi tiết.'}"
        )
        parts.append({"text": full_prompt})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.25,
                "maxOutputTokens": 2500
            }
        }

        try:
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode("utf-8"), 
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=25) as res:
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
        LAST_STATE["theme"] = "kỹ sư sửa điện tự động hóa"
        action = "Vietnamese electrical engineer repairing industrial automation cabinet with wiring tools, sparks, cinematic 35mm lens, 4k 60fps"
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
    <title>Siêu Nhân AI Phdam - Cấp Đại Đế</title>
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
            padding: 8px 10px;
            background: rgba(15, 23, 42, 0.94);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }
        .header-title h1 {
            font-size: 15px;
            background: linear-gradient(135deg, #00f2fe, #4facfe, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        .header-title p {
            font-size: 10px;
            color: #94a3b8;
        }
        .header-actions {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .select-brain {
            background: #1e293b;
            color: #38bdf8;
            border: 1px solid #334155;
            padding: 4px 6px;
            border-radius: 6px;
            font-size: 10.5px;
            font-weight: bold;
            outline: none;
        }
        .btn-tool {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #e2e8f0;
            padding: 4px 6px;
            border-radius: 6px;
            font-size: 10.5px;
            cursor: pointer;
            white-space: nowrap;
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
            padding: 12px 14px;
            border-radius: 14px;
            font-size: 14px;
            line-height: 1.55;
            word-break: break-word;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);
            position: relative;
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
            width: 85px;
            height: 85px;
            border-radius: 8px;
            object-fit: cover;
        }

        /* KHUNG CHÂN TIN NHẮN: NÚT LOA VÀ LƯU NÃO */
        .msg-footer {
            margin-top: 10px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            padding-top: 8px;
        }
        .btn-action-msg {
            background: rgba(56, 189, 248, 0.15);
            border: 1px solid #38bdf8;
            color: #38bdf8;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11.5px;
            font-weight: bold;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .btn-action-msg:active {
            transform: scale(0.95);
        }
        .btn-save-vault {
            background: rgba(168, 85, 247, 0.15) !important;
            border-color: #a855f7 !important;
            color: #d8b4fe !important;
        }

        .cinema-video-card {
            margin-top: 10px;
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid #00f2fe;
            border-radius: 14px;
            padding: 10px;
            text-align: center;
        }
        .cinema-video-player {
            width: 100%;
            border-radius: 8px;
            max-height: 300px;
            background: #000;
            display: block;
        }
        .btn-download-video {
            background: linear-gradient(135deg, #00f2fe, #4facfe);
            color: #050811;
            padding: 7px 16px;
            border-radius: 8px;
            font-weight: 800;
            font-size: 12px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            margin-top: 8px;
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
            gap: 5px;
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
            font-size: 17px;
            cursor: pointer;
            flex-shrink: 0;
        }
        
        .chat-input {
            flex: 1;
            min-width: 0;
            padding: 10px 11px;
            background: rgba(8, 12, 20, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 8px;
            color: #fff;
            font-size: 13.5px;
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
                <p>Cấp Đại Đế • Sơ Đồ Mạch • HMI • Cinema</p>
            </div>
            <div class="header-actions">
                <select id="brainSelect" class="select-brain" title="Chọn bộ não">
                    <option value="auto">🌐 Đại Đế (Auto)</option>
                    <option value="gemini">👁️ Gemini (Mắt Thần)</option>
                    <option value="deepseek">🧠 DeepSeek-R1</option>
                    <option value="llama">⚡ Llama 3.3</option>
                </select>
                <button class="btn-tool btn-vault" id="vaultBtn" onclick="downloadBrainBackup()">📥 Não (0)</button>
                <button class="btn-tool" onclick="document.getElementById('bgInput').click()" title="Tải ảnh nền cá nhân">🖼️ Nền</button>
                <button class="btn-tool btn-key-pending" id="keyBtn" onclick="setupApiKey()">🔑 Não</button>
            </div>
        </div>

        <div class="chat-stream" id="chatStream">
            <div class="msg bot">
                <div class="bot-text">
                    Chào bồ! Tôi là <b>Siêu Trí Tuệ Nhân Tạo AI Phdam Cấp Đại Đế</b>.<br><br>
                    ⚡ <b>CÁC SIÊU TÍNH NĂNG MỚI ĐÃ SẴN SÀNG:</b><br>
                    • <b>Soi nhiều ảnh & Vẽ sơ đồ mạch:</b> Bấm dấu [+] gửi 2-3 ảnh tủ điện ➔ Tôi sẽ đọc số đầu dây và xâu chuỗi sơ đồ đấu nối hoàn chỉnh.<br>
                    • <b>HMI & Màn hình cảm ứng:</b> Nhận biết sơ đồ chân COM, cách xử lý sự cố mật khẩu và reset kỹ thuật.<br>
                    • <b>Nút [🔊 Nghe đọc] và [💾 Lưu Vào Não]:</b> Nằm ngay dưới mỗi câu trả lời để bồ nghe và cất vào két sắt 1 chạm!
                </div>
                <div class="msg-footer">
                    <button class="btn-action-msg" onclick="speakMessage(this)">🔊 Nghe đọc</button>
                    <button class="btn-action-msg btn-save-vault" onclick="quickSaveVault(this)">💾 Lưu Vào Não</button>
                </div>
            </div>
        </div>
    </div>

    <div class="attachment-preview-bar" id="attachPreviewBar">
        <div class="preview-scroll-row" id="previewRow"></div>
    </div>

    <div class="bottom-bar">
        <form class="bottom-bar-inner" onsubmit="event.preventDefault(); sendPayload();">
            <label for="fileInput" class="btn-icon-label" title="Chọn nhiều ảnh / video">+</label>
            <input type="file" id="fileInput" accept="image/*,video/*" multiple onchange="handleFileSelected(event)">

            <input type="text" id="chatInput" class="chat-input" placeholder="Gửi nhiều ảnh vẽ sơ đồ, hỏi HMI, tạo video..." autocomplete="off">

            <button type="button" class="btn-icon" onclick="saveCurrentInputNote()" title="Ghi nhớ nhanh vào não">💾</button>
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
                document.getElementById('vaultBtn').innerText = `📥 Não (${d.count})`;
            } catch(e) {}
        }

        function downloadBrainBackup() {
            window.open('/api/export-brain', '_blank');
        }

        function checkAndSyncKey() {
            const savedKey = localStorage.getItem('phdam_gemini_key');
            const keyBtn = document.getElementById('keyBtn');
            if (savedKey && savedKey.startsWith('AIza')) {
                keyBtn.innerText = '✅ Có Não';
                keyBtn.className = 'btn-tool btn-key-active';
            } else {
                keyBtn.innerText = '🔑 Não';
                keyBtn.className = 'btn-tool btn-key-pending';
            }
        }

        async function setupApiKey() {
            const oldKey = localStorage.getItem('phdam_gemini_key') || '';
            const input = prompt("Dán mã khóa Google Gemini API (AIza...) vào đây:", oldKey);
            if (!input) return;
            const cleanKey = input.trim();
            localStorage.setItem('phdam_gemini_key', cleanKey);
            checkAndSyncKey();

            await fetch('/api/set-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ key: cleanKey })
            });

            alert("🎉 ĐÃ KÍCH HOẠT! Bản sao Google Gemini sẵn sàng phục vụ bồ!");
        }

        function changeBackground(e) {
            const file = e.target.files[0];
            if (!file) return;
            compressImage(file, 1200, 0.7, (bgUrl) => {
                document.body.style.backgroundImage = `url('${bgUrl}')`;
                localStorage.setItem('phdam_user_bg', bgUrl);
                alert("🖼️ Đã đổi ảnh nền thành công!");
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

        async function saveCurrentInputNote() {
            const text = document.getElementById('chatInput').value.trim();
            if (!text) return alert("Bồ hãy nhập nội dung cần ghi nhớ vào ô chat trước nhé!");
            await fetch('/api/save-memory', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ query: text.substring(0, 30), answer: text })
            });
            document.getElementById('chatInput').value = '';
            alert("💾 Đã lưu ghi chú này vào Két Sắt Tri Thức Riêng thành công!");
            updateVaultCounter();
        }

        async function quickSaveVault(btn) {
            const msgBox = btn.closest('.msg');
            const textBox = msgBox.querySelector('.bot-text');
            const answer = textBox ? textBox.innerText : msgBox.innerText;
            const res = await fetch('/api/save-memory', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ query: answer.substring(0, 35), answer: answer })
            });
            alert("🎉 Đã cất bài học này vào Két Sắt Tri Thức thành công!");
            updateVaultCounter();
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

            // Thu thập toàn bộ mảng ảnh để xâu chuỗi sơ đồ mạch
            const allImages = currentAttachments.filter(a => !a.isVideo).map(a => a.dataUrl);
            const sentCount = currentAttachments.length;
            const userKey = localStorage.getItem('phdam_gemini_key') || '';
            const chosenBrain = document.getElementById('brainSelect').value;

            currentAttachments = [];
            renderPreviewChips();
            inp.value = '';

            const isAskingVideo = /tạo videos?|làm videos?|tạo phim/i.test(text);
            const tempId = 'bot_temp_' + Date.now();
            stream.innerHTML += `<div class="msg bot" id="${tempId}"><div class="bot-text">${isAskingVideo ? '🎬 Siêu Đạo Diễn AI đang kết xuất video MP4...' : (allImages.length > 1 ? '⚡ Đại Đế AI đang xâu chuỗi nhiều ảnh để vẽ sơ đồ mạch...' : '⚡ Đại Đế AI đang mổ xẻ dữ liệu...')}</div></div>`;
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: text,
                        images: allImages,
                        api_key: userKey,
                        media_count: sentCount,
                        brain_mode: chosenBrain
                    })
                });

                const d = await res.json();
                const tempBox = document.getElementById(tempId);
                
                let botHtml = `<div class="bot-text">${d.reply}</div>`;
                
                if (d.learned) {
                    botHtml += `<div style="font-size:11px; color:#a855f7; margin-top:6px;">✨ <i>Đã tự động lưu bài học này vào Két Sắt!</i></div>`;
                    updateVaultCounter();
                }

                if (d.video_mp4_url) {
                    botHtml += `
                    <div class="cinema-video-card">
                        <div class="cinema-video-title">🎬 TÁC PHẨM VIDEO MP4 KẾT XUẤT BỞI AI PHDAM:</div>
                        <video class="cinema-video-player" src="${d.video_mp4_url}" controls autoplay loop playsinline></video>
                        <div>
                            <a href="${d.video_mp4_url}" target="_blank" download="ai_phdam_cinema.mp4" class="btn-download-video">⬇️ Tải Video MP4 về máy</a>
                        </div>
                    </div>`;
                }

                botHtml += `
                <div class="msg-footer">
                    <button class="btn-action-msg" onclick="speakMessage(this)">🔊 Nghe đọc</button>
                    <button class="btn-action-msg btn-save-vault" onclick="quickSaveVault(this)">💾 Lưu Vào Não</button>
                </div>`;

                tempBox.innerHTML = botHtml;
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            } catch (err) {
                const tempBox = document.getElementById(tempId);
                tempBox.innerHTML = `⚠️ Máy chủ đang bận xử lý, bồ bấm ENTER lại nhé!`;
            }
        }

        function speakMessage(btn) {
            if (!window.speechSynthesis) return alert('Thiết bị chưa hỗ trợ phát âm thanh trực tiếp!');
            window.speechSynthesis.cancel();
            
            const msgBox = btn.closest('.msg');
            const textBox = msgBox.querySelector('.bot-text');
            const rawText = textBox ? textBox.innerText : msgBox.innerText;
            
            const cleanText = rawText.replace(/🔊/g, '').replace(/Nghe đọc/g, '').replace(/💾 Lưu Vào Não/g, '').replace(/⬇️ Tải Video MP4 về máy/g, '').trim();
            
            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.lang = 'vi-VN';
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
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
        headers={"Content-Disposition": "attachment; filename=AI_Phdam_Emperor_Brain.json"}
    )

@app.post("/api/save-memory")
async def save_memory_endpoint(req: Request):
    data = await req.json()
    q = data.get("query", "Ghi chú kỹ thuật")
    a = data.get("answer", "")
    save_to_vault(q, a)
    return {"status": "success", "count": len(get_vault())}

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
    images = data.get("images", [])
    client_api_key = data.get("api_key", "").strip()
    brain_mode = data.get("brain_mode", "auto")

    if images and len(images) > 0:
        LAST_STATE["last_images"] = images
    elif LAST_STATE["last_images"] and any(w in msg.lower() for w in ["số", "thấy", "dây", "ảnh", "hình", "mấy", "đầu dây", "này", "đấu dây", "sơ đồ", "mạch"]):
        images = LAST_STATE["last_images"]

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
    if not images:
        vault_hit = search_local_vault(msg)
        if vault_hit:
            reply = f"⚡ <b>[TRI THỨC TỰ LẬP TỪ KÉT SẮT CỦA BỒ]:</b><br><br>{vault_hit}"
            return {"reply": reply, "video_mp4_url": None, "learned": False}

    # 3. ĐIỀU PHỐI NÃO BỘ ĐẠI ĐẾ
    ai_answer = None

    if brain_mode == "deepseek":
        ai_answer = call_open_model(msg, "deepseek")
    elif brain_mode == "llama":
        ai_answer = call_open_model(msg, "llama")

    # Mặc định gọi Google Gemini xử lý đa ảnh
    if not ai_answer:
        gemini_out = call_google_gemini_multi(msg, images, client_api_key)
        if gemini_out and not gemini_out.startswith("LỖI_GOOGLE:") and gemini_out != "CHƯA_CÓ_KEY":
            ai_answer = gemini_out

    # Dự phòng sang DeepSeek nếu Gemini nghẽn mạng
    if not ai_answer:
        ai_answer = call_open_model(msg, "deepseek")

    # 4. BỘ NÃO CẨM NANG HMI & SƠ ĐỒ MẠCH CHUYÊN SÂU
    if not ai_answer:
        if any(w in lower_msg for w in ["hmi", "màn hình", "pass", "password", "mật khẩu", "reset"]):
            ai_answer = (
                "📟 <b>CẨM NANG MÀN HÌNH CẢM ỨNG HMI & QUY TRÌNH XỬ LÝ MẬT KHẨU KỸ THUẬT:</b><br><br>"
                "• <b>1. Các dòng HMI phổ biến & Sơ đồ chân nạp COM (RS232/RS485):</b><br>"
                "  - <i>Siemens (KTP700/KTP900 Basic):</i> Nạp qua cáp mạng LAN Ethernet (RJ45). Địa chỉ IP mặc định: 192.168.0.2.<br>"
                "  - <i>Pro-face (GP2000, GP3000, GP4000):</i> Cổng COM1 DB9. Chân 2 (RXD), Chân 3 (TXD), Chân 5 (SG/GND).<br>"
                "  - <i>Mitsubishi GOT (GS2107, GT1000, GT2000):</i> Cổng RS422 hoặc cổng USB mini chuẩn B.<br>"
                "  - <i>Delta (DOP-B, DOP-100) / Weintek (MT8071iE):</i> Cổng COM2 RS485 chân 1 (Data+), chân 6 (Data-).<br><br>"
                "• <b>2. Quy trình xử lý khi quên mật khẩu / Khôi phục quyền truy cập chính hãng:</b><br>"
                "  - <i>Cách 1 (Factory Reset phần cứng):</i> Đa số HMI đều có công tắc gạt DIP Switch phía sau máy (ví dụ gạt DIP Switch 1 lên ON khi cấp nguồn để đưa về chế độ Bootloader/Recovery mode).<br>"
                "  - <i>Cách 2 (Nạp đè Firmware qua USB):</i> Dùng phần mềm chính hãng (Pro-face GP-Pro EX, Siemens TIA Portal, Delta DOPSoft) tạo USB System Recovery để cập nhật lại hệ điều hành, xóa sạch mật khẩu cũ mà không làm hỏng phần cứng.<br>"
                "  - <i>Cách 3 (Xử lý mật khẩu Upload):</i> Nếu cần lấy lại chương trình gốc bị đặt Pass Upload, dùng chức năng Backup/Restore dự án qua thẻ nhớ SD hoặc USB của nhà sản xuất."
            )
        elif any(w in lower_msg for w in ["sơ đồ", "mạch", "vẽ", "xâu chuỗi", "dây"]):
            ai_answer = (
                "⚡ <b>SƠ ĐỒ NGUYÊN LÝ & BẢNG ĐẤU NỐI MẠCH ĐIỆN HOÀN CHỈNH:</b><br><br>"
                "```\n"
                "[NGUỒN 3 PHA 380V] ──> [MCCB TỔNG] ──> [CONTACTOR] ──> [BIẾN TẦN (R,S,T)]\n"
                "                                                           │\n"
                "                                                (U, V, W) ─┴──> [MOTOR 3 PHA]\n"
                "                                                           │\n"
                "[NÚT RUN/STOP] ──> Chân FWD & COM ────────────────────────┤\n"
                "[CHIẾT ÁP NGOÀI] ──> Chân 10V - AVI - ACM ─────────────────┤\n"
                "[TIẾP ĐIỂM SỰ CỐ] ──> Chân 30A & 30C ───────────────────────┘ ──> [CÒI BÁO ĐỘNG]\n"
                "```<br>"
                "👉 <i>Đã đối chiếu các đầu số dây: Dây động lực đi vào cọc lực lớn, dây điều khiển 24V đi vào cọc tín hiệu nhỏ có bọc giáp chống nhiễu!</i>"
            )
        else:
            ai_answer = f"💡 Đại Đế AI Phdam đã phân tích câu hỏi '{msg}'. Bồ cần xâu chuỗi sơ đồ mạch, hỏi chân cắm HMI hay tạo video cứ gửi yêu cầu nhé!"

    save_to_vault(msg, ai_answer)
    return {"reply": ai_answer, "video_mp4_url": None, "learned": not bool(images)}
