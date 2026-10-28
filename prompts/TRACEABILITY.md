# Yêu cầu → sản phẩm → căn cứ kiểm tra

Đây là các liên kết hậu kiểm ở mốc dc19327, không phải chứng minh tác giả từng dòng hay kết quả test mới. Tên file là sản phẩm liên quan; ngày trong tên tài liệu không tự chứng minh ngày chạy AI. Chi tiết trạng thái/nguồn trong manifest.json.

## REQ-001 — EXACT_EXCERPT

- Yêu cầu: [req-001-project-review.md](01-requirements/req-001-project-review.md).
- Sản phẩm: [docs/replanning/2026-10-27-phan-tich-va-quy-hoach-v2.md](../docs/replanning/2026-10-27-phan-tich-va-quy-hoach-v2.md), [docs/replanning/V2-MASTER-PLAN-IMPROVED.md](../docs/replanning/V2-MASTER-PLAN-IMPROVED.md)
- Kiểm tra: Xem giới hạn prompt; không gắn kết quả pass riêng.
- Giới hạn: Các tài liệu quy hoạch là đầu ra liên quan đã lưu; không xác minh được ngày gửi hay nguyên bản đầy đủ của phiên phân tích.

## REQ-002 — EXACT_EXCERPT

- Yêu cầu: [req-002-real-data.md](01-requirements/req-002-real-data.md).
- Sản phẩm: [docker-compose.yml](../docker-compose.yml), [backend/app/db.py](../backend/app/db.py), [backend/app/billing_service.py](../backend/app/billing_service.py)
- Kiểm tra: [backend/tests/test_docker_bootstrap.py](../backend/tests/test_docker_bootstrap.py)
- Giới hạn: Runtime dùng PostgreSQL; test có fixture riêng là hợp lệ. Không suy diễn rằng mọi số ví dụ hoặc fixture đều bị cấm.

## PLAN-001 — EXACT_EXCERPT

- Yêu cầu: [plan-001-sdlc.md](02-planning/plan-001-sdlc.md).
- Sản phẩm: [docs/sdlc/SDLC-MASTER-PLAN.md](../docs/sdlc/SDLC-MASTER-PLAN.md), [docs/sdlc/SDLC-REQUIREMENTS-TRACEABILITY.md](../docs/sdlc/SDLC-REQUIREMENTS-TRACEABILITY.md), [docs/replanning/2026-10-27-backlog-v2.md](../docs/replanning/2026-10-27-backlog-v2.md)
- Kiểm tra: Xem giới hạn prompt; không gắn kết quả pass riêng.
- Giới hạn: Kế hoạch không phải chứng nhận mọi hạng mục đã triển khai hoặc nghiệm thu.

## PLAN-002 — EXACT_EXCERPT

- Yêu cầu: [plan-002-checkpoint.md](02-planning/plan-002-checkpoint.md).
- Sản phẩm: [IMPLEMENTATION_PROGRESS.md](../IMPLEMENTATION_PROGRESS.md)
- Kiểm tra: Xem giới hạn prompt; không gắn kết quả pass riêng.
- Giới hạn: Nhật ký do quá trình thực hiện ghi nhận; không phải transcript bất biến hay dữ liệu đo độc lập.

## DES-001 — VERBATIM_FILE

- Yêu cầu: [des-001-usecase-preserved.md](03-design/des-001-usecase-preserved.md).
- Sản phẩm: [docs/design/diagram-manifest.json](../docs/design/diagram-manifest.json), [docs/design/render-report.json](../docs/design/render-report.json), [docs/uml/specs/use-case-specifications.md](../docs/uml/specs/use-case-specifications.md)
- Kiểm tra: Xem giới hạn prompt; không gắn kết quả pass riêng.
- Giới hạn: Preserved file text, not proof of historical submission; named DOCX input missing at original path.

## DES-002 — EXACT_EXCERPT

