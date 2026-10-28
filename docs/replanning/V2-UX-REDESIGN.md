# V2.2 — Thiết kế lại trải nghiệm Nhà Mình

Ngày 27/10/2026 · Bản đề xuất V2.2 Product/UX · Chưa được người dùng phê duyệt.
Phạm vi: quy hoạch, không sửa sản phẩm, dữ liệu, migration hoặc cấu hình.
Đọc cùng [Master](V2-MASTER-PLAN-IMPROVED.md), [Backlog](V2-IMPROVED-BACKLOG.md), [AI](V2-AI-ARCHITECTURE.md), [So sánh và decision register](V2-REVIEW-COMPARISON.md).

## 1. Cách đọc bằng chứng

- **CURRENT VERIFIED**: hành vi nhìn thấy trong mã nguồn hiện tại; không đồng nghĩa đã chạy thành công.
- **PROPOSED**: thiết kế mục tiêu, số bước và điều kiện nghiệm thu chưa triển khai.
- **DECISION REQUIRED**: lựa chọn ảnh hưởng nghiệp vụ/phạm vi cần chốt trước phần code liên quan.
- **DEFERRED**: giữ ngoài bản đầu, không dựng affordance giả.
- “Giả thuyết đau điểm” là suy luận từ cấu trúc, chưa phải kết quả phỏng vấn hay usability test.
- Chưa có inspection rendered đáng tin của checkout: parent thử localhost nhưng phiên browser có đường dẫn/phiên bản khác; không gán lỗi build đó cho dự án này. Không khẳng định màu thực tế, tương phản, vỡ layout hoặc tốc độ.
- Đường dẫn nguồn dưới đây tương đối `website/`; `A` = `frontend/components/application.tsx`.
- Đã đọc hai kế hoạch cũ và tổng quan gốc; tổng quan là tài liệu mô tả, mã nguồn quyết định CURRENT.
- Kết quả test trong kế hoạch cũ là lịch sử của phiên trước, không phải chứng nhận UX hiện tại.

## 2. Phản biện tiền đề trước khi vẽ màn hình

**CURRENT VERIFIED:** nav đặt Nhập chỉ số ngay sau Tổng quan (`A:39–40`; `components/layout/AppLayout.tsx:50–59`).
Onboarding đi qua Gia đình → Điện → Nước → Xác nhận (`A:621–624`), chỉ có bỏ qua nước.
Reading ghi một lần rồi tạo hóa đơn ngay (`A:976`); tài liệu/ảnh đi qua chat (`A:1143–1210`).
Kế hoạch cũ vẫn nghiệm thu G2 bằng nhập tay, OCR G4 (`2026-10-27-phan-tich-va-quy-hoach-v2.md:402–406`).

**Giả thuyết:** cấu trúc này buộc hộ muốn lưu khoản điện nước phải học công tơ, biểu giá và kỳ trước khi có giá trị.
Không có nghiên cứu người dùng chứng minh mọi hộ sẵn sàng tự ghi chỉ số hàng tháng.
Tăng độ chính xác calculator không tự giải quyết việc thu thập và tìm lại hóa đơn.
Upload nằm trong chat làm bằng chứng tài chính khó tìm lại và khiến nhập liệu phụ thuộc cuộc hội thoại.

**PROPOSED — HYBRID TASK-FIRST:** không gian chung giúp hộ theo dõi mức dùng, ước tính và xử lý khoản thực tế; giữ cả mục đích đo/ước tính trong PRODUCT.md lẫn nhu cầu lưu hóa đơn. Ba cửa vào ngang khả năng truy cập: **Thêm hóa đơn/tệp**, **Ghi chỉ số/ước tính**, **Ghi nhanh khoản thực tế**. Không có nhánh bắt buộc đi qua OCR hoặc chat. Chọn mục tiêu ban đầu chỉ cá nhân hóa gợi ý, không khóa hai nhánh còn lại.
Nhánh record-only có giá trị lưu tiền/hạn nhưng không đủ bằng chứng giải thích biến động lượng dùng hay nguyên nhân tiêu thụ. Nhánh reading-only có lượng dùng/phân tích/estimate đủ điều kiện dù chưa có invoice; thiếu tariff vẫn lưu phép đo hợp lệ và xem lượng dùng, chỉ phần tiền ở `estimate_pending/not_computable` có lý do. Nhánh hybrid liên kết estimate với actual mà không cộng hai lần hoặc sửa lịch sử.
AI giảm nhập lại và giải thích căn cứ; form và trạng thái dùng được khi AI không hoạt động. Không yêu cầu biểu giá để ghi số tiền thực tế người dùng xác nhận; lưu khoản cũng không chứng minh calculator đúng.

**DECISION REQUIRED:** R01 định vị hybrid này chưa được duyệt; D01/D02/R02/R05 vẫn giữ nghĩa trong decision register. R06 quyết phạm vi định dạng sau nghiên cứu mẫu: JPEG/PNG là baseline candidate; PDF có text là early candidate nếu evidence cho thấy giá trị/độ an toàn phù hợp, không mặc định hỗ trợ và không mặc định hoãn toàn bộ PDF.
Không có bằng chứng API provider hoặc đọc email tự động đã được cấp; không đưa vào hành trình mặc định.
**DEFERRED:** scrape email, đồng bộ EVN/nước tự động, gateway, IoT, chia tiền phòng, trả góp/hoàn tiền.

## 3. Kiến trúc thông tin theo việc cần làm

**PROPOSED — điều hướng chính:**
1. **Hôm nay**: việc cần kiểm tra, khoản sắp hạn, tiếp tục bản nháp, lịch ghi số; tóm tắt chi phí và mức dùng có nguồn riêng.
2. **Hồ sơ điện nước**: chứng từ, khoản ghi nhận, ước tính, lịch sử ghi nhận đã trả; cùng account/kỳ.
3. **Mức sử dụng**: lịch sử đo, nhập chỉ số, so sánh, dự báo; không ép bật trong onboarding.
4. **Thêm**: hộ, tài khoản tiện ích, thành viên, cài đặt; admin là workspace riêng khi có quyền.
Trợ lý mở theo ngữ cảnh hồ sơ/biểu đồ và vẫn có trang hội thoại đầy đủ từ mục Thêm.
Thông báo truy cập bằng chuông, việc cần xử lý xuất hiện ở Hôm nay; không nhân đôi số việc.

Header luôn có tên hộ và bộ đổi hộ; kỳ/bộ lọc chỉ xuất hiện khi có ý nghĩa với trang hiện tại.
Cụm “Thêm dữ liệu” luôn đưa ba lựa chọn cùng cấp: “Hóa đơn/tệp”, “Chỉ số/ước tính”, “Khoản thực tế”. Desktop hiện ba nút; mobile mở cùng một sheet có ba mục ngay lần mở đầu. Không giấu ghi chỉ số trong menu phụ của upload.
“Hồ sơ” có tab Tất cả / Cần kiểm tra / Chưa ghi nhận trả / Đã ghi nhận trả, lọc account/kỳ/nguồn.
Chi tiết hồ sơ dùng ba miền: nội dung chứng từ, khoản tiền/hạn, lịch sử bằng chứng/hành động.
Không dùng một badge PAID cho cả chất lượng OCR, đối soát, và việc người dùng nói đã trả.

