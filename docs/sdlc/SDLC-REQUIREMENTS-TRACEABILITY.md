# Nhà Mình — SDLC Requirements & Traceability Register

Ngày: 28/10/2026 · Version1.0 · **PROPOSED, requirements baseline chưa được duyệt.**
Đọc [SDLC Master Plan](SDLC-MASTER-PLAN.md) và [V2.2 backlog](../replanning/V2-IMPROVED-BACKLOG.md).

## 1. Mục đích và cách sử dụng

Đây là initial requirement/traceability register để đi từ Planning sang Requirements Analysis, không thay SRS đầy đủ hoặc giả định mọi task V2.2 đã approved. Mọi requirement bên dưới là candidate PROPOSED cho formal baseline; những mục lấy từ PRODUCT có context đã xác nhận nhưng chi tiết AC/permission/policy vẫn cần PO duyệt.

Nguồn: PRODUCT.md ở thư mục cha (high-level context); Master/UX/AI/Backlog/Comparison V2.2; source V1 là evidence CURRENT, không tự biến behavior hiện tại thành requirement đúng. Evidence VERIFIED lịch sử và giới hạn đọc tại MasterV2.2§2; lượt SDLC28/10 không chạy tests mới.

Trạng thái mỗi dòng hiện là **PROPOSED / chưa có execution evidence**. “Test dự kiến” là testcase+expected result, không phải test đã có/đã pass. Priority P0 là control/độ đúng chặn release liên quan, P1 là chức năng core, P2 là option; không tự coi P2 baseline forecast là nâng cao hoặc ngược lại.

Requirement IDs SDLC-FR/BR/NFR là namespace mới cho truy vết SDLC; không đổi D01–D04/R01–R09 hay 20 task ID cũ. Design refs C01–C09 là contract đề xuất trong backlog; sau G3 cần pin phiên bản slice, schema và diagram thật.

## 2. Candidate functional requirements

