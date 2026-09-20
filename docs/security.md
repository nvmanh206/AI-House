# Bảo mật

- Argon2 hash mật khẩu; min 10/max 128 ký tự. JWT HS256 có exp/iat/iss/aud/sub/sid bắt buộc; secret tối thiểu 32 ký tự, sinh ngẫu nhiên qua setup script.
- Access token chỉ trong memory frontend; refresh HttpOnly/SameSite strict, Secure khi production, path giới hạn `/api/auth`. Refresh hash trong DB, rotation mỗi lần dùng; session revoke khi logout/change password. Không hỗ trợ OAuth/email reset trong V1.
- Mỗi request kiểm tra user active và auth session; household membership kiểm tra server-side. Global ADMIN không tự động đọc dữ liệu household ngoài membership.
- Chủ hộ quản lý member, không xóa owner. MEMBER mặc định read-only; quyền write/pay được cấp server-side. Every scoped ID có household check.
- Các input DTO `extra=forbid`; frontend không thể ép nguồn OCR/PROVIDER_API hay household_id trong chat. Data source trong domain hỗ trợ tương lai, endpoint V1 chỉ manual.
- Rate limit login/register/refresh: 20 request/phút/IP, memory trong một worker. Cần shared limiter khi scale. Không tin X-Forwarded-For mặc định.
- CORS một origin theo cấu hình. Refresh kiểm tra Origin. Cần HTTPS/reverse proxy và CSP phù hợp khi triển khai public.
- Error production không traceback. Không log exception text chứa SQL params, không log password/JWT/API key. Audit chỉ metadata cần thiết.
- Billing/forecast dùng server computation, transaction rollback và unique constraints. Payment V1 chỉ manual self-report; không xác nhận ngân hàng.
- Notification dedupe bảo đảm retry không nhân bản sự kiện; báo cáo lỗi scheduler không bị nuốt.

## Trước production

Đây là đồ án V1. Cần email verification/reset, shared rate limiting, CSRF/XSS review, pagination, load tests, backup/restore, secret rotation, log retention, monitoring và kiểm thử integration/concurrency PostgreSQL sâu hơn. Không mở demo credentials ra public. Nội dung AI offline không thay thế hóa đơn chính thức.
