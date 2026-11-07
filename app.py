import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
ACESTEP_API_URL = os.getenv("ACESTEP_API_URL", "").rstrip("/")

LY_NAM_BO_LIST = [
    {"name": "Lý Cây Bông", "desc": "Vui tươi, rộn rã, đậm sắc màu miền Tây sông nước"},
    {"name": "Lý Ngựa Ô Nam Bộ", "desc": "Hào sảng, dồn dập, khí thế phóng khoáng"},
    {"name": "Lý Chim Quyên", "desc": "Mượt mà, da diết, tình cảm quê hương sâu lắng"},
    {"name": "Lý Con Sáo Nam Bộ", "desc": "Thanh thoát, mênh mang, âm hưởng đồng quê"},
    {"name": "Lý Quạ Kêu", "desc": "Mộc mạc, dí dỏm, phong cách dân gian Nam Bộ"},
    {"name": "Lý Kéo Chài", "desc": "Khỏe khoắn, nhịp nhàng sông nước miền hạ lưu"},
    {"name": "Lý Chiều Chiều", "desc": "Lắng đọng, đượm buồn man mác lúc hoàng hôn"},
    {"name": "Lý Đất Giồng", "desc": "Chân chất, tươi vui của người mở đất phương Nam"},
    {"name": "Lý Bông Dừa", "desc": "Nhẹ nhàng, thắm đượm tình làng nghĩa xóm"},
    {"name": "Lý Ba Tri", "desc": "Chất phác, duyên dáng, âm điệu Bến Tre xưa"}
]

@app.route("/")
def index():
    return render_template("index.html", styles=LY_NAM_BO_LIST, server_ready=bool(ACESTEP_API_URL))

@app.route("/api/generate", methods=["POST"])
def generate():
    if not ACESTEP_API_URL:
        return jsonify({"status": "error", "message": "Chưa kết nối máy chủ tạo nhạc (ACESTEP_API_URL)!"}), 500

    data = request.json or {}
    prompt = data.get("prompt", "").strip()
    style = data.get("style", "Lý Cây Bông")

    if not prompt:
        return jsonify({"status": "error", "message": "Vui lòng nhập lời hoặc gợi ý bài hát!"}), 400

    full_prompt = (
        f"Vietnamese traditional folk music, {style}. Pure Southern Vietnamese Ly melody. "
        f"Acoustic instruments: Dan Tranh, Dan Kim, Dan Co, Song Lang. "
        f"Mood: {prompt}. Strictly NO modern remix, NO vong co."
    )

    try:
        res = requests.post(
            f"{ACESTEP_API_URL}/api/generate",
            json={"prompt": full_prompt, "style": style},
            timeout=20
        )
        if res.status_code == 200:
            return jsonify(res.json())
        return jsonify({"status": "error", "message": f"Máy chủ AI phản hồi lỗi: {res.status_code}"}), res.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Không thể kết nối máy chủ AI: {str(e)}"}), 502

@app.route("/api/status/<task_id>", methods=["GET"])
def check_status(task_id):
    if not ACESTEP_API_URL:
        return jsonify({"status": "error", "message": "Thiếu cấu hình máy chủ"}), 500
    try:
        res = requests.get(f"{ACESTEP_API_URL}/api/status/{task_id}", timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("audio_url") and not data["audio_url"].startswith("http"):
                data["audio_url"] = f"{ACESTEP_API_URL}/{data['audio_url'].lstrip('/')}"
            return jsonify(data)
        return jsonify({"status": "processing", "progress": 50})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
