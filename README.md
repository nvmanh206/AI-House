# Nhà Mình — Quản lý hóa đơn điện nước có tích hợp Gemini AI

## 1. Clone và khởi động

Yêu cầu: Git, Docker Desktop đang chạy với Linux containers và mạng để tải image/dependencies lần đầu. Không cần cài Python, Node.js, PostgreSQL hay pgAdmin trên máy.

```sh
git clone https://github.com/nvmanh206/AI-House.git
cd AI-House
docker compose up -d --build --wait
```

**Trong repo GitHub này, nội dung thư mục website đã nằm ở gốc repo. Không chạy thêm `cd website` sau khi clone.** Nếu bạn đang dùng workspace gốc có thư mục website thì chạy Docker ngay trong thư mục website đó.

- Ứng dụng: http://localhost:3000
- API Swagger: http://localhost:8000/docs
- pgAdmin: http://localhost:5050

Mở ứng dụng, tự đăng ký tài khoản rồi tạo hộ và công tơ. Tài khoản đầu tiên trong cấu hình phát triển là ADMIN, các tài khoản tiếp theo là USER. Không có tài khoản demo tự tạo. Launcher `docker-start.bat` hoặc `sh docker-start.sh` thực hiện cùng thao tác khởi động.

## 2. Hệ thống tự tạo những gì?

Lần chạy đầu, Docker tự tạo network và các volume; PostgreSQL tạo database `utility` và `knowledge`. Backend đợi hai database sẵn sàng, chạy migration tạo bảng/index/pgvector, đăng ký nguồn tri thức điện nước và nhập danh mục biểu giá điện EVN có nguồn, có phiên bản. Nếu chưa cấu hình JWT_SECRET, backend tự sinh khóa và lưu trong volume runtime. Frontend và scheduler chạy sau khi backend sẵn sàng.

Khi chạy lại, hệ thống dùng dữ liệu trong volume đã có. Migration/bootstrap được thiết kế chạy lặp mà không tạo trùng danh mục.

Các phần **không có sẵn khi clone**:

- Tài khoản, hộ, công tơ, chỉ số, hóa đơn, thanh toán của máy khác. Bạn tự đăng ký và nhập dữ liệu của mình.
- Gemini API key: mỗi thành viên tự cấu hình nếu cần AI.
- Nội dung kho RAG đã crawl trên máy người khác: Git chỉ chứa code và danh sách nguồn. Sau khi có key, scheduler thu thập nguồn đến hạn; admin cũng có thể yêu cầu crawl trong Kho tri thức. Nội dung cần tải, trích xuất, embedding và đạt điều kiện công bố trước khi AI truy xuất được; không bảo đảm thành công ngay vì còn phụ thuộc nguồn/quota.

Nhập chỉ số sẽ lưu PostgreSQL và tính lượng dùng. Hóa đơn ước tính được tạo khi có biểu giá nghiệp vụ phù hợp nhà cung cấp, nhóm giá, địa phương và kỳ. Giá nước trong RAG phục vụ giải thích/tra cứu, **không tự biến thành biểu giá tính hóa đơn**.

## 3. Dữ liệu lưu ở đâu?

Dữ liệu bền vững nằm trong **Docker named volumes trên máy đang chạy Docker**, không nằm trong source Git:

- `nha-minh-utilities_postgres_data`: PostgreSQL nghiệp vụ, gồm tài khoản/hộ/công tơ/chỉ số/hóa đơn/thanh toán. Mount tại `/var/lib/postgresql/data` của service postgres.
- `nha-minh-utilities_knowledge_data`: PostgreSQL RAG, gồm nguồn, tài liệu/phiên bản, đoạn văn, vector và nhật ký crawl/truy xuất. Mount tại `/var/lib/postgresql/data` của service knowledge-postgres.
- `nha-minh-utilities_knowledge_archive`: HTML/PDF gốc và nội dung trích xuất, mount tại `/data/knowledge`.
- `nha-minh-utilities_runtime_data`: khóa JWT tự sinh, mount tại `/app/runtime`.
- `nha-minh-utilities_pgadmin_data`: cấu hình, tài khoản và kết nối pgAdmin, mount tại `/var/lib/pgadmin`.

