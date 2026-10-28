# Coding conventions

Trạng thái: chuẩn hóa 2026-10-29 từ yêu cầu/code hiện có; không chứng minh mọi phiên trước đều tuân thủ. Phạm vi: agent hỗ trợ phát triển.

1. Đọc caller, schema và tests trước khi sửa. Giữ phong cách code và hợp đồng API hiện có; ưu tiên thay đổi nhỏ đủ giải quyết vấn đề.
2. Frontend TypeScript/React; backend FastAPI/Pydantic/SQLAlchemy. Đầu vào qua schema; lỗi có mã/thông báo, không nuốt lỗi thành thành công.
3. Dùng Decimal cho tiền/chỉ số ở backend; giữ null khác 0, kiểm tra ngày/kỳ/đơn vị trước khi hiển thị.
4. UI tiếng Việt, kWh/m³/VND rõ ràng. Runtime không chèn số liệu hộ mẫu; fixture dùng trong môi trường test tách biệt.

## Căn cứ

- `backend/app/schemas.py`
- `backend/app/billing_service.py`
