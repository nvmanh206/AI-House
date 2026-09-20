# public_tariff
## Purpose
Tra cứu biểu giá điện/nước công khai với Gemini Google Search.
## Trigger
Tra cứu biểu giá điện/nước, số bậc, VAT, ngày hiệu lực, biến động giá. Không phụ thuộc lịch sử hóa đơn. Không route cho câu hỏi tính toán tiền/hóa đơn cá nhân cụ thể (ví dụ: "350 kWh hết bao nhiêu").
## Supported Intents & Queries
- CURRENT_TARIFF: giá điện/nước hiện tại
- HISTORICAL_TARIFF: biểu giá thời điểm quá khứ (ví dụ: tháng 8/2025)
- TARIFF_STRUCTURE: cấu trúc biểu giá, số bậc
- TARIFF_CHANGE: biến động, điều chỉnh giá
- VAT_INFORMATION: thông tin thuế VAT
- EFFECTIVE_DATE: ngày áp dụng, ngày hiệu lực
## Extracted Arguments
- utility: ELECTRICITY | WATER
- location: Tỉnh/thành phố (bắt buộc đối với Nước; nếu câu hỏi Nước thiếu địa phương, phải yêu cầu người dùng cung cấp)
- customer_group: HOUSEHOLD | BUSINESS | PRODUCTION | OTHER | UNKNOWN
- target_date: Ngày cụ thể YYYY-MM-DD hoặc ngày hiện tại
- query_type: CURRENT_TARIFF | HISTORICAL_TARIFF | TARIFF_STRUCTURE | TARIFF_CHANGE | VAT_INFORMATION | EFFECTIVE_DATE
## Procedure
1. Kiểm tra membership server-side.
2. Trích xuất structured arguments từ câu hỏi người dùng.
3. Nếu utility == WATER và location == null, yêu cầu người dùng cung cấp địa phương: "Bạn muốn tra giá nước tại tỉnh/thành phố nào?" (không gọi Search).
4. Tạo canonical public question chuẩn hóa từ structured arguments (tuyệt đối không truyền thông tin cá nhân/hộ gia đình).
5. Gọi get_public_tariff → GeminiProvider.search_tariff với Google Search.
6. Kiểm tra grounding metadata: chỉ coi là grounded khi status 200, có text, HTTPS sources hợp lệ, groundingSupports, finishReason == STOP.
7. Nếu Search 429 hoặc thiếu bằng chứng grounding: trả thông báo chưa xác minh được, không đoán số và KHÔNG fallback về model memory đối với CURRENT_TARIFF.
8. Có thể bổ sung kiến thức cách tính và biểu giá LOCAL CONFIGURED từ đúng hộ qua service. Bắt buộc gắn nhãn chưa xác minh/demo và không phải giá địa phương được hỏi; giữ grounded=false/error_code, không tạo sources web và không gọi LLM đoán giá. Khi không có cấu hình thì nói rõ thiếu, không lấy biểu giá hộ khác.
## Tool Usage
get_public_tariff(service, **kwargs); chỉ đọc. Không có SQL hoặc write tool.
## Rules
Tuân thủ privacy/grounding rules. Nguồn web công khai phải trích dẫn; không ghi đè biểu giá trong DB. Không kết luận giá là hiện hành chỉ dựa vào ngày đăng.
## Output
Tiếng Việt, ngắn gọn, có trích dẫn [1], [2] nếu có nguồn. Trả về metadata và sources loại web.
