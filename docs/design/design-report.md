# BÁO CÁO TỔNG THỂ THIẾT KẾ HỆ THỐNG (MASTER SYSTEM DESIGN REPORT)
## Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia Đình tích hợp AI (Nhà Mình)

---

## 1. Tổng quan Dự án & Mục tiêu Tái cấu trúc
Tài liệu này tổng hợp toàn bộ kết quả rà soát, tái cấu trúc và hoàn thiện bộ thiết kế hệ thống **"Nhà Mình"** dựa trên trích dẫn đối sánh giữa **Tài liệu Báo cáo Yêu cầu (DOCX / SRS)** và **Mã nguồn Backend FastAPI / Database PostgreSQL**.

### Các Kết quả Chính Đạt được:
1. **Chuẩn hóa Danh mục Use Case:** Tách biệt 12 UCs gộp ban đầu thành **25 Use Cases nghiệp vụ độc lập**, tách hoàn toàn `UC-REGISTER` ("Đăng ký tài khoản") và `UC-LOGIN` ("Đăng nhập hệ thống").
2. **Bộ sơ đồ PlantUML (44 Sơ đồ):**
   - **19 Sơ đồ Use Case:** Bao phủ 6 phân hệ nghiệp vụ + 1 sơ đồ Tổng quan hệ thống. Mọi ellipse đều hiển thị cả `UC-CODE` và Tên tiếng Việt (`UC-CODE\nTên nghiệp vụ`).
   - **25 Sơ đồ Trình tự (Sequence):** Xây dựng đầy đủ sơ đồ trình tự tương ứng với tất cả 25 Use Cases, mô tả chi tiết tương tác Tác nhân -> UI -> Router -> Service -> CSDL.
3. **Chất lượng Xuất Ảnh 100% PASS:** Render thành công **44 file PNG** và **44 file SVG** (0 file lỗi 0-byte) dưới thư mục `docs/uml/images/`.
4. **Bố cục Chuẩn mực (Strict Orthogonal Layout):** Áp dụng `linetype ortho`, khoảng cách nút chuẩn (`nodesep 45`, `ranksep 65`), đường nối vuông góc ngang/dọc, không đè chữ hay cắt nhau.

---

## 2. Bảng Phủ Phân hệ Nghiệp vụ (Section Coverage Table)

| Phân hệ Nghiệp vụ | Tên Phân hệ tiếng Việt | Mã Use Case Bao phủ | Số Sơ đồ Use Case | Số Sơ đồ Sequence | File Sơ đồ Use Case (.puml / .png / .svg) | File Sơ đồ Sequence (.puml / .png / .svg) | Trạng thái Pass |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `auth` | Quản trị Tài khoản & Xác thực | `UC-REGISTER`<br>`UC-LOGIN`<br>`UC-LOGOUT`<br>`UC-USER-PROFILE` | 3 | 4 | `sources/usecase/auth/*` | `sources/sequence/auth/*` | **PASSED** |
| `household` | Khởi tạo & Quản lý Hộ gia đình | `UC-HOUSEHOLD-SETUP`<br>`UC-SELECT-HOUSEHOLD`<br>`UC-MEMBER-MGMT`<br>`UC-MEMBER-INVITE` | 3 | 4 | `sources/usecase/household/*` | `sources/sequence/household/*` | **PASSED** |
| `meter` | Quản lý Công tơ & Chỉ số | `UC-UTILITY-ACCOUNT-MGMT`<br>`UC-METER-MGMT`<br>`UC-METER-UPDATE`<br>`UC-READING-ENTRY`<br>`UC-OCR-READING` | 3 | 5 | `sources/usecase/meter/*` | `sources/sequence/meter/*` | **PASSED** |
| `billing` | Tính toán & Quản lý Hóa đơn | `UC-BILL-CALCULATION`<br>`UC-BILL-QUERY`<br>`UC-EXPORT-PDF`<br>`UC-PAYMENT-ENTRY`<br>`UC-ONLINE-PAYMENT` | 4 | 5 | `sources/usecase/billing/*` | `sources/sequence/billing/*` | **PASSED** |
| `ai_statistics` | Thống kê & Trợ lý AI Agent | `UC-STATISTICS-ALERT`<br>`UC-NOTIFICATION-READ`<br>`UC-AI-CHATBOT`<br>`UC-AI-FORECAST-ANOMALY` | 4 | 4 | `sources/usecase/ai_statistics/*` | `sources/sequence/ai_statistics/*` | **PASSED** |
| `admin` | Quản trị Hệ thống Admin | `UC-ADMIN-USER-MGMT`<br>`UC-ADMIN-TARIFF-CONFIG`<br>`UC-ADMIN-AUDIT-LOG` | 1 | 3 | `sources/usecase/admin/*` | `sources/sequence/admin/*` | **PASSED** |
| `system_overview` | Sơ đồ Tổng quan Hệ thống | **Tất cả 25 Use Cases** | 1 | N/A | `sources/usecase/system_overview/*` | N/A | **PASSED** |

