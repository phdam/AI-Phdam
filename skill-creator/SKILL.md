---
name: skill-creator
description: Create, structure, and refine reusable AI Agent Skills following the open SKILL.md standard. Use when the user asks to create a new skill, turn a repeated task or workflow into a skill, or audit and improve an existing SKILL.md file.
license: MIT
---

# Skill Creator

Create clean, reliable, and portable Agent Skills that follow the open `SKILL.md` specification.

## Communication Rule
- Always communicate with the user in the same language they used (e.g., reply in Vietnamese if the user prompts in Vietnamese).
- Keep questions minimal. Only ask clarifying questions if critical information is missing; otherwise make sensible defaults and explain them briefly.

## Step 1: Clarify the Skill Goal
Identify from the user's request:
1. **Core task**: What specific job should the new skill perform?
2. **Trigger scenarios**: When should an AI agent load and use this skill?
3. **Inputs & outputs**: What does the user provide, and what format/result should the agent produce?
4. **Dependencies (if any)**: Does it need scripts (Python/Bash), templates, or reference docs?

## Step 2: Design the Directory Structure
Choose a `kebab-case` name (lowercase letters, numbers, hyphens only; max 64 characters; must match the folder name):

    <skill-name>/
    ├── SKILL.md          # Required: YAML frontmatter + core instructions
    ├── scripts/          # Optional: deterministic executable scripts
    ├── references/       # Optional: detailed docs loaded only when needed
    └── assets/           # Optional: templates, schemas, or static files

Rules:
- Keep `SKILL.md` concise and actionable (ideally under 500 lines).
- Use **progressive disclosure**: put high-level steps in `SKILL.md`, and move long schemas, examples, or checklists into `references/` or `assets/` if needed.
- Do not add unnecessary files or a `README.md` inside the skill folder itself unless the repo root needs one for GitHub visitors.

## Step 3: Write `SKILL.md`
Use this structure:

1. **YAML Frontmatter** (required):
   - `name`: Must match the folder name (`kebab-case`).
   - `description`: Max 1024 characters. Clearly state **what the skill does** AND **when to use it** (include concrete trigger keywords/phrases).
   - `license`: Optional (e.g., `MIT`).

2. **Markdown Body**:
   - **Overview**: 1–2 sentences on the purpose.
   - **Workflow / Step-by-Step Instructions**: Numbered, unambiguous steps the AI must follow.
   - **Rules & Constraints**: Guardrails to prevent common mistakes.
   - **Output Format / Examples**: Concrete template or example of expected output.

## Step 4: Self-Check Before Delivering
Verify the generated skill against this checklist:
- [ ] Folder name and `name` field are identical and valid `kebab-case` (`<= 64` chars).
- [ ] `description` is `<= 1024` chars and clearly states both *what* and *when*.
- [ ] Instructions are specific and actionable (not vague advice).
- [ ] No hardcoded secrets, API keys, or machine-specific local paths.
- [ ] If the user's workspace allows writing files, create the folder and files directly; otherwise output the complete file tree and full file contents ready to copy.

**Nhắc kiểm tra checklist:** Sau khi tạo xong skill mới, AI luôn nhắc lại checklist trên và gợi ý xem xét các mục chưa check xong.

**Gợi ý cập nhật README.md:** Sau khi tạo skill mới, AI gợi ý người dùng cập nhật bảng skill trong `README.md` theo mẫu:
```
| **Tên skill mới** | `skill-moi/` | Công dụng |
```
Trước khi cập nhật, hỏi 1 câu ngắn: *"Cập nhật bảng skill trong README.md?"* Nếu đồng ý, hãy chỉnh bảng ở root `README.md`.
