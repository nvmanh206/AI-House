# Đặc Tả Use Case: UC10 — Admin Quản Lý Biểu Giá Điện Nước

- **Mã Use Case**: `UC10`
- **Tên Use Case**: Admin Tạo Phiên Bản Biểu Giá Mới (Tariff & TariffTier)
- **Tác nhân (Actor)**: Quản trị viên (`ADMIN`)
- **Mục tiêu**: Thiết lập biểu giá bậc thang mới cho hệ thống khi EVN hoặc công ty cấp nước thay đổi đơn giá.
- **Bằng chứng Code**: `backend/app/admin_service.py:41-55`, `backend/app/models.py:108-130`, `backend/app/main.py:176-177`
- **Trạng thái**: Implemented (As-Is)

## Luồng Chính
1. Admin truy cập trang Quản trị hệ thống (`/admin/tariffs`).
2. Chọn "Thêm biểu giá mới", chọn Loại tiện ích (`ELECTRICITY` / `WATER`), Tên nhà cung cấp (ví dụ: `EVN`), Tên biểu giá, Phiên bản (`version`), Loại nhóm khách hàng (`tariff_category`), Tỉnh/thành (nếu có) và Ngày hiệu lực (`effective_from`).
3. Khai báo danh sách các bậc giá (`TariffTier`): `from_value`, `to_value` (bậc cuối là `null`), đơn giá `unit_price`, chỉ số thứ tự `order_index`.
4. Bấm "Lưu biểu giá".
5. Backend kiểm tra quyền Admin (`admin()` decorator):
   - Xác thực các bậc liên tục từ 0 đến vô hạn.
   - Lưu `Tariff` và các `TariffTier` tương ứng.
   - Vô hiệu hóa biểu giá cũ nếu cần.
6. Hệ thống trả về `201 Created` và ghi nhận lịch sử vào `AuditLog`.
