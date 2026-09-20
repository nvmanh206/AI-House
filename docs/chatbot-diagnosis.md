# Kiểm tra luồng Gemini (07/09/2026)

## Cập nhật phản hồi khi thiếu Search/dữ liệu

- Basic knowledge: kWh, đọc công tơ, cách tính bậc thang, tiết kiệm có đáp án local; không yêu cầu readings hay gọi Google.
- Search quota/timeout/thiếu nguồn: giữ grounded=false và error_code; bổ sung giải thích chung và biểu giá CONFIGURED của đúng hộ nếu có, nêu tên/phiên bản/ngày hiệu lực. Giá demo được gắn nhãn rõ, không coi là giá hiện hành ở địa phương hỏi. Không tạo nguồn web giả hoặc gọi Gemini đoán giá.
- Có thể hỏi “biểu giá điện trong hệ thống” để đọc cấu hình mà không tra Search.
- Dự báo thiếu dữ liệu nói rõ đang có 0/1 kỳ, cần thêm bao nhiêu kỳ, hướng dẫn chọn đúng hộ và nhập chỉ số. Không tự tạo số tiền.
- 55 tests backend PASS (2 cảnh báo deprecation test client), gồm regression bảo mật và các fallback. Quota thực của Google vẫn cần được giải quyết ở project Google; không tuyên bố đã khôi phục tra cứu online.

## Nguyên nhân xác nhận được

- a.py dùng gemini-3.6-flash và chỉ gửi contents, không có google_search.
- Backend trước sửa dùng gemini-3.5-flash. Đã đổi GEMINI_MODEL trong .env local sang gemini-3.6-flash; giữ nguyên API key.
- Probe thực: chat gemini-3.5-flash trả 200; Search trên cả 3.5-flash và 3.6-flash trả 429 RESOURCE_EXHAUSTED. Vì vậy key dùng được cho chat nhưng Search đang bị giới hạn; đổi model không giải quyết được Search trong lần thử này.
- Router mặc định household_overview cho mọi câu không khớp: câu giới thiệu/hỗ trợ bị hiểu sai thành câu truy vấn household chưa có readings.

## Sửa

- assistant_identity trả lời giới thiệu; general_chat gọi Gemini thật, không Search/DB context; nghiệp vụ vẫn dùng các services deterministic.
- public_tariff nhận câu “giúp/xem điện nước …”, tách câu hỏi hai tiện ích thành yêu cầu chọn điện/nước, giữ location do user nêu.
- Registry khai báo public_tariff và general_chat; nội dung SKILL.md được nạp khi gọi Gemini. General skill có danh sách tính năng thực để không hướng dẫn OCR chưa được triển khai.
- Search 429 có error_code GEMINI_SEARCH_QUOTA, giải thích quota riêng; không fallback sang giá model nhớ, không ghi tariff/bill.
- Monitor ghi Search quota là lỗi, không ghi thành success. Bỏ log/raw Google error text để tránh lộ dữ liệu.
- Backend khởi chạy lại ở localhost:8000, nhận cấu hình model mới.

## Kiểm chứng

Pytest regression toàn bộ backend, cộng kiểm tra HTTP live qua login → chat identity → hỏi điện/nước Thái Nguyên → Gemini general_chat → Search tariff. General chat model 3.6-flash trả 200; Search vẫn 429.

## Giới hạn còn lại

Không thể làm Search hoạt động khi quota dự án Google không cho phép. Kiểm tra Google AI Studio → project chứa API key → Usage/Rate limits và billing theo cấu hình tài khoản; không mặc định đổi key hoặc đổi model sẽ tăng quota. Không tuyên bố tra giá hiện hành thành công khi chưa có grounding.

Chat vẫn là từng câu độc lập, chưa có lịch sử hội thoại gửi về backend. Khi được hỏi chọn điện/nước, nên hỏi lại đầy đủ “giá điện Thái Nguyên” hoặc “giá nước Thái Nguyên”.
