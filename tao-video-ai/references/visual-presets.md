# Visual Presets — Góc quay, Ánh sáng, Phong cách (Veo / Kling / Sora)

Tài liệu tham chiếu nội bộ cho skill `tao-video-ai`. Dùng cho tất cả prompt ảnh/video AI generation.

## Preset 1: Cinematic Tech Hook (Mặc định)

- **Góc quay (camera angle):** `Low angle shot` — ngang tầm mắt kỹ thuật viên, tăng cảm hứng "pro".
- **Ánh sáng (lighting):** `Cinematic Rembrandt lighting`, chiếu từ góc 45° trái, có rim light.
- **Phong cách:** `Photorealistic, 35mm film grain, shallow depth of field, warm key light + cool rim light`.
- **Motion:** `Slow push-in camera, subtle subject drift`.

## Preset 2: Macro Electronics Macro

- **Góc quay:** `Macro close-up, 100mm macro lens`.
- **Ánh sáng:** `Diffused softbox lighting, no harsh shadows, high detail texture`.
- **Phong cách:** `Extreme detail, photorealistic, f/2.8 shallow DOF`.
- **Motion:** `Slow focus rack / push-in`.

## Preset 3: Product UI / App Demo

- **Góc quay:** `Over-the-shoulder shot looking at smartphone screen + front flat-lay`.
- **Ánh sáng:** `Clean studio lighting, softbox + subtle rim light, white/neutral background`.
- **Phong cách:** `Clean product render, modern UI, neon accent (blue/purple) on dark background`.
- **Motion:** `UI elements animate in, smooth push-in on screen`.

## Preset 4: Workshop / Maker Scene

- **Góc quay:** `Medium shot, eye-level, slightly wide framing`.
- **Ánh sáng:** `Warm tungsten practical + soft ambient fill, moody`.
- **Phong cách:** `Cinematic, warm tones, filmic contrast, subtle grain`.
- **Motion:** `Slow dolly in / handheld feel`.

## Cách dùng preset

- Khi tạo prompt cho cả 3 nền tảng (Veo, Kling, Sora), **luôn thêm** vào cuối mỗi prompt:
  `style: <presets theo scene>, vertical 9:16, photorealistic`
- Veo: thêm `cinematic motion, 24fps feel`.
- Kling: thêm `character consistency, motion smoothness`.
- Sora: thêm `wide shot, high detail`.

## Quy tắc giữ consistency

- **Luôn lặp lại key descriptor** (chủng loại linh kiện, màu sắc accent, style) trong mỗi prompt.
- **Mỗi scene 1 chủ đề rõ ràng**, không scene nào chồng chéo nhiều hành động.
- Tránh cluttered scenes; mỗi scene tập trung 1 visual action duy nhất.

## Lưu ý
- File này là tài liệu tham chiếu nội bộ của skill — dùng khi cần prompt chi tiết, không đưa toàn bộ nội dung ra câu trả lời trừ khi người dùng yêu cầu.
