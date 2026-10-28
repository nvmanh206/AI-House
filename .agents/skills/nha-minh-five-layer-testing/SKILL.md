---
name: nha-minh-five-layer-testing
description: Use when verifying UI, API, server, system or data transforms in Nha Minh.
---

# Kiểm thử 5 tầng

Trạng thái: **PROPOSED** — workflow dự án tự soạn, chuẩn hóa 2026-10-29; không phải bản sao skill ngoài, không khẳng định đã dùng trong quá khứ.

## Quy trình

1. Đọc docs/sdlc/SDLC-TEST-STRATEGY.md; tạo ca từ acceptance criteria, đánh dấu tầng và mock/live.
2. UI: dữ liệu/trạng thái/thao tác; API: schema/quyền; server: nghiệp vụ/transaction/hộ; system: chuỗi dịch vụ thật; transform: Decimal/null/0/ngày/đơn vị.
3. Dùng DB/tài khoản test riêng, kiểm tra trước/sau để chứng minh chat không thay đổi dữ liệu nghiệp vụ.
4. Ghi pass/fail/skipped/not-run cùng lệnh và căn cứ; không dùng một tầng thay cho cả năm.

Đường dẫn tham chiếu tính từ gốc repo. Xem .agents/rules/README.md. Mỗi lần dùng trong tương lai cần ghi kết quả riêng; SKILL.md không phải log thực thi.
