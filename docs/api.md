# REST API

Base `/api`. Swagger `/docs`, schema `/openapi.json`. DTO chính xác và field constraints lấy từ OpenAPI; tất cả route nghiệp vụ yêu cầu Bearer access token. Current household lưu server-side trong auth session.

## Endpoints

- `GET /health` kiểm tra kết nối database.
- `POST /auth/register`, `POST /auth/login`: access_token JSON, refresh cookie HttpOnly.
- `POST /auth/refresh`: rotate refresh, phát access mới.
- `POST /auth/logout`: revoke session.
- `GET/PATCH /auth/me`: profile, current household, membership.
- `POST /auth/password`: đổi mật khẩu, revoke mọi session.
- `GET /households`: các hộ user thuộc về.
- `POST /households`: onboarding atomic gồm hộ, memberships, accounts và meters.
- `GET/PATCH /households/current`: đọc/sửa hộ hiện tại.
- `GET /households/{id}`: chỉ trong household hiện tại đã xác thực.
- `POST /households/{id}/select`: kiểm tra membership rồi đổi current household server-side.
- `GET/POST /members`, `DELETE /members/{id}`: quản lý thành viên, owner-only khi ghi.
- `GET/POST /utility-accounts`, `PATCH /utility-accounts/{id}`.
- `GET/POST /meters`, `PATCH /meters/{id}`: sửa tên/mã/disable.
- `GET/POST /readings`: nhập kỳ mới, tự lấy previous, tạo bill cùng transaction.
- `GET /bills?period=2026-08&status=UNPAID&utility_type=ELECTRICITY`.
- `GET /bills/{id}`: snapshot chi tiết.
- `GET/POST /payments`: ghi nhận manual full payment idempotent.
- `GET /tariffs`: biểu giá và tiers; authenticated.
- `GET /notifications`, `PATCH /notifications/{id}/read`: chỉ thông báo của user.
- `GET /statistics?months=6` hoặc `?start=2026-01-01&end=2026-08-31` (lọc theo kỳ tháng).
- `GET /statistics/forecast?utility_type=ELECTRICITY`.
- `POST /ai/chat`: chỉ nhận `{ "message": "..." }`; extra household_id bị reject.
- `GET /admin`: counts + basic AI usage.
- `GET /admin/users`, `PATCH /admin/users/{id}`: khóa/mở user, không tự khóa admin.
- `POST /admin/tariffs`: thêm phiên bản biểu giá, không sửa bill lịch sử.
- `GET /admin/audit`: 200 audit gần nhất.

## Error

```json
{"error":{"code":"INVALID_METER_READING","message":"Chỉ số mới không được nhỏ hơn chỉ số trước."}}
```

400 business validation, 401 authentication, 403 permission, 404 scoped resource, 409 duplicate/conflict, 422 Pydantic, 429 rate limit, 500 sanitized internal error, 503 unsupported LLM provider. Validation errors chỉ trả field/message, không echo password/input.

V1 chưa có pagination ở mọi collection, phù hợp demo nhỏ. Khi mở rộng cần cursor pagination và giới hạn truy vấn. Không dùng trực tiếp ở quy mô lớn trước khi harden.
