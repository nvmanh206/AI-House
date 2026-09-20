# Kế hoạch triển khai

## Khảo sát
- `website/` trống vào ngày 07/09/2026; không có mã nguồn cần di chuyển.
- Giữ nguyên toàn bộ tài liệu bên ngoài `website/`.
- Có Python 3.14 và Node 24; Docker CLI có sẵn nhưng daemon chưa chạy.
- Stack theo yêu cầu: Next.js App Router, React, Tailwind, Bootstrap; FastAPI, SQLAlchemy 2, Alembic, PostgreSQL.

## Các phase và cổng kiểm chứng
1. Khảo sát thư mục — xong.
2. Kế hoạch — tài liệu này.
3. Skeleton, cấu hình môi trường — kiểm tra import/compile.
4. Models, repository, Alembic — upgrade database và kiểm tra constraints.
5. Auth, household, membership — test đăng ký, đăng nhập và isolation.
6. Meters/readings — test delta, duplicate và quyền ghi.
7. Tariff/billing — test Decimal, snapshot, unique account/period.
8. Notifications — test idempotency và due date.
9. Statistics, forecast, anomaly — test tính toán deterministic.
10. AI Rules/Skills/Tools — trusted immutable context và tool allowlist.
11. Chat API — test grounding, isolation, thiếu dữ liệu, source.
12. Frontend — responsive shell, onboarding, forms và build.
13. Admin — quản lý user, tariff và audit, kiểm tra quyền backend.
14. Regression tests — chạy toàn bộ suite và sửa lỗi.
15. Docker, seed, docs — kiểm chứng startup, migration, seed; báo rõ phần chưa kiểm chứng.

## Quyết định
- Modular monolith; route → service → repository → database.
- Tiền và chỉ số dùng Decimal/Numeric; snapshot biểu giá trong bill.
- JWT có session revocation trong DB; mật khẩu Argon2; không lưu token thô.
- Household hiện tại được lưu server-side sau khi kiểm tra membership.
- AI offline deterministic mặc định; provider abstraction cho LLM; không giả API bên ngoài.
- Nhập chỉ số tuần tự, một chỉ số/meter/kỳ. Khóa công tơ khi nhập để tránh race.
- Scheduler chạy như một tiến trình riêng cùng codebase; khóa unique chống trùng notification.
- Biểu giá seed là dữ liệu minh họa, không khẳng định là giá EVN hiện hành.
- Test SQLite chỉ phục vụ kiểm thử nhanh; không thay thế kiểm chứng PostgreSQL.

## Trạng thái bàn giao

Các phần mã nguồn V1 đã triển khai. Backend regression được kiểm chứng cả SQLite và PostgreSQL 16.15; migration, seed, startup HTTP và frontend build đã chạy. Docker Compose có cấu hình hợp lệ nhưng chưa chạy containers do Docker Desktop lỗi nội bộ. AI hiện là deterministic offline với extension interfaces. Chưa browser E2E/visual QA. Xem `verification.md` và `delivery.md` để biết kết quả thực tế và giới hạn, không hiểu checklist phase là chứng nhận production.
