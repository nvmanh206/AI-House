# ĐẶC TẢ CHI TIẾT 25 USE CASES NGHỆP VỤ HỆ THỐNG
## Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia Đình tích hợp AI (Nhà Mình)

---

## 1. Phân hệ 1: Quản trị Tài khoản & Xác thực (`auth`)

### UC-REGISTER: Đăng ký tài khoản
- **Mã Use Case:** `UC-REGISTER`
- **Tên Nghiệp vụ:** Đăng ký tài khoản
- **Phân hệ:** `auth`
- **Mục tiêu:** Cho phép người dùng mới tạo tài khoản cá nhân trên hệ thống.
- **Actor chính:** `Guest` (Khách truy cập)
- **Actor hỗ trợ:** `FastAPI Auth Service` (Hệ thống xác thực)
- **Trigger:** Người dùng mở giao diện Đăng ký (`/register`) và bấm nút "Đăng ký".
- **Tiền điều kiện:** Người dùng chưa xác thực phiên làm việc (chưa đăng nhập).
- **Hậu điều kiện thành công:** Bản ghi người dùng mới được tạo trong bảng `users` với mật khẩu mã hóa Argon2id và vai trò mặc định `USER`.
- **Đảm bảo tối thiểu khi thất bại:** Không có dữ liệu rác lưu vào CSDL, hiển thị thông báo lỗi chính xác trên form.
- **Luồng chính (Main Flow):**
  1. Người dùng mở trang `/register` và nhập Họ tên, Email, Mật khẩu và Xác nhận mật khẩu.
  2. Người dùng nhấn nút "Đăng ký".
  3. Client kiểm tra cú pháp email và độ mạnh mật khẩu (≥ 8 ký tự, gồm chữ và số).
  4. Client gửi yêu cầu HTTP `POST /api/auth/register` kèm JSON payload.
  5. Backend verify email chưa tồn tại trong CSDL `users`.
  6. Backend mã hóa mật khẩu bằng thuật toán Argon2id (`hasher.hash(password)`).
  7. Backend chèn bản ghi mới vào CSDL `users` với `role='USER'`, `is_active=True`.
  8. Backend trả về HTTP status `200 OK` kèm thông tin tài khoản công khai.
  9. Frontend hiển thị thông báo đăng ký thành công và chuyển hướng sang `/login`.
- **Luồng rẽ nhánh (Alternative Flow):**
  - **3a. Dữ liệu không hợp lệ:** Nếu email sai cú pháp hoặc mật khẩu yếu, form hiển thị cảnh báo đỏ ngay tại trường tương ứng.
  - **5a. Email đã được sử dụng:** Tại bước 5, nếu email đã có trong `users`, backend trả về HTTP `400 Bad Request` với message `"Email đã được đăng ký"`. Frontend đề xuất người dùng Đăng nhập hoặc Khôi phục mật khẩu.
- **Luồng ngoại lệ (Exception Flow):**
  - **E1. Lỗi CSDL / Kết nối máy chủ:** Trả về HTTP `500 Internal Server Error`, hệ thống rollback transaction và thông báo `"Không thể kết nối máy chủ, vui lòng thử lại sau"`.
- **Business Rules:** Email phải là duy nhất trên toàn hệ thống. Mật khẩu lưu trữ bắt buộc phải băm Argon2id.
- **Quan hệ UML:** Độc lập. Không include hay extend UC-LOGIN.
- **Vết yêu cầu:** `FR01`, DOCX Sec 3.2.3, `POST /api/auth/register`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/auth/register.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/auth/register.puml)

---