**Ánh xạ đường cũ, PROPOSED:** `/dashboard` tới Hôm nay; `/bills` tới Hồ sơ.
`/readings`, `/meters`, `/statistics` còn deep link dưới Mức sử dụng; không xóa bookmark.
`/household`, `/household/members`, `/settings` còn trong Thêm; account nằm trong chi tiết hộ.
`/assistant` còn hội thoại đầy đủ; upload ở đây mở cùng pipeline chứng từ, không tạo kho riêng.
`/admin/*` giữ ranh giới quản trị và không kéo dữ liệu hộ vào dashboard hệ thống.
URL cuối cùng cần chốt khi làm contract routing; đây chưa là lệnh đổi route.

## 4. Ngôn ngữ và nguồn sự thật

- “Chứng từ nhà cung cấp — bạn đã kiểm tra” thay cho “đã xác minh bởi nhà cung cấp”.
- “Ước tính từ chỉ số” luôn kèm biểu giá/thuế/phí đã biết và giới hạn.
- “Khoản điện/nước đã ghi nhận” là ExpenseRecord: basis DOCUMENT_CONFIRMED khi có chứng từ đã người dùng review, hoặc USER_ENTERED khi ghi nhanh không cloud; source document là reference riêng, không bắt buộc.
- Account, report_period, khoảng tiêu thụ và hạn có thể chưa biết/null khi capture, có flag để bổ sung; không tạo meter/account/ngày giả. Confirm tối thiểu cần household, utility, amount, currency, basis (Backlog C02).
- “Bạn đã ghi nhận đã trả” không phải “Ngân hàng xác nhận thành công”.
- Hạn từ chứng từ, hạn tự đặt và chưa biết hạn là ba trạng thái phân biệt.
- Không ghi 0 ₫ khi thiếu số; hiển thị “Chưa có số tiền”; 0 hợp lệ vẫn là 0 ₫.
- Kỳ báo cáo tháng khác khoảng tiêu thụ; điện/nước có thể có ngày chốt khác nhau.
- Cùng account/kỳ: official record và estimate liên kết, không cộng hai lần vào tổng khoản phải trả.
- Đối soát chỉ số, lượng dùng, số tiền là các kết quả riêng; không dùng một MATCH bao trùm.
- Chứng từ không đọc được số công tơ vẫn có thể đủ để ghi khoản chi đã kiểm tra.
- Thiếu lịch sử đo trả “Chưa đủ dữ liệu đối chiếu”, không buộc tạo chỉ số giả.
- **DECISION REQUIRED:** bản đầu cho ghi nhận đã trả dựa estimate hay chỉ khoản thực tế; không tự kế thừa D01 cũ.

## 5. Quy ước đếm bước và state dùng chung

Một bước = một màn/miền quyết định cần người dùng xác nhận để đổi trạng thái nghiệp vụ.
Không đếm từng field, click chọn tệp của OS, request nền, màn thành công hay tự động trích xuất.
BEFORE chỉ là số màn/submit quan sát từ source, không gọi đó là số click/thời gian đo thực nghiệm.
Luồng mới không có tương đương end-to-end ghi “BEFORE: chưa đo/không có luồng tương đương”.
AFTER là số mục tiêu theo quy ước này, chưa chứng minh nhanh hơn; nhánh lỗi được mô tả riêng.

**State chung PROPOSED áp dụng mọi luồng dưới đây:**
- Loading: giữ tiêu đề/hộ, skeleton đúng vùng; không render empty trước khi tải xong.
- Empty: phân biệt chưa có dữ liệu, lọc không khớp và chưa đủ quyền; CTA đúng nguyên nhân.
- Error: giữ input, lỗi field + tóm tắt có focus; request_id kín đáo cho hỗ trợ; retry không ghi trùng.
- Offline: banner có thời điểm dữ liệu đã tải; chỉ đọc cache đúng hộ; chặn ghi và nói rõ chưa lưu.
- Permission: capability từ server; không chỉ ẩn nút; 403 giữa thao tác giữ bản nháp riêng an toàn.
- Conflict: hiển thị bản vừa đổi, người đổi/thời điểm nếu được phép; yêu cầu kiểm tra lại trước confirm.
- Busy: chặn double-submit, cho rời màn nếu tác vụ đã lưu bền; không suy đoán tiến độ phần trăm.
- Success: hiển thị record id, nguồn, việc tiếp theo; toast không là bằng chứng lưu duy nhất.
- Session hết hạn: đăng nhập lại rồi kiểm tra scope/revision; không tự phát lại ghi tài chính.

## 6. Thiết kế từng luồng

### UX01 — Truy cập, đăng ký và onboarding

**CURRENT VERIFIED:** AuthForm submit rồi chuyển onboarding/dashboard (`A:525–535`).
Bốn stage onboarding và default lịch/initial reading ở `A:623–624`.
`cleanAccounts` không chuyển `tariff_category`/`province` dù form thu hai trường (`A:623–624`).
Giả thuyết: thiết lập kỹ thuật trước khi dùng làm tăng bỏ cuộc, đặc biệt hộ chỉ có nước.
**Target PROPOSED:** tạo không gian tối thiểu rồi chọn mục tiêu; chỉ hỏi thiết lập cần cho mục tiêu đó.
1. Đăng ký/đăng nhập bằng form; nhãn demo riêng nếu có môi trường demo.
2. Nhập tên hộ, chọn dùng điện/nước/cả hai, có thể để account chưa hoàn chỉnh.
3. Chọn “Theo dõi chỉ số/ước tính”, “Lưu hóa đơn”, “Ghi khoản thực tế” hoặc “Để sau”; cùng cấp, đổi được trên dashboard. Nhánh đo mới hỏi meter/chỉ số đầu/ngày/đơn vị; tariff là bổ sung khi cần tính tiền. Account suy ra từ tệp luôn cần kiểm tra.
BEFORE: 4 stage onboarding sau auth; AFTER: 2 stage sau auth, upload tính ở UX04 riêng.
State riêng: loading submit; empty “Bạn muốn bắt đầu việc gì?”; lỗi không mất hộ/account; offline không báo tạo thành công; quyền tạo hộ kiểm tra server.
AI: chỉ gợi ý trường từ tài liệu, không tự tạo tariff hoặc mã khách hàng.
AC: nước-only hoàn tất; không cần initial reading; reload tiếp tục draft nếu chính sách cho phép; không gán EVN/Demo âm thầm.
**DECISION REQUIRED:** dữ liệu tối thiểu tạo hộ và người nào được tạo nhiều hộ; retention draft onboarding.

### UX02 — Hộ gia đình, đổi hộ và thành viên

