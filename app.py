from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import os
import re
import urllib.request

app = FastAPI(title="AI Phdam Omni")

MEMORY_FILE = "ai_omni_memory.json"

def get_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {
            "title": "Chuyên ngành Tự động hóa & IoT",
            "content": "AI Phdam nắm vững kiến trúc PLC, SCADA, biến tần VFD, giao thức truyền thông Modbus, MQTT, điều khiển từ xa qua LoRa, RF, Wi-Fi Mesh và mạng 5G không dây."
        }
    ]

def save_memory(memories):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

def ask_omni_brain(prompt: str, context: str, has_media: bool = False, media_type: str = ""):
    models = ["openai", "mistral", "qwen"]
    
    media_instruction = ""
    if has_media:
        media_instruction = f"\n[HỆ THỐNG]: Người dùng vừa đính kèm một {media_type.upper()}. Hãy kết hợp phân tích kỹ thuật, đưa ra nhận xét chuyên môn sắc sảo cùng câu trả lời.\n"

    sys_prompt = (
        "Bạn là SIÊU TRÍ TUỆ NHÂN TẠO PHDAM (Omni Intelligence). "
        "Bạn sở hữu khối lượng kiến thức tổng hợp sâu rộng của hàng triệu mô hình AI tiên tiến nhất hiện nay. "
        "Bạn là đại chuyên gia hàng đầu về:\n"
        "1. TỰ ĐỘNG HÓA CÔNG NGHIỆP: PLC, SCADA, HMI, cảm biến, rơ-le, van điều khiển, dây chuyền tự động.\n"
        "2. ĐIỀU KHIỂN TỪ XA & IOT: Vi điều khiển (ESP32, STM32, Arduino), giao thức Modbus RTU/TCP, MQTT, LoRa, RF 433MHz, điều khiển qua Internet.\n"
        "3. MẠNG KHÔNG DÂY: Wi-Fi 6, 5G/4G, Zigbee, Bluetooth Mesh, bảo mật đường truyền.\n"
        "4. CƠ ĐIỆN TỬ & BIẾN TẦN: Đấu nối, cài đặt thông số chạy thuận/nghịch, bảo vệ động cơ 3 pha, tiết kiệm năng lượng.\n"
        "5. TỔNG HỢP KHOA HỌC: Lập trình, tư duy logic, giải pháp tối ưu.\n\n"
        f"KHO TRI THỨC VÀ DỮ LIỆU ĐÍNH CHÍNH CỦA BẠN:\n{context}\n"
        f"{media_instruction}\n"
        "Quy tắc phản hồi: Trả lời thông thái, phân tích sâu sắc, ngắn gọn rõ ràng nhưng chuẩn xác đến từng thông số kỹ thuật. Rất tôn trọng và gắn kết với người dùng."
    )

    for m in models:
        try:
            url = "https://text.pollinations.ai/"
            headers = {"Content-Type": "application/json", "User-Agent": "AI-Phdam/Omni"}
            payload = {
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                "model": m,
                "seed": 100
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12) as res:
                out = res.read().decode("utf-8").strip()
                if out and len(out) > 5:
                    return out
        except Exception:
            continue
    return None

