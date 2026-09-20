# AI Agent: Rules / Skills / Tools

## Luồng

Authentication → membership → AgentContext frozen → intent router → skill registry/allowlist → tools → HouseholdService → Repository → database. Agent và tools không import ORM hay thực thi SQL. Endpoint chỉ nhận message, context không nhận từ JSON frontend.

Context: user_id, household_id, membership role, immutable permissions tuple, timezone, locale và request_id. Agent kiểm tra lại membership/context khi thực thi. LLM không thể thay context.

## Rules

`core.md`, `authorization.md`, `privacy-security.md`, `grounding.md`, `actions.md`, `response.md` trong `backend/app/ai/rules/`. Runtime đọc rules và skill instructions. Luật an toàn được enforce bằng DTO strict, tool allowlist, service authorization, numeric services và dữ liệu allowlist; không chỉ dựa vào prompt.

## 9 skills

`household_overview`, `consumption_analysis`, `consumption_comparison`, `bill_analysis`, `bill_forecast`, `anomaly_detection`, `saving_recommendation`, `payment_assistant`, `explain_result`. Mỗi SKILL.md có Purpose, Trigger, Required/Optional Data, Procedure, Tool Usage, Rules, Output, Failure Cases và Examples.

## Tools

- `get_household_profile()` — chỉ profile tối thiểu; không tên/địa chỉ tùy ý trong LLM evidence.
- `get_consumption_history()`, `get_latest_consumption()`.
- `get_bill_history()`, `get_current_bill()`.
- `get_tariff()`.
- `get_payment_status()`.
- `get_upcoming_notifications()` — metadata tối thiểu, không đưa text tùy ý làm instruction.

Tất cả tool nhận service đã gắn authenticated user; không nhận arbitrary house_id. V1 không có tool ghi. Payment assistant chỉ hướng dẫn sang bill UI.

## Deterministic analysis

- Forecast: trung bình trọng số 1..N, tối đa 3 kỳ, ít nhất 2 kỳ; tiền qua BillingService. Tin cậy low/medium là heuristic, không phải khoảng tin cậy thống kê.
- Anomaly: tăng trên 30% so với trung bình tối đa 3 kỳ trước; ít nhất 2 kỳ. Baseline 0 không chia cho 0 và báo chưa tính được phần trăm.
- Billing: Decimal theo tiers DB; LLM không quyết định tiền.
- Router V1: keyword tiếng Việt đã normalize, không phải semantic LLM router. Câu phức tạp có thể chọn sai intent.
- Provider mặc định deterministic tạo câu trả lời mẫu từ evidence. `LLMProvider` ABC + provider registry sẵn để thêm adapter, chưa tích hợp mạng. Provider không hỗ trợ trả 503, không âm thầm fallback.

## Grounding / security

Nguồn MANUAL được giữ nguyên; bill SYSTEM_ESTIMATE không gọi là hóa đơn nhà cung cấp. Dự báo ghi FORECAST và “ước tính”. Ngày due_day cấu hình phân biệt với official due_date. Không kết luận thiết bị là nguyên nhân. Retrieved data không chạy như instructions. Redaction phòng thủ loại secret-like keys, JWT, API keys, DB URI; không coi regex là lớp bảo mật duy nhất.

Không lưu chat prompt, raw sensitive data hoặc chain-of-thought. `ai_analyses` chỉ lưu intent/model/trạng thái/số nguồn. Output gồm message, intent, citations period/source, request metadata.
