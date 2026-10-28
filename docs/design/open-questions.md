# Danh Sách Câu Hỏi Mở & Bằng Chứng Bị Thiếu (Open Questions & Missing Evidence Log)

> Documented according to `system-design-orchestrator` workflow step 3.

## 1. Nguồn Yêu Cầu & Bằng Chứng Chưa Xác Định

| ID | Nhóm câu hỏi | Mô tả chi tiết | Tác động tới thiết kế | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| `OQ-01` | **Yêu cầu Hệ thống Tuyển dụng** | Người dùng gửi câu lệnh mẫu yêu cầu thiết kế "hệ thống tuyển dụng nội bộ" nhưng dự án hiện tại là hệ thống "Nhà Mình - Quản lý hóa đơn điện nước có tích hợp AI". Dự án không có file Sprint/Excel/BRD tuyển dụng. | Không thể tạo sơ đồ Use Case / Sequence cho tuyển dụng dựa trên code thật; chỉ có thể tạo sơ đồ **As-Is** cho hệ thống Hóa đơn Điện Nước hiện tại. | **BLOCKED** |
| `OQ-02` | **Hạn mức Gemini API & Proxy** | Cấu hình Gemini Search Grounding sử dụng direct REST API tới Google. Chưa có cơ chế proxy hóa hạn mức 429 khi quá số lượng truy vấn Search đồng thời. | Thiết kế `as-is` giữ nguyên direct call; thiết kế `as-designed` đề xuất thêm caching layer cho các câu hỏi giá điện/nước phổ biến. | **PROPOSED** |
| `OQ-03` | **Tích hợp Cổng thanh toán thực tế** | V1 thanh toán qua giao diện ghi nhận thủ công (`MANUAL`). Chưa có webhook/IPN callback từ các ngân hàng/cổng thanh toán. | Giữ nguyên Payment model 1-1 trong As-Is ERD; đề xuất Payment Gateway integration trong Gap view. | **PROPOSED** |

---

## 2. Nhật Ký Giả Định Thiết Kế (Design Assumptions)

1. **Giả định 1**: Scope phân tích As-Is lấy toàn bộ mã nguồn `backend/`, `frontend/`, `docs/`, `docker-compose.yml` làm Nguồn Sự Thật Duy Nhất (Single Source of Truth).
2. **Giả định 2**: Giữ nguyên toàn bộ tên Class (`User`, `Household`, `BillingService`, `Agent`...), Cột Database (`final_amount`, `consumption`, `dedupe_key`...) và API Endpoints trong sơ đồ.
3. **Giả định 3**: Các nhãn hiển thị trong sơ đồ UML/PlantUML/Mermaid sử dụng tiếng Việt nghiệp vụ rõ ràng để phục vụ việc đọc hiểu của người dùng.
