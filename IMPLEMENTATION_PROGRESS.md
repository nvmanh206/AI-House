# Nhật ký triển khai và tiếp tục công việc

## Điểm tiếp tục — 2026-10-28

### Sửa từ chối sai phạm vi khi hỏi biểu giá Thái Nguyên

- Nguyên nhân: luồng Gemini mới bỏ qua nhánh public_tariff cũ và không cấp nguồn giá cho respond; AI còn tự thu hẹp phạm vi thành chỉ quản lý chỉ số/công nợ.
- Đã nối lại routing chọn nguồn Google Search cho câu hỏi giá công khai; chỉ gửi utility/location/date/customer_group/query_type chuẩn hóa, không gửi household overview/lịch sử sang Search. Giá nước chưa rõ tỉnh hoặc hỏi cả hai loại thì để Gemini hỏi rõ tự nhiên.
- Kết quả Search vào overview.public_tariff cho bước Gemini diễn đạt; nguồn web trả về frontend. Không dùng câu fallback cũ làm câu trả lời; nguồn thiếu/429 chỉ đưa mã lỗi, Gemini giải thích tự nhiên. Prompt khẳng định giá điện/nước theo địa phương thuộc phạm vi, phân biệt quyền tra thông tin với cập nhật biểu giá. Không tự đổi giá tính hóa đơn trong database.
- 3test hồi quy mới test_chat_public_tariff.py: hai câu hỏi user trong screenshot và Search thiếu căn cứ; red3fail→green3pass. Full backend cuối **123passed, 2warnings, 24.26giây** trên PostgreSQL. Test quota cũ cập nhật kỳ vọng2call Search+diễn đạt. Diff check không có lỗi whitespace.
- API8108 đã restart với bản sửa (PID60476/session79699). Thử Gemini thật chính câu “mình cần xem giá điện thái nguyên hiện nay”: HTTP200, INSUFFICIENT_DATA, public_tariff.grounded=false/errorGEMINI_SEARCH_QUOTA. Message nói giới hạn tra cứu tạm thời, gợi ý EVNNPC/CSKH; không còn từ chối sai phạm vi. Không có nguồn verified nên chưa cung cấp số giá hiện hành. Kết quả ignored.local/public-tariff-live-result.json.

### Sửa runtime trang3108: API cũ từ chối conversation_id

- User gửi screenshot422 `body.conversation_id: Extra inputs are not permitted` tại3108/assistant.
- Tái hiện bằng HTTP có xác thực:8108/OpenAPI chỉ có message/image_base64/raw_ocr_text, gửi conversation_id:null trả422;8110/OpenAPI đã có trường mới. Frontend3108 được khởi chạy với API base8108, không phải cấu hình.env.local8000.
- Xác minh tiến trình đang nghe8108 là `scripts/system_test.py serve`, PID22052. Dừng đúng tiến trình này và chạy lại launcher hiện có. Launcher hiện đã đọc Gemini/key/model từ backend.env; không sửa launcher, không thay database/JWT/cookie, không đụng server8000/tab user/pgAdmin.
- Sau restart PID38272: OpenAPI có conversation_id; chat thật qua8108 trả200, providergemini, statusANSWERED, cóconversation_id; câu hỏi tiếp nối với ID đó cũng200/providergemini. Đã kiểm chứng bằng tài khoản fixture System, không dùng tài khoản user thật.
- API8108 hiện chạy code mới. Trang3108 có thể tải lại rồi gửi câu hỏi mới; các lỗi422 trước đó không tự biến thành câu trả lời. Không cần migration/reset/xóa dữ liệu. Server hiện tại qua exec session92291.

## Hoàn tất triển khai: Gemini multimodal có cấu trúc — kế hoạch được user duyệt

**Đã triển khai và nghiệm thu Gemini thật + browser:** xem `docs/sdlc/VERIFICATION-GEMINI-MULTIMODAL-2026-10-28.md`. Core mới: ai/contracts.py, gemini_structured.py, multimodal.py. Model cấu hình đã chuyển sang gemini-3.1-flash-lite vì2.5API404 và3.8/3.5lỗi dịch vụ;3.1đã qua ảnh→backend→Gemini→follow-up→OUT_OF_SCOPE. Các ảnh cropped/blurred/nonbill/foreign/water đều qua nghiệm thu với provider thật, không ghi chỉ số/hóa đơn/thanh toán từ chat. UI3110/API8110 riêng, giữ tab user3108 và pgAdmin.

- Backend bản cuối **120passed/2warnings, 22.41giây**, frontend **16passed+tsc**. Bao gồm snapshot Extraction từng lượt (test đỏ chứng minh thiếu snapshot). Reviewer xác nhận sửa lỗi follow-up, không còn finding đáng kể. Kiểm tra diff không có lỗi whitespace; dữ liệu và thay đổi có sẵn được giữ nguyên, chưa commit/push.
- System exercise bản cuối đạt với Gemini thật; UI hỏi tiếp số tiền từ ảnh cũ trả90.000VND và nêu rõ ước tính. Screenshot cuối: docs/sdlc/evidence/gemini-multimodal-conversation-2026-10-28.png. Đã logout/đóng tab test, không đóng tab user. utility_app vẫn25hóa đơn; .env và.local đã xác nhận gitignored. Server test API8110/frontend3110 còn chạy để có thể kiểm tra tiếp; không thay server/tab3108 của user. Backend ứng dụng cần khởi động lại để đọc code/model mới.
- Script chạy lại: `scripts/multimodal_system.py serve|exercise`, `scripts/multimodal_variants.py`; dữ liệu/testlogin/ảnh tại.local/multimodal-browser-state.json vàmultimodal-test-invoice.png, không in credentials thật.
- Ruling: phản hồi vẫn tự nhiên; enum/schema/nhãn UI và phép tính Decimal là hợp đồng/quy tắc nghiệp vụ, không phải câu trả lời mẫu. Nhánh deterministic cũ chỉ chạy khi APP_ENV=test và LLM_PROVIDERkhácgemini, để giữ các test nghiệp vụ cũ; mọi request production dùng luồngGemini mới và báo lỗi thật khiproviderlỗi.
- Snapshot hiện20tin nhắn theo user/hộ/conversation; giữ dữ liệu đã đọc theo lượt, ảnh gần nhất là ngữ cảnh đối chiếu đang hoạt động. Nhiều ảnh trong1lượt/PDF/tựlưu/streaming chưa thuộc giai đoạn này. Cần benchmark thêm ảnh nhà cung cấp thực tế và CI browser/mobile.

- Luồng ảnh: giải mã/kiểm tra JPEG PNG WebP ≤10MB → Gemini trích xuất độc lập dữ liệu hộ → backend đối chiếu Decimal đúng tài khoản/công tơ/kỳ → Gemini diễn đạt JSON chứa message tự nhiên. Không fallback câu trả lời mẫu trong production.
- Tổng quan mỗi lượt: 6 kỳ, tổng công nợ toàn bộ + tối đa50 chi tiết, lịch sử20 tin nhắn và kết quả trích xuất theo cuộc trò chuyện, khóa user/hộ. Không gửi email/token/mật khẩu/thành viên.
- UI ưu tiên message, dữ liệu có cấu trúc mở khi cần; không tự lưu chỉ số/hóa đơn/thanh toán.
- TDD và kiểm thử5tầng, ghi rõ kiểm thử mock provider so với Gemini thật. Giữ toàn bộ thay đổi có sẵn; không commit/push tự động.
- Ruling: dùng Pillow để kiểm tra decoder thực tế, không chỉ chữ ký file; tái mã hóa ảnh trước gửi để bỏ metadata. Dùng AIAnalysis JSON hiện có cho lịch sử được scope theo user/hộ/conversation, không cần migration.
- Bằng chứng đợt trước chưa ghi: OCR comparison/amount sửa, inline chat, UI màu chữ; backend100passed/2warnings, frontend13passed+tsc; HTTP/System riêng và browser MATCH/UNKNOWN đã đạt. Ảnh chụp docs/sdlc/evidence/ocr-unknown-2026-10-28.png. Đợt này thay luồng Gemini, phải chạy lại.

## Đang triển khai: Gemini multimodal có cấu trúc — kế hoạch được user duyệt

- Luồng ảnh: giải mã/kiểm tra JPEG PNG WebP ≤10MB → Gemini trích xuất độc lập dữ liệu hộ → backend đối chiếu Decimal đúng tài khoản/công tơ/kỳ → Gemini diễn đạt JSON chứa message tự nhiên. Không fallback câu trả lời mẫu trong production.
- Tổng quan mỗi lượt: 6 kỳ, tổng công nợ toàn bộ + tối đa50 chi tiết, lịch sử20 tin nhắn và kết quả trích xuất theo cuộc trò chuyện, khóa user/hộ. Không gửi email/token/mật khẩu/thành viên.
- UI ưu tiên message, dữ liệu có cấu trúc mở khi cần; không tự lưu chỉ số/hóa đơn/thanh toán.
- TDD và kiểm thử5tầng, ghi rõ kiểm thử mock provider so với Gemini thật. Giữ toàn bộ thay đổi có sẵn; không commit/push tự động.
- Ruling: dùng Pillow để kiểm tra decoder thực tế, không chỉ chữ ký file; tái mã hóa ảnh trước gửi để bỏ metadata. Dùng AIAnalysis JSON hiện có cho lịch sử được scope theo user/hộ/conversation, không cần migration.
- Bằng chứng đợt trước chưa ghi: OCR comparison/amount sửa, inline chat, UI màu chữ; backend100passed/2warnings, frontend13passed+tsc; HTTP/System riêng và browser MATCH/UNKNOWN đã đạt. Ảnh chụp docs/sdlc/evidence/ocr-unknown-2026-10-28.png. Đợt này thay luồng Gemini, phải chạy lại.

