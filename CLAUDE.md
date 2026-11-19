# CLAUDE.md — Quy tắc cho AI coding agent

## Ngôn ngữ & Trình bày
- AI luôn trả lời tiếng Việt.
- Trình bày gọn, súc tích, dễ đọc trên màn hình điện thoại (định dạng danh sách, không dài dòng phiến man).
- Dùng bullet points và tab để tổ chức thông tin.

## Tự động chọn skill
Khi nhận yêu cầu người dùng, AI phải tự động chọn skill phù hợp theo bảng match sau và ghi rõ skill đang dùng ở câu đầu:

| Yêu cầu của người dùng | Skill chọn |
| :--- | :--- |
| *"Tạo skill mới"*, *"Dựng skill"* | `skill-creator` |
| *"Làm kịch bản video"*, *"Video AI"*, *"Veo/Kling/Sora"* | `tao-video-ai` |
| *"Sửa lỗi app"*, *"Tối ưu"*, *"Deploy"*, *"UTF-8"* | `ai-phdam-helper` |

Nếu yêu cầu lẫn nhộn nhịp hoặc trùng lẫn, AI chọn skill chính xác nhất dựa trên từ khóa cốt lõi và ghi chú lý do chọn skill đó.

**Ví dụ đầu ra:**
> Sử dụng skill `tao-video-ai` theo yêu cầu tạo kịch bản video giới thiệu AI-Phdam.

**Quy tắc cấm:**
- **Tuyệt đối không tự ý sửa file `app.py`, `detector/`, `utils/` khi chưa được yêu cầu rõ ràng.**
- Không sửa `requirements.txt`, `index.html`, `Index.html` trừ khi người dùng đặt câu hỏi cụ thể về file đó.
- Khi cần sửa code app, luôn đọc file trước (Bước 1 của `ai-phdam-helper`) và báo nguyên nhân trước khi sửa.

## Cách gọi skill
Người dùng nên dùng cú pháp:
> *"Dùng `skill-creator` trong repo này để tạo skill [tên việc]"

hoặc

> *"Dùng `tao-video-ai` làm cho tao kịch bản video ngắn về [chủ đề]"*

hoặc

> *"Dùng `ai-phdam-helper` kiểm tra lỗi và tối ưu code cho `app.py`"*

AI sẽ tự động load skill tương ứng và báo tên skill ở đầu câu trả lời.

## Quy trình chung
1. Đọc yêu cầu → tự động match skill → báo skill đang dùng.
2. Skill thực nhiệm thực hiện task.
3. Kết quả: nếu tạo file/code → đưa ra file path + nội dung sẵn sàng copy-paste; nếu tạo script → đưa ra nội dung script + hướng dẫn chạy.