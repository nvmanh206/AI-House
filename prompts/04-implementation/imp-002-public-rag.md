---
id: IMP-002
status: EXACT_EXCERPT
collected_on: 2026-10-29
---

# RAG tri thức điện nước

**Mục đích:** Tích hợp crawler, embedding, PostgreSQL và câu trả lời có nguồn.

**Nguồn:** thông điệp người dùng trong ngữ cảnh hội thoại; trích đoạn `C-IMP-002` tại `../sources/user-excerpts.json`. Ngày gửi gốc chưa xác định; không phải bản export đầy đủ được ký xác thực.

**Công cụ:** Codex trong phiên hội thoại; không xác định chính xác mô hình/lượt gốc. Các công cụ như Gemini/Docker trong yêu cầu là tích hợp hoặc thực thi, không suy ra coding agent khác.

## Nội dung yêu cầu được giữ lại

````text
Nguồn chính thức → crawler → kiểm tra và lưu phiên bản → tạo embedding → PostgreSQL RAG → truy xuất tài liệu liên quan → Gemini trả lời tự nhiên kèm nguồn.
````

## Sản phẩm liên quan đã tìm thấy

- [backend/app/knowledge/service.py](../../backend/app/knowledge/service.py)
- [backend/app/knowledge/crawler.py](../../backend/app/knowledge/crawler.py)
- [backend/app/knowledge/embedding.py](../../backend/app/knowledge/embedding.py)
- [backend/app/knowledge/migrations/001.sql](../../backend/app/knowledge/migrations/001.sql)
- [frontend/components/knowledge-admin.tsx](../../frontend/components/knowledge-admin.tsx)

## Kiểm tra liên quan

- [backend/tests/test_knowledge.py](../../backend/tests/test_knowledge.py)
- [backend/tests/test_water_knowledge.py](../../backend/tests/test_water_knowledge.py)

**Giới hạn:** Trích câu luồng chính trong kế hoạch RAG. Bộ 50 câu hỏi/top-5 90% trong kế hoạch chưa có bằng chứng đã nghiệm thu đủ; không biến thành kết quả đạt.

Mốc sản phẩm trước tổng hợp: `dc19327`; không khẳng định một lượt AI tạo toàn bộ các file liên kết.
