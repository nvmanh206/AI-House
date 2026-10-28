---
name: nha-minh-implementation
description: Use when implementing or fixing frontend, backend, database or Gemini integration in Nha Minh.
---

# Triển khai có kiểm chứng

Trạng thái: **PROPOSED** — workflow dự án tự soạn, chuẩn hóa 2026-10-29; không phải bản sao skill ngoài, không khẳng định đã dùng trong quá khứ.

## Quy trình

1. Đọc rule coding/architecture cùng caller/test ở vùng sửa.
2. Tái hiện lỗi hoặc chốt input/output của tính năng từ yêu cầu trước khi sửa.
3. Sửa nhỏ nhất đủ hoàn thành, giữ Decimal, phân quyền, migration và fixture test tách biệt.
4. Chạy kiểm tra liên quan, xem diff và ghi nhật ký. Đầu ra: thay đổi, lệnh/kết quả và rủi ro.

Đường dẫn tham chiếu tính từ gốc repo. Xem .agents/rules/README.md. Mỗi lần dùng trong tương lai cần ghi kết quả riêng; SKILL.md không phải log thực thi.
