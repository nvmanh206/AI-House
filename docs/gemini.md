# Gemini + Google Search

## Bật trên máy local

Trong `backend/.env`:

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEY=YOUR_KEY_HERE
GEMINI_MODEL=gemini-3.6-flash
GEMINI_SEARCH_ENABLED=true
```

Điền API key trực tiếp trong file, không gửi key vào chat, không dùng NEXT_PUBLIC cho key. Giữ nguyên DATABASE_URL và JWT_SECRET. Khởi động lại backend để nhận cấu hình:

```powershell
cd F:\Web\AI_Household_Utility_Billing\website\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Nếu backend đang chạy thì Ctrl+C trong terminal đó trước. Không cần seed/migration hay thư viện mới. Mở `/assistant`, hỏi “Giá điện hiện nay là bao nhiêu?”. Có thể đổi GEMINI_MODEL sang model hỗ trợ Search mà project Google của bạn được phép dùng.

Nếu chạy Docker Compose: đặt cùng bốn biến trong `website/.env` (Compose đọc file root này), rồi recreate backend bằng `docker compose up -d --build backend`. Không commit file chứa key.

## Phạm vi đã tích hợp

- Nhận diện câu hỏi biểu giá điện/nước, không đòi chỉ số/hóa đơn mới tra cứu.
- Gemini REST `generateContent` với tool `google_search`. Chỉ gửi câu hỏi công khai chuẩn hóa và ngày hiện tại; không gửi nguyên chat, địa chỉ, mã khách hàng, token hay dữ liệu household.
- Nguồn trả về theo groundingMetadata, đánh số trong câu trả lời và link clickable. Google Search suggestions hiển thị trong iframe sandbox, không chạy script trong trang ứng dụng.
- Thiếu nguồn, response bị cắt hoặc bị chặn: báo chưa xác minh thay vì trả giá như đã kiểm chứng.
- Ưu tiên nguồn chính thức qua prompt; đây không phải domain allowlist hoặc chứng nhận mọi kết quả luôn chính xác. Người dùng cần xem nguồn/ngày hiệu lực.
- Giá online chỉ tham khảo; không ghi tariff/bill. Nước phụ thuộc địa phương, truy vấn hiện chưa gửi vị trí của hộ.
- Các câu hỏi nội bộ vẫn dùng local deterministic services. Chưa chuyển toàn bộ chatbot thành hội thoại tự do Gemini, chưa semantic intent routing.
- Thiếu key/quyền/model, timeout/quota đều có error riêng, không echo lỗi thô hoặc API key.

Google Search grounding có thể tính phí theo model/hạn mức của Google. Tham khảo [tài liệu Google chính thức](https://ai.google.dev/gemini-api/docs/generate-content/google-search).

## Kiểm chứng

Tests dùng response Gemini mô phỏng, kiểm tra payload, nguồn, thiếu key, HTTP lỗi, privacy và regression. Chưa xác nhận request Gemini thật khi chưa có API key hợp lệ. Không yêu cầu hoặc thu thập key qua chat.