**CURRENT VERIFIED:** sửa hộ, danh sách hộ, chuyển hộ, link thành viên cùng trang (`A:1104`).
Thêm thành viên bằng email đã đăng ký; quyền read/write/pay, xóa trực tiếp (`A:1105`).
Giả thuyết: hộ là trang cấu hình hơn là scope thường trực; đổi hộ ở sâu dễ bỏ sót.
**Target PROPOSED:** scope luôn hiện, quản lý thành viên diễn đạt bằng việc được phép.
1. Mở bộ đổi hộ ở header, chọn hộ; pending request cũ bị bỏ.
2. Xác nhận tên hộ trong header và dữ liệu mới trước khi thao tác; chỉ hỏi lại nếu đang có draft.
BEFORE: chưa đo end-to-end; AFTER: 1 quyết định đổi hộ, 2 nếu cần xử lý draft đang mở.
Quản lý thành viên: 1. Mở danh sách; 2. Chọn email/quyền; 3. Kiểm tra và thêm hoặc xác nhận xóa.
BEFORE: một form submit thêm trực tiếp; AFTER: 2 miền thao tác thêm kể từ danh sách (nhập + review).
State riêng: loading khóa thao tác chéo scope; empty “Chỉ có bạn”; lỗi thêm trùng có giải thích; offline không chuyển scope server; permission owner/members theo policy.
AI: không suy quyền từ lời chat; không mang hội thoại hộ A sang B.
AC: response đến muộn không hiển thị hộ cũ; quyền mới có hiệu lực lúc confirm; mô tả rõ direct-add chưa là lời mời email.
**DECISION REQUIRED:** quyền mới upload/xác nhận tài chính; không tự map `write` thành mọi quyền.

### UX03 — Tài khoản tiện ích và công tơ

**CURRENT VERIFIED:** account form nằm ở hộ (`A:1104`); công tơ ở trang riêng (`A:1106`).
Form công tơ cho thêm/sửa/trạng thái, nêu một công tơ hoạt động mỗi account V1.
Giả thuyết: tách account và meter làm người mới nhầm hợp đồng với thiết bị đo.
**Target PROPOSED:** chi tiết account có hồ sơ, lịch hạn, và tab Thiết bị đo tùy chọn.
1. Tạo/chọn account bằng loại dịch vụ, nhãn, provider/mã KH nếu biết.
2. Kiểm tra thông tin và lưu; cấu hình lịch/biểu giá là phần nâng cao khi cần.
3. Nếu bật tự theo dõi, thêm công tơ với chỉ số đầu + ngày + đơn vị, kiểm tra rồi lưu.
BEFORE: chưa đo chuỗi account→meter; AFTER: 2 stage account, thêm 2 stage meter khi tự nguyện.
State riêng: loading danh mục; empty account cho nhập tay; provider không có vẫn lưu thông tin; offline draft chưa lưu; permission quản lý account khác xem hồ sơ.
AI: gợi ý account từ mã trên ảnh, hỏi chọn khi nhiều ứng viên; không tự ghép chỉ theo utility.
AC: có hồ sơ không meter; hai account điện phân biệt bằng nhãn/mã che; thiếu tariff không chặn chứng từ.
**DEFERRED:** thay công tơ giữa kỳ tự động; nút Ngừng phải nói tác động tới nhập đo, không xóa lịch sử.

### UX04 — Upload/import, trích xuất và ghi khoản thực tế

**CURRENT VERIFIED:** ảnh JPEG/PNG/WebP, max 10 MB phía client, đọc Base64 và gửi `/ai/chat` (`A:1143–1210`).
Không thấy luồng document draft→review→confirm tài chính riêng tại frontend đã đọc.
Giả thuyết: phân tích xong trong chat chưa trả lời “đã vào sổ chưa”; không có nơi sửa từng trường.
**Target PROPOSED:** một trong ba hành trình giá trị, độc lập lịch sử đọc công tơ; upload M3 sau seam record M1, không làm gate M2 đo/ước tính.
1. Chọn định dạng được R06 cho phép tại M3 (JPEG/PNG là candidate baseline, PDF text là candidate sớm); xem tên, preview và thông báo dữ liệu gửi AI; hoặc chọn ghi nhanh USER_ENTERED không tệp, không cloud, không cần key.
2. Kiểm tra utility, số tiền/currency/basis; account, kỳ/khoảng dùng, hạn có thể null có cờ. Khi có ảnh, field và nguồn cạnh chứng từ; sửa phần chưa chắc.
3. Xác nhận “Ghi khoản điện/nước”; server lưu record có nguồn và hiện liên kết chi tiết.
BEFORE: chưa đo/không có luồng tương đương; AFTER: 3 stage khi đủ dữ liệu, +1 khi trùng/mơ hồ.
Loading: uploaded/processing/needs_review là trạng thái thật; rời/reload tìm lại job/draft nếu đã nhận.
Empty: vùng chọn tệp có nút camera/tệp và nhập tay; không bắt kéo thả trên mobile.
Error: ảnh mờ, không phải bill, oversized, quota, timeout khác nhau; giữ tệp theo retention, cho đổi ảnh/nhập tay.
Offline: không báo upload xong; hủy/retry giữ lựa chọn khi còn an toàn; không cache ảnh nhạy cảm ngầm.
Permission: xem ảnh, upload, confirm và xóa kiểm tra riêng theo quyết định quyền; mất quyền dừng confirm.
AI: field có null/cảnh báo; nguyên văn tài liệu là dữ liệu, không chỉ thị; không đoán hạn hoặc amount=0.
AC: ảnh không có chỉ số vẫn ghi được khoản; sửa field truy vết được; không tạo reading/payment từ OCR.
AC: cùng file retry chỉ một draft; trùng account/kỳ được review trước record; tệp lỗi không thành “đã lưu”.
**DECISION REQUIRED R06:** dùng gate nghiên cứu mẫu ở §11; cap byte/pixel/page, parser và chi phí cần evidence trước bật từng capability. R02 quyết TTL tệp/extracted data; minimum delete/cancel và chặn job phục hồi tệp đã xóa phải có ngay khi nhận tệp thật, không chờ M6.
**DEFERRED:** email import tự động/provider API. PDF text/scan/multi-page là lựa chọn có gate, không blanket-defer; định dạng chưa bật hiện lý do và hướng ghi nhanh, không ép parse hoặc quảng cáo hỗ trợ.

### UX05 — Đối soát tùy chọn với dữ liệu đo

**CURRENT VERIFIED:** `components/bill-analysis-card.tsx` trình bày MATCH/MISMATCH/UNKNOWN.
`backend/app/ai/tools/ocr_analysis.py` là nguồn logic cần sửa matching trước dùng làm bằng chứng.
Kế hoạch cũ F02 nhận diện so lịch sử mới nhất thiếu account/kỳ (`…phan-tich…:68–72`).
Giả thuyết: badge trùng chỉ số dễ bị hiểu là toàn hóa đơn hợp lệ.
**Target PROPOSED:** so đúng cặp, giải thích phạm vi, không cản ghi khoản chi.
1. Từ hồ sơ chọn “Đối chiếu dữ liệu đo”; chọn account/khoảng phù hợp nếu mơ hồ.
2. Xem bảng chỉ số/lượng dùng/tiền/thuế và nguồn; lưu kết quả đối chiếu hoặc để chưa đủ dữ liệu.
BEFORE: chưa đo; AFTER: 2 stage; 1 stage nếu cặp đã xác định và chỉ đọc kết quả.
State riêng: loading từng nguồn; empty NOT_COMPARABLE có lý do; lỗi đọc ảnh không kết luận sai; offline xem kết quả cũ có timestamp; permission theo hồ sơ/công tơ.
AI: giải thích chênh lệch như giả thuyết, không kết luận gian lận/rò rỉ hoặc sửa tiền.
AC: ảnh tháng trước không so latest tháng này; thiếu VAT không gọi tổng tiền khớp; ghi khoản vẫn hoạt động khi chưa có meter.
AC: official đến sau payment khác số tiền tạo việc cần xem lại, không đổi lịch sử thanh toán.
**DECISION REQUIRED:** tolerance từng trường, correction và xử lý chênh lệch; bản đầu không tự phân bổ.

