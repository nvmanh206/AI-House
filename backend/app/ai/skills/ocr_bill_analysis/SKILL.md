# Skill: OCR Bill Analysis (Trích xuất & Phân tích Hóa đơn OCR)

## Mục đích
Hỗ trợ người dùng trích xuất dữ liệu hóa đơn điện/nước từ ảnh upload hoặc văn bản OCR, đối soát với dữ liệu công tơ của hộ gia đình, cảnh báo các điểm bất thường và dự báo chi phí kỳ tiếp theo.

## Các bước thực thi
1. Trích xuất thông tin hóa đơn bằng công cụ `analyze_bill_ocr`.
2. Kiểm tra tính trùng khớp của mã khách hàng và chỉ số công tơ.
3. So sánh mức tiêu thụ hiện tại với trung bình 3-6 kỳ lịch sử của hộ.
4. Cảnh báo nếu tiêu thụ tăng đột biến (>30%, >50%, >100%) hoặc số tiền hóa đơn không khớp với biểu giá hệ thống.
5. Đưa ra dự báo mức tiêu thụ và chi phí cho kỳ tiếp theo.
6. Trả lời linh hoạt theo đúng trọng tâm câu hỏi của người dùng.
