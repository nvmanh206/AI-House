# BÁO CÁO THIẾT KẾ VÀ KIỂM CHỨNG SƠ ĐỒ USE CASE TỔNG QUAN
## Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia Đình tích hợp AI (Nhà Mình)

---

## 1. Phạm vi và Căn cứ Nguồn Dữ liệu

### 1.1 Căn cứ Trích dẫn & Đối soát
Báo cáo thiết kế này được xây dựng trên sự kết hợp thống nhất giữa:
1. **Báo cáo Dự án / DOCX Yêu cầu Hệ thống (`BaoCao_DuAn_QuanLyDienNuoc (1).docx`):** Xác định mục tiêu nghiệp vụ, phân hệ chức năng (Section 3.2.3, 3.5), yêu cầu phi chức năng (NFR01-NFR11) và định hướng phát triển (Section 8.6, 8.7).
2. **Mã nguồn Backend Thực tế (`backend/app/`):** FastAPI Routes (`main.py`, `ai/router.py`), ORM Models (`models.py`), Dịch vụ (`billing_service.py`, `security.py`, `services.py`), và Test suite (`tests/`).
3. **Danh mục Use Case Chuẩn hóa (`docs/design/use-case-catalog.md`):** Thống nhất 25 Use Cases độc lập với mã số cố định.

### 1.2 Phân định Trạng thái Hiện thực (As-Is vs As-Designed / Future)
- **Hiện trạng được Code chứng minh (Code-Proven / As-Is):** Các chức năng đã có Backend Router, ORM Model và Dịch vụ xử lý hoạt động (Ví dụ: `UC-LOGIN`, `UC-REGISTER`, `UC-READING-ENTRY`, `UC-BILL-CALCULATION`, `UC-AI-CHATBOT`).
- **Thiết kế Yêu cầu SRS (As-Designed SRS):** Chức năng thuộc tài liệu thiết kế nghiệp vụ nhưng chưa có API chính thức (Ví dụ: `UC-EXPORT-PDF` xuất file PDF hóa đơn, `UC-MEMBER-INVITE` gửi email token mời).
- **Mở rộng Tương lai (Planned / Future Extension):** Chức năng thuộc hướng phát triển nâng cao được DOCX ghi nhận chưa triển khai bản hiện tại (Ví dụ: `UC-OCR-READING` nhận diện chỉ số từ ảnh công tơ, `UC-ONLINE-PAYMENT` thanh toán online VNPay/MoMo 1-Click). Cả 2 UC này được gắn nhãn `<<Future Extension>>` trên sơ đồ.

---

## 2. Bảng Phân quyền Actor -> Scope -> Use Cases

Các Tác nhân (Actors) được định nghĩa là đối tượng bên ngoài ranh giới hệ thống tương tác trực tiếp với các Use Case:

| Actor (Ký hiệu) | Vai trò & Phân quyền Hệ thống | Phạm vi Dữ liệu & Ngữ cảnh (Scope) | Danh sách Use Cases Thực hiện |
| :--- | :--- | :--- | :--- |
| **Guest** *(Khách)* | Người dùng chưa xác thực danh tính | Toàn hệ thống (Public Scope) | `UC-REGISTER`, `UC-LOGIN` |
| **User** *(Người dùng)* | Người dùng đã đăng nhập hệ thống | Cá nhân (User Scope) | `UC-LOGIN`, `UC-LOGOUT`, `UC-USER-PROFILE`, `UC-SELECT-HOUSEHOLD`, `UC-NOTIFICATION-READ` |
| **Owner** *(Chủ hộ)* | Quản trị viên của một Hộ gia đình | Hộ gia đình sở hữu (`OWNER` role) | `UC-HOUSEHOLD-SETUP`, `UC-MEMBER-MGMT`, `UC-MEMBER-INVITE`, `UC-UTILITY-ACCOUNT-MGMT`, `UC-METER-MGMT`, `UC-METER-UPDATE`, `UC-READING-ENTRY`, `UC-OCR-READING`, `UC-BILL-QUERY`, `UC-EXPORT-PDF`, `UC-PAYMENT-ENTRY`, `UC-ONLINE-PAYMENT`, `UC-STATISTICS-ALERT`, `UC-AI-CHATBOT`, `UC-AI-FORECAST-ANOMALY` |
| **Member** *(Thành viên)* | Thành viên thuộc Hộ gia đình | Hộ gia đình tham gia (`MEMBER` role) | `UC-READING-ENTRY`, `UC-OCR-READING`, `UC-BILL-QUERY`, `UC-EXPORT-PDF`, `UC-PAYMENT-ENTRY`, `UC-STATISTICS-ALERT`, `UC-AI-CHATBOT`, `UC-AI-FORECAST-ANOMALY` |
| **Admin** *(Quản trị viên)* | Quản trị viên toàn bộ hệ thống | Toàn bộ CSDL (`ADMIN` role) | `UC-ADMIN-USER-MGMT`, `UC-ADMIN-TARIFF-CONFIG`, `UC-ADMIN-AUDIT-LOG` |
| **VNPay Gateway** | Cổng thanh toán trực tuyến bên ngoài | External Payment API | `UC-ONLINE-PAYMENT` |

