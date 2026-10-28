---
name: nha-minh-security-optimization
description: Use when reviewing tenant isolation, crawler safety, Gemini quota or performance in Nha Minh.
---

# Bảo mật và tối ưu có đo lường

Trạng thái: **PROPOSED** — workflow dự án tự soạn, chuẩn hóa 2026-10-29; không phải bản sao skill ngoài, không khẳng định đã dùng trong quá khứ.

## Quy trình

1. Xác định vấn đề qua latency/log/quota hoặc đường dữ liệu cụ thể; không tối ưu theo phỏng đoán.
2. Kiểm tra quyền hộ/admin, secret, SSRF/redirect/TLS và prompt injection. Không in secret làm minh chứng.
3. Với AI, đo số lần gọi/ngữ cảnh/cache; không tạo fallback giả hoặc áp giá sai địa phương.
4. Đề xuất thay đổi hẹp, đo lại và kiểm tra hồi quy. Không ghi tiết kiệm % nếu chưa đo.

Đường dẫn tham chiếu tính từ gốc repo. Xem .agents/rules/README.md. Mỗi lần dùng trong tương lai cần ghi kết quả riêng; SKILL.md không phải log thực thi.
