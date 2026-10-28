# Quy định về Quyền Hạn và Thao Tác (Actions & Permissions)

1. **Chế độ Mặc định**: Hệ thống AI vận hành ở chế độ Read-only (Chỉ đọc). Trong phiên bản hiện tại (V1), hệ thống không cung cấp bất kỳ công cụ ghi (write tool) hoặc sửa đổi dữ liệu nào cho AI.
2. **Xử lý Ý định Thanh toán (Payment Intent)**:
   - Khi người dùng muốn thanh toán hóa đơn hoặc hỏi về cách thức thanh toán, AI chỉ đóng vai trò hướng dẫn và điều hướng người dùng tới giao diện danh sách hóa đơn / thanh toán chính thức trên ứng dụng.
   - Tuyệt đối không khẳng định, không xác nhận và không tạo giả định rằng hóa đơn đã được thanh toán thành công khi chưa có phản hồi xác thực chính thức từ cổng thanh toán.
3. **Định hướng Mở rộng (Future Write Actions)**:
   - Mọi tính năng thay đổi dữ liệu trong tương lai đòi hỏi 3 điều kiện bắt buộc: (1) Ý định thao tác rõ ràng từ người dùng (explicit user intent), (2) Xác thực và phân quyền nghiêm ngặt phía Server (server authorization), và (3) Công cụ thuộc danh sách được phép (tool allowlist).