### UX06 — Nhập chỉ số, preview và xác nhận ước tính

**CURRENT VERIFIED:** form chọn meter/kỳ/ngày/chỉ số, nút “Lưu và tạo hóa đơn” (`A:967–976`).
`previous` lấy lịch sử cùng meter hoặc initial (`A:975`); không có preview confirm riêng trong form.
Giả thuyết: người dùng khó kiểm tra số tiền trước một thao tác ghi không dễ sửa.
**Target PROPOSED:** nhánh chính ngang upload/quick-entry, triển khai sớm M2 độc lập OCR (có thể song song M1 sau shared gates), cho hiểu lượng dùng và khả năng tính giá trước confirm.
1. Chọn meter, nhập số/ngày; đọc previous và khoảng thời gian. Initial cũ không có ngày không bị gán ngày giả: cho lưu phép đo mới có ngày làm baseline; đến khi có hai observation có ngày hợp lệ mới có interval/lượng dùng/estimate.
2. Xem preview consumption khi đủ hai observation có ngày, hoặc “Mốc đo đầu — sau xác nhận sẽ cần lần đo tiếp”; phiên bản giá/thuế/phí/giới hạn chỉ khi đủ điều kiện; sửa khi cần.
3. Ngay trong màn preview ở bước 2, xác nhận lưu phép đo và estimate đủ điều kiện hoặc pending có nhãn; đây là action cuối cùng của cùng stage, không một màn thứ ba.
BEFORE: 1 form submit từ trang reading; AFTER: 2 stage nhập + preview/confirm, không tính kết quả.
State riêng: loading previous; empty mời thêm meter tùy chọn; lỗi lùi số/trùng kỳ tại field; offline chưa lưu; permission nhập đo kiểm tra lại confirm.
AI: đọc ảnh mặt công tơ thành draft tùy phạm vi; không dùng ảnh hóa đơn để giả phép đo độc lập.
AC: preview cũ bị 409 khi nguồn đổi; double-submit một record; thiếu tariff không biến 0 thành estimate; usage chỉ có khi có hai compatible dated observations, một baseline không có usage.
AC: “Bỏ qua đo” quay về hồ sơ, không làm mất dữ liệu chứng từ hoặc chặn khoản chi.
**PROPOSED:** reading hợp lệ vẫn lưu khi không có tariff; hiển thị lượng dùng và trạng thái estimate_pending/not_computable kèm nguyên nhân, không yêu cầu hóa đơn hoặc cloud. **DECISION REQUIRED D02–D04:** interval, giá đổi giữa kỳ và nguồn giá; chưa chốt policy tính tiền không được làm mất/khóa nhánh đo hợp lệ.
**PROPOSED minimum M2:** invalidate observation nhập nhầm có reason/version/history, preview interval kề bị ảnh hưởng và đánh dấu estimate/insight stale. Không xóa lịch sử. **DEFERRED:** correction lịch sử tổng quát/thay công tơ tự phục vụ tới khi R07 đủ policy.

### UX07 — Hồ sơ, khoản chi và ghi nhận đã trả thủ công

**CURRENT VERIFIED:** filter bill kỳ/status/utility (`A:978–1009`), detail snapshot (`A:1010–1048`).
Nút ghi nhận thủ công gọi `/payments` chỉ bill_id ngay (`A:1042`); có in browser (`A:1044–1046`).
Giả thuyết: “Tổng cộng” bên cạnh official chưa có khiến estimate dễ bị hiểu thành khoản nợ provider.
**Target PROPOSED:** detail tách amount_basis, chứng từ, estimate và record đã trả rõ ràng.
1. Từ hồ sơ mở khoản; xem số tiền/cơ sở/hạn và lịch sử.
2. Chọn “Ghi nhận đã trả”, nhập ngày/reference/phương thức theo phạm vi, kiểm tra số tiền đã pin.
3. Confirm; nhận trạng thái “Bạn đã ghi nhận đã trả” cùng thời điểm/tác nhân.
BEFORE: 2 miền kể từ danh sách (mở detail, nút ghi trực tiếp); AFTER: 3 miền (detail, form, confirm).
Nhập khoản không tệp: 1. Nhập utility/tiền, account/kỳ/hạn tùy chọn; 2. Review + xác nhận đây là khoản thực tế đã biết, không chỉ số tiền mô phỏng; basis USER_ENTERED, source “Bạn nhập”. Không convert estimate thành actual chỉ vì người dùng bấm quick-entry; legacy payment dựa estimate giữ nguồn/ý nghĩa riêng để review D01. Không cloud/model bắt buộc; cùng ExpenseRecord contract với nhánh chứng từ.
BEFORE nhập khoản độc lập: chưa có tương đương trong frontend; AFTER: 2 stage.
State riêng: loading detail; empty không lọc nhầm chưa có bill; lỗi amount/revision giữ form; offline chặn ghi; permission pay kiểm tra lại.
AI: mở form điền sẵn từ record, không nói đã trả trước response; không đề xuất QR như kết nối ngân hàng.
AC: paid một lần idempotent; print không menu và ghi nguồn; record thực tế/estimate không cộng trùng.
AC: thiếu due date vẫn ghi được khoản khi policy cho phép; nhắc hạn không tự chọn ngày 28 như nguồn chính thức.
**DECISION REQUIRED:** amount_basis, ngày trả, reference bắt buộc/tùy chọn, correction sau đã trả.
**DEFERRED:** partial/refund/gateway; không hiển thị số dư giả khi chưa có ledger hỗ trợ.

### UX08 — Hôm nay, phân tích và dự báo

**CURRENT VERIFIED:** dashboard tải statistics/bills/house/readings (`A:725`).
Budget fallback 2 triệu và forecast=currentTotalCost×1.1 (`A:748–752`); card gắn “AI dự đoán” (`A:919`).
Statistics có range, average và bảng kỳ (`A:1052–1101`); backend forecast là nhánh riêng.
CURRENT VERIFIED bổ sung: frontend/components/dashboard/AIInsightPanel.tsx:7–31 hardcode +8,2%, tiết kiệm 80–120 nghìn và thấp hơn nhóm hộ 12%.
frontend/components/statistics/AISavingTips.tsx:20–23 hardcode 180 nghìn/12% và tuyên bố dựa 6 kỳ; được source `StatisticsPage.tsx:111` render và `A:957` chọn StatisticsPage; đây là trace render tĩnh, chưa phải browser verification.
PROPOSED: bỏ các insight cá nhân giả khỏi mọi surface đang dùng; chỉ hiện claim có dữ liệu/phương pháp, hoặc kiến thức chung có nhãn.
Giả thuyết: nhiều KPI trước công việc có thể làm tăng độ tin giả, nhất là hộ thiếu tháng đo.
**Target PROPOSED:** Hôm nay ưu tiên việc; phân tích phân biệt chi thực tế và lượng sử dụng.
1. Chọn hộ/khoảng; xem việc cần xử lý, tổng actual theo basis và lượng dùng điện/nước riêng, mỗi vùng có kỳ/coverage/nguồn.
2. Mở phân tích khi cần; chọn Chi phí hoặc Lượng dùng, xem bảng nguồn và phương pháp.
3. Bật dự báo tùy chọn khi có dữ liệu đủ điều kiện; xem kỳ đầu vào và giới hạn.
BEFORE: chưa đo; AFTER: 1 stage xem việc, 2 stage tới phân tích, thêm 1 khi xem dự báo.
State riêng: loading từng vùng; empty không có việc khác chưa có dữ liệu; lỗi chart giữ bảng; offline ghi thời điểm; permission chỉ dữ liệu đúng scope.
AI: giải thích từ series/service, không nhân 1.1 rồi gán AI; không chẩn đoán thiết bị hỏng từ một tháng tăng.
AC: chưa đặt budget hiện CTA; missing không là zero; điện/nước khác interval không giả so cùng khoảng.
AC: record-only vẫn thấy chi phí nhưng không claim nguyên nhân mức dùng; reading-only vẫn thấy lượng dùng và estimate đủ điều kiện dù không invoice; hybrid không cộng actual+estimate. Dự báo thiếu dữ liệu nói rõ, không cản workspace.
**DECISION REQUIRED:** budget có thuộc bản đầu; nguồn nào quyết định tổng và cách xử lý official mới đến.