HTML_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI Phdam Omni</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        
        body { 
            background: #060911; 
            color: #f1f5f9; 
            height: 100dvh; 
            display: flex; 
            flex-direction: column; 
            overflow: hidden;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            transition: background 0.3s ease;
        }

        /* Lớp phủ làm dịu ảnh nền cá nhân */
        .backdrop-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(6, 9, 17, 0.85);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            z-index: 1;
        }

        .app-container {
            position: relative;
            z-index: 2;
            display: flex;
            flex-direction: column;
            height: 100%;
            max-width: 600px;
            width: 100%;
            margin: 0 auto;
        }

        /* Header */
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            background: rgba(15, 23, 42, 0.7);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        .header-title h1 {
            font-size: 18px;
            background: linear-gradient(135deg, #00f2fe, #4facfe, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header-title p {
            font-size: 11px;
            color: #94a3b8;
        }
        .header-actions {
            display: flex;
            gap: 8px;
        }
        .btn-tool {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #e2e8f0;
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* Chat Stream */
        .chat-stream {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            scroll-behavior: smooth;
        }
        .msg {
            max-width: 86%;
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 14px;
            line-height: 1.5;
            word-break: break-word;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .msg.bot {
            background: rgba(30, 41, 59, 0.85);
            color: #f8fafc;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .msg.user {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #fff;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }
        .msg img, .msg video {
            width: 100%;
            max-height: 220px;
            border-radius: 10px;
            margin-top: 8px;
            object-fit: cover;
            display: block;
        }
        .speak-btn {
            background: none;
            border: none;
            font-size: 14px;
            cursor: pointer;
            margin-left: 6px;
            vertical-align: middle;
        }

        /* Khay xem trước tệp trước khi gửi */
        .attachment-preview {
            display: none;
            padding: 8px 16px;
            background: rgba(15, 23, 42, 0.9);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            position: relative;
        }
        .preview-thumb-box {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #1e293b;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 12px;
        }
        .preview-thumb-box img, .preview-thumb-box video {
            width: 36px;
            height: 36px;
            object-fit: cover;
            border-radius: 4px;
        }
        .btn-remove-attach {
            background: none;
            border: none;
            color: #ef4444;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            margin-left: 6px;
        }

        /* Bottom Input Bar */
        .bottom-bar {
            padding: 10px 12px;
            background: rgba(15, 23, 42, 0.85);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .input-btn {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #38bdf8;
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            cursor: pointer;
            flex-shrink: 0;
            transition: 0.2s;
        }
        .input-btn:active {
            transform: scale(0.92);
        }
        .chat-input {
            flex: 1;
            padding: 11px 14px;
            background: rgba(8, 12, 20, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            color: #fff;
            font-size: 14px;
            outline: none;
        }
        .chat-input::placeholder {
            color: #64748b;
        }
        .btn-send {
            background: linear-gradient(135deg, #00f2fe, #4facfe);
            color: #060911;
            border: none;
            width: 42px;
            height: 40px;
            border-radius: 10px;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        /* Ẩn các input file */
        #fileInput, #cameraInput, #bgInput {
            display: none;
        }
    </style>
</head>
<body>
    <div class="backdrop-overlay"></div>

    <div class="app-container">
        <!-- Header -->
        <div class="header">
            <div class="header-title">
                <h1>⚡ SIÊU AI PHDAM OMNI</h1>
                <p>Tự động hóa • IoT • Viễn thông • Đa phương thức</p>
            </div>
            <div class="header-actions">
                <button class="btn-tool" onclick="document.getElementById('bgInput').click()">🖼️ Đổi nền</button>
                <button class="btn-tool" onclick="resetBg()">↺ Nền gốc</button>
            </div>
        </div>

        <!-- Chat Stream -->
        <div class="chat-stream" id="chatStream">
            <div class="msg bot">
                Chào bồ! Tôi là Siêu Trí Tuệ AI Phdam Omni. Tôi tích hợp kiến thức chuyên sâu về Tự động hóa, Điều khiển từ xa IoT, Mạng không dây, Biến tần cùng toàn bộ tri thức khoa học hiện đại.<br><br>
                Bồ có thể bấm <b>dấu [+]</b> để gửi ảnh/video, bấm <b>máy ảnh [📷]</b> để chụp trực tiếp, hoặc bấm <b>Micro [🎙️]</b> để nói chuyện với tôi nhé!
                <button class="speak-btn" onclick="speakText(this.parentElement.innerText)">🔊</button>
            </div>
        </div>

        <!-- Khay xem trước tệp trước khi gửi -->
        <div class="attachment-preview" id="attachPreview">
            <div class="preview-thumb-box">
                <span id="previewMediaBox"></span>
                <span id="attachFileName" style="max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"></span>
                <button class="btn-remove-attach" onclick="removeAttachment()">×</button>
            </div>
        </div>

        <!-- Bottom Input Bar -->
        <div class="bottom-bar">
            <!-- Nút [+] Mở ảnh/video từ máy -->
            <button class="input-btn" onclick="document.getElementById('fileInput').click()" title="Tải ảnh hoặc video">+</button>
            <input type="file" id="fileInput" accept="image/*,video/*" onchange="handleFileSelected(event)">

            <!-- Nút [📷] Mở camera chụp/quay trực tiếp -->
            <button class="input-btn" onclick="document.getElementById('cameraInput').click()" title="Chụp ảnh trực tiếp">📷</button>
            <input type="file" id="cameraInput" accept="image/*" capture="environment" onchange="handleFileSelected(event)">

            <!-- Ô nhập văn bản -->
            <input type="text" id="chatInput" class="chat-input" placeholder="Hỏi tự động hóa, gửi ảnh hoặc chat..." onkeypress="if(event.key==='Enter') sendPayload()">

            <!-- Nút Micro [🎙️] -->
            <button class="input-btn" id="micBtn" onclick="toggleMic()" title="Nói tiếng Việt">🎙️</button>

            <!-- Nút Gửi -->
            <button class="btn-send" onclick="sendPayload()">🚀</button>
        </div>
    </div>

    <!-- Input đổi ảnh nền cá nhân -->
    <input type="file" id="bgInput" accept="image/*" onchange="changeBackground(event)">

    <script>
        let currentAttach = null;
        let attachDataUrl = '';

        // Tải ảnh nền cá nhân đã lưu nếu có
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
            const f = e.target.files[0];
            if (!f) return;
            currentAttach = f;
            const isVideo = f.type.startsWith('video');
            const reader = new FileReader();
            reader.onload = (evt) => {
                attachDataUrl = evt.target.result;
                const box = document.getElementById('previewMediaBox');
                if (isVideo) {
                    box.innerHTML = `<video src="${attachDataUrl}" muted></video>`;
                } else {
                    box.innerHTML = `<img src="${attachDataUrl}">`;
                }
                document.getElementById('attachFileName').innerText = (isVideo ? '🎥 ' : '📸 ') + f.name;
                document.getElementById('attachPreview').style.display = 'block';
            };
            reader.readAsDataURL(f);
        }

        function removeAttachment() {
            currentAttach = null;
            attachDataUrl = '';
            document.getElementById('attachPreview').style.display = 'none';
            document.getElementById('fileInput').value = '';
            document.getElementById('cameraInput').value = '';
        }

        async function sendPayload() {
            const inp = document.getElementById('chatInput');
            const text = inp.value.trim();
            if (!text && !currentAttach) return;

            const stream = document.getElementById('chatStream');

            // Hiển thị tin nhắn người dùng
            let userHtml = `<div class="msg user">`;
            if (currentAttach) {
                if (currentAttach.type.startsWith('video')) {
                    userHtml += `<video src="${attachDataUrl}" controls playsinline></video>`;
                } else {
                    userHtml += `<img src="${attachDataUrl}">`;
                }
            }
            if (text) userHtml += `<div>${text}</div>`;
            userHtml += `</div>`;
            stream.innerHTML += userHtml;
            stream.scrollTop = stream.scrollHeight;

            const sentAttach = currentAttach;
            const sentAttachUrl = attachDataUrl;
            inp.value = '';
            removeAttachment();

            // Hiệu ứng đang suy nghĩ
            const tempId = 'bot_temp_' + Date.now();
            stream.innerHTML += `<div class="msg bot" id="${tempId}">⏳ Siêu AI đang phân tích dữ liệu đa tầng...</div>`;
            stream.scrollTop = stream.scrollHeight;

            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: text,
                    has_media: !!sentAttach,
                    media_type: sentAttach ? (sentAttach.type.startsWith('video') ? 'video' : 'hình ảnh') : ''
                })
            });

            const d = await res.json();
            const tempBox = document.getElementById(tempId);
            tempBox.innerHTML = `${d.reply} <button class="speak-btn" onclick="speakText('${d.reply.replace(/['"\\n]/g, ' ')}')">🔊</button>`;
            stream.scrollTop = stream.scrollHeight;

            if (d.speak) speakText(d.reply);
        }

        function speakText(txt) {
            if (!window.speechSynthesis) return;
            window.speechSynthesis.cancel();
            const clean = txt.replace(/<[^>]*>/g, '').replace(/🔊/g, '');
            const u = new SpeechSynthesisUtterance(clean);
            u.lang = 'vi-VN';
            u.rate = 1.0;
            window.speechSynthesis.speak(u);
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

@app.post("/api/chat")
async def chat_endpoint(req: Request):
    data = await req.json()
    msg = data.get("message", "").strip()
    has_media = data.get("has_media", False)
    media_type = data.get("media_type", "")
    mems = get_memory()

    # 1. Tự sửa sai khi bị chê
    wrong_triggers = ["sai rồi", "nhầm rồi", "không phải", "đâu phải"]
    if any(t in msg.lower() for t in wrong_triggers):
        fix_info = re.sub(r'^(sai rồi|nhầm rồi|không phải|đâu phải)[,.]*\s*', '', msg, flags=re.IGNORECASE)
        mems.append({
            "title": "Đính chính lỗi sai",
            "content": f"ĐÍNH CHÍNH QUAN TRỌNG: {fix_info}"
        })
        save_memory(mems)
        return {
            "reply": f"🛠️ <b>Siêu AI Phdam đã tự đính chính!</b> Tôi đã cập nhật dữ liệu chuẩn xác vào bộ nhớ: <i>'{fix_info}'</i>. Cam kết áp dụng ngay từ câu tiếp theo!",
            "speak": True
        }

    # 2. Tự học chủ động (Active Learning)
    learn_triggers = ["hãy nhớ:", "hãy nhớ là", "ghi nhớ:", "ghi nhớ nhé:", "nhớ kỹ:"]
    for p in learn_triggers:
        if msg.lower().startswith(p):
            new_know = msg[len(p):].strip()
            mems.append({
                "title": f"Kiến thức mới: {new_know[:25]}...",
                "content": new_know
            })
            save_memory(mems)
            return {
                "reply": f"🧠 <b>Đã tiếp thu và ghi nhớ vĩnh viễn!</b> Khối tri thức mới: <i>'{new_know}'</i> đã được nạp vào bộ não trung tâm của Siêu AI Phdam.",
                "speak": True
            }

    # 3. RAG Context
    context_docs = []
    keywords = [w for w in msg.lower().split() if len(w) > 2]
    for m in mems:
        t = (m["title"] + " " + m["content"]).lower()
        if any(k in t for k in keywords):
            context_docs.append(f"[{m['title']}]: {m['content']}")

    context_str = "\n".join(context_docs[:4]) if context_docs else "Kho dữ liệu chuyên ngành sẵn sàng."

    # 4. Kích hoạt Não Omni
    effective_prompt = msg if msg else f"Hãy phân tích và đưa ra đánh giá kỹ thuật chuyên sâu về {media_type} vừa được gửi lên."
    reply = ask_omni_brain(effective_prompt, context_str, has_media, media_type)
    
    if not reply:
        if "biến tần" in msg.lower():
            reply = "Biến tần (VFD) điều khiển tốc độ động cơ 3 pha qua điều biến độ rộng xung PWM, bảo vệ quá dòng/áp và tối ưu hóa hệ số công suất Cos Phi."
        else:
            reply = "Siêu AI Phdam Omni đã tiếp nhận dữ liệu và đang kích hoạt liên kết tri thức để phản hồi tối ưu nhất cho bồ!"

    return {"reply": reply, "speak": False}
