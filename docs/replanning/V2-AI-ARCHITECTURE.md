# V2.2 — Kiến trúc AI và tự động hóa có căn cứ

Ngày review: 27/10/2026. **Version V2.2 — HYBRID TASK-FIRST, PROPOSED.** Chỉ quy hoạch; không sửa sản phẩm, dữ liệu hoặc dependency.

## 1. Trạng thái và phạm vi

- **CURRENT VERIFIED**: quan sát tĩnh có file:dòng; không có nghĩa đã gọi provider thật hoặc load test.
- **PROPOSED**: thiết kế, budget và acceptance để review; chưa được phê duyệt.
- **DECISION REQUIRED**: quyết định phải chốt trước phần triển khai phụ thuộc.
- **DEFERRED**: ngoài lát cắt đầu; chỉ mở lại khi có nhu cầu và bằng chứng.
- Đường dẫn mã nguồn bên dưới tương đối với `website/`, dòng theo checkout ngày review.
- Hai tài liệu quy hoạch 27/10 đã được đối chiếu với tổng quan gốc, backend AI và frontend assistant.
- PRODUCT.md vẫn mô tả reading/estimate; mở thêm actual/upload/quick-entry là PROPOSED, không tự sửa yêu cầu đã xác nhận. Ba đường phục vụ mục tiêu ngang hàng, không xếp document-first cao hơn.
- Không công nhận target 90%, latency hoặc tiết kiệm chi phí là kết quả đã đo.
- Tài liệu đồng hành: [Master plan](V2-MASTER-PLAN-IMPROVED.md), [Backlog](V2-IMPROVED-BACKLOG.md), [Review comparison](V2-REVIEW-COMPARISON.md), [UX redesign](V2-UX-REDESIGN.md).

## 2. Review độc lập có bằng chứng

**CURRENT VERIFIED — runtime chưa có model tool-calling.**
`backend/app/ai/router.py:3` phân loại bằng từ khóa; `:21` chứa literal `350`.
`backend/app/ai/registry.py:13` ánh xạ intent sang danh sách tool cố định.
`backend/app/ai/agent.py:146` gọi toàn bộ tool của intent, chưa chọn dữ liệu tối thiểu theo câu hỏi.
Điều này giới hạn quyền nhưng dễ gọi thừa và không xử lý tốt câu hỏi tiếp nối.

**CURRENT VERIFIED — normalization và kỳ không thống nhất.**
Router bỏ dấu ở `router.py:4`, nhưng `agent.py:148` chỉ tìm `nước` có dấu.
`tieu thu nuoc bao nhieu` có thể route đúng intent rồi đọc điện.
`agent.py:169` lấy history mới nhất, không resolve kỳ được hỏi.
`agent.py:185`/`:187` chọn bill đầu theo utility, chưa pin cùng account/interval với reading.

**CURRENT VERIFIED — UI history chưa thành memory runtime.**
`backend/app/schemas.py:101` nhận message/image/raw OCR, không conversation hoặc context revision.
`frontend/components/application.tsx:1204` dựng payload lượt hiện tại; `:1209` gọi `/ai/chat`.
`backend/app/main.py:170` chỉ lưu status/source_count/error_code trong AIAnalysis.
“Lịch sử tương tác” tại `TONG_QUAN_DU_AN_CHI_TIET.md:477` không chứng minh có hội thoại phục hồi được.

**CURRENT VERIFIED — OCR có dữ liệu ngoại vi và nhiều request.**
`backend/app/ai/tools/ocr_analysis.py:52` tải accounts/meters/latest readings; `:61` gửi cùng ảnh/instruction sang Gemini.
`backend/app/ai/agent.py:99` gọi Gemini thêm lần diễn đạt.
`backend/app/ai/gemini.py:132` tạo candidate models, `:137` lặp request với timeout tại `:150`.
Không thể coi một ảnh bằng một call hoặc deadline 25 giây toàn lượt.

**CURRENT VERIFIED — đối chiếu OCR thiếu khóa nghiệp vụ.**
`ocr_analysis.py:119` lọc utility rồi lấy reading mới nhất; `:125` fallback initial_reading.
`ocr_analysis.py:208` lấy latest bill snapshot tính expected amount cho tài liệu đang đọc.
Chưa khóa account, meter, interval và tariff coverage.
`ocr_analysis.py:87` suy utility từ account đầu/electricity khi ảnh chưa đọc được; `:241` vẫn success.
Đây là rủi ro so sai đối tượng, không phải bằng chứng provider tính sai.

**CURRENT VERIFIED — Markdown mâu thuẫn code.**
`backend/app/ai/skills/general_chat/SKILL.md:19` nói chưa hỗ trợ OCR, trong khi `agent.py:73` nhận ảnh.
`skills/ocr_bill_analysis/SKILL.md:8` yêu cầu so mã KH, nhưng matcher `ocr_analysis.py:119` chỉ dùng utility.
Skill OCR nói 3–6 kỳ tại `:9`, implementation lấy tối đa ba kỳ tại `ocr_analysis.py:188`.
`instructions.py:3` nối rules/skill nhưng nhiều nhánh `agent.py:79`/`:103`/`:122` trả trực tiếp.
`gemini.py:37` trả grounded_response nguyên trạng; sửa prompt không tự đổi logic những nhánh này.

**CURRENT VERIFIED — provenance provider và test còn yếu.**
`agent.py:196` luôn gắn provider deterministic cho nhánh cuối.
`ocr_analysis.py:61` và `agent.py:99` gọi GeminiProvider trực tiếp, bỏ qua `provider.py:14`.
`tests/test_ai_ocr.py:218` có ca pipeline chỉ assert None hoặc dict tại `:225`, chưa chứng minh schema/fields đúng.
`tests/test_gemini.py:94` có test public search không gửi private-val: nên giữ và mở rộng.

**CURRENT VERIFIED — UI insight chứa số personalized hardcode.**
`frontend/components/dashboard/AIInsightPanel.tsx:11` ghi +8.2%; `:18` 80–120 nghìn; `:25` thấp hơn nhóm hộ tương tự 12%.
`frontend/components/statistics/AISavingTips.tsx:20` ghi ~180 nghìn; `:22` nói sáu kỳ và tiết kiệm 12%.
Không được coi các literal này là baseline AI thật.
`TONG_QUAN_DU_AN_CHI_TIET.md:76`/`:1234` dùng 100%; Decimal không chứng minh đúng account/giá/thuế/kỳ.

