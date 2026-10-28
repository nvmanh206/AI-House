# MA TRẬN TRUY XUẤT NGUỒN GỐC TỔNG THỂ (TRACEABILITY MATRIX)
## Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia Đình tích hợp AI (Nhà Mình)

---

## 1. Yêu cầu Chức năng (FR01 - FR28) -> Mã UC -> Sơ đồ -> Mã nguồn & Cơ sở dữ liệu

| Mã FR | Tên Yêu cầu Chức năng (SRS) | Mã Use Case | Tên Sơ đồ Use Case | Tên Sơ đồ Sequence | API Endpoint (FastAPI Router) | Bảng CSDL (PostgreSQL ORM) | Bảng Kịch bản Kiểm thử |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FR01` | Đăng ký tài khoản cá nhân | `UC-REGISTER` | `auth/register.puml` | `auth/register.puml` | `POST /api/auth/register` | `users` | `test_system.py::test_auth` |
| `FR02` | Đăng nhập & Đăng xuất an toàn | `UC-LOGIN`<br>`UC-LOGOUT` | `auth/login.puml`<br>`auth/auth_overview.puml` | `auth/login.puml`<br>`auth/logout.puml` | `POST /api/auth/login`<br>`POST /api/auth/logout` | `users`, `auth_sessions` | `test_system.py::test_auth` |
| `FR03` | Quản lý thông tin hộ gia đình | `UC-HOUSEHOLD-SETUP`<br>`UC-SELECT-HOUSEHOLD` | `household/household_setup.puml`<br>`household/household_overview.puml` | `household/household_setup.puml`<br>`household/select_household.puml` | `POST /api/households`<br>`POST /api/households/{id}/select` | `households`, `household_members` | `test_system.py::test_household` |
| `FR04` | Quản lý thành viên hộ & phân quyền | `UC-MEMBER-MGMT`<br>`UC-MEMBER-INVITE` | `household/member_management.puml` | `household/member_management.puml`<br>`household/member_invite.puml` | `GET/POST/DELETE /api/members` | `household_members` | `test_system.py::test_members` |
| `FR05` | Khai báo & quản lý danh mục công tơ | `UC-UTILITY-ACCOUNT-MGMT`<br>`UC-METER-MGMT`<br>`UC-METER-UPDATE` | `meter/meter_management.puml`<br>`meter/meter_overview.puml` | `meter/utility_account_mgmt.puml`<br>`meter/meter_management.puml`<br>`meter/meter_update.puml` | `GET/POST/PATCH /api/utility-accounts`<br>`GET/POST/PATCH /api/meters` | `utility_accounts`, `meters` | `test_system.py::test_meters` |
| `FR06` | Ghi nhận chỉ số điện/nước hàng tháng | `UC-READING-ENTRY` | `meter/reading_entry.puml` | `meter/reading_entry.puml` | `POST /api/readings` | `meter_readings`, `billing_periods` | `test_system.py::test_readings` |
| `FR07` | Kiểm tra tính hợp lệ số đo chốt kỳ | `UC-READING-ENTRY` | `meter/reading_entry.puml` | `meter/reading_entry.puml` | `POST /api/readings` (validation logic) | `meter_readings` | `test_regressions.py` |
| `FR08` | Nhận diện chỉ số từ ảnh công tơ (OCR) | `UC-OCR-READING` | `meter/reading_entry.puml` | `meter/ocr_reading.puml` | `providers/ocr.py` (Mock Provider) | `meter_readings.image_url` | (Planned / Future) |
| `FR09` | Xác nhận & điều chỉnh chỉ số OCR | `UC-OCR-READING` | `meter/reading_entry.puml` | `meter/ocr_reading.puml` | `providers/ocr.py` (Mock Provider) | `meter_readings.is_confirmed` | (Planned / Future) |
| `FR10` | Tự động tính tiền điện bậc thang EVN | `UC-BILL-CALCULATION` | `billing/bill_calculation.puml` | `billing/bill_calculation.puml` | `billing_service.py::calculate_tiers` | `tariffs`, `tariff_tiers`, `bills` | `test_system.py::test_billing` |
| `FR11` | Tự động tính tiền nước sinh hoạt bậc thang | `UC-BILL-CALCULATION` | `billing/bill_calculation.puml` | `billing/bill_calculation.puml` | `billing_service.py::calculate_tiers` | `tariffs`, `tariff_tiers`, `bills` | `test_system.py::test_billing` |
| `FR12` | Quản lý & xem chi tiết hóa đơn | `UC-BILL-QUERY` | `billing/bill_query.puml` | `billing/bill_query.puml` | `GET /api/bills`, `GET /api/bills/{id}` | `bills` | `test_system.py::test_billing` |
| `FR13` | Ghi nhận trạng thái thanh toán | `UC-PAYMENT-ENTRY`<br>`UC-ONLINE-PAYMENT` | `billing/payment_entry.puml` | `billing/payment_entry.puml`<br>`billing/online_payment.puml` | `POST /api/payments` | `payments`, `bills` | `test_system.py::test_payments` |
| `FR14` | Xuất hóa đơn định dạng PDF | `UC-EXPORT-PDF` | `billing/bill_query.puml` | `billing/export_pdf.puml` | (SRS Design Specification) | `bills` | SRS Test Suite |
| `FR15` | Phát hiện chỉ số tiêu thụ bất thường | `UC-AI-FORECAST-ANOMALY` | `ai_statistics/ai_forecast_anomaly.puml` | `ai_statistics/ai_forecast_anomaly.puml` | `anomaly_service.py`, `ai/tools/` | `ai_analyses` | `test_chat_process.py` |
| `FR16` | Cảnh báo rò rỉ điện/nước & phân tích | `UC-AI-CHATBOT` | `ai_statistics/ai_chatbot.puml` | `ai_statistics/ai_chatbot.puml` | `POST /api/ai/chat`, `notification_service.py` | `notifications`, `ai_analyses` | `test_chat_process.py` |
| `FR17` | Dự báo chi phí hóa đơn kỳ tới | `UC-AI-FORECAST-ANOMALY` | `ai_statistics/ai_forecast_anomaly.puml` | `ai_statistics/ai_forecast_anomaly.puml` | `GET /api/statistics/forecast` | `bills`, `meter_readings` | `test_system.py::test_forecast` |
| `FR18` | Đề xuất giải pháp tiết kiệm năng lượng | `UC-AI-CHATBOT` | `ai_statistics/ai_chatbot.puml` | `ai_statistics/ai_chatbot.puml` | `POST /api/ai/chat` (LLM instructions) | N/A (Dynamic AI LLM) | `test_useful_answers.py` |
| `FR19` | Màn hình Dashboard tổng quan | `UC-STATISTICS-ALERT` | `ai_statistics/statistics_alert.puml` | `ai_statistics/statistics_alert.puml` | `GET /api/households/current`, `GET /api/statistics` | `households`, `bills` | Frontend Integration |
| `FR20` | Biểu đồ sản lượng tiêu thụ | `UC-STATISTICS-ALERT` | `ai_statistics/statistics_alert.puml` | `ai_statistics/statistics_alert.puml` | `GET /api/statistics` | `meter_readings` | Frontend Integration |
| `FR21` | Biểu đồ so sánh chi phí qua các kỳ | `UC-STATISTICS-ALERT` | `ai_statistics/statistics_alert.puml` | `ai_statistics/statistics_alert.puml` | `GET /api/statistics` | `bills` | Frontend Integration |
| `FR22` | Báo cáo chi phí hộ gia đình | `UC-STATISTICS-ALERT` | `ai_statistics/statistics_alert.puml` | `ai_statistics/statistics_alert.puml` | `GET /api/statistics` | `bills` | Frontend Integration |
| `FR23` | Thông báo nhắc nhở ngày chốt số | `UC-STATISTICS-ALERT` | `ai_statistics/statistics_alert.puml` | `ai_statistics/statistics_alert.puml` | `scheduler.py`, `notification_service.py` | `notifications` | Background Scheduler |
| `FR24` | Thông báo nhắc hạn thanh toán | `UC-STATISTICS-ALERT` | `ai_statistics/statistics_alert.puml` | `ai_statistics/statistics_alert.puml` | `scheduler.py`, `notification_service.py` | `notifications` | Background Scheduler |
| `FR25` | Quản lý danh sách thông báo | `UC-NOTIFICATION-READ` | `ai_statistics/statistics_alert.puml` | `ai_statistics/notification_read.puml` | `GET /api/notifications`, `PATCH /api/notifications/{id}/read` | `notifications` | `test_system.py::test_notifications` |
| `FR26` | Quản lý người dùng hệ thống (Admin) | `UC-ADMIN-USER-MGMT` | `admin/admin_management.puml` | `admin/admin_user_mgmt.puml` | `GET/PATCH /api/admin/users` | `users` | `test_system.py::test_admin` |
| `FR27` | Quản lý biểu giá điện/nước bậc thang | `UC-ADMIN-TARIFF-CONFIG` | `admin/admin_management.puml` | `admin/admin_tariff_config.puml` | `GET /api/tariffs`, `POST /api/admin/tariffs` | `tariffs`, `tariff_tiers` | `test_system.py::test_admin` |
| `FR28` | Theo dõi nhật ký hệ thống Audit Log | `UC-ADMIN-AUDIT-LOG` | `admin/admin_management.puml` | `admin/admin_audit_log.puml` | `GET /api/admin/audit` | `audit_logs` | `test_system.py::test_admin` |

---

## 2. Yêu cầu Phi chức năng (NFR01 - NFR11) -> Thiết kế Kiến trúc & Hiện thực

| Mã NFR | Tên Yêu cầu Phi chức năng | Tiêu chuẩn & Thông số Thiết kế | Hiện thực trong Mã nguồn & Hạ tầng |
| :--- | :--- | :--- | :--- |
| `NFR01` | Thời gian phản hồi API | Phản hồi API thường $< 500\text{ms}$; truy vấn RAG $< 3.0\text{s}$ | Async FastAPI, Uvicorn, PostgreSQL indexing, ChromaDB vector search |
| `NFR02` | Khả năng mở rộng (Scalability) | Hỗ trợ 10.000+ hộ gia đình, kiến trúc Modular Monolith | Next.js 14 App Router, RESTful APIs, Stateless JWT Session |
| `NFR03` | Mã hóa mật khẩu & Bảo mật | Mã hóa mật khẩu chuẩn an toàn trước khi lưu CSDL | Implement bằng `Argon2id` (`argon2-cffi`) trong `security.py` |
| `NFR04` | Xác thực & Phân quyền RBAC | Signed JWT Access Token + Role-based Access Control | OAuth2 Bearer, HTTPOnly Cookie Refresh Token, Owner/Member scope |
| `NFR05` | Quản lý Phiên làm việc (Session) | Access Token 15 phút, Refresh Token 7 ngày | `AuthSession` database table, token rotation trong `security.py` |
| `NFR06` | Độ chính xác tính toán tài chính | Không sai lệch số dư tiền điện/nước | Định dạng `DECIMAL(12,2)` cho `consumption`, `unit_price`, `official_amount` |
| `NFR07` | Tính sẵn sàng của Hệ thống | Availability 99.9% | Docker Compose, PostgreSQL multi-container setup |
| `NFR08` | Bảo mật Dữ liệu Riêng tư | Phân lập dữ liệu giữa các Hộ gia đình | Filter bắt buộc `household_id` trong Repository scope (`household_context`) |
| `NFR09` | Khả năng tương thích thiết bị | Responsive UI trên Mobile, Tablet & Desktop | Tailwind CSS utility-first styling, Next.js dynamic layouts |
| `NFR10` | Khai thác Tri thức AI (RAG) | RAG Hybrid Search với trích dẫn văn bản quy định | ChromaDB Vector Indexing + BM25 Lexical + Reciprocal Rank Fusion |
| `NFR11` | Nhật ký Truy vết (Auditing) | Lưu vết mọi thao tác ghi dữ liệu quan trọng | Middleware & `repository.py::audit` ghi nhận IP, action, metadata |
