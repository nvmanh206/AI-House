---
id: DEP-002
status: EXACT_EXCERPT
collected_on: 2026-10-29
---

# Làm sạch và push website

**Mục đích:** Lưu yêu cầu công bố code đã lọc.

**Nguồn:** thông điệp người dùng trong ngữ cảnh hội thoại; trích đoạn `C-DEP-002` tại `../sources/user-excerpts.json`. Ngày gửi gốc chưa xác định; không phải bản export đầy đủ được ký xác thực.

**Công cụ:** Codex trong phiên hội thoại; không xác định chính xác mô hình/lượt gốc. Các công cụ như Gemini/Docker trong yêu cầu là tích hợp hoặc thực thi, không suy ra coding agent khác.

## Nội dung yêu cầu được giữ lại

````text
mình cần push /website lên repo này
nhưng phải clean chỉ push những gì liên quan đến project
tránh đẩy rác lên
````

## Sản phẩm liên quan đã tìm thấy

- [.gitignore](../../.gitignore)
- [scripts/repo_audit.py](../../scripts/repo_audit.py)
- [IMPLEMENTATION_PROGRESS.md](../../IMPLEMENTATION_PROGRESS.md)

## Kiểm tra liên quan

Không có kết quả test độc lập gắn trực tiếp với prompt này. Xem nhật ký và diff liên quan.

**Giới hạn:** Commit ab8fc26 loại file local/agent thừa. Không chép key cũ vào bằng chứng; xóa ở tip không xóa lịch sử Git. Bản tổng hợp này chỉ cho phép .agents đã chọn lọc.

Mốc sản phẩm trước tổng hợp: `dc19327`; không khẳng định một lượt AI tạo toàn bộ các file liên kết.
