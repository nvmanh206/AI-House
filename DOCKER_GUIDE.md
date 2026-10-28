# Chạy Nhà Mình bằng Docker

Cài Docker Desktop và bật Linux containers. Từ thư mục repo vừa clone (AI-House, nơi chứa docker-compose.yml), chạy:

```sh
docker compose up -d --build --wait
```

Không cần cài Python, Node.js, PostgreSQL hoặc tạo `.env` trên máy. Lần đầu cần mạng để tải image và dependencies. Mở http://localhost:3000 và đăng ký tài khoản của bạn. Trong cấu hình phát triển này, tài khoản đầu tiên là ADMIN; các tài khoản tiếp theo là USER. Cơ chế này bị tắt khi APP_ENV khác development.

Backend tự chạy migration cho hai database và nhập danh mục biểu giá công khai có phiên bản; không tạo tài khoản, hộ, chỉ số hay hóa đơn demo. Hãy tạo hộ và công tơ của bạn. Biểu giá EVN sinh hoạt được cung cấp trong `backend/data/tariffs/`; chỉ áp dụng khi đúng nhà cung cấp, nhóm giá và thời điểm hiệu lực. Hóa đơn hệ thống là ước tính, chưa gồm thuế/phí. Giá nước phải cấu hình theo nhà cung cấp và địa phương; không có giá nước chung tự suy đoán.

## Gemini (tùy chọn)

Ứng dụng quản lý điện nước chạy được khi chưa có key. Muốn chat AI hoặc thu thập tri thức:

1. Sao chép `.env.example` thành `.env` ở thư mục website.
2. Điền GEMINI_API_KEY của bạn và chọn model được tài khoản cấp quyền.
3. Chạy `docker compose up -d --force-recreate backend scheduler`.

Không commit `.env`. Không thay mật khẩu database đã dùng trên volume hiện có bằng giá trị ví dụ. AI chưa cấu hình sẽ báo lỗi dịch vụ rõ ràng. Kho RAG ban đầu chỉ đăng ký nguồn; vào quản trị để yêu cầu thu thập sau khi có key. Crawler phụ thuộc mạng/quota và việc duyệt tài liệu.

## PostgreSQL và pgAdmin

pgAdmin: http://localhost:5050. Mặc định phát triển: email `admin@example.com`, mật khẩu `LocalPgAdmin2026!`. Hai máy chủ được đăng ký sẵn; khi kết nối, dùng mật khẩu database:

- Nghiệp vụ: host postgres, database/user utility, mật khẩu utility_local_dev.
- Tri thức: host knowledge-postgres, database/user knowledge, mật khẩu knowledge_local_dev.

Các giá trị trên có thể đổi trong `.env` trước lần chạy đầu. Các cổng chỉ bind 127.0.0.1. Đây là cấu hình phát triển nội bộ; triển khai production cần cấu hình bảo mật riêng.

## Lưu dữ liệu và xử lý lỗi

Database, bản gốc tài liệu, phiên pgAdmin và khóa JWT tự sinh được lưu bằng named volumes. `docker compose down` rồi `docker compose up -d` giữ dữ liệu. **Không dùng `down -v` hoặc xóa volumes nếu muốn giữ dữ liệu.** Không cần sao chép database cá nhân lên Git.

```sh
docker compose ps
docker compose logs --tail=100 backend scheduler frontend
```

Có thể đổi FRONTEND_PORT, API_PORT, POSTGRES_PORT, KNOWLEDGE_POSTGRES_PORT và PGADMIN_PORT trong `.env` nếu trùng cổng. API docs mặc định http://localhost:8000/docs. Các launcher docker-start cũng chờ khởi động và trả lỗi nếu thất bại.

## Trước khi push

Chạy `python scripts/repo_audit.py` nếu máy có Python, xem `git status` và diff. Script kiểm tra tập file dự kiến đưa lên Git, chặn env/runtime artifacts và một số mẫu secret; không thay thế kiểm toán toàn bộ lịch sử Git. Các thư mục .local, .env, node_modules, cache/build và cấu hình agent cá nhân được ignore. File `.env.example`, migration, lockfile và dữ liệu biểu giá công khai có nguồn phải giữ lại.


## Sao lưu dữ liệu

Tạo thư mục backups tại gốc repo. Lệnh dưới dùng dump nhị phân bên trong container rồi docker cp ra máy host, tránh lỗi encoding khi chuyển hướng output trong Windows PowerShell:

```sh
mkdir backups
docker compose exec -T postgres pg_dump -U utility -d utility -Fc -f /tmp/utility.dump
docker compose cp postgres:/tmp/utility.dump ./backups/utility.dump
docker compose exec -T knowledge-postgres pg_dump -U knowledge -d knowledge -Fc -f /tmp/knowledge.dump
docker compose cp knowledge-postgres:/tmp/knowledge.dump ./backups/knowledge.dump
```

Các tên file cố định sẽ thay bản backup trước; đổi tên theo ngày nếu muốn giữ nhiều bản. Đây là backup từng database, không phải snapshot đồng bộ của cả hệ thống đang ghi dữ liệu. Để backup đầy đủ và nhất quán, tạm dừng backend/scheduler trong thời gian backup, đồng thời export volume knowledge_archive bằng Docker Desktop (Volumes → chọn volume → Export), rồi chạy lại backend/scheduler. Cần giữ cả dump RAG và archive để đọc/tải tài liệu gốc sau khi khôi phục. Runtime/pgAdmin cũng có thể export nếu muốn giữ khóa JWT và cấu hình đăng nhập.

Không commit backups hoặc gửi dump có dữ liệu cá nhân lên GitHub. Dùng pgAdmin Restore để khôi phục dump vào database đích đã chuẩn bị; kiểm tra đúng môi trường trước khi restore vì có thể xung đột với dữ liệu hiện có. Clone code đơn thuần không tự lấy backup hay dữ liệu của máy khác.
