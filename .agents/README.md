# AI Development Resources & Agent Skills — Nhà Mình

Thư mục `.agents/` đóng vai trò là **AI Development Documentation & Evidence Repository** cho đồ án môn **Ứng dụng Trí tuệ nhân tạo**: *Hệ thống quản lý hóa đơn điện nước hộ gia đình tích hợp AI (Nhà Mình)*.

Nơi đây lưu trữ có hệ thống các **Agent Skills**, **Rules phát triển**, **Tài nguyên Sơ đồ** và **Minh chứng ứng dụng AI Coding Agent** xuyên suốt toàn bộ vòng đời phát triển phần mềm (SDLC).

---

## 1. Cấu trúc thư mục `.agents/`

```text
.agents/
├── skills/                     # 19 Agent Skills chuẩn hóa theo định dạng SKILL.md
│   ├── nha-minh-*/             # Các workflow đặc thù phát triển hệ thống Nhà Mình
│   ├── system-design-*/        # Điều phối phân tích hệ thống và mô hình hóa
│   ├── architecture-c4/        # Thiết kế kiến trúc C4, CSDL PostgreSQL, ERD
│   ├── uml-*/                  # Thiết kế Use Case, Code Tracer, Spec Generator
│   ├── ui-*/                   # Thiết kế UI/UX, Design System, Tailwind, shadcn/ui
│   └── diagram-*/              # Thiết kế và kết xuất sơ đồ hệ thống
├── rules/                      # 5 bộ quy tắc chuẩn hóa định hướng AI Coding Agent
│   ├── 01-coding-conventions.md# Chuẩn code TypeScript/React & Python/FastAPI
│   ├── 02-architecture.md      # Quy tắc phân tầng, cô lập dữ liệu và tích hợp Gemini
│   ├── 03-sdlc.md              # Quy trình SDLC, lập kế hoạch và truy vết thay đổi
│   ├── 04-quality-security.md  # Tiêu chuẩn kiểm thử 5 tầng và bảo mật dữ liệu
│   ├── 05-ai-evidence.md       # Nguyên tắc trung thực học thuật và phân loại minh chứng
│   └── README.md               # Hướng dẫn áp dụng rules cho AI Coding Agent
├── diagrams/                   # Tài nguyên, hướng dẫn và quy tắc vẽ sơ đồ SDLC
│   ├── sdlc-diagrams/          # Workflow tạo sơ đồ chuẩn SDLC
│   ├── legacy-bundle/          # Bundle công cụ phân tích và render sơ đồ
│   └── README.md               # Hướng dẫn chi tiết từng loại sơ đồ trong dự án
├── CATALOG.md                  # Danh mục chi tiết, nguồn gốc GitHub, License upstream
├── evidence.json               # Manifest máy đọc được (SHA-256, mốc commit, trạng thái)
└── README.md                   # Tài liệu chỉ dẫn này
```

---

## 2. Bảng Danh mục 19 Agent Skills theo giai đoạn SDLC

Tất cả các skill đều tuân theo chuẩn `SKILL.md` (chứa YAML Frontmatter gồm `name` và `description`), tương thích hoàn toàn với **Google Antigravity**, **OpenAI Codex**, **Claude Code** và các AI Coding Agent hiện đại.

