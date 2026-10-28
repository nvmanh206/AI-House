# Đặc Tả Use Case: UC05 — Thanh Toán Hóa Đơn (Manual Payment)

- **Mã Use Case**: `UC05`
- **Tên Use Case**: Thanh toán Hóa đơn Thủ công (Idempotent Payment)
- **Tác nhân (Actor)**: Chủ hộ (`USER` / `OWNER`)
- **Mục tiêu**: Ghi nhận thanh toán thủ công cho hóa đơn chưa trả, chuyển trạng thái bill sang `PAID`.
- **Bằng chứng Code**: `backend/app/services.py:211-230`, `backend/app/models.py:149-157`, `backend/app/main.py:141-144`
- **Trạng thái**: Implemented (As-Is)

## Luồng Chính
1. Người dùng mở trang "Hóa đơn", xem danh sách các hóa đơn chưa thanh toán (`UNPAID` / `OVERDUE`).
2. Chọn hóa đơn cần thanh toán và chọn "Ghi nhận đã thanh toán".
3. Nhập mã tham chiếu (nếu có, ví dụ: Mã chuyển khoản ngân hàng) và chọn Phương thức `MANUAL`.
4. Frontend gửi request `POST /api/payments` kèm `bill_id`, `amount`, `method`, `reference`.
5. Backend khởi tạo transaction:
   - Khóa bản ghi `Bill` với `lock=True`.
   - Kiểm tra bill trạng thái khác `PAID`.
   - Tạo bản ghi `Payment` với `bill_id`.
   - Cập nhật `Bill.status = 'PAID'` và `Bill.paid_at = now()`.
6. Hệ thống trả về `200 OK` kèm thông tin thanh toán.

## Lỗi / Trường hợp Đặc biệt
- **Err 1 (Idempotent Duplicate Payment)**: Hóa đơn đã được thanh toán trước đó -> CSDL báo lỗi UNIQUE `bill_id` hoặc Backend trả về `409 Conflict` ("Hóa đơn đã được thanh toán").
