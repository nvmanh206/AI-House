---
id: DES-001
status: VERBATIM_FILE
collected_on: 2026-10-29
---

# Prompt Use Case được lưu trong dự án

**Mục đích:** tách sơ đồ theo chức năng, chuẩn UML và kiểm tra include/extend.

**Nguồn:** [docs/prompt/usecase.md](../../docs/prompt/usecase.md); SHA-256 `8a43b7b9ca190a6e9caaaaf726b956dbc16df9e3c62c71066e6b2eecd5ff34f8`. Nội dung file được giữ nguyên dưới đây. File này không chứng minh nguyên văn đã được gửi cho agent hoặc xác định agent nào thực thi.

**Công cụ:** prompt nhắc system-design-orchestrator, uml-use-case, diagram-renderer; không có log xác nhận host/model gốc.

## Nội dung file nguồn

````text
Update the installed system-design-orchestrator, uml-use-case and
diagram-renderer skills to follow the requirements below, then apply them.

INPUT
Read docs/requirements/project-documentation.docx using the bundled DOCX
extractor. Read paragraphs, tables and relevant embedded images.
Preserve section headings and paragraph/table-cell references.
Report unreadable or ambiguous content; do not invent missing requirements.
Keep the original document and application code unchanged.

SECTION-BY-SECTION OUTPUT
1. Inventory every functional section in the document.
2. Identify its actors, business goals and documented relationships.
3. Produce a separate Use Case diagram for each functional section.
4. Add focused detailed diagrams when a section contains several substantial
   goals. Split crowded diagrams into readable subdiagrams.
5. Keep a coverage table linking each section to its diagrams and source.
6. Describe detailed steps, alternatives and errors in accompanying Use Case
   specifications; avoid turning every internal processing step into an oval.

LOGIN AND REGISTER
- Model Login and Register as separate use cases with distinct IDs.
- Produce separate detailed login.png and register.png images.
- They may appear together in an authentication overview.
- Do not combine them into “Login/Register”.
- Do not connect them with include or extend merely because they share a page.
- If the document lacks their behavior, record the missing details rather
  than inventing a flow.

INCLUDE AND EXTEND
For every proposed relationship, record:
source use case, target use case, relationship type, business justification,
document reference and, for extend, condition and extension point.

- <<include>>: required reused behavior at the defined insertion point.
  Dashed arrow points FROM the including use case TO the included use case.
- <<extend>>: supplementary behavior added at an extension point, potentially
  conditionally. The base use case remains meaningful independently.
  Dashed arrow points FROM the extending use case TO the base use case.
- Do not use these relationships to show chronological order, navigation,
  ordinary validation errors or functional grouping.
- Treat authentication as a precondition where appropriate; do not attach
  “include Login” automatically to every secured operation.
- If the evidence cannot justify a relationship, omit it and document the
  uncertainty. Do not force every diagram to contain include or extend.

STANDARD UML NOTATION
- Human actors: standard UML stick figures, outside the system boundary.
- External software actors: clearly labeled, with a suitable stereotype.
- Use cases: ellipses inside a named rectangular system boundary.
- Actor associations: solid lines, normally without arrowheads.
- Include/extend: dashed dependencies with open arrowheads and exact labels.
- Generalization: hollow triangle toward the parent, only when justified.
- Use mind-map-like spacing and grouping while preserving UML semantics.

ORTHOGONAL AND TIDY LAYOUT
Use this starting configuration for Use Case sources:

left to right direction
skinparam linetype ortho
skinparam nodesep 50
skinparam ranksep 70
skinparam shadowing false
skinparam defaultFontSize 16
skinparam dpi 180

Place primary actors on the left and supporting actors on the right where
this reduces crossings. Align actors and use cases consistently.
Use horizontal/vertical connector segments with 90-degree bends.
Keep connectors clear of ellipses, actor labels and relationship labels.
Avoid ambiguous overlapping lines or decorative shared connector hubs.
Keep each relationship’s endpoints independently understandable.

Use direction hints, spacing and hidden layout constraints only to improve
placement; never change relationship semantics or remove real associations
to make the picture tidier. Comment any hidden layout constraints.
Split diagrams when crossings cannot be resolved cleanly.

EXPORT AND VERIFICATION
Export PNG and SVG into:
docs/uml/images/usecase/<section>/

Keep editable .puml sources in:
docs/uml/sources/usecase/<section>/

Keep evidence, specifications, coverage and relationship-review tables
outside the image folder.

Validate syntax, render, and inspect EVERY exported image.
Check arrow direction, include/extend labels, actor placement, crossings,
clipping and readability. Revise and rerender until these checks pass.
Use the document’s language for business labels.

Orthogonal routing alone does not guarantee a clean layout.
If an engine cannot render the required notation/layout correctly, report
the limitation instead of claiming the image passed.````

## Sản phẩm liên quan

- [Manifest sơ đồ](../../docs/design/diagram-manifest.json)
- [Báo cáo render lịch sử](../../docs/design/render-report.json)
- [Use Case specifications](../../docs/uml/specs/use-case-specifications.md)

**Giới hạn:** đầu vào docs/requirements/project-documentation.docx được prompt nhắc tới chưa có tại đường dẫn đó trong tree hiện tại. Không gán report render là bằng chứng UML đúng nghiệp vụ, đủ input hoặc đã kiểm tra hình ảnh hôm nay.