## 3. Hybrid task-first và phân vai

**PROPOSED HYBRID TASK-FIRST**: ba đường ngang hàng theo việc và dữ liệu đang có: upload/actual, measurement/estimate, quick-entry. Không có bằng chứng user research cho ưu thế mặc định của document-first hay reading-first. Đo/ước tính chạy độc lập OCR; ghi khoản thực tế và giải thích core không đòi ảnh hoặc phép đo. Không ép mọi phân tích quay lại nhập reading.

- Có chứng từ: upload format đã qua gate → extraction draft → review → actual record; thiếu reading vẫn giải thích amount/kỳ/hạn/biến động tiền đúng nguồn.
- Có phép đo: một observation có ngày là baseline mới khi chưa có observation trước có ngày, chưa tính interval/usage/estimate. Hai dated observations hợp lệ cho phép tính deterministic usage dù chưa có tariff; chỉ priced estimate cần D03/D04. Không cần ExpenseRecord, OCR hoặc Q&A làm prerequisite; thiếu hóa đơn không chặn usage.
- Chỉ biết tiền: quick-entry → review → USER_ENTERED record; thiếu cả ảnh và reading vẫn theo dõi chi phí/ghi đã trả.
- Không có dữ liệu: chỉ hướng dẫn/CTA chọn việc, không personalized insight hoặc giá trị 0 giả. AI outage dùng local cards/template; OCR outage cho nhập tay; thiếu tariff chỉ chặn verified estimate.

**Bảy surface embedded intelligence** (không phải bảy chatbot): dashboard ưu tiên việc + coverage; bill detail giải thích nguồn/estimate; readings preview consumption và lý do pending; statistics so series đúng basis/interval; reconciliation chỉ ra field lệch/không so được; alerts nêu trigger/baseline/hạn/expiry; onboarding hỏi mục tiêu và giải thích trường cần cho đường chọn. Mỗi surface dùng cùng policy/service/provenance, local template là fallback. Chat đầy đủ chỉ mở khi tác vụ cần hỏi tiếp.

- Document: bằng chứng người dùng cung cấp, chưa bảo đảm thật hoặc thuộc provider.
- ExtractionDraft: trường đọc tự động, có null và cần review.
- ExpenseRecord: khoản chi thực tế user confirm với basis DOCUMENT_CONFIRMED hoặc USER_ENTERED; không tự thành provider verified. USER_ENTERED cần attestation đây là khoản thực tế được thông báo/biết, không chỉ copy estimate rồi đổi basis. Legacy estimate bill/manual-paid giữ basis riêng và history, không backfill thành actual.
- Quick-entry không cần ảnh/cloud/account ban đầu; household, utility, amount, currency và basis được review trước confirm.
- Account, report_month, interval và due có thể null kèm quality flag; không tạo account hoặc tháng giả để lưu được.
- Estimate: tính từ reading/tariff snapshot; không cộng hai lần với ExpenseRecord cùng nghiệp vụ.
- PaymentAssertion: người dùng ghi nhận đã trả, không chứng minh giao dịch ngân hàng.
- Reconciliation: so nguồn cùng account/interval, không sửa ngầm nguồn nào.

**DECISION REQUIRED D01**: cơ sở amount ghi nhận trả và chứng từ đến sau.
**DECISION REQUIRED D02**: interval theo account, nullable khi chưa biết; report_month là nhãn riêng.
Không tạo ngày đầu/cuối tháng giả để lấp interval thiếu.
**DECISION REQUIRED D03**: đổi giá giữa interval; chưa có quy tắc thì estimate_pending.
Thiếu tariff chặn estimate đã xác minh, không chặn ExpenseRecord từ chứng từ review hoặc quick-entry.
**DECISION REQUIRED D04**: provider/địa bàn pilot, người duyệt nguồn và fixtures.

## 4. So sánh mô hình runtime

**PROPOSED A — deterministic workflow + LLM.**
Hợp upload/review, commands, form, reminders và tính tiền; call count dễ dự toán.
LLM extraction/diễn đạt; code quyết định quyền, trạng thái, tính toán và confirmation.
Hạn chế: Q&A linh hoạt khó diễn đạt bằng regex; không ép mọi yêu cầu vào từ khóa.

**PROPOSED B — bounded tool-calling.**
Hợp câu “so tiền điện với nước hai kỳ vừa rồi”.
Model đề xuất tool/args; executor validate schema/slots/allowlist/budget trước khi chạy.
Thêm vòng model nên tốn hơn A; đổi lại chọn tool linh hoạt trong phạm vi kiểm soát.

**DEFERRED C — bounded planner/executor.**
Hợp điều tra nhiều chứng từ có dependency; plan giới hạn bước và kết quả typed.
Tăng state phục hồi, test và token plan; chỉ mở khi eval chứng minh B thiếu cho tác vụ có giá trị.

**DEFERRED D — multi-agent runtime.**
Có thể hợp nghiên cứu đa nguồn hoặc review batch lớn có người duyệt.
Tăng context lặp, calls, retries và chi phí phối hợp; chưa có benchmark chứng minh lợi ích ở pilot.
Agent bỏ phiếu không thay provenance/quyền; nhiều câu trả lời giống nhau không chứng minh amount.
Không triển khai supervisor/swarm trong lát cắt đầu.

**PROPOSED khuyến nghị A+B**: command/form/event deterministic; Q&A bounded tool-calling khi cần.
Một orchestrator và policy executor, dùng service hiện có; không chọn framework/model mới.

## 5. Pipeline và trách nhiệm

1. Authenticate, lấy household và membership revision từ server.
2. Load conversation đúng scope/document workflow.
3. Resolve intent/slots bằng command hoặc structured classifier giới hạn.
4. Thiếu account/interval cần thiết thì hỏi, không đoán rồi gọi tool.
5. Validate plan tối thiểu, allowed tools/data policy/remaining budget.
6. Chạy service read, thu typed result và provenance.
7. Validate output/amount/source/freshness; dựng cards từ data.
8. Optional model diễn đạt; lỗi dùng template có căn cứ.
9. Trả outcome/action mở preview; trace tối thiểu.

