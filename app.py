from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import os
import re
import urllib.request

app = FastAPI(title="AI Phdam Superhuman")

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
            "content": "Siêu Nhân AI Phdam tinh thông kiến trúc PLC, SCADA, biến tần VFD, giao thức truyền thông Modbus, MQTT, điều khiển từ xa qua LoRa, RF, Wi-Fi Mesh và mạng 5G không dây."
        }
    ]

def save_memory(memories):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

def ask_superhuman_brain(prompt: str, context: str, has_media: bool = False, media_type: str = ""):
    models = ["openai", "qwen", "mistral"]
    
    media_info = ""
    if has_media:
        media_info = f"\n[HỆ THỐNG]: Người dùng vừa gửi một {media_type.upper()}. Hãy phân tích kỹ thuật chuyên sâu và đưa ra đánh giá chính xác.\n"

    sys_prompt = (
        "Bạn là SIÊU NHÂN TRÍ TUỆ NHÂN TẠO PHDAM (Superhuman Omni-Intelligence). "
        "Bạn sở hữu năng lực tư duy logic đa tầng và tri thức bách khoa của các mô hình AI tiên tiến nhất hiện nay. "
        "Bạn là đại chuyên gia tối thượng về:\n"
        "1. TỰ ĐỘNG HÓA & CÔNG NGHIỆP: PLC (Siemens, Mitsubishi, Delta), SCADA, HMI, cảm biến, van điện từ, sơ đồ rơ-le.\n"
        "2. ĐIỀU KHIỂN TỪ XA & IOT: Vi điều khiển (ESP32, STM32), truyền thông Modbus RTU/TCP, MQTT, LoRa, sóng RF, điều khiển qua Internet.\n"
        "3. MẠNG KHÔNG DÂY: Wi-Fi 6, 5G/4G công nghiệp, Zigbee, Bluetooth Mesh, bảo mật mạng.\n"
        "4. CƠ ĐIỆN TỬ & BIẾN TẦN: Đấu nối dây lực, dây điều khiển, cài đặt thông số chạy thuận/nghịch, biến trở ngoài, bảo vệ quá dòng, quá áp, mất pha.\n"
        "5. CÔNG NGHỆ VIDEO AI & ĐA PHƯƠNG THỨC: Phân tích hình ảnh, video, công nghệ motion transfer, deepfake, tổng hợp giọng nói.\n"
        "6. TỔNG HỢP TRI THỨC TOÀN NĂNG: Giải bài toán kỹ thuật, lập trình, tính toán logic và đời sống.\n\n"
        f"KHO TRI THỨC VÀ ĐÍNH CHÍNH:\n{context}\n"
        f"{media_info}\n"
        "Phong thái: Đẳng cấp, siêu thông thái, tư duy mạch lạc, trả lời rõ ràng từng bước (step-by-step), chính xác từng thông số kỹ thuật và cực kỳ thân thiện với người dùng."
    )

    for m in models:
        try:
            url = "https://text.pollinations.ai/"
            headers = {"Content-Type": "application/json", "User-Agent": "AI-Phdam/Superhuman"}
            payload = {
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                "model": m,
                "seed": 777
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Siêu Nhân AI Phdam</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        
        body { 
            background: #060911; 
            color: #f1f5f9; 
            min-height: 100vh;
            display: flex; 
            flex-direction: column; 
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            padding-bottom: 85px;
        }

        .backdrop-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(6, 9, 17, 0.88);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
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

        /* Header */
        .header {
            position: sticky;
            top: 0;
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            background: rgba(15, 23, 42, 0.9);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
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
            gap: 6px;
        }
        .btn-tool {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #e2e8f0;
            padding: 5px 9px;
            border-radius: 8px;
            font-size: 11px;
            cursor: pointer;
        }

        /* Luồng tin nhắn */
        .chat-stream {
            flex: 1;
            padding: 14px 12px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .msg {
            max-width: 88%;
            padding: 12px 14px;
            border-radius: 14px;
            font-size: 14px;
            line-height: 1.5;
            word-break: break-word;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        }
        .msg.bot {
            background: rgba(30, 41, 59, 0.92);
            color: #f8fafc;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.06);
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
            border-radius: 8px;
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

        /* Khay xem trước tệp */
        .attachment-preview {
            display: none;
            position: fixed;
            bottom: 72px;
            left: 0; right: 0;
            z-index: 99;
            background: rgba(15, 23, 42, 0.95);
            padding: 5px 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        .preview-inner {
            max-width: 650px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            gap: 8px;
            background: #1e293b;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 12px;
            width: fit-content;
        }
        .preview-inner img, .preview-inner video {
            width: 30px;
            height: 30px;
            object-fit: cover;
            border-radius: 4px;
        }
        .btn-del-attach {
            background: none;
            border: none;
            color: #ef4444;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-left: 6px;
        }

        /* KHUNG NHẬP CỐ ĐỊNH Ở ĐÁY MÀN HÌNH */
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
        
        /* Nút [+] dùng thẻ label: bấm là mở trực tiếp 100% */
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
            user-select: none;
        }
        .btn-icon-label:active {
            background: rgba(56, 189, 248, 0.2);
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

        /* Nút ENTER */
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
        .btn-enter:active {
            transform: scale(0.95);
        }

        #fileInput, #bgInput {
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
                <h1>⚡ SIÊU NHÂN AI PHDAM</h1>
                <p>Tự động hóa • IoT • Biến tần • Video AI</p>
            </div>
            <div class="header-actions">
                <button class="btn-tool" onclick="document.getElementById('bgInput').click()">🖼️ Đổi nền</button>
                <button class="btn-tool" onclick="resetBg()">↺ Nền gốc</button>
            </div>
        </div>

        <!-- Chat Stream -->
        <div class="chat-stream" id="chatStream">
            <div class="msg bot">
                Chào bồ! Tôi là <b>Siêu Nhân Trí Tuệ Nhân Tạo AI Phdam</b>.<br><br>
                Bồ chạm vào <b>dấu [+]</b> để chọn ảnh/video từ máy, hoặc nhập câu hỏi rồi bấm nút <b>ENTER ↵</b> để tôi giải đáp nhé!
                <button class="speak-btn" onclick="speakText(this.parentElement.innerText)">🔊</button>
            </div>
        </div>
    </div>

    <!-- Khay xem trước tệp đính kèm -->
    <div class="attachment-preview" id="attachPreview">
        <div class="preview-inner">
            <span id="previewMediaBox"></span>
            <span id="attachFileName" style="max-width: 170px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"></span>
            <button class="btn-del-attach" onclick="removeAttachment()">×</button>
        </div>
    </div>

    <!-- KHUNG NHẬP CỐ ĐỊNH Ở ĐÁY MÀN HÌNH -->
    <div class="bottom-bar">
        <form class="bottom-bar-inner" onsubmit="event.preventDefault(); sendPayload();">
            <!-- Nút [+] dạng label gốc: Bấm phát ăn ngay 100% trên mọi điện thoại -->
            <label for="fileInput" class="btn-icon-label" title="Tải ảnh, video, tệp">+</label>
            <input type="file" id="fileInput" accept="image/*,video/*,.txt,.pdf" onchange="handleFileSelected(event)">

            <!-- Ô nhập câu hỏi không bị tràn lề -->
            <input type="text" id="chatInput" class="chat-input" placeholder="Nhập câu hỏi..." autocomplete="off">

            <!-- Nút [🎙️] Micro -->
            <button type="button" class="btn-icon" id="micBtn" onclick="toggleMic()" title="Nói tiếng Việt">🎙️</button>

            <!-- NÚT ENTER -->
            <button type="submit" class="btn-enter" title="Gửi tin nhắn">ENTER ↵</button>
        </form>
    </div>

    <!-- Input đổi ảnh nền cá nhân -->
    <input type="file" id="bgInput" accept="image/*" onchange="changeBackground(event)">

    <script>
        let currentAttach = null;
        let attachDataUrl = '';

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
            const isImage = f.type.startsWith('image');
            
            const reader = new FileReader();
            reader.onload = (evt) => {
                attachDataUrl = evt.target.result;
                const box = document.getElementById('previewMediaBox');
                if (isVideo) {
                    box.innerHTML = `<video src="${attachDataUrl}" muted></video>`;
                    document.getElementById('attachFileName').innerText = '🎥 ' + f.name;
                } else if (isImage) {
                    box.innerHTML = `<img src="${attachDataUrl}">`;
                    document.getElementById('attachFileName').innerText = '📸 ' + f.name;
                } else {
                    box.innerHTML = `📄`;
                    document.getElementById('attachFileName').innerText = '📄 ' + f.name;
                }
                document.getElementById('attachPreview').style.display = 'block';
            };
            reader.readAsDataURL(f);
        }

        function removeAttachment() {
            currentAttach = null;
            attachDataUrl = '';
            document.getElementById('attachPreview').style.display = 'none';
            document.getElementById('fileInput').value = '';
        }

        async function sendPayload() {
            const inp = document.getElementById('chatInput');
            const text = inp.value.trim();

            if (!text && !currentAttach) {
                alert('Bồ hãy nhập câu hỏi hoặc chọn tệp trước khi bấm ENTER nhé!');
                return;
            }

            const stream = document.getElementById('chatStream');

            let userHtml = `<div class="msg user">`;
            if (currentAttach) {
                if (currentAttach.type.startsWith('video')) {
                    userHtml += `<video src="${attachDataUrl}" controls playsinline></video>`;
                } else if (currentAttach.type.startsWith('image')) {
                    userHtml += `<img src="${attachDataUrl}">`;
                } else {
                    userHtml += `<div>📄 Đính kèm: <b>${currentAttach.name}</b></div>`;
                }
            }
            if (text) userHtml += `<div>${text}</div>`;
            userHtml += `</div>`;
            stream.innerHTML += userHtml;
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            const sentAttach = currentAttach;
            inp.value = '';
            removeAttachment();

            const tempId = 'bot_temp_' + Date.now();
            stream.innerHTML += `<div class="msg bot" id="${tempId}">⚡ Siêu Nhân AI đang vận hành tư duy đa tầng...</div>`;
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: text,
                        has_media: !!sentAttach,
                        media_type: sentAttach ? sentAttach.type : ''
                    })
                });

                const d = await res.json();
                const tempBox = document.getElementById(tempId);
                tempBox.innerHTML = `${d.reply} <button class="speak-btn" onclick="speakText('${d.reply.replace(/['"\\n]/g, ' ')}')">🔊</button>`;
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

                if (d.speak) speakText(d.reply);
            } catch (err) {
                const tempBox = document.getElementById(tempId);
                tempBox.innerHTML = `⚠️ Máy chủ đang bận xử lý, bồ bấm ENTER lại nhé!`;
            }
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

    wrong_triggers = ["sai rồi", "nhầm rồi", "không phải", "đâu phải"]
    if any(t in msg.lower() for t in wrong_triggers):
        fix_info = re.sub(r'^(sai rồi|nhầm rồi|không phải|đâu phải)[,.]*\s*', '', msg, flags=re.IGNORECASE)
        mems.append({
            "title": "Đính chính lỗi sai",
            "content": f"ĐÍNH CHÍNH QUAN TRỌNG: {fix_info}"
        })
        save_memory(mems)
        return {
            "reply": f"🛠️ <b>Siêu Nhân AI đã tự đính chính!</b> Tôi đã cập nhật dữ liệu chuẩn xác vào bộ nhớ trung tâm: <i>'{fix_info}'</i>. Lần sau tôi cam kết sẽ phân tích chính xác tuyệt đối!",
            "speak": True
        }

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
                "reply": f"🧠 <b>Đã tiếp thu và ghi nhớ vĩnh viễn!</b> Khối tri thức mới: <i>'{new_know}'</i> đã được nạp vào bộ não tối thượng của Siêu Nhân AI.",
                "speak": True
            }

    context_docs = []
    keywords = [w for w in msg.lower().split() if len(w) > 2]
    for m in mems:
        t = (m["title"] + " " + m["content"]).lower()
        if any(k in t for k in keywords):
            context_docs.append(f"[{m['title']}]: {m['content']}")

    context_str = "\n".join(context_docs[:4]) if context_docs else "Kho dữ liệu công nghệ sẵn sàng."

    effective_prompt = msg if msg else f"Hãy phân tích và đưa ra đánh giá kỹ thuật chuyên sâu về tệp tin {media_type} vừa được gửi lên."
    reply = ask_superhuman_brain(effective_prompt, context_str, has_media, media_type)
    
    if not reply:
        if "biến tần" in msg.lower():
            reply = "Biến tần (VFD) điều khiển tốc độ động cơ 3 pha bằng cách điều biến độ rộng xung PWM, bảo vệ quá dòng, ngắn mạch và tiết kiệm 20-40% điện năng."
        else:
            reply = "Siêu Nhân AI Phdam đã tiếp nhận dữ liệu và đang kích hoạt liên kết tri thức để đưa ra phương án tối ưu nhất cho bồ!"

    return {"reply": reply, "speak": False}
