---
id: DEP-001
status: EXACT_EXCERPT
collected_on: 2026-10-29
---

# Clone rồi chạy Docker

**Mục đích:** Tự khởi tạo hạ tầng và dữ liệu bền vững.

**Nguồn:** thông điệp người dùng trong ngữ cảnh hội thoại; trích đoạn `C-DEP-001` tại `../sources/user-excerpts.json`. Ngày gửi gốc chưa xác định; không phải bản export đầy đủ được ký xác thực.

**Công cụ:** Codex trong phiên hội thoại; không xác định chính xác mô hình/lượt gốc. Các công cụ như Gemini/Docker trong yêu cầu là tích hợp hoặc thực thi, không suy ra coding agent khác.

## Nội dung yêu cầu được giữ lại

````text
mình cần cấu hình tự động hoàn toàn để khi push lên git thành viên khác clone về chỉ cần chạy lệnh docker là có thể sử dụng như bình thường được
và quan trọng phải clean được project khi push lên git
````

## Sản phẩm liên quan đã tìm thấy

- [docker-compose.yml](../../docker-compose.yml)
- [backend/app/container_start.py](../../backend/app/container_start.py)
- [backend/app/bootstrap.py](../../backend/app/bootstrap.py)
- [deploy/pgadmin.servers.json](../../deploy/pgadmin.servers.json)
- [DOCKER_GUIDE.md](../../DOCKER_GUIDE.md)

## Kiểm tra liên quan

- [backend/tests/test_docker_bootstrap.py](../../backend/tests/test_docker_bootstrap.py)

**Giới hạn:** Dữ liệu máy tác giả không đi theo Git. Gemini cần key riêng; bootstrap nguồn không đồng nghĩa đã có nội dung RAG. Lượt test clone/volume được ghi trong nhật ký, không có raw transcript công khai.

Mốc sản phẩm trước tổng hợp: `dc19327`; không khẳng định một lượt AI tạo toàn bộ các file liên kết.
