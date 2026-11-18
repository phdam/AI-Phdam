# AI-Phdam

Ứng dụng **AI phân tích linh kiện điện tử** (Flask, nhận diện linh kiện & đọc điện trở) kèm bộ **AI Agent Skills** chuẩn mở `SKILL.md`.

Tương thích với các AI coding agent phổ biến: **Claude Code, Cursor, Codex, Gemini CLI, GitHub Copilot, Antigravity...**

---

## Bộ Agent Skills trong repo

Repo này tích hợp sẵn 3 skill chuẩn `SKILL.md`:

| Skill | Thư mục | Công dụng |
| :--- | :--- | :--- |
| **skill-creator** | `skill-creator/SKILL.md` | Tự động thiết kế và tạo thêm các Agent Skill mới chuẩn `SKILL.md` |
| **tao-video-ai** | `tao-video-ai/SKILL.md` | Tạo trọn bộ kịch bản video ngắn (Hook, voice-over, phân cảnh, prompt ảnh/video AI) |
| **ai-phdam-helper** | `ai-phdam-helper/SKILL.md` | Kiểm tra, sửa lỗi, tối ưu UTF-8 và hỗ trợ deploy ứng dụng AI-Phdam |

---

## Cách cài đặt & sử dụng Skills

### Cách 1: Tải trực tiếp
1. Bấm nút xanh **Code** → **Download ZIP** và giải nén.
2. Copy thư mục skill bạn muốn dùng (`skill-creator`, `tao-video-ai`, hoặc `ai-phdam-helper`) vào thư mục skills của AI bạn đang dùng (ví dụ `.claude/skills/` hoặc `.agents/skills/`), hoặc mở AI trực tiếp trong thư mục repo này.

### Cách 2: Dùng Git

    git clone https://github.com/phdam/AI-Phdam.git

### Câu lệnh mẫu gọi AI chạy ngay
- Tạo skill mới: *"Dùng `skill-creator` trong repo này để tạo cho tao skill làm [việc bạn muốn]"*
- Làm kịch bản video AI: *"Dùng `tao-video-ai` làm cho tao kịch bản video ngắn về [chủ đề]"*
- Sửa lỗi & nâng cấp app: *"Dùng `ai-phdam-helper` kiểm tra lỗi và tối ưu code cho `app.py`"*

---

## Cấu trúc chính

    AI-Phdam/
    ├── app.py                   # Backend Flask chính
    ├── main.py                  # Entry point
    ├── index.html               # Giao diện web
    ├── requirements.txt         # Thư viện Python
    ├── detector/                # Module nhận diện linh kiện
    ├── utils/                   # Tiện ích (đọc vạch điện trở, xử lý ảnh)
    ├── skill-creator/
    │   └── SKILL.md
    ├── tao-video-ai/
    │   └── SKILL.md
    ├── ai-phdam-helper/
    │   └── SKILL.md
    └── README.md

## License
MIT
