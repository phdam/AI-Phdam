import os
import json
import uuid
import re
import httpx

from pathlib import Path
from urllib.parse import urljoin, urlparse
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AI Phdam Music")

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

ACESTEP_API_URL = os.getenv("ACESTEP_API_URL", "").rstrip("/")
ACESTEP_API_KEY = os.getenv("ACESTEP_API_KEY", "")

# Lưu mã tác vụ trong bộ nhớ máy chủ
TASKS = {}

LY_STYLES = [
    "Lý Chiều Chiều",
    "Lý Cây Bông",
    "Lý Con Sáo",
    "Lý Ngựa Ô",
    "Lý Kéo Chài",
    "Lý Qua Cầu",
    "Lý Chim Quyên",
    "Lý Giao Duyên",
    "Lý Đất Giồng",
    "Lý Bông Dừa",
    "Lý Ba Tri",
    "Lý Mỹ Hưng",
]

INSTRUMENTS = [
    "Acoustic Guitar",
    "Electric Guitar",
    "Classical Guitar",
    "Bass Guitar",
    "Piano",
    "Keyboard",
    "Organ",
    "Synthesizer",
    "Electric Piano",
    "Violin",
    "Cello",
    "Đàn tranh",
    "Đàn bầu",
    "Đàn kìm",
    "Đàn cò",
    "Đàn nguyệt",
    "Sáo trúc",
    "Sáo flute",
    "Saxophone",
    "Trumpet",
    "Harmonica",
    "Trống acoustic",
    "Trống điện tử",
    "Cajon",
    "Conga",
    "Bongo",
    "Song lang",
    "Deep Bass",
    "Sub Bass",
    "Synth Bass",
    "Electronic Beat",
    "String Orchestra",
]


def ace_headers():
    headers = {"Content-Type": "application/json"}
    if ACESTEP_API_KEY:
        headers["Authorization"] = f"Bearer {ACESTEP_API_KEY}"
    return headers


def unwrap_response(data):
    if isinstance(data, dict):
        if data.get("error"):
            raise HTTPException(502, str(data["error"]))
        return data.get("data", data)
    return data


def ace_url(path):
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return urljoin(ACESTEP_API_URL + "/", path.lstrip("/"))


# =========================
# TRANG CHỦ
# =========================

@app.get("/", response_class=HTMLResponse)
async def home():
    if not INDEX_FILE.exists():
        raise HTTPException(
            404,
            "Không tìm thấy index.html trong thư mục ứng dụng."
        )

    return HTMLResponse(
        INDEX_FILE.read_text(encoding="utf-8")
    )


@app.get("/api/health")
async def health():
    return {
        "app": "AI Phdam Music",
        "status": "online",
        "gemini_configured": bool(GEMINI_API_KEY),
        "acestep_configured": bool(ACESTEP_API_URL),
    }


# =========================
# GEMINI SÁNG TÁC LỜI
# =========================

@app.post("/api/lyrics")
async def create_lyrics(req: Request):
    data = await req.json()

    idea = str(data.get("idea", "")).strip()
    genre = str(data.get("genre", "Dân ca hiện đại"))
    voice = str(data.get("voice", "Nam cao"))
    mood = str(data.get("mood", "Sâu lắng"))

    if len(idea) < 3:
        raise HTTPException(400, "Hãy nhập ý tưởng bài hát.")

    if not GEMINI_API_KEY:
        raise HTTPException(
            503,
            "Chưa cấu hình GEMINI_API_KEY trên Render."
        )

    prompt = f"""
Bạn là nhạc sĩ sáng tác ca khúc tiếng Việt.

Hãy sáng tác một bài hát hoàn chỉnh dựa trên ý tưởng:

{idea}

Phong cách: {genre}
Giọng hát: {voice}
Cảm xúc: {mood}

YÊU CẦU:
- Lời tiếng Việt tự nhiên, dễ hát, dễ nhớ.
- Có cấu trúc Intro, Verse, Chorus, Bridge, Outro khi phù hợp.
- Không dùng từ ngữ sáo rỗng.
- Không sao chép lời bài hát có sẵn.
- Nếu là điệu Lý Nam Bộ, giữ tinh thần dân ca Nam Bộ.
- Không tự ý chuyển thành vọng cổ hoặc tân cổ.
- Viết lời hoàn chỉnh, không giải thích bên ngoài.
"""

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)

        result = await client.aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        lyrics = (result.text or "").strip()

        if not lyrics:
            raise ValueError("Gemini không trả về nội dung.")

        return {"lyrics": lyrics}

    except Exception as e:
        raise HTTPException(
            502,
            f"Lỗi Gemini: {str(e)}"
        )


# =========================
# TẠO BÀI HÁT ACE-STEP
# =========================

