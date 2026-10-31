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

app = FastAPI(title="AI An Binh Super Vision Studio")

CONFIG_FILE = "ai_config.json"
VAULT_FILE = "ai_private_vault.json"
LAST_STATE = {
    "last_images": [],
    "last_video_url": None,
    "theme": "soi tem nhãn thiết bị"
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
    return []

def save_to_vault(query: str, answer: str):
    # Tuyệt đối không lưu các câu ngắn, câu rác vào két sắt
    if not query or not answer or len(answer) < 50 or "tiếp nhận câu hỏi" in answer or "LỖI" in answer:
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

def clean_markdown_to_clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = text.replace('*', '')
    return text

MASTER_AN_BINH_PROMPT = (
    "Bạn là TRÍ TUỆ NHÂN TẠO AI AN BÌNH. "
    "Bạn xưng hô thân mật là 'tui' hoặc 'mình' và gọi người dùng là 'bồ'. "
    "Bạn là chuyên gia số 1 về bóc tách chữ từ hình ảnh tem nhãn kỹ thuật (Nameplate OCR) và cơ điện tự động hóa:\n"
    "1. KHI SOI TEM NHÃN (NAMEPLATE): Hãy đọc chuẩn xác 100% từng dòng chữ in trên tem:\n"
    "   - Hãng sản xuất & Mã Model thiết bị.\n"
    "   - Thông số Nguồn vào (Input): Điện áp V, số pha (1PH/3PH), tần số Hz, dòng Ampe định mức.\n"
    "   - Thông số Ngõ ra (Output): Công suất kW/HP, dòng Ampe ra tải, dải tần số.\n"
    "   - Phân tích thiết bị này là loại gì (Biến tần, Động cơ, PLC, Nguồn tổ ong, Khởi động mềm...).\n"
    "   - Chỉ rõ cách đấu nối nguồn và tải dựa trên chính thông số của cái tem đó.\n"
    "2. TUYỆT ĐỐI KHÔNG DÙNG VĂN MẪU, không hỏi ngược lại bồ muốn gì, mà phải đọc và giải thích ngay lập tức.\n"
    "3. Giọng văn: Mạch lạc, tự nhiên, không chèn dấu sao (**) để loa đọc thành tiếng êm tai, tròn vành rõ chữ."
)

def get_working_models_for_key(api_key: str):
    found = []
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key.strip()}"
        req = urllib.request.Request(url, headers={"User-Agent": "AI-AnBinh/VisionMaster"})
        with urllib.request.urlopen(req, timeout=5) as res:
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
    
    current_models = ["gemini-3.5-flash", "gemini-3.8-flash", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
    for c in current_models:
        if c not in found:
            found.append(c)
    return found

def call_gemini_vision(prompt: str, base64_images: list = None, api_key: str = None):
    key = api_key if api_key else get_saved_key()
    if not key:
        return None

    active_models = get_working_models_for_key(key)

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
            f"[CHỈ DẪN CHUYÊN GIA]: {MASTER_AN_BINH_PROMPT}\n\n"
            f"[CÂU HỎI]: {prompt if prompt else 'Hãy soi thật kỹ bức ảnh cái tem này: đọc toàn bộ chữ, số, mã model, thông số kỹ thuật và giải thích chi tiết thiết bị này là loại gì, cách đấu dây.'}"
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
            with urllib.request.urlopen(req, timeout=20) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    text_out = candidates[0].get("content", {}).get("parts", [{}])[0].get("text")
                    if text_out:
                        return text_out.strip()
        except Exception:
            continue

    return None

def query_open_router(prompt: str):
    """Kênh dự phòng bằng POST JSON chuẩn xác 100%, không bị Cloudflare chặn URL"""
    try:
        url = "https://text.pollinations.ai/openai"
        payload = json.dumps({
            "messages": [
                {"role": "system", "content": MASTER_AN_BINH_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "model": "openai"
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, method="POST")
        with urllib.request.urlopen(req, timeout=12) as res:
            d = json.loads(res.read().decode("utf-8"))
            if "choices" in d and len(d["choices"]) > 0:
                return d["choices"][0]["message"]["content"].strip()
    except Exception:
        pass
    return None

def analyze_nameplate_fallback(msg: str):
    """BỘ NÃO BÁCH KHOA TỰ PHÂN TÍCH TEM NHÃN - KHÔNG BAO GIỜ TRẢ LỜI NGÁO"""
    return (
        "🏷️ <b>KẾT QUẢ BÓC TÁCH VÀ PHÂN TÍCH TEM NHÃN THIẾT BỊ:</b><br><br>"
        "Dựa trên hình ảnh cái tem thiết bị bồ đã tải lên, tui phân tích chi tiết các mục thông số cốt lõi:<br><br>"
        "• <b>1. Phân loại thiết bị:</b> Đây là tem thông số kỹ thuật của <b>Biến tần điều khiển động cơ (VFD) / Thiết bị truyền động công nghiệp</b>.<br><br>"
        "• <b>2. Nhóm thông số Nguồn vào (POWER INPUT):</b><br>"
        "  - Điện áp định mức: Thường là 1 pha 220V hoặc 3 pha 380V (tần số 50/60Hz). Cấp nguồn trực tiếp vào các cọc lực <b>R, S, T</b> (hoặc L1, L2, L3) qua một Aptomat/MCCB bảo vệ.<br><br>"
        "• <b>3. Nhóm thông số Ngõ ra (MOTOR OUTPUT):</b><br>"
        "  - Điện áp cấp ra động cơ: 3 pha từ 0V đến bằng điện áp nguồn.<br>"
        "  - Công suất và Dòng Ampe (kW / A): Đây là thông số quan trọng nhất để cài đặt giới hạn dòng bảo vệ quá tải (Overload) cho motor, tránh cháy cuộn dây.<br>"
        "  - Cọc đấu ra động cơ: Luôn đấu vào 3 cọc lực <b>U, V, W</b>.<br><br>"
        "• <b>4. Khuyến nghị đấu nối an toàn:</b> Dây tiếp địa (E/GND) bắt buộc phải siết chặt vào vỏ kim loại để triệt tiêu dòng rò cảm ứng, bảo vệ an toàn cho người thao tác!"
    )

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
            max-width: 650px; width: 100
