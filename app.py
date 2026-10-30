import json
import os
import re
import urllib.request
import urllib.parse
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="AI Phdam Autonomous Pro")

MEMORY_FILE = "ai_memory.json"

def get_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {
            "title": "Kiến thức căn bản: Biến tần (Inverter/VFD)",
            "content": "Biến tần là thiết bị điện tử làm biến đổi tần số dòng điện để điều khiển tốc độ và mô-men xoắn của động cơ 3 pha vô cấp, bảo vệ quá dòng, chống sốc cơ khí và tiết kiệm điện năng."
        }
    ]

def save_memory(memories):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

def extract_text_from_url(url: str):
    """Tự động cào và bóc tách chữ từ đường link web"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8', errors='ignore')
            html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
            html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', html)
            lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 30]
            clean_text = " ".join(lines[:25])
            return clean_text[:2500] if clean_text else None
    except Exception:
        return None

def call_ai_multi_brain(system_prompt: str, user_prompt: str):
    """Hệ thống đa não tự phục hồi lỗi (Multi-Engine Resilience)"""
    models = ["openai", "mistral", "qwen"]
    for m in models:
        try:
            url = "https://text.pollinations.ai/"
            headers = {"Content-Type": "application/json", "User-Agent": "AI-Phdam/4.0"}
            data = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "model": m,
                "seed": 42
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                res = response.read().decode("utf-8").strip()
                if res and len(res) > 10:
                    return res
        except Exception:
            continue
    return None

HTML_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI Phdam V-Pro Max</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: #080c14; color: #f1f5f9; min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 12px; }
        .header { text-align: center; margin: 10px 0; width: 100%; max-width: 500px; }
        .header h1 { font-size: 24px; background: linear-gradient(135deg, #00f2fe, #4facfe, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .status-bar { background: #111827; border-radius: 12px; padding: 8px 14px; margin-top: 6px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; border: 1px solid #1f2937; }
        .badge { background: #8b5cf6; padding: 2px 8px; border-radius: 10px; font-weight: bold; }
        .tabs { display: flex; gap: 6px; width: 100%; max-width: 500px; margin: 10px 0; }
        .tab-btn { flex: 1; padding: 10px; background: #111827; color: #94a3b8; border: 1px solid #1f2937; border-radius: 8px; font-weight: bold; font-size: 13px; cursor: pointer; }
        .tab-btn.active { background: #2563eb; color: #fff; border-color: #3b82f6; }
        .panel { display: none; width: 100%; max-width: 500px; background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 16px; }
        .panel.active { display: block; }
        /* Chat */
        .chat-box { height: 350px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding-right: 4px; }
        .msg { max-width: 85%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.5; word-break: break-word; }
        .msg.bot { background: #1e293b; color: #f8fafc; align-self: flex-start; border-bottom-left-radius: 2px; position: relative; }
        .msg.user { background: #2563eb; color: #fff; align-self: flex-end; border-bottom-right-radius: 2px; }
        .msg.alert { background: rgba(245,158,11,0.15); border: 1px dashed #f59e0b; color: #fbbf24; font-size: 12px; align-self: center; text-align: center; width: 100%; }
        .speak-btn { background: none; border: none; font-size: 15px; cursor: pointer; margin-left: 6px; vertical-align: middle; }
        .chat-row { display: flex; gap: 6px; margin-top: 10px; }
        .chat-input { flex: 1; padding: 12px; background: #080c14; border: 1px solid #334155; border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
        .btn-action { padding: 0 14px; background: #38bdf8; color: #080c14; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .btn-mic { background: #1e293b; color: #38bdf8; border: 1px solid #334155; font-size: 16px; padding: 0 12px; }
        /* Training */
        .input-text { width: 100%; padding: 10px; background: #080c14; border: 1px solid #334155; border-radius: 8px; color: #fff; font-size: 13px; margin-bottom: 8px; outline: none; }
        .btn-learn { width: 100%; padding: 12px; background: linear-gradient(135deg, #a855f7, #6366f1); color: #fff; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; margin-bottom: 12px; }
        .mem-item { background: #131b2e; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; font-size: 12px; border-left: 3px solid #8b5cf6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ AI PHDAM V-PRO MAX</h1>
        <div class="status-bar">
            <span>🛡️ Trí tuệ: <b>Tự học & Tự sửa sai</b></span>
            <span class="badge" id="iqBadge">IQ Level: 160</span>
        </div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="tab('chat')">💬 Hội thoại Thông thái</button>
        <button class="tab-btn" onclick="tab('train')">🧠 Nạp Tri thức & Link</button>
    </div>

    <!-- Chat Panel -->
    <div id="p-chat" class="panel active">
        <div class="chat-box" id="chatBox">
            <div class="msg alert">💡 <b>Cơ chế Tự Sửa Sai:</b> Nếu AI trả lời chưa đúng, bồ chỉ cần nói <i>"Sai rồi, phải là [ý đúng] mới chuẩn"</i>, AI sẽ tự khắc phục ngay!</div>
            <div class="msg bot">Chào bồ! Tôi là siêu AI Phdam V-Pro Max. Tôi đã sẵn sàng nghe giọng nói, đọc tài liệu và hỗ trợ giải đáp mọi bài toán kỹ thuật. <button class="speak-btn" onclick="speakText(this.parentElement.innerText)">🔊</button></div>
        </div>
        <div class="chat-row">
            <button class="btn-action btn-mic" id="micBtn" onclick="toggleMic()">🎙️</button>
            <input type="text" id="chatInp" class="chat-input" placeholder="Nói hoặc gõ câu hỏi..." onkeypress="if(event.key==='Enter') sendChat()">
            <button class="btn-action" onclick="sendChat()">Gửi</button>
        </div>
    </div>

    <!-- Training Panel -->
    <div id="p-train" class="panel">
        <h4 style="font-size:13px; color:#38bdf8; margin-bottom:6px">🌐 1. Tự học từ đường Link Web:</h4>
        <input type="text" id="urlInput" class="input-text" placeholder="Dán link bài viết/tài liệu (https://...)">
        <button class="btn-learn" onclick="learnFromUrl()">📥 Quét & Nuốt Tri thức từ Link</button>

        <h4 style="font-size:13px; color:#a855f7; margin-bottom:6px">📖 2. Tự nạp văn bản thủ công:</h4>
        <input type="text" id="docTitle" class="input-text" placeholder="Tiêu đề tài liệu">
        <textarea id="docContent" class="input-text" style="height:90px; resize:none;" placeholder="Dán nội dung kỹ thuật vào đây..."></textarea>
        <button class="btn-learn" onclick="trainManual()">⚡ Nạp vào Vỏ Não</button>

        <h4 style="font-size:13px; color:#94a3b8; margin: 10px 0 6px">🗂️ Kho Tri thức đã học:</h4>
        <div id="memList" style="max-height:140px; overflow-y:auto;"></div>
    </div>

    <script>
        function tab(t) {
            document.querySelectorAll('.tab-btn').forEach((b,i)=>b.classList.toggle('active', (t==='chat'&&i===0)||(t==='train'&&i===1)));
            document.getElementById('p-chat').classList.toggle('active', t==='chat');
            document.getElementById('p-train').classList.toggle('active', t==='train');
            if(t==='train') loadMemories();
        }

        async function loadMemories() {
            const res = await fetch('/api/memories');
            const data = await res.json();
            document.getElementById('memList').innerHTML = data.map(m=>`<div class="mem-item"><b>${m.title}</b><br>${m.content.substring(0,80)}...</div>`).join('');
            document.getElementById('iqBadge').innerText = 'IQ Level: ' + (150 + data.length * 6);
        }

        async function trainManual() {
            const title = document.getElementById('docTitle').value.trim();
            const content = document.getElementById('docContent').value.trim();
            if(!title || !content) return alert('Bồ điền đủ tiêu đề và nội dung nhé!');
            await fetch('/api/train', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ title, content }) });
            document.getElementById('docTitle').value = '';
            document.getElementById('docContent').value = '';
            alert('✅ Đã nạp thành công!');
            loadMemories();
        }

        async function learnFromUrl() {
            const url = document.getElementById('urlInput').value.trim();
            if(!url.startsWith('http')) return alert('Bồ nhập link chuẩn bắt đầu bằng https:// nhé!');
            const btn = event.target;
            btn.innerText = '⏳ AI đang quét và đọc nội dung web...';
            const res = await fetch('/api/learn-url', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ url }) });
            const d = await res.json();
            btn.innerText = '📥 Quét & Nuốt Tri thức từ Link';
            if(d.status === 'success') {
                alert('🎉 Tuyệt vời! AI đã đọc và ghi nhớ toàn bộ nội dung từ trang web!');
                document.getElementById('urlInput').value = '';
                loadMemories();
            } else {
                alert('Trang web chặn quét hoặc link lỗi, bồ thử link khác nhé!');
            }
        }

        async function sendChat() {
            const inp = document.getElementById('chatInp');
            const q = inp.value.trim();
            if (!q) return;
            inp.value = '';
            const box = document.getElementById('chatBox');
            box.innerHTML += `<div class="msg user">${q}</div>`;
            box.scrollTop = box.scrollHeight;

            const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ message: q }) });
            const d = await res.json();
            
            box.innerHTML += `<div class="msg bot">${d.reply} <button class="speak-btn" onclick="speakText('${d.reply.replace(/['"\\n]/g, ' ')}')">🔊</button></div>`;
            box.scrollTop = box.scrollHeight;
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
            if (!SpeechRec) return alert('Trình duyệt chưa hỗ trợ ghi âm trực tiếp, bồ dùng bàn phím gõ nhé!');
            if (recognition) { recognition.stop(); recognition = null; mic.style.background = '#1e293b'; return; }
            recognition = new SpeechRec();
            recognition.lang = 'vi-VN';
            recognition.start();
            mic.style.background = '#ef4444';
            recognition.onresult = (e) => {
                document.getElementById('chatInp').value = e.results[0][0].transcript;
                recognition.stop();
                recognition = null;
                mic.style.background = '#1e293b';
                sendChat();
            };
            recognition.onerror = () => { recognition = null; mic.style.background = '#1e293b'; };
        }
        loadMemories();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

@app.get("/api/memories")
async def get_mems():
    return get_memory()

@app.post("/api/train")
async def train_text(req: Request):
    d = await req.json()
    mems = get_memory()
    mems.append({"title": d.get("title", "Tài liệu"), "content": d.get("content", "")})
    save_memory(mems)
    return {"status": "success"}

@app.post("/api/learn-url")
async def learn_url(req: Request):
    d = await req.json()
    url = d.get("url", "")
    content = extract_text_from_url(url)
    if content:
        mems = get_memory()
        parsed = urllib.parse.urlparse(url).netloc
        mems.append({"title": f"Tài liệu tự học từ: {parsed}", "content": content})
        save_memory(mems)
        return {"status": "success"}
    return {"status": "failed"}

@app.post("/api/chat")
async def chat_endpoint(req: Request):
    data = await req.json()
    msg = data.get("message", "").strip()
    mems = get_memory()

    # 1. Cơ chế Tự sửa sai (Self-Correction & Reflection)
    wrong_triggers = ["sai rồi", "nhầm rồi", "không phải", "đâu phải"]
    if any(t in msg.lower() for t in wrong_triggers):
        fix_info = re.sub(r'^(sai rồi|nhầm rồi|không phải|đâu phải)[,.]*\s*', '', msg, flags=re.IGNORECASE)
        mems.append({
            "title": "Hiệu chỉnh khắc phục sai sót",
            "content": f"ĐÍNH CHÍNH LỖI SAI: {fix_info}"
        })
        save_memory(mems)
        return {
            "reply": f"🛠️ <b>AI Phdam đã tự giác sửa lỗi!</b> Tôi đã ghi đè dữ liệu đính chính vào bộ não: <i>'{fix_info}'</i>. Cảm ơn bồ đã chỉ dạy, tôi cam kết lần sau sẽ trả lời chuẩn xác!",
            "speak": True
        }

    # 2. Cơ chế RAG: Tìm tài liệu liên quan trong kho tri thức
    context_docs = []
    keywords = [w for w in msg.lower().split() if len(w) > 2]
    for mem in mems:
        txt = (mem["title"] + " " + mem["content"]).lower()
        if any(k in txt for k in keywords):
            context_docs.append(f"[{mem['title']}]: {mem['content']}")

    context_str = "\n".join(context_docs[:4]) if context_docs else "Chưa có ghi chú riêng."

    # 3. Kích hoạt Đa Não AI
    sys_prompt = (
        "Bạn là AI Phdam V-Pro Max, một siêu trí tuệ nhân tạo có khả năng tự sửa lỗi và suy luận sâu sắc. "
        f"KHO TÀI LIỆU VÀ GHI NHỚ ĐÃ ĐÍNH CHÍNH CỦA BẠN:\n{context_str}\n\n"
        "Hãy ưu tiên tuyệt đối các thông tin đính chính nếu có. Trả lời súc tích, chuyên sâu, thông minh và thân thiện."
    )
    
    reply = call_ai_multi_brain(sys_prompt, msg)
    if not reply:
        reply = "Tôi đã ghi nhận câu hỏi. Bộ não đang xử lý dữ liệu và tiếp tục đồng bộ kho tài liệu của bồ!"

    return {"reply": reply, "speak": False}
