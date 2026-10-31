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

app = FastAPI(title="AI An Binh Automation Studio")

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

def clean_markdown_to_clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = text.replace('*', '')
    return text

MASTER_AN_BINH_PROMPT = (
    "Bạn là TRÍ TUỆ NHÂN TẠO AI AN BÌNH (AI An Bình). "
    "Bạn xưng hô thân mật là 'tui' hoặc 'mình' và gọi người dùng là 'bồ'. "
    "Bạn sở hữu năng lực phân tích thị giác chuyên sâu và tự động hóa hàng đầu:\n\n"
    "QUY TRÌNH PHÂN TÍCH HÌNH ẢNH & TRÍCH XUẤT CHỮ (OCR CHUYÊN NGHIỆP):\n"
    "1. BƯỚC TIẾP NHẬN & PHÂN LOẠI: Nhận diện thể loại bức ảnh (tủ điện điều khiển, bo mạch PLC, biến tần, nhãn mác đầu cosse dây điện, màn hình HMI, hay sơ đồ bản vẽ).\n"
    "2. BƯỚC BÓC TÁCH KÝ TỰ (OCR): Phóng to điểm ảnh, đọc chính xác 100% từng con số, mã dây cosse, ký hiệu chân cắm (như FWD, REV, COM, Y0, Y1, Y2, X1-X8, 10V, AI1, AI2, GND, R-S-T, U-V-W...).\n"
    "3. BƯỚC PHÂN TÍCH CHUYÊN MÔN: Xâu chuỗi chức năng từng dây, hướng dẫn sơ đồ đấu nối hoàn chỉnh, giải thích nguyên lý vận hành.\n"
    "4. HỖ TRỢ MÀN HÌNH HMI: Phân tích chân nạp COM RS232/RS485, quy trình bảo trì khôi phục cài đặt gốc Factory Reset hợp chuẩn.\n\n"
    "Quy tắc viết: Câu cú gãy gọn, mạch lạc, dễ hiểu, TUYỆT ĐỐI KHÔNG lạm dụng các ký tự dấu sao (**) để khi chuyển thành giọng đọc nghe tự nhiên và êm tai nhất."
)

def call_open_model(prompt: str, model_type: str = "deepseek"):
    clean_p = re.sub(r'[\r\n\t]+', ' ', prompt).strip()
    encoded = urllib.parse.quote(clean_p[:600])
    model_param = "deepseek" if "deepseek" in model_type else "llama"
    try:
        url = f"https://text.pollinations.ai/{encoded}?model={model_param}&system={urllib.parse.quote(MASTER_AN_BINH_PROMPT[:300])}"
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
        req = urllib.request.Request(url, headers={"User-Agent": "AI-AnBinh/VisionMaster"})
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