### UC-LOGIN: Đăng nhập hệ thống
- **Mã Use Case:** `UC-LOGIN`
- **Tên Nghiệp vụ:** Đăng nhập hệ thống
- **Phân hệ:** `auth`
- **Mục tiêu:** Xác thực tài khoản người dùng và cấp cặp Signed JWT Access Token cùng Refresh Token.
- **Actor chính:** `Guest`, `User`, `Admin`
- **Actor hỗ trợ:** `FastAPI Auth Service`
- **Trigger:** Người dùng nhập thông tin tại trang `/login` và bấm nút "Đăng nhập".
- **Tiền điều kiện:** Tài khoản đã được đăng ký và ở trạng thái hoạt động (`is_active=True`).
- **Hậu điều kiện thành công:** Phiên làm việc được tạo trong `auth_sessions`, client nhận JWT Access Token (15 phút) và Refresh Token Cookie (7 ngày).
- **Đảm bảo tối thiểu khi thất bại:** Xóa sạch token tạm trên client, ghi log truy cập thất bại.
- **Luồng chính (Main Flow):**
  1. Người dùng mở trang `/login`, nhập Email và Mật khẩu.
  2. Người dùng nhấn nút "Đăng nhập".
  3. Client gửi HTTP `POST /api/auth/login` với dữ liệu form.
  4. Backend truy vấn `users` theo email.
  5. Backend đối soát hash mật khẩu bằng `hasher.verify(user.password_hash, password)`.
  6. Backend kiểm tra `user.is_active == True`.
  7. Backend khởi tạo bản ghi `auth_sessions` và ký Signed JWT Access Token (hạn 15 phút, bao gồm `sub: user.id`, `sid: session.id`).
  8. Backend thiết lập cookie an toàn HttpOnly chứa Refresh Token và trả về Access Token trong HTTP `200 OK` body.
  9. Client lưu Access Token vào bộ nhớ tạm và chuyển hướng đến `/dashboard`.
- **Luồng rẽ nhánh (Alternative Flow):**
  - **7a. Hết hạn Access Token:** Khi Access Token hết hạn trong lúc đang thao tác, client tự động gọi `UC-REFRESH-TOKEN` để lấy Access Token mới mà không bắt buộc đăng nhập lại.
- **Luồng ngoại lệ (Exception Flow):**
  - **4a/5a. Sai thông tin:** Nếu không tìm thấy email hoặc mật khẩu không khớp, backend trả về HTTP `401 Unauthorized` với message `"Email hoặc mật khẩu không chính xác"`.
  - **6a. Tài khoản bị khóa:** Nếu `is_active == False`, backend trả về HTTP `403 Forbidden` với message `"Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Admin"`.
- **Business Rules:** Access Token hết hạn sau 15 phút. Refresh Token hết hạn sau 7 ngày.
- **Quan hệ UML:** Độc lập với UC-REGISTER.
- **Vết yêu cầu:** `FR02`, DOCX Sec 3.2.3, `POST /api/auth/login`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/auth/login.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/auth/login.puml)

---

### UC-LOGOUT: Đăng xuất hệ thống
- **Mã Use Case:** `UC-LOGOUT`
- **Tên Nghiệp vụ:** Đăng xuất hệ thống
- **Phân hệ:** `auth`
- **Mục tiêu:** Hủy phiên làm việc hiện tại và thu hồi Refresh Token trên máy chủ.
- **Actor chính:** `User`, `Admin`
- **Trigger:** Người dùng nhấn nút "Đăng xuất" trên menu người dùng.
- **Tiền điều kiện:** Người dùng đang trong phiên làm việc hợp lệ.
- **Hậu điều kiện thành công:** `auth_sessions.revoked = True`, Refresh Token Cookie bị xóa, client quay lại `/login`.
- **Luồng chính (Main Flow):**
  1. Người dùng bấm "Đăng xuất".
  2. Client gửi HTTP `POST /api/auth/logout` kèm Header Authorization Bearer.
  3. Backend đánh dấu `revoked = True` cho session hiện tại trong CSDL `auth_sessions`.
  4. Backend xóa cookie Refresh Token và trả về HTTP `200 OK`.
  5. Client xóa Access Token trong bộ nhớ và chuyển hướng người dùng về trang `/login`.
- **Vết yêu cầu:** `FR02`, `POST /api/auth/logout`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/auth/logout.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/auth/logout.puml)

---

