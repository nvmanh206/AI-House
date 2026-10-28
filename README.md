# Nhà Mình — Quản lý hóa đơn điện nước có tích hợp AI

## Clone và chạy

```sh
cd website
docker compose up -d --build --wait
```

Mở http://localhost:3000, đăng ký tài khoản đầu tiên để quản trị và tạo hộ của bạn. Không cần `.env` để khởi động; Gemini cần key riêng khi sử dụng AI. PostgreSQL, pgAdmin, migration và danh mục biểu giá công khai được cấu hình tự động. Không seed dữ liệu hộ demo. Xem [hướng dẫn Docker](DOCKER_GUIDE.md) về dữ liệu bền vững, cấu hình Gemini và tài khoản pgAdmin.

## Chạy từng phần để phát triển

Yêu cầu: Python 3.12+; Node.js 22+; PostgreSQL 16+.

**Ghi chú lịch sử máy phát triển (không áp dụng cho clone Docker mới):** PostgreSQL portable 16.15 chạy tại `127.0.0.1:5433`, database ứng dụng `utility_app`; pgAdmin Docker tại `http://127.0.0.1:5050`. SQLite trước đây đã được sao lưu và chuyển đổi, đối chiếu đủ 15 bảng trước khi đổi `backend/.env`. Database PostgreSQL `utility` cũ vẫn được giữ nguyên. Xem [hướng dẫn PostgreSQL và pgAdmin](docs/POSTGRESQL-PGADMIN.md) trước khi khởi động; không tự chuyển sang database Docker ở cổng 5434.

```powershell
cd website
python scripts/setup_env.py
docker compose up -d postgres
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.lock.txt
.\.venv\Scripts\python -m alembic upgrade head
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 
```

Terminal khác:

```powershell
cd website/frontend
npm ci
npm run dev
```

Terminal thứ ba, nếu cần nhắc lịch tự động:

```powershell
cd website/backend
.\.venv\Scripts\python -m app.scheduler
```

Dùng cùng hostname `localhost` cho frontend/backend để cookie same-site hoạt động. `.env` được tạo một lần, không ghi đè và không in secret. Nếu PostgreSQL của bạn dùng cấu hình riêng, sửa `backend/.env`. Tuyệt đối không commit các file `.env`.

## Tài khoản demo

Chỉ tồn tại sau lệnh seed, seed bị chặn khi `APP_ENV=production`:

- Chủ hộ: `demo@example.com` / `DemoHouse123!`
- Admin: `admin@example.com` / `AdminHouse123!`
- Seed gồm một hộ, hai công tơ, 12 tháng điện + 12 tháng nước, hóa đơn, thanh toán thủ công, thông báo và biểu giá minh họa.
- Provider seed: **Điện Demo**, **Nước Demo**. Giá không phải biểu giá hiện hành của EVN hay công ty nước.
- Tài khoản mới cần nhà cung cấp khớp biểu giá admin đã cấu hình. Có thể dùng tên provider demo nếu đang demo.

## Kiểm thử

```powershell
cd website/backend
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m alembic check
cd ../frontend
npm run build
npm run typecheck
npm audit
```

Lệnh pytest trực tiếp vẫn mặc định SQLite. Để chạy đúng PostgreSQL đang dùng, từ `website` chạy `.\backend\.venv\Scripts\python.exe scripts/test_postgres.py`: runner dùng database riêng `utility_app_test`, không dùng database ứng dụng và không xóa dữ liệu có sẵn. Kết quả mới nhất: 86 passed trên PostgreSQL. `utility_test` cũ thiếu cột, đã giữ nguyên để tránh sửa nhầm schema. Xem [hướng dẫn PostgreSQL và pgAdmin](docs/POSTGRESQL-PGADMIN.md).

## Cấu trúc

