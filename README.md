AI-Phdam
# skill-creator

Skill chuẩn mở `SKILL.md` giúp AI tự động thiết kế, cấu trúc và tạo mới các **Agent Skill** gọn sạch, dễ dùng lại.

Tương thích với các AI coding agent phổ biến như: **Claude Code, Cursor, Codex, Gemini CLI, GitHub Copilot, Antigravity...**

## Cách cài đặt

### Cách 1: Tải trực tiếp (đơn giản nhất)
1. Bấm nút xanh **Code** $\rightarrow$ **Download ZIP** và giải nén.
2. Copy thư mục `skill-creator` vào thư mục skills của AI bạn đang dùng (ví dụ: `.claude/skills/skill-creator` hoặc `.agents/skills/skill-creator`), hoặc mở AI ngay trong thư mục vừa giải nén.

### Cách 2: Dùng Git

    git clone https://github.com/<ten-tai-khoan-cua-ban>/skill-creator.git

## Cách sử dụng

Mở AI trong thư mục chứa skill này và nhắn:

> **"Dùng skill-creator trong repo này để tạo cho tao skill làm [mô tả việc bạn muốn]"**

### Ví dụ mẫu
- *"Dùng skill-creator trong repo này để tạo cho tao skill viết kịch bản video ngắn TikTok/Reels"*
- *"Dùng skill-creator trong repo này để tạo cho tao skill review code Python và tìm lỗi bảo mật"*
- *"Dùng skill-creator trong repo này để tạo cho tao skill tóm tắt tài liệu thành checklist hành động"*

## Cấu trúc repo

    skill-creator/
    ├── SKILL.md      # Hướng dẫn cốt lõi cho AI agent
    └── README.md     # Tài liệu hướng dẫn sử dụng

## License
MIT
