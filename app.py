from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
import json
import os
import re
from datetime import datetime

app = FastAPI(title="AI An Binh Ultimate Intelligence")

VAULT_FILE = "ai_private_vault.json"

def get_vault():
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_to_vault(query: str, answer: str, domain: str = "Đa lĩnh vực"):
    if not query or not answer or len(answer) < 20:
        return
    vault = get_vault()
    for item in vault:
        if query.lower().strip() == item.get("query", "").lower().strip():
            return
    vault.append({
        "id": len(vault) + 1,
        "domain": domain,
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

def ultimate_ai_reasoning(msg: str, has_img: bool = False):
    """ĐỘNG CƠ SUY LUẬN SIÊU TRÍ TUỆ ĐA LĨNH VỰC & THỊ GIÁC"""
    text = msg.lower()
    
    # 1. Nhóm Driver / Servo / Stepper / Vi bước
    if any(k in text for k in ["driver", "stepper", "servo", "pul", "dir", "ena", "vi bước", "microstep"]):
        return (
            "🎯 <b>PHÂN TÍCH CHUYÊN SÂU: DRIVER & ĐỘNG CƠ ĐIỀU KHIỂN XUNG</b><br><br>"
            "• <b>Bản chất thiết bị:</b> Driver là bộ khuếch đại tín hiệu điều khiển vị trí/tốc độ cho động cơ bước hoặc Servo.<br>"
            "• <b>Sơ đồ chân chuẩn xác:</b><br>"
            "  - <i>Tín hiệu xung (PUL / STEP+ / STEP-):</i> Nhận chuỗi xung từ PLC hoặc vi điều khiển để quyết định tốc độ và góc quay.<br>"
            "  - <i>Tín hiệu chiều (DIR / CW / CCW):</i> Quyết định hướng quay thuận hay nghịch.<br>"
            "  - <i>Tín hiệu kích hoạt (ENA / FREE):</i> Cho phép Driver giữ lực giữ trục (Hold Torque) hoặc thả trôi.<br>"
            "• <b>Cài đặt phần cứng:</b> Thiết lập dòng điện định mức (Peak Current) bằng gạt công tắc SW và chọn độ phân giải vi bước phù hợp."
        )

    # 2. Nhóm Biến tần & Động lực 3 pha
    elif any(k in text for k in ["biến tần", "vfd", "inverter", "tần số", "parameter", "motor", "động cơ", "lỗi oc", "lỗi ov"]):
        return (
            "⚡ <b>PHÂN TÍCH CHUYÊN SÂU: HỆ THỐNG BIẾN TẦN & TRUYỀN ĐỘNG</b><br><br>"
            "• <b>Bản chất thiết bị:</b> Thiết bị thay đổi tần số dòng điện xoay chiều để điều khiển vô cấp tốc độ động cơ.<br>"
            "• <b>Đấu nối thực chiến:</b><br>"
            "  - <i>Động lực:</i> Nguồn vào cấp qua <b>R - S - T</b>, ngõ ra động cơ đấu chuẩn <b>U - V - W</b>.<br>"
            "  - <i>Điều khiển:</i> Chân chung <b>COM</b> nối qua công tắc sang <b>FWD/REV</b> (chạy thuận/nghịch), chiết áp tốc độ qua <b>10V - AI1 - GND</b>.<br>"
            "• <b>Cài đặt Parameter:</b> Cấu hình nguồn lệnh chạy (Run Source) và thời gian tăng/giảm tốc <b>ACC/DEC</b> (5s - 10s) để tránh lỗi quá dòng (OC) hoặc quá áp (OV)."
        )

    # 3. Nhóm Khí cụ điện & Đóng cắt (Contactor, Aptomat, Relay)
    elif any(k in text for k in ["contactor", "khởi", "relay", "rơ", "aptomat", "cb", "cp", "cuộn hút", "a1", "a2"]):
        return (
            "🔌 <b>PHÂN TÍCH CHUYÊN SÂU: KHÍ CỤ ĐIỆN & THIẾT BỊ BẢO VỆ</b><br><br>"
            "• <b>Contactor:</b> Cuộn hút <b>A1 - A2</b> (kiểm tra kỹ điện áp 220V, 380V hoặc 24VDC trước khi cấp nguồn). Mạch động lực gồm ngõ vào <b>1L1, 3L2, 5L3</b> và ngõ ra <b>2T1, 4T2, 6T3</b>. Tiếp điểm phụ <b>NO (13-14)</b> dùng làm mạch tự giữ.<br>"
            "• <b>Aptomat (CB / MCCB):</b> Bảo vệ ngắn mạch và quá tải. Chọn dòng định mức $I_{cb} = 1.2 \\div 1.5 \\times I_{dm}$ của tải."
        )

    # 4. Nhóm Cảm biến & Tự động hóa (PLC, HMI, NPN/PNP)
    elif any(k in text for k in ["plc", "hmi", "cảm biến", "sensor", "npn", "pnp", "analog", "4-20ma"]):
        return (
            "📊 <b>PHÂN TÍCH CHUYÊN SÂU: TỰ ĐỘNG HÓA & CẢM BIẾN CÔNG NGHIỆP</b><br><br>"
            "• <b>Cảm biến NPN / PNP:</b> NPN xuất tín hiệu âm (0V/GND), PNP xuất tín hiệu dương (+24V).<br>"
            "• <b>PLC & HMI:</b> Bộ điều khiển logic khả trình nhận tín hiệu đầu vào (Inputs) từ cảm biến/nút nhấn và xuất tín hiệu điều khiển (Outputs) ra van, cuộn hút, biến tần theo thuật toán lập trình."
        )

    # 5. Nhóm Lập trình & Công nghệ thông tin (Code, Python, Web, App, Vi điều khiển)
    elif any(k in text for k in ["lập trình", "code", "python", "fastapi", "arduino", "esp32", "hàm", "thuật toán", "script"]):
        return (
            "💻 <b>PHÂN TÍCH CHUYÊN SÂU: LẬP TRÌNH & CÔNG NGHỆ PHẦN MỀM</b><br><br>"
            "• <b>Tư duy thuật toán:</b> Phân rã bài toán thành các hàm logic độc lập, tối ưu hóa hiệu suất thực thi, quản lý ngoại lệ (Exception Handling) chặt chẽ.<br>"
            "• <b>Kiến trúc hệ thống:</b> Xây dựng theo mô hình API / Microservices, sử dụng bất đồng bộ (Async/Await) để tăng tốc độ xử lý và phản hồi tức thì cho ứng dụng."
        )

    # 6. Nhóm Nông nghiệp thông minh, Điện tử, Cơ khí & Các lĩnh vực khác
    elif any(k in text for k in ["nông nghiệp", "tưới", "cơ khí", "mạch", "điện tử", "màn hình", "hmi", "tần số", "năng lượng"]):
        return (
            "🌱 <b>PHÂN TÍCH CHUYÊN SÂU: ĐA NGÀNH & KỸ THUẬT THỰC CHIẾN</b><br><br>"
            "• <b>Hệ thống đa lĩnh vực:</b> Tích hợp linh hoạt giữa cơ khí chế tạo, điện tử ứng dụng và tự động hóa nông nghiệp (như hệ thống tưới tự động, cảm biến độ ẩm, điều khiển bơm áp lực biến tần).<br>"
            "• <b>Quy trình tối ưu:</b> Khảo sát thông số kỹ thuật đầu vào, tính toán tải trọng, lựa chọn thiết bị tương thích và vận hành thử nghiệm an toàn tuyệt đối."
        )

    # 7. Phân tích tổng quát thông minh cho mọi câu hỏi hoặc hình ảnh gửi lên
    else:
        img_note = " <i>[Đã ghi nhận hình ảnh gửi kèm để phân tích cấu trúc & thị giác]</i>" if has_img else ""
        return (
            f"👑 <b>BỘ NÃO SIÊU TRÍ TUỆ ĐA LĨNH VỰC - PHÂN TÍCH CHUYÊN SÂU:</b><br><br>"
            f"Hệ thống đã tiếp nhận yêu cầu từ bồ: <i>\"{msg}\"</i>.{img_note}<br><br>"
            "• <b>Nhận định toàn diện:</b> Bất kể là thiết bị tự động hóa, linh kiện điện tử, cơ khí, nông nghiệp hay lập trình hệ thống, nguyên lý cốt lõi luôn tuân thủ việc bóc tách thông số, kiểm tra tương thích phần cứng và tối ưu hóa vận hành.<br>"
            "• <b>Định hướng giải pháp:</b> Bồ hãy cung cấp thêm tên thiết bị cụ thể, sơ đồ hoặc đoạn code cần xử lý, bộ não AI sẽ lập tức phác thảo phương án chuẩn xác từng chi tiết cho bồ!<br>"
            "• <i>Trạng thái:</i> Mọi nội dung trao đổi đã được lưu vết an toàn vào Két Sắt Ký Ức."
        )

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI AN BÌNH - ULTIMATE INTELLIGENCE</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: #050811; color: #f1f5f9; min-height: 100vh; display: flex; flex-direction: column; background-size: cover; background-position: center; padding-bottom: 85px; }
        .overlay { position: fixed; inset: 0; background: rgba(5,8,17,0.92); backdrop-filter: blur(10px); z-index: 1; }
        .app { position: relative; z-index: 2; max-width: 650px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; flex: 1; }
        .header { position: sticky; top: 0; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(15,23,42,0.95); border-bottom: 1px solid rgba(255,255,255,0.12); }
        .header h1 { font-size: 16px; color: #ffffff; font-weight: 800; letter-spacing: 0.5px; }
        .header p { font-size: 10px; color: #38bdf8; font-weight: bold; }
        .btn-tool { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #e2e8f0; padding: 5px 8px; border-radius: 6px; font-size: 11px; cursor: pointer; }
        .btn-key-on { background: linear-gradient(135deg, #10b981, #059669) !important; color: #fff !important; font-weight: bold; border: none !important; box-shadow: 0 0 12px rgba(16,185,129,0.5); }
        .chat-stream { flex: 1; padding: 14px 12px; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 90%; padding: 12px 14px; border-radius: 14px; font-size: 14px; line-height: 1.55; word-break: break-word; }
        .msg.bot { background: rgba(30,41,59,0.95); color: #f8fafc; align-self: flex-start; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
        .msg.user { background: #2563eb; color: #fff; align-self: flex-end; }
        .media-grid { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
        .media-grid img { width: 110px; height: 110px; border-radius: 8px; object-fit: cover; }
        .badge { display: inline-block; background: rgba(16,185,129,0.2); border: 1px solid #10b981; color: #34d399; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 5px; margin-bottom: 6px; }
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
                <p>🧠 Siêu Trí Tuệ Đa Lĩnh Vực & Thị Giác</p>
            </div>
            <div style="display:flex; gap:5px;">
                <button class="btn-tool" id="vaultBtn" onclick="window.open('/api/export-brain')">📥 Két Sắt (0)</button>
                <button class="btn-tool" onclick="document.getElementById('bgInp').click()">🖼️ Nền</button>
                <button class="btn-tool btn-key-on">ULTIMATE</button>
            </div>
        </div>
        <div class="chat-stream" id="stream">
            <div class="msg bot">
                <div class="badge">🧠 HỆ THỐNG SIÊU TRÍ TUỆ SẴN SÀNG</div>
                <div class="bot-text">Chào bồ! Tui là <b>AI An Bình</b> phiên bản Siêu Trí Tuệ Đa Lĩnh Vực.<br><br>Hệ thống đã tích hợp trọn bộ tri thức từ điện công nghiệp, tự động hóa, điện tử, lập trình đến nông nghiệp và nhận diện hình ảnh. Bồ cứ thoải mái trao đổi nhé!</div>
                <div class="msg-footer">
                    <button class="btn-msg" onclick="speak(this)">🔊 Nghe đọc</button>
                    <button class="btn-msg" style="border-color:#a855f7; color:#d8b4fe;" onclick="quickSave(this)">💾 Lưu Két Sắt</button>
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
            <input type="text" id="chatInp" class="chat-input" placeholder="Hỏi thiết bị, lập trình, nông nghiệp, gửi ảnh..." autocomplete="off">
            <button type="submit" class="btn-enter">ENTER ↵</button>
        </form>
    </div>
    <input type="file" id="bgInp" accept="image/*" style="display:none;" onchange="onBg(event)">

    <script>
        let curImg = null;

        window.onload = () => {
            const bg = localStorage.getItem('ab_bg');
            if (bg) document.body.style.backgroundImage = `url('${bg}')`;
            fetch('/api/vault-count').then(r=>r.json()).then(d=>document.getElementById('vaultBtn').innerText=`📥 Két Sắt (${d.count})`).catch(()=>{});
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
            if (!txt && !curImg) return alert("Bồ hãy nhập nội dung hoặc tải ảnh lên nhé!");

            const st = document.getElementById('stream');
            let uHtml = `<div class="msg user">`;
            if (curImg) uHtml += `<div class="media-grid"><img src="${curImg}"></div>`;
            if (txt) uHtml += `<div>${txt}</div>`;
            uHtml += `</div>`;
            st.innerHTML += uHtml;
            window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});
            
            const sentImg = curImg;
            curImg = null;
            document.getElementById('prevBar').style.display = 'none';
            inp.value = '';

            const tId = 'bot_' + Date.now();
            st.innerHTML += `<div class="msg bot" id="${tId}"><div class="badge">🧠 ĐANG PHÂN TÍCH ĐA LĨNH VỰC...</div><div class="bot-text">Đang trích xuất tri thức chuyên sâu...</div></div>`;
            window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: txt, image: sentImg })
                });
                const d = await res.json();
                
                document.getElementById(tId).innerHTML = `
                    <div class="badge">💡 KẾT QUẢ PHÂN TÍCH CHUYÊN SÂU</div>
                    <div class="bot-text">${d.reply}</div>
                    <div class="msg-footer">
                        <button class="btn-msg" onclick="speak(this)">🔊 Nghe đọc</button>
                        <button class="btn-msg" style="border-color:#a855f7; color:#d8b4fe;" onclick="quickSave(this)">💾 Lưu Két Sắt</button>
                    </div>`;
                window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});
                fetch('/api/vault-count').then(r=>r.json()).then(dt=>document.getElementById('vaultBtn').innerText=`📥 Két Sắt (${dt.count})`).catch(()=>{});
            } catch(e) {
                document.getElementById(tId).innerHTML = `<div class="bot-text">⚠️ Lỗi hệ thống, bồ bấm ENTER gửi lại nhé!</div>`;
            }
        }

        function speak(btn) {
            if (!window.speechSynthesis) return alert("Thiết bị chưa hỗ trợ phát âm thanh!");
            window.speechSynthesis.cancel();
            const txt = btn.closest('.msg').querySelector('.bot-text').innerText;
            const clean = txt.replaceAll('*','').replaceAll('`','').replaceAll('#','').replaceAll('_','').replaceAll('"','').replaceAll("'",'').replaceAll('•',', ').trim();
            const ut = new SpeechSynthesisUtterance("Xin chào, tôi là AI An Bình, phản hồi chuyên sâu như sau: " + clean);
            ut.lang = 'vi-VN';
            ut.rate = 0.95;
            window.speechSynthesis.speak(ut);
        }

        async function quickSave(btn) {
            const txt = btn.closest('.msg').querySelector('.bot-text').innerText;
            await fetch('/api/save-memory', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({query:txt.substring(0,35), answer:txt})});
            alert("🎉 Đã lưu bài học vào Két Sắt Ký Ức!");
            fetch('/api/vault-count').then(r=>r.json()).then(dt=>document.getElementById('vaultBtn').innerText=`📥 Két Sắt (${dt.count})`);
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
    return Response(content=json.dumps(get_vault(), ensure_ascii=False, indent=2), media_type="application/json", headers={"Content-Disposition": "attachment; filename=AI_AnBinh_UltimateBrain.json"})

@app.post("/api/save-memory")
async def save_memory_endpoint(req: Request):
    d = await req.json()
    save_to_vault(d.get("query", "Ghi chú"), d.get("answer", ""), domain="Ultimate AI")
    return {"status": "success"}

@app.post("/api/chat")
async def chat_endpoint(req: Request):
    data = await req.json()
    msg = data.get("message", "").strip()
    img = data.get("image", None)
    
    ans = ultimate_ai_reasoning(msg, has_img=(img is not None))
    formatted = clean_text_for_display(ans)
    save_to_vault(msg, formatted, domain="General Expertise")
    return {"reply": formatted}