**Đợt OCR — đã sửa đối chiếu sai tài khoản/kỳ:** `ocr_analysis.py` chỉ lấy bản ghi đúng kỳ từ công tơ thuộc tài khoản trong hộ đang xác thực; mã khách hàng nếu có phải khớp chính xác. Không lấy chỉ số mới nhất khác kỳ hoặc chỉ số ban đầu để kết luận MATCH/MISMATCH. Thiếu kỳ, không tìm thấy mã, nhiều tài khoản/bản ghi trả UNKNOWN. Giữ lại due_date/invoice_code/meter_code từ parser khi chuẩn hóa. Không thay đổi schema hoặc dữ liệu ứng dụng.

- TDD: 5 ca mới trong `backend/tests/test_ocr_reading_scope.py` đều thất bại trước sửa; sau sửa toàn backend PostgreSQL **95 passed, 2 warnings**, 19.32 giây. Hai ca API MATCH/MISMATCH cũ đã đổi đầu vào sang đúng kỳ và tài khoản duy nhất; ca mã khách hàng khác không còn kỳ vọng MATCH với baseline.
- Rà soát độc lập `ocr_scope_review`: không có finding cần sửa trong phạm vi selector; đề xuất bổ sung ca nhiều công tơ/bản ghi cùng kỳ. Chưa commit/push.
- Đã kiểm thử Server (selector), API (chat trên PostgreSQL test), Transform (parser và chuẩn hóa trong bộ backend); frontend regression hiện có **12 passed**. Đây chưa phải bằng chứng kiểm thử UI/System riêng cho OCR.
- Điểm tiếp tục: bổ sung UI/System OCR qua HTTP thật và màn hình trợ lý; kiểm tra thông điệp UNKNOWN. Rà soát còn tồn tại: so sánh tiêu thụ/dự báo đang gộp cùng utility, chưa khóa theo tài khoản/kỳ; amount_analysis có nhánh gọi hàm không tồn tại; OCR đang gửi household context cho Gemini và suy đoán loại ảnh không rõ. Chưa tuyên bố các nhánh này đã sửa hoặc toàn OCR đạt 5 tầng.


**Hoàn tất đợt cache/cookie:** cache generation chặn response cũ; useData gắn snapshot với key/generation và reset đúng khi tải mới. System cookie utility_system_refresh tách khỏi utility_refresh mặc định. Đã tái hiện red và sửa green; **90 test backend PostgreSQL đạt, 2 warnings**, 20.91 giây; **12 test frontend đạt + typecheck**. HTTP thật kiểm tra cookie login/refresh/logout không đụng cookie ứng dụng; browser chuyển hộ có 63.000 đồng/35 kWh → hộ rỗng → hộ gốc đều đúng, không reload. Reviewer không có finding đáng kể. Xem phần bổ sung tại docs/sdlc/VERIFICATION-DASHBOARD-2026-10-28.md. PostgreSQL local đã khởi động lại vì đang dừng đầu đợt, không tạo lại/xóa dữ liệu.

**Mới nhất: đã hoàn tất lát cắt dashboard, kiểm chứng tại đủ 5 tầng trong phạm vi đã chọn.** Xem `docs/sdlc/VERIFICATION-DASHBOARD-2026-10-28.md`. Backend PostgreSQL **89 passed, 2 warnings**; frontend **11 passed** (7 SSR + 4 Transform), typecheck đạt. System thật: UI đăng nhập → ghi chỉ số → API/server → PostgreSQL → dashboard; đã kiểm tra rỗng/zero/nhiều tài khoản, thanh toán idempotent và cập nhật lịch sử sau lưu. SQL/API/UI cùng 35 kWh, 63.000 đồng kỳ 2026-10 trong DB `utility_system_7b7fdf4ad38d_test`. Database utility_app vẫn 25 hóa đơn, không ghi thử vào dữ liệu ứng dụng. Không đồng nghĩa toàn bộ sản phẩm đã đủ 5 tầng hoặc mọi tình huống đều đạt.

**Mới nhất: PostgreSQL + pgAdmin đã triển khai và xác minh.** Backend `.env` dùng `127.0.0.1:5433/utility_app`; pgAdmin tại `http://127.0.0.1:5050`, email `admin@example.com`, mật khẩu chỉ ở `.local/pgadmin-access.txt`. PostgreSQL là portable local, pgAdmin là Docker; không nhầm với PostgreSQL Docker cũ cổng 5434. Xem `docs/POSTGRESQL-PGADMIN.md`. Backend chưa được khởi động lại ở đợt này; lần khởi động tiếp theo sẽ đọc PostgreSQL mới.

**Yêu cầu đã xác nhận:** kiểm thử 5 tầng UI, API, Server, System và toàn bộ Transform. Ứng dụng dùng dữ liệu thật, không hardcode số liệu; dùng PostgreSQL và pgAdmin làm giao diện quản trị database. Xem `docs/sdlc/SDLC-TEST-STRATEGY.md` trước khi tiếp tục. Không dùng kết quả 86 test backend/SQLite hay 2 test SSR để tuyên bố toàn hệ thống đạt. Kiểm thử ghi dữ liệu phải dùng PostgreSQL test riêng; không ghi thử hoặc xóa dữ liệu đang sử dụng.

- Người dùng đã yêu cầu bắt đầu cải thiện hệ thống và lưu dấu vết để tiếp tục sau khi hết quota.
- Workspace: `F:\Web\AI_Household_Utility_Billing`; toàn bộ code trong `website/`.
- Git tại `website/.git`; nhánh triển khai: `codex/m0-reliability-foundation`.
- Checkout có nhiều thay đổi từ trước. Đã giữ nguyên và tạo nhánh trên checkout hiện tại; không reset, stash hoặc sao chép sang worktree làm mất các thay đổi chưa commit.
- Căn cứ: `docs/sdlc/SDLC-MASTER-PLAN.md`, `docs/sdlc/SDLC-REQUIREMENTS-TRACEABILITY.md` và `docs/replanning/V2-MASTER-PLAN-IMPROVED.md`.

## Đợt hiện tại: M0 — độ tin cậy khi chọn biểu giá

Trạng thái: **Hoàn tất lát cắt biểu giá; rà soát độc lập không phát hiện lỗi cần sửa**. Đây chỉ là một phần M0/S0.2, chưa hoàn tất toàn bộ M0.

Tiêu chí nghiệm thu:
- Chỉ chọn biểu giá đúng loại tiện ích, nhà cung cấp, nhóm khách hàng và phạm vi địa phương; giữ ưu tiên địa phương trước biểu giá toàn quốc.
- Không lấy giá nhà cung cấp/nhóm/địa phương khác khi thiếu cấu hình.
- Khi có nhiều biểu giá cùng mức ưu tiên còn hiệu lực, báo lỗi rõ ràng thay vì tự chọn một bản.
- Giữ phép tính Decimal, snapshot lịch sử và rollback giao dịch khi không thể tạo hóa đơn.
- Viết kiểm thử hồi quy, chứng kiến lỗi trước khi sửa, sau đó chạy lại toàn bộ backend.

## Dấu vết đã làm

1. Đọc kế hoạch SDLC và source liên quan; xác định fallback biểu giá có thể trả giá sai phạm vi.
2. Tạo nhánh triển khai, giữ nguyên thay đổi có sẵn.
3. Tạo file nhật ký này trước khi sửa code.
4. Thêm `backend/tests/test_tariff_selection.py`: 14 ca cho sai phạm vi, hiệu lực, ưu tiên địa phương/toàn quốc, chồng lấn và rollback API.
5. Chạy trước khi sửa: **8 failed, 6 passed**; tái hiện được fallback sai và tự chọn giá chồng lấn.
6. Sửa `backend/app/billing_service.py`: bỏ fallback sai phạm vi; thêm lỗi `TARIFF_AMBIGUOUS` HTTP 409; giữ nguyên thuật toán tính và snapshot.
7. Chạy toàn bộ backend sau sửa: **82 passed, 2 warnings**, 11.31 giây.

## Đợt tiếp: M0 — AI hiểu câu tiếng Việt không dấu

Trạng thái: **Hoàn tất lát cắt AI không dấu; toàn bộ backend 86 test đạt; rà soát độc lập không phát hiện hồi quy đáng kể**. Reviewer chạy riêng 4 ca API mới: 4 passed.

- Thêm `backend/tests/test_ai_unaccented_queries.py`: 4 ca API cho câu có dấu và không dấu.
- Trước sửa: **2 failed, 2 passed**. Hỏi nước không dấu nhận nhầm điện; so sánh tiền không dấu nhận nhầm lượng tiêu thụ.
- `backend/app/ai/router.py`: trích hàm `normalize_message` từ phép chuẩn hóa đang có, router tiếp tục dùng cùng logic.
- `backend/app/ai/agent.py`: dùng hàm chuẩn hóa cho tham số biểu giá, chọn loại tiện ích và phân biệt so sánh tiền. Các thay đổi khác có sẵn trong file không thuộc đợt này.
- Chưa mở rộng hội thoại nhiều lượt hoặc đổi provider.

## Kiểm chứng

