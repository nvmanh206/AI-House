# Dashboard — bằng chứng kiểm thử 5 tầng

Ngày 2026-10-28. Phạm vi: tổng hợp tiền/tiêu thụ, thiếu dữ liệu khác 0, hóa đơn hủy, thông báo và ngày hiển thị, cập nhật dữ liệu sau lưu. Đây là nghiệm thu lát cắt dashboard, không chứng nhận toàn bộ dự án.

## Bổ sung cache và cookie — đợt tiếp theo cùng ngày

- Race được tái hiện bằng đúng exports prefetchEndpoints/invalidateCache với response trì hoãn: trước sửa chỉ có 1 request thay vì 2, vì response cũ lấp lại cache. Sau sửa generation guard, response cũ bị bỏ và cache mới vẫn tái sử dụng được.
- useData gắn snapshot với key/generation, ẩn dữ liệu cũ khi invalidation hoặc đổi key. Request lỗi của lần tải mới có snapshot rỗng đúng generation để có thể hiển thị lỗi thay vì kẹt loading. Nhánh lỗi này đã được rà soát code, chưa có test mounted-hook riêng.
- Setting REFRESH_COOKIE_NAME mặc định utility_refresh, không đổi phiên ứng dụng đang dùng; System runner đặt utility_system_refresh. Set/read/delete cookie đều dùng cùng setting.
- Test cookie API chạy PostgreSQL đã tái hiện lỗi tên cookie trước sửa. Sau sửa, đăng ký/refresh/logout không thay đổi cookie ứng dụng giả định; thiếu cookie System trả 401.
- Toàn bộ backend: **90 passed, 2 warnings**, 20.91 giây. Frontend: **12 passed**, gồm thêm test race; typecheck đạt.
- HTTP thật 8108: đặt cookie ứng dụng sentinel, login/refresh/logout System không ghi đè/xóa sentinel, System cookie được xóa đúng và refresh sau đó trả 401.
- HTTP thật và browser: hộ System verification có 63.000 đồng/35 kWh → chọn Cache isolation empty → dashboard chưa có dữ liệu/0 hóa đơn → chuyển về hộ gốc → đúng 63.000 đồng/35 kWh. Không refresh trang thủ công giữa các lần chuyển hộ.
- Database dùng riêng utility_system_7b7fdf4ad38d_test. Reviewer độc lập không có finding đáng kể; chạy test race riêng đạt. Không chứng minh mọi race hoặc mọi luồng UI của dự án đã được kiểm thử.

## Thay đổi

- Server bổ sung ELECTRICITY_COST và WATER_COST nullable, cộng tiền bằng Decimal và loại hóa đơn CANCELLED. Giữ API cost và các trường tiêu thụ hiện có để tương thích.
- Dashboard đọc tổng đã tính từ server; bỏ lấy hóa đơn đầu tiên, không ép thiếu dữ liệu thành 0, không tự gán kỳ hiện tại khi chưa có kỳ dữ liệu.
- Biểu đồ phân bổ nêu rõ khi thiếu tiền điện/nước; hai giá trị 0 thật được trình bày là 0. Bộ lọc tiêu thụ ghi Lượng điện/kWh và Lượng nước/m³, không gọi lượng dùng là tiền.
- Bỏ ba thông báo mẫu khi API rỗng, dùng nội dung và thời gian bản ghi thật. Bỏ ngày cố định, dùng thời gian Asia/Ho_Chi_Minh.
- useData đăng ký nhận thông báo invalidateCache để lịch sử và dashboard đang hiển thị tải lại sau lưu, thay vì chỉ xóa Map mà không chạy lại effect.

## 1. Giao diện

- 7 test SSR component đạt: gợi ý không bịa số liệu, nhãn gợi ý chung, thiếu nước khác 0, cả hai loại bằng 0, thông báo rỗng, không có ngày cố định và nhãn lượng dùng đúng đơn vị.
- Trình duyệt đăng nhập vào frontend thật tại 127.0.0.1:3108: dashboard rỗng hiển thị chưa có dữ liệu, chưa có kỳ; không có tiền nước giả bằng 0.
- Với hai chỉ số 0 kỳ 2026-09: dashboard hiển thị 0 ₫, 0 kWh, nước chưa có dữ liệu và đúng kỳ lịch sử.
- Qua UI nhập 10 kWh cho công tơ đầu tiên: request POST /readings trả 201; API sau đó từ chối bản ghi trùng bằng 409 và tìm lại đúng hóa đơn đã tạo.
- Kiểm tra System phát hiện lịch sử không tự cập nhật sau lưu. Sau sửa cache, nhập 5 kWh cho công tơ thứ ba qua UI: lịch sử hiện ngay hàng 5 kWh và chỉ số trước đổi sang 5, không reload.
- Mở dashboard bằng điều hướng nội bộ sau lưu: 35 kWh, 63.000 ₫, kỳ 2026-10, tiền nước chưa có dữ liệu. Chọn Lượng điện: tiêu đề và đơn vị biểu đồ chuyển sang kWh.
- Đã xem screenshot desktop 1280×720. Chưa kiểm tra viewport mobile toàn dashboard, screen reader hoặc tương phản tự động đầy đủ ở đợt này.

## 2. API

- TestClient chạy PostgreSQL cho hợp đồng nullable/zero, hóa đơn hủy, nhiều tài khoản và phép cộng 0.10 + 0.20 = 0.3.
- HTTP thật: health 200; statistics chưa đăng nhập 401; đăng ký/tạo hộ/tài khoản/công tơ 201; login 200; ghi chỉ số 201; ghi trùng 409.
- Thanh toán thủ công gọi lặp trả cùng payment ID; bill đổi PAID. Đây là ghi nhận thanh toán, không phải giao dịch ngân hàng.
- Tổng tiền và lượng dùng API được đối chiếu trực tiếp SQL, không chỉ kiểm tra status code.