| ID / priority | Yêu cầu và outcome | Nguồn / decision cần chốt | Task / design đề xuất | Test dự kiến và acceptance |
|---|---|---|---|---|
| SDLC-FR01 P0 | Authenticated user chỉ xem/ghi dữ liệu hộ được phép, đổi hộ không lẫn response/cache | PRODUCT; R05 | S0.2, mọi task write; C01 | SDTC01: userA không đọc/confirm ID hộB; đổi hộ khi request cũ pending không render data cũ |
| SDLC-FR02 P1 | Tạo/chọn hộ, account/meter theo mục tiêu; không bắt meter với actual entry | PRODUCT + UX01–03; R01/R05 | S0.1/S1.1/S3.1; C01/C02/C08 | SDTC02: quick-only không meter vẫn dùng; measurement-only không invoice vẫn tạo meter/baseline |
| SDLC-FR03 P1 | User có quyền lưu observation giá trị/đơn vị/ngày thật làm baseline | PRODUCT; D02/R05/R07 | S3.1 tierA; C08 | SDTC03: không biết prior date vẫn lưu mốc mới; chưa sinh interval/usage/actual giả |
| SDLC-FR04 P0 | Hai observations hợp lệ cùng meter/unit sinh interval/consumption theo D02 | PRODUCT; D02 | S3.1 tierB; C08 | SDTC04:1000→1120kWh20→27/10=120kWh theo convention; saiunit/thứtự/countergiảm chặn hoặc route policy rõ |
| SDLC-FR05 P0 | Tính estimate tiền từ đúng scope giá/policy/snapshot; thiếu giá vẫn giữ measurement/usage | PRODUCT; D03/D04 | S0.2/S3.1 tierC; C08 | SDTC05: giá provider khác không fallback; tariff missing→NOT_COMPUTABLE, không amount0 hoặc mất observation |
| SDLC-FR06 P1 | Baseline forecast/anomaly có method/window/data gate; lượng dùng và money dự báo tách | PRODUCT; D02/D03/D04 theo priced part | S3.1/S3.3; C05/C08 | SDTC06: đủ comparable history nhưng thiếu giá có consumption forecast, amountnull; thiếuhistory nói rõ, không chẩn đoán thiết bị |
| SDLC-FR07 P1 | Ghi actual qua quick-entry, amount/utility/basis được user xác nhận, kỳ/hạn/account có thể chưa biết | V2.2; D01/D02/R05/R07 | S1.1; C02/C09 | SDTC07:180000VND lưu/mở lại nguyên; kỳnull→Chưa gán kỳ, không tự hiện tại; no meter/tariff/OCR |
| SDLC-FR08 P0 | Candidate duplicate phải được review, link evidence không tạo obligation mới | V2.2; D01/R07 | S1.1/S1.2/S2.2; C09 | SDTC08: manual/manual và manual/document concurrent có review/idempotency/canonical version; không unique amount+month |
| SDLC-FR09 P1 | File thuộc format được duyệt có private upload, extraction draft, field review và confirm/link actual | V2.2; R02/R03/R05/R06 | S1.2; C04/C02 | SDTC09: unsupported/blur/missingfield/quota→typedstate+manualfallback; retry/reload không duplicate effect; OCR không tự confirm |
| SDLC-FR10 P0 | Manual payment assertion pin record/version/amount/date/source, không bank confirmation | PRODUCT manualpayment + V2.2; D01/R05/R07 | S1.4; C03 | SDTC10: double submit một assertion; mismatch→review; model/userchat chưaserverconfirm khôngPAID; oldassertion khôngrewrite khi invoice mới |
| SDLC-FR11 P1 | Detail/dashboard/totals phân biệt actual/estimate/cash/coverage, source có thể mở đúng quyền | PRODUCT + V2.2; D01/D02/R05 | S1.3/S3.3; C05 | SDTC11:actual530000+estimate500000 không tổng1030000; paid500000 riêng; unallocated/unassigned rõ |
| SDLC-FR12 P1 | Due reminder/task có nguồn/ngày/preference, không đồng nghĩa read hoặc xử lý tiền | PRODUCT; R09/D01 | S2.1/S2.4; C05/C09 | SDTC12: khôngbiếtdue khôngoverdue; configured due nhãn dựkiến; đãtrả ngừngnhắc; restart khôngtrùng |
| SDLC-FR13 P1 | Reconcile exact pair account/interval/sourceversions, thiếu cặp trả NOT_COMPARABLE theo field | V2.2; D01/D02/D03 | S3.2/S2.2; C05 | SDTC13:bill tháng8 khôngso latest tháng9; thiếuVAT khôngkếtluận tổngkhớp; manualactual cũngsođược khôngảnh |
| SDLC-FR14 P1 | Embedded assistant giải thích từ scoped services, hỏi slot thiếu, multi-turn đúng context | PRODUCT assistant + V2.2; R02/R03/R05 | S1.3/S2.3; C06 | SDTC14:còn nước giữ kỳ/basis nhưng bỏaccountđiện; nhiềuaccount hỏi; noGemini vẫn localform/math/sourcecard |
| SDLC-FR15 P1 | Event insight có source/rule/version, permission/dedupe/cooldown, không fake personalized claim | PRODUCT anomaly + V2.2; R09 | S3.3; C05/AI A01–12 | SDTC15:sourcekhôngđổi→0newLLM/notifier; monetarychange khôngsuyconsumption, sốcard khớp service |
| SDLC-FR16 P0 | User được sửa nhầm an toàn theo scope: cancel/reverse/invalidate/delete và giữ lịch sử | V2.2; R07/R02/R05 | S1.1/S1.4/S3.1/S1.2, S4.1rộng; C03/C08/C09 | SDTC16: mốc đo sai→dependentstale, khôngerasenearinterval/snapshot; xóaảnh pendingjob khôngresurrectrecord/file |
| SDLC-FR17 P1 | Admin validate/publish tariff với scope/hiệu lực/nguồn/reviewer; history không bị đổi | PRODUCT; D03/D04/R05 | S3.1 minimalgovernance/S4.3 fullUI | SDTC17:overlap/ambiguity bịchặn; oldsnapshot táihiện; admin khôngtự xem tài liệu hộ |
| SDLC-FR18 P2 | Budget/what-if/digest/recovery/advancedformats chỉ bật theo scope/evidence đã duyệt | V2.2 optional; R02/R03/R06/R09 | S2.5/S3.4/S4.5/S4.2–3 | SDTC18:unset không giả%budget;simulation khôngmutateactual; noemailconfigured khôngfake gửi; khônggateM1/M2 |

## 3. Candidate business rules — điều kiện tài chính và dữ liệu phải baseline

