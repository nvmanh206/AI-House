# Chuẩn kiểm thử 5 tầng — Nhà Mình

Ngày ghi nhận: 2026-10-28. Người dùng yêu cầu kiểm thử giao diện, API, server, system và transform. Dù câu mở đầu ghi 3 tầng, danh sách cụ thể có 5 tầng; áp dụng đủ 5 tầng.

## 1. Giao diện — UI

Kiểm tra điều người dùng thấy và thao tác được:
- Hiển thị số liệu, đơn vị, kỳ, nguồn dữ liệu và nhãn ước tính đúng.
- Phân biệt đang tải, lỗi, chưa có dữ liệu và giá trị thực bằng 0.
- Form, validation, nút gửi, điều hướng, gửi lặp và thao tác bàn phím.
- Bố cục trên desktop/mobile, nội dung dài và quyền truy cập khác nhau.
- Kiểm thử component và kiểm tra trình duyệt. Render HTML tĩnh hoặc typecheck không thay thế kiểm thử tương tác trên trình duyệt.

## 2. API — hợp đồng và quyền truy cập

- Request/response schema, kiểu dữ liệu, trường bắt buộc và mã lỗi.
- Xác thực, phiên hết hạn, quyền thành viên/admin và phân tách dữ liệu giữa các hộ.
- Dữ liệu không hợp lệ, tài nguyên không tồn tại, thao tác trùng và xung đột.
- Kiểm tra giá trị response và thay đổi dữ liệu, không chỉ HTTP 200.
- TestClient kiểm tra hợp đồng API trong tiến trình; kiểm tra HTTP qua server đang chạy được ghi riêng, không đánh đồng hai loại.

## 3. Server — nghiệp vụ, lưu trữ và vận hành backend

- Tính tiền Decimal, bậc giá, chọn phiên bản/phạm vi, làm tròn, snapshot.
- Ràng buộc dữ liệu, transaction/rollback, tính idempotent, cạnh tranh ghi dữ liệu.
- Job nhắc việc, lỗi provider AI, timeout, cấu hình thiếu và xử lý lỗi.
- Khởi động server, health/readiness, kết nối database, migration trên database thử nghiệm và log không lộ dữ liệu nhạy cảm.
- SQLite là bằng chứng cho logic/transaction trong môi trường test; chưa chứng minh hành vi PostgreSQL, khóa đồng thời hoặc cấu hình production.

## 4. System — toàn bộ hệ thống phối hợp

Kiểm thử xuyên suốt trên frontend + API + backend + database chạy thật trong môi trường riêng:
- Đăng nhập → chọn hộ → nhập chỉ số → tạo ước tính → xem hóa đơn → ghi nhận thanh toán → thống kê/AI phản ánh đúng dữ liệu.
- Chuyển hộ/đăng xuất không thấy dữ liệu từ phiên hoặc hộ trước.
- Khi API lỗi, biểu giá thiếu/chồng lấn hoặc AI không sẵn sàng: giao diện báo đúng, không ghi dở, không tự bịa kết quả.
- Refresh, cache/invalidation và nhiều tab/phiên khi thuộc phạm vi thay đổi.
- Kiểm tra vận hành bằng staging/local stack; không chạy thử ghi dữ liệu trên production.
- File có tên `test_system.py` không tự chứng minh đã kiểm thử tầng System. Nếu dùng TestClient + SQLite thì ghi đúng là kiểm thử API/server tích hợp.

## 5. Transform — toàn bộ luồng biến đổi dữ liệu

Người dùng xác nhận bao phủ toàn bộ luồng chuyển đổi dữ liệu:
- API DTO → dữ liệu dashboard/chart/view model; gộp nhiều tài khoản đúng kỳ và loại hóa đơn hủy.
- Null/missing/empty khác 0; không tạo ngân sách, chi phí hoặc dự báo mặc định thiếu căn cứ.
- Chuỗi số/Decimal → hiển thị VND/kWh/m³; độ chính xác và làm tròn theo quy tắc nghiệp vụ.
- Ngày, kỳ, múi giờ; không lệch kỳ khi chuyển định dạng.
- Chuẩn hóa tiếng Việt có dấu/không dấu; OCR/đầu vào AI → dữ liệu có cấu trúc, giữ nguồn và trạng thái chưa xác nhận.
- Dùng dữ liệu đầu vào và kết quả mong đợi cụ thể. Có ca rỗng, số 0, nhiều tài khoản, biên ngày và dữ liệu sai; không chỉ kiểm tra cấu trúc giống implementation.

Bao phủ cả đầu vào, API, lưu trữ, xử lý nghiệp vụ, AI/OCR và hiển thị; không giới hạn ở một hàm mapping hoặc một mô hình AI.

## Dữ liệu thật, PostgreSQL và pgAdmin — yêu cầu đã xác nhận

