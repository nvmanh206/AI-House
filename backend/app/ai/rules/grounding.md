# Quy định về Nguồn Gốc và Phân Loại Dữ Liệu (Data Grounding & Provenance)

1. **Phân Loại Nhãn Nguồn Dữ Liệu**:
   - `ACTUAL`: Dữ liệu chỉ số/hóa đơn chính thức đã được hệ thống xác nhận.
   - `MANUAL`: Dữ liệu do người dùng tự nhập thủ công (mang tính tham khảo cá nhân).
   - `OCR`: Dữ liệu trích xuất tự động từ hình ảnh/hóa đơn (cần kiểm tra xác nhận).
   - `PROVIDER_API`: Dữ liệu đồng bộ trực tiếp từ nhà cung cấp dịch vụ (EVN, công ty cấp nước).
   - `ESTIMATED`: Giá trị ước tính tính toán từ biểu giá quy định.
   - `FORECAST`: Giá trị dự báo chỉ số hoặc chi phí trong tương lai.
2. **Xử Lý Dữ Liệu Tự Nhập (`MANUAL`)**: Dữ liệu do người dùng tự nhập không bao giờ tự động chuyển thành số liệu chính thức của hệ thống nếu chưa qua xác minh.
3. **Xử Lý Hạn Thanh Toán**: Ngày cấu hình nhắc nợ của hộ gia đình (`due_day`) không phải hạn chót pháp lý. Luôn sử dụng `due_date` chính thức ghi trên hóa đơn kèm theo nhãn nguồn dữ liệu tương ứng.
