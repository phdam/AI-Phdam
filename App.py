import os
import json
import httpx

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai

app = FastAPI(title="AI Phdam Music")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

ACE_STEP_URL = os.getenv("ACE_STEP_URL", "").rstrip("/")
ACE_STEP_API_KEY = os.getenv("ACE_STEP_API_KEY", "")


class LyricsRequest(BaseModel):
    idea: str = Field(min_length=3, max_length=4000)
    genre: str = "Modern Bolero Remix"
    voice: str = "Nam cao"
    mood: str = "Hài hòa, hiện đại"
    language: str = "Tiếng Việt"


class MusicRequest(BaseModel):
    lyrics: str = Field(min_length=1, max_length=12000)
    genre: str = "Modern Bolero Remix"
    instruments: str = "Guitar, piano, bass, electronic drums"
    voice: str = "Male high vocal"
    bpm: int = Field(default=90, ge=30, le=300)
    duration: int = Field(default=120, ge=10, le=600)
    format: str = "mp3"


def require_gemini():
    if not GEMINI_API_KEY:
        raise HTTPException(
            503,
            "Chưa cấu hình GEMINI_API_KEY trên máy chủ."
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def require_music_server():
    if not ACE_STEP_URL:
        raise HTTPException(
            503,
            "Chưa cấu hình ACE_STEP_URL. Cần máy chủ tạo nhạc AI."
        )


@app.get("/")
def home():
    return {
        "app": "AI Phdam Music",
        "status": "online",
        "version": "1.0"
    }


@app.get("/api/health")
def health():
    return {
        "server": "online",
        "gemini_configured": bool(GEMINI_API_KEY),
        "music_server_configured": bool(ACE_STEP_URL),
        "music_generation_ready": bool(ACE_STEP_URL)
    }


@app.post("/api/lyrics")
def create_lyrics(req: LyricsRequest):
    client = require_gemini()

    prompt = f"""
Bạn là nhạc sĩ chuyên sáng tác nhạc Việt Nam hiện đại.

Hãy sáng tác một bài hát hoàn chỉnh dựa trên yêu cầu:

Ý tưởng: {req.idea}
Thể loại: {req.genre}
Giọng hát: {req.voice}
Cảm xúc: {req.mood}
Ngôn ngữ: {req.language}

Yêu cầu:
- Lời tự nhiên, gần gũi, dễ hát.
- Không dùng từ ngữ quá cầu kỳ.
- Có cấu trúc Intro, Verse, Pre-Chorus,
  Chorus, Verse 2, Bridge và Outro khi phù hợp.
- Điệp khúc có câu nhấn dễ nhớ.
- Không tự ý thêm phần hát bè.
- Không sao chép lời bài hát có bản quyền.
- Chỉ trả về lời bài hát và tên bài hát.
"""

    try:
        result = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return {
            "success": True,
            "lyrics": result.text
        }
    except Exception as exc:
        raise HTTPException(502, f"Lỗi Gemini: {str(exc)}")


@app.post("/api/music/generate")
async def generate_music(req: MusicRequest):
    require_music_server()

    prompt = (
        f"{req.genre}, {req.instruments}, "
        f"{req.voice}, modern professional production, "
        "clear Vietnamese vocal, balanced mixing, "
        "high quality arrangement, no backing vocals"
    )

    payload = {
        "prompt": prompt,
        "lyrics": req.lyrics,
        "thinking": True,
        "vocal_language": "vi",
        "audio_format": req.format,
        "bpm": req.bpm,
        "audio_duration": req.duration,
        "time_signature": "4",
        "inference_steps": 8,
        "batch_size": 1,
        "use_format": True
    }

    headers = {"Content-Type": "application/json"}

    if ACE_STEP_API_KEY:
        headers["Authorization"] = (
            f"Bearer {ACE_STEP_API_KEY}"
        )

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{ACE_STEP_URL}/release_task",
                json=payload,
                headers=headers
            )

            response.raise_for_status()
            data = response.json()

        if data.get("error"):
            raise HTTPException(502, data["error"])

        task = data.get("data", data)
        task_id = task.get("task_id")

        if not task_id:
            raise HTTPException(
                502,
                "Máy chủ tạo nhạc không trả về task_id."
            )

        return {
            "success": True,
            "task_id": task_id,
            "status": task.get("status", "queued"),
            "message": "Đã gửi yêu cầu tạo nhạc."
        }

    except httpx.HTTPError as exc:
        raise HTTPException(
            502,
            f"Không kết nối được máy chủ tạo nhạc: {str(exc)}"
        )


@app.get("/api/music/status/{task_id}")
async def music_status(task_id: str):
    require_music_server()

    headers = {"Content-Type": "application/json"}

    if ACE_STEP_API_KEY:
        headers["Authorization"] = (
            f"Bearer {ACE_STEP_API_KEY}"
        )

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{ACE_STEP_URL}/query_result",
                json={"task_id_list": [task_id]},
                headers=headers
            )

            response.raise_for_status()
            data = response.json()

        if data.get("error"):
            raise HTTPException(502, data["error"])

        results = data.get("data", [])

        if not results:
            raise HTTPException(
                404,
                "Không tìm thấy tác vụ tạo nhạc."
            )

        task = results[0]
        status = task.get("status", 0)

        result_data = task.get("result", [])

        if isinstance(result_data, str):
            try:
                result_data = json.loads(result_data)
            except json.JSONDecodeError:
                result_data = []

        audio_files = []

        if status == 1:
            for item in result_data:
                file_path = item.get("file")
                if file_path:
                    audio_files.append(
                        ACE_STEP_URL + file_path
                        if file_path.startswith("/")
                        else ACE_STEP_URL + "/" + file_path
                    )

        return {
            "success": True,
            "task_id": task_id,
            "status": status,
            "audio_files": audio_files,
            "error": task.get("error")
        }

    except httpx.HTTPError as exc:
        raise HTTPException(
            502,
            f"Lỗi kiểm tra tiến trình: {str(exc)}"
        )