## 3. Server

- Toàn bộ backend trên PostgreSQL riêng: **89 passed, 2 warnings**, 18.36 giây. Bao gồm 3 ca API/server mới tại tests/test_dashboard_statistics.py; không cộng nhầm thành 89 test mới.
- Ca nhiều tài khoản kiểm tra dữ liệu đã lưu: 2 hóa đơn, 90 kWh; sửa số tiền fixture thành 0.10 và 0.20 trong database test để chứng minh phép cộng Decimal và response 0.3.
- Server HTTP thật 8108 dùng database riêng và schema Alembic. Query SQL cuối: tổng tiền 63000.00, lượng dùng 35.000, trùng API.
- Database ứng dụng utility_app vẫn có 25 hóa đơn sau thử nghiệm. Không tạo fixture trong database ứng dụng.
- Hai warning còn từ Starlette/httpx và AnyIO, không bị bỏ qua khi báo kết quả.

## 4. System

- Stack thật: Next.js 16.3.4 tại 3108 → FastAPI/Uvicorn 8108 → PostgreSQL 16.15.
- Database: utility_system_7b7fdf4ad38d_test, tạo riêng; cấu hình biểu giá và tiers lấy từ PostgreSQL ứng dụng, không lấy số tiền hardcode từ frontend.
- Hành trình đã chạy: chuẩn bị tài khoản/hộ/công tơ qua HTTP → đăng nhập UI → dashboard rỗng → chỉ số 0 → nhập chỉ số UI → tạo hóa đơn và tổng hợp nhiều tài khoản → thanh toán lặp → đối chiếu PostgreSQL → dashboard.
- Hai tài khoản đầu có 10 và 20 kWh: SQL/API tổng 54.000 đồng. Sau test cache thêm công tơ thứ ba 5 kWh qua UI: SQL/API/dashboard đều 63.000 đồng, 35 kWh. Đây là kết quả tính từ biểu giá được lưu, không phải giá trị mặc định của sản phẩm.
- Các thao tác browser là kiểm thử có điều khiển, chưa phải bộ browser test tự chạy trong CI. Dữ liệu test và database được giữ lại để đối chiếu, không tự xóa.

## 5. Transform

- 4 ca riêng tại frontend/tests/dashboard-transform.test.cjs: rỗng, zero khác null, kỳ mới nhất và tổng server, dữ liệu số thiếu/sai.
- API → view model → UI giữ nguyên trường thiếu thành null; không tự tạo tiền nước hoặc kỳ lịch hiện tại. Server Decimal → JSON số → UI đã được đối chiếu với PostgreSQL trong System test.
- Kiểm thử hóa đơn CANCELLED: không cộng chi phí, vẫn giữ lượng dùng đã ghi. Thời gian hiển thị lấy đồng hồ thực và timezone sản phẩm.
- OCR/AI, chuyển đổi đơn vị khác và provider mạng không nằm trong lát cắt này; chưa được xác nhận chỉ vì dashboard đạt.

## Lệnh tái kiểm tra

Tại website:

```powershell
.\backend\.venv\Scripts\python.exe scripts/test_postgres.py
.\backend\.venv\Scripts\python.exe scripts/system_test.py prepare
.\backend\.venv\Scripts\python.exe scripts/system_test.py serve
```

Terminal khác tại website/frontend:

```powershell
node --test tests/dashboard-truth.test.cjs tests/dashboard-transform.test.cjs
node node_modules/typescript/bin/tsc --noEmit --incremental false
$env:NEXT_PUBLIC_API_BASE_URL='http://127.0.0.1:8108/api'
$env:NEXT_DIST_DIR='.next/system-test'
node node_modules/next/dist/bin/next dev --hostname 127.0.0.1 --port 3108
```

Sau khi server sẵn sàng, terminal website chạy exercise, đăng nhập browser bằng fixture trong .local/system-test-state.json, kiểm tra rỗng, chạy zero, kiểm tra 0, rồi chạy values và đối chiếu UI. Nếu nhập qua UI trước values, runner kiểm tra lại bản ghi trùng thay vì ghi đè. Mỗi chuỗi mới bắt đầu từ prepare để tạo database riêng; không chạy lại exercise trên tài khoản đã đăng ký.

System runner hiện đặt REFRESH_COOKIE_NAME=utility_system_refresh, tách khỏi utility_refresh mặc định của ứng dụng. Không tự bỏ cấu hình này khi chạy hai môi trường cùng hostname. Tách database vẫn bắt buộc; cookie riêng không thay thế phân quyền hay database test riêng.

## Rà soát và việc còn lại

- Reviewer độc lập không phát hiện lỗi đáng kể trong thay đổi tổng hợp/null/UI của lát cắt; chạy riêng 11 test frontend đạt. Typecheck không cache đạt.
- Race request cũ và cookie System đã được xử lý ở phần bổ sung; vẫn cần mở rộng kiểm thử mounted-hook, lỗi mạng, nhiều tab và mọi kịch bản tải đồng thời.
- Cần mở rộng browser automation, kiểm tra mobile, OCR/AI và lỗi hạ tầng. Chuyển hộ hai chiều đã được kiểm chứng trong phạm vi System test ở trên.
- Trang đăng nhập còn các claim marketing chưa có bằng chứng (20%, 10.000 gia đình, ISO). Đã ghi nhận để xử lý riêng; không dùng chúng làm chứng cứ năng lực hệ thống.