### UX09 — Cảnh báo và nhắc hạn

**CURRENT VERIFIED:** notifications hiển thị list và PATCH đã đọc (`A:953`); unread count từ is_read (`A:139`).
Account có lịch do người dùng cấu hình (`A:624`, `A:1104`); chưa là lịch provider đã xác minh.
Giả thuyết: đọc thông báo dễ bị hiểu là đã xử lý khoản cần trả.
**Target PROPOSED:** notification là tín hiệu; task có trạng thái nghiệp vụ riêng.
1. Mở việc từ Hôm nay/chuông; xem deadline, nguồn hạn, account và amount_basis.
2. Đi tới đúng hồ sơ và xử lý/để sau; “Đã đọc” chỉ tắt unread, không trả tiền.
BEFORE: chưa đo; AFTER: 2 stage tới hồ sơ xử lý, thao tác payment tính UX07.
State riêng: loading giữ count trước có nhãn; empty “Không có việc”; lỗi retry; offline không đánh dấu server; quyền chỉ mở hồ sơ còn được xem.
AI: diễn giải lý do cảnh báo có baseline; gợi ý kiểm tra không kết luận nguyên nhân.
AC: bill đã ghi trả không nhắc tiếp; đọc không set PAID; hạn không biết không báo quá hạn.
**DECISION REQUIRED:** preference, kênh in-app và cadence; email/push chỉ bật sau chứng minh delivery.

### UX10 — Trợ lý trong ngữ cảnh và hội thoại đầy đủ

**CURRENT VERIFIED:** messages ở component state (`A:1109`); request không gửi conversation_id (`A:1202–1208`).
Timer mô phỏng thinking (`A:1121–1134`), smooth scroll tự động (`A:1137–1139`).
Giả thuyết: rời trang mất mạch; thông báo “đang làm” có thể không phản ánh tool thật.
**Target PROPOSED:** hỏi từ hồ sơ/chart với scope nhìn thấy, câu trả lời link về dữ liệu.
1. Chọn “Giải thích khoản này” hoặc mở hội thoại; scope hộ/account/kỳ hiển thị.
2. Đọc answer card có nguồn, phương pháp, giới hạn; bổ sung slot nếu mơ hồ.
3. Chọn hành động mở form review; mọi ghi nhận theo luồng chính, không ghi trong prose.
BEFORE: chưa đo; AFTER: 1–2 stage hỏi/resolve slot, thêm form riêng khi tạo draft.
State riêng: loading theo tool event thật; empty câu hỏi gắn việc; timeout retry/cancel không mất câu; offline giữ draft; permission kiểm tra từng tool và source link.
AI: answered/needs_input/unavailable; không nêu số khác service; web nguồn công khai tách nguồn hộ.
AC: follow-up giữ đúng kỳ; đổi hộ không kế thừa dữ liệu riêng; quota vẫn xem bill; không giả progress bằng timer.
**DECISION REQUIRED:** retention/xóa conversation, dữ liệu gửi model, default external AI; có đường nhập thủ công khi từ chối OCR.

### UX11 — Cài đặt và tài khoản cá nhân

**CURRENT VERIFIED:** tên và đổi mật khẩu; đổi xong logout (`A:1107`).
Giả thuyết: privacy/reminder lẫn với cấu hình hộ sẽ khó biết tác động cá nhân hay cả gia đình.
**Target PROPOSED:** nhóm Cá nhân / Nhắc việc / AI và tài liệu; scope của mỗi setting có nhãn.
1. Mở nhóm và sửa; trước tác động rộng thấy “Chỉ bạn” hoặc “Cả hộ”.
2. Review khi đổi mật khẩu/quyền/retention; xác nhận, hiện kết quả và phiên còn hoạt động.
BEFORE: 1 submit đổi mật khẩu; AFTER: 2 stage với thông báo logout trước confirm.
State riêng: loading setting; empty chưa có preference dùng default có nhãn; lỗi giữ field an toàn; offline chặn; permission owner cho cài hộ.
AI: giải thích privacy bằng nội dung policy, không hứa “mọi dữ liệu ở local”.
AC: không lưu mật khẩu draft; thay retention nói rõ ảnh/field/chat chịu ảnh hưởng; thao tác xóa có scope/version.
**DEFERRED:** MFA/recovery email khi hạ tầng chưa xác nhận; không nút gửi email giả.

### UX12 — Quản trị hệ thống

**CURRENT VERIFIED:** admin overview/users/tariffs/audit (`A:1524–1535`), tariff create (`A:1537–1576`).
403 phía UI ở `A:962`; server là ranh giới bắt buộc, không coi client check là bảo vệ đủ.
Giả thuyết: tạo tariff trực tiếp thiếu preview phạm vi/ảnh hưởng trước publish.
**Target PROPOSED:** workspace riêng, thao tác nhạy cảm qua draft→validate→publish có audit.
1. Tạo tariff draft với nguồn/phạm vi/hiệu lực và các bậc.
2. Validate overlap/gap và xem ví dụ tính tiền; nêu bản nào có thể dùng cho estimate mới.
3. Review + publish; lịch sử snapshot không đổi.
BEFORE: 1 form submit tạo tariff; AFTER: 3 stage tariff, nhiều hơn để kiểm soát tác động.
User: 1. Chọn user; 2. Kiểm tra tác động và confirm khóa/mở; audit có filter/deep link.
State riêng: loading query; empty audit filter; lỗi validate tại scope; offline chặn publish; permission admin tái kiểm tra không bao hàm membership hộ.
AI: hỗ trợ tìm nguồn và giải thích validate, không tự publish hoặc thấy toàn bộ chứng từ hộ.
AC: cấm self-disable theo service; không log prompt/ảnh thô; published tariff có nguồn/người/thời điểm.
**DECISION REQUIRED:** người duyệt dữ liệu giá pilot; không mặc định developer là người xác nhận nghiệp vụ.

## 7. Hướng thị giác đề xuất — Sổ nhà sáng rõ