def call_google_gemini_vision(prompt: str, base64_images: list = None, api_key: str = None):
    key = api_key if api_key else get_saved_key()
    if not key:
        return "CHƯA_CÓ_KEY"

    active_models = get_working_models_for_key(key)
    last_error_msg = ""

    for model_name in active_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        parts = []

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
            f"[CHỈ DẪN HỆ THỐNG]: {MASTER_AN_BINH_PROMPT}\n\n"
            f"[YÊU CẦU CỦA BỒ]: {prompt if prompt else 'Hãy soi thật kỹ ảnh này: phân loại ảnh, trích xuất chính xác từng con số/chữ/ký hiệu trên dây điện và phân tích chuyên môn chi tiết.'}"
        )
        parts.append({"text": full_prompt})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.2,
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
        action = "Vietnamese electrical technician working on automation cabinet with wiring tools, sparks, cinematic 35mm lens, 4k 60fps"
    elif any(k in m for k in ["bánh mì", "ăn bánh mì"]):
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
    <title>AI AN BÌNH</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { 
            background: #050811; color: #f1f5f9; min-height: 100vh; display: flex; flex-direction: column; 
            background-size: cover; background-position: center; background-repeat: no-repeat; padding-bottom: 90px; 
        }
        .backdrop-overlay { 
            position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
            background: rgba(5, 8, 17, 0.88); backdrop-filter: blur(10px); z-index: 1; 
        }
        .app-container { 
            position: relative; z-index: 2; display: flex; flex-direction: column; 
            max-width: 650px; width: 100%; margin: 0 auto; flex: 1; 
        }
        .header { 
            position: sticky; top: 0; z-index: 10; display: flex; align-items: center; justify-content: space-between; 
            padding: 10px 14px; background: rgba(15, 23, 42, 0.95); border-bottom: 1px solid rgba(255, 255, 255, 0.1); 
            backdrop-filter: blur(12px); 
        }
        .header-title h1 { font-size: 18px; color: #ffffff; font-weight: 800; letter-spacing: 0.5px; }
        .header-title p { font-size: 10.5px; color: #94a3b8; }
        .header-actions { display: flex; align-items: center; gap: 6px; }
        .btn-tool { 
            background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); color: #e2e8f0; 
            padding: 5px 8px; border-radius: 6px; font-size: 11px; cursor: pointer; white-space: nowrap; 
        }
        .btn-vault { background: #2563eb !important; color: #fff !important; font-weight: bold; border: none !important; }
        .btn-key-active { background: #10b981 !important; color: #fff !important; font-weight: bold; border: none !important; }
        .btn-key-pending { background: #f59e0b !important; color: #fff !important; font-weight: bold; border: none !important; }
        .chat-stream { flex: 1; padding: 14px 12px; display: flex; flex-direction: column; gap: 12px; }
        .msg { 
            max-width: 90%; padding: 12px 14px; border-radius: 14px; font-size: 14px; line-height: 1.55; 
            word-break: break-word; box-shadow: 0 4px 15px rgba(0,0,0,0.25); position: relative; 
        }
        .msg.bot { background: rgba(30, 41, 59, 0.95); color: #f8fafc; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.08); }
        .msg.user { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; }
        .user-media-grid { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
        .user-media-grid img, .user-media-grid video { width: 85px; height: 85px; border-radius: 8px; object-fit: cover; }
        .msg-footer { 
            margin-top: 10px; display: flex; align-items: center; justify-content: flex-end; gap: 8px; 
            border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 8px; 
        }
        .btn-action-msg { 
            background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; color: #38bdf8; 
            padding: 4px 10px; border-radius: 6px; font-size: 11.5px; font-weight: bold; cursor: pointer; 
            display: inline-flex; align-items: center; gap: 4px; 
        }
        .btn-save-vault { background: rgba(168, 85, 247, 0.15) !important; border-color: #a855f7 !important; color: #d8b4fe !important; }
        .cinema-video-card { margin-top: 10px; background: rgba(0, 0, 0, 0.6); border: 1px solid #38bdf8; border-radius: 14px; padding: 10px; text-align: center; }
        .cinema-video-player { width: 100%; border-radius: 8px; max-height: 300px; background: #000; display: block; }
        .btn-download-video { 
            background: #38bdf8; color: #050811; padding: 7px 16px; border-radius: 8px; font-weight: 800; 
            font-size: 12px; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; margin-top: 8px; 
        }
        .attachment-preview-bar { 
            display: none; position: fixed; bottom: 74px; left: 0; right: 0; z-index: 99; 
            background: rgba(15, 23, 42, 0.96); padding: 6px 12px; border-top: 1px solid rgba(255, 255, 255, 0.1); 
        }
        .preview-scroll-row { max-width: 650px; margin: 0 auto; display: flex; gap: 8px; overflow-x: auto; }
        .preview-item-chip { display: flex; align-items: center; gap: 6px; background: #1e293b; padding: 4px 8px; border-radius: 8px; font-size: 11px; flex-shrink: 0; }
        .preview-item-chip img, .preview-item-chip video { width: 32px; height: 32px; object-fit: cover; border-radius: 4px; }
        .btn-chip-remove { background: none; border: none; color: #ef4444; font-weight: bold; font-size: 14px; cursor: pointer; }
        .bottom-bar { 
            position: fixed; bottom: 0; left: 0; right: 0; z-index: 100; background: rgba(15, 23, 42, 0.96); 
            backdrop-filter: blur(14px); border-top: 1px solid rgba(255, 255, 255, 0.12); 
            padding: 8px 10px calc(8px + env(safe-area-inset-bottom, 8px)); 
        }
        .bottom-bar-inner { max-width: 650px; margin: 0 auto; display: flex; align-items: center; gap: 5px; width: 100%; }
        .btn-icon-label { 
            background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); color: #38bdf8; 
            width: 36px; height: 42px; border-radius: 8px; display: flex; align-items: center; justify-content: center; 
            font-size: 22px; font-weight: bold; cursor: pointer; flex-shrink: 0; 
        }
        .btn-icon { 
            background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); color: #38bdf8; 
            width: 36px; height: 42px; border-radius: 8px; display: flex; align-items: center; justify-content: center; 
            font-size: 17px; cursor: pointer; flex-shrink: 0; 
        }
        .chat-input { 
            flex: 1; min-width: 0; padding: 10px 11px; background: rgba(8, 12, 20, 0.9); 
            border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 8px; color: #fff; font-size: 13.5px; outline: none; 
        }
        .btn-enter { 
            background: #10b981; color: #ffffff; border: none; padding: 0 12px; height: 42px; 
            border-radius: 8px; font-weight: 800; font-size: 13.5px; cursor: pointer; display: flex; 
            align-items: center; justify-content: center; gap: 3px; flex-shrink: 0; white-space: nowrap; 
        }
        #fileInput, #bgInput { display: none; }
    </style>
</head>
<body>
    <div class="backdrop-overlay"></div>

    <div class="app-container">
        <div class="header">
            <div class="header-title">
                <h1>AI AN BÌNH</h1>
                <p>Tự Động Hóa • Thị Giác Chuyên Sâu • Video</p>
            </div>
            <div class="header-actions">
                <button class="btn-tool btn-vault" id="vaultBtn" onclick="downloadBrainBackup()">📥 Não (0)</button>
                <button class="btn-tool" onclick="document.getElementById('bgInput').click()" title="Tải ảnh nền cá nhân">🖼️ Nền</button>
                <button class="btn-tool btn-key-pending" id="keyBtn" onclick="setupApiKey()">🔑 Não</button>
            </div>
        </div>

        <div class="chat-stream" id="chatStream">
            <div class="msg bot">
                <div class="bot-text">
                    Chào bồ! Tui là <b>AI An Bình</b>.<br><br>
                    👁️ <b>Quy trình soi ảnh & bóc tách chữ chuyên sâu đã kích hoạt:</b><br>
                    • Tiếp nhận ảnh ➔ Phân loại thể loại ➔ Trích xuất chuẩn xác từng số cosse dây, ký hiệu chân cắm (FWD, REV, Y0, Y1, R-S-T, U-V-W...).<br>
                    • Bấm nút <b>[🔊 Nghe đọc]</b> ở dưới để tui cất giọng đọc to rõ, rành mạch cho bồ nhen!
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

            <input type="text" id="chatInput" class="chat-input" placeholder="Gửi ảnh soi dây, hỏi PLC, biến tần, tạo video..." autocomplete="off">

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

            alert("🎉 ĐÃ KÍCH HOẠT! AI An Bình sẵn sàng phục vụ bồ!");
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
            alert("💾 Đã lưu ghi chú này vào Két Sắt thành công!");
            updateVaultCounter();
        }

        async function quickSaveVault(btn) {
            const msgBox = btn.closest('.msg');
            const textBox = msgBox.querySelector('.bot-text');
            const answer = textBox ? textBox.innerText : msgBox.innerText;
            await fetch('/api/save-memory', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ query: answer.substring(0, 35), answer: answer })
            });
            alert("🎉 Đã cất bài học này vào Két Sắt thành công!");
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

            const allImages = currentAttachments.filter(a => !a.isVideo).map(a => a.dataUrl);
            const sentCount = currentAttachments.length;
            const userKey = localStorage.getItem('phdam_gemini_key') || '';

            currentAttachments = [];
            renderPreviewChips();
            inp.value = '';

            const isAskingVideo = /tạo videos?|làm videos?|tạo phim/i.test(text);
            const tempId = 'bot_temp_' + Date.now();
            stream.innerHTML += `<div class="msg bot" id="${tempId}"><div class="bot-text">${isAskingVideo ? '🎬 AI An Bình đang kết xuất video MP4...' : (allImages.length > 1 ? '⚡ AI An Bình đang xâu chuỗi nhiều ảnh để vẽ sơ đồ mạch...' : '⚡ AI An Bình đang bóc tách chữ và phân tích...')}</div></div>`;
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: text,
                        images: allImages,
                        api_key: userKey,
                        media_count: sentCount
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
                        <div style="font-size:12px; color:#38bdf8; font-weight:bold; margin-bottom:6px;">🎬 VIDEO KẾT XUẤT:</div>
                        <video class="cinema-video-player" src="${d.video_mp4_url}" controls autoplay loop playsinline></video>
                        <div>
                            <a href="${d.video_mp4_url}" target="_blank" download="ai_anbinh_video.mp4" class="btn-download-video">⬇️ Tải Video MP4 về máy</a>
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

        // GIỌNG ĐỌC AI AN BÌNH: MỞ ĐẦU THÂN MẬT, XÓA SẠCH DẤU SAO
        function speakMessage(btn) {
            if (!window.speechSynthesis) return alert('Thiết bị chưa hỗ trợ phát âm thanh trực tiếp!');
            window.speechSynthesis.cancel();
            
            const msgBox = btn.closest('.msg');
            const textBox = msgBox.querySelector('.bot-text');
            let rawText = textBox ? textBox.innerText : msgBox.innerText;
            
            rawText = rawText.replace(/🔊/g, '')
                             .replace(/Nghe đọc/g, '')
                             .replace(/💾/g, '')
                             .replace(/Lưu Vào Não/g, '')
                             .replace(/⬇️ Tải Video MP4 về máy/g, '')
                             .replace(/🎬 VIDEO KẾT XUẤT.*/g, '')
                             .replace(/Siêu Nhân/gi, '')
                             .replace(/Đại đế/gi, '')
                             .replace(/Emperor/gi, '');

            let clean = rawText.replaceAll('*', '')
                               .replaceAll('`', '')
                               .replaceAll('#', '')
                               .replaceAll('_', '')
                               .replaceAll('~', '')
                               .replaceAll('>', '')
                               .replaceAll('"', '')
                               .replaceAll("'", '')
                               .replaceAll('•', ', ')
                               .replace(/[-]{2,}/g, ' ')
                               .replace(/\s+/g, ' ')
                               .trim();

            let finalSpeech = "Xin chào, tôi là AI An Bình, tôi xin đọc nội dung như sau: " + clean;
            
            const utterance = new SpeechSynthesisUtterance(finalSpeech);
            utterance.lang = 'vi-VN';
            utterance.rate = 0.95;
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
        headers={"Content-Disposition": "attachment; filename=AI_AnBinh_Brain_Backup.json"}
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

    if images and len(images) > 0:
        LAST_STATE["last_images"] = images
    elif LAST_STATE["last_images"] and any(w in msg.lower() for w in ["số", "thấy", "dây", "ảnh", "hình", "mấy", "đầu dây", "này", "đấu dây", "sơ đồ", "mạch", "plc"]):
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
            f"🎬 Đã kết xuất video MP4 phân cảnh {LAST_STATE['theme']} thành công cho bồ!<br><br>"
            "Bồ có thể bấm nút Play để xem trực tiếp hoặc bấm Tải Video MP4 về máy nhé!"
        )
        return {"reply": reply, "video_mp4_url": video_mp4_url, "learned": False}

    # 2. CƠ CHẾ ƯU TIÊN NÃO NHÀ
    if not images:
        vault_hit = search_local_vault(msg)
        if vault_hit:
            clean_reply = clean_markdown_to_clean_html(f"⚡ [Tri thức tự thân từ Két Sắt của bồ]:<br><br>{vault_hit}")
            return {"reply": clean_reply, "video_mp4_url": None, "learned": False}

    # 3. TỰ ĐỘNG ĐIỀU PHỐI ĐA NÃO (GEMINI + DEEPSEEK + LLAMA)
    ai_answer = None

    # Gọi Google Gemini Mắt Thần OCR xử lý ảnh và bóc tách chữ
    gemini_out = call_google_gemini_vision(msg, images, client_api_key)
    if gemini_out and not gemini_out.startswith("LỖI_GOOGLE:") and gemini_out != "CHƯA_CÓ_KEY":
        ai_answer = gemini_out

    # Dự phòng sang DeepSeek-R1 nếu Gemini nghẽn
    if not ai_answer:
        ai_answer = call_open_model(msg, "deepseek")

    # Dự phòng sang Meta Llama 3.3
    if not ai_answer:
        ai_answer = call_open_model(msg, "llama")

    # 4. KHO DỮ LIỆU CẨM NANG DỰ PHÒNG CHUYÊN SÂU
    if not ai_answer:
        if any(w in lower_msg for w in ["hmi", "màn hình", "pass", "password", "mật khẩu", "reset"]):
            ai_answer = (
                "Về màn hình cảm ứng HMI: Các cổng giao tiếp chính gồm COM1 RS232 (chân 2 RXD, chân 3 TXD, chân 5 GND) và COM2 RS485 (chân 1 Data+, chân 6 Data-). "
                "Khi cần xử lý mật khẩu kỹ thuật viên hoặc khôi phục quyền truy cập: Nhà sản xuất hỗ trợ gạt DIP Switch phía sau máy về chế độ Bootloader để Factory Reset, hoặc nạp đè Firmware System Recovery qua thẻ nhớ USB để thiết lập lại mật khẩu quản trị."
            )
        elif any(w in lower_msg for w in ["sơ đồ", "mạch", "vẽ", "dây", "plc", "y0", "y1"]):
            ai_answer = (
                "Sơ đồ đấu nối giữa PLC FX3S và Biến tần VFD: "
                "Chân COM của biến tần nối vào chân chung ngõ ra PLC. Ngõ ra Y0 trên PLC nối vào chân FWD (chạy thuận), ngõ ra Y1 nối vào chân REV (chạy nghịch). "
                "Để chỉnh tốc độ bằng chiết áp ngoài: Cấp nguồn chân 10V và chân GND của biến tần vào hai đầu điện trở, chân giữa biến trở đấu vào chân AI1 (0-10V) để tăng giảm tần số mượt mà."
            )
        else:
            ai_answer = f"Bồ ơi, tui đã ghi nhận câu hỏi '{msg}'. Bồ cần bóc tách chữ trong ảnh, xâu chuỗi sơ đồ mạch hay kiểm tra thông số cứ gửi ảnh và yêu cầu nhé!"

    formatted_reply = clean_markdown_to_clean_html(ai_answer)
    save_to_vault(msg, formatted_reply)
    return {"reply": formatted_reply, "video_mp4_url": None, "learned": not bool(images)}