@app.post("/api/music/generate")
async def generate_music(req: Request):
    data = await req.json()

    lyrics = str(data.get("lyrics", "")).strip()

    if not lyrics:
        raise HTTPException(400, "Chưa có lời bài hát.")

    if not ACESTEP_API_URL:
        raise HTTPException(
            503,
            "Chưa cấu hình ACESTEP_API_URL. "
            "Cần địa chỉ máy chủ ACE-Step đang hoạt động."
        )

    genre = str(data.get("genre", "Modern Bolero"))
    voice = str(data.get("voice", "Nam cao"))
    instruments = str(data.get("instruments", "Guitar, piano, bass"))

    bpm = int(data.get("bpm", 90))
    duration = int(data.get("duration", 120))
    audio_format = str(data.get("format", "mp3")).lower()

    if not 30 <= bpm <= 300:
        raise HTTPException(400, "BPM phải từ 30 đến 300.")

    if not 10 <= duration <= 600:
        raise HTTPException(400, "Thời lượng phải từ 10 đến 600 giây.")

    if audio_format not in ["mp3", "wav", "flac", "opus", "aac"]:
        raise HTTPException(400, "Định dạng âm thanh không hợp lệ.")

    # Nhận diện các điệu Lý
    selected_ly = next(
        (s for s in LY_STYLES if s.lower() in genre.lower()),
        None
    )

    prompt = f"""
Vietnamese music.
Style: {genre}.
Vocal: {voice}.
Instruments: {instruments}.
"""

    if selected_ly:
        prompt += f"""
Traditional Vietnamese Southern folk melody:
{selected_ly}.
Respect the characteristic melodic phrasing,
rhythm and ornamentation of this folk style.
Do not turn it into vọng cổ or cải lương.
"""

    if data.get("noBacking"):
        prompt += " Solo lead vocal, no backing vocals, no choir."

    payload = {
        "prompt": prompt,
        "lyrics": lyrics,
        "vocal_language": "vi",
        "audio_format": audio_format,
        "audio_duration": duration,
        "bpm": bpm,
        "thinking": True,
        "use_format": True,
        "task_type": "text2music"
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                ace_url("/release_task"),
                json=payload,
                headers=ace_headers()
            )

            response.raise_for_status()
            result = unwrap_response(response.json())

        task_id = result.get("task_id") if isinstance(result, dict) else None

        if not task_id:
            raise ValueError("ACE-Step không trả về task_id.")

        internal_id = str(uuid.uuid4())

        TASKS[internal_id] = {
            "ace_task_id": task_id,
            "base_url": ACESTEP_API_URL,
            "status": 0
        }

        return {
            "task_id": internal_id,
            "status": "queued"
        }

    except Exception as e:
        raise HTTPException(
            502,
            f"Lỗi kết nối ACE-Step: {str(e)}"
        )


# =========================
# KIỂM TRA TIẾN ĐỘ TẠO NHẠC
# =========================

@app.get("/api/music/status/{task_id}")
async def music_status(task_id: str):

    task = TASKS.get(task_id)

    if not task:
        raise HTTPException(404, "Không tìm thấy mã tác vụ.")

    ace_task_id = task["ace_task_id"]

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                ace_url("/query_result"),
                json={"task_id_list": [ace_task_id]},
                headers=ace_headers()
            )

            response.raise_for_status()
            result = unwrap_response(response.json())

        if isinstance(result, dict):
            results = result.get("data", [])
        else:
            results = result

        if not results:
            return {
                "status": 0,
                "audio_files": []
            }

        item = results[0]

        status = int(item.get("status", 0))

        if status == 2:
            return {
                "status": 2,
                "error": item.get("error", "Tạo nhạc thất bại.")
            }

        if status != 1:
            return {
                "status": 0,
                "audio_files": []
            }

        raw_result = item.get("result", [])

        if isinstance(raw_result, str):
            raw_result = json.loads(raw_result)

        if isinstance(raw_result, dict):
            raw_result = [raw_result]

        audio_files = []

        for audio in raw_result or []:
            audio_path = audio.get("file")

            if audio_path:
                audio_files.append(ace_url(audio_path))

        if not audio_files:
            return {
                "status": 0,
                "audio_files": []
            }

        task["status"] = 1
        task["audio_files"] = audio_files

        return {
            "status": 1,
            "audio_files": audio_files
        }

    except Exception as e:
        raise HTTPException(
            502,
            f"Lỗi kiểm tra kết quả: {str(e)}"
        )


# =========================
# DANH SÁCH ĐIỆU LÝ
# =========================

@app.get("/api/music/ly-styles")
async def get_ly_styles():
    return {"styles": LY_STYLES}


# =========================
# DANH SÁCH NHẠC CỤ
# =========================

@app.get("/api/music/instruments")
async def get_instruments():
    return {"instruments": INSTRUMENTS}
