---
name: nha-minh-sdlc-diagrams
description: Use when deriving UML, ERD, DFD, flowchart or architecture diagrams from Nha Minh requirements and code.
---

# Sơ đồ SDLC có căn cứ

Trạng thái: PROPOSED, tự chuẩn hóa 29/10/2026; không phải skill lịch sử đã được chứng minh chạy.

1. Chọn as-is (code) hoặc as-designed (yêu cầu); ghi revision/phạm vi/giả định, không trộn hai view trong kết luận.
2. Chọn sơ đồ theo mục tiêu: Use Case (actor/mục tiêu), Activity/Flowchart (nhánh), Sequence (lời gọi), Class (trách nhiệm), ERD (bảng/khóa), DFD (luồng/kho dữ liệu), Architecture (ranh giới), State (vòng đời), Deployment (container/volume).
3. Đọc routes/services/schema/ORM/migration/tests; gắn thành phần chính với căn cứ. Chức năng chỉ có trong SRS phải ghi dự kiến.
4. Use Case: actor ngoài boundary; include từ ca bao gồm tới ca dùng chung, extend từ ca mở rộng tới ca nền. Không dùng include/extend cho thứ tự màn hình hay mặc định include Login.
5. ERD ghi PK/FK/cardinality từ schema; Class không mặc định là bảng. DFD thể hiện luồng dữ liệu, không dùng thay Sequence.
6. Lưu nguồn sửa được .puml/.mmd/.drawio; render SVG/PNG khi có công cụ. Ghi lỗi syntax/thiếu renderer; chỉ nói đã kiểm tra hình nếu thực sự mở xem.
7. Đầu ra: source, export, traceability và giới hạn. Báo cáo cũ không thay kiểm tra lại theo code mới.
