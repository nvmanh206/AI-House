# V2.2 — Critical Review, Change Impact Matrix và quyết định

Ngày 27/10/2026 · Planning V2.2 refinement của V2.1 · Không ghi đè hai V2 gốc, không sửa source/database.
Đối chiếu [Master](V2-MASTER-PLAN-IMPROVED.md), [UX](V2-UX-REDESIGN.md), [AI](V2-AI-ARCHITECTURE.md), [Backlog](V2-IMPROVED-BACKLOG.md).

## 1. Quy ước bằng chứng

CURRENT: có source; VERIFIED: kiểm tra nêu rõ phương pháp; PROPOSED: chưa duyệt; DECISION REQUIRED: chủ dự án cần chọn; DEFERRED: ngoài scope. Mọi đề xuất mới dưới đây mang trạng thái PROPOSED trừ khi ghi khác. Evidence E01–E18 và đường dẫn/dòng ở Master §2; đây là nguồn tham chiếu cho phát hiện, không thêm claim đã chạy thật.

Đã đọc đầy đủ hai tài liệu ngày 27/10 và dùng source/test liên quan để phản biện. Tài liệu tổng quan 1.258 dòng là nguồn diễn giải có phần chưa khớp implementation. Kết quả 68 tests/typecheck là kiểm chứng ở lượt trước cùng ngày, không rerun tại review này. Browser URL không được xác minh cùng checkout nên không chấm mỹ thuật, responsive hay a11y thực tế. Không gọi Gemini bằng ảnh/tài khoản thật trong nhiệm vụ.

## 2. Change Impact Matrix — V2.1 Improved → V2.2

Tất cả quyết định mới trong bảng là **PROPOSED / chưa phê duyệt**, kể cả khi user yêu cầu nghiên cứu hướng Hybrid. Chỉ sửa planning, không sửa hành vi runtime.

