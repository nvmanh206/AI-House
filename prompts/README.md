# Kho Lưu trữ Prompt theo 8 Giai đoạn SDLC — Nhà Mình

Thư mục `prompts/` lưu trữ toàn bộ các câu lệnh (prompts), chỉ dẫn và yêu cầu kỹ thuật đã được sử dụng để điều phối các **AI Coding Agent** (như Google Antigravity, OpenAI Codex, Claude Code) trong suốt quá trình xây dựng đồ án **Hệ thống quản lý hóa đơn điện nước hộ gia đình tích hợp AI (Nhà Minh)**.

Đọc [Minh chứng Tổng quan (AI_DEVELOPMENT.md)](../AI_DEVELOPMENT.md) và [Ma trận Truy vết Toàn diện (TRACEABILITY.md)](TRACEABILITY.md).

---

## 1. Cấu trúc Tổ chức Thư mục Prompts

Các prompt được tổ chức khoa học theo 8 giai đoạn của Vòng đời Phát triển Phần mềm (SDLC):

```text
prompts/
├── 01-requirements/       # Phân tích yêu cầu, phạm vi và dữ liệu thực tế
│   ├── req-001-project-review.md
│   └── req-002-real-data.md
├── 02-planning/           # Lập kế hoạch tổng thể, chia backlog và nhật ký
│   ├── plan-001-sdlc.md
│   └── plan-002-checkpoint.md
├── 03-design/             # Thiết kế 12 Use Case, UI/UX và Kiến trúc hệ thống
│   ├── des-001-usecase-preserved.md
│   └── des-002-impeccable-init.md
├── 04-implementation/     # Lập trình Gemini Multimodal và RAG pgvector
│   ├── imp-001-gemini-images.md
│   └── imp-002-public-rag.md
├── 05-testing/            # Chiến lược kiểm thử 5 tầng (UI/API/Server/System/Transform)
│   └── test-001-five-layers.md
├── 06-deployment/         # Docker hóa 1 lệnh khởi động và dọn dẹp mã nguồn
│   ├── dep-001-clone-docker.md
│   └── dep-002-clean-push.md
├── 07-optimization/       # Quản trị Quota Free Key, chống ảo giác và bảo mật
│   ├── opt-001-free-key.md
│   ├── opt-002-no-fake-fallback.md
│   └── opt-003-security-review-proposed.md
├── 08-documentation/      # Hướng dẫn vận hành Docker và tổng hợp minh chứng AI
│   ├── doc-001-readme-data.md
│   └── doc-002-ai-evidence.md
├── TRACEABILITY.md        # Ma trận liên kết Yêu cầu → Prompt → Sản phẩm → Kiểm tra
├── manifest.json          # Manifest kỹ thuật máy đọc được (SHA-256, mốc git)
├── sources/               # Nguồn trích đoạn người dùng được khử dữ liệu nhạy cảm
└── README.md              # Tài liệu chỉ dẫn này
```

---

## 2. Bảng Danh mục Prompts qua 8 Giai đoạn SDLC