Các tên trên dùng project name mặc định. Nếu dùng `docker compose -p ten-khac`, prefix volume cũng thay đổi, nên bạn sẽ thấy bộ dữ liệu riêng.

Trên Windows Docker Desktop, volume nằm trong ổ đĩa Linux do Docker quản lý; không phải thư mục PostgreSQL ngay bên cạnh code. Xem tại **Docker Desktop → Volumes** hoặc:

```sh
docker volume ls
docker volume inspect nha-minh-utilities_postgres_data
```

Để xem dữ liệu dạng bảng, dùng pgAdmin. Không sửa trực tiếp các file vật lý của PostgreSQL.

## 4. Xem database trong pgAdmin

Đăng nhập http://localhost:5050 bằng cấu hình phát triển mặc định: email `admin@example.com`, mật khẩu `LocalPgAdmin2026!`. Đây là tài khoản pgAdmin, khác tài khoản bạn đăng ký trong ứng dụng.

Hai server được đăng ký sẵn. Khi pgAdmin hỏi mật khẩu kết nối:

- Nghiệp vụ: host `postgres`, port `5432`, database/user `utility`, mật khẩu mặc định `utility_local_dev`.
- Tri thức: host `knowledge-postgres`, port `5432`, database/user `knowledge`, mật khẩu mặc định `knowledge_local_dev`.

Đó là địa chỉ **bên trong Docker**. Công cụ PostgreSQL cài trên máy host dùng `localhost:5434` cho nghiệp vụ, `localhost:5435` cho RAG. Nếu đã đổi `.env`, dùng giá trị riêng của bạn. Mật khẩu mặc định chỉ dành cho phát triển local; các cổng chỉ bind 127.0.0.1.

## 5. Bật Gemini và thu thập tri thức

Tạo `.env` tại cùng thư mục với docker-compose.yml:

```powershell
Copy-Item .env.example .env
```

Linux/macOS dùng `cp .env.example .env`. Điền GEMINI_API_KEY trong file vừa tạo; chọn GEMINI_MODEL được tài khoản của bạn cấp quyền. Sau đó:

```sh
docker compose up -d --force-recreate backend scheduler
```

Trên máy đã có `.env`, sửa file hiện tại; không chép đè vì có thể làm sai mật khẩu database đang sử dụng. Không đưa key lên Git. Chưa có key vẫn quản lý chỉ số/hóa đơn được; chat/crawl sẽ cần key và quota hợp lệ.

Đăng nhập tài khoản admin → Quản trị hệ thống → Kho tri thức (`/admin/knowledge`) → chọn nguồn → Thu thập lại → xem lịch sử và trạng thái tài liệu. Scheduler xử lý công việc nền; trang có trạng thái chờ không đồng nghĩa crawl đã hoàn tất. Biểu giá thiếu căn cứ vẫn chờ duyệt.

## 6. Dừng, cập nhật và giữ dữ liệu

```sh
# Dừng container, giữ volumes và dữ liệu
docker compose down

# Khởi động lại
docker compose up -d --wait

# Nhận code mới và build lại
git pull
docker compose up -d --build --wait
```

Không dùng `docker compose down -v`, không xóa volume hay chọn dọn cả volumes trong Docker Desktop nếu cần giữ dữ liệu. Clone trên máy mới hoặc đổi project name sẽ có database riêng; Git không đồng bộ dữ liệu giữa các máy. Muốn chia sẻ dữ liệu, cần backup/restore hoặc một database dùng chung được cấu hình riêng.

## 7. Sao lưu và kiểm tra lỗi

Chi tiết backup ở [DOCKER_GUIDE.md](DOCKER_GUIDE.md#sao-lưu-dữ-liệu). Xem trạng thái và log:

```sh
docker compose ps
docker compose logs --tail=100 backend scheduler frontend
```

Có thể đổi cổng trong `.env` nếu trùng cổng trên máy. Hướng dẫn Docker là luồng khởi động chuẩn; các tài liệu PostgreSQL portable/SQLite cũ dưới docs mô tả môi trường phát triển trước đây.

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
