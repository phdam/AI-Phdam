---
name: tao-video-ai
description: Generate complete AI short-video production packages from a topic or idea, including 3-second hooks, natural Vietnamese voice-over scripts, scene-by-scene breakdowns, and English image/video prompts. Use when the user asks to create an AI video, write a TikTok/Reels/Shorts script, or generate prompts for Veo, Sora, Kling, Runway, or Midjourney.
license: MIT
---

# Tạo Video AI

Turn any raw topic, product, or idea into a ready-to-produce short video package (TikTok, YouTube Shorts, Facebook Reels).

## Communication Rule
- Respond in the same language as the user (default to natural, spoken Vietnamese for scripts and explanations).
- Write all AI visual/video generation prompts in clear, descriptive English for maximum model quality.
- Ask at most 2 quick clarifying questions only if the topic is completely unclear; otherwise choose sensible defaults (30–45 seconds, 9:16 vertical format).

## Step 1: Lock the Video Brief
Extract or infer:
1. **Topic & core message**: What is the single takeaway?
2. **Target audience & tone**: Educational, dramatic, storytelling, review, or humorous?
3. **Format & duration**: Default `9:16` vertical, `30–45s` (`5–7` scenes).

## Step 2: Build the Production Package
Always deliver the output in these 4 structured sections:

### 1. Hook Options (3 giây đầu)
Provide 3 punchy opening lines designed to stop scrolling immediately.

### 2. Full Voice-Over Script (Lời thoại đọc)
- Write short, conversational sentences easy to read aloud or feed into TTS/ElevenLabs.
- Mark pacing cues like `[pause]`, `[nhấn giọng]` where helpful.
- Target ~110–140 Vietnamese words for a 40-second video.

### 3. Scene-by-Scene Breakdown & AI Prompts
For each scene (`Scene 1`, `Scene 2`, ...):
- **Time**: e.g., `00:00 - 00:05`
- **Voice-over line**: Exact spoken text for this scene.
- **On-screen text (Chữ trên màn hình)**: Short 3–7 word caption.
- **Image Prompt (EN)**: Subject, action, environment, lighting, camera angle, style, `vertical 9:16, photorealistic` (or chosen style).
- **Video Motion Prompt (EN)**: Camera movement + subject motion (e.g., `Slow push-in camera, subtle hair movement in wind, cinematic motion`).

### 4. Posting Kit
- **Caption**: 1–2 short engaging lines + CTA.
- **Hashtags**: 5–8 relevant hashtags.

## Rules & Guardrails
- Keep visual style consistent across all scenes (repeat key character/color/style descriptors in every prompt).
- Avoid cluttered scenes; each scene should focus on 1 clear visual action.
- Never include copyrighted brand names or restricted real-person likenesses in generation prompts unless explicitly requested for editorial context.
