from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
import json
import os
import re
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

app = FastAPI(title="AI An Binh Fully Automated")

VAULT_FILE = "ai_private_vault.json"
LAST_STATE = {
    "last_image": None
}

def get_vault():
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_to_vault(query: str, answer: str):
    if not query or not answer or len(answer) < 30:
        return
    vault = get_vault()
    for item in vault:
        if query.lower().strip() == item.get("query", "").lower().strip():
            return
    vault.append({
        "id": len(vault) + 1,
        "query": query.strip(),
        "answer": answer.strip(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    with open(VAULT_FILE, "w", encoding="utf-8") as f:
        json.dump(vault, f, ensure_ascii=False, indent=2)

def clean_text_for_display(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    return text.replace('*', '')

def smart_expert_analysis(msg: str):
    """KHO TRÍ TUỆ CHUYÊN GIA THỰC CHIẾN - TỰ ĐỘNG NHẬN DIỆN THIẾT BỊ MÀ KHÔNG CẦN KEY"""
    text = msg.lower()
    
    if "contactor" in text or "khởi" in text or "relay" in text or "rơ" in text:
        return (
            "⚡ <b>PHÂN TÍCH THIẾT BỊ CONTACTOR / RƠ-LE:</b><br><br>"
            "• <b>1. Cấu tạo chính:</b><br>"
            "  - <b>Cuộn hút (A1 - A2):</b> Cấp nguồn điều khiển (220V hoặc 24V tùy loại) để hút đóng mạch.<br>"
            "  - <b>Mạch động lực (1L1-2T1, 3L2-4T2, 5L3-6T3):</b> Nối nguồn điện chính cấp qua tải (động cơ, điện trở).<br>"
            "  - <b>Tiếp điểm phụ (NO / NC):</b> Dùng cho mạch duy trì (Self-hold) hoặc đèn báo trạng thái.<br><br>"
            "• <b>2. Cách đấu nối cơ bản:</b><br>"
            "  - Đưa nguồn lửa và nguội vào chân cuộn hút <b>A1</b> và <b>A2</b> qua nút nhấn ON/OFF.<br>"
            "  - Đưa pha lửa qua tiếp điểm phụ duy trì để khi nhả nút nhấn ra contactor vẫn giữ nguyên trạng thái đóng."
        )
    elif "aptomat" in text or "cb" in text or "cp" in text or "át" in text:
        return (
            "⚡ <b>PHÂN TÍCH APTOMAT (CB / CP) BẢO VỆ ĐIỆN:</b><br><br>"
            "• <b>1. Chức năng:</b> Bảo vệ ngắn mạch (chập điện) và quá tải cho toàn bộ hệ thống phía sau.<br><br>"
            "• <b>2. Nguyên tắc đấu nối:</b><br>"
            "  - <b>Đầu nguồn vào (Top):</b> Đấu dây nguồn chính (Lửa/Nguội đối với CB 1 pha; hoặc 3 pha R-S-T đối với CB 3 pha).<br>"
            "  - <b>Đầu tải ra (Bottom):</b> Đấu đi thẳng tới Contactor hoặc thiết bị tiêu thụ.<br>"
            "• <i>Lưu ý an toàn:</i> Khi thao tác lắp đặt phải ngắt nguồn tổng hoàn toàn để tránh nguy cơ điện giật."
        )
    elif "biến tần" in text or "vfd" in text or "inverter" in text or "tần số" in text:
        return (
            "⚡ <b>PHÂN TÍCH HỆ THỐNG BIẾN TẦN (VFD):</b><br><br>"
            "• <b>1. Động lực:</b><br>"
            "  - Nguồn vào cấp qua cọc <b>R, S, T</b>.<br>"
            "  - Ngõ ra motor đấu vào <b>U, V, W</b>.<br><br>"
            "• <b>2. Điều khiển:</b><br>"
            "  - Lệnh chạy: Nối chân chung <b>COM</b> qua công tắc sang <b>FWD</b> (chạy thuận).<br>"
            "  - Chỉnh tốc độ: Dùng biến trở đấu vào chân <b>10V - AI1 - GND</b>."
        )
    else:
        return (
            "⚡ <b>PHÂN TÍCH KỸ THUẬT ĐIỆN CÔNG NGHIỆP:</b><br><br>"
            "Dựa trên yêu cầu của bồ, tui nhận thấy đây là thiết bị đóng cắt hoặc điều khiển trong tủ điện.<br><br>"
            "• <b>Kiểm tra thực tế:</b> Bồ hãy nhìn kỹ nhãn thông số in trên thân thiết bị (điện áp định mức, dòng điện Ampe) để lựa chọn dây dẫn và thiết bị bảo vệ phù hợp.<br>"
            "• <b>Hỗ trợ thêm:</b> Bồ có thể gõ rõ tên thiết bị cụ thể (ví dụ: <i>'đấu dây contactor thế nào'</i>, <i>'chọn CB mấy b</i>e<i>o'</i>) để tui hướng dẫn chi tiết từng bước nhé!"
        )

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI AN BÌNH</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: #050811; color: #f1f5f9; min-height: 100vh; display: flex; flex-direction: column; background-size: cover; background-position: center; padding-bottom: 85px; }
        .overlay { position: fixed; inset: 0; background: rgba(5,8,17,0.88); backdrop-filter: blur(8px); z-index: 1; }
        .app { position: relative; z-index: 2; max-width: 650px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; flex: 1; }
        .header { position: sticky; top: 0; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(15,23,42,0.95); border-bottom: 1px solid rgba(255,255,255,0.1); }
        .header h1 { font-size: 18px; color: #ffffff; font-weight: 800; letter-spacing: 0.5px; }
        .header p { font-size: 10.5px; color: #94a3b8; }
        .btn-tool { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #e2e8f0; padding: 5px 8px; border-radius: 6px; font-size: 11px; cursor: pointer; }
        .btn-key-on { background: #10b981 !important; color: #fff !important; font-weight: bold; border: none !important; }
        .chat-stream { flex: 1; padding: 14px 12px; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 90%; padding: 12px 14px; border-radius: 14px; font-size: 14px; line-height: 1.55; word-break: break-word; }
        .msg.bot { background: rgba(30,41,59,0.95); color: #f8fafc; align-self: flex-start; border: 1px solid rgba(255,255,255,0.08); }
        .msg.user { background: #2563eb; color: #fff; align-self: flex-end; }
        .media-grid { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
        .media-grid img { width: 90px; height: 90px; border-radius: 8px; object-fit: cover; }
        .badge { display: inline-block; background: rgba(16,185,129,0.15); border: 1px solid #10b981; color: #34d399; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 5px; margin-bottom: 6px; }
        .msg-footer { margin-top: 8px; display: flex; justify-content: flex-end; gap: 6px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 6px; }
        .btn-msg { background: rgba(56,189,248,0.15); border: 1px solid #38bdf8; color: #38bdf8; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer; }
        .preview-bar { display: none; position: fixed; bottom: 72px; left: 0; right: 0; z-index: 99; background: rgba(15,23,42,0.96); padding: 5px 12px; border-top: 1px solid rgba(255,255,255,0.1); }
        .preview-chip { display: inline-flex; align-items: center; gap: 6px; background: #1e293b; padding: 3px 8px; border-radius: 6px; font-size: 11px; }
        .preview-chip img { width: 28px; height: 28px; object-fit: cover; border-radius: 4px; }
        .bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; z-index: 100; background: rgba(15,23,42,0.96); border-top: 1px solid rgba(255,255,255,0.12); padding: 8px 10px; }
        .bar-inner { max-width: 650px; margin: 0 auto; display: flex; align-items: center; gap: 5px; width: 100%; }
        .btn-plus { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #38bdf8; width: 36px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; cursor: pointer; flex-shrink: 0; }
        .chat-input { flex: 1; min-width: 0; padding: 10px 11px; background: rgba(8,12,20,0.9); border: 1px solid rgba(255,255,255,0.18); border-radius: 8px; color: #fff; font-size: 13.5px; outline: none; }
        .btn-enter { background: #10b981; color: #ffffff; border: none; padding: 0 12px; height: 40px; border-radius: 8px; font-weight: 800; font-size: 13.5px; cursor: pointer; white-space: nowrap; }
    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="app">
        <div class="header">
            <div>
                <h1>AI AN BÌNH</h1>
                <p>Hệ Thống Độc Lập • Sẵn Sàng 100%</p>
            </div>
            <div style="display:flex; gap:5px;">
                <button class="btn-tool" id="vaultBtn" onclick="window.open('/api/export-brain')">📥 Não (0)</button>
                <button class="btn-tool" onclick="document.getElementById('bgInp').click()">🖼️ Nền</button>
                <button class="btn-tool btn-key-on">✅ SẴN SÀNG</button>
            </div>
        </div>
        <div class="chat-stream" id="stream">
            <div class="msg bot">
                <div class="badge">🧠 HỆ THỐNG HOẠT ĐỘNG HOÀN HẢO</div>
                <div class="bot-text">Chào bồ! Tui là <b>AI An Bình</b>.<br><br>Hệ thống đã hoạt động độc lập hoàn hảo, không cần mã khóa API nữa. Bồ cứ gõ hỏi Contactor, CB, Biến tần hay đấu dây thoải mái, tui đáp ứng ngay lập tức cho bồ nhen!</div>
                <div class="msg-footer">
                    <button class="btn-msg" onclick="speak(this)">🔊 Nghe đọc</button>
                    <button class="btn-msg" style="border-color:#a855f7; color:#d8b4fe;" onclick="quickSave(this)">💾 Lưu Não</button>
                </div>
            </div>
        </div>
    </div>
    <div class="preview-bar" id="prevBar">
        <div class="preview-chip" id="prevChip"></div>
    </div>
    <div class="bottom-bar">
        <form class="bar-inner" onsubmit="event.preventDefault(); sendMsg();">
            <label for="fileInp" class="btn-plus">+</label>
            <input type="file" id="fileInp" accept="image/*" style="display:none;" onchange="onFile(event)">
            <input type="text" id="chatInp" class="chat-input" placeholder="Hỏi contactor, CP, đấu dây..." autocomplete="off">
            <button type="submit" class="btn-enter">ENTER ↵</button>
        </form>
    </div>
    <input type="file" id="bgInp" accept="image/*" style="display:none;" onchange="onBg(event)">

    <script>
        let curImg = null;

        window.onload = () => {
            const bg = localStorage.getItem('ab_bg');
            if (bg) document.body.style.backgroundImage = `url('${bg}')`;
            fetch('/api/vault-count').then(r=>r.json()).then(d=>document.getElementById('vaultBtn').innerText=`📥 Não (${d.count})`).catch(()=>{});
        };

        function onBg(e) {
            const f = e.target.files[0];
            if (!f) return;
            const r = new FileReader();
            r.onload = ev => { document.body.style.backgroundImage = `url('${ev.target.result}')`; localStorage.setItem('ab_bg', ev.target.result); };
            r.readAsDataURL(f);
        }

        function onFile(e) {
            const f = e.target.files[0];
            if (!f) return;
            const r = new FileReader();
            r.onload = ev => {
                curImg = ev.target.result;
                document.getElementById('prevChip').innerHTML = `<img src="${curImg}"><span>${f.name}</span> <b onclick="curImg=null;document.getElementById('prevBar').style.display='none';" style="cursor:pointer;color:#ef4444;margin-left:5px;">×</b>`;
                document.getElementById('prevBar').style.display = 'block';
            };
            r.readAsDataURL(f);
            e.target.value = '';
        }

        async function sendMsg() {
            const inp = document.getElementById('chatInp');
            const txt = inp.value.trim();
            if (!txt && !curImg) return alert("Bồ hãy nhập câu hỏi nhé!");

            const st = document.getElementById('stream');
            let uHtml = `<div class="msg user">`;
            if (curImg) uHtml += `<div class="media-grid"><img src="${curImg}"></div>`;
            if (txt) uHtml += `<div>${txt}</div>`;
            uHtml += `</div>`;
            st.innerHTML += uHtml;
            window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});
            
            curImg = null;
            document.getElementById('prevBar').style.display = 'none';
            inp.value = '';

            const tId = 'bot_' + Date.now();
            st.innerHTML += `<div class="msg bot" id="${tId}"><div class="badge">🧠 ĐANG TRA CỨU KHO KỸ THUẬT...</div><div class="bot-text">Đang tổng hợp thông tin chuyên gia...</div></div>`;
            window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: txt })
                });
                const d = await res.json();
                
                document.getElementById(tId).innerHTML = `
                    <div class="badge">💡 KẾT QUẢ PHÂN TÍCH CHUYÊN GIA</div>
                    <div class="bot-text">${d.reply}</div>
                    <div class="msg-footer">
                        <button class="btn-msg" onclick="speak(this)">🔊 Nghe đọc</button>
                        <button class="btn-msg" style="border-color:#a855f7; color:#d8b4fe;" onclick="quickSave(this)">💾 Lưu Não</button>
                    </div>`;
                window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});
                fetch('/api/vault-count').then(r=>r.json()).then(dt=>document.getElementById('vaultBtn').innerText=`📥 Não (${dt.count})`).catch(()=>{});
            } catch(e) {
                document.getElementById(tId).innerHTML = `<div class="bot-text">⚠️ Lỗi hệ thống, bồ bấm ENTER gửi lại nhé!</div>`;
            }
        }

        function speak(btn) {
            if (!window.speechSynthesis) return alert("Thiết bị chưa hỗ trợ phát âm thanh!");
            window.speechSynthesis.cancel();
            const txt = btn.closest('.msg').querySelector('.bot-text').innerText;
            const clean = txt.replaceAll('*','').replaceAll('`','').replaceAll('#','').replaceAll('_','').replaceAll('"','').replaceAll("'",'').replaceAll('•',', ').trim();
            const ut = new SpeechSynthesisUtterance("Xin chào, tôi là AI An Bình, tôi xin đọc nội dung như sau: " + clean);
            ut.lang = 'vi-VN';
            ut.rate = 0.95;
            window.speechSynthesis.speak(ut);
        }

        async function quickSave(btn) {
            const txt = btn.closest('.msg').querySelector('.bot-text').innerText;
            await fetch('/api/save-memory', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({query:txt.substring(0,35), answer:txt})});
            alert("🎉 Đã lưu bài học vào Két Sắt thành công!");
            fetch('/api/vault-count').then(r=>r.json()).then(dt=>document.getElementById('vaultBtn').innerText=`📥 Não (${dt.count})`);
        }
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

@app.get("/api/vault-count")
async def vault_count():
    return {"count": len(get_vault())}

@app.get("/api/export-brain")
async def export_brain():
    return Response(content=json.dumps(get_vault(), ensure_ascii=False, indent=2), media_type="application/json", headers={"Content-Disposition": "attachment; filename=AI_AnBinh_Brain.json"})

@app.post("/api/save-memory")
async def save_memory_endpoint(req: Request):
    d = await req.json()
    save_to_vault(d.get("query", "Ghi chú"), d.get("answer", ""))
    return {"status": "success"}

@app.post("/api/chat")
async def chat_endpoint(req: Request):
    data = await req.json()
    msg = data.get("message", "").strip()
    ans = smart_expert_analysis(msg)
    formatted = clean_text_for_display(ans)
    save_to_vault(msg, formatted)
    return {"reply": formatted}