| Giai đoạn SDLC | Mã ID | Tên Nhiệm vụ Prompt | Trạng thái Minh chứng | Công cụ AI Sử dụng | Sản phẩm Mã nguồn & Tài liệu Liên kết |
|---|---|---|---|---|---|
| **01. Requirements** | [REQ-001](01-requirements/req-001-project-review.md) | Phân tích lại tổng thể hệ thống | `EXACT_EXCERPT` | Codex / AI Agent | [`docs/replanning/2026-10-27-phan-tich-va-quy-hoach-v2.md`](../docs/replanning/2026-10-27-phan-tich-va-quy-hoach-v2.md) |
| | [REQ-002](01-requirements/req-002-real-data.md) | Chuyển đổi dữ liệu mẫu sang dữ liệu thực | `EXACT_EXCERPT` | Codex / AI Agent | [`docker-compose.yml`](../docker-compose.yml), [`backend/app/db.py`](../backend/app/db.py) |
| **02. Planning** | [PLAN-001](02-planning/plan-001-sdlc.md) | Lập kế hoạch tổng thể SDLC | `EXACT_EXCERPT` | Codex / AI Agent | [`docs/sdlc/SDLC-MASTER-PLAN.md`](../docs/sdlc/SDLC-MASTER-PLAN.md) |
| | [PLAN-002](02-planning/plan-002-checkpoint.md) | Ghi nhận tiến độ và Checkpoint kỹ thuật | `EXACT_EXCERPT` | Codex / AI Agent | [`IMPLEMENTATION_PROGRESS.md`](../IMPLEMENTATION_PROGRESS.md) |
| **03. Design** | [DES-001](03-design/des-001-usecase-preserved.md) | Chuẩn hóa 12 Ca sử dụng cốt lõi | `VERBATIM_FILE` | Codex / AI Agent | [`docs/uml/specs/use-case-specifications.md`](../docs/uml/specs/use-case-specifications.md) |
| | [DES-002](03-design/des-002-impeccable-init.md) | Khởi tạo Design System & UI/UX | `EXACT_EXCERPT` | Impeccable / UI Agent | [`docs/replanning/V2-UX-REDESIGN.md`](../docs/replanning/V2-UX-REDESIGN.md) |
| **04. Implementation** | [IMP-001](04-implementation/imp-001-gemini-images.md) | Xây dựng pipeline Gemini Multimodal OCR | `EXACT_EXCERPT` | Codex / AI Agent | [`backend/app/ai/multimodal.py`](../backend/app/ai/multimodal.py) |
| | [IMP-002](04-implementation/imp-002-public-rag.md) | Xây dựng RAG Tri thức Biểu giá với pgvector | `EXACT_EXCERPT` | Codex / AI Agent | [`backend/app/knowledge/service.py`](../backend/app/knowledge/service.py) |
| **05. Testing** | [TEST-001](05-testing/test-001-five-layers.md) | Chiến lược Kiểm thử Toàn diện 5 Tầng | `EXACT_EXCERPT` | Codex / AI Agent | [`docs/sdlc/SDLC-TEST-STRATEGY.md`](../docs/sdlc/SDLC-TEST-STRATEGY.md) |
| **06. Deployment** | [DEP-001](06-deployment/dep-001-clone-docker.md) | Docker hóa toàn bộ môi trường (1 lệnh) | `EXACT_EXCERPT` | Codex / AI Agent | [`docker-compose.yml`](../docker-compose.yml), [`DOCKER_GUIDE.md`](../DOCKER_GUIDE.md) |
| | [DEP-002](06-deployment/dep-002-clean-push.md) | Dọn dẹp sạch mã nguồn trước Git push | `EXACT_EXCERPT` | Codex / AI Agent | [`.gitignore`](../.gitignore), [`scripts/repo_audit.py`](../scripts/repo_audit.py) |
| **07. Optimization** | [OPT-001](07-optimization/opt-001-free-key.md) | Quản lý Quota Free Key & Cooldown | `EXACT_EXCERPT` | Codex / AI Agent | [`backend/app/ai/quota.py`](../backend/app/ai/quota.py) |
| | [OPT-002](07-optimization/opt-002-no-fake-fallback.md) | Chống ảo giác (No-fake-fallback) | `EXACT_EXCERPT` | Codex / AI Agent | [`backend/app/ai/agent.py`](../backend/app/ai/agent.py) |
| | [OPT-003](07-optimization/opt-003-security-review-proposed.md) | Rà soát Bảo mật & Phân quyền Hộ | `PROPOSED` | Codex / AI Agent | [`backend/app/ai/multimodal.py`](../backend/app/ai/multimodal.py) |
| **08. Documentation** | [DOC-001](08-documentation/doc-001-readme-data.md) | Tài liệu hóa Triển khai & CSDL | `EXACT_EXCERPT` | Codex / AI Agent | [`README.md`](../README.md), [`DOCKER_GUIDE.md`](../DOCKER_GUIDE.md) |
| | [DOC-002](08-documentation/doc-002-ai-evidence.md) | Chuẩn hóa Toàn bộ Minh chứng AI | `EXACT_EXCERPT` | Antigravity / Codex | [`AI_DEVELOPMENT.md`](../AI_DEVELOPMENT.md), [`.agents/`](../.agents/README.md) |

---

## 3. Quy chuẩn Định dạng File Prompt

Mỗi file prompt `.md` trong thư mục này được cấu trúc thống nhất:
1. **YAML Frontmatter:**
   - `id`: Mã định danh duy nhất (ví dụ: `REQ-001`, `IMP-001`).
   - `status`: Phân loại minh chứng (`VERBATIM_FILE`, `EXACT_EXCERPT`, `RECONSTRUCTED`, `PROPOSED`).
   - `collected_on`: Ngày thu thập và chuẩn hóa dữ liệu.
2. **Tiêu đề & Mục đích:** Nêu rõ bối cảnh và mục tiêu kỹ thuật cần đạt được.
3. **Nguồn & Công cụ AI:** Ghi nhận nguồn gốc và công cụ AI hỗ trợ thực hiện.
4. **Nội dung yêu cầu:** Trích đoạn nguyên văn hoặc tái dựng chính xác prompt đã gửi cho AI.
5. **Sản phẩm liên quan:** Danh sách đường dẫn file mã nguồn, file cấu hình hoặc tài liệu được sinh ra hoặc sửa đổi.
6. **Kiểm tra liên quan:** Danh sách các test suite hoặc quy trình xác minh tính đúng đắn.
7. **Giới hạn & Lưu ý học thuật:** Các ghi chú minh bạch về phạm vi và tính khách quan của dữ liệu.

---

## 4. Kiểm tra Toàn vẹn Tự động

Để bảo đảm toàn bộ liên kết nội bộ, cấu trúc frontmatter và an toàn dữ liệu không bị lỗi, chạy công cụ kiểm tra tự động:

```bash
python scripts/check_ai_evidence.py
```