### UC-USER-PROFILE: Cập nhật hồ sơ cá nhân
- **Mã Use Case:** `UC-USER-PROFILE`
- **Tên Nghiệp vụ:** Cập nhật hồ sơ cá nhân
- **Phân hệ:** `auth`
- **Mục tiêu:** Cập nhật thông tin cá nhân (họ tên) hoặc thay đổi mật khẩu tài khoản.
- **Actor chính:** `User`, `Admin`
- **Trigger:** Người dùng truy cập trang Hồ sơ cá nhân (`/profile`) và lưu thay đổi.
- **Tiền điều kiện:** Đã đăng nhập hệ thống.
- **Hậu điều kiện thành công:** Thông tin mới được cập nhật vào bảng `users`.
- **Luồng chính (Main Flow):**
  1. Người dùng nhập thông tin họ tên mới hoặc mật khẩu hiện tại + mật khẩu mới.
  2. Client gửi HTTP `PATCH /api/auth/me` (đổi thông tin) hoặc `POST /api/auth/password` (đổi mật khẩu).
  3. Backend xác thực mật khẩu cũ nếu thực hiện đổi mật khẩu.
  4. Backend cập nhật dữ liệu trong `users` và trả về HTTP `200 OK`.
- **Vết yêu cầu:** `FR01`, `FR02`, `PATCH /api/auth/me`, `POST /api/auth/password`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/auth/user_profile.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/auth/user_profile.puml)

---

## 2. Phân hệ 2: Khởi tạo & Quản lý Hộ gia đình (`household`)

### UC-HOUSEHOLD-SETUP: Khởi tạo hộ gia đình (Onboarding)
- **Mã Use Case:** `UC-HOUSEHOLD-SETUP`
- **Tên Nghiệp vụ:** Khởi tạo hộ gia đình (Onboarding)
- **Phân hệ:** `household`
- **Mục tiêu:** Hướng dẫn người dùng khởi tạo hộ gia đình mới, địa chỉ và tự động tạo 2 công tơ điện/nước ban đầu.
- **Actor chính:** `Owner` (Chủ hộ)
- **Trigger:** Người dùng mới đăng nhập chưa có hộ gia đình hoặc chọn "Tạo hộ gia đình mới".
- **Tiền điều kiện:** Người dùng đã xác thực tài khoản.
- **Hậu điều kiện thành công:** Bản ghi `households` được tạo mới, người tạo được gán vai trò `OWNER` trong `household_members`, 2 công tơ điện và nước được khởi tạo trong `meters`.
- **Luồng chính (Main Flow):**
  1. Người dùng nhập Tên hộ (ví dụ: "Gia đình Nguyễn Văn A"), Địa chỉ, Tỉnh/Thành phố.
  2. Bấm "Khởi tạo Hộ gia đình".
  3. Client gửi HTTP `POST /api/households` với JSON payload.
  4. Backend mở DB Transaction:
     - Tạo bản ghi trong `households`.
     - Tạo bản ghi `household_members` với `role='OWNER'`.
     - Tự động tạo 2 công tơ mặc định (Điện kWh và Nước m³) liên kết với hộ trong `meters`.
  5. Backend cập nhật `session.household_id` và trả về HTTP `200 OK`.
  6. Frontend chuyển hướng người dùng đến Trang chủ Dashboard hộ (`/dashboard`).
- **Vết yêu cầu:** `FR03`, `FR05`, DOCX Sec 3.2.3 (UC-02), `POST /api/households`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/household/household_setup.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/household/household_setup.puml)

---

### UC-SELECT-HOUSEHOLD: Chọn hộ gia đình hoạt động
- **Mã Use Case:** `UC-SELECT-HOUSEHOLD`
- **Tên Nghiệp vụ:** Chọn hộ gia đình hoạt động
- **Phân hệ:** `household`
- **Mục tiêu:** Chuyển đổi ngữ cảnh làm việc hiện tại sang hộ gia đình khác nếu người dùng thuộc nhiều hộ.
- **Actor chính:** `User`
- **Trigger:** Người dùng chọn hộ gia đình từ menu thả xuống trên Header.
- **Luồng chính (Main Flow):**
  1. Người dùng chọn một Hộ gia đình từ danh sách.
  2. Client gửi HTTP `POST /api/households/{id}/select`.
  3. Backend kiểm tra người dùng có quyền thành viên trong hộ đó.
  4. Backend cập nhật `session.household_id` và cấp Access Token cập nhật context.
  5. Frontend tải lại dữ liệu Dashboard theo hộ gia đình vừa chọn.
- **Vết yêu cầu:** `FR03`, `POST /api/households/{id}/select`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/household/select_household.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/household/select_household.puml)

---

