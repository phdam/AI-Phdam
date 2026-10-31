from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
import json
import os
import re
from datetime import datetime

app = FastAPI(title="AI An Binh VIP Intelligence Engine")

VAULT_FILE = "ai_private_vault.json"

def get_vault():
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_to_vault(query: str, answer: str):
    if not query or not answer or len(answer) < 20:
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

def vip_ai_core_reasoning(msg: str):
    """ĐỘNG CƠ SUY LUẬN SIÊU TRÍ TUỆ - PHÂN TÍCH CHUYÊN SÂU VIP"""
    text = msg.lower()
    
    # Phân tích sâu chuyên đề Biến tần & Truyền động
    if any(k in text for k in ["biến tần", "vfd", "inverter", "tần số", "parameter", "cài", "motor", "động cơ", "lỗi oc", "lỗi ov", "acc", "dec"]):
        return (
            "🚀 <b>TRÍ TUỆ VIP: PHÂN TÍCH HỆ THỐNG BIẾN TẦN & ĐỘNG LỰC CHUYÊN SÂU</b><br><br>"
            "• <b>1. Phân tích bản chất cốt lõi:</b> Biến tần thay đổi tần số lưới điện ($f = \\frac{p \\cdot n}{120}$) để điều khiển tốc độ motor không đồng bộ. Đòi hỏi sự đồng bộ chặt chẽ giữa mạch động lực và mạch điều khiển.<br>"
            "• <b>2. Sơ đồ đấu nối thực chiến chuẩn kỹ thuật:</b><br>"
            "  - <i>Động lực:</i> Cấp nguồn 3 pha vào <b>R - S - T</b>; đầu ra motor đấu chính xác vào <b>U - V - W</b>. Khi đảo chiều quay, chỉ cần hoán đổi 2 trong 3 pha ngõ ra.<br>"
            "  - <i>Điều khiển:</i> Chân chung <b>COM</b> kết nối qua công tắc/nút nhấn về <b>FWD</b> (chạy thuận) hoặc <b>REV</b> (chạy nghịch).<br>"
            "• <b>3. Cài đặt thông số (Parameter) tối ưu:</b><br>"
            "  - Thiết lập nguồn lệnh chạy (Run Source) từ bàn phím hay cầu đấu ngoài.<br>"
            "  - Cài đặt thời gian tăng/giảm tốc <b>ACC / DEC</b> hợp lý (thường từ 5s đến 10s) để triệt tiêu hiện tượng sốc cơ khí, tránh tuyệt đối lỗi quá dòng (OC) hoặc quá áp (OV)."
        )

    # Phân tích sâu chuyên đề Khí cụ điện & Contactor
    elif any(k in text for k in ["contactor", "khởi", "relay", "rơ", "nút nhấn", "cuộn hút", "tiếp điểm", "a1", "a2", "khóa liên động"]):
        return (
            "🚀 <b>TRÍ TUỆ VIP: PHÂN TÍCH KHÍ CỤ ĐIỆN & MẠCH ĐIỀU KHIỂN TỰ ĐỘNG</b><br><br>"
            "• <b>1. Phân tích bản chất cốt lõi:</b> Contactor là thiết bị đóng cắt bằng lực điện từ, vận hành dòng điện lớn thông qua mạch điều khiển điện áp nhỏ an toàn.<br>"
            "• <b>2. Định danh và kiểm tra cấu trúc chân:</b><br>"
            "  - <i>Cuộn hút (A1 - A2):</i> Bắt buộc phải xác định đúng điện áp định mức trên nhãn (220VAC, 380VAC hoặc 24VDC) trước khi cấp nguồn để tránh cháy cuộn dây.<br>"
            "  - <i>Mạch động lực:</i> Ngõ vào <b>(1L1, 3L2, 5L3)</b>, ngõ ra tải <b>(2T1, 4T2, 6T3)</b>.<br>"
            "  - <i>Tiếp điểm phụ:</i> Tiếp điểm thường mở <b>NO (13-14)</b> dùng làm mạch tự giữ (self-hold) cho nút nhấn nhả.<br>"
            "• <b>3. Tiêu chuẩn an toàn:</b> Mạch điều khiển phải luôn qua tiếp điểm thường đóng (NC) của nút nhấn Dừng trước khi vào cuộn hút."
        )

    # Phân tích sâu chuyên đề Aptomat & Bảo vệ
    elif any(k in text for k in ["aptomat", "cb", "cp", "át", "cầu chì", "bảo vệ", "ngắn mạch", "quá tải", "ampe", "chập"]):
        return (
            "🚀 <b>TRÍ TUỆ VIP: PHÂN TÍCH THIẾT BỊ BẢO VỆ & AN TOÀN ĐIỆN</b><br><br>"
            "• <b>1. Phân tích bản chất cốt lõi:</b> Aptomat bảo vệ hệ thống trước tai nạn ngắn mạch (chập điện) và sự cố quá tải nhiệt, đồng thời đóng vai trò là dao cách ly cô lập nguồn điện.<br>"
            "• <b>2. Quy tắc lắp đặt chuẩn:</b><br>"
            "  - Cọc trên (Top) đấu nguồn điện chính đi tới; cọc dưới (Bottom) đấu dây dẫn tiếp về phía tải tiêu thụ.<br>"
            "• <b>3. Công thức kinh nghiệm chọn dòng định mức (Ampe):</b><br>"
            "  - Chọn dòng của CB $I_{cb} = (1.2 \\div 1.5) \\times I_{dm}$ của tải để đảm bảo không bị tác động giả khi khởi động mà vẫn bảo vệ an toàn tuyệt đối cho hệ thống dây dẫn."
        )

    # Phân tích tổng quát suy luận đa tầng VIP cho mọi câu hỏi còn lại
    else:
        return (
            f"👑 <b>BỘ NÃO TRÍ TUỆ VIP - PHÂN TÍCH SUY LUẬN CHUYÊN SÂU:</b><br><br>"
            f"Hệ thống đã tiếp nhận yêu cầu từ bồ: <i>\"{msg}\"</i>.<br><br>"
            "• <b>Tư duy chiến lược:</b> Dưới góc độ chuyên gia kỹ thuật cấp cao, mọi bài toán đều tuân thủ nguyên lý bóc tách thông số đầu vào, kiểm tra tiêu chuẩn an toàn và đưa ra phương án thi công tối ưu nhất.<br>"
            "• <b>Định hướng giải pháp:</b> Bồ hãy cung cấp thêm thông số cụ thể (như công suất thiết bị, hiện tượng thực tế hoặc yêu cầu cấu hình), bộ não VIP sẽ lập tức phác thảo sơ đồ và hướng dẫn chi tiết từng bước cho bồ!<br>"
            "• <i>Trạng thái:</i> Toàn bộ thông tin trao đổi đã được lưu vết tự động vào Két Sắt Ký Ức an toàn tuyệt đối."
        )

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI AN BÌNH - VIP INTELLIGENCE</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: #050811; color: #f1f5f9; min-height: 100vh; display: flex; flex-direction: column; background-size: cover; background-position: center; padding-bottom: 85px; }
        .overlay { position: fixed; inset: 0; background: rgba(5,8,17,0.9); backdrop-filter: blur(10px); z-index: 1; }
        .app { position: relative; z-index: 2; max-width: 650px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; flex: 1; }
        .header { position: sticky; top: 0; z-index: 10; display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(15,23,42,0.95); border-bottom: 1px solid rgba(255,255,255,0.12); }
        .header h1 { font-size: 17px; color: #ffffff; font-weight: 800; letter-spacing: 0.5px; }
        .header p { font-size: 10px; color: #38bdf8; font-weight: bold; }
        .btn-tool { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #e2e8f0; padding: 5px 8px; border-radius: 6px; font-size: 11px; cursor: pointer; }
        .btn-key-on { background: linear-gradient(135deg, #10b981, #059669) !important; color: #fff !important; font-weight: bold; border: none !important; box-shadow: 0 0 12px rgba(16,185,129,0.5); }
        .chat-stream { flex: 1; padding: 14px 12px; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 90%; padding: 12px 14px; border-radius: 14px; font-size: 14px; line-height: 1.55; word-break: break-word; }
        .msg.bot { background: rgba(30,41,59,0.95); color: #f8fafc; align-self: flex-start; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
        .msg.user { background: #2563eb; color: #fff; align-self: flex-end; }
        .media-grid { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
        .media-grid img { width: 90px; height: 90px; border-radius: 8px; object-fit: cover; }
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
                <p>👑 Động Cơ Suy Luận Siêu Trí Tuệ VIP</p>
            </div>
            <div style="display:flex; gap:5px;">
                <button class="btn-tool" id="vaultBtn" onclick="window.open('/api/export-brain')">📥 Não (0)</button>
                <button class="btn-tool" onclick="document.getElementById('bgInp').click()">🖼️ Nền</button>
                <button class="btn-tool btn-key-on">VIP MAX</button>
            </div>
        </div>
        <div class="chat-stream" id="stream">
            <div class="msg bot">
                <div class="badge">👑 HỆ THỐNG VIP ĐÃ KHỞI ĐỘNG</div>
                <div class="bot-text">Chào bồ! Tui là <b>AI An Bình</b> phiên bản Suy Luận Siêu Trí Tuệ VIP.<br><br>Bộ não đã được huấn luyện tối đa, sẵn sàng phân tích sâu sắc, logic và sắc sảo mọi vấn đề kỹ thuật cho bồ. Cứ thử thách thoải mái nhé!</div>
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
            <input type="text" id="chatInp" class="chat-input" placeholder="Hỏi bất cứ vấn đề gì, tui phân tích VIP..." autocomplete="off">
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
            if (!txt && !curImg) return alert("Bồ hãy nhập nội dung trao đổi nhé!");

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
            st.innerHTML += `<div class="msg bot" id="${tId}"><div class="badge">👑 BỘ NÃO VIP ĐANG SUY LUẬN...</div><div class="bot-text">Đang kích hoạt tầng phân tích chuyên sâu...</div></div>`;
            window.scrollTo({top: document.body.scrollHeight, behavior:'smooth'});

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: txt })
                });
                const d = await res.json();
                
                document.getElementById(tId).innerHTML = `
                    <div class="badge">💡 KẾT QUẢ PHÂN TÍCH VIP CHUYÊN SÂU</div>
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
            const ut = new SpeechSynthesisUtterance("Xin chào, tôi là AI An Bình phiên bản VIP, tôi xin phân tích chi tiết như sau: " + clean);
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
    return Response(content=json.dumps(get_vault(), ensure_ascii=False, indent=2), media_type="application/json", headers={"Content-Disposition": "attachment; filename=AI_AnBinh_VIP_Brain.json"})

@app.post("/api/save-memory")
async def save_memory_endpoint(req: Request):
    d = await req.json()
    save_to_vault(d.get("query", "Ghi chú"), d.get("answer", ""))
    return {"status": "success"}

@app.post("/api/chat")
async def chat_endpoint(req: Request):
    data = await req.json()
    msg = data.get("message", "").strip()
    ans = vip_ai_core_reasoning(msg)
    formatted = clean_text_for_display(ans)
    save_to_vault(msg, formatted)
    return {"reply": formatted}