*Ghi chú:* Các thành phần nội bộ như FastAPI, PostgreSQL Database, BillingService hay AI Module **không phải Actor bên ngoài** và không xuất hiện ngoài ranh giới hệ thống.

---

## 3. Bảng Độ phủ Nghiệp vụ Phân hệ (Business Coverage Table)

| Nhóm Chức năng (Sub-Package) | Mã UC | Tên Nghiệp vụ tiếng Việt | Nguồn Trích dẫn DOCX / Code | Trạng thái Hiện thực |
| :--- | :--- | :--- | :--- | :--- |
| **1. Tài khoản & Xác thực** | `UC-REGISTER`<br>`UC-LOGIN`<br>`UC-LOGOUT`<br>`UC-USER-PROFILE` | Đăng ký tài khoản<br>Đăng nhập hệ thống<br>Đăng xuất hệ thống<br>Cập nhật hồ sơ cá nhân | DOCX Sec 3.2.3, `POST /api/auth/register`<br>DOCX Sec 3.2.3, `POST /api/auth/login`<br>`POST /api/auth/logout`<br>`PATCH /api/auth/me` | Code-Proven |
| **2. Hộ gia đình & Thành viên** | `UC-HOUSEHOLD-SETUP`<br>`UC-SELECT-HOUSEHOLD`<br>`UC-MEMBER-MGMT`<br>`UC-MEMBER-INVITE` | Khởi tạo hộ gia đình<br>Chọn hộ gia đình hoạt động<br>Quản lý thành viên hộ<br>Mời thành viên vào hộ | DOCX Sec 3.2.3 (UC-02), `POST /api/households`<br>`POST /api/households/{id}/select`<br>DOCX Sec 3.2.3 (UC-03), `GET/POST /api/members`<br>DOCX Sec 3.5 (SD-03), `services.py` | Code-Proven / As-Designed |
| **3. Công tơ & Chỉ số** | `UC-UTILITY-ACCOUNT-MGMT`<br>`UC-METER-MGMT`<br>`UC-METER-UPDATE`<br>`UC-READING-ENTRY`<br>`UC-OCR-READING` | Quản lý tài khoản dịch vụ<br>Khai báo công tơ điện nước<br>Cập nhật thông tin công tơ<br>Ghi nhận chỉ số công tơ<br>Nhận diện chỉ số từ ảnh (OCR) | `GET/POST/PATCH /api/utility-accounts`<br>DOCX Sec 3.2.3 (UC-04), `POST /api/meters`<br>DOCX Sec 3.5 (SD-04), `PATCH /api/meters/{id}`<br>DOCX Sec 3.2.3 (UC-05), `POST /api/readings`<br>DOCX Sec 8.6, `providers/ocr.py` | Code-Proven / Future Extension |
| **4. Hóa đơn & Thanh toán** | `UC-BILL-CALCULATION`<br>`UC-BILL-QUERY`<br>`UC-EXPORT-PDF`<br>`UC-PAYMENT-ENTRY`<br>`UC-ONLINE-PAYMENT` | Tự động tính tiền bậc thang<br>Xem chi tiết hóa đơn<br>Xuất hóa đơn PDF<br>Ghi nhận thanh toán thủ công<br>Thanh toán hóa đơn trực tuyến | DOCX Sec 3.2.3 (UC-06), `billing_service.py`<br>DOCX Sec 3.2.3 (UC-07), `GET /api/bills`<br>DOCX Sec 3.5 (SD-07), SRS FR14<br>DOCX Sec 3.2.3 (UC-08), `POST /api/payments`<br>DOCX Sec 8.7 (VNPay Gateway) | Code-Proven / Future Extension |
| **5. Thống kê & Thông báo** | `UC-STATISTICS-ALERT`<br>`UC-NOTIFICATION-READ` | Theo dõi thống kê tiêu thụ<br>Đánh dấu đã đọc thông báo | DOCX Sec 3.2.3 (UC-09), `GET /api/statistics`<br>`PATCH /api/notifications/{id}/read` | Code-Proven |
| **6. Trợ lý AI & Dự báo** | `UC-AI-CHATBOT`<br>`UC-AI-FORECAST-ANOMALY` | Hỏi đáp với Trợ lý AI Agent<br>AI Dự báo & Bất thường | DOCX Sec 3.2.3 (UC-10), `POST /api/ai/chat`<br>DOCX Sec 3.2.3 (UC-11), `GET /api/statistics/forecast` | Code-Proven |
| **7. Quản trị hệ thống** | `UC-ADMIN-USER-MGMT`<br>`UC-ADMIN-TARIFF-CONFIG`<br>`UC-ADMIN-AUDIT-LOG` | Quản lý người dùng Admin<br>Cấu hình biểu giá bậc thang<br>Tra cứu nhật ký hệ thống | DOCX Sec 3.2.3 (UC-12), `GET/PATCH /api/admin/users`<br>DOCX Sec 3.2.3 (UC-12), `POST /api/admin/tariffs`<br>DOCX Sec 3.2.3 (UC-12), `GET /api/admin/audit` | Code-Proven |