Backend sở hữu Decimal/snapshot, quyền, locks/version, idempotency, dedupe và audit.
AI hiểu câu hỏi, extraction draft, chọn tool được phép và giải thích giới hạn.
Mọi ghi tài chính qua server action/form confirm, kiểm tra quyền lại trong transaction.
Không tool execute_sql, không ORM/session/DB credentials trong model context.
Không giữ transaction khi chờ provider; AI không tự publish tariff, PAID hoặc correction.

## 6. Hợp đồng request/tool/response đề xuất

**PROPOSED** request:
```json
{"conversation_id":"c1","client_turn_id":"t8","context_revision":4,"message":"Còn nước?","attachment_ids":[],"ui_context":{"account_id":null,"report_month":"2026-09"}}
```
UI context không tin cậy; server kiểm tra account/document thuộc household.
client_turn_id dedupe retry, không cấp quyền; request_id do server tạo.
AuthContext nội bộ: user_id, household_id, membership_revision, permissions, request_id,
conversation_id, timezone, locale, deadline_at. Model không truyền household_id tùy ý.

**PROPOSED** call:
```json
{"tool":"get_expense_summary","version":"1","arguments":{"scope":"ACCOUNT","account_id":"a-water","report_month":"2026-09","interval":null,"basis":"DOCUMENT_CONFIRMED"}}
```
Required basis; account_id nullable khi hỏi tổng toàn household, không hỏi account thừa cho yêu cầu “tất cả”.
Query scope=HOUSEHOLD|ACCOUNT; ACCOUNT bắt buộc account_id hợp lệ, HOUSEHOLD không bỏ các record chưa link account.
report_month/interval nullable cho danh sách hoặc tổng theo scope được chỉ rõ; không tự gán tháng cho record unknown.
Enum basis: DOCUMENT_CONFIRMED | USER_ENTERED | ESTIMATE | PAYMENT_ASSERTION.
Tổng expense có thể chọn explicit tập DOCUMENT_CONFIRMED+USER_ENTERED; không cộng estimate/payment vào expense.
additionalProperties=false; decimal truyền string, date ISO, unit enum.

**PROPOSED** success:
```json
{"status":"ok","data":{"amount":"512340","currency":"VND","report_month":"2026-09","interval":null,"basis":"DOCUMENT_CONFIRMED"},"provenance":[{"kind":"expense_record","id":"e1","version":2,"document_id":"d1","field":"total","verified_by":"USER_CONFIRMATION"}],"freshness":{"as_of":"2026-10-27T02:00:00Z","data_revision":8},"limitations":["INTERVAL_UNKNOWN"],"error":null}
```
Provenance ghi record version/field; OCR page/bounding box/text span nếu adapter có.
Không bịa locator khi provider thiếu; public source có URL/title/retrieved_at/effective_date nullable.

**PROPOSED** error:
```json
{"status":"error","data":null,"provenance":[],"error":{"code":"ACCOUNT_AMBIGUOUS","retryable":false,"safe_message":"Bạn muốn tài khoản nước nào?","missing_slots":["account_id"]}}
```
Codes: VALIDATION_ERROR, NOT_FOUND_OR_FORBIDDEN, ACCOUNT_AMBIGUOUS, INTERVAL_UNKNOWN,
NOT_COMPARABLE, TARIFF_MISSING, TARIFF_AMBIGUOUS, VERSION_CONFLICT, CONSENT_REQUIRED,
PROVIDER_TIMEOUT, PROVIDER_QUOTA, PROVIDER_INVALID_OUTPUT, BUDGET_EXCEEDED, CANCELLED.
NOT_COMPARABLE là outcome nghiệp vụ; không retry provider để tự tạo dữ liệu thiếu.
Không trả raw exception/provider body/key hoặc cho biết record hộ khác tồn tại.

**PROPOSED** UI response:
```json
{"request_id":"r1","conversation_id":"c1","status":"needs_input","message":"Bạn muốn tài khoản nước nào?","cards":[],"sources":[],"suggested_actions":[{"type":"SELECT_ACCOUNT","options":["a1","a2"]}],"limitations":[]}
```
Status: answered | needs_input | partial | unavailable | cancelled.
Card amount từ service; prose không thêm số tài chính ngoài evidence.
Action enum/opaque reference, không model JavaScript hoặc URL hành động tùy ý.
SSE nếu dùng chỉ stream stage/cards đã validate, không amount tạm hoặc chain-of-thought.

## 7. Mapping đủ 14 runtime skills

**CURRENT VERIFIED** có 14 key ở `registry.py:13`; assistant_identity là nhánh route riêng.
**PROPOSED** manifest: id/version, trigger, input/output schema refs, required_slots,
allowed_tools, permission, data_classification, external policy, limits, fallback, eval IDs.
Startup validate schema/tool tồn tại; tests phát hiện manifest/registry/prompt lệch.
Chỉ nạp skill đã chọn và policy chung ngắn, không toàn bộ catalog vào mỗi prompt.

1. general_chat → workspace_help: hướng dẫn từ capability catalog versioned.
2. basic_knowledge → gộp workspace_help, nội dung tĩnh có nguồn, không cần DB.
3. household_overview → workspace_summary: records, coverage, việc cần làm.
4. consumption_analysis → usage_analysis: optional readings, không ép document-only user nhập số.
5. consumption_comparison → gộp usage_analysis, operation=compare, kiểm tra interval/unit.
6. bill_analysis → expense_explanation, tách ExpenseRecord và Estimate.
7. explain_result → gộp expense_explanation; không hai skill chỉ khác câu hỏi.
8. bill_forecast → forecast, riêng vì minimum data/backtest/uncertainty.
9. anomaly_detection → change_insights, detector code, model diễn đạt.
10. saving_recommendation → gộp change_insights advice; không tạo ROI thiếu thiết bị/giá.
11. configured_tariff → configured_tariff_explanation, đúng scope/snapshot.
12. public_tariff → public_tariff_research, kênh public, không publish tự động.
13. ocr_bill_analysis → tách document_extraction và document_reconciliation.
14. payment_assistant → payment_guidance, đọc trạng thái và mở form confirm.