### UC-MEMBER-MGMT: Quản lý thành viên hộ
- **Mã Use Case:** `UC-MEMBER-MGMT`
- **Tên Nghiệp vụ:** Quản lý thành viên hộ
- **Phân hệ:** `household`
- **Mục tiêu:** Xem danh sách thành viên, thêm thành viên trực tiếp và xóa thành viên khỏi hộ.
- **Actor chính:** `Owner`, `Member`
- **Luồng chính (Main Flow):**
  1. Chủ hộ xem danh sách thành viên hộ gia đình (`GET /api/members`).
  2. Chủ hộ nhập email thành viên muốn thêm trực tiếp (`POST /api/members`).
  3. Backend kiểm tra người dùng tồn tại và chèn bản ghi vào `household_members` với `role='MEMBER'`.
  4. Nếu cần xóa thành viên, Chủ hộ bấm xóa (`DELETE /api/members/{id}`).
- **Vết yêu cầu:** `FR04`, DOCX Sec 3.2.3 (UC-03), `GET/POST/DELETE /api/members`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/household/member_management.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/household/member_management.puml)

---

### UC-MEMBER-INVITE: Mời thành viên vào hộ
- **Mã Use Case:** `UC-MEMBER-INVITE`
- **Tên Nghiệp vụ:** Mời thành viên vào hộ
- **Phân hệ:** `household`
- **Mục tiêu:** Gửi thư mời qua email chứa Token tham gia hộ gia đình (thời hạn 48h).
- **Actor chính:** `Owner`
- **Trạng thái:** As-Designed SRS.
- **Luồng chính (Main Flow):**
  1. Chủ hộ nhập email người thân và bấm "Gửi lời mời".
  2. Hệ thống tạo Token mời ngẫu nhiên có thời hạn 48 giờ, lưu bản ghi `PENDING`.
  3. Hệ thống gửi email mời chứa đường link kích hoạt.
  4. Thành viên nhận email, đăng nhập và nhấn "Chấp nhận lời mời".
  5. Trạng thái chuyển từ `PENDING` sang `ACTIVE`.
- **Vết yêu cầu:** `FR04`, DOCX Sec 3.5 (SD-03).
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/household/member_invite.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/household/member_invite.puml)

---

## 3. Phân hệ 3: Quản lý Công tơ & Ghi nhận Chỉ số (`meter`)

### UC-UTILITY-ACCOUNT-MGMT: Quản lý tài khoản dịch vụ
- **Mã Use Case:** `UC-UTILITY-ACCOUNT-MGMT`
- **Tên Nghiệp vụ:** Quản lý tài khoản dịch vụ
- **Phân hệ:** `meter`
- **Mục tiêu:** Quản lý mã khách hàng, nhà cung cấp điện lực (EVN) hoặc cấp nước.
- **Actor chính:** `Owner`, `Member`
- **Luồng chính:**
  1. Người dùng chọn "Thêm tài khoản dịch vụ" (`POST /api/utility-accounts`).
  2. Nhập mã khách hàng (ví dụ: `PA13010012345`), nhà cung cấp (EVN Hà Nội), loại biểu giá.
  3. Lưu vào CSDL `utility_accounts`.
- **Vết yêu cầu:** `FR05`, `GET/POST/PATCH /api/utility-accounts`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/meter/utility_account_mgmt.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/meter/utility_account_mgmt.puml)

---

### UC-METER-MGMT: Khai báo công tơ điện nước
- **Mã Use Case:** `UC-METER-MGMT`
- **Tên Nghiệp vụ:** Khai báo công tơ điện nước
- **Phân hệ:** `meter`
- **Mục tiêu:** Thêm công tơ mới cho hộ gia đình (Công tơ tổng hoặc công tơ phụ).
- **Actor chính:** `Owner`, `Member`
- **Luồng chính:**
  1. Nhập tên công tơ, mã công tơ, loại dịch vụ (Điện/Nước), chỉ số ban đầu.
  2. Gửi `POST /api/meters`.
  3. Backend chèn công tơ mới vào `meters` liên kết với `household_id`.
- **Vết yêu cầu:** `FR05`, DOCX Sec 3.2.3 (UC-04), `POST /api/meters`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/meter/meter_management.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/meter/meter_management.puml)

---