| ID | Rule đề xuất | Decision / test liên quan |
|---|---|---|
| SDLC-BR01 | Observation/usage/estimate độc lập actual invoice; new estimate không tự tạo debt/actual | D01/D02; SDTC03–07/11 |
| SDLC-BR02 | USER_ENTERED actual cần người dùng xác nhận khoản thực tế; xác nhận số copy từ forecast chưa đủ | D01; SDTC07/10/11 |
| SDLC-BR03 | Actual amount, estimated amount và paid-cash là projections riêng; paymentuserreport không provider verified | D01; SDTC10/11 |
| SDLC-BR04 | Interval derive từ dated observations, reportmonth không phải measured interval; unknown giữ null | D02; SDTC03/04/07 |
| SDLC-BR05 | Tariff applicability/provider/category/location/hiệu lực và rounding phải rõ; nhiều version cắt kỳ thiếupolicy→pending | D03/D04; SDTC05/17 |
| SDLC-BR06 | Model không quyết quyền, khôngSQLtùyý, khôngcompute tài chính, khôngauto publish/pay/correct | R05/D01; SDTC01/10/14/17 |
| SDLC-BR07 | Confidence/OCRsuccess không đủ confirmfinancial; supplier-reported reading không tự thay independent observation | R06/R05; SDTC09/13 |
| SDLC-BR08 | Sourcecorrection làm derived stale và recomputeversion mới; không rewrite snapshot/assertion cũ | R07; SDTC10/13/16 |
| SDLC-BR09 | Legacy bill/manualpayment giữ ID/basis gốc; không relabel invoice hoặc suy user đã chọn policy mới | D01/R07; SDTC10/19 |

Chủ dự án/domain owner duyệt rule khi G2; engineer không tự chọn số ngày/phân bổ giá, chữ ký nhà cung cấp hoặc tolerance tài chính từ tên field. Date/unit precision/convention còn mở được chốt trong D02/D03 của slice trước G3.

## 4. Candidate nonfunctional requirements

| ID / priority | Quality / control đề xuất | Test và cách chốt acceptance |
|---|---|---|
| SDLC-NFR01 P0 | Household isolation, least privilege, fresh auth tại financial confirm, no private payload trong public search | SDTC01/14/20; test API+cache/inflight/revoke+payload; critical breach không được bù bằng accuracy chung |
| SDLC-NFR02 P0 | Decimal math/snapshot/provenance/version/idempotency; không partial commit/trùng effect | SDTC04/05/08/10/19; PG separateconnections+exactfixtures, khôngsuy từSQLite |
| SDLC-NFR03 P0 | Private file/ingress type-size-pixel-page limits, consent/retention/deletion rõ | SDTC09/16/20; enabledformat corpus+limits/permission/job/delete; R02/R06 chốt trước file thật |
| SDLC-NFR04 P1 | Mobile/responsive/keyboard/focus/status/error/labels, đề xuất target WCAG2.2AA cho màn scope | SDTC21:manual+a11y/E2E đúngcheckout,360/768/1440 và zoom; target cần baseline, không tuyên bố conformant từ tokenCSS |
| SDLC-NFR05 P1 | Performance/capacity/cost hữu hạn và đo trên môi trường/workload xác định | SDTC22:pin machine/dataset/concurrency/p95/cost thresholds trướcđo; R03/R04 chưachốt thì không tựgán SLA |
| SDLC-NFR06 P0 | Migration/backup/restore/compatibility và durable accepted jobs phục hồi được | SDTC19/23:empty+legacyAlembic/restoreDBfiles/restartlease; preservation bybasis/status; RPO/RTO trướcrelease |
| SDLC-NFR07 P1 | AI budget/policy/schema/provenance/fallback áp mọi branch; runtime nhiềuagent không mặc định | SDTC14/15/20:2model/3read/45s là configPROPOSED V2.2, retry/repair trongcap; same-logicaljob khôngpromise exactly-once externalcall |
| SDLC-NFR08 P0 | Production config failfast, schema readiness, no secret mặc định/logPII | SDTC23:failedmigration khônghealthyrelease; known defaults rejected; logs redacted; devseed khôngproduction |
| SDLC-NFR09 P1 | Maintainability/traceability/observability đủ sửa lỗi mà không framework/broker dư thừa | SDTC24:Requirement→design→commit→test→UAT→release links valid, logs request/job/tool metadata khôngrawsecret; owner/runbook rõ |

## 5. Test scenario register bổ sung — kỳ vọng, chưa execution