| Quyết định cũ V2.1 | Nhược điểm còn lại | Refinement V2.2 | Lý do / mức ảnh hưởng | Tài liệu / task cần đồng bộ | Rủi ro | Phê duyệt |
|---|---|---|---|---|---|---|
| Chọn P-A document-first làm lõi | Hạ measurement/estimate thành bổ sung dù PRODUCT có core này | So A Measurement/B Document/C Hybrid, khuyến nghị C có điều kiện | Cao — bảo toàn thế mạnh, không chuyển scope theo hypothesis | Master§1/4/5;UX§2–3/11;AI§3;BacklogM1/M2;R01 | Hybrid phình UI/scope | DECISION REQUIRED R01/R08 |
| First usable S1 phải có upload/OCR | Key/format/job trở thành đường găng dù manual/reading không cần | M1quick/records và M2measurement độc lập, M3file | Cao — giá trị sớm và an toàn, không chờ OCR | Master§12;UXjourneys;AIrollout;BacklogS1.1–4/S3.1 | Tích hợp nhiều nhánh | PROPOSED |
| S3.1 phụ thuộc record+D03/D04 toàn phần | Không lưu/hiểu usage khi thiếu giá | Observation→usage→estimate tiers; giá chỉ gate money | Cao — remove wrong dependencies, preserve math | Master§7/17;C08;S3.1;AIavailabilityeval;UX06 | Legacy Bill coupling | DECISION REQUIRED D02/D03/D04 theo tầng |
| Initial date chưa biết cần hỏi trước nhập | Có thể chặn mốc đo mới hợp lệ | Lưu dated baseline mới, chưa interval/usage | Cao — không giả ngày cũ và không mất dữ liệu thực | C08/S3.1;Master§17;UX06;AIbaselinecase | User hiểu baseline là consumption | PROPOSED; D02 |
| Ước tính có thể làm quick-entry USER_ENTERED | Dễ relabel forecast thành actual chi phí | Explicit actual-charge attestation; estimate không auto-record | Cao — giữ nghĩa tài chính và lịch sử paid | D01/C02/C03;S1.1/S1.4;UX07;AIschemas | User gõ tiền cũng có thể sai | DECISION REQUIRED D01 |
| Same-data mới liệt kê entity | Chưa ai sở hữu field/quyền ghi; stale derived chưa rõ | Authority/lifecycle/invalidation/projection từng domain | Cao — không overwrite evidence/source/history | Master§17;C05/C08/C09;AI source refs | Migration/schema tăng | PROPOSED |
| Duplicate rich matching S2 sau capture | Manual/manual hoặc manual/doc có thể đếm đôi sớm | Minimum candidate/link/canonical active revision cùng M1/M3 | Cao — no doublecount trước AI semantics | S1.1/S1.2/S2.2;C09;Mastercases | False merge | PROPOSED; user confirm |
| Correction rộng S4, minimum undo chưa phủ record/reading | Release sớm tạo lỗi không sửa được | Cancel/supersede M1, reversal M1, invalidation M2, deleteM3 | Cao — safety đi cùng writes | R07/C09;S1.1/1.4/3.1/4.1/4.2 | Thay observation ảnh hưởng neighbor intervals | DECISION REQUIRED R07 |
| JPEG/PNG-first, PDF defer sẵn | Chưa có corpus, textPDF có thể thuận tiện/ít AI hơn ảnh | M0sample gate→boundedformat M3; ảnh/textPDF/scan/multipage tách | Vừa–cao — không chọn ngược nhu cầu | R06;UXformatmatrix;AI extraction;C04/S1.2 | Parser/security/cost | DECISION REQUIRED R06/R02/R03 |
| Inbox task dẫn đầu, measurement entry phụ | Dễ thành hóa đơn tracker có chatbot | Dashboard task+actual+usage; ba-entry dễ thấy, chọn theo goal | Cao — UI thể hiện đúng hybrid | UXwireframes/navigation;Master§6;S0.1/S1.3/S3.1 | Quá nhiều CTA/empty metrics | PROPOSED R08 |
| Baseline AI analysis chờ orchestrator | Trì hoãn forecast/anomaly hữu ích | Local metrics/template sớm M1/M2, bounded dialogue M5 | Cao — core hoạt động noGemini | AI7surfaces/12automations;S1.3/S3.3/S2.3 | Nói vượt mức evidence | PROPOSED |
| Tự động hóa thiếu cooldown/quyền/test mỗi mục | Có thể spam hoặc bypass branch | Mỗi automation có trigger/conditions/auth/source/dedupe/cooldown/cap/test | Vừa — contract vận hành, không tăng skill | AI A01–12;S2.1/S3.3;QA matrix | Nhiều policy cần kiểm nhất quán | PROPOSED |
| Eval target global90% có thể che lỗi task | Sai tiền/hộ không được bù bằng câu dễ | Mode-level outcomes và critical fail gates | Cao — kiểm giá trị thật | AIeval;Master§14/17;S2.3/S4.4 | Dataset thiếu đại diện | PROPOSED |
| Mọi backlog EP-S1/S2 là prerequisite rộng | Không release branch-only/pilot độc lập | Hard/shared-interface/optional/release-gate graph, taskportion rõ | Cao — critical path theo outcome chọn | Master§12;Backlog§3 và mọi dependency field | Dependency chỉ đổi sơ đồ không đổi task | Đã refinement planning; triển khai chưa duyệt |
| Prediction nhiều hơn giá trị đo xác nhận | Có thể bỏ core khi không đủ forecasthistory | Lưu/usage hữu ích trước forecast; baseline forecast không gate optionalwhatif | Vừa — rõ data requirements | S3.1/S3.3/S3.4;AI mode matrix;UX08 | Forecast sai khi interval không comparable | PROPOSED |
| Unknown month/account chỉ nói nullable | Tổng dashboard có thể tự gán hiện tại | Unassigned period/unallocated account counts và projections tách | Cao — source/denominator đúng | C05/Master§17;S1.1/S1.3/S4.2 | UI nhiều nhóm | PROPOSED |

Các tiến bộ V2.1 giữ nguyên: modular monolith/stack, Decimal/snapshot, no providerAPI giả, prompt/code separation, scope/version/idempotency, limits 2model/3read/45s, durablejob khi nhận upload, privacy/backup/migration, originalplan preservation. Không refactor toàn bộ trước core journey.

## 3. Nội dung giữ, bỏ và cần nghiên cứu

