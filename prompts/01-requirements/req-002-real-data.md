---
id: REQ-002
status: EXACT_EXCERPT
collected_on: 2026-10-29
---

# Dữ liệu thật và PostgreSQL

**Mục đích:** Lưu ràng buộc dữ liệu và công cụ database.

**Nguồn:** thông điệp người dùng trong ngữ cảnh hội thoại; trích đoạn `C-REQ-002` tại `../sources/user-excerpts.json`. Ngày gửi gốc chưa xác định; không phải bản export đầy đủ được ký xác thực.

**Công cụ:** Codex trong phiên hội thoại; không xác định chính xác mô hình/lượt gốc. Các công cụ như Gemini/Docker trong yêu cầu là tích hợp hoặc thực thi, không suy ra coding agent khác.

## Nội dung yêu cầu được giữ lại

````text
toàn bộ . lưu ý mình cần xử lí với dữ liệu thật không có hardcode
sử dụng postgresql và pgadmin để làm giao diện hiển thị database
````

## Sản phẩm liên quan đã tìm thấy

- [docker-compose.yml](../../docker-compose.yml)
- [backend/app/db.py](../../backend/app/db.py)
- [backend/app/billing_service.py](../../backend/app/billing_service.py)

## Kiểm tra liên quan

- [backend/tests/test_docker_bootstrap.py](../../backend/tests/test_docker_bootstrap.py)

**Giới hạn:** Runtime dùng PostgreSQL; test có fixture riêng là hợp lệ. Không suy diễn rằng mọi số ví dụ hoặc fixture đều bị cấm.

Mốc sản phẩm trước tổng hợp: `dc19327`; không khẳng định một lượt AI tạo toàn bộ các file liên kết.
