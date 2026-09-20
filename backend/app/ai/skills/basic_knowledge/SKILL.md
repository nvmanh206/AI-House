# basic_knowledge
## Purpose
Giải thích kiến thức phổ thông không phụ thuộc API Search hoặc dữ liệu hộ.
## Trigger
kWh là gì, cách đọc công tơ, cách tính bậc thang, cách tiết kiệm.
## Required Data
Nội dung câu hỏi; membership được xác thực ở Agent.
## Optional Data
Không cần chỉ số, hóa đơn hay dữ liệu mạng.
## Procedure
Chọn lời giải thích cố định trong basic_explanation. Câu hỏi yêu cầu giá mới nhất chuyển public_tariff, không dùng kiến thức chung làm giá hiện hành.
## Tool Usage
basic_explanation trong tools/knowledge.py; không SQL, không gọi LLM/Search.
## Rules
Không khẳng định đơn giá/thuế hiện hành, không khẳng định thiết bị cụ thể tiêu thụ nhiều.
## Output
Tiếng Việt, nhãn kiến thức chung, không nguồn web giả.
## Failure Cases
Chủ đề chưa có đáp án cố định được route sang general_chat; không báo cần nhập chỉ số cho câu hỏi khái niệm.
## Examples
“kWh là gì?” → giải thích đơn vị kWh và công suất × thời gian.
