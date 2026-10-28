# KHO DANH MỤC THIẾT KẾ HỆ THỐNG (SYSTEM INVENTORY)
## Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia Đình tích hợp AI (Nhà Mình)

---

## 1. Phân hệ Nghiệp vụ & Bản đồ API Backend

| Phân hệ Nghiệp vụ | Mã UC Liên quan | Router File Backend | Base Endpoint | Mô hình ORM (SQLAlchemy) | Dịch vụ Xử lý (Service Layer) | Trạng thái Hiện thực |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Auth & Identity** | `UC-REGISTER`, `UC-LOGIN`, `UC-LOGOUT`, `UC-USER-PROFILE` | `app/ai/router.py`, `app/security.py` | `/api/auth` | `User`, `AuthSession` | `security.py` | Code-Proven |
| **Household & Members** | `UC-HOUSEHOLD-SETUP`, `UC-SELECT-HOUSEHOLD`, `UC-MEMBER-MGMT`, `UC-MEMBER-INVITE` | `app/main.py` | `/api/households`, `/api/members` | `Household`, `HouseholdMember` | `services.py` | Code-Proven / SRS |
| **Meters & Readings** | `UC-UTILITY-ACCOUNT-MGMT`, `UC-METER-MGMT`, `UC-METER-UPDATE`, `UC-READING-ENTRY`, `UC-OCR-READING` | `app/main.py` | `/api/utility-accounts`, `/api/meters`, `/api/readings` | `UtilityAccount`, `Meter`, `MeterReading` | `services.py`, `providers/ocr.py` | Code-Proven / Future |
| **Billing & Payments** | `UC-BILL-CALCULATION`, `UC-BILL-QUERY`, `UC-EXPORT-PDF`, `UC-PAYMENT-ENTRY`, `UC-ONLINE-PAYMENT` | `app/main.py` | `/api/bills`, `/api/payments` | `Tariff`, `TariffTier`, `Bill`, `Payment` | `billing_service.py` | Code-Proven / Future |
| **AI & Statistics** | `UC-STATISTICS-ALERT`, `UC-NOTIFICATION-READ`, `UC-AI-CHATBOT`, `UC-AI-FORECAST-ANOMALY` | `app/main.py`, `app/ai/router.py` | `/api/statistics`, `/api/notifications`, `/api/ai/chat` | `Notification`, `AIAnalysis` | `forecast_service.py`, `anomaly_service.py`, `app/ai/agent.py` | Code-Proven |
| **Admin & System** | `UC-ADMIN-USER-MGMT`, `UC-ADMIN-TARIFF-CONFIG`, `UC-ADMIN-AUDIT-LOG` | `app/main.py` | `/api/admin` | `User`, `Tariff`, `AuditLog` | `admin_service.py` | Code-Proven |

---

## 2. Bảng Yêu cầu Phi chức năng (NFR Inventory)

| Mã NFR | Tên Yêu cầu Phi chức năng | Mô tả Thông số Thiết kế | Cơ chế Kiểm tra & Đạt tiêu chuẩn |
| :--- | :--- | :--- | :--- |
| `NFR01` | Latency / Phản hồi | API REST $< 500\text{ms}$, RAG AI Agent $< 3\text{s}$ | Benchmark qua `http_smoke.py` và `test_system.py` |
| `NFR02` | Khả năng Mở rộng | Kiến trúc Modular Monolith RESTful, 10.000+ hộ | FastAPI Async Uvicorn engine |
| `NFR03` | Mã hóa Mật khẩu | Mật khẩu mã hóa Argon2id | `argon2-cffi` trong `security.py` |
| `NFR04` | Phân quyền RBAC | JWT Bearer Token + Cookie Refresh | FastAPI Depends `get_current_user` / `household_context` |
| `NFR05` | Quản lý Session | Access Token 15m, Refresh Token 7d | Bảng `auth_sessions` và session rotation |
| `NFR06` | Độ chính xác Tiền tệ | Không làm tròn sai lệch số dư tiền | Định dạng `DECIMAL(12,2)` trên DB & Python `decimal.Decimal` |
| `NFR07` | Tính Sẵn sàng | Availability 99.9% | Docker Compose deployment |
| `NFR08` | Phân lập Dữ liệu Hộ | Không rò rỉ dữ liệu giữa các hộ | Repository filter `household_id` scope bắt buộc |
| `NFR09` | Tương thích Giao diện | Responsive Mobile/Tablet/Desktop | Tailwind CSS responsive utility classes |
| `NFR10` | Khai thác Tri thức AI | RAG Hybrid Search với trích dẫn văn bản quy định | ChromaDB Vector Index + BM25 Lexical Search |
| `NFR11` | Nhật ký Truy vết Audit | Lưu vết mọi thao tác ghi dữ liệu quan trọng | Bảng `audit_logs` & Audit Middleware |
