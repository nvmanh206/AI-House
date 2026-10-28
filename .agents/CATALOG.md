# Danh mục skill và trạng thái

Ngày thu thập: 29/10/2026. Skill đọc trong phiên hội thoại là căn cứ về việc truy cập hướng dẫn; không chứng minh mọi bước đã được thực thi. Xem [manifest nguồn/hash](evidence.json).

## Tài nguyên ngoài dự án

### EXT-01 — diagram-design

- Trạng thái: `INSTALLATION_RECORD_ONLY`.
- Căn cứ: Local skills-lock.json identifies source and skillPath; imported metadata only, not full personal lockfile.
- GitHub: [https://github.com/cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design).
- Giấy phép upstream: [MIT](https://github.com/cathrynlavery/diagram-design/blob/main/LICENSE).
- Giới hạn: No pinned upstream commit or invocation log; installation is not execution.

### EXT-02 — impeccable

- Trạng thái: `USER_REQUESTED`.
- Căn cứ: Prompt DES-002 requests /impeccable init; local SKILL header read during collection.
- GitHub: [https://github.com/pbakaus/impeccable](https://github.com/pbakaus/impeccable).
- Giấy phép upstream: [Apache-2.0](https://github.com/pbakaus/impeccable/blob/main/LICENSE).
- Giới hạn: Does not prove initialization completed or local version equals current upstream.

### EXT-03 — systematic-debugging

- Trạng thái: `LOCAL_READ_IN_CONVERSATION`.
- Căn cứ: Visible tool read and debugging commentary in water-ingestion conversation; related code/tests at ab8fc26.
- GitHub: [https://github.com/obra/superpowers](https://github.com/obra/superpowers).
- Giấy phép upstream: [MIT](https://github.com/obra/superpowers/blob/main/LICENSE).
- Giới hạn: Repository is an upstream reference; local snapshot equivalence to upstream not verified.

### EXT-04 — verification-before-completion

- Trạng thái: `LOCAL_READ_IN_CONVERSATION`.
- Căn cứ: Visible tool read before release checks in available conversation; independent proof of all prescribed steps is not claimed.
- GitHub: [https://github.com/obra/superpowers](https://github.com/obra/superpowers).
- Giấy phép upstream: [MIT](https://github.com/obra/superpowers/blob/main/LICENSE).
- Giới hạn: Local snapshot equivalence to upstream not verified.

### EXT-05 — writing-plans

- Trạng thái: `AVAILABLE_SOURCE`.
- Căn cứ: Local skill available and docs/superpowers/plans/2026-10-29-portable-docker.md exists; no authenticated per-skill execution log archived.
- GitHub: [https://github.com/obra/superpowers](https://github.com/obra/superpowers).
- Giấy phép upstream: [MIT](https://github.com/obra/superpowers/blob/main/LICENSE).
- Giới hạn: A plan artifact alone does not establish this skill was executed.

### EXT-06 — skill-creator

- Trạng thái: `LOCAL_READ_CURRENT_COLLECTION`.
- Căn cứ: Bundled skill-creator SKILL.md read during this evidence-authoring request.
- GitHub: [https://github.com/openai/skills](https://github.com/openai/skills).
- Giấy phép upstream: [PER_SKILL_LICENSE_NOT_VERIFIED](https://github.com/openai/skills#license).
- Giới hạn: Exact upstream path/revision/license of local snapshot not established; no third-party contents vendored.

### LOCAL-01 — ponytail

- Trạng thái: `LOCAL_READ_IN_CONVERSATION`.
- Căn cứ: Local SKILL.md read during water ingestion; no verified upstream metadata recovered.
- GitHub: chưa xác minh; không tự gán nguồn.
- Giấy phép: chưa xác định; không sao chép nội dung skill.
- Giới hạn: Do not invent GitHub source or license; not copied into this repo.

### LOCAL-02 — writing-for-agents

- Trạng thái: `LOCAL_READ_CURRENT_COLLECTION`.
- Căn cứ: Local SKILL.md and SKILL-MECHANICS.md read for current documentation.
- GitHub: chưa xác minh; không tự gán nguồn.
- Giấy phép: chưa xác định; không sao chép nội dung skill.
- Giới hạn: No verified upstream metadata recovered; local contents not redistributed.

## Workflow dự án chuẩn hóa mới

Các workflow sau được viết mới, không phải bản sao skill ngoài và chưa có minh chứng từng được dùng trong quá khứ:

- [nha-minh-documentation-evidence](skills/nha-minh-documentation-evidence/SKILL.md) — PROPOSED.
- [nha-minh-five-layer-testing](skills/nha-minh-five-layer-testing/SKILL.md) — PROPOSED.
- [nha-minh-implementation](skills/nha-minh-implementation/SKILL.md) — PROPOSED.
- [nha-minh-requirements-planning](skills/nha-minh-requirements-planning/SKILL.md) — PROPOSED.
- [nha-minh-security-optimization](skills/nha-minh-security-optimization/SKILL.md) — PROPOSED.
- [sdlc-diagrams](diagrams/sdlc-diagrams/SKILL.md) — PROPOSED.

## Bundle sơ đồ khôi phục

Xem [nguồn và giấy phép chưa khai báo](diagrams/legacy-bundle/PROVENANCE.md). Năm skill từ dictionary bộ cài: system-design-orchestrator, uml-use-case, uml-code-tracer, architecture-c4, diagram-renderer. Đây là RECONSTRUCTED_FROM_INSTALLER, không phải bản đã cài được xác nhận nguyên trạng.

## Cài đặt / sử dụng

- Workflow mới: agent đọc trực tiếp SKILL.md và rule bằng đường dẫn từ gốc repo. Nếu host hỗ trợ thư mục skill riêng, sao chép đúng thư mục nha-minh-* theo hướng dẫn host; không cần sửa source ứng dụng. Không giả định mọi host tự quét .agents/diagrams.
- Diagram Design: upstream hướng dẫn `npx skills add cathrynlavery/diagram-design`; kiểm tra phiên bản/giấy phép trước khi cài, không tự chạy trong lúc chỉ đọc minh chứng.
- Impeccable: upstream hướng dẫn `npx impeccable install`, sau đó `/impeccable init`. Đây là hướng dẫn cài lại, không phải log đã cài/chạy hôm nay.
- Superpowers: chọn hướng dẫn host phù hợp tại [repo chính thức](https://github.com/obra/superpowers#installation); không áp lệnh của Claude cho Codex một cách mặc định.
- OpenAI skills: đọc [catalog chính thức](https://github.com/openai/skills) và LICENSE.txt của skill riêng; không coi toàn bộ catalog có một giấy phép duy nhất.

Chỉ dẫn/giấy phép upstream được kiểm tra ngày 29/10/2026 và có thể thay đổi; hash local trong manifest không phải upstream commit. Không vendor toàn bộ thư viện skill vào repo này.