- Yêu cầu: [des-002-impeccable-init.md](03-design/des-002-impeccable-init.md).
- Sản phẩm: [docs/replanning/V2-UX-REDESIGN.md](../docs/replanning/V2-UX-REDESIGN.md)
- Kiểm tra: Xem giới hạn prompt; không gắn kết quả pass riêng.
- Giới hạn: Có lệnh người dùng yêu cầu Impeccable; chưa có log đủ xác nhận init hoàn tất hoặc gán toàn bộ UI cho skill này.

## IMP-001 — EXACT_EXCERPT

- Yêu cầu: [imp-001-gemini-images.md](04-implementation/imp-001-gemini-images.md).
- Sản phẩm: [backend/app/ai/multimodal.py](../backend/app/ai/multimodal.py), [backend/app/ai/gemini_structured.py](../backend/app/ai/gemini_structured.py), [frontend/components/invoice-result-details.tsx](../frontend/components/invoice-result-details.tsx)
- Kiểm tra: [backend/tests/test_multimodal.py](../backend/tests/test_multimodal.py), [frontend/tests/multimodal-ui.test.cjs](../frontend/tests/multimodal-ui.test.cjs)
- Giới hạn: Trích riêng câu luồng chính trong kế hoạch ảnh do người dùng cung cấp, không phải toàn bộ plan. Đối chiếu thêm schema/test; không kết luận mọi ảnh thật đều được nhận diện.

## IMP-002 — EXACT_EXCERPT

- Yêu cầu: [imp-002-public-rag.md](04-implementation/imp-002-public-rag.md).
- Sản phẩm: [backend/app/knowledge/service.py](../backend/app/knowledge/service.py), [backend/app/knowledge/crawler.py](../backend/app/knowledge/crawler.py), [backend/app/knowledge/embedding.py](../backend/app/knowledge/embedding.py), [backend/app/knowledge/migrations/001.sql](../backend/app/knowledge/migrations/001.sql), [frontend/components/knowledge-admin.tsx](../frontend/components/knowledge-admin.tsx)
- Kiểm tra: [backend/tests/test_knowledge.py](../backend/tests/test_knowledge.py), [backend/tests/test_water_knowledge.py](../backend/tests/test_water_knowledge.py)
- Giới hạn: Trích câu luồng chính trong kế hoạch RAG. Bộ 50 câu hỏi/top-5 90% trong kế hoạch chưa có bằng chứng đã nghiệm thu đủ; không biến thành kết quả đạt.

## TEST-001 — EXACT_EXCERPT

- Yêu cầu: [test-001-five-layers.md](05-testing/test-001-five-layers.md).
- Sản phẩm: [docs/sdlc/SDLC-TEST-STRATEGY.md](../docs/sdlc/SDLC-TEST-STRATEGY.md), [docs/sdlc/VERIFICATION-GEMINI-MULTIMODAL-2026-10-28.md](../docs/sdlc/VERIFICATION-GEMINI-MULTIMODAL-2026-10-28.md)
- Kiểm tra: [backend/tests/test_multimodal.py](../backend/tests/test_multimodal.py), [frontend/tests/knowledge-ui.test.cjs](../frontend/tests/knowledge-ui.test.cjs)
- Giới hạn: Nguyên văn ghi 3 tầng nhưng liệt kê 5, gồm lỗi chính tả tranform. Chuẩn hóa thành UI/API/server/system/transform. Test tĩnh/TestClient không thay nghiệm thu trình duyệt/live.

## DEP-001 — EXACT_EXCERPT

- Yêu cầu: [dep-001-clone-docker.md](06-deployment/dep-001-clone-docker.md).
- Sản phẩm: [docker-compose.yml](../docker-compose.yml), [backend/app/container_start.py](../backend/app/container_start.py), [backend/app/bootstrap.py](../backend/app/bootstrap.py), [deploy/pgadmin.servers.json](../deploy/pgadmin.servers.json), [DOCKER_GUIDE.md](../DOCKER_GUIDE.md)
- Kiểm tra: [backend/tests/test_docker_bootstrap.py](../backend/tests/test_docker_bootstrap.py)
- Giới hạn: Dữ liệu máy tác giả không đi theo Git. Gemini cần key riêng; bootstrap nguồn không đồng nghĩa đã có nội dung RAG. Lượt test clone/volume được ghi trong nhật ký, không có raw transcript công khai.