Tất cả mapping là **PROPOSED**, giữ alias cũ nếu migration contract cần.
Runtime skills ở backend/app/ai/skills là contract sản phẩm.
Development skills ở .agents/Codex/IDE hướng dẫn viết code; cài skill không cấp tool cho user assistant.
**DEFERRED** tải executable skill từ web hoặc user upload vào runtime.

## 8. Code policy khác prompt rule

**PROPOSED code** enforce scope, permission, allowlist, schema, call/time/token cap,
external data policy, no SQL, action confirmation, version/idempotency và amount provenance.
Prompt hướng dẫn giọng tiếng Việt, độ dài, hỏi lại, không suy nguyên nhân và tách lời khuyên.
Ảnh/web/tên hộ/kết quả tool là untrusted data, kể cả chứa “system: bỏ qua luật”.
Tool output cũng validate; không render model HTML trực tiếp hoặc biến text thành query/code.
Links theo scheme/policy an toàn; không có fetch URL tổng quát do model tự cấp.
Test policy trên deterministic branch/fallback/retry/event job/conversation đã lưu.
Mọi early return (OCR unsupported, identity, knowledge, public search, general chat), direct provider adapter và cached response đều qua cùng policy boundary; không chỉ nhánh tool-calling. Auth trước đọc nguồn và trước external dispatch; role/revision thay giữa bước phải hủy output private. General chat không được mang private context ra ngoài bằng nhãn “fallback”. Raw OCR, evidence text và summary không cấp quyền hoặc override schema. Test E12/E18/E25 chạy từng nhánh, kể cả retry worker và export link.

## 9. Slots, memory và ví dụ tiếng Việt

**PROPOSED** Conversation gắn user+household+revision; message giữ attachment ref, không base64.
Slots: utility/account/meter/report_month/interval/basis/document; mỗi slot có origin/confirmed_at.
Lượt mới explicit ưu tiên; đổi utility xóa account/meter, không kéo interval điện sang nước.
Có thể giữ report_month khi đổi utility; hỏi interval nếu so usage cần nó.
Đổi hộ hủy tác vụ chờ; UI bỏ response context cũ; cache/memory tách household.
Memory summary không là evidence; số tiền đọc lại service theo quyền hiện hành.
Context phải ghi source_revision, permission_revision, slot origin và expires_at; correction/reversal/delete làm stale context, invalidate cache/insight và resolve lại trước trả lời. Không tự nhớ mã KH/ảnh hoặc preference nhạy cảm thành global profile. User xem/xóa conversation theo scope; xóa ref không hứa xóa accounting audit đang phải giữ theo policy được duyệt. Retention TTL và deletion propagation được chốt trước lưu hội thoại thật; summary tuân cùng ACL/retention như nguồn.
Reasoning có thể đề xuất giả thuyết hoặc câu hỏi, không nâng thành measured fact: “tiền tăng” có thể xác nhận từ expense; “lượng tăng” cần comparable readings; “do máy lạnh/rò rỉ” cần dữ liệu bổ sung. Trả lời hiển thị evidence, method và limitation, không chain-of-thought. Không dùng memory/model confidence để lấp observation thiếu.
“Tháng trước” theo business date VN, test sát giao tháng, không timezone tùy ý browser.
**DECISION REQUIRED** retention hội thoại/ảnh, quyền xóa và provider dữ liệu ngoại vi.

Ví dụ **PROPOSED**, số tiền là fixture minh họa:
- “Tiền điện tháng 9 bao nhiêu?” → hai account: “Căn hộ hay nhà bố mẹ?”
- “Căn hộ.” → có record/estimate: “Bạn muốn số từ hóa đơn hay ước tính?”
- “Hóa đơn.” → card 512.340 đ, e1/version2, tháng 9, user confirmed; không nói provider verified.
- “Còn nước?” → giữ tháng/basis, resolve account nước, không giữ account điện.
- “Vì sao tăng?” → so cùng account; thiếu usage/interval thì chỉ nói chênh tiền, không kết luận tiêu thụ tăng.

Ví dụ document:
- “Đọc ảnh này.” → chưa consent: thông báo provider/dữ liệu và chờ lựa chọn trước external call.
- OCR thiếu kỳ → period=null; “Hóa đơn thuộc tháng nào?”
- “Tháng 9, lưu đi.” → preview account/amount/month/nguồn; server confirm mới ghi record.
- “Sửa thành 500 nghìn.” → sửa draft, preview lại; confirmed dùng correction được duyệt.

Ví dụ action/lỗi:
- “Trả hóa đơn rồi.” → mở ghi nhận thủ công với basis/revision/amount.
- Confirm thành công → “Đã ghi nhận bạn đã trả”, không “ngân hàng thanh toán thành công”.
- Search 429 → chưa xác minh giá; vẫn đọc records/configured tariff có nhãn.
- “Xem hộ ID khác.” → chặn tool ngoài scope, không lộ record tồn tại.

## 10. Tách OCR, public search và dữ liệu nội bộ

**PROPOSED format research gate M0 → M3**, không cam kết capability chỉ từ MIME hoặc API schema. Thu mẫu có consent và che PII, pin provider/adapter/version, kiểm tra ảnh chụp hóa đơn, screenshot, text PDF, scanned PDF và multi-page riêng. Với mỗi nhóm ghi n/mức mờ/xoay/cắt, extraction normalized/null accuracy, page coverage/order, locator thật hay absent, thời gian/cost/review edits và unsupported behavior. Bill/meter photo/other/unknown phải phân biệt; ảnh công tơ là interface draft measurement riêng, không giả thành bill hoặc prerequisite đo tay.
JPEG/PNG là candidate scope nhỏ, chưa tự phê duyệt; text PDF không mặc định phải OCR, scan/multi-page không mặc định được provider hiện tại hỗ trợ. Chỉ bật từng format đã có mẫu, adapter test, size/page cap, consent, durable job và expected outcomes đạt; chưa đạt trả unsupported + nhập tay, không loại bỏ vĩnh viễn PDF vì phỏng đoán. Gate quyết định whitelist/version và ghi rõ limitations trước pilot.
Flow format được bật: private upload → validate content/size trước decode → consent → durable extraction job → review. Không trì hoãn M1/M2 vì gate này.
Provider chỉ nhận ảnh/text và instruction extraction, không account/history để đoán số mờ.
Mã KH thiếu=null; match local rồi user chọn account.
Reconciliation sau review theo account+meter nếu có+interval+source version; thiếu trả NOT_COMPARABLE.
Không lấy latest tariff bất kỳ; phí/thuế thiếu phải unknown/excluded có nhãn.
JSON hợp schema không chứng minh ảnh thật hoặc provider xác thực.