### Dashboard và 5 tầng — hoàn tất lát cắt 2026-10-28

- Source đổi: backend/app/services.py (statistics); frontend/components/application.tsx (nullable summary + invalidation listener), dashboard/dashboard-data.ts mới, dashboard/CostBreakdown.tsx, dashboard/NotificationPanel.tsx, dashboard/ExpenseTrendChart.tsx, charts.tsx (chỉ nhãn lượng dùng), layout/AppLayout.tsx (chỉ ngày động).
- Test mới/đổi: backend/tests/test_dashboard_statistics.py (3 ca); frontend/tests/dashboard-transform.test.cjs (4 ca); dashboard-truth.test.cjs (7 ca hiện tại, gồm 2 ca cũ).
- Đã tái hiện red trước sửa API (2 KeyError thiếu cost từng tiện ích), SSR thiếu/zero (2 failed), thông báo giả (1 failed), ngày cố định (1 failed), nhãn lượng dùng như tiền (1 failed). Test Transform module mới ban đầu chưa có module; không coi lỗi import là bằng chứng tái hiện logic cũ.
- Sau sửa: 89 test backend trên PostgreSQL utility_app_test đạt, 2 warning, 18.36 giây; frontend 11 test đạt. Typecheck không ghi cache đạt. Reviewer độc lập chạy 11 frontend test đạt, không có finding đáng kể trong phạm vi.
- scripts/system_test.py chuẩn bị PostgreSQL test riêng, giữ nguyên dữ liệu ứng dụng. Cấu hình giá được đọc từ PostgreSQL hiện có; thông tin hộ/chỉ số test là fixture có kiểm soát trong DB riêng, không hardcode vào app.
- System HTTP health/auth/401/onboarding/2 tài khoản/rỗng đạt; zero hai tài khoản kỳ 09 đạt. Browser nhập 10 kWh, server trả 201; runner thấy 409 khi thử lặp và đối chiếu hóa đơn cũ. Nhập tài khoản thứ hai qua HTTP: tổng 54.000 đồng. Thanh toán lặp cùng ID và bill PAID đạt.
- Browser phát hiện cache xóa Map nhưng không thông báo useData: lịch sử đứng yên sau POST thành công. Sau bổ sung listener/revision, browser nhập thêm công tơ thứ ba 5 kWh: hàng lịch sử 5 kWh hiện ngay không reload. Điều hướng dashboard: SQL/API/UI đều tổng 63.000 đồng, 35 kWh; nước null, kỳ đúng 2026-10.
- Browser phát hiện thêm fallback thông báo mẫu và ngày giả; đã thêm test/sửa. Biểu đồ lượng dùng đã đổi nhãn để không nhầm kWh/m³ với số tiền.
- Test infrastructure: frontend/next.config.ts có NEXT_DIST_DIR tùy chọn để chạy build cache riêng .next/system-test; Next tự bổ sung 2 glob type test vào tsconfig. Không cần dependency test mới. System test guard chỉ chấp nhận database prefix utility_system_ và suffix _test.
- Các hạn chế còn lại được ghi trong báo cáo: cache race request cũ sau invalidation; chưa có CI browser automation; chưa kiểm tra mobile toàn dashboard và mọi chức năng OCR/AI/hạ tầng. Trang login còn claim marketing thiếu căn cứ. Không mở rộng vô hạn trong đợt này.

### Triển khai PostgreSQL và pgAdmin — hoàn tất 2026-10-28

- Kiểm tra thực tế phát hiện `backend/.env` đang dùng SQLite, dù README cũ ghi PostgreSQL. Đã sửa mô tả sau khi chuyển đổi, không dựa vào README để đoán database.
- Docker 29.5.3 hoạt động khi chạy công cụ có quyền. Đã khởi động PostgreSQL portable 16.15 hiện có trên localhost:5433; giữ nguyên `.local/pgdata` và PostgreSQL Docker cũ (không khởi động/chuyển volume).
- SQLite có 25 hóa đơn, PostgreSQL `utility` cũ có 26: không tự merge. Dùng database mới `utility_app`, chạy Alembic rồi copy toàn bộ dữ liệu SQLite theo thứ tự khóa ngoại trong một transaction.
- Trước copy xác nhận không có backend UVicorn/scheduler đang chạy; các container backend/scheduler cũ đều dừng. Sao lưu SQLite và backend/.env vào `.local/` trước khi chuyển; không xóa nguồn.
- Lần copy đầu phát hiện timestamp bị diễn giải theo múi giờ PostgreSQL: kiểm tra hash thất bại và transaction rollback, cấu hình chưa đổi. Sửa bằng cách giữ rõ UTC cho timestamp SQLite không timezone; lần sau đối chiếu đủ 15 bảng đạt rồi mới đổi backend/.env.
- Báo cáo thành công: `.local/postgres-migration-20261027T200853010199Z.json` (tên UTC), chỉ có số lượng/hash và đường dẫn backup. Đối chiếu lại SQLite gốc đang có và PostgreSQL sau toàn bộ kiểm thử: nội dung đủ 15 bảng vẫn bằng nhau sau chuẩn hóa UTC.
- Dữ liệu bảo toàn gồm 3 users, 3 households, 6 accounts, 6 meters, 25 readings, 25 bills và 20 payments. Chưa xác minh nguồn gốc thực tế/demo của từng bản ghi; không tự xóa dữ liệu cũ.
- `docker-compose.yml`: thêm pgAdmin 9.18 profile admin, chỉ bind 127.0.0.1:5050, volume cấu hình riêng, mật khẩu/passfile từ `.local/`. Không khởi động backend hoặc database Docker cũ.
- `scripts/configure_pgadmin.py`: sinh mật khẩu ngẫu nhiên nếu chưa có, đăng ký database ứng dụng từ backend/.env, tạo passfile và file hướng dẫn truy cập. Mọi file credential và backend/.env đã xác nhận được Git ignore.
- Đã kiểm tra HTTP đăng nhập pgAdmin và HTTP API kết nối server đã đăng ký: 200, success true. Truy vấn trực tiếp từ container pgAdmin đọc đúng utility_app PostgreSQL 16.15 và 25 hóa đơn. Không in mật khẩu ra tool output.
- Lần đầu chạy test trên utility_test cũ: 28 failed / 29 passed / 29 errors vì schema thiếu cột. Không sửa/xóa database cũ; tạo runner `scripts/test_postgres.py` dùng utility_app_test tách biệt, từ chối database test có bản ghi đã commit.
- Runner mới: **86 passed, 2 warnings trên PostgreSQL**, 17.15 giây. Alembic check utility_app: **No new upgrade operations detected**. Compose config --quiet exit 0.
- Rà soát độc lập nêu nguy cơ writer tiếp tục ghi SQLite khi chuyển đổi. Đã bổ sung --offline, chặn khi API 8000 đang chạy, khóa ghi SQLite và so sánh live source với snapshot trong thời gian chuyển; reviewer xác nhận không còn finding đáng kể. Đối chiếu live sau chuyển cũng đạt.
- `scripts/migrate_local_sqlite_to_postgres.py` không được chạy lại trên đích có dữ liệu. Sau bổ sung guard: kiểm tra cú pháp 3 script đạt; gọi không --offline từ chối trước thay đổi như mong đợi. Chưa kiểm thử lại toàn bộ migration trên một database đích mới sau khi thêm guard, không được tuyên bố guard đã E2E đầy đủ.
- Tài liệu mới `docs/POSTGRESQL-PGADMIN.md`, README đã cập nhật nguồn database và bỏ seed trong luồng chạy mặc định.
- Đây là bằng chứng Transform bảo toàn dữ liệu + API/server integration + pgAdmin HTTP/database smoke. Chưa có UI/System E2E toàn bộ sản phẩm sau đăng nhập, chưa kiểm tra AI mạng thật. Không đồng nhất cài database đạt với tất cả 5 tầng đã đạt.

### PostgreSQL và dữ liệu thật — xác nhận mới

- Chuẩn 5 tầng cập nhật theo yêu cầu người dùng: Transform bao phủ toàn luồng, không còn chờ xác nhận thuật ngữ.
- Kiểm tra source: Compose dùng PostgreSQL 16; runner local có cấu hình 127.0.0.1:5433 và database utility/utility_test. Đây là thông tin cấu hình, chưa xác nhận tiến trình hoặc kết nối đang hoạt động.
- `docker-compose.yml`: bỏ tự chạy `app.seed --demo` và bỏ `|| true` ở command backend. Backend chỉ khởi động sau migration thành công; không tự nạp dữ liệu demo trong lần khởi động mới.
- Chưa restart container, chưa migrate/xóa dữ liệu, chưa xác nhận dữ liệu hiện có là thật hay demo.
- Kiểm tra command khởi động đạt; `docker compose config --quiet` exit 0, có cảnh báo không đọc được Docker user config trong sandbox. Chưa chạy container hoặc kiểm thử kết nối PostgreSQL ở lượt này.
- Chưa tìm thấy pgAdmin trong thư mục cài đặt thông dụng; chưa cài hoặc cấu hình kết nối. Bước tiếp theo: xác minh PostgreSQL đang chạy và cấu hình pgAdmin bằng kết nối local hiện có, giữ kín credential; chạy tích hợp trên utility_test riêng.

### Đợt dashboard — 2026-10-28 (hoàn tất lát cắt nội dung)