**PROPOSED, mode Operate:** một bàn làm việc gia đình bình tĩnh, giống hồ sơ đã sắp gọn hơn là bảng trình diễn AI.
Đây là một phương án cụ thể để review, không là hướng người dùng đã chọn hoặc kết quả browser audit.
Incumbent code dùng sidebar/card trắng trong, blur, nhiều gradient (`AppLayout.tsx:123–145`; `A:757–786`).
Đề xuất thay thế bằng bề mặt đặc, ranh giới tinh tế và thứ tự chữ rõ; cần prototype trước áp dụng diện rộng.

Palette đề xuất: nền #F5F3EE, surface #FFFFFF, text #18231F, secondary #526159, border #D8DFD9.
Primary #176449 trên trắng; hover #104E38; focus ring #245CC5 có khoảng tách.
Điện dùng ochre #8A5812 + nền #FBF1DC; nước dùng blue #205B85 + nền #EAF3F8.
Cảnh báo #8A4B08, lỗi #B42318, success #176449; luôn thêm icon/nhãn, không dùng màu làm tín hiệu duy nhất.
Đây là token đề xuất; contrast từng cặp/text size phải đo trước nghiệm thu, không tự gọi AA chỉ từ mã hex.

Chữ: Be Vietnam Pro nếu được duyệt/font sẵn có, system sans fallback; test dấu tiếng Việt và tải font.
Body 16/24; label 14/20; supporting 14/20; H1 28/36 desktop, 24/32 mobile; số tiền 32/40 tabular numerals.
Dùng tối đa 400/500/600; không chữ 9–11px cho hạn, đơn vị, nguồn hoặc việc tài chính.
Tên account dài xuống dòng; mã KH che ở default, người có quyền có thể xem khi cần.

Topology desktop: sidebar đặc 224px, main max 1200px; header hộ + CTA, không search giả.
Hôm nay: cột chính danh sách việc 2/3, cột phụ hạn/tóm tắt 1/3; summary không lấn việc.
Hồ sơ: danh sách có hàng rõ (dịch vụ/kỳ/nguồn/tiền/hạn/trạng thái), detail mở trang có URL.
Review chứng từ: ảnh 45% + field 55%, sticky vùng action dưới field; không modal chồng modal.
Mobile: một cột, field trước, ảnh mở/đóng bằng nút rõ; sticky action không che lỗi/bàn phím.
Bán kính 8–12px, grid 4/8px, đường chia 1px; shadow chỉ cho popover/dialog.
Không decor nền chuyển động trong app; motion 120–180ms phản hồi thao tác, reduced-motion tắt chuyển cảnh.
AI có cùng hệ component; không panel tím riêng để gây cảm giác đáp án có thẩm quyền hơn bằng chứng.
Landing có thể kể chuyện bằng ví dụ hồ sơ ẩn danh; không số tiết kiệm/testimonial chưa có nguồn.

## 8. Mobile, bàn phím và khả năng tiếp cận

**PROPOSED mục tiêu:** WCAG 2.2 AA cho màn trong scope, cần kiểm chứng thật.
320/360px không cuộn ngang trang; 768/1440px kiểm tra topology; bảng có vùng cuộn riêng và summary.
Bottom nav mobile Hôm nay / Hồ sơ / Mức dùng / Thêm; nút “Thêm dữ liệu” mở ba cửa ngang cấp, dễ chạm và không che nội dung.
Mục tiêu vùng chạm 44×44 CSS px; tiêu chuẩn tối thiểu và ngoại lệ đo theo thiết kế triển khai.
Heading/landmark đúng, skip link, aria-current, focus visible không bị sticky header che.
Drawer/dialog khóa focus, Escape, trả focus về trigger; đóng drawer không làm mất vị trí.
Mọi field có label, required bằng chữ, đơn vị, format và lỗi liên kết; không chỉ placeholder.
Số thập phân nhận locale theo parser được test; date hiển thị tiếng Việt, contract không phụ thuộc chuỗi locale.
Screen reader nghe tiền/đơn vị/kỳ/nguồn và trạng thái lưu; live region không spam từng token AI.
Upload bằng bàn phím, nút chọn tệp thay kéo thả; tên tệp/loại/lỗi đọc được bằng SR.
Chart có bảng tương đương, missing gap có chú thích; không chỉ tooltip hover.
Zoom 200%, text reflow, chế độ high contrast và reduced motion thuộc checklist browser, chưa đạt từ static review.
Không auto-scroll chat khi người dùng đang đọc trên; có “Tin mới” và tùy chọn tới cuối.

## 9. Đo kiểm và thứ tự xác thực đề xuất

Prototype trước ba trường hợp: hộ mới chỉ có hóa đơn; hộ đã tự đo; thành viên chỉ được xem.
Bài 1: từ ảnh được cung cấp tìm số tiền/hạn, sửa một field OCR sai và ghi khoản.
Bài 2: giải thích khác nhau giữa estimate, khoản thực tế và ghi nhận đã trả.
Bài 3: mở ảnh cũ/account khác, tránh đối soát nhầm và tránh tạo trùng.
Bài 4: không dùng AI hoặc provider timeout vẫn ghi khoản bằng tay.
Bài 5: đổi hộ khi đang review, xác định draft đang thuộc hộ nào.
Đo task completion, sai account/kỳ/tiền, trợ giúp cần dùng, thời gian tới record đầu; không suy giảm số click = UX tốt.
Mục tiêu pilot PROPOSED: tất cả ca tài chính fixture đúng nguồn; không người nào hiểu ghi nhận tay là giao dịch bank.
Ngưỡng tỷ lệ/thời gian cần baseline và cỡ mẫu trước cam kết; không bịa 90% hoặc tiết kiệm phút.

Thứ tự PROPOSED thống nhất Master/Backlog: M0 shared gates và legacy safeties; M1 quick-entry/records/explanation/payment assertion; M2 measurement/estimate sớm độc lập OCR, có thể song song M1 sau shared gates; M3 upload/review theo format evidence sau record seam; M4 reconciliation; M5 dialogue/event insight/search/handoff mở rộng; M6 correction/privacy/admin/pilot rộng hơn. Security, job bền khi nhận tệp, delete tối thiểu và assertion reversal không đợi M6. ID UX01–12 và task backlog cũ giữ nguyên; M là wave, không đổi tên ID.
Mỗi flow chỉ Done khi states/permission/keyboard/mobile và fixture đúng; typecheck không thay usability verification.

## 10. Review độc lập Product + UX và xung đột phải giải quyết

**Product:** kế hoạch cũ sửa cơ chế đáng tin khá kỹ nhưng để hành vi thu thập thủ công là đường găng chưa có bằng chứng.
Đẩy OCR tới G4 khiến bản đầu vẫn không kiểm tra giả thuyết “hộ muốn sổ chứng từ hơn công cụ tính giá”.
V2.2 sửa thiên lệch chứng từ-first: hybrid task-first là khuyến nghị cần kiểm chứng với cả ba nhóm, không coi đã được người dùng chọn.
Hộ có hóa đơn điện tử nhưng không được API/email access vẫn có thể cung cấp tệp; đừng hứa tự động thu thập.
Đối soát là giá trị bổ sung; không phải mọi khoản chi đều cần chứng minh bằng phép đo riêng.