## DEP-002 — EXACT_EXCERPT

- Yêu cầu: [dep-002-clean-push.md](06-deployment/dep-002-clean-push.md).
- Sản phẩm: [.gitignore](../.gitignore), [scripts/repo_audit.py](../scripts/repo_audit.py), [IMPLEMENTATION_PROGRESS.md](../IMPLEMENTATION_PROGRESS.md)
- Kiểm tra: Xem giới hạn prompt; không gắn kết quả pass riêng.
- Giới hạn: Commit ab8fc26 loại file local/agent thừa. Không chép key cũ vào bằng chứng; xóa ở tip không xóa lịch sử Git. Bản tổng hợp này chỉ cho phép .agents đã chọn lọc.

## OPT-001 — EXACT_EXCERPT

- Yêu cầu: [opt-001-free-key.md](07-optimization/opt-001-free-key.md).
- Sản phẩm: [backend/app/ai/quota.py](../backend/app/ai/quota.py), [backend/app/ai/gemini_structured.py](../backend/app/ai/gemini_structured.py), [backend/app/knowledge/service.py](../backend/app/knowledge/service.py)
- Kiểm tra: [backend/tests/test_knowledge_postgres.py](../backend/tests/test_knowledge_postgres.py)
- Giới hạn: Code/nhật ký ghi cơ chế model cấu hình, giới hạn/cooldown và tìm kiếm suy giảm. Không có benchmark chuẩn để khẳng định % tiết kiệm/tốc độ.

## OPT-002 — EXACT_EXCERPT

- Yêu cầu: [opt-002-no-fake-fallback.md](07-optimization/opt-002-no-fake-fallback.md).
- Sản phẩm: [backend/app/ai/agent.py](../backend/app/ai/agent.py), [backend/app/ai/gemini_structured.py](../backend/app/ai/gemini_structured.py)
- Kiểm tra: [frontend/tests/chat-degraded.test.cjs](../frontend/tests/chat-degraded.test.cjs), [backend/tests/test_multimodal.py](../backend/tests/test_multimodal.py)
- Giới hạn: Ảnh minh họa gốc không được sao chép do có thông tin tài khoản. Offline deterministic behavior còn cho test; production phải xem đường gọi hiện hành.

## OPT-003 — PROPOSED

- Yêu cầu: [opt-003-security-review-proposed.md](07-optimization/opt-003-security-review-proposed.md).
- Sản phẩm: Chưa có (đề xuất).
- Kiểm tra: Xem giới hạn prompt; không gắn kết quả pass riêng.
- Giới hạn: Proposed only; no security-audit result.

## DOC-001 — EXACT_EXCERPT

- Yêu cầu: [doc-001-readme-data.md](08-documentation/doc-001-readme-data.md).
- Sản phẩm: [README.md](../README.md), [DOCKER_GUIDE.md](../DOCKER_GUIDE.md)
- Kiểm tra: Xem giới hạn prompt; không gắn kết quả pass riêng.
- Giới hạn: Commit dc19327 bổ sung clone-root, migration, named volumes, pgAdmin và backup. Kiểm tra tài liệu không thay kiểm thử restore thực tế.

## DOC-002 — EXACT_EXCERPT

- Yêu cầu: [doc-002-ai-evidence.md](08-documentation/doc-002-ai-evidence.md).
- Sản phẩm: [AI_DEVELOPMENT.md](../AI_DEVELOPMENT.md), [.agents/README.md](../.agents/README.md), [.agents/evidence.json](../.agents/evidence.json), [prompts/README.md](../prompts/README.md)
- Kiểm tra: Xem giới hạn prompt; không gắn kết quả pass riêng.
- Giới hạn: Trích từ yêu cầu hiện tại; bộ tài liệu đang được tổng hợp ngày 29/10/2026, không phải đã tồn tại từ đầu đồ án.
