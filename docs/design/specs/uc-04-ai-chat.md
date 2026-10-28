# Đặc Tả Use Case: UC07 — Tra Cứu & Hỏi Đáp Với Trợ Lý AI

- **Mã Use Case**: `UC07`
- **Tên Use Case**: Hỏi đáp Trợ lý AI ("Nhà Mình Assistant") & Tra cứu biểu giá công cộng
- **Tác nhân (Actor)**: Chủ hộ (`USER`), Thành viên (`MEMBER`), External (`Gemini API`)
- **Mục tiêu**: Trả lời thắc mắc chi tiêu, dự báo hóa đơn kỳ tới, cảnh báo tiêu thụ bất thường và tra cứu biểu giá điện/nước sinh hoạt công cộng.
- **Bằng chứng Code**: `backend/app/main.py:158-169`, `backend/app/ai/agent.py:65-167`, `backend/app/ai/gemini.py:70-194`
- **Trạng thái**: Implemented (As-Is)

## Luồng Chính
1. Người dùng mở trang "Trợ lý AI" và nhập câu hỏi (ví dụ: "Tháng tới tiền điện khoảng bao nhiêu?" hoặc "Giá điện Thái Nguyên hiện nay là bao nhiêu?").
2. Frontend gửi `POST /api/ai/chat` kèm nội dung câu hỏi.
3. Backend xây dựng `AgentContext` đóng băng từ JWT session (gồm `user_id`, `household_id`, `permissions`).
4. Intent Router (`route()`) xác định intent của tin nhắn (ví dụ: `BILL_FORECAST`, `PUBLIC_TARIFF`, `GENERAL_CHAT`).
5. Nếu intent là `PUBLIC_TARIFF`:
   - Chuẩn hóa câu hỏi công cộng (không kèm thông tin gia đình).
   - Gọi `GeminiProvider.search_tariff()` qua REST API tới Google AI Studio kèm Google Search tool.
   - Trả về câu trả lời kèm danh sách nguồn trích dẫn web `[1], [2]`.
6. Nếu intent liên quan đến dữ liệu gia đình (`BILL_FORECAST`, `CONSUMPTION_ANALYSIS`...):
   - Gọi các Tool được cấp phép (`Allowlisted Tools`) đọc dữ liệu tiêu thụ.
   - Tính toán deterministic (Forecast WMA, Anomaly percentage).
   - Ghép kết quả vào câu trả lời mẫu grounding an toàn.
7. Ghi nhận thông tin gọi AI vào bảng `AIAnalysis` và trả về kết quả cho Frontend.