**UX:** giảm cấu hình ban đầu hữu ích hơn chỉ giảm padding/gradient; nav phải theo tác vụ và tần suất.
Có trường hợp nên tăng bước (payment/tariff) để kiểm tra căn cứ, thay vì tối ưu mọi thao tác một click.
Không biến workspace thành chatbot bắt buộc; hồ sơ và trạng thái phải truy cập trực tiếp bằng URL và keyboard.
Màu sắc/font ở trên là proposal để review; chưa có screenshot kiểm chứng và chưa thay DESIGN.md.

**DECISION REQUIRED trước implementation:**
1. R01: đề xuất hybrid task-first với ba cửa ngang cấp, giữ đo/ước tính là giá trị chính và research trước mở rộng.
2. Phân quyền tạo draft/xác nhận khoản/xem-xóa tệp/ghi nhận trả; mapping quyền legacy.
3. Amount_basis và tổng hợp official/estimate/payment, nhất là official đến sau đã trả.
4. R06 duyệt format sau sample gate: JPEG/PNG baseline candidate, PDF text early candidate, scan/multi-page theo evidence; cap/storage/retention/consent, draft khi offline/session hết hạn.
5. Kỳ account, pending estimate, correction và đổi giá giữa kỳ; không để người dựng UI tự quyết.
6. Review prototype hướng thị giác, tên mục Hồ sơ/Hôm nay và ngôn ngữ tài chính bằng người dùng thật.

**DEFERRED có chủ đích:** đồng bộ provider/email, thanh toán tự động, IoT, partial/refund, meter replacement nâng cao.
Tài liệu này không phê duyệt triển khai, không chứng nhận tính đúng thực tế, không thay dữ liệu hoặc bỏ luồng hiện có.




## 11. V2.2 — Structural wireframes và lựa chọn tương tác

Các bản dưới là wireframe cấu trúc **PROPOSED**, không screenshot, không chứng nhận visual đúng checkout. Giữ token §7; bước implementation phải kiểm rendered đúng process/root trước phán xét. Không tạo thêm artifact/file ở lượt planning này.

### 11.1 Dashboard thống nhất, desktop

```text
+----------------+---------------------------------------------------------+
| Nhà Mình       | Hộ [chọn]                 Kỳ [chọn]     Thông báo       |
| Hôm nay        | Hôm nay / khoảng dữ liệu đang xem                        |
| Hồ sơ          | [Hóa đơn/tệp] [Chỉ số/ước tính] [Khoản thực tế]           |
| Mức sử dụng    +----------------------------------+----------------------+
| Thêm           | VIỆC CẦN LÀM                     | CHI PHÍ              |
|                | Kiểm draft / lịch ghi số / hạn   | Actual + basis       |
|                | Mỗi việc: nguồn, ngày, hành động | Đã ghi trả riêng     |
|                | Không việc != không dữ liệu      | Estimate riêng       |
|                +----------------------------------+----------------------+
|                | MỨC DÙNG: Điện [kWh] / Nước [m3], không cộng khác đơn vị |
|                | Khoảng đo | coverage | bảng/biểu đồ | nguồn/method       |
|                | [Ghi chỉ số] [Xem cách tính] [Giải thích thay đổi]        |
|                +---------------------------------------------------------+
|                | Hồ sơ/gần đây và liên kết nguồn; thiếu dữ liệu có CTA   |
+----------------+---------------------------------------------------------+
```

Thứ tự đọc: scope → ba tác vụ → việc cần làm → actual/assertion/estimate có nhãn riêng → lượng dùng → hồ sơ gần đây. Vùng việc ngắn không để dashboard trống khi chưa có task. Cột chi phí không gọi toàn bộ tổng là “phải trả”; muốn aggregate phải nêu basis/kỳ/coverage và loại trừ estimate đã liên kết actual. Điện/nước có interval lệch hiển thị riêng; không coi report month là cửa sổ đo.

### 11.2 Dashboard mobile

```text
+----------------------------------+
| Hộ [chọn]                 Chuông  |
| Hôm nay           Kỳ [chọn]       |
| [Thêm dữ liệu]                    |
| Sheet cùng cấp khi mở:            |
|  Hóa đơn/tệp                      |
|  Chỉ số/ước tính                  |
|  Khoản thực tế                    |
+----------------------------------+
| Việc cần làm [nguồn + hành động]  |
| Chi phí actual [basis/coverage]   |
| Đã ghi trả / estimate riêng       |
| Mức dùng [Điện] [Nước]            |
| khoảng đo + bảng/biểu đồ          |
| Hồ sơ gần đây                    |
+----------------------------------+
| Hôm nay | Hồ sơ | Mức dùng | Thêm |
+----------------------------------+
```

Sheet dùng một lần mở cho cả ba entry, không carousel hoặc phải cuộn ngang để tìm đo. Empty toàn hộ giữ ba entry; empty riêng usage đưa “Ghi chỉ số” trong chính vùng đó. Khi chưa có tariff vùng usage vẫn hoạt động, estimate hiển thị lý do pending và hành động bổ sung nguồn giá. Chart lỗi vẫn có bảng, offline chỉ xem dữ liệu có timestamp và đúng hộ.

### 11.3 Entry và chi tiết: desktop

```text
+---------------------------------------------------------------------+
| Hộ / Account nếu biết / [Hóa đơn-tệp | Chỉ số-ước tính | Khoản thực tế]|
+------------------------------+--------------------------------------+
| NGUỒN / CĂN CỨ               | NHẬP / KIỂM TRA                      |
| Tệp: preview, trang/snippet  | Tệp: utility, amount, kỳ, hạn         |
| Đo: previous + ngày + meter  | Đo: meter, ngày, số mới, đơn vị       |
| Nhanh: Bạn nhập, không tệp   | Nhanh: utility, amount; optional khác |
| Không có nguồn -> nói rõ    | Field chưa biết + warning + sửa       |
+------------------------------+--------------------------------------+
| Preview: lượng dùng / estimate hoặc pending / actual riêng           |
| [Quay lại sửa]  [Lưu phép đo] hoặc [Ghi khoản thực tế]                |
+---------------------------------------------------------------------+
| CHI TIẾT CÓ URL: basis + số tiền/đơn vị + kỳ/interval + nguồn          |
| Chứng từ | Phép đo/estimate liên kết | Ghi đã trả | Lịch sử            |
| [Giải thích] [Đối chiếu nếu đủ nguồn] [Sửa/bỏ ghi nhầm theo quyền]     |
+---------------------------------------------------------------------+
```

Form theo nhánh, không hiển thị mọi trường của ba nghiệp vụ cùng lúc. Đổi nhánh khi có input hỏi giữ draft/hủy, không âm thầm convert estimate sang actual. Tệp tới review không tự tạo reading; reading preview không có nút giả ghi hóa đơn nhà cung cấp. Chi tiết actual ưu tiên amount/basis/hạn, chi tiết measurement ưu tiên lượng dùng/interval rồi estimate/cách tính; liên kết qua cùng hồ sơ account khi đã ghép đúng.

### 11.4 Entry và chi tiết: mobile

```text
+----------------------------------+
| Hộ / nhánh đang nhập [Đổi nhánh]  |
| Tiêu đề việc + trạng thái lưu     |
| [Xem nguồn/previous] mở vùng đọc  |
| Field chính + đơn vị + lỗi        |
| Field tùy chọn [Mở rộng]          |
| Preview và giới hạn/pending       |
| [Quay lại] [Xác nhận đúng nhánh]   |
+----------------------------------+
| Chi tiết: nguồn/basis/kỳ          |
| Actual hoặc lượng dùng           |
| Estimate riêng / chưa tính được  |
| Hạn + ghi đã trả nếu actual       |
| [Nguồn] [Lịch sử] [Giải thích]    |
+----------------------------------+
```

