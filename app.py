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

app = FastAPI(title="AI Phdam Automation Studio")

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
    """Chuyển đổi các dấu sao ** thành thẻ in đậm <b>, xóa sạch dấu sao thô để mắt nhìn đẹp và loa không đọc dấu sao"""
    if not text:
        return ""
    # Chuyển **chữ** thành <b>chữ</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Chuyển *chữ* thành <i>chữ</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Xóa sạch mọi dấu sao lẻ loi còn sót lại
    text = text.replace('*', '')
    return text

MASTER_PERSONA_PROMPT = (
    "Bạn là TRÍ TUỆ NHÂN TẠO PHDAM (AI Phdam). "
    "Bạn xưng hô thân mật là 'tui' hoặc 'mình' và gọi người dùng là 'bồ'. Tuyệt đối không dùng danh xưng siêu nhân hay đại đế. "
    "Bạn là chuyên gia thực chiến hàng đầu về PLC (Mitsubishi FX3S/FX3U, Siemens, Delta), Biến tần VFD (R-S-T, U-V-W, terminal điều khiển), HMI và tạo video MP4. "
    "Quy tắc trình bày: Viết câu văn gãy gọn, mạch lạc, KHÔNG dùng các ký tự markdown dấu sao (**) rườm rà để người dùng vừa dễ đọc trên màn hình, vừa nghe đọc thành tiếng trôi chảy tự nhiên như người thật."
)

def call_open_model(prompt: str, model_type: str = "deepseek"):
    clean_p = re.sub(r'[\r\n\t]+', ' ', prompt).strip()
    encoded = urllib.parse.quote(clean_p[:600])
    model_param = "deepseek" if "deepseek" in model_type else "llama"
    try:
        url = f"https://text.pollinations.ai/{encoded}?model={model_param}&system={urllib.parse.quote(MASTER_PERSONA_PROMPT[:300])}"
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
            f"[CHỈ DẪN HỆ THỐNG]: {MASTER_PERSONA_PROMPT}\n\n"
            f"[YÊU CẦU CỦA BỒ]: {prompt if prompt else 'Hãy quan sát kỹ toàn bộ ảnh này, phân tích số dây và hướng dẫn sơ đồ đấu nối chi tiết, mạch lạc.'}"
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
    <title>AI Phdam</title>
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

        /* HEADER CHỮ TRẮNG TINH KHÔI, KHÔNG MÀU CẦU VỒNG */
        .header {
            position: sticky;
            top: 0;
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            background: rgba(15, 23, 42, 0.95);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }
        .header-title h1 {
            font-size: 18px;
            color: #ffffff; /* Chữ trắng sáng thanh lịch, không cầu vồng */
            font-weight: 800;
            letter-spacing: 0.5px;
        }
        .header-title p {
            font-size: 10.5px;
            color: #94a3b8;
        }
        .header-actions {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .btn-tool {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #e2e8f0;
            padding: 5px 8px;
            border-radius: 6px;
            font-size: 11px;
            cursor: pointer;
            white-space: nowrap;
        }
        .btn-vault {
            background: #2563eb !important;
            color: #fff !important;
            font-weight: bold;
            border: none !important;
        }
        .btn-key-active {
            background: #10b981 !important;
            color: #fff !important;
            font-weight: bold;
            border: none !important;
        }
        .btn-key-pending {
            background: #f59e0b !important;
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
            border: 1px solid #38bdf8;
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
            background: #38bdf8;
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