### UC-METER-UPDATE: Cập nhật thông tin công tơ
- **Mã Use Case:** `UC-METER-UPDATE`
- **Tên Nghiệp vụ:** Cập nhật thông tin công tơ
- **Phân hệ:** `meter`
- **Mục tiêu:** Chỉnh sửa tên, thông số kỹ thuật hoặc bật/tắt trạng thái hoạt động công tơ.
- **Actor chính:** `Owner`
- **Luồng chính:**
  1. Chủ hộ chọn công tơ và chỉnh sửa thông tin.
  2. Gửi `PATCH /api/meters/{id}`.
  3. Backend cập nhật `meters` và lưu Audit Log.
- **Vết yêu cầu:** `FR05`, DOCX Sec 3.5 (SD-04), `PATCH /api/meters/{id}`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/meter/meter_update.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/meter/meter_update.puml)

---

### UC-READING-ENTRY: Ghi nhận chỉ số công tơ
- **Mã Use Case:** `UC-READING-ENTRY`
- **Tên Nghiệp vụ:** Ghi nhận chỉ số công tơ
- **Phân hệ:** `meter`
- **Mục tiêu:** Nhập chỉ số đo chốt kỳ hàng tháng, tự động kiểm tra số cũ và tính hóa đơn.
- **Actor chính:** `Owner`, `Member`
- **Actor hỗ trợ:** `FastAPI System`
- **Trigger:** Người dùng nhập số đo chốt kỳ tại màn hình Nhập chỉ số.
- **Tiền điều kiện:** Công tơ đang hoạt động (`is_active=True`).
- **Hậu điều kiện thành công:** Lưu `meter_readings`, tự động kích hoạt `UC-BILL-CALCULATION` để tạo hóa đơn.
- **Luồng chính (Main Flow):**
  1. Người dùng chọn công tơ và nhập giá trị chỉ số mới (ví dụ: `1450` kWh).
  2. Gửi `POST /api/readings`.
  3. Backend truy vấn chỉ số kỳ trước (`previous_reading`).
  4. Backend kiểm tra quy tắc: $C_{\text{mới}} \ge C_{\text{cũ}}$. Nếu sai, báo lỗi `400 Bad Request`.
  5. Tính sản lượng $C = C_{\text{mới}} - C_{\text{cũ}}$.
  6. Lưu bản ghi vào `meter_readings`.
  7. Backend tự động gọi `BillingService.create()` để tính tiền và xuất bản ghi `bills`.
  8. Trả về thông báo thành công và hóa đơn vừa được khởi tạo.
- **Vết yêu cầu:** `FR06`, `FR07`, DOCX Sec 3.2.3 (UC-05), `POST /api/readings`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/meter/reading_entry.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/meter/reading_entry.puml)

---

### UC-OCR-READING: Nhận diện chỉ số từ ảnh (AI OCR)
- **Mã Use Case:** `UC-OCR-READING`
- **Tên Nghiệp vụ:** Nhận diện chỉ số từ ảnh (AI OCR)
- **Phân hệ:** `meter`
- **Mục tiêu:** Trích xuất tự động chỉ số công tơ từ ảnh chụp mặt đồng hồ bằng AI.
- **Actor chính:** `Owner`, `Member`
- **Trạng thái:** Planned / Future Extension (Mock Provider).
- **Luồng chính:**
  1. Người dùng tải ảnh chụp mặt công tơ lên.
  2. Hệ thống gọi AI OCR Provider phân tích vùng chứa chữ số.
  3. Trả về chỉ số dự đoán kèm độ tin cậy (`source_confidence`).
  4. Người dùng xác nhận hoặc điều chỉnh chỉ số trước khi lưu.
- **Vết yêu cầu:** `FR08`, `FR09`, DOCX Sec 8.6, `providers/ocr.py`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/meter/ocr_reading.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/meter/ocr_reading.puml)

---

## 4. Phân hệ 4: Tính toán & Quản lý Hóa đơn (`billing`)