| Giai đoạn SDLC | Agent Skill | Trạng thái Minh chứng | Mục đích & Trách nhiệm |
|---|---|---|---|
| **Yêu cầu & Kế hoạch** | [`nha-minh-requirements-planning`](skills/nha-minh-requirements-planning/SKILL.md) | `PROPOSED` | Phân tích yêu cầu SRS, phân rã User Story, Acceptance Criteria và lập Backlog |
| **Phân tích Hệ thống** | [`system-design-orchestrator`](skills/system-design-orchestrator/SKILL.md) | `RECONSTRUCTED` | Điều phối tổng thể phân tích hệ thống, lập sơ đồ và kiểm soát tính nhất quán |
| **Kiến trúc & CSDL** | [`architecture-c4`](skills/architecture-c4/SKILL.md) | `RECONSTRUCTED` | Thiết kế kiến trúc C4 Context/Container/Component và lược đồ CSDL ERD |
| **Mô hình hóa Use Case** | [`uml-usecase-generator`](skills/uml-usecase-generator/SKILL.md) | `IN_USE` | Master Skill chuẩn hóa 12 Ca sử dụng cốt lõi của đồ án Nhà Mình |
| **Mô hình hóa Ca sử dụng** | [`uml-use-case`](skills/uml-use-case/SKILL.md) | `RECONSTRUCTED` | Phân tích Actor, Goal, include/extend và viết đặc tả Use Case chi tiết |
| **Trace Code sang UML** | [`uml-code-tracer`](skills/uml-code-tracer/SKILL.md) | `RECONSTRUCTED` | Trace từ mã nguồn thật sang Sequence, Class, Activity và State Diagram |
| **Đồ họa & Sơ đồ** | [`diagram-design`](skills/diagram-design/SKILL.md) | `EXTERNAL_INSTALLED` | Thiết kế sơ đồ đa dạng (flowchart, timeline, quadrant, architecture delta) |
| **Render & Audit Sơ đồ** | [`diagram-renderer`](skills/diagram-renderer/SKILL.md) | `RECONSTRUCTED` | Tự động kiểm tra cú pháp, audit metadata và render sơ đồ sang SVG/PNG |
| **Thiết kế UI/UX** | [`ui-ux-pro-max`](skills/ui-ux-pro-max/SKILL.md) | `ACTIVE` | Cung cấp hệ thống bảng màu, font chữ, UX guideline và biểu đồ giao diện |
| **Styling & Components** | [`ui-styling`](skills/ui-styling/SKILL.md) | `ACTIVE` | Tạo giao diện với Next.js, shadcn/ui, Tailwind CSS và responsive layout |
| **Design System** | [`design-system`](skills/design-system/SKILL.md) | `ACTIVE` | Quản trị Design Tokens 3 lớp (primitive, semantic, component) |
| **Thiết kế Nhận diện** | [`brand`](skills/brand/SKILL.md) | `ACTIVE` | Quản trị tiếng nói thương hiệu và ngôn ngữ thiết kế nhất quán |
| **Đồ họa Trực quan** | [`design`](skills/design/SKILL.md) | `ACTIVE` | Tổng hợp hình ảnh, logo, phối cảnh CIP và biểu đồ |
| **Thiết kế Banner** | [`banner-design`](skills/banner-design/SKILL.md) | `ACTIVE` | Thiết kế banner giới thiệu hệ thống và tài sản hình ảnh |
| **Trình chiếu Báo cáo** | [`slides`](skills/slides/SKILL.md) | `ACTIVE` | Tạo slide trình chiếu HTML/Chart.js chuyên nghiệp phục vụ bảo vệ đồ án |
| **Lập trình Ứng dụng** | [`nha-minh-implementation`](skills/nha-minh-implementation/SKILL.md) | `PROPOSED` | Quy chuẩn code Frontend (Next.js), Backend (FastAPI) và Tích hợp Gemini AI |
| **Kiểm thử 5 Tầng** | [`nha-minh-five-layer-testing`](skills/nha-minh-five-layer-testing/SKILL.md) | `PROPOSED` | Kiểm thử toàn diện: UI → API → Server → System → Data Transform |
| **Bảo mật & Tối ưu** | [`nha-minh-security-optimization`](skills/nha-minh-security-optimization/SKILL.md) | `PROPOSED` | Cô lập hộ gia đình, an toàn crawler RAG, quota Gemini API và hiệu năng |
| **Quản lý Minh chứng** | [`nha-minh-documentation-evidence`](skills/nha-minh-documentation-evidence/SKILL.md) | `PROPOSED` | Ghi nhận prompt, duy trì bảng truy vết Traceability và kiểm toán secret |

---

## 3. Phân loại Minh chứng Học thuật (Evidence Classification)

Nhằm đảm bảo tính **khách quan, trung thực và khoa học** trong đồ án đại học, mọi tài nguyên đều được phân loại trạng thái minh chứng rõ ràng:

1. **`VERBATIM_FILE` / `EXACT_EXCERPT` (Đã sử dụng thực tế):**
   - Nội dung được bảo tồn nguyên văn từ các file cấu hình hoặc trích đoạn hội thoại thực tế của người dùng đã được đối soát qua commit Git.
2. **`LOCAL_READ` / `ACTIVE` / `IN_USE` (Đang sử dụng):**
   - Các skill và rule được nạp và tham chiếu trực tiếp trong các phiên làm việc của AI Coding Agent.
3. **`RECONSTRUCTED` (Tái dựng có căn cứ):**
   - Các tài nguyên được khôi phục từ bộ script cài đặt hoặc nhật ký kỹ thuật, được ghi rõ nguồn gốc và giới hạn.
4. **`PROPOSED` (Đề xuất chuẩn hóa mới):**
   - Các quy chuẩn workflow và hướng dẫn tốt nhất được xây dựng để hoàn thiện hệ thống, chuẩn bị cho các đợt phát triển tiếp theo.

---

## 4. Nguồn gốc Skill bên ngoài & Bản quyền (Upstream Licenses)

Chi tiết được quản lý tại file [`CATALOG.md`](CATALOG.md) và [`evidence.json`](evidence.json):
- **diagram-design:** Upstream [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) — Giấy phép MIT.
- **impeccable:** Upstream [pbakaus/impeccable](https://github.com/pbakaus/impeccable) — Giấy phép Apache-2.0.
- **superpowers:** Upstream [obra/superpowers](https://github.com/obra/superpowers) — Giấy phép MIT.
- **openai/skills:** Upstream [openai/skills](https://github.com/openai/skills) — Giấy phép per-skill.

---

## 5. An toàn và Bảo mật Dữ liệu

- Tuyệt đối **không đưa API key, Bearer token, password, credential, ảnh hóa đơn cá nhân hoặc file `.env` lên Git**.
- Toàn bộ dữ liệu mật được kiểm tra tự động trước mỗi lần commit.
- Để kiểm tra tính hợp lệ toàn diện của tài nguyên minh chứng:

```bash
# Kiểm tra cấu trúc tài liệu minh chứng, liên kết và bí mật
python scripts/check_ai_evidence.py

# Kiểm toán an toàn mã nguồn Git (bảo đảm 0 credential)
python scripts/repo_audit.py
```
