# Tài nguyên và Hướng dẫn Sơ đồ Hệ thống (SDLC Diagrams)

Tài liệu này tổng hợp các kỹ năng (Agent Skills), quy tắc thiết kế và danh mục sơ đồ phục vụ toàn bộ vòng đời phát triển phần mềm (SDLC) của dự án **Hệ thống quản lý hóa đơn điện nước hộ gia đình tích hợp AI (Nhà Mình)**.

---

## 1. Danh mục Agent Skills hỗ trợ Sơ đồ

| Skill | Vị trí | Mục đích & Công việc | Định dạng đầu ra |
|---|---|---|---|
| **sdlc-diagrams** | [`sdlc-diagrams/SKILL.md`](sdlc-diagrams/SKILL.md) | Workflow tổng thể dẫn xuất sơ đồ từ yêu cầu SRS và source code thực tế | Quy chuẩn đa mô hình |
| **uml-usecase-generator** | [`../skills/uml-usecase-generator/SKILL.md`](../skills/uml-usecase-generator/SKILL.md) | Sinh sơ đồ ca sử dụng chuẩn hóa 12 Use Case cốt lõi cho hệ thống Nhà Mình | PlantUML, Mermaid |
| **uml-use-case** | [`../skills/uml-use-case/SKILL.md`](../skills/uml-use-case/SKILL.md) | Phân tích Actor, Goal, System Boundary, `<<include>>`, `<<extend>>`, đặc tả UC | PlantUML `.puml`, Specs `.md` |
| **uml-code-tracer** | [`../skills/uml-code-tracer/SKILL.md`](../skills/uml-code-tracer/SKILL.md) | Trace trực tiếp từ FastAPI, SQLAlchemy sang Sequence, Class, Activity, State | PlantUML `.puml` |
| **architecture-c4** | [`../skills/architecture-c4/SKILL.md`](../skills/architecture-c4/SKILL.md) | Thiết kế kiến trúc C4 (Context, Container, Component, Deployment), Mermaid ERD | PlantUML C4, Mermaid ERD |
| **diagram-design** | [`../skills/diagram-design/SKILL.md`](../skills/diagram-design/SKILL.md) | Thiết kế sơ đồ kiến trúc nâng cao, Data Flow, Flowchart, Timeline, UI layout | HTML/SVG/DrawIO/Mermaid |
| **diagram-renderer** | [`../skills/diagram-renderer/SKILL.md`](../skills/diagram-renderer/SKILL.md) | Kiểm tra cú pháp, audit metadata minh chứng và render tự động sang SVG/PNG | Báo cáo audit, SVG/PNG |

---

## 2. Bản đồ Sơ đồ SDLC đã xây dựng trong Dự án

Toàn bộ sơ đồ được phân loại rõ ràng theo góc nhìn:
- **As-Is:** Phản ánh chính xác hiện trạng mã nguồn (Source code, DB schema, Docker Compose, API Routers).
- **As-Designed:** Thể hiện yêu cầu thiết kế nghiệp vụ và mục tiêu tương lai (SRS).

### A. Sơ đồ Ca sử dụng (UML Use Case Diagrams)
- **Tổng quan 12 Ca sử dụng chuẩn:** [`docs/uml/sources/usecase/system_overview/`](../../docs/uml/sources/usecase/system_overview/)
- **Đặc tả chi tiết Use Case:** [`docs/uml/specs/use-case-specifications.md`](../../docs/uml/specs/use-case-specifications.md)
- **Phân rã theo phân hệ:**
  - Xác thực & Tài khoản: [`docs/uml/sources/usecase/auth/`](../../docs/uml/sources/usecase/auth/)
  - Quản lý Hộ gia đình & Thành viên: [`docs/uml/sources/usecase/household/`](../../docs/uml/sources/usecase/household/)
  - Quản lý Công tơ & Chỉ số: [`docs/uml/sources/usecase/meter/`](../../docs/uml/sources/usecase/meter/)
  - Hóa đơn & Biểu giá EVN/Nước: [`docs/uml/sources/usecase/billing/`](../../docs/uml/sources/usecase/billing/)
  - Trợ lý AI & Thống kê thông minh: [`docs/uml/sources/usecase/ai_statistics/`](../../docs/uml/sources/usecase/ai_statistics/)
  - Quản trị viên hệ thống: [`docs/uml/sources/usecase/admin/`](../../docs/uml/sources/usecase/admin/)

### B. Sơ đồ Tuần tự (UML Sequence Diagrams)
- **Luồng nhận diện hóa đơn Multimodal AI:** [`docs/diagrams/as-is/sequence/`](../../docs/diagrams/as-is/sequence/)
- **Luồng tra cứu hỏi đáp RAG Tri thức công khai:** [`docs/uml/sources/sequence/ai_statistics/`](../../docs/uml/sources/sequence/ai_statistics/)
- **Luồng ghi chỉ số và tính tiền tự động:** [`docs/uml/sources/sequence/billing/`](../../docs/uml/sources/sequence/billing/)
- **Luồng xác thực JWT Refresh Token kép:** [`docs/uml/sources/sequence/auth/`](../../docs/uml/sources/sequence/auth/)