GIỮ: stack, modular monolith, Decimal, snapshot, authorization server, token rotation, no raw SQL tools, deterministic fallback, idempotency/dedupe, migration bảo toàn, giới hạn ngành tích hợp chưa có.

CẢI THIỆN: typed contracts, tool schemas/provenance, transaction ngắn, cache isolation, test/migration evidence và tài liệu source of truth.

REFINE V2.2: activation hybrid, early independent measurement tiers, shared financial authority/lifecycle, three-entry IA, sample-gated document workflow, exactpair reconciliation và embedded intelligence.

LOẠI: dữ liệu personalized hardcode, benchmark hộ thiếu dataset, AI progress giả, dependency meter/tariff trước lưu khoản, latest-utility matcher và fallback giá xuyên scope. “Loại” là đề xuất thay behavior trong triển khai, không xóa dữ liệu/code ở nhiệm vụ này.

BỔ SUNG: actual quick-entry, document inbox/review, task resolution, quality/provenance per field, duplicate/version handling, late-document reconciliation, family handoff, delta explanation, event digest.

NGHIÊN CỨU: hành vi tự đo/nhận/trả theo nhóm hộ, corpus ảnh/textPDF/scan/multipage, willingness-to-review, OCR field correction, tariff rules/location, provider terms/retention, chính sách payment/correction. Không coi research docs kỹ thuật là user research.

## 4. Cải tiến vượt kế hoạch cũ: giá trị và đánh đổi

### N01 — Ghi nhanh không ảnh/không cloud (PROPOSED, P0, M1/M3 theo nguồn)
Vấn đề: không có ảnh/key hoặc không muốn gửi dữ liệu. Giá trị: vẫn có sổ và nhắc hạn. Ví dụ: “Tiền nước tháng 10 là 180 nghìn, chưa rõ hạn”. UX: form ít trường, due=null, review một lần. Kỹ thuật: cùng draft/confirm contract, basis USER_ENTERED, parser deterministic hoặc optional LLM theo consent. Rủi ro: ngày/đơn vị mơ hồ cần hỏi, không auto-commit lời chat. Complexity S–M; V2 có, không phụ thuộc provider.

### N02 — Hộp việc có thể kết thúc (PROPOSED, P0, M1/M3/M4)
Vấn đề: unread notification không phản ánh khoản đã xử lý. Giá trị: biết việc tiếp theo và ngừng nhắc khi xong. Ví dụ: “Kiểm tra hóa đơn nước”, rồi “Ghi nhận đã trả”. UX: task có source/owner/action, snooze/dismiss khác resolve. Kỹ thuật: task projection từ source revision/rule, idempotent after-commit job. Rủi ro: spam/false urgency; preference/cooldown, ngày cấu hình chỉ dự kiến. Complexity M; V2 có.

### N03 — Quality map từng trường (PROPOSED, P0, M1/M3 theo nguồn)
Vấn đề: một success badge che amount/period sai. Giá trị: người dùng tập trung phần cần sửa. Ví dụ: tiền rõ nhưng mã KH mờ. UX: highlight field cần kiểm, ảnh/snippet cạnh field, unknown không 0. Kỹ thuật: extraction version + field provenance/validation; không confidence tự khai làm quyền auto-confirm. Rủi ro: quá nhiều cảnh báo; ưu tiên field tài chính/identity. Complexity M; V2 có, bbox chỉ khi provider thực có.

### N04 — Duplicate và phiên bản hóa đơn (PROPOSED, P0, M1/M3/M4)
Vấn đề: upload lại/rescan/correction có thể ghi hai khoản. Giá trị: không đếm đôi và không mất bản sửa. Ví dụ: chụp lại cùng hóa đơn rõ hơn. UX: “Có thể cùng hồ sơ”, chọn thêm chứng cứ/link phiên bản/giữ riêng có lý do. Kỹ thuật: household hash, invoice identity candidate, confirmation lock/version. Rủi ro: false merge; không auto unique amount+month hoặc lộ hash hộ khác. Complexity M–L; V2 có minimum manual/manual candidate M1 và exactfile+manual/document review M3, semantic refinement M4; không đợi semantic model để chống đếm đôi.

