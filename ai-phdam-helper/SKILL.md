---
name: ai-phdam-helper
description: Inspect, debug, improve, and prepare deployment updates for the AI-Phdam electronic component analyzer web app (Flask, app.py, main.py, detector/, utils/resistor_reader.py, index.html). Use when the user asks to fix bugs, improve component or resistor detection, update the web UI, check UTF-8 rendering, or deploy AI-Phdam.
license: MIT
---

# AI-Phdam Helper

Safely inspect, debug, and upgrade the `AI-Phdam` electronic component analyzer application without breaking existing Flask endpoints, detection logic, or deployment setup.

## Communication Rule
- Communicate in the user's language (Vietnamese if prompted in Vietnamese).
- Explain the root cause clearly in plain language before or alongside proposing code edits.

## Step 1: Inspect Relevant Files First
Before editing any code, read the actual files in the workspace to confirm exact function names, routes, and imports:
- Backend entry points: `app.py`, `main.py`
- Detection & analysis modules: `detector/` (e.g., component detector), `utils/` (e.g., `resistor_reader.py`)
- Frontend & deployment files: `index.html` (also check `Index.html` for duplicate/case-sensitivity conflicts), `requirements.txt`

## Step 2: Mandatory Quality & Deployment Checks
Whenever modifying `AI-Phdam`, always verify:
1. **UTF-8 & Vietnamese rendering**: Ensure file I/O (`encoding="utf-8"`), JSON responses (`ensure_ascii=False` or proper UTF-8 headers), and HTML `<meta charset="UTF-8">` render Vietnamese component labels cleanly without mojibake.
2. **Linux case-sensitivity**: Check exact filename casing (for example `index.html` vs `Index.html`) so cloud deployment (Render/Linux) never fails with 404 or `FileNotFoundError`.
3. **Flask & dependency parity**: Keep `requirements.txt` synchronized with every imported package (Flask, Gunicorn, image/CV libraries, etc.) and avoid mixing unused FastAPI/Uvicorn leftovers unless intentionally needed.
4. **Electronics domain accuracy**: When updating resistor color-band reading or component analysis, verify edge cases (lighting/noise, 4-band vs 5-band resistors, tolerance bands, clear error messages when detection confidence is low).
5. **No hardcoded secrets or local paths**: Use environment variables (`os.getenv`) and relative paths (`pathlib.Path`).

## Step 3: Deliver Clean, Safe Updates
- Make minimal, targeted edits instead of rewriting working modules unnecessarily.
- When the user works from mobile or copies code manually, state the exact file path and provide complete, ready-to-paste updated sections or files.
- End with brief verification steps (how to run locally with Flask and which UI flow or endpoint to test).