### UC-BILL-CALCULATION: Tự động tính tiền bậc thang
- **Mã Use Case:** `UC-BILL-CALCULATION`
- **Tên Nghiệp vụ:** Tự động tính tiền bậc thang
- **Phân hệ:** `billing`
- **Mục tiêu:** Phân rã sản lượng tiêu thụ qua biểu giá 6 bậc EVN hoặc 4 bậc nước bằng tính toán chuẩn `DECIMAL(12,2)`.
- **Actor chính:** `System` (Hệ thống tự động)
- **Luồng chính (Main Flow):**
  1. Đọc sản lượng $C$ từ lượt ghi chỉ số mới.
  2. Lấy biểu giá đang có hiệu lực trong `tariffs` và `tariff_tiers`.
  3. Phân bổ sản lượng qua từng bậc giá:
     - Điện: Bậc 1 (0-50 kWh), Bậc 2 (51-100 kWh), Bậc 3 (101-200 kWh), Bậc 4 (201-300 kWh), Bậc 5 (301-400 kWh), Bậc 6 (>400 kWh).
     - Nước: Bậc 1 (0-10 m³), Bậc 2 (10-20 m³), Bậc 3 (20-30 m³), Bậc 4 (>30 m³).
  4. Tính tổng tiền trước thuế, tiền thuế GTGT (8% hoặc 10%) và phí bảo vệ môi trường.
  5. Tạo hóa đơn trong `bills` với trạng thái `UNPAID` và lưu snapshot phân rã bậc giá trong `bill_detail_snapshot`.
- **Vết yêu cầu:** `FR10`, `FR11`, DOCX Sec 3.2.3 (UC-06), `billing_service.py`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/billing/bill_calculation.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/billing/bill_calculation.puml)

---

### UC-BILL-QUERY: Truy vấn & xem chi tiết hóa đơn
- **Mã Use Case:** `UC-BILL-QUERY`
- **Tên Nghiệp vụ:** Truy vấn & xem chi tiết hóa đơn
- **Phân hệ:** `billing`
- **Mục tiêu:** Xem danh sách hóa đơn theo kỳ và phân rã chi tiết đơn giá từng bậc.
- **Actor chính:** `Owner`, `Member`
- **Luồng chính:**
  1. Người dùng mở màn hình Hóa đơn (`GET /api/bills`).
  2. Chọn xem chi tiết một hóa đơn (`GET /api/bills/{id}`).
  3. Hiển thị thông tin tiêu thụ, số tiền theo từng bậc giá và hạn thanh toán.
- **Vết yêu cầu:** `FR12`, DOCX Sec 3.2.3 (UC-07), `GET /api/bills`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/billing/bill_query.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/billing/bill_query.puml)

---

### UC-EXPORT-PDF: Kết xuất hóa đơn PDF
- **Mã Use Case:** `UC-EXPORT-PDF`
- **Tên Nghiệp vụ:** Kết xuất hóa đơn PDF
- **Phân hệ:** `billing`
- **Mục tiêu:** Xuất và tải xuống file hóa đơn tiền điện/nước dạng PDF chuẩn in ấn.
- **Actor chính:** `Owner`, `Member`
- **Trạng thái:** As-Designed SRS.
- **Luồng chính:**
  1. Người dùng nhấn nút "Tải PDF" tại màn hình Chi tiết Hóa đơn.
  2. Hệ thống biên dịch HTML template hóa đơn thành file PDF.
  3. Trả về file PDF cho trình duyệt tải xuống.
- **Vết yêu cầu:** `FR14`, DOCX Sec 3.5 (SD-07).
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/billing/export_pdf.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/billing/export_pdf.puml)

---

### UC-PAYMENT-ENTRY: Ghi nhận thanh toán thủ công
- **Mã Use Case:** `UC-PAYMENT-ENTRY`
- **Tên Nghiệp vụ:** Ghi nhận thanh toán thủ công
- **Phân hệ:** `billing`
- **Mục tiêu:** Đánh dấu hóa đơn đã được trả tiền (chuyển trạng thái sang `PAID`).
- **Actor chính:** `Owner`, `Member`
- **Luồng chính:**
  1. Người dùng chọn hóa đơn `UNPAID` và bấm "Xác nhận đã thanh toán".
  2. Gửi `POST /api/payments` kèm hình thức thanh toán (Tiền mặt/Chuyển khoản).
  3. Backend tạo bản ghi `payments` và cập nhật `bills.status = 'PAID'`, `paid_at = now()`.
- **Vết yêu cầu:** `FR13`, DOCX Sec 3.2.3 (UC-08), `POST /api/payments`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/billing/payment_entry.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/billing/payment_entry.puml)

---

