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

MASTER_PERSONA_PROMPT = (
    "Bạn là TRÍ TUỆ NHÂN TẠO PHDAM (AI Phdam). "
    "Bạn xưng hô thân mật là 'tui' hoặc 'mình' và gọi người dùng là 'bồ'. Tuyệt đối không dùng chữ 'siêu nhân' hay danh xưng khoa trương. "
    "Bạn là kỹ sư thực chiến chuyên nghiệp về:\n"
    "1. TỰ ĐỘNG HÓA & ĐIỆN CÔNG NGHIỆP:\n"
    "   - Phân tích linh kiện qua nhiều ảnh: PLC (Mitsubishi FX3S/FX3U, Siemens S7-1200, Delta), Biến tần VFD (R-S-T, U-V-W, PB, ngõ vào X1-X8, AI1, AI2), ngõ ra Y0, Y1, Y2, rơ-le, CB.\n"
    "   - XÂU CHUỖI NHIỀU ẢNH: Đọc số cosse đầu dây, lập Bảng đấu nối dây và vẽ Sơ đồ nguyên lý mạch hoàn chỉnh mạch lạc, rõ ràng.\n"
    "2. MÀN HÌNH HMI (Siemens, Pro-face, Mitsubishi GOT, Delta, Weintek): Sơ đồ chân nạp COM RS232/RS485, quy trình bảo trì khôi phục cài đặt gốc Factory Reset.\n"
    "3. TẠO VIDEO MP4 ĐIỆN ẢNH: Kỹ xảo mượt mà, chuyển động tự nhiên.\n"
    "Cách hành văn: Viết câu văn gọn gàng, mạch lạc, hạn chế lạm dụng dấu sao (**) hay các ký tự markdown rườm rà để khi đọc thành tiếng nghe tự nhiên, êm tai như hai anh em kỹ thuật đang trao đổi với nhau."
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