Field trước nguồn trên mobile để giảm cuộn; “Xem nguồn” giữ vị trí và focus khi đóng. Sticky confirm phải nhường bàn phím/lỗi, đủ vùng chạm §8. Không dùng modal lồng modal cho duplicate hay scope conflict; review riêng quay lại cùng draft.

**Lựa chọn và trade-off:** document-first dễ tập trung capture nhưng làm nhánh đo bị khuất; measurement-first tái dùng lõi hiện tại nhưng tăng setup cho người chỉ biết tiền. **Khuyến nghị hybrid task-first** tăng độ phức tạp tổng hợp/basis và yêu cầu empty states theo từng vùng, đổi lại ba nhóm đều có giá trị trực tiếp. Dashboard một chiều dọc tránh ba dashboard khác nhau; contextual CTA có thể nổi bật theo mục tiêu đã chọn nhưng ba entry vẫn cùng cấp. Đây là recommendation R01/R08, không lựa chọn đã approved.

### 11.5 Gate nghiên cứu hóa đơn/định dạng — R06

Trước quyết format, thu mẫu có consent và che dữ liệu: ảnh chụp giấy, screenshot hóa đơn điện tử, PDF có text, PDF scan, nhiều trang/nhiều hóa đơn, thiếu trường, mờ/nghiêng và unsupported/encrypted/corrupt. Ghi nguồn/utility/provider, tần suất trong mẫu, trang/byte/pixel, trường amount/identity/period/due có hay không, text layer có dùng được không; không tự tạo mẫu giả làm evidence người dùng.

Đo từng lớp: extraction exact-match theo field quan trọng; tỷ lệ phải sửa/không đọc được; thời gian review; false account/period match; số trang/call, latency, memory và chi phí mỗi **record xác nhận được**, không chỉ mỗi request OCR. Pilot sample không chứng minh tỷ lệ toàn thị trường. Gate an toàn phải gồm signature/MIME, size/pixel/page limits trước decode, tệp riêng có auth, parser isolation/timeouts, consent/retention/delete/job cancellation và prompt injection handling.

JPEG/PNG baseline candidate có ít nhánh parser nhưng vẫn có decode bomb/ảnh mờ và có thể buộc người vốn có PDF phải chụp lại. PDF text early candidate có thể tránh OCR ảnh và giảm nhập lại nếu text đáng tin; đổi lại cần text-order/page/embedded-content/security checks, không mặc định rẻ hoặc đúng hơn. Scan/multi-page cần render/OCR/page association/chi phí và UX chọn chứng từ riêng; chỉ thêm khi mẫu và ngân sách biện minh. Không defer tất cả PDF chỉ vì implementation tiện hơn. Quyết định ghi trong R06 theo từng lớp: bật sớm / nghiên cứu tiếp / chưa hỗ trợ kèm lý do, lợi ích/chi phí và điều kiện xét lại. Không thay nghĩa R06 bằng “JPEG/PNG đã approved”.

Happy path: supported file → durable job → field review → confirm actual. Edge: text PDF không có usable text → xin phép fallback OCR nếu capability/chi phí cho phép, hoặc hướng screenshot/ghi nhanh; không gửi external âm thầm. Blur/missing amount → giữ null và yêu cầu nhập; multi-invoice → chọn tách có review nếu enabled, nếu chưa thì không gộp tiền. Unsupported/encrypted/oversized → lý do cụ thể và quick-entry không cloud. Provider timeout/quota → draft có trạng thái thật, retry idempotent hoặc nhập tay; không ảnh hưởng reading/estimate. Không có sample evidence tại lượt planning này: tất cả format candidates còn mở.

### 11.6 Acceptance có thể kiểm chứng theo đường dùng

- **Ba cửa:** ở 360/768/1440px và keyboard, mỗi entry xuất hiện trên dashboard (mobile trong cùng sheet, một lần mở); không cần mở chat hoặc menu của upload để ghi số. Người chỉ xem thấy capability bị giới hạn rõ, server vẫn kiểm quyền.
- **Record-only fixture:** không meter, không tariff, actual có amount/basis; lưu/tìm lại/ghi đã trả theo policy được; usage ghi “Chưa có phép đo”, không suy luận tăng dùng/rò rỉ từ tiền. Thiếu interval không bị biến thành ngày đầu/cuối tháng.
- **Baseline fixture:** initial legacy thiếu ngày → lưu một observation mới có ngày, không reject chỉ vì thiếu initial_date và không tính usage/estimate từ mốc không ngày. Sau observation có ngày thứ hai mới có interval/lượng dùng; không cần document hoặc ExpenseRecord.
- **Reading-only fixture:** có hai compatible dated observations, không document/OCR key; nhập meter/date/reading → preview → lưu; thấy lượng dùng, interval và lịch sử. Có giá đủ điều kiện thì estimate có snapshot; thiếu giá thì pending có lý do và lượng dùng vẫn còn sau reload. Không sinh actual/payment assertion.
- **Hybrid fixture:** estimate 500.000, actual 530.000 và assertion 500.000 hiển thị ba nguồn, một việc cần review; tổng actual là 530.000, không thành 1.030.000; assertion không bị đổi âm thầm. Ghép sai account/kỳ trả NOT_COMPARABLE hoặc yêu cầu chọn.
- **Fallback fixture:** external AI unavailable/declined không chặn quick-entry hoặc measurement; failed upload không báo record saved; retry/reload không tạo draft/record trùng. Source/revision đổi thì preview cũ bị chặn, không tự replay confirm sau login.
- **Lifecycle fixture:** record cancel/supersede tối thiểu M1 và observation invalidation tối thiểu M2 có reason/version/history, preview ảnh hưởng và derived stale; minimal assertion reversal giữ actor/reason/original; delete khi job processing không làm file sống lại; revoke/đổi hộ giữa thao tác không hiển thị hoặc ghi sang hộ khác. Đây là gate sớm M0/M1/M3 theo capability, không dồn M6.
- **Pilot quan sát:** đo completion/error/help/time-to-first-value riêng ba nhánh và khả năng phân biệt actual/estimate/assertion; báo numerator/denominator, không gộp điểm cao để che sai hộ/tiền. Ngưỡng tốc độ/tỷ lệ chốt sau baseline; mọi critical financial/scope fixture phải đúng trước enabled release.

## 12. Changelog V2.2

- Chuyển recommendation document-first thành **HYBRID TASK-FIRST**, giữ measurement/estimate sớm và ba entry cùng cấp; chưa coi R01 được duyệt.
- Thêm dashboard và entry/detail desktop/mobile dạng ASCII, thứ tự thông tin, trade-off, progressive onboarding và ba nhóm fixture.
- Thay blanket-defer PDF bằng sample/economics/security gate R06; JPEG/PNG và text PDF chỉ là candidates.
- Giữ UX01–12, source evidence, shared states, visual tokens và decision meanings D01–D04/R01–R09; đồng bộ M0–M6, không sửa code/database/dependencies hoặc original V2.


