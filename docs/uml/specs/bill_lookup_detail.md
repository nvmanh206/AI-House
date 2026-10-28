# ĐẶC TẢ CHI TIẾT VÀ KIỂM CHỨNG USE CASE — TRA CỨU VÀ XEM CHI TIẾT HÓA ĐƠN
## Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia Đình tích hợp AI (Nhà Mình)

---

## 1. Tổng quan Phân hệ Nghiệp vụ

Phân hệ **Tra cứu và xem chi tiết hóa đơn** cung cấp khả năng truy vấn, quản lý và theo dõi thông tin tài chính điện nước hàng tháng cho các hộ gia đình. 

### 1.1 Căn cứ Nguồn Yêu cầu & Mã nguồn
- **Tài liệu Báo cáo Yêu cầu (DOCX):** Section 3.2.3 (UC-07 Tra cứu hóa đơn), Section 3.5 (SD-07 Sơ đồ trình tự xem chi tiết hóa đơn), Yêu cầu SRS `FR12` (Truy vấn hóa đơn theo kỳ/trạng thái), `FR14` (Kết xuất hóa đơn PDF).
- **Mã nguồn Backend FastAPI:**
  - REST Endpoint: `GET /api/bills` (Danh sách hóa đơn hộ gia đình), `GET /api/bills/{id}` (Chi tiết hóa đơn).
  - SQLAlchemy Models: `Bill`, `UtilityAccount`, `BillingPeriod`, `MeterReading`, `Tariff`, `TariffTier`.
  - Service Layer: `services.py` (`bills()`, `bill(id)`), `billing_service.py` (`BillingService`).

### 1.2 Phân quyền Actor & Phạm vi Dữ liệu (Access Scope)
- **Actor hợp lệ:** `Owner` (Chủ hộ) và `Member` (Thành viên hộ).
- **Ranh giới Phân lập Dữ liệu:** Mọi truy vấn bắt buộc lọc theo `household_id` của phiên làm việc hiện tại (`self.member().household_id`). Người dùng thuộc hộ gia đình A tuyệt đối không thể xem hóa đơn của hộ gia đình B (`403 Forbidden / DomainError`).

---

## 2. Đặc tả Chi tiết các Use Case

### 2.1 Đặc tả UC-BILL-LIST: Tra cứu danh sách hóa đơn

| Mục (Attribute) | Nội dung Chi tiết (Specification Detail) |
| :--- | :--- |
| **Mã Use Case** | `UC-BILL-LIST` |
| **Tên Nghiệp vụ** | Tra cứu danh sách hóa đơn |
| **Tác nhân chính** | `Owner` (Chủ hộ), `Member` (Thành viên hộ) |
| **Mục tiêu** | Xem danh sách tổng quan các hóa đơn điện nước của hộ gia đình với các tùy chọn bộ lọc. |
| **Kích hoạt (Trigger)** | Người dùng chọn mục "Hóa đơn" trên thanh điều hướng giao diện Web/Mobile. |
| **Tiền điều kiện** | 1. Người dùng đã đăng nhập hệ thống (`UC-LOGIN`).<br>2. Người dùng đã chọn hộ gia đình hoạt động hiện tại. |
| **Hậu điều kiện** | Danh sách hóa đơn tương ứng với bộ lọc được hiển thị trên giao diện người dùng. |

#### Luồng sự kiện chính (Main Flow):
1. Người dùng truy cập trang Quản lý Hóa đơn.
2. Giao diện gửi yêu cầu `GET /api/bills` kèm JWT Bearer Token.
3. Backend kiểm tra quyền thành viên hộ (`self.member().household_id`) và truy vấn danh sách hóa đơn từ CSDL.
4. Backend tính toán trạng thái hóa đơn thực tế (`UNPAID`, `PAID`, `OVERDUE` nếu quá hạn `due_date`) và sắp xếp giảm dần theo kỳ thanh toán (`period YYYY-MM`).
5. Giao diện hiển thị danh sách hóa đơn bao gồm các thông tin tóm tắt: Loại dịch vụ (Điện/Nước), Kỳ hóa đơn, Tổng tiền (`final_amount`), Hạn thanh toán (`due_date`), Trạng thái (`UNPAID`/`PAID`/`OVERDUE`).

