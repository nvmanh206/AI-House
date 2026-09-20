# Báo cáo bàn giao V1

Ngày kiểm chứng: 07/09/2026. Mã nguồn nằm hoàn toàn trong `website/`, giữ nguyên tài liệu dự án bên ngoài. Không có kết nối EVN, ngân hàng hoặc LLM mạng giả.

## 1. Cấu trúc project

`frontend/`, `backend/`, `docs/`, `scripts/`, `.gitignore`, `README.md`, `docker-compose.yml`. Thư mục `.local/` được gitignore, chứa PostgreSQL portable/database phục vụ bản chạy local; không thuộc mã nguồn phân phối. Cấu trúc chi tiết trong README.

## 2. Backend architecture

FastAPI dependency injection → services → Repository → SQLAlchemy Session/PostgreSQL. Services riêng cho billing, forecast, anomaly, notification, admin. Transaction commit/rollback per request. Scheduler là process dùng cùng codebase, không microservices.

## 3. Frontend architecture

Next.js 16 App Router / React 19 / TypeScript, Tailwind 4 và Bootstrap grid-only. Shared application shell, page components, API client giữ token trong memory, Recharts. Responsive sidebar/mobile nav, form/loading/empty/error/toast. Dữ liệu lấy từ backend, không có fake-data fallback.

## 4. Database schema

14 bảng nghiệp vụ theo yêu cầu + `auth_sessions`: users, households, household_members, utility_accounts, meters, billing_periods, meter_readings, tariffs, tariff_tiers, bills, payments, notifications, ai_analyses, audit_logs. Numeric/Decimal, constraints, foreign keys, unique billing/account/period và dedupe keys. Alembic initial migration thực, đã chạy PostgreSQL. Chi tiết [database.md](database.md).

## 5. Authentication flow

Register/login → Argon2 verify/hash → JWT access + HttpOnly refresh cookie. Refresh rotation, hash trong DB, revoke khi logout/change password. Authenticate kiểm tra session/user active; membership và permissions được kiểm tra lại server-side. Chọn hộ chỉ thay server context sau khi kiểm tra membership.

## 6. Billing flow

Chọn công tơ/kỳ → backend lấy previous reading → reject negative/old/duplicate → consumption → tariff DB theo ngày → Decimal tier calculation → bill + tariff/breakdown snapshot. Một transaction, row locks PostgreSQL và unique constraint. Thay tariff không sửa hóa đơn lịch sử. Tiền là ước tính chưa gồm thuế/phí; official_amount còn null.

## 7. Notification flow

APScheduler chạy 07:00 giờ Việt Nam; kiểm tra lịch ghi chỉ số, lịch thanh toán cấu hình, bill gần hạn/quá hạn. Sự kiện nhập chỉ số tạo BILL_CREATED/ABNORMAL_CONSUMPTION; payment tạo PAYMENT_SUCCESS. Dedupe key theo sự kiện + user, savepoint xử lý race đúng loại. UI có bell/unread/mark read. Không gửi email/SMS.

## 8. AI architecture

Frozen AgentContext do backend tạo → router → skill registry → allowlisted tools → services. Runtime đọc Rules/SKILL.md. ForecastService/AnomalyService/BillingService tính số, provider giải thích kết quả. V1 **deterministic offline**, keyword router; có LLMProvider ABC/registry nhưng chưa có adapter LLM mạng. Không lưu chain-of-thought hoặc raw chat.

## 9. Rules

`core`, `authorization`, `privacy-security`, `grounding`, `actions`, `response` — sáu file Markdown. Quyền truy cập được enforce bằng code, không chỉ prompt.

## 10. Skills

`household_overview`, `consumption_analysis`, `consumption_comparison`, `bill_analysis`, `bill_forecast`, `anomaly_detection`, `saving_recommendation`, `payment_assistant`, `explain_result`. Mỗi file có đủ 10 mục cấu trúc được yêu cầu.

## 11. Tools