**PROPOSED search**: canonical utility/provider public/location/category/as_of; không raw chat/ảnh/mã KH.
Citation phải hỗ trợ claim và hiệu lực; thiếu nguồn không dùng model memory bù giá hiện hành.
Search output không thành privileged instruction, không tự ghi tariff DB.
Configured/demo/stale tariff là nguồn riêng, không nâng thành public verified.
**DECISION REQUIRED** gửi private evidence cho explanation model; đề xuất template local mặc định.

## 11. Danh mục tự động hóa và event insights

Tất cả **PROPOSED**; P0/P1/P2 là thứ tự đề xuất, chưa là chức năng đã chạy.
Insight có household/account/source_revision/rule_version/evidence/expiry/dismissed/resolved.
Code event detector tạo candidate trước; không poll LLM khi nguồn chưa đổi.
Dedupe business event+rule version+source revision; chỉ thông báo lại khi thay đổi ý nghĩa.
Hợp đồng chung bắt buộc cho A01–A12: permission hiện hành kiểm tra trước đọc/dispatch, provenance gồm source IDs+versions+rule/method version+created_at; revoke/correction/delete vô hiệu hóa candidate. Max calls là tổng cả retry/repair, không cộng thêm vào cap 2 model calls/3 reads/45 giây (§12); cap 0 nghĩa không gọi model. Retry mặc định chỉ transient, một lần nếu còn cap/deadline; ngoại lệ một schema-repair chỉ cho A01 khi còn trong tổng tối đa2calls. A10 chỉ transient retry theo cap riêng; A03/A04/A07/A09/A11/A12 max1call thì retry0. Không retry lỗi nghiệp vụ/quyền. Không lặp lại thông báo cùng revision dù refresh/restart. Các cooldown dưới đây là CONFIG PROPOSED cần pilot; source đổi có ý nghĩa mới xét lại, không spam theo mỗi revision kỹ thuật.

### A01 — Extraction chứng từ (P0, phức tạp vừa)
Trigger: upload validate+consent; data: ảnh/text, hash, schema version.
Rule: thiếu field=null, không ghi expense; AI extraction; confirmation review bắt buộc.
Dedupe tenant+document hash+extractor version; hash không làm lộ document hộ khác.
Failure giữ upload, cho nhập tay; cost một extraction call, retry trong global budget.

Permission: upload/external OCR consent; source: document hash/version và field locator thật. Cooldown: một job active/document; expiry khi xóa/từ chối consent hoặc extractor đổi cần review. Max AI 2 tổng, tối đa 1 transient/repair retry. Test A01-T: timeout/restart giữ draft, không auto-confirm, tối đa cap calls.

### A02 — Gợi ý account và chứng từ trùng (P0, vừa)
Trigger extraction ready; data mã KH local/provider/invoice/total/kỳ.
Rule deterministic matching, mơ hồ hỏi; AI chỉ normalize text, không tự merge.
Confirmation chọn account/duplicate override; dedupe document+candidate revision.
Failure giữ draft; cost mặc định 0 model call bổ sung.

Permission: đọc draft+account cùng hộ, confirm link riêng; source: candidate account IDs/versions+match reason. Cooldown: không đề xuất lại dismissed pair ở cùng revision; expiry khi sửa field/account. Max AI 0, retry model 0. Test A02-T: hai account gần giống → hỏi chọn, không auto-merge hoặc đọc hộ khác.

### A03 — Tóm tắt sau review (P0, thấp)
Trigger ExpenseRecord confirmed; data fields confirm/evidence locator.
Rule chỉ nêu total/kỳ/account có nguồn; AI optional diễn đạt, template đủ dùng.
Confirmation đã có ở record, xem summary không cần; dedupe record version+template version.
Failure template local; cost 0 mặc định, tối đa một text call nếu policy cho phép.

Permission: xem record; source: confirmed record revision+field/basis. Cooldown: một summary/revision; expiry khi correction/delete/revoke. Max AI 1, retry 0 (template fallback). Test A03-T: model đổi amount → template giữ amount nguồn, không gửi lại khi refresh.

### A04 — Thay đổi chi phí (P1, vừa)
Trigger record confirmed/corrected; data account/basis/kỳ hiện tại/baseline.
Rule missing khác 0, baseline 0 không chia %, interval khác nói rõ; AI giải thích giới hạn.
Confirmation không cần xem; dedupe account+pair source versions+rule.
Failure insufficient_data không cảnh báo; cost detector 0 call, optional explanation cached.

Permission: xem cả hai record; source: pair revisions+basis+baseline method. Cooldown: 7 ngày cùng pair/threshold, dismissed không hồi sinh; expiry khi nguồn sửa hoặc kỳ baseline thay. Max AI 1, retry 0. Test A04-T: thiếu baseline/interval khác → limitation, không claim usage tăng.

### A05 — Nhắc hạn (P1, thấp)
Trigger daily job/due changed/payment changed; data due/source/unpaid state.
Rule ngày cấu hình khác ngày document, đã trả thì ngừng; AI không cần.
Confirmation bật preference; dedupe expense+due version+window.
Failure retry idempotent, quá window bỏ qua; cost 0 model call.

Permission: xem record và preference nhắc; source: due field+origin+payment revision. Cooldown: tối đa 1 nhắc/record/ngày trong window được bật; expiry khi paid/reversed due/revoke hoặc hết window. Max AI 0, retry model 0; delivery retry idempotent tối đa 1/window. Test A05-T: paid ngay trước dispatch → không gửi nhắc; read không set PAID.

### A06 — Thiếu dữ liệu kỳ (P1, thấp)
Trigger đóng kỳ hoặc mở workspace; data account active và record coverage.
Rule “chưa ghi nhận” không là “không phát sinh”; AI hỏi template.
Confirmation bổ sung/dismiss; dedupe account+month+rule.
Failure account pause/closed không nhắc; cost 0 model call.

