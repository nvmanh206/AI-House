---
name: nha-minh-documentation-evidence
description: Use when recording prompts, skills, provenance or implementation evidence for Nha Minh.
---

# Tài liệu và minh chứng AI

Trạng thái: **PROPOSED** — workflow dự án tự soạn, chuẩn hóa 2026-10-29; không phải bản sao skill ngoài, không khẳng định đã dùng trong quá khứ.

## Quy trình

1. Đọc AI_DEVELOPMENT.md và nguồn Git/file/hội thoại thực có; cài skill không đồng nghĩa đã chạy.
2. Ghi source_kind, mức nguyên văn, ngày tổng hợp, đầu ra và giới hạn; tái dựng ghi RECONSTRUCTED, chưa dùng ghi PROPOSED.
3. Cập nhật prompts/manifest.json, giữ liên kết và hash; không sao chép .local hoặc toàn bộ chat riêng.
4. Chạy scripts/check_ai_evidence.py và scripts/repo_audit.py. Kết quả cũ không được biến thành nghiệm thu mới.

Đường dẫn tham chiếu tính từ gốc repo. Xem .agents/rules/README.md. Mỗi lần dùng trong tương lai cần ghi kết quả riêng; SKILL.md không phải log thực thi.