---

## 4. Bảng Kiểm chứng Quan hệ Include / Extend (Relationship Verification Table)

Đánh giá toàn bộ các mối quan hệ `<<include>>` và `<<extend>>` theo chuẩn ngữ nghĩa UML 2.x:

| STT | UC Nguồn (Source) | UC Đích (Target) | Loại Quan hệ UML | Lý do Nghiệp vụ & Căn cứ Mã nguồn / DOCX | Điều kiện (Condition) & Extension Point | Quyết định Kiểm duyệt |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | `UC-MEMBER-INVITE` | `UC-MEMBER-MGMT` | **Không có** | Mời thành viên qua email token 48h là một mục tiêu nghiệp vụ độc lập của Chủ hộ, không phải hành vi mở rộng kịch bản quản lý. | N/A | **ĐỘC LẬP (NO EXTEND)** |
| **B** | `UC-METER-UPDATE` | `UC-METER-MGMT` | **Không có** | Cập nhật thông tin công tơ là thao tác chỉnh sửa dữ liệu độc lập thuộc nhóm CRUD công tơ, không phải quan hệ extend. | N/A | **ĐỘC LẬP (NO EXTEND)** |
| **C** | `UC-EXPORT-PDF` | `UC-BILL-QUERY` | `<<extend>>` | Người dùng xem chi tiết hóa đơn có thể tùy chọn yêu cầu xuất file PDF tại điểm mở rộng kịch bản. | **Condition:** Người dùng nhấn nút "Tải PDF".<br>**Extension Point:** Màn hình Chi tiết Hóa đơn. | **GIỮ (KEEP EXTEND)** |
| **D** | `UC-READING-ENTRY` | `UC-BILL-CALCULATION` | `<<include>>` | Hợp đồng nghiệp vụ quy định: Mỗi khi ghi nhận chỉ số công tơ thành công (`POST /api/readings`), hệ thống bắt buộc tự động tính toán hóa đơn bậc thang (`BillingService.create()`). | N/A (Hành vi bắt buộc) | **GIỮ (KEEP INCLUDE)** |
| **E** | `UC-OCR-READING` | `UC-READING-ENTRY` | **Không có** | OCR từ ảnh là phương thức nhập liệu thay thế cho nhập tay, được mô hình hóa thành Use Case độc lập mang nhãn `<<Future Extension>>`. | N/A | **ĐỘC LẬP (NO EXTEND)** |
| **F** | `UC-ONLINE-PAYMENT` | `UC-PAYMENT-ENTRY` | **Không có** | Thanh toán trực tuyến VNPay là kênh thanh toán độc lập song song với thanh toán thủ công, không phải hành vi mở rộng cho thao tác thủ công. | N/A | **ĐỘC LẬP (NO EXTEND)** |
| **G** | `UC-REFRESH-TOKEN` | `UC-LOGIN` | **Không có** | Cấp mới Access Token là cơ chế kỹ thuật nội bộ của Session Management, không phải Use Case độc lập hay mở rộng của Đăng nhập. | N/A | **LOẠI BỎ (REMOVE)** |
| **H** | `UC-BILL-QUERY (List)` | `UC-BILL-QUERY (Detail)` | **Không có** | Xem danh sách và xem chi tiết là các góc nhìn truy vấn thuộc cùng một Use Case `UC-BILL-QUERY`, không dùng include giữa xem danh sách và xem chi tiết. | N/A | **GỘP CHUNG (SINGLE UC)** |

---

## 5. Mâu thuẫn và Giả định Thiết kế đã Giải quyết

1. **Thuật toán Mã hóa Mật khẩu:** Code hiện tại sử dụng `Argon2id` (`argon2-cffi`), trong khi DOCX NFR03 ghi `Bcrypt`. Báo cáo chốt `Argon2id` làm tiêu chuẩn hiện hành chứng minh bằng code.
2. **Quy trình Mời Thành viên Hộ:** Code hiện tại hỗ trợ thêm trực tiếp nếu đúng email; DOCX SD-03 thiết kế luồng email token 48h. Cả 2 luồng đều được ghi nhận trong danh mục đặc tả.
3. **Phân định Tính năng Tương lai:** `UC-OCR-READING` và `UC-ONLINE-PAYMENT` được đánh dấu rõ stereotype `<<Future Extension>>` trên sơ đồ tổng quan để không gây nhầm lẫn với các tính năng đã vận hành chính thức.