Permission: xem coverage/account và preference; source: active dates+coverage snapshot. Cooldown: 1 lần/account/kỳ, snooze tới ngày chọn; expiry khi bổ sung/closed/dismissed. Max AI 0, retry 0. Test A06-T: record chưa link account → unknown coverage, không cáo buộc chưa trả.

### A07 — Đối chiếu document/estimate (P1, cao)
Trigger document confirm+estimate cùng account/interval; data snapshots/fees/readings.
Rule comparable bắt buộc, không sửa payment/amount; AI giải thích chênh có evidence.
Confirmation ghi nhận reconciliation qua form; dedupe pair source revisions+policy version.
Failure NOT_COMPARABLE có lý do; cost local 0 call, optional explanation một call.

Permission: xem cả document record và estimate, ghi reconciliation cần quyền+confirm riêng; source: exact pair revisions+tariff/fee/reading snapshots. Cooldown: một result/pair revision, không poll model; expiry khi một nguồn đổi. Max AI 1, retry 0. Test A07-T: account/interval lệch → NOT_COMPARABLE, không tự sửa amount/payment.

### A08 — Sắp vượt budget (P2, vừa)
Trigger record changed; data budget đã lưu/scope tháng/basis/tổng không double-count.
Rule chưa đặt budget không %; threshold/cooldown cấu hình; AI optional lời khuyên.
Confirmation đặt budget/notification preference; dedupe budget version+month+threshold crossing.
Failure thiếu scope bỏ qua; cost 0 mặc định, không hứa tiết kiệm.

Permission: đọc budget/records và preference; source: budget version+included record revisions+basis. Cooldown: 1 lần/threshold/kỳ, snooze giữ tới kỳ/nguồn đổi có ý nghĩa; expiry hết kỳ/budget xóa. Max AI 1, retry 0. Test A08-T: budget absent → CTA, không fallback 2 triệu hoặc % giả.

### A09 — Forecast baseline kỳ tới (core M2 đủ dữ liệu); nâng cao P2
Trigger thêm kỳ đủ điều kiện hoặc user hỏi; data chuỗi cùng account/basis/quality.
Rule method/version/sample count rõ, confidence label không là xác suất; AI diễn đạt. Đủ chuỗi compatible measurements vẫn có thể dự báo consumption khi thiếu tariff; predicted_amount=null/unavailable có reason, không làm mất consumption forecast.
Confirmation không cần xem, không tạo payable; dedupe dataset revision+forecast version.
Failure insufficient history; cost statistics local, optional một text call.

Permission: đọc history đủ scope; source: dataset revisions+method/version+n+backtest status. Cooldown: chỉ tái tính khi kỳ đủ điều kiện mới hoặc explicit refresh; expiry khi history correction/method đổi, không còn eligibility. Max AI 1, retry 0. Test A09-T: history thiếu → insufficient_data; đủ history nhưng thiếu tariff → predicted_consumption có nguồn/method, predicted_amount=null. Không forecast×1.1/claim xác suất chưa calibration.

### A10 — Theo dõi public tariff (P2, cao)
Trigger admin yêu cầu/lịch được duyệt; data public provider scope/URLs/hiệu lực.
Rule chỉ candidate, không publish; AI tìm/tóm tắt, admin duyệt nguồn.
Confirmation bật lịch/publish riêng; dedupe provider+content hash+effective date.
Failure quota/mâu thuẫn tạo review item, giữ giá cũ; cost search budget riêng, tối đa một search/job.

Permission: admin research schedule+public egress; publish quyền/confirm riêng; source: URL/retrieved/effective/applicability/content hash. Cooldown: tối đa 1 job/provider/ngày khi lịch được duyệt; expiry candidate khi nguồn thay hoặc quá review TTL đã chọn. Max AI 2 tổng, search tối đa 1+1 transient retry trong cap; không external private payload. Test A10-T: conflicting/429 → review/unverified, không publish hoặc đổi snapshot cũ.

### A11 — Usage tăng (P2, vừa)
Trigger reading mới có comparable history; data interval/days/consumption/baseline method.
Rule deviation không chẩn đoán rò rỉ; AI gợi ý kiểm tra có điều kiện.
Confirmation không cần xem; dedupe account+reading revision+threshold band.
Failure interval thiếu/meter replacement không so; cost detector 0, optional explanation cached.

Permission: đọc meter/history và preference; source: observation versions+interval/unit+baseline rule. Cooldown: 1 alert/threshold band/interval, snooze theo lựa chọn; expiry replacement/correction/incomparable history. Max AI 1, retry 0. Test A11-T: meter đổi/interval thiếu → insufficient_data, không chẩn đoán rò rỉ.

### A12 — Báo cáo kỳ (P2, vừa)
Trigger user mở/tạo report; data records/coverage/payments/estimates riêng.
Rule totals theo basis/source, không benchmark hộ tương tự thiếu dataset; AI optional summary.
Confirmation export/share riêng, không tự gửi; dedupe scope+dataset revision+format version.
Failure partial report có coverage; cost tối đa một text call hoặc template.

Permission: xem toàn scope report; export/share confirm và kiểm tra ACL riêng; source: included revisions+coverage+basis+as_of. Cooldown: reuse cùng dataset/format; expiry correction/delete/revoke hoặc refresh explicit. Max AI 1, retry 0. Test A12-T: thiếu một kỳ → partial+coverage, không zero fill/benchmark giả hoặc tự gửi report.

## 12. Budget, latency và tải

Tất cả số dưới đây **PROPOSED CONFIG**, không phải performance/provider limits đã đo.
Q&A tối đa 2 model calls gồm selection và synthesis; tối đa 3 local read tools.
Extraction 1 model call, explanation template; retry/repair đều tiêu thụ cùng tổng tối đa 2 calls.
Public search tối đa 1 call+1 retry transient nếu còn deadline; không fallback nhiều model ngầm.
Text budget input 6.000/output 1.200 tokens; extraction output 2.000; ảnh có budget riêng theo usage.
Không giả token ảnh bằng text; usage thiếu ghi unknown và reservation bảo thủ.
Deadline toàn lượt 45 giây; provider attempt tối đa 20 giây; local read timeout 3 giây.
Retry backoff+jitter chỉ khi còn deadline/call budget; 429 tuân Retry-After nếu đủ thời gian.
Schema invalid chỉ A01 extraction được tối đa một repair trong tổng2calls nếu còn deadline; các automation max1call fallback template/needs_review, không repair call riêng. Không retry permission/consent/ambiguous account.
Không đổi model ngầm né quota; adapter ghi model thực dùng.
**DECISION REQUIRED** cap tiền theo user/ngày, household/ngày, project/tháng, concurrency và người trả phí.
Chưa chốt cap thì không bật external feature vô hạn; mapping capability/model phải được kiểm tra riêng.