- Chức năng ứng dụng phải lấy dữ liệu từ PostgreSQL và các nguồn thực được cấu hình; không dùng giá trị hardcode để đóng giả dữ liệu hộ, xu hướng, dự báo, mức tiết kiệm hay số tiền.
- Không có dữ liệu thì hiển thị thiếu dữ liệu; không tự chèn demo/seed vào database sử dụng thực tế.
- PostgreSQL là database chính và môi trường kiểm thử tích hợp/Server/System dùng PostgreSQL riêng. Kết quả SQLite trước đây chỉ là bằng chứng lịch sử cho phạm vi đã chạy, không đủ nghiệm thu PostgreSQL.
- pgAdmin là giao diện quản trị PostgreSQL: xem bảng, truy vấn và đối chiếu bản ghi trước/sau thao tác. pgAdmin không thay thế backend, phân quyền ứng dụng hoặc công cụ kiểm thử.
- Phân biệt dữ liệu thực trong ứng dụng với fixture của kiểm thử: các ca rỗng, biên và lỗi cần dữ liệu kiểm soát được trong database test riêng, không ghi thử vào database đang sử dụng. Fixture không được xuất hiện như dữ liệu thật trên sản phẩm.
- Kiểm chứng bằng dữ liệu thật phải nêu rõ nguồn, database/môi trường, kỳ và kết quả đối chiếu. Không đưa dữ liệu cá nhân hoặc chuỗi kết nối có mật khẩu vào nhật ký.
- Không xóa database hiện tại hoặc tự gỡ bản ghi cũ chưa xác định là demo. Kiểm kê nguồn gốc trước khi xử lý dữ liệu tồn tại.

## Quy trình cho mỗi lát cắt

1. Ghi tiêu chí nghiệm thu và xác định tác động tới cả 5 tầng trước khi sửa.
2. Với lỗi: tạo kiểm thử tái hiện, chạy thấy lỗi đúng nguyên nhân, sau đó sửa tối thiểu và chạy lại.
3. Chạy kiểm thử các tầng bị tác động; chạy hồi quy liên quan.
4. Tầng không bị tác động phải ghi rõ lý do, không tự đánh dấu đạt. Chưa có môi trường hoặc chưa chạy thì ghi **chưa kiểm chứng**.
5. Trước khi nghiệm thu đầy đủ một chức năng/phiên bản, phải có bằng chứng cho cả 5 tầng liên quan, gồm System chạy stack thật. Không kết luận hoàn tất chỉ từ typecheck hoặc một bộ unit test.
6. Lưu vào `IMPLEMENTATION_PROGRESS.md`: phạm vi/commit hoặc trạng thái checkout, môi trường, dữ liệu test, ca kiểm tra, lệnh, kết quả thực tế, hạn chế và bước tiếp theo.

Không gộp số lượng test khác tầng thành tuyên bố “toàn hệ thống đạt”. Một ca có thể đi qua nhiều lớp nhưng cần nêu rõ những gì nó thực sự kiểm chứng.

## Baseline hiện có — phân loại bằng chứng, chưa chạy lại ở lượt này

- UI: 2 test SSR cho panel gợi ý; đã xem component trong browser với CSS thật. Chưa có bộ tương tác tự động cho dashboard sau đăng nhập.
- API: nhiều test dùng FastAPI TestClient, gồm quyền truy cập, ghi chỉ số/hóa đơn và AI không dấu. Chưa chứng minh hợp đồng qua HTTP server thật cho mọi luồng.
- Server: lần chạy trước 86 test backend đạt, gồm cả unit và integration; không có nghĩa 86 test đều thuộc riêng tầng server. Chưa có chứng cứ staging/PostgreSQL/concurrency đầy đủ.
- System: chưa có bằng chứng E2E frontend → database thật cho lát cắt mới. Trạng thái **chưa kiểm chứng**.
- Transform: đã có ca chuẩn hóa AI không dấu và tính số tiền trong bộ hiện tại; còn thiếu bộ biến đổi dashboard cho null/0, nhiều tài khoản và hóa đơn hủy.

## Ưu tiên triển khai tiếp

Cập nhật triển khai 2026-10-28: đã chuyển nguồn SQLite hiện có sang PostgreSQL utility_app, đối chiếu nội dung đủ 15 bảng và giữ nguồn/backup. Runner `scripts/test_postgres.py` chạy trên utility_app_test: **86 passed, 2 warnings**. pgAdmin HTTP đăng nhập/kết nối database đạt. Đây là bằng chứng PostgreSQL mới bổ sung; UI/System E2E toàn bộ sản phẩm vẫn chưa được xác nhận. Xem `docs/POSTGRESQL-PGADMIN.md` và nhật ký triển khai.

1. Viết kiểm thử Transform cho tổng hợp dashboard: rỗng, thiếu một tiện ích, 0 thật, nhiều tài khoản và hóa đơn hủy.
2. Kiểm thử UI dùng dữ liệu đó, gồm nhãn kỳ/nguồn và trạng thái thiếu dữ liệu.
3. Bổ sung/đối chiếu API và server để bảo đảm response cùng quy tắc, không chỉ sửa phía hiển thị.
4. Dựng môi trường System riêng với dữ liệu tổng hợp, xác minh hành trình sau đăng nhập và lưu bằng chứng.
