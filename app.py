from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
import json
import os
import re
from datetime import datetime

app = FastAPI(title="AI An Binh Encyclopedia")

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

def encyclopedia_expert_analysis(msg: str):
    """BÁCH KHOA TOÀN THƯ ĐIỆN CÔNG NGHIỆP & TỰ ĐỘNG HÓA THỰC CHIẾN"""
    text = msg.lower()
    
    # 1. Biến tần & Cài đặt thông số Parameter
    if "biến tần" in text or "vfd" in text or "inverter" in text or "tần số" in text or "parameter" in text or "cài" in text:
        return (
            "📖 <b>BÁCH KHOA TOÀN THƯ: HỆ THỐNG BIẾN TẦN (VFD) & CÀI ĐẶT THÔNG SỐ</b><br><br>"
            "• <b>1. Đấu nối động lực cơ bản:</b><br>"
            "  - <b>Nguồn vào:</b> Cọc <b>R - S - T</b> (Nếu dùng nguồn 1 pha cho biến tần vào 3 pha, cấp lửa vào R, nguội vào T và chọn dòng biến tần phù hợp).<br>"
            "  - <b>Ngõ ra motor:</b> Cọc <b>U - V - W</b> nối trực tiếp xuống động cơ 3 pha. Nếu động cơ quay ngược, đảo 2 trong 3 dây bất kỳ.<br><br>"
            "• <b>2. Nhóm thông số cài đặt (Parameter) cốt lõi:</b><br>"
            "  - <b>Mã lệnh chạy (Source of Run Command):</b> Cài về 0 (chạy bằng bàn phím/RUN trên mặt máy) hoặc 1 (chạy bằng công tắc ngoài qua chân FWD/REV-COM).<br>"
            "  - <b>Mã tần số nguồn (Frequency Source):</b> Cài về bàn phím (Up/Down), hoặc chiết áp ngoài (AI1: 0-10V / 4-20mA).<br>"
            "  - <b>Tần số Max (Max Frequency):</b> Thường đặt 50Hz hoặc 60Hz tùy động cơ.<br>"
            "  - <b>Thời gian tăng tốc (ACC - Acceleration Time):</b> Thường cài từ 5s đến 10s để tránh quá dòng.<br>"
            "  - <b>Thời gian giảm tốc (DEC - Deceleration Time):</b> Thường cài từ 5s đến 10s để tránh lỗi quá áp (Overvoltage).<br><br>"
            "• <b>3. Xử lý mã lỗi thường gặp:</b><br>"
            "  - <i>OC (Overcurrent - Quá dòng):</i> Do kẹt cơ khí, tăng tốc quá nhanh hoặc motor chạm vỏ.<br>"
            "  - <i>OV (Overvoltage - Quá áp):</i> Do giảm tốc quá nhanh, cần lắp điện trở xả hoặc tăng thời gian DEC.<br>"
            "  - <i>OH (Overheat - Quá nhiệt):</i> Do quạt tản nhiệt hỏng hoặc tủ điện bí gió."
        )

    # 2. Contactor & Rơ-le
    elif "contactor" in text or "khởi" in text or "relay" in text or "rơ" in text or "nút nhấn" in text:
        return (
            "📖 <b>BÁCH KHOA TOÀN THƯ: CONTACTOR (KHỞI ĐỘNG TỪ) & MẠCH ĐIỀU KHIỂN</b><br><br>"
            "• <b>1. Sơ đồ chân định danh:</b><br>"
            "  - <b>Cuộn hút:</b> Hai chân <b>A1</b> và <b>A2</b> (Cấp điện áp 220V, 380V hoặc 24VDC tùy tem nhãn để đóng ngắt).<br>"
            "  - <b>Mạch động lực:</b> 3 ngõ vào <b>1L1, 3L2, 5L3</b> và 3 ngõ ra <b>2T1, 4T2, 6T3</b>.<br>"
            "  - <b>Tiếp điểm phụ:</b> Thường mở <b>NO (Normally Open - 13, 14)</b> và Thường đóng <b>NC (Normally Closed)</b> dùng cho mạch tự giữ (duy trì) và khóa liên động.<br><br>"
            "• <b>2. Nguyên lý mạch duy trì (Khởi động động cơ qua nút nhấn):</b><br>"
            "  - Nhấn nút <b>ON (NO)</b>: Dòng điện chạy qua cuộn hút A1-A2, contactor hút, tiếp điểm chính đóng điện cho motor, đồng thời tiếp điểm phụ NO song song với nút ON đóng lại để duy trì nguồn khi nhả tay ra.<br>"
            "  - Nhấn nút <b>OFF (NC)</b>: Ngắt nguồn cuộn hút, contactor nhả ra, động cơ dừng."
        )

    # 3. Aptomat & Bảo vệ điện
    elif "aptomat" in text or "cb" in text or "cp" in text or "át" in text or "cầu chì" in text or "nhiệt" in text:
        return (
            "📖 <b>BÁCH KHOA TOÀN THƯ: THIẾT BỊ BẢO VỆ (APTOMAT / CB / RCCB)</b><br><br>"
            "• <b>1. Phân loại & Chức năng:</b><br>"
            "  - <b>MCB (Miniature Circuit Breaker):</b> Aptomat tép dân dụng và công nghiệp nhẹ, bảo vệ quá tải và ngắn mạch.<br>"
            "  - <b>MCCB (Moulded Case Circuit Breaker):</b> Aptomat khối công suất lớn, chỉnh dòng định mức linh hoạt.<br>"
            "  - <b>ELCB / RCCB:</b> Aptomat chống dòng rò, bảo vệ giật điện.<br><br>"
            "• <b>2. Kinh nghiệm chọn dòng điện định mức (Ampe):</b><br>"
            "  - Dòng điện của Aptomat thường được chọn bằng khoảng <b>1.2 đến 1.5 lần dòng điện định mức (I_dm)</b> của thiết bị tiêu thụ để tránh nhảy át giả khi khởi động mà vẫn bảo vệ an toàn."
        )

    # 4. PLC & HMI & Cảm biến
    elif "plc" in text or "hmi" in text or "cảm biến" in text or "sensor" in text or "npn" in text or "pnp" in text:
        return (
            "📖 <b>BÁCH KHOA TOÀN THƯ: PLC, HMI & CẢM BIẾN CÔNG NGHIỆP</b><br><br>"
            "• <b>1. Phân biệt cảm biến NPN và PNP:</b><br>"
            "  - <b>NPN (Sink - Ngõ ra âm):</b> Khi có tín hiệu, ngõ ra nối chung với chân 0V (GND). Dùng chung với PLC ngõ vào dạng Common là 24V.<br>"
            "  - <b>PNP (Source - Ngõ ra dương):</b> Khi có tín hiệu, ngõ ra xuất điện áp 24V. Dùng chung với PLC ngõ vào dạng Common là 0V.<br><br>"
            "• <b>2. PLC (Programmable Logic Controller):</b> Là bộ điều khiển lập trình trung tâm, nhận tín hiệu từ nút nhấn, cảm biến (Inputs) và điều khiển cuộn hút, đèn báo, biến tần (Outputs) theo thuật toán lập trình sẵn."
        )

    # Mặc định: Tổng hợp bách khoa toàn thư
    else:
        return (
            "📖 <b>BÁCH KHOA TOÀN THƯ ĐIỆN CÔNG NGHIỆP & TỰ ĐỘNG HÓA</b><br><br>"
            "Tui đã nạp đầy đủ toàn bộ kho tàng kiến thức thực chiến vào hệ thống. Bồ có thể tra cứu bất kỳ chủ đề nào bằng cách gõ trực tiếp:<br><br>"
            "• <b>Biến tần & Parameter:</b> Cách cài đặt, đấu nối, mã lỗi OC, OV.<br>"
            "• <b>Contactor & Mạch điện:</b> Sơ đồ chân A1-A2, mạch tự giữ, khóa chéo.<br>"
            "• <b>Aptomat & Bảo vệ:</b> Cách chọn dòng CB, phân biệt MCB, MCCB.<br>"
            "• <b>Cảm biến & PLC:</b> Phân biệt NPN / PNP, đấu nối ngõ vào ra.<br><br>"
            "<i>Bồ muốn tra cứu chi tiết phần nào, cứ gõ tên thiết bị hoặc câu hỏi cụ thể, tui trả lời ngay lập tức!</i>"
        )

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI AN BÌNH - BÁCH KHOA</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: #050811; color: #f1f5f9; min-height: 100vh; display: flex; flex-direction: column; background-size: cover; background-position: center; padding-bottom: 85px; }
        .overlay { position: fixed; inset: 0; background: rgba(5,8,17,0.88); backdrop-filter: blur(8px); z-index: 1; }
        .app { position: relative; z-index: 2; max-width: 650px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; flex: 1; }
        .header { position: sticky; top: 0; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(15,23,42,0.95); border-bottom: 1px solid rgba(255,255,255,0.1); }
        .header h1 { font-size: 17px; color: #ffffff; font-weight: 800; letter-spacing: 0.5px; }
        .header p { font-size: 10px; color: #38bdf8; font-weight: bold; }
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
                <p>📖 Bách Khoa Toàn Thư Điện Công Nghiệp</p>
            </div>
            <div style="display:flex; gap:5px;">
                <button class="btn-tool" id="vaultBtn" onclick="window.open('/api/export-brain')">📥 Não (0)</button>
                <button class="btn-tool" onclick="document.getElementById('bgInp').click()">🖼️ Nền</button>
                <button class="btn-tool btn-key-on">⚡ VIP</button>
            </div>
        </div>
        <div class="chat-stream" id="stream">
            <div class="msg bot">
                <div class="badge">📖 BÁCH KHOA TOÀN THƯ ĐÃ SẴN SÀNG</div>
                <div class="bot-text">Chào bồ! Tui là <b>AI An Bình</b> phiên bản Bách Khoa Toàn Thư.<br><br>Hệ thống đã nạp trọn bộ kiến thức về Biến tần, Contactor, Aptomat, PLC và cảm biến. Bồ muốn tra cứu bất kỳ thông số hay cách đấu nối nào, cứ gõ vào đây nhé!</div>
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
            <input type="text" id="chatInp" class="chat-input" placeholder="Hỏi biến tần, contactor, NPN/PNP..." autocomplete="off">
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
            if (!txt && !curImg) return alert("Bồ hãy nhập nội dung cần tra cứu nhé!");

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
            st.innerHTML += `<div class="msg bot" id="${tId}"><div class="badge">📖 ĐANG TRA CỨU BÁCH KHOA TOÀN THƯ...</div><div class="bot-text">Đang trích xuất tri thức chuyên ngành...</div></div>`;
            window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: txt })
                });
                const d = await res.json();
                
                document.getElementById(tId).innerHTML = `
                    <div class="badge">💡 KẾT QUẢ TRA CỨU CHUYÊN SÂU</div>
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
    return Response(content=json.dumps(get_vault(), ensure_ascii=False, indent=2), media_type="application/json", headers={"Content-Disposition": "attachment; filename=AI_AnBinh_Encyclopedia.json"})

@app.post("/api/save-memory")
async def save_memory_endpoint(req: Request):
    d = await req.json()
    save_to_vault(d.get("query", "Ghi chú"), d.get("answer", ""))
    return {"status": "success"}

@app.post("/api/chat")
async def chat_endpoint(req: Request):
    data = await req.json()
    msg = data.get("message", "").strip()
    ans = encyclopedia_expert_analysis(msg)
    formatted = clean_text_for_display(ans)
    save_to_vault(msg, formatted)
    return {"reply": formatted}
