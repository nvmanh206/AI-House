---
id: OPT-003
status: PROPOSED
collected_on: 2026-10-29
---

# Prompt rà soát bảo mật — đề xuất bổ sung

**Mục đích:** dùng cho lần review bảo mật tiếp theo. **Nguồn:** mới soạn khi chuẩn hóa, không phải prompt lịch sử. **Công cụ dự kiến:** agent tương thích, chưa thực thi prompt này.

## Nội dung

Đọc code hiện tại và truy vết quyền user/hộ/admin, bí mật cấu hình và đường tải tài liệu RAG. Chỉ báo finding có đường dữ liệu và bằng chứng file/test. Đề xuất sửa nhỏ có kiểm chứng; không in secret, không sửa dữ liệu thật và không ghi đã an toàn nếu chưa xác minh.

## Đầu ra dự kiến

Findings có source/sink, mức ảnh hưởng, test và giới hạn. **Kết quả thực hiện:** chưa có; không dùng file này làm bằng chứng đã audit toàn hệ thống.
