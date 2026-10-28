# Yêu Cầu Hệ Thống (System Requirements)

> **Phạm vi phân tích**: Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia Đình tích hợp AI (**Nhà Mình**).  
> **Nguồn bằng chứng**: Codebase hiện tại (`backend/`, `frontend/`, `docs/`, `docker-compose.yml`).  
> **Trạng thái Nguồn thiết kế ban đầu**: Không tìm thấy file Excel / Sprint backlog cho "Hệ thống tuyển dụng nội bộ" trong project root. Do đó, các yêu cầu tuyển dụng được ghi nhận là **Nguồn bổ sung bị thiếu (Blocked Gap)** theo quy định của Skill `system-design-orchestrator`.

---

## 1. Yêu Cầu Chức Năng Hiện Tại (As-Is Functional Requirements)

### FR-01: Quản lý Tài khoản & Phân quyền
- **FR-01.1**: Người dùng có thể đăng ký tài khoản với Email (mã hóa mật khẩu Argon2) và tên đầy đủ (`backend/app/services.py:10-30`).
- **FR-01.2**: Người dùng đăng nhập bằng Email/Password, hệ thống cấp Access Token JWT (lưu bộ nhớ frontend) và Refresh Token trong HttpOnly Cookie (`backend/app/main.py:70-86`).
- **FR-01.3**: Phân quyền theo vai trò hệ thống (`USER`, `MEMBER`, `ADMIN`) và vai trò thành viên hộ gia đình (`OWNER`, `MEMBER`) (`backend/app/security.py:30-65`).

### FR-02: Thiết Lập Hộ Gia Đình (Onboarding Wizard)
- **FR-02.1**: Cho phép tạo Hộ gia đình mới gồm Tên, Địa chỉ, Số thành viên (`backend/app/services.py:68-85`).
- **FR-02.2**: Đăng ký các Tài khoản Tiện ích (Điện / Nước), thiết lập Nhà cung cấp, Loại biểu giá, Mã khách hàng, Ngày chốt chỉ số, Ngày hạn nợ và Nhắc trước (`backend/app/models.py:54-71`).
- **FR-02.3**: Khởi tạo Công tơ ban đầu (`Meter`) với chỉ số khởi tạo `initial_reading` (`backend/app/models.py:72-82`).

### FR-03: Nhập Chỉ Số & Tính Toán Hóa Đơn Tự Động (Billing Engine)
- **FR-03.1**: Cho phép người dùng nhập chỉ số công tơ định kỳ theo kỳ (`BillingPeriod`) (`backend/app/services.py:161-190`).
- **FR-03.2**: Tự động tính lượng tiêu thụ `consumption = current_reading - previous_reading`, kiểm tra điều kiện `current >= previous` (`backend/app/models.py:93-107`).
- **FR-03.3**: Hệ thống tự động khớp Biểu giá bậc thang (`Tariff` & `TariffTier`) tương ứng với loại tiện ích, nhà cung cấp, loại biểu giá và tỉnh/thành phố (`backend/app/billing_service.py:21-53`).
- **FR-03.4**: Phát hành Hóa đơn ước tính `Bill` với số tiền `estimated_amount = final_amount`, lưu Snapshot phiên bản biểu giá & chi tiết từng bậc vào JSON (`backend/app/billing_service.py:54-68`).

### FR-04: Thanh Toán & Theo Dõi Hạn Nợ
- **FR-04.1**: Cho phép người dùng ghi nhận thanh toán thủ công cho hóa đơn chưa trả (`UNPAID` / `OVERDUE`) (`backend/app/services.py:211-230`).
- **FR-04.2**: Đảm bảo tính Idempotent của thanh toán: Mỗi hóa đơn chỉ được thanh toán 1 lần duy nhất (`UNIQUE bill_id` trong `Payment` model) (`backend/app/models.py:149-157`).

### FR-05: Nhắc Lịch Tự Động (Scheduler & Notifications)
- **FR-05.1**: Chạy tiến trình ngầm hàng ngày quét ngày nhập chỉ số và ngày thanh toán (`backend/app/scheduler.py:1-25`).
- **FR-05.2**: Tự động sinh thông báo `Notification` kèm `dedupe_key` độc nhất để tránh tạo thông báo trùng lặp (`backend/app/notification_service.py:1-80`).

### FR-06: Trợ Lý AI ("Nhà Mình Assistant")
- **FR-06.1**: Trợ lý AI trả lời câu hỏi về chỉ số, hóa đơn, so sánh tiêu thụ và dự báo chi phí dựa trên dữ liệu hộ gia đình (`backend/app/ai/agent.py:65-167`).
- **FR-06.2**: Cho phép tra cứu biểu giá điện/nước sinh hoạt công cộng theo tỉnh/thành phố trực tuyến qua Google Search Grounding (Google Gemini API) (`backend/app/ai/gemini.py:70-194`).
- **FR-06.3**: Đảm bảo an toàn AI: Không chạy SQL, không lộ dữ liệu hộ gia đình ra bên ngoài ngoại trừ câu hỏi công cộng đã chuẩn hóa (`backend/app/ai/agent.py:68-71`).

### FR-07: Quản Trị Hệ Thống (Admin Operations)
- **FR-07.1**: Xem thống kê tổng quan hệ thống (số user, số hộ gia đình, số hóa đơn) (`backend/app/admin_service.py:1-25`).
- **FR-07.2**: Khóa/Mở khóa hoặc thay đổi vai trò người dùng (`backend/app/admin_service.py:26-40`).
- **FR-07.3**: Tạo phiên bản biểu giá bậc thang mới cho Điện/Nước (`backend/app/admin_service.py:41-55`).
- **FR-07.4**: Xem nhật ký hệ thống (`AuditLog`) (`backend/app/admin_service.py:56-60`).

---

## 2. Khoảng Trống Yêu Cầu Bị Thiếu (As-Designed Gap / Blocked Gap)

| Mã Gap | Mô tả Khoảng trống | Trạng thái | Ghi chú & Hành động khuyến nghị |
| :--- | :--- | :--- | :--- |
| `GAP-REQ-01` | **Yêu cầu Hệ thống Tuyển dụng Nội bộ**: Không tìm thấy file Sprint / Excel / BRD mô tả các vai trò (Ứng viên, HR, Interviewer), quy trình tuyển dụng (Tạo tin, Nộp CV, Phỏng vấn, Offer). | **BLOCKED GAP** | Đã ghi nhận trong báo cáo. Hệ thống hiện tại trong codebase là **Quản lý Hóa đơn Điện Nước Hộ Gia Đình Tích hợp AI**. Cần bổ sung file yêu cầu tuyển dụng nếu muốn thiết kế cho hệ thống đó. |
| `GAP-REQ-02` | **Tích hợp Cổng thanh toán trực tuyến**: Hiện tại thanh toán chỉ hỗ trợ ghi nhận thủ công `MANUAL`. Chưa có tích hợp VNPay / VietQR / MoMo SDK. | **PROPOSED GAP** | Sẽ được đưa vào mô hình thiết kế mở rộng `as-designed`. |
| `GAP-REQ-03` | **Tự động đọc chỉ số qua OCR / IoT**: Chưa có service kết nối camera OCR đọc chỉ số từ ảnh công tơ tự động. | **PROPOSED GAP** | Đưa vào luồng đề xuất nâng cấp V2. |
