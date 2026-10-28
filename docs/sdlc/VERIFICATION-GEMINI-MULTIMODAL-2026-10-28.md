# Gemini multimodal — triển khai và kiểm chứng 2026-10-28

## Hành vi đã triển khai

- Chat production đi qua Gemini có schema, không ghép lời trả lời theo từ khóa và không fallback câu trả lời giả khi provider lỗi. Nhánh deterministic cũ chỉ còn cho môi trường test tường minh.
- Ảnh JPEG/PNG/WebP: giải mã Base64, giới hạn 10MB trước/sau chuẩn hóa, decoder Pillow kiểm tra nội dung, từ chối ảnh động/hỏng và ảnh trên25triệu pixel. Đọc EXIF orientation, tái mã hóa ảnh. Không ghi ảnh vào database.
- Lần gọi1 chỉ nhận ảnh/văn bản OCR và yêu cầu; không nhận dữ liệu PostgreSQL. Schema Extraction phân biệt loại tài liệu, nhiệm vụ, trường thiếu và trường không rõ. Decimal ở dạng chuỗi chuẩn; null khác0; ngày/kỳ có kiểm tra.
- Backend đối chiếu trong hộ đã xác thực, đúng tài khoản/công tơ/kỳ. Không dùng baseline hoặc kỳ mới nhất khác kỳ. Kiểm tra đơn vị, hiệu chỉ số/sản lượng. Tiền đối chiếu final_amount và source của đúng hóa đơn; không tự ghi chỉ số/hóa đơn/thanh toán.
- Lần gọi2 nhận Extraction + kết quả backend + tổng quan mới nhất + lịch sử, trả Reply có requested_task hiện tại, status, message và evidence_refs. Schema đúng không đồng nghĩa nội dung chắc chắn đúng; backend từ chối tham chiếu không hợp lệ và kết luận đối chiếu không có căn cứ.
- Mỗi lượt gửi6kỳ gần nhất theo kỳ dữ liệu hiện có; tổng nợ tính toàn bộ, chi tiết tối đa50 khoản và unpaid_has_more. Không gửi hồ sơ user, email, thành viên, token hoặc mật khẩu từ database.
- Conversation_id do server phát hành, lưu JSON trong AIAnalysis với user/hộ; tối đa20tin nhắn và snapshot trích xuất theo lượt, có ảnh gần nhất làm ngữ cảnh đang hoạt động. Câu hỏi về nhiều ảnh cũ có thể cần làm rõ; không có bộ chọn nhiều ảnh.
- Frontend ưu tiên message, chi tiết dữ liệu đọc ảnh mặc định đóng. Chat localStorage tách user/hộ, tối đa20tin và không lưu ảnh Base64. Không dùng lịch sử do client gửi làm nguồn sự thật. Bỏ bộ đếm tiến trình giả và số tiền/tip tiết kiệm giả ở sidebar trợ lý.

## Hợp đồng API

POST /api/ai/chat giữ message, image_base64 và raw_ocr_text; thêm conversation_id UUID tùy chọn. Không gửi conversation_id khi bắt đầu hội thoại mới.

Response giữ message, intent, sources, metadata; thêm status. metadata.conversation_id dùng ở lượt tiếp theo. metadata.result chứa requested_task, status, message, evidence_refs, extracted_data, extraction và verification. Backend verification có reading/amount: MATCH, MISMATCH hoặc UNKNOWN; consistency chứa mã lỗi nghiệp vụ. requested_task của ảnh không được dùng thay nhiệm vụ câu hỏi tiếp nối.

OUT_OF_SCOPE/INSUFFICIENT_DATA/NEEDS_CLARIFICATION là kết quả HTTP200. Provider lỗi/timeout/quota hoặc JSON sai trả lỗi dịch vụ, không phải lời tư vấn AI. Không log body trả lỗi từ Google hoặc ảnh/private context.

## Bằng chứng5tầng

