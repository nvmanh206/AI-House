# Đặc Tả Use Case: UC02 — Thiết Lập Hộ Gia Đình (Onboarding Wizard)

- **Mã Use Case**: `UC02`
- **Tên Use Case**: Thiết lập Hộ gia đình (Onboarding Wizard 4 bước)
- **Tác nhân (Actor)**: Chủ hộ (`USER`)
- **Mục tiêu**: Tạo không gian hộ gia đình mới, cấu hình các tài khoản tiện ích Điện/Nước, thiết lập chu kỳ chốt chỉ số và công tơ ban đầu.
- **Bằng chứng Code**: `frontend/components/application.tsx:620-625`, `backend/app/services.py:68-124`, `backend/app/main.py:104-105`
- **Trạng thái**: Implemented (As-Is)

## Luồng Chính (Main Success Scenario)
1. Người dùng mới đăng ký/đăng nhập mở trang Onboarding (Bước 1/4).
2. Người dùng nhập tên Hộ gia đình, địa chỉ và số thành viên.
3. Người dùng chuyển sang Bước 2/4: Nhập nhà cung cấp điện, loại biểu giá (1 pha/3 pha/kinh doanh), tỉnh/thành phố, mã khách hàng, ngày chốt chỉ số, ngày thanh toán dự kiến và chỉ số điện ban đầu.
4. Người dùng chuyển sang Bước 3/4: Nhập cấu hình tương tự cho tài khoản Nước (hoặc chọn Bỏ qua nước).
5. Bước 4/4: Người dùng xem màn hình xác nhận thông tin tổng quan và bấm "Vào dashboard".
6. Frontend gửi yêu cầu `POST /api/households` kèm toàn bộ payload.
7. Backend khởi tạo trong 1 Database Transaction: `Household`, `HouseholdMember` (vai trò OWNER), các `UtilityAccount` (Điện/Nước) và các `Meter` ban đầu.
8. Hệ thống trả về `201 Created`, tự động chọn hộ gia đình làm active context và chuyển về Dashboard.

## Các Luồng Rẽ Nhánh & Lỗi (Alternative / Error Flows)
- **Alt 1 (Bỏ qua nước)**: Tại Bước 3/4, người dùng bấm "Bỏ qua nước". Hệ thống chỉ tạo tài khoản Điện.
- **Err 1 (Dữ liệu không hợp lệ)**: Ngày chốt chỉ số nằm ngoài khoảng 1..31 hoặc chỉ số âm -> Backend trả về `422 Validation Error`.