| Test ID | Scope | Expected result / evidence cần ghi |
|---|---|---|
| SDTC19 | Migration/legacy/restore | DB trống và bản sao legacy upgrade đúng, ID/snapshot/amount/basis giữ; reportcounts/totals/exception; restore DB+files diễn tập, không suy từ create_all |
| SDTC20 | AI/security/privacy | Injection/PII/foreignrefs/directadapter/cache/job retry không bypasspolicy; no unauthorizedwrite; sourcecard đúng; provideroutage có fallback |
| SDTC21 | UX/a11y/E2E | Từng mode hoàn thành trên đúngcheckout/build,keyboard/reader/mobile,error/offline; screenshot/manualresults đúngsourceversion |
| SDTC22 | Performance/cost | Workload+machine+dataset+thresholds approved trướcđo; report latency/error/calls/usage/cost thật hoặcunknown; khônghứa khôngphíreplay |
| SDTC23 | Deploy/jobs/ops | Migrationfail chặnstart/readiness; acceptedjob phục hồi bounded saucrash; privateaccess/retention policyđúng; smokebuildversion vàsupportowners rõ |
| SDTC24 | Traceability/handover | Không requirement trongrelease thiếu test/evidence/owner; UAT và go/no-go đúngartifactversion; knownlimitations vàrollbacktrigger rõ |

SDTC01–18 nằm cùng hàng FR tương ứng. Trước execution viết case cụ thể preconditions/dataset/steps/assertions theo slice; ví dụ SDTC05 có missingprice/crossprovider/midchange/overlap các case riêng. Mock pass không thay liveprovider evidence, UAT không thay PGconcurrency hoặc securitytest.

## 6. Mẫu traceability record khi baseline và thực hiện

Mỗi requirement có các trường: ID, version, source, actor, preconditions, trigger, input/output, businessrules, happy/alternate/error flows, AC, priority, owner, approval actor/date, linked D/R IDs, design refs/version, task/commit/PR, testcases, testenvironment/build/dataset, executionlog/result, defectIDs, UAT/release refs.

Hiện chỉ có requirement candidates và mapping planning ở các bảng trên. Các trường commit/build/log/UAT/release chưa có phải ghi **chưa có**, không sinh URL/evidence giả. Khi slice G2/G3 được duyệt, cập nhật bản record/version cụ thể; không dùng chữ approved khi chưa có người duyệt thực.

## 7. Decision subset và yêu cầu chuyển bước

| Slice chọn | Cần chốt trước requirements/design tương ứng | Không được thêm thành dependency bắt buộc |
|---|---|---|
| M1 quickactual/manualpayment | R01scope; D01/D02report/R05/R07 minimal; R09 nếureminder | OCR/PDF/Gemini/meter/tariff coverage |
| M2 baseline/usage | R01scope; D02/R05/R07 mininvalidation | Actualrecord/document/OCR/approvedprice choobservations |
| M2 pricedestimate | D02/D03/D04 vàtariffsource/policyfixtures | FulladminUI hoặcAIchat trướccalculator |
| M3 upload/review | C02actualseam; R02/R03/R05/R06 vàminfilelifecycle | Measurement/history/Q&Aexpanded |
| M4 reconcile | Correctpairrefs/version/canonicalactual, D01/D02/comparability, D03choestimate | Ảnh bắtbuộc nếumanualactual đãconfirm |
| M5 dialogue/insight | Sourceđủquyền; R02/R03choexternal; R09chocadence | MọiM4feature hoặc runtime multiagent |
| Release từngslice | R04environment/owner/support/RPO-RTO; G4/G5evidence, go/no-go | Mọioptional budget/advancedforecast/digest phải xong |

R01–R09/D01–D04 giữ nghĩa tại [decision registerV2.2](../replanning/V2-REVIEW-COMPARISON.md). Chưa approved policy không cản lập tài liệu, nhưng chặn implementation phần phụ thuộc cho tới lúc được quyết.

## 8. Review và baseline checklist

- [ ] PO xác nhận selectedslice, nhu cầu vàpriority; không lấy đềxuấtAI làm userconsent.
- [ ] Domainowner chốt rule/unknown/date/price/payment trong scope và ký version.
- [ ] Architect/UX/QA review happy/edge/fallback/permission, đầy đủ testableAC.
- [ ] RTM links source/design/task/test rõ; phần future và current không lẫn.
- [ ] Các acceptance về performance/retention/security/accessibility đã có scope/measurement phùhợp.
- [ ] G2 record và người duyệt thực được ghi; chỉ sau đó G3design → implementation.

Checklist hiện **chưa được đánh dấu hoàn thành**. Tạo requirement register không có nghĩa nhiệm vụ đã hoàn thành RequirementsAnalysis hoặc hệ thống đã qua Testing. Không thay đổi năm V2.2 hoặc hai V2gốc trong nhiệm vụ lập SDLC này.