### N05 — Handoff nội bộ gia đình (PROPOSED, P1, M5)
Vấn đề: người upload không có quyền ghi trả hoặc cần người khác kiểm tra. Giá trị: không nhắn lại số liệu ở kênh khác. Ví dụ: thành viên tạo draft nhờ owner duyệt. UX: task gửi người trong hộ đủ quyền, scope rõ. Kỹ thuật: assignee reference + membership authorization + notification dedupe. Rủi ro: lộ nội bộ/thêm quyền ngầm; revoke xử lý, không tự gửi email. Complexity M; V2 sau role mapping, external messaging DEFERRED.

### N06 — Tìm chứng từ bằng câu tự nhiên (PROPOSED, P1, M5)
Vấn đề: nhớ “hóa đơn nước tháng trước” nhưng không tên file. Giá trị: tìm và mở ngay record đúng. UX: filter có thể sửa, kết quả có kỳ/nguồn, ambiguity hỏi lại. Kỹ thuật: slot→scoped query, full-text nếu cần text hợp lệ; không vector store bắt buộc. Rủi ro: scope/relative date; kiểm quyền và timezone. Complexity M; V2 có.

### N07 — Giải thích biến động thành phần (PROPOSED, P1, M1/M2 baseline, M5 enriched)
Vấn đề: câu “tăng 20%” không giúp hành động. Giá trị: tách do lượng dùng/độ dài kỳ/giá/phí khi đủ dữ liệu. Ví dụ: tiền tăng nhưng mức dùng/ngày tương đương. UX: breakdown nguồn, phần unknown và gợi ý kiểm tra. Kỹ thuật: deterministic delta decomposition trên comparable records; LLM chỉ diễn đạt. Rủi ro: attribution sai khi thiếu interval/fees; kết luận giới hạn thay đoán thiết bị. Complexity M–L; Cost-only delta có từ M1, usage-only M2 không giá; attribution giá/phí cần D02–D04/comparable pair.

### N08 — What-if không làm bẩn sổ (PROPOSED, P2, optional sau M2)
Vấn đề: muốn thử giảm dùng nhưng không muốn đổi dữ liệu thật. Giá trị: hiểu tác động giả định. Ví dụ: nhập consumption mục tiêu và xem estimate theo tariff chọn. UX: nhãn mô phỏng, reset, không CTA “đã tiết kiệm”. Kỹ thuật: pure calculator sandbox input + pinned policy; không mutate expense. Rủi ro: hiểu là dự báo bảo đảm; assumptions và scope. Complexity M; V2 nếu pilot cho thấy có nhu cầu, nếu không defer.

### N09 — Digest có lựa chọn (PROPOSED, P2, M6 optional)
Vấn đề: thông báo riêng lẻ quá nhiều hoặc mở app không biết thay đổi gì. Giá trị: một tổng hợp việc xong/chưa xong có nguồn. Ví dụ: hai khoản mới, một draft chưa rõ hạn. UX: opt-in theo kỳ, không digest không có thay đổi. Kỹ thuật: dataset revision + template, model optional; không gửi ra ngoài chưa cho phép. Rủi ro: fatigue/PII trong thông báo; giới hạn nội dung/kênh. Complexity M; V2 opt-in, email delivery defer khi chưa có hạ tầng.

### N10 — Tạm dừng tài khoản và tín hiệu thiếu hồ sơ (PROPOSED, P1, M5)
Vấn đề: không có hóa đơn không đồng nghĩa bỏ quên. Giá trị: giảm nhắc sai với hộ chuyển nhà/tạm ngưng. Ví dụ: nước gộp phí nên không có hóa đơn riêng. UX: “Không theo dõi kỳ này” có lý do và thời hạn, không tạo khoản 0. Kỹ thuật: account tracking preference/coverage exception, detector xét trước task. Rủi ro: ẩn việc thật nếu thiết lập nhầm; hiển thị scope và cho khôi phục. Complexity S–M; V2 có tối thiểu snooze/skip, không auto đoán không phát sinh.

## 5. Decision register và hệ quả nếu chưa chốt