- `frontend/components/dashboard/AIInsightPanel.tsx`: bỏ tăng 8.2%, tiết kiệm 80–120 nghìn và so sánh nhóm hộ thấp hơn 12% không có nguồn. Đổi thành gợi ý chung, ghi rõ chưa phân tích dữ liệu hộ, giữ đường dẫn trợ lý; nội dung không bị ẩn trước animation.
- `frontend/components/application.tsx`: bỏ dự báo tự nhân 1.1; hiển thị chưa có dự báo và liên kết trợ lý. Bỏ ngân sách mặc định 2 triệu; thiếu ngân sách thì không hiển thị phần trăm/phần còn lại giả.
- `frontend/tests/dashboard-truth.test.cjs`: render component React thật bằng ReactDOMServer + TypeScript hiện có, không thêm dependency. Trước sửa 2 failed; sau sửa 2 passed.
- `node node_modules/typescript/bin/tsc --noEmit --incremental false`: **exit 0**. Lệnh npm typecheck ban đầu lỗi EPERM khi ghi tsconfig.tsbuildinfo; dùng kiểm tra không ghi cache để hoàn tất.
- Impeccable detector cho hai file UI: `[]`, exit 0.
- Đã xác minh component trên trình duyệt, từ frontend đúng checkout `127.0.0.1:3107`, Next.js 16.3.4. Dùng route tạm render AIInsightPanel với CSS thật ở khung 448px và 320px; sửa header xuống dòng hợp lý và bỏ icon trang trí lặp lại để lời khuyên dễ đọc ở khung hẹp. Đã xóa route `app/m0-insight-preview/page.tsx` và thư mục tạm sau kiểm tra.
- Rà soát độc lập không phát hiện lỗi cần sửa trong phạm vi nội dung/budget/forecast; reviewer chạy 2 test SSR đạt. Sau điều chỉnh bố cục và xóa route tạm, chạy lại 2 test SSR đạt và typecheck không cache exit 0.
- Hai test SSR chỉ kiểm tra nội dung panel và đường dẫn trợ lý; chưa kiểm thử tự động đầy đủ budget/forecast trên dashboard sau đăng nhập. Chưa xác nhận browser E2E, chưa build production. Backend không đổi ở đợt này; kết quả 86 test backend ở trên thuộc đợt trước.
- Frontend dev đã khởi động trên 3107 phục vụ kiểm chứng. Lần chạy sandbox lỗi quyền lockfile; chạy lại được bằng công cụ được cấp quyền. Nếu tiếp tục và port đang bận, kiểm tra tiến trình trước khi mở server mới.
- Còn số liệu giả trong component `StatGrid.tsx` không được Dashboard hiện tại sử dụng; chưa sửa trong lát cắt này. Dashboard cũng còn xử lý thiếu dữ liệu thành 0 và tổng tiền chọn một tài khoản: cần kiểm thử và sửa ở đợt tiếp.

Baseline mới 2026-10-28: **68 passed**, 10.62 giây. Sau sửa biểu giá: **82 passed**, 11.31 giây. Hai cảnh báo có sẵn từ Starlette/httpx và AnyIO; chưa thay dependency trong đợt này.

Sau sửa cả hai lát cắt: **86 passed, 2 warnings**, 11.97 giây. Tổng cộng **18 ca hồi quy mới**. Kiểm thử dùng SQLite tạm và provider deterministic, không xác nhận chất lượng Gemini thật hoặc UI/browser.

`git diff --check` toàn checkout phát hiện whitespace có sẵn ở README, Gemini, registry, Docker và frontend. Không sửa các thay đổi ngoài phạm vi. Kiểm tra tập trung ba file source của đợt này **exit 0**, chỉ có thông báo Git sẽ chuyển LF/CRLF.

Lưu ý vận hành: cấu hình biểu giá sai nhóm/địa phương hoặc chồng lấn trước đây bị che bởi fallback nay sẽ trả 409. Chưa tự sửa dữ liệu; cần quản trị viên chỉnh phạm vi/thời gian hiệu lực trước khi tạo hóa đơn mới. Hóa đơn đã lưu giữ snapshot cũ.

Lệnh backend chạy trong `website/backend` với biến môi trường riêng cho tiến trình:

```powershell
$env:TEST_DATABASE_URL='sqlite://'
$env:GEMINI_API_KEY=''
$env:LLM_API_KEY=''
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

Không dùng database thật; không đọc hoặc ghi secret vào nhật ký.

## Cách tiếp tục sau quota

1. Đọc file này và `git status` trong `website/`; không xóa thay đổi chưa commit.
2. Xem mục trạng thái và kết quả kiểm thử mới nhất, kiểm tra source thực tế trước khi tiếp tục.
3. Hai lát cắt biểu giá và tiếng Việt không dấu đã có code và kiểm thử; không triển khai lại. Kiểm tra kết quả rà soát cuối và chuyển sang mục tiếp theo bên dưới.
4. Cập nhật ngay file này với file đã đổi, kết quả thực tế, hạn chế và việc tiếp theo.
5. Sau M0 mới triển khai các lát cắt M1–M6 theo tài liệu SDLC; không coi toàn bộ kế hoạch V2.2 đã hoàn tất.

## Còn lại ngoài đợt này

- Bước tiếp theo M0/S0.2: mở rộng test mounted-hook/error/nhiều tab và browser automation/mobile; xử lý claim login, OCR/AI và đối soát đúng tài khoản/kỳ theo chuẩn 5 tầng. Cache race response cũ, snapshot đổi hộ, cookie System riêng và chuyển hộ hai chiều đã có bằng chứng, không làm lại đợt vừa xong.
- Tiếp đó rà soát OCR (đối chiếu đúng tài khoản/kỳ; đường gọi phép tính), cache và phạm vi hộ gia đình. Chỉ sửa sau khi có kiểm thử tái hiện.
- UI và các insight đang hiển thị; luồng chỉ số/ước tính/hóa đơn thực tế/thanh toán.
- Nhận diện ý định AI, hội thoại, OCR và đối soát, quyền truy cập, dữ liệu cá nhân.
- Các quyết định dữ liệu/nghiệp vụ còn mở trong kế hoạch; không tự di trú hoặc xóa dữ liệu.
- Chưa triển khai production; chưa thay đổi schema, biểu giá thực tế hoặc dữ liệu người dùng.
- Chưa commit/push/merge. Tất cả source và nhật ký đang lưu trên ổ đĩa trong nhánh nêu trên; không dùng `git add .` vì checkout có công việc cũ.

## Câu nhắc để tiếp tục

> Tiếp tục cải thiện Nhà Mình theo SDLC. Đọc website/IMPLEMENTATION_PROGRESS.md trước, giữ toàn bộ thay đổi hiện tại, kiểm tra trạng thái thực tế và làm tiếp mục M0 còn lại; cập nhật nhật ký sau mỗi phần được kiểm chứng.

Lệnh kiểm tra frontend đợt dashboard (cwd `website/frontend`):

```powershell
node --test tests/dashboard-truth.test.cjs
node node_modules/typescript/bin/tsc --noEmit --incremental false
```

## RAG — 2026-10-28 — đang triển khai
- Spec: kế hoạch RAG đã được user duyệt trong chat. Giữ database nghiệp vụ nguyên trạng; kho knowledge riêng PG16 + pgvector, cổng 5435.
- Đã tạo app/knowledge: migration 001, crawler HTTPS chặn IP nội bộ và pin IP/SNI từng redirect, biến đổi/chunk, embedding 768, kho phiên bản, truy xuất hybrid RRF, API admin và CLI scripts/knowledge.py.
- RED: tests/test_knowledge.py lỗi thiếu module; GREEN: 5 passed trên utility_app_test. Chưa phải nghiệm thu toàn hệ thống.
- Docker knowledge-postgres đã chạy, migration thành công; preflight Gemini embedding thật trả 768 chiều. Image đã pin digest trong compose.
- Feature flag vẫn false. Còn: tích hợp chat/UI, dữ liệu crawl thật, kiểm thử PostgreSQL RAG riêng, E2E và tập đánh giá 50 câu.
- Ruling: tái sử dụng checkout nhánh phát triển hiện tại có nhiều thay đổi cũ để giữ runtime đang dùng; không tạo checkout khác làm mất ngữ cảnh local. Không commit/push.
- Ruling: dùng chỉ mục vector qua SQL cast của pgvector để tránh thêm thư viện client không cần thiết; embedding model đổi sẽ không trộn chỉ mục cũ.

### RAG — cập nhật kiểm chứng
- Đã nối StructuredGemini phân loại nhu cầu công khai → hybrid retrieval → natural response; giữ endpoint chat, thêm metadata retrieval/sources/warnings. Khi flag false giữ đường cũ.
- Thêm /admin/knowledge và nguồn trích dẫn trong chat; TypeScript pass, 2 test UI render pass (nguồn RAG đúng link, cảnh báo độ mới bằng tiếng Việt).
- pgAdmin đã nhập đăng ký server RAG qua setup.py load-servers, không replace server cũ.
- Database knowledge_test tách biệt: 5 test PostgreSQL/vector pass, kiểm tra hybrid/keyword degraded, scope/date/stale/pending, hàng đợi idempotent, phân quyền, ingestion idempotent và lỗi embedding không ghi đè phiên bản.
- Regression parser ASP.NET RED→GREEN. Regression metadata ngày ký/phạm vi cơ quan RED→GREEN. Đã quarantine 3 phiên bản giá chưa đủ căn cứ của lượt nhập ban đầu, không công bố giá giả.
- System thật PASS: scripts/knowledge_system.py exercise (Gemini + pgvector + PostgreSQL + refs, số business rows không đổi). API test 8112, UI test 3112, cookie utility_knowledge_refresh. Dữ liệu test ở System DB hiện có, không utility_app.
- Còn: UI browser, bộ truy xuất 50 câu, review toàn phần, kiểm thử hồi quy đầy đủ, bật flag sau nghiệm thu. Chưa công bố hoàn tất.

### RAG — đánh giá & review độc lập
- scripts/evaluate_knowledge.py: 50/50 HYBRID; 40/44 câu có căn cứ đúng đoạn trong top5 = 90,9%; 6/6 câu giá nước chưa có nguồn không lấy giá sai. Đây là tập 2 bài hướng dẫn EVN, không phải chứng nhận độ phủ toàn quốc hay correctness của mọi câu Gemini.
- Final review: agent rag_final_review (read-only) phát hiện 5 vấn đề quan trọng: độ mới của giá cũ khi nội dung thay đổi, scope địa phương không khớp quote, nhầm overlap thành conflict, nguồn tắt vẫn veto, ngày hiệu lực/interval thiếu chặt chẽ.
- Fix pass: 3 regression mới đã quan sát RED; sau sửa 19 test knowledge pass. observed_hash/fetched_at (migration003) tách lần tải với checked_at của nội dung đã công bố. Giá hiện hành không dùng bản active khác nội dung vừa tải. Quote địa phương phải chứa đúng tên chuẩn hóa; ngày phải là biểu thức ngày thật sau cụm hiệu lực, interval phải hợp lệ.
- Conflict chỉ khi cùng category/nhãn/đơn vị/ngày hiệu lực nhưng amount có quote khác nhau; bản hỗ trợ cùng giá và nhóm khách hàng khác không bị coi mâu thuẫn. Schedule mới hơn được ưu tiên theo ngày; truy vấn lịch sử vẫn giữ bản cũ. Nguồn tắt không chặn nguồn đang bật.
- Ruling: price facts chỉ làm kiểm tra bằng chứng và phát hiện mâu thuẫn trong kho công khai, không cập nhật Tariff nghiệp vụ hoặc tính công nợ. Không coi overlap thời gian là chứng cứ mâu thuẫn.
- Còn nghiệm thu browser sau fix, bộ hồi quy cuối, bật và khởi động lại runtime.

## RAG — ĐÃ TRIỂN KHAI LOCAL — 2026-10-28

### Bản đang chạy
- Feature flag KNOWLEDGE_RAG_ENABLED=true trong backend/.env và .local/knowledge-backend.env (ignored). Preflight embedding thật thành công khi bật.
- PostgreSQL RAG container nha-minh-knowledge-postgres, loopback 5435, database knowledge; pgvector 0.8.7, unaccent 1.1. pgAdmin cổng5050 có server public RAG; đã gỡ đúng đăng ký application bị nhập trùng, giữ đăng ký cũ.
- API local chính 8108 được nạp lại bằng scripts/system_test.py serve, PID28652/session30751; giữ nguyên System DB và cookie utility_system_refresh. HTTP chat thật sau restart: HYBRID + ANSWERED + source refs. Không đổi database nghiệp vụ utility_app.
- Worker scripts/knowledge.py worker đang chạy (exec session21180). Lập lịch 6h giá/24h hướng dẫn, hàng đợi xử lý mỗi phút, advisory lock chống chạy trùng. Không bật thêm app.scheduler cùng lúc.
- API thử nghiệm8112 session33114 và frontend3112 session8419 dùng cookie utility_knowledge_refresh; frontend chính3108 vẫn chạy, không đổi origin hay dữ liệu đang dùng.
- Kho hiện có 2 nguồn EVN, 37 tài liệu, 74 phiên bản, 19 chunk bao gồm lịch sử. Đang dùng 4 tài liệu hướng dẫn; biểu giá chưa đủ căn cứ vẫn chờ duyệt. Số lượng raw chunk không tương đương số tài liệu được công bố.

### Bằng chứng cuối
- scripts/test_postgres.py: 142 passed, 2 deprecation warnings của thư viện, trên utility_app_test + knowledge_test; rollback fixture.
- Frontend: TypeScript --noEmit --incremental false đạt; node --test tests/*.test.cjs: 18 passed.
- scripts/evaluate_knowledge.py chạy lại sau fix: 50/50 HYBRID; hit@5 40/44=90,9%; 6/6 câu giá nước thiếu nguồn trả rỗng. .local/knowledge-evaluation.json.
- scripts/knowledge_system.py exercise PASS: câu có nguồn, hỏi tiếp ANSWERED, thiếu nguồn INSUFFICIENT_DATA, ngoài phạm vi OUT_OF_SCOPE, ảnh có extracted_data, số meter_readings/bills/payments không đổi. .local/knowledge-system-result.json và knowledge-chat-result.json. Có một lượt trước đó gặp Gemini503 tạm thời; script nghiệm thu chỉ retry tối đa3 lần, ứng dụng không tạo phân tích giả.
- UI browser: đăng nhập tài khoản test, mở /admin/knowledge, lọc đang sử dụng, chạy truy xuất hybrid, chat VNeID trả lời tự nhiên + link EVN. .local/knowledge-chat-ui.png và knowledge-admin-ui.png. CSS bảng đã xử lý wrap ở viewport nhỏ.
- Docker compose config --quiet đạt. Image pgvector pin digest. Không build/recreate toàn bộ stack Docker nghiệp vụ.
- Code: backend/app/knowledge, scripts/knowledge.py, scripts/evaluate_knowledge.py, scripts/knowledge_system.py; tích hợp ai/multimodal.py + gemini_structured.py; UI knowledge-admin.tsx và chat-answer.tsx. Vận hành/rollback: docs/RAG_OPERATIONS.md.

### Giới hạn và điểm tiếp tục
- Chưa coi corpus ban đầu là phủ toàn quốc; chưa có nguồn nước đủ điều kiện. PDF scan/infographic chưa có chữ đọc chắc chắn giữ pending; không tự OCR nguồn ở phiên bản này.
- Tập50 đo retrieval trên 2 bài hướng dẫn +6 negative water cases; chưa phải benchmark phát sinh câu trả lời số liệu biểu giá. Trước khi công bố tài liệu giá, cần kiểm tra ngày/phạm vi/price facts với bản gốc. Không thay Tariff/Bill/Payment tự động.
- Parser hash v3 giữ các lượt nhập cũ làm lịch sử, không xóa để đẹp số liệu. Có thể mở rộng nguồn chính thức qua giao diện admin, không sửa hardcode câu trả lời.
- Không commit/push/merge; giữ thay đổi cũ của user. Khi tiếp tục đọc mục RAG này trước; kiểm tra runtime thực tế, không chạy prepare System DB lần nữa hoặc đổi sang database Docker nghiệp vụ cũ.
- Final review: đã xử lý 5 finding quan trọng bằng regression tests; không có minor bị trì hoãn từ reviewer. Không yêu cầu review agent thứ hai.

## Bổ sung NƯỚC — 2026-10-28 — thay thế giới hạn chỉ có EVN
- User chỉ ra còn thiếu nguồn nước. Đã xác minh chính thức các trang SAWACO (cskh.sawaco.com.vn/ho_tro/hoi_dap và bài giới thiệu dịch vụ/ứng dụng CSKH trên sawaco.com.vn).
- Migration004 thêm seed_mode DOCUMENT/LISTING, utility và service_area. Crawler đọc URL tài liệu nước trực tiếp; không ép mọi nguồn theo đường dẫn bài EVN. UI nguồn có cách thu thập, điện/nước và khu vực phục vụ; sửa payload edit không gửi id/checked_at thừa.
- Backend gắn WATER + service_area ho chi minh cho SAWACO; truy vấn có địa phương khác không lấy hướng dẫn SAWACO để áp dụng. Test direct URL nước RED→GREEN; test giới hạn nước/điện và HCM/Thái Nguyên đạt.
- Phát hiện qua thực nghiệm Gemini400: maxItems=100 trong schema nested price_facts bị từ chối. Bỏ constraint khỏi JSON schema, vẫn giới hạn100 bằng Pydantic field_validator. Probe no_facts/unbounded_facts/bounded_number đềuHTTP200, nhập thật hết lỗi schema. Hai lượt nhập lỗi cũ giữ trong lịch sử, không tạo kết quả giả.
- Đã crawl 2 nguồn SAWACO. Tài liệu dịch vụ được đọc/duyệt GUIDANCE và công bố với embedding thật. Trang giá nước/hỏi đáp còn PENDING_REVIEW vì thiếu căn cứ hiệu lực/phạm vi/giá cần xác minh; không công bố thành giá hiện hành cả nước.
- Backend sau thay đổi: 144 passed trên PostgreSQL test; TypeScript đạt. Bằng chứng System riêng của nước ở .local/water-acceptance.json sau khi script kết thúc, không đưa nội dung test vào prompt runtime.
- API local8108 đã nạp lại PID65056/session91318. Worker mới session22375 có hỗ trợ nguồn DOCUMENT và các trường phạm vi; worker cũ21180 đã dừng.
- Kết quả System nước cuối: ANSWERED có link SAWACO; giá hiện hành Thái Nguyên và TP.HCM đều INSUFFICIENT_DATA, không có nguồn giá giả. .local/water-acceptance.json đã ghi thành công. Frontend 18 tests đạt. Phần nguồn nước đã có; độ phủ vẫn giới hạn nhà cung cấp được đăng ký, chưa chứng nhận biểu giá hiện hành.

## Sửa Docker đăng nhập / localhost — 2026-10-28 22:34

### Tiếp tục: không lưu được chỉ số — 2026-10-28

#### Nhập tháng9 và toast — 2026-10-28

##### Gemini-only và Docker config — 2026-10-28

###### Tối ưu free tier / Flash Lite — 2026-10-28

####### Tổng quan sau nhập chỉ số — 2026-10-28

######## Hoàn thiện tính tiền / hóa đơn / Gemini — 2026-10-29
- User yêu cầu xử lý thực tế. Xác minh bảng giá nguồn EVNSPC hiện công bố QĐ1279/QĐ-BCT, nguồn Chính phủ xác nhận áp dụng10/05/2025; trang EVN giá điện hiện hành vẫn tham chiếu quyết định này. Không thay biểu giá demo, không sửa provider/category của tài khoản hộ.
- app/tariff_import.py đọc bảng residential JS literal qua crawler đã có, chọn cột GIÁ MỚI, xác minh bậc liên tục/open-ended; không nhúng đơn giá vào code. scripts/prepare_evn_billing.py tải liveEVN, lưu .local/knowledge/evn-billing-original.html và evn-billing-verified.json gồm sourceURL,effectiveSourceURL,date,hash,unit,VATfalse. scripts/apply_evn_billing.py kiểm hash và parse lại so catalog trước khi nhập.
- Nhập Tariff EVN RESIDENTIAL_1PHASE NATIONAL (provinceNone), version1279-2025-verified, tiers từ tài liệu. Bằng chứng lưu AuditLog actionVERIFY_TARIFF_SOURCE, actor existingADMINowner; BillingService.create chụp source vào tariff_version_snapshot. Đây là import nghiệp vụ được user yêu cầu và agent xác minh, không phải tự động công bốRAG rồi sửa biểu giá.
- Thêm HouseholdService.generate_bills và POST/api/bills/generate: chỉ hộ hiện tại có quyềnwrite, khóa account, bỏ qua kỳđãcóbill, không thay hóa đơn paid, báo skippedmissing/ambiguous. Không tạo lại chỉ số. UIHóađơn có nútTính hóa đơn từ chỉ số và toast/result, ghi rõước tínhchưathuế, linknguồn trongdetail.
- Đã tạo THẬT cho đúng hộ người dùng:09/2026 consumption1500 →4.880.500VND;10/2026 consumption722 →2.188.620VND. SYSTEM_ESTIMATE, trướcVAT/phí, chưaofficial/chưathanh toán. LưuPostgreSQLDocker; chạyapplylạicreated[],skipped[],khôngtrùng. Không tác động24billdemo hộkhác. Không tự cấu hình nướcThiênLong thiếu nguồn.
- Gemini overview bill_context bổ sungtax_note/tariff_source. Phát hiện câu privateinvoicehỏithuế bịrouterđưaquaRAG khiếnemptypublicsourcechặnprivatebill. Sửa public_query: câu tiềnđiện/nước/hóađơnriêng không explicitđơngiá/thuếsuất/quyđịnh thì đọc dữ liệu hộ; hỏi luật/thuếsuất vẫnRAG.
- scripts/check_existing_billing.py read-onlyrollback hội thoại kiểm thử, xác minh tổngtiers=final,statisticslatestcost=billamount,AgentGeminiANSWERED vàcitebillđúng. Nghiệm thu THẬT đãPASS: Gemini trả tiềnđiện2026-10=2.188.620đồng,chưabaogồmthuếphí. Không thay nội dung bằng câu mẫu. Cuộc hội thoại testrollback, hóađơn nghiệp vụ đãcommit.
- TestPostgreSQLfulltrướcsửarouter178passed,1deselected(lỗiRAGcũ); sauthayđổicuối47tests billing/import/Gemini/multimodal/quota đạt. Importtransform2tests dùngratesfixturekhác nguồn thật để chứng minh khônghardcode vàrejectgap/incomplete. Backfilltest missing→configured,2kỳ,scope,idempotency,paidunchanged. DockerbuildfrontendTypeScriptđạt,backendhealthy;UIthậtphiênuserchưađượcthao tác lại.
- Thuế/phí chưa có chính sách cấu hình được xác minh nên sốtiền làsubtotalước tính, đã ghi rõ ởUI/snapshot/Gemini. Chưa tự động backfillmọihộ khiadminthêmgiá; usercóthểbấm nút tạochohộhiệntại. Sourcecatalogupdatephảireview,không chạyimportscriptmùkhi quyếtđịnhđổi. Điểmtiếptục:thuế/phí theo kỳ,UIbrowsernghiệmthu,nguồnnước đúngnhàcungcấp.
- User hỏi Docker mất dữ liệu/hardcode. Đọc PostgreSQL Docker xác nhận hộ có đúng2readings (09/2026=1500consumption,10/2026=722),0bills. Không phải hóa đơn đã thêm; màn hình user gửi là lịch sử chỉ số. Docker mount named volume nha-minh-utilities_postgres_data tại /var/lib/postgresql/data, không xóa/đổi volume.
- Dashboard lấy số tiền từ bills, usage từ APIstatistics. Khi chưa có biểu giá phù hợp, chỉ số vẫn lưu theo thay đổi trước nhưng không tạo bill; costnull đúng, nhãn Chưa có dữ liệu gây hiểu lầm. Không thay biểu giá/nhà cung cấp/số tiền để lấp dữ liệu.
- Thêm ReadingBillingNotice dùng readings/bills/summary thật: đã lưu Nchỉsố, chưa có hóa đơn, nêu kỳ và lượng dùng, giải thích tiền chưa biết không đồng nghĩa0, link đọc chỉ số/bills. Khi chưa có cost nhưng có usage, thẻ điện/nước hiện lượng dùng chính thay vì Chưa có dữ liệu; totalcostnull nhãn Chưa có hóa đơn.
- Typecheck đạt; frontend28tests sẵn có đạt,3SSRtests mới notice đạt (số thực,zero,không hiển thị nhầm khi có bills). PostgreSQL2tests missingtariff/statistics đạt: latestOctoberELECTRICITY722,costnull,WATERnull. Fixture rollback, không tạo bill/nhập thêm dữ liệu hộ thật.
- Dockerfrontend rebuild production đạt, session25473 xem completion. Chưa đăng nhập phiên thật user để kiểm tra visualdashboard; không khẳng định đã nghiệm thu UI bằng tài khoản user. Reload Tổng quan để nhận bundle mới.
- User cho phép chọn model thấp hơn, ưu tiên nhiều câu hỏi và tốc độ, vẫn chỉ nhận câu Gemini sinh. Đã xác minh official models/gemini-3.5-flash-lite hỗ trợ ảnh/structured outputs; API list key thật có3.1/3.5FlashLite. Probe3.5 trả200JSON hợp lệ (khoảng15–18s cho probe nhỏ),3.1 gặp503 cả probe và luồng đầy đủ. Không hứa tốc độ cố định/free unlimited.
- Chọn GEMINI_MODEL=gemini-3.5-flash-lite trong backend/.env và sync sidecar Docker allowlist. Model code/default/env.example đã đồng bộ. Chat response maxOutputTokens8192→2048, Flash Lite dùng thinkingLevel=minimal (đã probe200), không dùng thinkingBudget không tương thích. Giữ extraction/metadata budget8192 để tránh cắt dữ liệu hóa đơn/bảng giá.
- Rút prompt respond lặp dài thành chỉ dẫn gọn, giữ phạm vi/không bịa/không tự ghi/tham chiếu/đối chiếu ảnh/phân biệt estimate và ngày hiệu lực. Không bỏ overview6kỳ, tổng nợ đầy đủ hoặc50hóađơnchi tiết. Chat thường vẫn1generation; ảnh vẫn2bước và câu tiếp nối không đọc lại ảnh.
- Migration knowledge005 tạo provider_limits(scope SHA256(key+model),state JSONB). Rolling window12calls/60s và cooldown dùng PostgreSQL clock/advisory transaction lock, chung các tiến trình backend/worker dùng kho này. Reserve trước mọi generate attempt kể cả retry503. Không dựa RAM nên restart không mất cooldown; không lưu key/prompt/dữ liệu hộ ở bảng. Không bao phủ ứng dụng ngoài cùng project, không mở rộng quota Google.
- Parse Retry-After/RetryInfo/QuotaFailure thành wait/kind (REQUESTS/TOKENS/DAILY/UNKNOWN), log chuẩn hóa không raw response/key. API429 có retry_after và Retry-After. Khi Google không cung cấp wait dùng60s bảo thủ; không coi đây là thời điểm chắc chắn quota ngày reset.
- Frontend truyền code/retryAfter từ API; sendingRef chặn bấm gửi trùng khi render chưa cập nhật; nút gửi khóa với đếm ngược khi429. Backend còn chặn được retry sau reload. Không thêm canned answer/failover vòng model hay semantic cache riêng tư.
- Test quota3unit đạt +1PostgreSQLsharedwindow/cooldown: từ chối không tiêu thêm slot, expiry, pause và providerRetryInfo. Conftest ép guardfalse cho mocktests, tránh mock tests chạm runtime store. PostgreSQL176passed,1deselected (lỗi RAG phạm vi/freshness đã biết). Sau rút prompt68testsGemini/multimodal/schema/quota đạt; frontend28tests và production TypeScript/build đạt.
- SystemDocker key/model mới: lần đầu prompt dài timeout25s; sau rút prompt, check_reading_docker CHECK_GEMINI=1 đã PASS phân tíchWATERfixture và followup tiền nước, providergemini, không bịa biểu giá; toàn bộ fixtures rollback, business counts trước/sau bằng nhau. 3.1 trả503 nên không chọn. Đây là nghiệm thu text+followup thật; chưa chạy ảnh thật lại với model mới trong lượt này.
- Backend/frontend/scheduler đã rebuild; final backend/scheduler cosmetic log/config rebuild session51680. Migrate đã áp dụng knowledge005 thật. Vận hành: khi đổi Gemini settings chạy python scripts/sync_gemini_docker.py rồi docker compose up -d --force-recreate backend scheduler; khi có migration mới chạy python scripts/knowledge.py migrate trước. Không ghi secrets vào log.
- Chưa làm answer cache, streaming, hay đổi lịch ingestion; không tuyên bố triển khai các phần này. Điểm tiếp tục: quan sát latency/quota thực tế và kiểm thử ảnh thật trên Flash Lite, xử lý riêng lỗi RAG cũ.
- User phát hiện câu trả lời nội bộ/canned và greeting sai ngữ cảnh. Root cause Docker runtime provider=deterministic,key_present=False,model=gemini-2.5-flash; compose environment mặc định rỗng ghi đè key trong backend/.env. Multimodal bắt lỗi provider và local_reply tạo câu nội bộ, còn lưu vào CHAT_CONTEXT.
- Loại bỏ local_reply khỏi pipeline runtime. Extract/respond/schema/evidence failures trả DomainError tương ứng; không tạo câu phân tích hoặc CHAT_CONTEXT giả. Search/retrieval có thể trả thiếu căn cứ cho Gemini diễn đạt, không thay Gemini bằng câu mẫu. Agent offline deterministic chỉ còn cho APP_ENV=test explicit.
- Dùng scripts/sync_gemini_docker.py xuất đúng5biến allowlist LLM_PROVIDER,GEMINI_API_KEY,GEMINI_MODEL,GEMINI_SEARCH_ENABLED,GEMINI_TIMEOUT_SECONDS vào .local/gemini-backend.env (gitignored). Compose đọc sidecar này thay các environment default rỗng. Không đưa toàn bộ backend/.env vào shared env_file; auto-review đã từ chối phương án rộng, đã sửa bằng allowlist. Không in/ghi key vào nhật ký.
- Runtime sau recreate:provider=gemini,model=gemini-3.5-flash,key_present=True,RAG=True. Backend/scheduler đã rebuild/recreate. Khi đổi Gemini config, chạy sync_gemini_docker.py rồi docker compose up -d --force-recreate backend scheduler.
- Log ERROR lưu code+request_id (không prompt/key), server warning cùng mã. Frontend gắn nhãn Gemini chưa trả lời và role=alert cho lỗi, không render như kết quả ChatAnswer.
- Test mới RED4→GREEN5: key/quota/timeout/schema lỗi trả503/429/504/502, không message phân tích, không CHAT_CONTEXT; happy path giữ đúng message provider và lịch sử2turn. Cập nhật các test trước đó yêu cầu fallback sang hợp đồng Gemini-only; giữ bounded retry/ảnh/evidence/phân quyền.
- PostgreSQL hồi quy172passed,1deselected (lỗi RAG test_excludes_wrong_scope_future_pending_and_stale đã biết, không được tính đạt). Docker production build trước nhãn lỗi đã đạt; frontend label build xem kết quả session44857.
- System Gemini THẬT: scripts/check_reading_docker.py qua docker exec -e CHECK_GEMINI=1 -i kiểm tra fixture rollback, nhận429 GEMINI_QUOTA từ provider. Chưa xác nhận được câu Gemini thành công/followup thật vì hạn mức dịch vụ. Không đổi model/key để né quota, không giả thành công. Có thể chạy lại đúng lệnh sau khi quota/provider phục hồi; mọi fixture users/readings/bills rollback.
- Tin nhắn canned cũ có thể vẫn nằm trong lịch sử browser. Không xóa dữ liệu hội thoại của user; nên bắt đầu Cuộc trò chuyện mới sau reload để kiểm tra luồng mới.
- Screenshot kỳ09/2026 nhập2334 nhưng kỳ10/2026 đã ghi2222: backend chặn đúng thứ tự công tơ tích lũy. Không nới điều kiện cho phép tiêu thụ âm hoặc tự sửa chỉ số thật.
- Phát hiện Application có toast state/notify/timer nhưng JSX chưa render toast. Thêm NoticeToast dùng CSS hiện có, role=status, nút đóng, hiển thị9s, giới hạn chiều rộng trên mobile. Catch lỗi lưu chỉ số nay gọi cả setSaveError và notify.
- API lỗi backfill nêu cụ thể kỳ đang nhập, số nhập, kỳ sau và số đã ghi cùng hướng xử lý. Không ghi secret hoặc dữ liệu riêng vào console. Inline error vẫn tồn tại sau khi toast đóng.
- Kiểm thử PostgreSQL27passed gồm tháng10=2222, nhập tháng9=2334 trả400 có đầy đủ hai kỳ/số; tháng9=2000 lưu201 và tháng10 được tính lại previous2000/consumption222. Fixture rollback, không nhập vào dữ liệu user.
- Toast SSR2tests đạt, typecheck đạt, Docker backend/frontend build và recreate thành công. Chưa thực hiện lại thao tác bằng phiên đăng nhập thật của user trong trình duyệt. Reload localhost3000/readings để nhận bundle mới.
- Log Docker cho thấy POST /api/readings409 liên tục. Database Docker có tài khoản nhà cung cấp/nhóm không khớp biểu giá cấu hình. BillingService.create ném TARIFF_NOT_FOUND khiến transaction rollback cả MeterReading; lỗi frontend chỉ toast khó thấy.
- Sửa HouseholdService.reading: chỉ bắt TARIFF_NOT_FOUND, lưu chỉ số/consumption thật và trả bill:null,billing_status:TARIFF_NOT_FOUND. Không tạo tiền/biểu giá giả; TARIFF_AMBIGUOUS và các lỗi khác vẫn rollback. BILL_CREATED chỉ phát khi có hóa đơn.
- UI có busy/timeout20s và lỗi/thông báo ngay biểu mẫu; nút Lưu chỉ số, thông báo có/không tạo hóa đơn theo response thật. Hướng dẫn không còn cam kết luôn tạo hóa đơn. Chưa có tác vụ tự tạo lại hóa đơn cho các chỉ số đã lưu trước khi quản trị cấu hình biểu giá.
- RED→GREEN test_reading_without_tariff: lưu decimal125.5,consumption25.5,billnull,history1 và duplicate409. Cập nhật hai regression theo hành vi mới, giữ kiểm tra ambiguous rollback/không notification hóa đơn giả.
- PostgreSQL test:166passed,1deselected. Test RAG test_excludes_wrong_scope_future_pending_and_stale đang thất bại độc lập ở fullrun; tách khỏi kiểm thử cuối, chưa sửa trong phạm vi lỗi chỉ số. Không tuyên bố toàn suite đạt.
- System thật trong container: scripts/check_reading_docker.py chạy qua docker exec -i, TestClient+PostgreSQL transaction rollback; chỉ số WATER2223 lưu201,consumption2223,billnull,history1; users/meter_readings/bills đếm trước/sau không đổi. Không tự nhập2223 vào công tơ thật của user.
- Typecheck và Docker production build đạt. Đã rebuild/recreate backend/frontend cổng3000, backend healthy. User cần reload trang readings để nhận bản mới.
- User yêu cầu kiểm tra Docker3000 bị treo và tắt3108. Đã dừng đúng Next.js PID60020; kiểm tra listener3108 cuối:0.
- Bằng chứng nguyên nhân: frontend container là build cũ4tuần, bundle gọi http://localhost:8000/api. Preflight từ http://127.0.0.1:3000 nhận400 Disallowed CORS origin. IPv4 trang login200, IPv6 localhost timeout6s.
- Chuyển frontend Docker sang NEXT_PUBLIC_API_BASE_URL=/api; Next rewrite tới http://backend:8000 bằng INTERNAL_API_URL lúc build. Dockerfile nhận buildarg; không mở rộng CORS. Đăng nhập/đăng ký và refresh có timeout15s để thoát busy khi mất mạng.
- Nhận diện listener riêng ::1:3000 thuộc dllhost PID33428, module C:/Program Files/WSL/wsldevicehost.dll; chỉ distro docker-desktop đang chạy. Dừng đúng forwarder WSL kẹt, không shutdown Docker/WSL hoặc xóa volume. Sau đó localhostIPv6 HTTP200 ~0.047s,127.0.0.1 HTTP200 ~0.026s; localhost:3000/api/health trả status:ok. Nếu tái diễn sau restart, xác minh lại PID/module trước khi xử lý, không dùng PID cũ.
- Đã chạy docker compose up -d --build frontend, rồi --build --no-deps frontend để nhận bản timeout cuối. Build production/TypeScript đạt, frontend container mới đang chạy; backend/postgres/knowledge-postgres healthy. Không down -v, không đổi database/credentials.
- System/API: POST localhost/127.0.0.1:3000/api/auth/login với tài khoản không tồn tại trả401 INVALID_CREDENTIALS ngay. UI thật localhost3000 hiển thị lỗi và nút Đăng nhập ngay hoạt động lại. Không sử dụng hoặc đổi mật khẩu thật; chưa chứng nhận đăng nhập thành công bằng tài khoản của user.
- Frontend26tests đạt, gồm2test mới same-origin timeout và refresh thất bại rồi phục hồi. Typecheck --incremental false đạt. Ảnh bằng chứng .local/docker-login-fixed.png. Các thay đổi khác trong working tree có sẵn, không reset/commit.
- Điểm tiếp tục RAG: viewer/readiness, focus/scroll, sửa/lưu/bật/tắt nguồn đã thử browser3112; API tải67617bytes, reject unverified422, hybrid8đoạn đạt. Backend146tests PostgreSQL đạt sau dùng basetemp mới. Crawler literal JS table đã thêm test; EVNSPC được đăng ký và nhập, nhưng chưa chứng nhận giá hiện hành. Không tuyên bố hoàn tất nghiệm thu biểu giá. Bước summary/form cuối lượt trước bị auto-review hếtquota nên không thực thi; phải kiểm tra diff trước khi tiếp tục.


## 2026-10-28 — Portable Docker and Git hygiene

- Compose no longer requires .local or backend/.env. Startup migrates both PostgreSQL databases, registers three electricity/water sources and imports versioned public EVN tariff idempotently. No demo users, households or readings are seeded.
- Named volumes persist DBs, knowledge archive, pgAdmin and generated JWT. Existing credentials preserved in ignored root .env (no values logged). First registered account becomes ADMIN only under explicit local-development flag; subsequent accounts are USER.
- pgAdmin starts by default with tracked password-free registry. Frontend/pgAdmin readiness checks support --wait. README/DOCKER_GUIDE and launchers updated; optional Gemini key remains private.
- Ignore rules exclude local configuration, generated artifacts and agent tooling. 172 previously tracked .agents files removed from Git index only; local copies retained. Added redacted path/credential-pattern scanner scripts/repo_audit.py; this does not audit all Git history.

Evidence:
- Exported proposed Git source set to .local/clone-smoke/source without .env/local data. Built isolated project nha-minh-clonecheck with fresh volumes and ports 3210/8210/5440/5441/5060, no personal key or config. All six services started; production frontend build passed. Frontend login and pgAdmin HTTP200.
- Initial users=0, bills=0, tariff=1, RAG sources=3. First registration ADMIN; onboarding plus September 1500/October 2222 readings created two estimated bills: 4,880,500 and 2,188,620 VND before tax/fees. Second registration USER.
- Test-project down then up --wait preserved login, both bills and single tariff. Missing Gemini key returns HTTP503, no fabricated answer.
- Applied new Compose to main stack after copying 162 archive files into knowledge_archive volume. Before/after counts unchanged: users=2, meter_readings=26, bills=26. Existing household September/October amounts unchanged. Gemini key retained outside Git. Existing pgAdmin registry now uses Docker service DNS.
- Backend tests/test_docker_bootstrap.py: 2 passed. repo_audit.py: 525 source paths, 0 blocking findings. Full pre-existing regression suite not rerun for this infrastructure slice.

Continuation:
- No commit or push performed. Include new code/config/catalog files in eventual commit; never include .env/.local. Audit proposed source again before push.
- Each developer supplies their own Gemini key/quota to enable AI/crawling; ordinary billing works without it. Registered sources are not a pre-populated RAG corpus. Water tariffs need verified provider/locality data.
- Isolated smoke volumes retained as disposable evidence; do not delete main data volumes. Existing unrelated work preserved.


## 2026-10-29 — Water knowledge ingestion

Request: crawl actual public water data so Gemini can answer from RAG.

Diagnosis: existing water corpus had one general service article and one pending SAWACO pricing FAQ. Precision HTML extraction dropped FAQ lists/questions and HAWACOM effective-date/customer-condition text. SAWACO tariff itself is an image, not a readable HTML price table. DAWACO FAQ currently returns a JS shell; thawaco.vn failed TLS certificate validation. No TLS bypass used.

Changes:
- Preserve FAQ accordion questions, lists and explicit HAWACOM content sections; normalize whitespace without losing numeric values, customer conditions or tax/fee notices. Preserve questions inside accordion buttons.
- Support a registered document URL fragment as a separately versioned FAQ section, retaining its source URL and full original HTML archive. Missing section fails explicitly instead of ingesting unrelated page content.
- Bootstrap registers official HAWACOM Hanoi prices, SAWACO online services and a four-section SAWACO meter/service FAQ source. These water sources use DOCUMENT mode, not EVN-only article-link discovery.
- Pricing without an explicit effective date stays PENDING_REVIEW even when locality is known.

Live evidence:
- Real crawler -> Gemini metadata -> Gemini embedding -> PostgreSQL pgvector ingestion executed. Active water corpus grew to six published documents including HAWACOM effective 2026-01-01 (Hanoi) and SAWACO registration/meter-seal/replacement guidance. Raw HTML and versions retained.
- HAWACOM price facts are checked against source text; three numeric facts verified on the final import. Keep full original table/customer conditions as retrieved evidence.
- HYBRID retrieval returned HAWACOM for Hanoi prices and ranked SAWACO meter-replacement FAQ first for that question. Thai Nguyen price query returned EMPTY rather than borrowing Hanoi prices.
- Relevant unit/API tests: knowledge + water + local bootstrap 18 passed; final knowledge + water run 16 passed. Regression tests first reproduced missing effective dates and missing fragment support before fixes.
- Main business row counts remain meter_readings=26, bills=26, payments=20. Scheduler restored with updated code.

Remaining limits:
- SAWACO full price FAQ still pending: tariff in image and no verified effective date. No guessed price was published. FAQ section collapsePricing19 repeatedly hit bounded Gemini timeout; source crawl remains PARTIAL with errors visible; existing successful documents remain active.
- No verified Thai Nguyen water price imported because provider TLS failed. Hanoi/Ho Chi Minh evidence must not be presented as nationwide water prices.
- Final chat acceptance evidence, when successful, is saved without credentials in ignored .local/water-rag-acceptance.json. No new commit/push.

Final acceptance: frontend proxy POST /api/ai/chat returned HTTP200, status ANSWERED, provider gemini, retrieval HYBRID/FOUND without warnings; response included HAWACOM source/version and the residential tiers, preferential first-tier condition and VAT/fee exclusions. Saved .local/water-rag-acceptance.json contains no login credentials. Repository path/credential-pattern scan: 525 paths, zero blocking findings.


## 2026-10-29 — Thai Nguyen water query correction

User screenshot: generic "giá nước thái nguyên" was answered as if specifically asking the household provider Thiên Long, with no evidence available.

- Found working official alternative domain nuocsachthainguyen.vn (TLS/robots checks retained). Crawled actual notice Content.aspx?tab=news&lang=vi&pid=1&cid=1&id=6778: water rates effective 15/10/2026 under decision 3169/QĐ-UBND, with separate privatized/non-privatized supply areas, customer groups, exemptions and tax/fee exclusions.
- Registered source in Docker bootstrap for future clones. Ingestion succeeded, one PUBLISHED version with WATER / thai nguyen / effective_from 2026-10-15. Original HTML, ordered regional tables, source URL and chunks archived in RAG. Extracted numeric price_facts remained empty after strict quote verification; full sourced tables remain evidence, not a business tariff import.
- Preserved legacy news_detail_detail content in original order; recognizes explicit "kể từ" effective dates while still rejecting mismatched dates. Gemini instructions distinguish generic public/locality queries from a household account's provider; no household provider or tariff was changed.
- Regression proof: added tests first reproduced unsupported effective-date wording; water/knowledge/public-tariff/multimodal tests: 39 passed. TLS validation was not disabled and no price numbers were hardcoded into application logic.
- End-to-end acceptance output is saved to ignored .local/thai-nguyen-water-acceptance.json when the final HTTP chat check succeeds. No commit/push performed.

Final verification: exact screenshot query "giá nước thái nguyên" through frontend API returned HTTP200 / ANSWERED / gemini, with nuocsachthainguyen.vn citations and both supply-area schedules. Response did not assign Thiên Long. Evidence saved to .local/thai-nguyen-water-acceptance.json. Scheduler restored with --no-deps. Business counts unchanged: meter_readings 26, bills 26, payments 20. Source-set scan: 525 paths, zero blocking findings.


## 2026-10-29 — Publish cleaned website source to AI-House

User authorized cleaning and pushing website to https://github.com/nvmanh206/AI-House.
- Confirmed origin and remote main match the local initial commit before publication; preserve history and use fast-forward push only.
- Excluded local experiment a.py, skill installation helpers, skills-lock and personal CLAUDE tooling from the proposed tree; retained local files. Existing .agents tracked files removed from index. Application source, migrations, public tariff catalog, Docker config, lockfiles, tests and project docs retained.
- IMPORTANT: a.py in the initial commit already contained an embedded API credential. Removing the file from the new tree does not remove it from existing remote history. Owner must revoke/rotate that old key; history was not rewritten.
- Extended source audit for AQ-style and GitHub token formats. Final targeted checks: frontend node tests 31 passed; backend chat/public tariff/multimodal/knowledge/water/bootstrap 41 passed; docker compose config -q passed. DOCX project reports checked for embedded Gemini credential patterns without displaying values.
- Publication uses a normal commit and push HEAD:main; no force-push, no database or env files included. GitHub main verification follows push.
