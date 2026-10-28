# Kiến trúc và dữ liệu

Trạng thái: chuẩn hóa 2026-10-29 từ yêu cầu/code hiện có; không chứng minh mọi phiên trước đều tuân thủ. Phạm vi: agent hỗ trợ phát triển.

1. Giữ ranh giới controller/service/persistence hiện có. Phân quyền user/hộ/admin ở backend; không tin ID trong câu chat hay do AI trả về.
2. PostgreSQL nghiệp vụ giữ chỉ số/hóa đơn/thanh toán; RAG chỉ giữ tri thức công khai, không embedding dữ liệu riêng vào kho chung.
3. Code tính tiền và xác minh, Gemini diễn đạt. Chat/đọc ảnh không tự ghi chỉ số, hóa đơn hoặc xác nhận thanh toán.
4. Thay đổi schema có migration; bảo toàn volume. Không mặc định database trên máy khác giống máy tác giả.

## Căn cứ

- `backend/app/ai/multimodal.py`
- `backend/app/knowledge/store.py`
- `docker-compose.yml`