```text
website/
  frontend/app/                 Next.js App Router, CSS
  frontend/components/         shell, pages, forms, charts, API client
  backend/app/
    main.py                    REST controllers, DI, errors, rate limit
    config.py, db.py            configuration, transaction lifecycle
    models.py, schemas.py       ORM và validation
    repository.py              persistence queries
    services.py                auth, households, readings, statistics
    billing_service.py         deterministic Decimal tier pricing
    forecast_service.py        weighted moving average
    anomaly_service.py         rolling deviation
    notification_service.py    idempotent reminders
    admin_service.py           admin-only operations
    ai/                        context, router, registry, Rules/Skills/Tools
    providers/                 OCR/payment/provider extension points
    scheduler.py, seed.py
  backend/alembic/              versioned schema migration
  backend/tests/                pytest tests
  scripts/                      environment setup, HTTP smoke checks
  docs/                         architecture, schema, API, security, report
  docker-compose.yml
```

## Các luồng chính

1. Đăng ký → wizard 4 bước tạo hộ + tài khoản điện + tùy chọn nước.
2. Nhập chỉ số → lấy chỉ số trước → kiểm tra kỳ → tính lượng dùng → biểu giá DB → snapshot → bill ước tính và thông báo, trong một transaction.
3. Mở bill → xem breakdown → ghi nhận đã trả thủ công; thao tác idempotent, không giả gateway.
4. Scheduler → kiểm tra ngày nhập / ngày thanh toán / quá hạn → unique dedupe key → notifications.
5. Chat → authentication → immutable AgentContext → intent router → skill allowlist → tools → service → repository. Không SQL trong AI; không lưu chain-of-thought.

## Tài liệu và phạm vi

- [Tổng quan & Phân tích chi tiết toàn diện](TONG_QUAN_DU_AN_CHI_TIET.md)
- [Kiến trúc](docs/architecture.md), [Database](docs/database.md), [API](docs/api.md)
- [AI Agent](docs/ai-agent.md), [Bảo mật](docs/security.md), [Phát triển](docs/development.md)
- [Kế hoạch](docs/implementation-plan.md), [Kiểm chứng](docs/verification.md), [Báo cáo bàn giao](docs/delivery.md)

V1 mặc định dùng provider **deterministic**, không gọi LLM bên ngoài. Có abstraction LLMProvider và registry để bổ sung adapter; provider không hỗ trợ báo lỗi rõ ràng. OCR, EVN/water API, IoT, cổng thanh toán là **future interfaces**, chưa hoạt động thực. Không có endpoint EVN tự bịa. PDF dùng chức năng in/lưu PDF của trình duyệt.

Giới hạn nghiệp vụ: một công tơ hoạt động/tài khoản; chỉ nhập kỳ mới; chưa có workflow điều chỉnh bill đã phát hành, thay công tơ giữa kỳ, hóa đơn chính thức và thuế/phí theo địa phương. Admin tạo phiên bản biểu giá mới để giữ lịch sử. Chưa có quên mật khẩu/email verification, email/SMS push hay LLM mạng. Xem báo cáo để phân biệt phần đã kiểm chứng với phần chưa kiểm chứng.

## Khởi động hệ thống

Đăng nhập bằng:
- Chủ hộ: demo@example.com / DemoHouse123!
- Admin: admin@example.com / AdminHouse123!
Nếu đã tắt máy hoặc trang không mở, chạy lại như sau:
1. Mở PowerShell, khởi động PostgreSQL:
cd F:\Web\AI_Household_Utility_Billing\website
python scripts/local_postgres.py start
2. Trong cùng cửa sổ, chạy backend:
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
3. Mở PowerShell thứ hai, chạy frontend:
cd F:\Web\AI_Household_Utility_Billing\website\frontend
npm.cmd run dev
Giữ hai cửa sổ này mở rồi truy cập localhost:3000.
Nếu muốn bật nhắc lịch tự động, mở thêm PowerShell:
cd F:\Web\AI_Household_Utility_Billing\website\backend
.\.venv\Scripts\python.exe -m app.scheduler
Hiện tại không cần Docker, cài lại thư viện hay chạy seed lại.
