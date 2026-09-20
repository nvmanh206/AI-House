# Phát triển

1. Chạy `python scripts/setup_env.py` từ website; giữ `.env` local.
2. PostgreSQL + Alembic trước backend. Không dùng create_all làm startup shortcut.
3. Seed có cờ `--demo`, idempotent, không nằm trong migrations.
4. Backend: route mỏng → service authorize/business → repository persistence.
5. Frontend: App Router, API client chung tự refresh khi 401; không lưu access token trong localStorage.

## Thêm migration

```powershell
cd backend
.\.venv\Scripts\python -m alembic revision --autogenerate -m describe_change
# Đọc migration, đặc biệt rename/drop trước khi chạy.
.\.venv\Scripts\python -m alembic upgrade head
.\.venv\Scripts\python -m alembic check
```

Không sửa initial migration sau khi đưa vào môi trường dùng chung. Khi thêm fields bắt buộc cần backfill.

## Test layers

- pytest: API/service/security regression, SQLite fixture mặc định.
- PostgreSQL integration: `TEST_DATABASE_URL` riêng, fixture transaction/savepoints; không dùng DB thật.
- Production build + TypeScript: `npm run build`, `npm run typecheck`.
- HTTP smoke: sau seed và khởi chạy backend, `python scripts/http_smoke.py`.
- Kiểm tra frontend HTTP/luồng trực quan độc lập; build thành công không có nghĩa browser QA đã hoàn tất.

## Future integrations

- OCRService.extract: chỉ trích xuất value/confidence/raw_text, validate rồi user confirm trước save.
- ProviderAdapter: normalize ProviderBill, verify credential, official due date; cần hợp đồng API thật trước adapter EVN/water.
- IoT: identity thiết bị, event idempotency, normalization trước service; không đưa MQTT vào V1.
- PaymentProvider: cần intent, verified webhook/signature/idempotency và reconciliation; không tin callback frontend.
- LLMProvider: thêm adapter registry, chỉ gửi allowlisted evidence, validate output; không gửi DB URL hoặc secret vào prompt.

## Known development limits

Schemas và services tập trung để đồ án dễ đọc; khi lớn lên tách module household/billing/auth. UI sử dụng shared screen components trong một file để đồng bộ trải nghiệm, có thể tách theo feature. Collection chưa pagination toàn diện. Không có sửa/xóa chỉ số quá khứ vì ảnh hưởng chuỗi và snapshot tài chính.