### C. Sơ đồ Hoạt động & Luồng xử lý (Activity Diagrams & Flowcharts)
- **Quy trình ghi chỉ số và chốt hóa đơn:** [`docs/diagrams/as-is/activity/`](../../docs/diagrams/as-is/activity/)
- **Quy trình fallback an toàn khi Gemini API quá tải hoặc offline:** Tham chiếu [`prompts/07-optimization/opt-002-no-fake-fallback.md`](../../prompts/07-optimization/opt-002-no-fake-fallback.md)

### D. Sơ đồ Lớp (UML Class Diagrams)
- **Cấu trúc Domain Models & Schemas:** [`docs/diagrams/as-is/class/`](../../docs/diagrams/as-is/class/)
  - Phản ánh các schema Pydantic (`backend/app/schemas.py`) và ORM Models (`backend/app/models.py`).

### E. Sơ đồ Thực thể Liên kết (Entity Relationship Diagram - ERD)
- **Physical Database Schema (PostgreSQL):** [`docs/diagrams/as-is/c4/erd-database-schema.mmd`](../../docs/diagrams/as-is/c4/erd-database-schema.mmd)
  - Thể hiện đầy đủ các bảng: `users`, `households`, `household_members`, `utility_accounts`, `meters`, `readings`, `billing_periods`, `bills`, `bill_items`, `payments`, `ai_analysis`, `knowledge_documents`, `knowledge_embeddings`.

### F. Sơ đồ Luồng Dữ liệu (Data Flow Diagrams - DFD)
- **DFD Mức 0 (Context Diagram):** Tương tác giữa Hộ gia đình, Nhân viên EVN/Nước, Quản trị viên và Nền tảng Nhà Mình.
- **DFD Mức 1 (Decomposition):** Phân luồng dữ liệu giữa Tiếp nhận dữ liệu, Động cơ tính cước EVN, Động cơ OCR/RAG AI và Kho lưu trữ PostgreSQL.

### G. Sơ đồ Kiến trúc C4 & Triển khai (C4 Architecture & Deployment)
- **C4 Context & Container:** [`docs/diagrams/as-is/c4/`](../../docs/diagrams/as-is/c4/)
  - Next.js Web App (Port 3108)
  - FastAPI Backend (Port 8108)
  - PostgreSQL Database (Port 5433)
  - pgAdmin Container (Port 5050)
  - Google Gemini API (External Cloud Service)
- **Deployment Diagram:** [`docs/diagrams/as-is/deployment/`](../../docs/diagrams/as-is/deployment/)
  - Khối Docker Compose, volume gắn ngoài, network cô lập.

---

## 3. Quy chuẩn mô hình hóa dành cho AI Agent

1. **System Boundary rõ ràng:** Mọi Actor nằm ngoài khung hệ thống. Không đưa Database vào vai trò Actor nghiệp vụ.
2. **Quy tắc quan hệ Use Case:**
   - `<<include>>`: Hành vi dùng chung BẮT BUỘC thực thi. Mũi tên đứt nét từ use case gọi đến use case được gọi.
   - `<<extend>>`: Hành vi MỞ RỘNG có điều kiện tại extension point. Mũi tên đứt nét từ use case mở rộng trỏ về use case cơ sở.
   - Tuyệt đối không dùng `<<include>> Login` bừa bãi cho mọi ca sử dụng; xác thực là điều kiện tiên quyết (Precondition).
3. **Mã nguồn sửa được (Editable Sources):**
   - Lưu trữ dạng văn bản thuần: `.puml` (PlantUML) hoặc `.mmd` (Mermaid).
   - Đặt alias bằng ký tự ASCII và nhãn hiển thị bằng tiếng Việt UTF-8.

---

## 4. Hướng dẫn Render Sơ đồ

Để biên dịch các sơ đồ `.puml` và `.mmd` sang ảnh SVG/PNG để đưa vào báo cáo đồ án:

### Sử dụng Script kiểm tra & render tự động
```bash
# Kiểm tra metadata và cú pháp
python scripts/check_ai_evidence.py

# Xem trợ giúp script render (nếu có môi trường Java/PlantUML)
python .agents/diagrams/legacy-bundle/diagram-renderer/scripts/render_diagrams.py --help
```

### Sử dụng PlantUML CLI hoặc VS Code Extension
- Cài extension **PlantUML** trong VS Code / IDE.
- Mở file `.puml` bất kỳ trong `docs/uml/sources/` hoặc `docs/diagrams/` và nhấn `Alt + D` để xem trước hoặc render trực tiếp.
- Đối với Mermaid `.mmd`: Sử dụng extension **Mermaid Preview** hoặc render trực tiếp trên GitHub Markdown.
