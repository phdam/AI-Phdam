---
name: skill-creator
description: Create, validate, and evolve AI Agent Skills following agentskills.io with self-learning memory. Use when creating or auditing a SKILL.md. Do NOT use for one-off coding or casual chat.
license: MIT
compatibility: Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot
metadata:
  author: phdam
  version: "2.0.0"
---

# Skill Creator (Self-Learning)

- Reply in the user's language; ask max 2 questions only if critical info is missing.

## Step 0: Load Memory
Read [references/lessons-learned.md](references/lessons-learned.md) first so past mistakes are never repeated.

## Step 1: Author Skill
Follow [references/spec-checklist.md](references/spec-checklist.md):
- Use `kebab-case` (`<= 64` chars) matching folder name; `description <= 1024` chars with negative triggers.
- Keep `SKILL.md < 500` lines; offload details to `references/` or `scripts/`. Never hardcode secrets.

## Step 2: Validate & Self-Learn
1. Run `python3 scripts/validate_skill.py <skill-dir>` and check [references/evals.json](references/evals.json).
2. After corrections or errors, add 1 concise rule to [references/lessons-learned.md](references/lessons-learned.md).