#### Luồng phụ - Áp dụng Bộ lọc (Filter Sub-flow):
1. Tại màn hình danh sách, người dùng chọn các tiêu chí lọc:
   - **Kỳ thanh toán:** Năm (`year`), Tháng (`month`).
   - **Loại dịch vụ:** Điện (`ELECTRICITY`), Nước (`WATER`).
   - **Trạng thái:** Chưa thanh toán (`UNPAID`), Đã thanh toán (`PAID`), Quá hạn (`OVERDUE`).
2. Giao diện cập nhật danh sách hiển thị tương ứng với tiêu chí lọc đã chọn.

#### Ngoại lệ & Luồng thay thế (Exception Flows):
- **E1: Danh sách trống (No Bills Found):** Hệ thống hiển thị thông báo "Chưa có hóa đơn nào trong hộ gia đình / kỳ đã chọn".
- **E2: Lỗi kết nối CSDL / Backend (500 Server Error):** Hệ thống hiển thị thông báo lỗi "Không thể tải danh sách hóa đơn. Vui lòng thử lại sau."

---

### 2.2 Đặc tả UC-BILL-DETAIL: Xem chi tiết hóa đơn

| Mục (Attribute) | Nội dung Chi tiết (Specification Detail) |
| :--- | :--- |
| **Mã Use Case** | `UC-BILL-DETAIL` |
| **Tên Nghiệp vụ** | Xem chi tiết hóa đơn |
| **Tác nhân chính** | `Owner` (Chủ hộ), `Member` (Thành viên hộ) |
| **Mục tiêu** | Xem toàn bộ chi tiết chỉ số, phân bổ bậc giá, thuế phí và tổng tiền của một hóa đơn cụ thể. |
| **Kích hoạt (Trigger)** | Người dùng chọn bấm vào một dòng hóa đơn trong danh sách `UC-BILL-LIST`. |
| **Tiền điều kiện** | 1. Người dùng đang ở màn hình danh sách hóa đơn (`UC-BILL-LIST`).<br>2. Hóa đơn tồn tại trong CSDL và thuộc hộ gia đình của người dùng. |
| **Hậu điều kiện** | Giao diện hiển thị chi tiết hóa đơn dạng phiếu tính tiền tiền điện/nước. |

#### Luồng sự kiện chính (Main Flow):
1. Người dùng bấm chọn hóa đơn mã `ID`.
2. Giao diện gửi yêu cầu `GET /api/bills/{id}`.
3. Backend kiểm tra quyền truy cập `scope(Bill, id)` đảm bảo hóa đơn thuộc `household_id` người dùng.
4. Backend trả về thông tin chi tiết đầy đủ bao gồm:
   - Thông tin Hộ gia đình, Mã công tơ, Loại dịch vụ (Điện/Nước), Đơn vị tính (`kWh`/`m³`).
   - Kỳ hóa đơn (`YYYY-MM`), Ngày chốt chỉ số, Chỉ số cũ (`previous_reading`), Chỉ số mới (`current_reading`), Sản lượng tiêu thụ (`consumption`).
   - Biểu giá áp dụng và Phân bổ sản lượng/tiền theo từng bậc thang (`tier_breakdown`).
   - Tiền điện/nước trước thuế (`subtotal`), Thuế GTGT/Phí môi trường (`tax_amount`), Tổng tiền thanh toán (`final_amount`).
   - Trạng thái thanh toán (`UNPAID`/`PAID`/`OVERDUE`), Hạn thanh toán (`due_date`), Ngày thanh toán (`paid_at` nếu có).
5. Giao diện hiển thị đầy đủ chi tiết hóa đơn dưới dạng bảng phiếu tính tiền trực quan.

#### Ngoại lệ & Luồng thay thế (Exception Flows):
- **E1: Hóa đơn không tồn tại (404 Not Found):** Hệ thống thông báo "Không tìm thấy thông tin hóa đơn yêu cầu".
- **E2: Truy cập trái phép hóa đơn hộ khác (403 Forbidden):** Backend từ chối truy cập và thông báo "Bạn không có quyền xem hóa đơn của hộ gia đình này".

