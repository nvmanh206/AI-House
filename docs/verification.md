# Kiểm chứng thực tế

Ngày: 07/09/2026. Môi trường: Windows, Python 3.14, Node 24, Next.js 16.3.4, PostgreSQL 16.15.

## Database và backend

- PASS — Alembic `upgrade head` trên database SQLite kiểm thử ban đầu.
- PASS — Alembic `upgrade head` trên **PostgreSQL 16.15**, database `utility` và `utility_test` riêng.
- PASS — `alembic check`: `No new upgrade operations detected`.
- PASS — demo seed: một hộ, hai meter, 24 readings, 24 bills, tariffs, notifications, manual payments.
- PASS — chạy seed lần hai không thêm/trùng dữ liệu.
- PASS — FastAPI/Uvicorn startup và `GET /api/health` trên database thật.
- PASS — HTTP smoke qua login/profile/household/meters/readings/bills/statistics/notifications/tariffs và AI forecast có nhãn FORECAST/ước tính.
- Scheduler đã khởi chạy, logic idempotency đã kiểm thử; không tuyên bố đã chờ tới lần chạy 07:00 ngày hôm sau.

## Backend regression suite

Lệnh: `python -m pytest -q -p no:cacheprovider` từ `backend/`.

**22 PASS trên SQLite; 22 PASS trên PostgreSQL.** PostgreSQL dùng biến TEST_DATABASE_URL trỏ database riêng, không dùng database demo làm test fixture.

- Auth register/login/unauthorized/logout/refresh.
- Household isolation và admin permission.
- Negative reading, valid consumption, duplicate kỳ, historical snapshot.
- Tier calculation ở 0, ranh giới bậc và số lẻ.
- Reminder idempotency.
- Manual payment idempotency.
- AI no-data và household isolation.
- Manual source, forecast label, due day không phải official deadline, injection trong tên hộ.
- Frozen context, cross-house rejection, secret stripping.
- MEMBER read-only không nhập chỉ số.
- Forecast weighted average và anomaly deterministic.
- Missing tariff rollback toàn bộ reading/bill.
- Không re-enable meter khi đã có active meter khác.
- Duplicate account-period bill khi đổi công tơ bị reject.
- Admin tariff validation/duplicate version/self-disable guard.
- Removed membership mất quyền ngay.
- Password change revoke sessions.
- Invalid JWT, absent/stale refresh rejection.
- Reject reading sai kỳ và nguồn giả provider.
- Notification chỉ user sở hữu được mark-read.
- Three-period bill comparison và zero baseline.
- Missing water data là null, không bị tính bằng 0 trong trung bình.

Warnings: 2 deprecation warnings từ Starlette test client (`httpx`) và AnyIO BlockingPortal alias. Không có traceback hoặc test failure ở lần chạy cuối.

## Frontend

- PASS — `npm run build` với Next.js 16.3.4 sau thay đổi cuối.
- PASS — `npm run typecheck`.
- PASS — `npm audit`: 0 vulnerabilities tại thời điểm kiểm tra. Bản Next.js ban đầu có dependency alert đã được nâng cấp, không dùng `audit fix --force`.
- PASS — HTTP 200 cho 18 route tĩnh được yêu cầu; dynamic bill API đã kiểm tra trong backend tests. Client-side quyền không thay backend authorization.
- PASS — local page compile/render response trước khi gửi yêu cầu mở preview.
- **CHƯA CHẠY** — browser interaction/E2E, visual screenshots, responsive device testing, PDF print verification. Build/HTTP không chứng minh các phần này.

## Docker

- PASS — `docker compose config --quiet`.
- **CHƯA KIỂM CHỨNG** — `docker compose up --build` do Docker Desktop lỗi nội bộ `dockerInference` socket. Không reset Docker.
- Đã dùng PostgreSQL portable **thật**, không dùng SQLite làm thay thế cho kết luận PostgreSQL.

## Nguồn PostgreSQL portable

Binary Windows 16.15 tải từ [EDB PostgreSQL binaries](https://www.enterprisedb.com/download-postgresql-binaries), theo hướng dẫn [PostgreSQL Windows downloads](https://www.postgresql.org/download/windows/). Runtime và data chỉ nằm trong `.local/`, được gitignore; không cài system service, bind loopback và dùng SCRAM password. Docker/PostgreSQL thông thường vẫn là hướng chạy phân phối chính.