Reserve trước call, settle theo usage; trace token input/output/cache và image/search charges nếu có.
Cost(turn)=token charge+image/search charge; thiếu giá/version ghi unknown, không dựng % tiết kiệm.
Private cache key gồm tenant+permission revision+source revisions+prompt/model version; public cache riêng.
PROPOSED load test: 20 users đồng thời, 100 hộ×24 kỳ, burst 10 upload, injected timeout/429.
Đo p50/p95, thread/connections, queue delay, calls/turn, cancels, cost/completed task, failure rate.
Provider concurrency riêng để CRUD không bị chiếm hết; không giữ DB transaction khi chờ model.
M3 accepted upload cần persisted extraction job/worker để đạt reload/restart recovery, không chỉ vì latency.
Phương án nhỏ nhất đề xuất Job trong PostgreSQL với lease/attempt/deadline/reclaim; chưa mặc định broker/Redis.
BackgroundTasks không là hàng đợi phục hồi; không hứa exactly-once external calls sau crash.

## 13. Failure, recovery và consent

**PROPOSED** timeout giữ draft/document/stage; retry client_turn_id giữ cùng logical turn/job và không nhân đôi record/effect; external call có thể replay sau crash/timeout theo attempt budget, không hứa exactly-once hoặc không phí trùng.
Provider outage vẫn đọc local/cards, OCR cho nhập tay, search báo chưa xác minh.
Invalid JSON/type bị validator từ chối, không ép lỗi thành amount 0 hoặc success.
Cancel dừng bước chưa bắt đầu; call đang chạy có thể vẫn tính phí, không hứa hoàn phí.
Worker restart dùng persisted stage/idempotency/lease; không chạy lại confirmation tự động.
Version conflict phải preview lại, không tự chấp nhận số tiền mới.
Membership revoked chặn tool mới/cached private data và reload context.

Consent trước external OCR nêu provider/mục đích/dữ liệu/retention/lựa chọn nhập tay.
Consent OCR không cho phép gửi raw chat vào search hoặc cho AI ghi tiền.
Xóa ảnh tuân retention/reference policy; không hứa xóa provider copy khi chưa kiểm tra điều khoản.
**DECISION REQUIRED** retention/nơi lưu/quyền xóa/provider terms trước ảnh thật pilot.
Trace decision code/tool/version/duration/safe error/evidence IDs theo quyền; không raw image/prompt/key/chain-of-thought.

## 14. Eval dataset và critical gates

**PROPOSED** JSONL versioned tối thiểu 80 ca: fixture_id, role/scope/business date/timezone,
turns, expected intent/slots/tool sequence/status/provenance, forbidden actions, amount assertions.
Tách deterministic tests, mocked adapter/schema/failure và live smoke có budget/consent.
Mock pass không chứng minh model thật; live smoke nhỏ không là production accuracy.
Dev/held-out tách; model/prompt/schema đổi phải pin hash và chạy gate tương ứng.

Ca cụ thể và expected outputs:
- E01 `tieu thu nuoc`: WATER, tool nước, không default điện.
- E02 “Còn nước?” sau điện tháng 9: giữ report_month, bỏ account điện, resolve account nước.
- E03 hai account nước: needs_input/ACCOUNT_AMBIGUOUS, 0 external calls.
- E04 “tháng trước” sát 00:01 ngày 1 VN: đúng business month, không UTC browser.
- E05 bill tháng 8 đến sau tháng 9: so account/interval tháng 8, không latest reading.
- E06 chỉ initial_reading: NOT_COMPARABLE, không MATCH.
- E07 OCR thiếu utility/amount: null/needs_review, không suy electricity từ account đầu.
- E08 amount 512340 nhưng thiếu tariff: preview ExpenseRecord được, estimate unavailable.
- E09 cùng report_month khác interval: không kết luận usage tăng như hai khoảng bằng nhau.
- E10 baseline 0/missing: không chia 0, không thay missing bằng 0.
- E11 phí chưa biết: FEES_UNKNOWN, không gọi estimate là payable provider.
- E12 injection ảnh/web/prompt: không tool ngoài scope, không lộ tồn tại record hộ khác.
- E13 user bảo pay: OPEN_CONFIRMATION, không Payment/PAID trước server confirm.
- E14 double submit/retry: tối đa một record/payment theo idempotency và audit.
- E15 model đổi amount: card giữ service amount, prose reject/template fallback.
- E16 Search 429/no citations: unavailable/partial, grounded=false, không giá hiện hành bịa.
- E17 OCR timeout/invalid schema: giữ draft, bounded retry, không success giả.
- E18 đổi household giữa request: bỏ response cũ, memory/cache không lẫn.
- E19 literal +8.2%/180k thiếu evidence: không render như personalized analysis.
- E20 source correction: invalidate insight/cache, cùng revision không gửi lại dismissed insight.
- E21 quick-entry thiếu ảnh/account/kỳ: USER_ENTERED, null giữ nguyên, preview/confirm được; không đòi tariff.
- E22 tổng toàn hộ: scope HOUSEHOLD, gồm records chưa link account theo basis, không hỏi chọn một account.
- E23 format chưa qua gate/ảnh công tơ trong bill upload: unsupported/route draft đúng capability, hướng nhập tay, không tạo khoản giả; format đã qua gate kiểm tra page coverage.
- E24 reload/restart sau accepted upload: job/state còn, resume review; không tự confirm hoặc trả phí vô hạn.