### UC-ONLINE-PAYMENT: Thanh toán hóa đơn trực tuyến
- **Mã Use Case:** `UC-ONLINE-PAYMENT`
- **Tên Nghiệp vụ:** Thanh toán hóa đơn trực tuyến
- **Phân hệ:** `billing`
- **Mục tiêu:** Thanh toán hóa đơn trực tiếp qua cổng VNPay/MoMo.
- **Actor chính:** `Owner`
- **Trạng thái:** Planned / Future Extension.
- **Luồng chính:**
  1. Người dùng chọn "Thanh toán VNPay".
  2. Hệ thống chuyển hướng sang VNPay Payment Gateway.
  3. Sau khi người dùng quét mã thanh toán, VNPay gửi IPN Callback cập nhật trạng thái hóa đơn.
- **Vết yêu cầu:** `FR13`, DOCX Sec 8.7.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/billing/online_payment.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/billing/online_payment.puml)

---

## 5. Phân hệ 5: Thống kê & Trợ lý Trí tuệ Nhân tạo AI (`ai_statistics`)

### UC-STATISTICS-ALERT: Theo dõi thống kê tiêu thụ
- **Mã Use Case:** `UC-STATISTICS-ALERT`
- **Tên Nghiệp vụ:** Theo dõi thống kê tiêu thụ
- **Phân hệ:** `ai_statistics`
- **Mục tiêu:** Xem biểu đồ sản lượng, chi phí qua các kỳ và danh sách cảnh báo nhắc hạn.
- **Actor chính:** `Owner`, `Member`
- **Luồng chính:**
  1. Người dùng mở trang Dashboard Thống kê (`GET /api/statistics`).
  2. Hệ thống trả về dữ liệu chuỗi thời gian tiêu thụ kWh/m³ và tổng tiền từng tháng.
  3. Frontend vẽ biểu đồ cột/đường tương tác.
- **Vết yêu cầu:** `FR19-24`, DOCX Sec 3.2.3 (UC-09), `GET /api/statistics`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/ai_statistics/statistics_alert.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/ai_statistics/statistics_alert.puml)

---

### UC-NOTIFICATION-READ: Đánh dấu đã đọc thông báo
- **Mã Use Case:** `UC-NOTIFICATION-READ`
- **Tên Nghiệp vụ:** Đánh dấu đã đọc thông báo
- **Phân hệ:** `ai_statistics`
- **Mục tiêu:** Đánh dấu thông báo nhắc chốt số/đóng tiền là đã đọc.
- **Actor chính:** `User`
- **Luồng chính:**
  1. Người dùng mở danh sách thông báo (`GET /api/notifications`).
  2. Nhấn nút "Đánh dấu đã đọc" (`PATCH /api/notifications/{id}/read`).
  3. Backend cập nhật `is_read = True`.
- **Vết yêu cầu:** `FR25`, `PATCH /api/notifications/{id}/read`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/ai_statistics/notification_read.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/ai_statistics/notification_read.puml)

---

### UC-AI-CHATBOT: Hỏi đáp với Trợ lý AI Agent
- **Mã Use Case:** `UC-AI-CHATBOT`
- **Tên Nghiệp vụ:** Hỏi đáp với Trợ lý AI Agent
- **Phân hệ:** `ai_statistics`
- **Mục tiêu:** Chatbot thông minh giải thích hóa đơn, tra cứu quy định biểu giá nhà nước qua RAG.
- **Actor chính:** `Owner`, `Member`
- **Actor hỗ trợ:** `AI_Assistant` (Gemini + ChromaDB Vector Index)
- **Luồng chính (Main Flow):**
  1. Người dùng gửi câu hỏi (ví dụ: "Vì sao tháng này nhà tôi bị tính tiền điện Bậc 5?").
  2. Client gửi `POST /api/ai/chat`.
  3. AI Agent gọi RAG Hybrid Search truy xuất tri thức biểu giá và thông tin tiêu thụ hộ.
  4. LLM tổng hợp câu trả lời chi tiết có đính kèm trích dẫn văn bản pháp lý.
- **Vết yêu cầu:** `FR15`, `FR16`, `FR18`, DOCX Sec 3.2.3 (UC-10), `POST /api/ai/chat`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/ai_statistics/ai_chatbot.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/ai_statistics/ai_chatbot.puml)

---