---

### 2.3 Đặc tả UC-BILL-EXPORT-PDF: Xuất hóa đơn PDF

| Mục (Attribute) | Nội dung Chi tiết (Specification Detail) |
| :--- | :--- |
| **Mã Use Case** | `UC-BILL-EXPORT-PDF` |
| **Tên Nghiệp vụ** | Xuất hóa đơn PDF |
| **Tác nhân chính** | `Owner` (Chủ hộ), `Member` (Thành viên hộ) |
| **Mục tiêu** | Kết xuất và tải về file tài liệu PDF chứa thông tin hóa đơn chính thức để lưu trữ hoặc in ấn. |
| **Kích hoạt (Trigger)** | Người dùng nhấn nút "Xuất PDF / Tải hóa đơn" tại màn hình Chi tiết Hóa đơn (`UC-BILL-DETAIL`). |
| **Tiền điều kiện** | Người dùng đang xem chi tiết một hóa đơn hợp lệ (`UC-BILL-DETAIL`). |
| **Hậu điều kiện** | File PDF hóa đơn được tải thành công về thiết bị của người dùng. |

#### Luồng sự kiện chính (Main Flow):
1. Tại màn hình xem chi tiết hóa đơn, người dùng nhấn nút "Tải file PDF".
2. Giao diện khởi tạo yêu cầu xuất dữ liệu PDF.
3. Hệ thống tạo file tài liệu PDF định dạng chuẩn gồm đầy đủ logo, thông tin hộ, công tơ, phân bổ bậc giá và tổng tiền.
4. Trình duyệt tự động mở cửa sổ tải file `HoaDon_{Kỳ}_{Loại}.pdf` về máy người dùng.

#### Ngoại lệ & Luồng thay thế (Exception Flows):
- **E1: Trình duyệt chặn Popup/Download (Download Blocked):** Giao diện hiển thị thông báo hướng dẫn cho phép tải file.
- **E2: Lỗi khởi tạo file PDF (PDF Generation Error):** Thông báo "Không thể khởi tạo file PDF. Vui lòng thử lại sau."

---

## 3. Bảng Kiểm chứng Quan hệ UML (Relationship Justification Table)

| STT | UC Nguồn (Source) | UC Đích (Target) | Loại Quan hệ UML | Căn cứ Nghiệp vụ & Thiết kế | Điều kiện (Condition) & Extension Point | Kết luận Kiểm duyệt |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `UC-BILL-LIST` | `UC-BILL-DETAIL` | **Không có (Độc lập)** | Người dùng có thể xem danh sách mà không nhất thiết phải mở chi tiết một hóa đơn cụ thể. Thao tác chọn dòng là thứ tự chuyển màn hình UI, không tạo quan hệ include/extend. | N/A | **2 UC ĐỘC LẬP** |
| **2** | `UC-BILL-EXPORT-PDF` | `UC-BILL-DETAIL` | `<<extend>>` | Tính năng xuất PDF là hành vi bổ sung tùy chọn tại màn hình xem chi tiết hóa đơn khi người dùng có nhu cầu tải file. | **Condition:** `[Người dùng chọn xuất PDF]`<br>**Extension Point:** `[Hiển thị chi tiết hóa đơn]` | **GIỮ EXTEND** |
| **3** | Bộ lọc hóa đơn | `UC-BILL-LIST` | **Không có (Luồng phụ)** | Bộ lọc theo kỳ/dịch vụ/trạng thái là luồng sự kiện phụ (Filter Sub-flow) bên trong `UC-BILL-LIST`, không tách thành UC riêng. | N/A | **NẰM TRONG MAIN FLOW** |
| **4** | Phân rã bậc giá | `UC-BILL-DETAIL` | **Không có (Cấu trúc dữ liệu)** | Bảng phân rã bậc giá (`tier_breakdown`) là thành phần dữ liệu mặc định trong nội dung chi tiết hóa đơn, không tách thành UC include riêng. | N/A | **NẰM TRONG MAIN FLOW** |