Tất cả dòng là **DECISION REQUIRED**, chưa áp dụng vào sản phẩm. Owner mặc định “chủ dự án” là trách nhiệm đề xuất, chưa xác nhận người cụ thể.

| ID | Cần quyết định | Khuyến nghị PROPOSED | Lựa chọn khác và hệ quả | Gate/ai tham gia |
|---|---|---|---|---|
| R01 | Định vị và đường activation | C Hybrid task-first, ba đường độc lập theo goal | A Measurement sâu nhưng nhập liệu; B Document dễ thành tracker; C cần progressive UX | M0; chủ dự án + người dùng pilot |
| D01 | Amount basis và payment assertion | Expense actual/document hoặc user entry riêng Estimate | Chỉ document chặn user thiếu ảnh; final_amount chung gây nhầm | Trước M1 actual/payment; Product/domain |
| D02 | report period và consumption interval | Record nullable interval, measurement strict | Calendar-only dễ so sai; strict mọi record chặn capture | Trước M1 report và M2 observation/interval; data/domain |
| D03 | Giá đổi giữa kỳ | pending khi thiếu policy; simulation explicit | Cuối kỳ/chia ngày chỉ sau nguồn phù hợp | Trước M2 PRICE output, không observation/usage; domain/data owner |
| D04 | Nguồn giá/pilot scope/người duyệt | Narrow verified scope, admin publish có nguồn | Custom giá chỉ simulation; AI auto publish không khuyến nghị | Trước M2 PRICE output, không chặn M1/M2 usage |
| R02 | External AI, retention, delete | No-cloud path; consent trước gửi; separate lifecycle | Self-host OCR tăng chi phí; không ảnh giảm tiện lợi | Trước M3 file/external hoặc external explanation khi bật; owner/security |
| R03 | Ai trả phí và cap/concurrency | Budget hữu hạn, reserve/settle, stop/degrade | Unlimited không kiểm soát chi phí | Trước external pilot; owner/ops |
| R04 | Team, hosting, rollout/support/rollback | Pilot cohort nhỏ, acceptance+restore trước mở rộng | Public ngay tăng ops/security scope | Trước lịch/cutover; owner/ops/QA |
| R05 | Quyền runtime mới | Docs read/upload/external-process/record-confirm/pay phân biệt | Map legacy write sang tất cả có rủi ro | Trước write tương ứng M1/M2/M3; owner/security |
| R06 | JPEG/PNG, PDF và credit scope | Sample/cost/security gate ở M0, boundedformat M3; textPDF có thể sớm; credit unsupported không ép dương | Ảnh-only có thể miss e-bill; allPDF tăng pages/parser/security; chọn corpus evidence | Trước M3 file scope; Product/QA |
| R07 | Correction/reversal | Giữ original, revision có reason, reversal assertion không erase | Edit trực tiếp mất audit; ledger đầy đủ tăng scope | Trước M1 cancel/reversal/M2 observationinvalidation; M6 correction rộng; domain/security |
| R08 | User study/prototype/visual | So concept, test fixture tasks, duyệt visual proposal | Chỉ code trước giảm bằng chứng fit | M0; owner + UX/pilot |
| R09 | Reminder cadence/notification channels | In-app, opt-in insight/digest, source-labelled | Push/email cần permission/delivery thật | Trước due/event capability bật M1/M2/M5; Product/ops |

Gate không phải lý do dừng nhiệm vụ planning: mọi phương án đã mô tả để chủ dự án có thể review. Implementation chỉ chờ quyết định tại phần phụ thuộc; không lấy im lặng làm đồng ý.

## 6. Năm rủi ro trọng yếu và control