- Server/API/Transform: bộ backend PostgreSQL bản cuối **120passed, 2warnings**, 22.41giây, bao gồm snapshot Extraction theo lượt (đã chứng kiến red trước sửa). Hai warnings hiện có của Starlette/httpx/AnyIO.
- TDD các ca chính: module mới chưa tồn tại → triển khai; follow-up dùng sai nhiệm vụ cũ (2ca fail) → sửa; giải thích ảnh mâu thuẫn bị chặn (fail) → sửa; internal evidence bị hiển thị giả thành nhãn chỉ số trên UI (fail) → sửa.
- Frontend **16passed + tsc --noEmit --incremental false**, gồm kiểm thử SSR chi tiết mặc định đóng, giữ số0, không gán nhãn nguồn giả và chat persistence không ảnh.
- System thật: scripts/multimodal_system.py exercise đã gọi Gemini thật, ảnh test tự tạo theo số tiền đọc từ hóa đơn PostgreSQL test; MATCH150kWh, câu hỏi tiếp nối không cần gửi lại ảnh, OUT_OF_SCOPE cho yêu cầu viết trò chơi; counts meter_readings/bills/payments không đổi sau chat.
- scripts/multimodal_variants.py dùng Gemini thật: cropped=INSUFFICIENT_DATA; blurred=INSUFFICIENT_DATA; non-invoice được nhận OTHER và trả lời câu hỏi nhận diện (ANSWERED hợp lệ); foreign-account=NEEDS_CLARIFICATION; water=INSUFFICIENT_DATA, unitm³. Không trường hợp nào kết luận MATCH; counts nghiệp vụ không đổi.
- UI thật tại frontend3110 → API8110 → Gemini → PostgreSQL System: đăng nhập, nút đính kèm/filechooser chọn ảnh, gửi câu hỏi, hiển thị message tự nhiên, mở chi tiết đúng100/150/50kWh/90000VND. Screenshot: evidence/gemini-multimodal-details-2026-10-28.png. Không dùng networkmock để tạo bằng chứng này.
- Bản cuối đã chạy lại System exercise thành công sau bổ sung snapshot theo lượt. UI hỏi tiếp “Ảnh đó ghi bao nhiêu tiền?” không gửi lại ảnh: trả90.000VND, phân biệt ước tính hệ thống; screenshot evidence/gemini-multimodal-conversation-2026-10-28.png. Đã đăng xuất và đóng riêng tab test; giữ nguyên pgAdmin và tab3108 của user. Database ứng dụng vẫn25hóa đơn; không ghi test vào utility_app.
- Reviewer độc lập phát hiện lỗi nhiệm vụ follow-up, đã sửa và tái hiện red/green; lượt rà soát lại không có finding cần sửa. Reviewer không tự chạy Gemini thật.

## Cấu hình model và cách chạy lại

Key có sẵn được giữ nguyên, không in/log. API từ chối gemini-2.5-flash với404; gemini-3.8-flash/3.5-flash không ổn định (503/timeout). gemini-3.1-flash-lite được API liệt kê và đã qua nghiệm thu thật; cập nhật backend/.env, .env.example, Settings mặc định sang model này. Không có vòng fallback âm thầm sang model khác. Cần khởi động lại backend đang chạy để đọc cấu hình/code mới.

Backend dependency mới: Pillow>=11,<13; đã cài12.3.0 trong backend/.venv. Không cần migration database.

Từ thư mục website:

```powershell
.\backend\.venv\Scripts\python.exe scripts/test_postgres.py
.\backend\.venv\Scripts\python.exe scripts/multimodal_system.py serve
# Terminal khác, tạo fixture/user mới chỉ trong DB System:
.\backend\.venv\Scripts\python.exe scripts/multimodal_system.py exercise
.\backend\.venv\Scripts\python.exe scripts/multimodal_variants.py
```

Frontend test (cwd website/frontend):

```powershell
node --test tests/*.test.cjs
node node_modules/typescript/bin/tsc --noEmit --incremental false
$env:NEXT_PUBLIC_API_BASE_URL='http://127.0.0.1:8110/api'
$env:NEXT_DIST_DIR='.next/multimodal-test'
node node_modules/next/dist/bin/next dev --hostname 127.0.0.1 --port 3110
```

System phải có .local/system-test-state.json từ script system_test.py prepare. Fixture đăng nhập/ảnh/kết quả ở .local/multimodal-browser-state.json, multimodal-test-invoice.png, multimodal-live-result.json, multimodal-live-variants.json; đều ignored. Không dùng file này để kết nối ứng dụng production.

## Giới hạn

Đã thử trên fixture tự tạo được phép sử dụng, chưa phải bộ benchmark hóa đơn nhà cung cấp thực tế diện rộng. Chưa có CI tự động hóa browser upload, kiểm tra mobile/screenreader đầy đủ hoặc cam kết tuyệt đối về việc AI không suy luận sai. JSON, phân quyền và đối chiếu backend có kiểm tra; user vẫn cần xem lại ảnh khi dữ liệu không rõ. Không có tự lưu dữ liệu nghiệp vụ, PDF, nhiều ảnh trong một lượt, streaming hoặc thao tác thanh toán.
