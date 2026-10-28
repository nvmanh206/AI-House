# BÁO CÁO MÂU THUẪN VÀ GIẢ ĐỊNH THIẾT KẾ (CONFLICTS & ASSUMPTIONS)
## Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia Đình tích hợp AI (Nhà Mình)

---

## 1. Danh sách Mâu thuẫn giữa Tài liệu DOCX và Mã nguồn Thực tế

### 1. Mật khẩu Băm (Argon2id vs Bcrypt)
- **Tài liệu DOCX NFR03 / Table 3.3:** Ghi nhận mật khẩu người dùng mã hóa bằng thuật toán Bcrypt.
- **Mã nguồn `security.py` & DOCX SD-01:** Sử dụng thuật toán Argon2id (`from argon2 import PasswordHasher`).
- **Quyết định đối sánh:** Mã nguồn sử dụng `Argon2id` đại diện cho công nghệ hiện tại (Code-Proven). Trong sơ đồ và đặc tả, ghi nhận thuật toán Argon2id làm chuẩn hiện hành và chú thích mâu thuẫn văn bản với NFR03.

### 2. Luồng Mời Thành viên Hộ (Email Token Invite vs Thêm trực tiếp)
- **Tài liệu DOCX (SD-03 / UC-03):** Mô tả quy trình gửi email mời kèm Token có thời hạn 48 giờ; người nhận bấm link chấp nhận (`accept-invite`) để đổi trạng thái từ `PENDING` sang `ACTIVE`.
- **Mã nguồn `services.py` & Router `POST /api/members`:** Thực hiện thêm trực tiếp người dùng có sẵn vào `household_members` nếu đúng email.
- **Quyết định đối sánh:** Ghi nhận cả 2 luồng: `UC-MEMBER-MGMT` (thêm trực tiếp - Code-Proven) và `UC-MEMBER-INVITE` (mời qua email token - As-Designed SRS). Sơ đồ sequence trình bày rõ luồng trực tiếp hiện tại và luồng token qua email theo thiết kế SRS.

### 3. Đánh dấu Trạng thái Thanh toán Hóa đơn (Thủ công vs Trực tuyến)
- **Tài liệu DOCX (Section 8.7 & UC-08):** Đề xuất tích hợp VNPay/MoMo để thanh toán tự động 1-Click.
- **Mã nguồn `POST /api/payments`:** Ghi nhận thanh toán thủ công (chuyển trạng thái hóa đơn sang `PAID`, tạo bản ghi `payments`).
- **Quyết định đối sánh:** Phân định rõ 2 Use Case riêng biệt: `UC-PAYMENT-ENTRY` (thanh toán thủ công - Code-Proven) và `UC-ONLINE-PAYMENT` (thanh toán online - Planned / Future Extension).

### 4. Xử lý Chỉ số AI OCR từ Ảnh (Mock Provider vs Production AI)
- **Tài liệu DOCX (Section 8.6, FR08, FR09):** Đánh dấu OCR là tính năng nâng cao được thiết kế trong yêu cầu hệ thống nhưng chưa triển khai chính thức trong bản phát hành hiện tại.
- **Mã nguồn `providers/ocr.py`:** Có chứa class Mock Provider trả về kết quả định dạng chỉ số giả lập.
- **Quyết định đối sánh:** Phân loại `UC-OCR-READING` là tính năng As-Designed / Planned Future.

### 5. Kết xuất Hóa đơn PDF (PDF Export Engine)
- **Tài liệu DOCX (SD-07, FR14):** Mô tả tính năng xuất file PDF hóa đơn từ màn hình chi tiết hóa đơn.
- **Mã nguồn `bills` router:** Trả về dữ liệu JSON đầy đủ chi tiết các bậc giá và thông tin hộ.
- **Quyết định đối sánh:** Phân loại `UC-EXPORT-PDF` là tính năng As-Designed SRS.

---

## 2. Bảng Giả định Thiết kế được Xác minh

| STT | Chủ đề Giả định | Mô tả Giả định | Căn cứ Xác minh trong Mã nguồn | Tác động Thiết kế |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Phân quyền Chủ hộ / Thành viên** | Chủ hộ (`OWNER`) có toàn quyền chỉnh sửa thông tin hộ và phân quyền thành viên; Thành viên (`MEMBER`) chỉ được xem và nhập chỉ số nếu được cấp quyền `readings:write`. | `security.py::household_context`, `models.py::HouseholdMember` | Sơ đồ Use Case thể hiện rõ vai trò `Owner` và `Member`. |
| 2 | **Cấu trúc Bảng Công tơ (`meters`)** | Công tơ điện/nước liên kết trực tiếp với `household_id` và tùy chọn gắn với `utility_account_id`. | `models.py::Meter` (khóa ngoại `household_id`, `utility_account_id`) | Sơ đồ ERD và Sequence thể hiện đúng liên kết trực tiếp này. |
| 3 | **Cách tính Kỳ Chỉ số Trước** | Chỉ số kỳ trước (`previous_reading`) được tự động truy vấn từ lượt ghi chỉ số chốt kỳ gần nhất trước đó của cùng công tơ. | `billing_service.py`, `meter_readings` table query | Khóa ràng buộc $C_{\text{mới}} \ge C_{\text{cũ}}$ trong `UC-READING-ENTRY`. |
| 4 | **Tính toán Bậc giá Decimal** | Đơn giá và sản lượng tiêu thụ được tính toán đồng bộ theo chuẩn `DECIMAL(12,2)` để không gây sai số tiền tệ. | `models.py::Bill`, `billing_service.py` | Đảm bảo đạt yêu cầu phi chức năng `NFR06`. |