`get_household_profile`, `get_consumption_history`, `get_latest_consumption`, `get_bill_history`, `get_current_bill`, `get_tariff`, `get_payment_status`, `get_upcoming_notifications`. Không SQL trực tiếp trong AI, không tool ghi dữ liệu V1.

## 12. API endpoints

Các nhóm `/api/auth`, `/households`, `/members`, `/utility-accounts`, `/meters`, `/readings`, `/bills`, `/payments`, `/tariffs`, `/notifications`, `/statistics`, `/ai`, `/admin`; danh sách method/path đầy đủ tại [api.md](api.md), schema sống tại `/docs`.

## 13. Frontend pages

`/`, `/login`, `/register`, `/onboarding`, `/dashboard`, `/household`, `/household/members`, `/meters`, `/readings`, `/bills`, `/bills/[id]`, `/statistics`, `/notifications`, `/assistant`, `/settings`, `/admin`, `/admin/users`, `/admin/tariffs`, `/admin/audit`.

## 14–15. Tests đã chạy và kết quả

Xem [verification.md](verification.md) cho lệnh, số test và giới hạn. Backend suite được chạy trên cả SQLite và PostgreSQL thật; frontend production build/TypeScript, HTTP route smoke, backend HTTP workflow và npm audit được kiểm tra. Không gọi build là visual/E2E verification.

## 16. Cách chạy

Xem README cho Docker và chạy thủ công. Trong môi trường bàn giao hiện tại, Docker Desktop lỗi nên PostgreSQL portable đã được tạo trong `.local/`, chạy trên `127.0.0.1:5433`. `backend/.env` local trỏ tới database này.

```powershell
cd website
python scripts/local_postgres.py start
cd backend
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# Terminal khác: cd website/frontend; npm run dev
# Terminal khác: cd website/backend; .\.venv\Scripts\python -m app.scheduler
```

Mở http://localhost:3000. Sau khi dùng xong, dừng frontend/backend/scheduler bằng Ctrl+C; dừng PostgreSQL bằng `python scripts/local_postgres.py stop`. Bản portable không cần thiết khi máy khác chạy Docker/PostgreSQL sẵn.

## 17. Demo credentials

- `demo@example.com` / `DemoHouse123!`
- `admin@example.com` / `AdminHouse123!`

Đây là tài khoản demo, không dùng public/production. Seed có 12 tháng điện/nước, 24 bill và dữ liệu minh họa. Seed idempotent và bị cấm trong production.

## 18. Mock / placeholder

- Deterministic offline provider là mặc định, không phải LLM sinh văn bản thật.
- `MockProviderAdapter` chỉ nhận fixture cho test; không đóng giả EVN.
- EVN/water adapter raise NotImplementedError rõ ràng.
- OCRService là interface, chưa upload/OCR.
- ManualPaymentProvider chỉ xác nhận người dùng tự ghi nhận, không xác minh ngân hàng.
- PDF dùng chức năng in của trình duyệt, chưa tạo PDF server-side.

## 19. Future

OCR + user confirmation; provider API đã được cấp quyền/hợp đồng; IoT normalization/idempotency; payment gateway/webhook; external LLM adapter + output validation; email/SMS; password recovery; pagination và giám sát vận hành.

## 20. Vấn đề còn tồn tại

- Docker Desktop của máy lỗi socket `dockerInference`; đã validate Compose nhưng chưa build/chạy toàn bộ containers. Không reset/xóa cấu hình Docker người dùng.
- Chưa có kiểm thử browser tương tác/E2E hoặc visual QA trên thiết bị thật; frontend đã build/typecheck và HTTP smoke.
- Hai deprecation warnings từ test client/AnyIO, không có test thất bại.
- Chỉ nhập kỳ mới, một active meter/account; chưa sửa kỳ lịch sử/thay công tơ giữa kỳ, official provider bill và thuế/phí địa phương.
- AI router keyword có giới hạn; forecast heuristic cần ít nhất 2 kỳ. Không kết luận thiết bị cụ thể là nguyên nhân.
- Chưa tối ưu pagination/load, rate limit memory single worker, chưa email verification/reset. Đây là V1 đồ án, chưa tuyên bố sẵn sàng production công khai.