| Risk | Tác động / bằng chứng | Control đề xuất | Kiểm chứng và gate | Owner đề xuất |
|---|---|---|---|---|
| K01 — Sai định vị | Xây sổ tài liệu trong khi người dùng muốn tự đo hoặc chỉ cần nhắc; hiện chưa research | S0 so ba concept, giữ quick-entry/measurement, không ép cloud | Observe task completion/friction trên 5–8 người; xem lại R01 trước diện rộng | Product + chủ dự án |
| K02 — Sai OCR/identity/interval | Ghi tiền/ghép kỳ nhầm; E06/E15 | Field review, null, account confirmation, matching đúng pair/version, NOT_COMPARABLE | Fixture wrong-month/multi-account/zero/blur/injection; critical fail không release | Domain + AI + QA |
| K03 — Lộ dữ liệu | Cloud payload/ảnh/cache/inflight/revoke; E06/E09 | Minimized payload, R02/R05, private file, context epoch, fresh auth, redacted logs | Payload/cross-house/browser/job-delete/revoke tests; R02 trước dữ liệu thật | Security + fullstack |
| K04 — Sai ý nghĩa tiền | Estimate/manual assertion thành nợ/provider settlement; E10/E11 | D01 contract/basis labels, no double count, no auto financial commit, late-document review | Fixture 500k estimate/530k doc/500k assertion giữ mọi nguồn; không tự đổi PAID | Product + domain + UX |
| K05 — Migration mất dữ liệu/hành vi | Schema mới optional account khác legacy, rollback khó | Coexist/adapters, basis-aware mapping, snapshot giữ nguyên, restore rehearsal | DB/file counts+IDs+links+totals theo basis; write mới còn đọc được khi rollback | Data + ops + QA |

Rủi ro bổ sung: chi phí model/fan-out (R03, budget/cancel); notification fatigue (task dedupe/cooldown/dismiss); tariff sai hiệu lực (D03/D04, pending); deployment giả healthy (schema readiness/fail-fast); user không sửa nổi OCR (M0/M3 sample và fallback); credit/PDF không hỗ trợ (R06, no forced parse). Các control là PROPOSED, chưa chứng minh hiệu quả từ giấy.

## 7. Architecture review: giữ đơn giản nhưng đủ

**PROPOSED quyết định A1:** modular monolith giữ stack; domain seam theo slice. Thay framework/microservices không giải E02/E05/E10. Revisit nếu tổ chức team/deployment boundary thực cần.

**A2:** Document/ExpenseRecord/Estimate/PaymentAssertion riêng semantics, không nhất thiết bốn service/bốn deploy. Tốn mapping/migration nhưng tránh trạng thái giả. Không xây double-entry accounting đầy đủ cho release chỉ manual full payment.

**A3:** deterministic workflow + bounded tool-calling. Tăng flexibility Q&A mà không cấp model SQL/write authority. Planner/multi-agent chỉ sau eval/cost đo được lợi ích.

**A4:** explicit scope/revision/idempotency từ browser tới transaction, không chỉ hide button/prompt. Chi phí thêm tests/version handling đổi lấy kiểm soát đúng khoản/hộ.

**A5:** durable job tối thiểu khi nhận upload dài; PostgreSQL worker/outbox đủ xem xét đầu. Broker/Redis/shared rate limit là quyết định theo tải và số process, không dependency mặc định của sản phẩm. Không hứa exactly-once network calls.