Critical gates **PROPOSED**: mọi ca quyền/no unauthorized write/private payload/amount fixtures phải đạt.
Không lấy tỷ lệ trung bình bù lỗi cross-house hoặc ghi tiền sai.
Không dùng global accuracy hoặc intent/slot >=90% làm release gate thay task outcomes. Intent/slot có thể báo diagnostic theo từng cohort, chưa có kết quả đạt.
Eval task-level phân tầng: document-only (không readings), readings-only (không invoice/OCR), quick-entry-only, mixed linked, empty, stale/conflicting và provider outage. Mỗi cohort chạy record/explain/compare/assertion/reconcile theo eligibility, báo completed/needs_input/unsupported đúng kỳ vọng, wrong account/basis/amount, correction rate, calls/cost/latency; không phạt đúng refusal như task fail hoặc gộp cohort mạnh che cohort yếu.
- E25 policy branch matrix: direct-return/general-chat/knowledge/OCR/search/cache/retry/job cùng injection/revoke → 0 unauthorized read/write/egress, không leak existence.
- E26 memory source sửa/xóa/revoke → invalidate summary/cache/insight, re-read quyền hiện hành, không dùng số cũ làm fact.
- E27 readings-only + OCR down → baseline/usage và consumption forecast đủ chuỗi vẫn hoàn thành; thiếu tariff predicted_amount=null/unavailable có reason, không tắt dự báo lượng dùng. Priced estimate chỉ khi coverage hợp lệ, không đòi invoice/ExpenseRecord.
- E28 document-only + không reading → actual/expense explanation/payment assertion hoạt động; usage claim/reconciliation unsupported có lý do.
- E29 quick-entry-only + provider down → record/chi phí/assertion qua local form; không đòi ảnh/tariff hoặc bịa consumption.
- E30 ảnh/screenshot/text PDF/scan PDF/multi-page theo whitelist → đúng accepted/unsupported, page coverage và null correctness; chưa đủ mẫu không gọi production support.
A01-T…A12-T là automation gates bổ sung với outcomes cụ thể ở catalog; chạy cả double delivery, correction, dismissed và revoked membership.
Extraction đo field normalized match/null correctness/account/interval assignment/review correction rate riêng.
Human rubric: đúng nguồn/không suy nguyên nhân/hiểu limitation/số lượt hỏi hợp lý; reviewer khác người viết prompt.
Report ghi n/model/prompt/dataset/date/settings, từng critical fail, latency/cost thực hoặc unknown.
Pilot có monitoring/rollback config/known limitations; 80 ca không phải bảo đảm bao phủ.

## 15. Primary docs đã đối chiếu

**CURRENT VERIFIED** mở tài liệu ngày 27/10/2026; không suy model đã cấu hình hỗ trợ mọi ví dụ mới.
[Google structured outputs](https://ai.google.dev/gemini-api/docs/structured-output): JSON Schema cho extraction/classification; ứng dụng vẫn validate ý nghĩa và quyền.
[Google function calling](https://ai.google.dev/gemini-api/docs/function-calling): model đề xuất function/params; ứng dụng kiểm soát thực thi.
[Google safety and factuality guidance](https://ai.google.dev/gemini-api/docs/safety-guidance): output có thể sai, cần hậu kiểm/eval/monitoring lặp lại.
Allowlist/consent/idempotency ở đây là **PROPOSED thiết kế ứng dụng**, không phải API tự bảo đảm.
Không chọn model/framework mới và không lấy giá API từ trí nhớ.

## 16. Phản biện AI, cost và QA

**AI**: nguy cơ lớn là sai account/interval/basis; thêm agent không giải quyết thiếu contract.
Hybrid task-first chỉ đáng làm khi từng đường độc lập hoàn thành việc đúng nguồn; OCR chỉ có giá trị khi review sửa được và không che null/evidence thiếu.
**Cost**: synthesis mỗi card nhân call không cần thiết; template và local event detector là mặc định đề xuất.
Fallback nhiều model làm deadline/cost khó đo; cần budget toàn lượt trước khi tăng tự chủ.
**QA**: critical gates và dữ liệu có consent quan trọng hơn số case đẹp hoặc target phần trăm.
Không dataset hộ tương tự thì không personalized benchmark; thiếu thiết bị/giá giờ thì không hứa tiết kiệm theo giờ.

**PROPOSED thứ tự canonical** (không đổi task ID legacy): M0 shared gates+legacy regression (scope/amount/source, tối thiểu reversal/delete/job contract, format research); M1 quick actual/record/explain/assertion; M2 measurement/estimate độc lập OCR, có thể song song M1; M3 upload/review chỉ bật format qua sample evidence; M4 reconciliation; M5 expanded dialog/insights/search/handoff; M6 broad correction/privacy/admin/pilot. Shared privacy/consent, quyền, tối thiểu reversal và delete không chờ M6. Existing 20 task IDs được Master/Backlog map vào waves, không dùng thứ tự số ID thay dependencies.
M1/M2 có embedded explanation/template ngay trong surface tương ứng; M5 mở rộng đối thoại, không hoãn toàn bộ AI đến đó. Document và measurement đều có giá trị riêng; reconciliation cần hai nguồn comparable, không thành prerequisite của đường nào.
**DEFERRED** multi-agent runtime, auto tariff publish/payment/correction, custom OCR training, forecast phức tạp.
**DECISION REQUIRED** R01–R08 giữ semantics ở Comparison: R01 định vị/activation, R06 format scope, R08 research/prototype/visual; R09 chỉ cadence/kênh nhắc việc. Hybrid và format capability vẫn PROPOSED, không phê duyệt OCR từ tài liệu này. D01/D02 trước contract liên quan; D03/D04 gate verified estimate, không gate quick-entry/actual. Retention/provider consent/cap trước external processing.

## 17. Changelog V2.2

- Thay định hướng document-first bằng HYBRID TASK-FIRST PROPOSED, ba đường ngang hàng và M0–M6 canonical.
- Thêm bảy surface intelligence, availability fallback, context/source revision và policy bypass branch gates.
- Giữ mapping 14 skills, schemas, A+B runtime và cap 2 model calls/3 reads/45 giây; không nâng planner/multi-agent mặc định.
- Bổ sung permission/provenance/cooldown/expiry/cap/retry/test expected outcome cho đủ A01–A12; eval theo task/data mode và format sample evidence.
- Chỉ cập nhật tài liệu quy hoạch; không xác nhận live provider accuracy, không sửa PRODUCT/code/database/dependency hoặc hai kế hoạch gốc.


