# Đặc Tả Use Case: UC03 — Nhập Chỉ Số Công Tơ Định Kỳ

- **Mã Use Case**: `UC03`
- **Tên Use Case**: Nhập chỉ số công tơ định kỳ & Tự động phát hành Hóa đơn
- **Tác nhân (Actor)**: Chủ hộ (`USER` / `OWNER`)
- **Mục tiêu**: Ghi nhận chỉ số mới cho công tơ điện/nước trong kỳ, tự động tính lượng tiêu thụ và phát hành hóa đơn theo biểu giá bậc thang.
- **Bằng chứng Code**: `frontend/components/application.tsx:133-136`, `backend/app/services.py:161-210`, `backend/app/billing_service.py:54-68`, `backend/app/main.py:133-136`
- **Trạng thái**: Implemented (As-Is)

## Luồng Chính (Main Success Scenario)
1. Người dùng chọn công tơ (Điện hoặc Nước) tại trang "Nhập chỉ số".
2. Hệ thống hiển thị kỳ hiện tại, ngày đọc chỉ số trước và chỉ số cũ (`previous_reading`).
3. Người dùng nhập chỉ số mới (`current_reading`) và ngày ghi chỉ số (`reading_date`).
4. Bấm "Lưu chỉ số".
5. Backend tiếp nhận request `POST /api/readings`:
   - Kiểm tra `current_reading >= previous_reading`.
   - Tính lượng tiêu thụ `consumption = current_reading - previous_reading`.
   - Lưu `MeterReading`.
   - Gọi `BillingService.tariff()` tìm biểu giá (`Tariff` & `TariffTier`) phù hợp theo loại tiện ích, nhà cung cấp và địa phương.
   - Tính số tiền từng bậc và tổng tiền `estimated_amount`.
   - Sinh `Bill` với snapshot vĩnh viễn của biểu giá và chi tiết từng bậc.
6. Hệ thống trả về `201 Created` kèm thông tin Hóa đơn mới phát hành.

## Các Luồng Lỗi (Error Flows)
- **Err 1 (Chỉ số mới nhỏ hơn chỉ số cũ)**: Backend từ chối `CheckConstraint` hoặc DomainError `400 Bad Request` ("Chỉ số mới không được nhỏ hơn chỉ số cũ").
- **Err 2 (Kỳ đã có hóa đơn)**: Đã nhập chỉ số cho kỳ này -> Backend trả về `409 Conflict` ("Tài khoản đã có hóa đơn trong kỳ này").
