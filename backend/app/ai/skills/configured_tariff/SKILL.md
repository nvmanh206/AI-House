# configured_tariff
## Purpose
Đọc biểu giá cấu hình của hộ hiện tại khi người dùng hỏi hoặc khi tra web thất bại.
## Trigger
Biểu giá trong hệ thống, biểu giá đã lưu, giá demo. Public search thiếu bằng chứng/quota/timeout cũng có thể gọi fallback này.
## Required Data
Trusted household context và tariffs_for_agent từ service đã authorize.
## Optional Data
Không dùng dữ liệu hộ khác để thay chỗ trống.
## Procedure
Đọc tên, provider, phiên bản, ngày hiệu lực ghi trong hệ thống và các tiers. Ghi rõ CONFIGURED chưa xác minh giá chính thức; tên/version có demo thì gắn nhãn demo. Không thay tariff/bill.
## Tool Usage
configured_tariff_text → HouseholdService.tariffs_for_agent → Repository.
## Rules
Không coi biểu giá hộ hiện tại là giá chính thức của địa phương trong câu hỏi. Fallback vẫn grounded=false, giữ error_code để audit. Không gọi thêm Gemini để đoán giá khi Search lỗi.
## Output
Văn bản có nhãn nguồn cấu hình, ngày, đơn vị; metadata configured_tariffs, không sources web.
## Failure Cases
Chưa có tariff phù hợp: nói thiếu, hướng dẫn admin thêm biểu giá có nguồn.
## Examples
“Biểu giá điện trong hệ thống” → đọc biểu giá đã lưu, không gọi Search.