### UC-AI-FORECAST-ANOMALY: AI Dự báo & Bất thường
- **Mã Use Case:** `UC-AI-FORECAST-ANOMALY`
- **Tên Nghiệp vụ:** AI Dự báo & Bất thường
- **Phân hệ:** `ai_statistics`
- **Mục tiêu:** Dự báo chi phí hóa đơn kỳ tới bằng WMA và phát hiện tiêu thụ bất thường nghi ngờ rò rỉ.
- **Actor chính:** `AI_Assistant`, `Owner`
- **Luồng chính:**
  1. Người dùng truy cập trang Dự báo (`GET /api/statistics/forecast`).
  2. Backend gọi `forecast_service.py` (Weighted Moving Average) và `anomaly_service.py` (Rolling StdDev).
  3. Trả về sản lượng dự báo kỳ tới và danh sách cảnh báo chỉ số bất thường.
- **Vết yêu cầu:** `FR15`, `FR17`, DOCX Sec 3.2.3 (UC-11), `GET /api/statistics/forecast`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/ai_statistics/ai_forecast_anomaly.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/ai_statistics/ai_forecast_anomaly.puml)

---

## 6. Phân hệ 6: Quản trị Hệ thống Admin (`admin`)

### UC-ADMIN-USER-MGMT: Quản lý người dùng Admin
- **Mã Use Case:** `UC-ADMIN-USER-MGMT`
- **Tên Nghiệp vụ:** Quản lý người dùng Admin
- **Phân hệ:** `admin`
- **Mục tiêu:** Xem danh sách người dùng, khóa hoặc mở khóa tài khoản người dùng hệ thống.
- **Actor chính:** `Admin`
- **Luồng chính:**
  1. Admin mở trang Quản lý Người dùng (`GET /api/admin/users`).
  2. Bấm khóa hoặc mở khóa một tài khoản (`PATCH /api/admin/users/{id}`).
  3. Backend cập nhật `is_active` trong `users` và ghi Audit Log.
- **Vết yêu cầu:** `FR26`, DOCX Sec 3.2.3 (UC-12), `GET/PATCH /api/admin/users`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/admin/admin_user_mgmt.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/admin/admin_user_mgmt.puml)

---

### UC-ADMIN-TARIFF-CONFIG: Cấu hình biểu giá bậc thang
- **Mã Use Case:** `UC-ADMIN-TARIFF-CONFIG`
- **Tên Nghiệp vụ:** Cấu hình biểu giá bậc thang
- **Phân hệ:** `admin`
- **Mục tiêu:** Thiết lập phiên bản đơn giá điện/nước bậc thang mới theo quyết định của nhà nước.
- **Actor chính:** `Admin`
- **Luồng chính:**
  1. Admin nhập phiên bản biểu giá mới (ví dụ: QĐ 2699/QĐ-BCT).
  2. Gửi `POST /api/admin/tariffs`.
  3. Backend chèn bản ghi mới vào `tariffs` và `tariff_tiers`.
- **Vết yêu cầu:** `FR27`, DOCX Sec 3.2.3 (UC-12), `POST /api/admin/tariffs`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/admin/admin_tariff_config.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/admin/admin_tariff_config.puml)

---

### UC-ADMIN-AUDIT-LOG: Tra cứu nhật ký hệ thống
- **Mã Use Case:** `UC-ADMIN-AUDIT-LOG`
- **Tên Nghiệp vụ:** Tra cứu nhật ký hệ thống
- **Phân hệ:** `admin`
- **Mục tiêu:** Xem lịch sử truy vết các thao tác quan trọng trên toàn hệ thống.
- **Actor chính:** `Admin`
- **Luồng chính:**
  1. Admin mở trang Nhật ký Hệ thống (`GET /api/admin/audit`).
  2. Hệ thống trả về 200 bản ghi audit log mới nhất kèm thông tin IP, user, thao tác và thời gian.
- **Vết yêu cầu:** `FR28`, DOCX Sec 3.2.3 (UC-12), `GET /api/admin/audit`.
- **Sơ đồ Trình tự:** [`docs/uml/sources/sequence/admin/admin_audit_log.puml`](file:///f:/Web/AI_Household_Utility_Billing/website/docs/uml/sources/sequence/admin/admin_audit_log.puml)