---

## 3. Bảng Kiểm duyệt Quan hệ Include/Extend (Relationship-Review Table)

| STT | Use Case Nguồn | Use Case Đích | Loại Quan hệ | Lý do Nghiệp vụ & Trích dẫn Mã nguồn / Tài liệu | Quyết định Kiểm duyệt |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `UC-READING-ENTRY` | `UC-BILL-CALCULATION` | `<<include>>` | Mỗi khi ghi nhận chỉ số công tơ thành công, hệ thống bắt buộc tự động tính hóa đơn tiền điện/nước (`BillingService.create()`). | **GIỮ (KEEP)** |
| 2 | `UC-EXPORT-PDF` | `UC-BILL-QUERY` | `<<extend>>` | Người dùng mở xem chi tiết hóa đơn mới có thể tùy chọn bấm "Kết xuất PDF" để tải về. | **GIỮ (KEEP)** |
| 3 | `UC-MEMBER-INVITE` | `UC-MEMBER-MGMT` | `<<extend>>` | Tính năng gửi email mời qua token mở rộng luồng thêm thành viên trực tiếp hiện có. | **GIỮ (KEEP)** |
| 4 | `UC-OCR-READING` | `UC-READING-ENTRY` | `<<extend>>` | Nhận diện chỉ số qua camera ảnh là phương thức hỗ trợ mở rộng cho luồng nhập chỉ số thủ công. | **GIỮ (KEEP)** |
| 5 | `UC-ONLINE-PAYMENT` | `UC-PAYMENT-ENTRY` | `<<extend>>` | Thanh toán trực tuyến VNPay/MoMo là phương thức thanh toán mở rộng cho luồng ghi nhận thanh toán. | **GIỮ (KEEP)** |
| 6 | `UC-REGISTER` | `UC-LOGIN` | **KHÔNG CÓ** | Tách hoàn toàn thành 2 Use Case độc lập. Đăng ký không include Đăng nhập. | **LOẠI BỎ (REMOVE)** |

---

## 4. Kết quả Kiểm định Xuất Hình ảnh & Bố cục Sơ đồ
- **Tổng số sơ đồ nguồn PlantUML (.puml):** 44 file
- **Tổng số hình ảnh PNG (.png):** 44 file (100% PASS, size $>0$ KB)
- **Tổng số hình ảnh SVG (.svg):** 44 file (100% PASS, SVG XML valid)
- **Bố cục Visual Audit:**
  - Định dạng đường nối: `skinparam linetype ortho` (đường vuông góc 90 degree).
  - Khoảng cách nút: `nodesep 45`, `ranksep 65` (thông thoáng, rõ rệt).
  - Độ phân giải: `dpi 180` (sắc nét trên màn hình và báo cáo in ấn).
  - Tên tiếng Việt & mã UC: Hiển thị 100% trên các hình ellipse Use Case và mũi tên giao tiếp.
