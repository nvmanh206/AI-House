# PostgreSQL và pgAdmin — môi trường local

Cập nhật 2026-10-28. Không tự seed dữ liệu demo.

## Truy cập

- PostgreSQL 16.15: `127.0.0.1:5433`; database ứng dụng `utility_app`. Backend đọc kết nối từ `backend/.env`.
- Database kiểm thử: `utility_app_test`, tách biệt khỏi dữ liệu ứng dụng.
- pgAdmin 4 9.18: <http://127.0.0.1:5050>.
- Email pgAdmin: `admin@example.com`; đây là tài khoản quản trị local, không phải tài khoản ứng dụng.
- Mật khẩu ngẫu nhiên và URL nằm trong `.local/pgadmin-access.txt`. Không commit hoặc đưa nội dung vào log.
- Trong pgAdmin: **Servers → Nha Minh → Nha Minh - application PostgreSQL → Databases → utility_app → Schemas → public → Tables**. Chọn bảng rồi **View/Edit Data → All Rows**, hoặc dùng Query Tool.

Server pgAdmin dùng `host.docker.internal:5433` từ container và passfile riêng đã cấu hình. Windows/backend dùng `127.0.0.1:5433`.

## Khởi động lại

Chạy PowerShell tại `website`:

```powershell
.\backend\.venv\Scripts\python.exe scripts/local_postgres.py start
.\backend\.venv\Scripts\python.exe scripts/configure_pgadmin.py
docker compose --profile admin up -d --no-deps pgadmin
```

`configure_pgadmin.py` giữ mật khẩu đã tạo, đọc credential từ cấu hình ứng dụng và sinh file kết nối trong `.local/`. Không thay đổi dữ liệu PostgreSQL. Nó không đặt lại tài khoản trong volume pgAdmin đã tồn tại; không xóa file mật khẩu hoặc volume để restart.

pgAdmin lưu cấu hình trong volume `nha-minh-utilities_pgadmin_data`. PostgreSQL ứng dụng lưu dữ liệu tại `.local/pgdata`, không phải volume PostgreSQL Docker cũ. Trong cấu hình local này chỉ pgAdmin chạy bằng Docker. Không chạy `docker compose down -v`, không xóa `.local/pgdata`.

Khởi động backend bằng lệnh uvicorn trong README sau khi PostgreSQL sẵn sàng. Backend phải restart sau khi đổi DATABASE_URL; tiến trình đang chạy không tự đổi database. Không khởi động PostgreSQL Docker cổng 5434 rồi nhầm đó là database local của ứng dụng.

## Dữ liệu và bản sao lưu

Cấu hình thực tế trước triển khai dùng `backend/utility.db` (SQLite), khác README cũ. Đã sao lưu và chuyển vào PostgreSQL mới `utility_app`, giữ ID, khóa ngoại, snapshot, Decimal và JSON; timestamp SQLite không có timezone được diễn giải UTC theo quy ước ứng dụng.

- 15 bảng nghiệp vụ đã được đối chiếu số lượng và SHA-256 nội dung chuẩn hóa trước khi đổi kết nối.
- Sau chuyển, kiểm tra lại SQLite gốc và PostgreSQL mới vẫn trùng đủ 15 bảng.
- SQLite gốc và PostgreSQL `utility` cũ được giữ nguyên, không tự merge hai bộ dữ liệu khác nhau.
- Backup SQLite: `.local/pre-postgres-*.sqlite3`.
- Backup cấu hình: `.local/backend-env-before-postgres-*`.
- Báo cáo đối chiếu: `.local/postgres-migration-*.json`, chứa số lượng/hash, không chứa bản ghi hoặc mật khẩu.

Đây là dữ liệu hiện có được bảo toàn, chưa xác nhận mọi bản ghi đều có nguồn gốc thực tế. Dữ liệu demo cũ nếu có vẫn được giữ; không tự xóa hoặc gọi là hóa đơn nhà cung cấp thật.

## Kiểm thử và bằng chứng

```powershell
# Tại website
.\backend\.venv\Scripts\python.exe scripts/test_postgres.py
# Tại website/backend
.\.venv\Scripts\python.exe -m alembic check
```

- API/server integration trên PostgreSQL: **86 passed, 2 warnings**, 17.15 giây. Fixture dùng dữ liệu kiểm soát và rollback trong database riêng.
- Alembic check database ứng dụng: **No new upgrade operations detected**.
- pgAdmin HTTP login và API kết nối server: **HTTP 200, success true**.
- Truy vấn từ container pgAdmin: PostgreSQL 16.15, đúng `utility_app`, 25 hóa đơn.
- `utility_test` cũ thiếu cột: lần chạy đầu 28 failed, 29 passed, 29 errors. Không xóa/sửa database đó; runner mới dùng `utility_app_test` với schema hiện tại.
- Chưa thay thế UI/system E2E toàn bộ sản phẩm hoặc xác nhận chất lượng provider AI thật.

## Chuyển đổi offline và khôi phục

`scripts/migrate_local_sqlite_to_postgres.py` chỉ dành cho chuyển đổi offline vào đích rỗng. Phải dừng backend, scheduler và mọi tiến trình ghi SQLite, rồi mới dùng cờ `--offline`; giữ tiến trình cũ dừng cho đến khi restart backend với PostgreSQL. Script từ chối nếu cổng 8000 hoạt động, khóa ghi nguồn và kiểm tra lại nguồn sau snapshot. Không chạy lại vào đích có dữ liệu.

Nếu PostgreSQL đã phát sinh dữ liệu mới, phải đối soát trước rollback. Không đơn giản đổi về SQLite cũ vì sẽ bỏ sót bản ghi mới. Chỉ phục hồi backup cấu hình khi đã dừng writer và xác nhận chưa có dữ liệu phát sinh; giữ nguyên database PostgreSQL để khôi phục khi cần.

Tham khảo: [container pgAdmin](https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html), [định dạng server JSON](https://www.pgadmin.org/docs/pgadmin4/latest/import_export_servers.html).