Nghiên cứu chính thức được đối chiếu trong independent review: [PostgreSQL constraints](https://www.postgresql.org/docs/16/ddl-constraints.html) — nullable unique cần semantics chủ động; [range constraints](https://www.postgresql.org/docs/16/rangetypes.html) — interval/exclusion sau khi chốt scope; [locking](https://www.postgresql.org/docs/16/explicit-locking.html) — lock ordering/retry chứ không bảo đảm hết deadlock; [FastAPI BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) — không tự bảo đảm durable completion. Các lựa chọn app ở đây là suy luận thiết kế, không được thư viện quyết định thay.

## 8. Independent review theo vai và kết quả xử lý

**Product:** V2.1 đã giảm setup nhưng chưa chứng minh document-first tốt hơn, làm measurement xuống muộn. V2.2 so A/B/C nghiêm túc, đề xuất Hybrid và M1/M2 độc lập OCR; hai prior-workflow loops và metrics theo mode. R01/R08 vẫn chưa phê duyệt.

**UX:** giảm bước không phải mục tiêu duy nhất; payment/tariff cần review. Resolution: mỗi flow có before static/unmeasured, after target, states/AC; visual cụ thể nhưng chưa rendered. Còn mở: prototype/actual checkout browser.

**Backend/fullstack:** Bill legacy không chứa được invoice không measurement; global cache late response. Resolution: records domain/adapters, permission/context epochs, transactions ngắn, typed contracts. Còn mở: schema details trước task triển khai, không migration tự ý.

**AI:** routing regex/memory giả/skills lệch code/đa model fallback thiếu cap. Resolution: hybrid có limit; merge map14 skills, typed provenance, eval critical và per-field, no extra model để “giải thích” OCR khi template đủ. Còn mở: provider capability/price/cap/retention thực.

**Security/data:** upload limit sau decode, household context vào provider, revoke trong job/lock, exact hash chưa đủ duplicate. Resolution: R02/R05, minimal payload/local match, confirm fresh auth/version, multi-signal duplicate review; chưa gọi đây penetration test.

**QA:** 68 tests/create_all/SQLite không chứng minh Alembic/PG concurrency/OCR accuracy/E2E. Resolution: release-specific gates, PG separate connections, source+semantic eval, actual browser/pilot, rõ kết quả lịch sử.

**Ops:** secret dài mặc định vẫn pass, startup nuốt lỗi/schema health yếu, persisted work cần hơn RAM. Resolution: fail-fast/schema readiness/demo seed riêng trước release cohort; job recovery+restore DB/files; chưa mở rộng hạ tầng vô căn cứ.

**Xung đột giải quyết V2.2:** local quick-entry và measurement có release riêng, không chờ OCR; observation một mốc có ngày không cần interval cũ, usage cần hai mốc; giá chỉ gate predicted money; actual cần attestation, source/history không bị relabel; min duplicate/cancel/reversal/invalidation/delete đi cùng mốc tạo dữ liệu. Multi-turn/event phrasing không chặn metric/local template.

Ba reviewer là subagent độc lập, main tổng hợp và kiểm tra consistency; không đại diện stakeholder pháp lý hoặc người dùng thực. Những quyết định cần chủ dự án vẫn để DECISION REQUIRED.

## 9. Bao phủ yêu cầu và evidence còn thiếu

- Product: Master §1/3/4/5, ba định vị có trade-off/cost/khả thi, user research gate.
- UX toàn hệ thống: UX01–12, shared states, before/after logical stages, AI/AC, visual/mobile/a11y.
- AI: runtime alternatives, 14 skill mapping, prompt/code split, typed tool/memory/cost/failure/eval, 12 automation opportunities.
- Data/architecture: Master §7–10/13–14, D01–04 options không tự approve, migration bảo toàn.
- Cải tiến mới: N01–10 gồm vấn đề/giá trị/example/UX/kỹ thuật/rủi ro/complexity/priority/scope.
- Bảng cũ/mới: §2; giữ/cải thiện/thiết kế lại/loại/bổ sung/research: §3.
- Roadmap/tasks: Backlog giữ ID task Sx.y nhưng schedule M0–M6, từng task có story/dependencies/scope/input-output/contracts/AC/tests/risk/priority/DoD.
- Executive summary: Master §16 và bản tóm tắt cuối chat gồm 10 cải tiến, 5 architecture calls, 5 risks, khác biệt và khuyến nghị.

Chưa có: user interview, trustworthy rendered UI inspection đúng checkout, OCR field benchmark/live provider cost, PG concurrency/Alembic verification mới, production deployment/restore/load evidence. Không lấp bằng score tự chấm hoặc claim 100%.

## 10. Kết luận đề xuất để chủ dự án review

Không triển khai “V1 viết lại sạch hơn” hoặc “bill tracker có OCR/chat” làm mục tiêu. Khuyến nghị PROPOSED Hybrid: đo/usage/estimate sớm độc lập invoice, quick-entry actual độc lập meter/OCR, document theo format evidence; nối các nguồn đúng thời điểm để giải thích và tối ưu có căn cứ. Core local vẫn có ích khi bỏ LLM/OCR; không tự nhận Hybrid tốt nhất về retention.

Gate M1: D01/D02 report/R05/R07 minimum cancel/reversal; gate M2 observation: D02/R05/R07 minimal invalidation, priced estimate thêm D03/D04. Gate M3: C02 record seam+R02/R03/R06. R01/R08 định hướng/user research chung; R04 capacity/rollout theo enabled scope. Không cần chốt cloud/PDF để làm local measurement hoặc quick-entry; không thêm dependency ngược full admin/AI. Sau duyệt và lệnh triển khai riêng mới chuyển mốc được chọn thành spec.




## 11. Decision ID stability và các giả định chưa xác nhận

**D01** vẫn là cơ sở ghi nhận tiền/payment, **D02** là kỳ/interval, **D03** là giá đổi giữa kỳ, **D04** là nguồn giá và scope/người duyệt. **R01** vẫn định vị/activation, **R02** privacy/retention/external, **R03** chi phí/cap, **R04** nguồn lực/môi trường/rollout, **R05** quyền, **R06** format+credit scope, **R07** correction/reversal, **R08** research/prototype/visual; R09 cadence/kênh giữ nguyên. Chỉ recommendation và gate áp dụng được refine, không đổi ID để gán vấn đề khác.

Chủ dự án chưa duyệt: ưu thế Hybrid, lịch M1/M2 cụ thể, format whitelist, corpus/nhóm pilot, exact interval boundary, tolerance/comparability, retention/provider terms/cost caps, correction authority và tariff coverage. Tất cả đều là PROPOSED/DECISION REQUIRED, không lấy nội dung tệp yêu cầu nghiên cứu làm lệnh triển khai.

Để chuyển spec không phải suy đoán lại: chọn mode/mốc, pin acceptance portion của task cũ, duyệt đúng decision subset ở register §5, ghi version contract C01–C09 và fixtures. Nếu quyết định chưa duyệt, phần phụ thuộc giữ gated; phần đã đủ policy có thể làm trước. Giữ legacy calculator/auth/snapshot/history/valid forecast/anomaly đúng qua characterize/regression, nhưng không giữ test OCR đang coi initial reading đủ MATCH như behavior mong muốn.

## 12. Changelog V2.2 và báo cáo consistency

- Giữ hai bản V2 gốc, cập nhật đúng năm Improved lên V2.2; không tạo bộ planning từ đầu.
- Master: sửa định vị, thêm A/B/C decision trade-off matrix, capability-without-AI/OCR matrix, domain authority/lifecycle/projection, three-path architecture, M0–M6 DAG và scenarios.
- UX: giữ UX01–12/states/tokens, refine ba-entry task-first, dashboard cost/usage/task, thêm bốn structural wireframes, sample-format economics và path-specific AC.
- AI: giữ hybrid runtime A+B/budget/mapping14skills, bổ sung embedded7surfaces, mỗi A01–12 có trigger/conditions/permission/provenance/dedupe/cooldown/call cap/test; mode-level eval thay một global score quyết định.
- Backlog: giữ 20 task và 5 epic ID, update dependency tại từng block, C08 measurement tiers/C09 minimum lifecycle, tách first usable outcome khỏi OCR. Minimum duplicate/lifecycle đi sớm, advanced correction/format/model optional không gate core.
- Comparison: Change Impact Matrix và decision register cùng nghĩa, risk/control/review theo tám góc nhìn; tài liệu mở đang thiếu evidence được ghi rõ.

**Consistency cần kiểm trước bàn giao:** version/changelog đủ năm; cùng nghĩa D/R; mốc M không rename task S; S3.1 không có hard dependency S1.1/OCR/D03-D04 cho observation; record-only không usage causation; measurement-only không actual invoice; new estimate không relabel actual; unknown month/account có projection; format chỉ được bật sau sample/security/economics gate; AI caps/policy/budget thống nhất; mọi reference local còn tồn tại; checksum source/config/tests/migration/PRODUCT và hai V2 gốc không đổi.

Độc lập review lần cuối: Product/UX và AI agents review phạm vi chuyên môn; agent Data/Backend/QA/Security/Operations đọc chéo năm bản, main tổng hợp. Không tuyên bố user research, live OCR, actual checkout browser, PG concurrency hoặc production readiness đã đạt. Nếu checklist tĩnh đạt, chỉ gọi là **planning nhất quán trong phạm vi kiểm tra**, không bảo đảm dự án hết mọi rủi ro.
