# Quy định về Phân Quyền và Ngữ Cảnh Người Dùng (Authorization & Context)

1. **Nguồn Định danh Duy nhất**: Mã hộ gia đình (`household_id`) và mã người dùng (`user_id`) chỉ được lấy duy nhất từ đối tượng `AgentContext` bất biến do Backend tạo ra sau khi xác thực token (Authentication).
2. **Cách Ly Ngữ Cảnh Chat**:
   - Tuyệt đối không tin tưởng, không trích xuất và không sử dụng `household_id` hay `user_id` từ nội dung câu hỏi người dùng, tài liệu tải lên hoặc phản hồi từ các bên thứ ba.
   - Không cho phép người dùng thay đổi hoặc yêu cầu truy vấn dữ liệu của hộ gia đình khác bằng cách truyền ID trực tiếp trong prompt.
3. **Kiểm tra Quyền Truy Cập (Membership Check)**: Mọi công cụ (tool) thực thi đều phải xác minh quyền thành viên hiện hành của người dùng đối với hộ gia đình được truy vấn.
