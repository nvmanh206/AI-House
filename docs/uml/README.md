# BỘ SƠ ĐỒ VÀ THIẾT KẾ UMD/UML (UML DIAGRAM REPOSITORY)
## Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia Đình tích hợp AI (Nhà Mình)

---

## 1. Cấu trúc Thư mục Thiết kế

```
docs/
├── design/
│   ├── use-case-catalog.md          # Master Catalog 25 Use Cases tiếng Việt
│   ├── system-inventory.md          # Kho danh mục API Router, ORM Model, Service
│   ├── design-report.md             # Báo cáo Phủ phân hệ, Bảng kiểm duyệt quan hệ & Layout audit
│   ├── traceability.md              # Ma trận TRACEABILITY FR/NFR -> UC -> Code -> Test
│   ├── conflicts-and-assumptions.md # Báo cáo Mâu thuẫn DOCX vs Code & Giả định thiết kế
│   └── diagram-manifest.json        # File manifest kiểm duyệt 44 sơ đồ (JSON format)
└── uml/
    ├── README.md                    # Hướng dẫn sử dụng bộ sơ đồ UML
    ├── specs/
    │   └── use-case-specifications.md# Đặc tả chi tiết 25 Use Cases nghiệp vụ
    ├── sources/                     # File mã nguồn PlantUML (.puml)
    │   ├── usecase/                 # 19 Sơ đồ Use Case theo phân hệ & tổng quan
    │   └── sequence/                # 25 Sơ đồ Trình tự (Sequence) theo 25 UCs
    └── images/                      # Ảnh sơ đồ đã xuất (.png và .svg)
        ├── usecase/                 # 19 Ảnh PNG và 19 Ảnh SVG Use Case
        └── sequence/                # 25 Ảnh PNG và 25 Ảnh SVG Sequence
```

---

## 2. Hướng dẫn Biên dịch & Xuất ảnh Sơ đồ

Để tự động kiểm tra cú pháp và render lại toàn bộ sơ đồ ra hai định dạng **PNG** và **SVG**, hãy chạy lệnh Python sau từ thư mục gốc dự án:

```bash
py -3 .agents/skills/diagram-renderer/scripts/render_diagrams.py \
  --project . \
  --input docs/uml/sources \
  --plantuml-jar C:\Users\Admin\AppData\Local\Temp\plantuml.jar \
  --format both \
  --report docs/design/render-report.json
```

Sau khi render xong, tự động đồng bộ ảnh sang thư mục `docs/uml/images/`:

```bash
py -3 -c "import os, glob, shutil; [shutil.copy2(src, os.path.join('docs/uml/images', os.path.relpath(src, 'docs/uml/sources'))) for src in glob.glob('docs/uml/sources/**/*.png', recursive=True) + glob.glob('docs/uml/sources/**/*.svg', recursive=True)]"
```

---

## 3. Trạng thái Kiểm định (Audit Status)
- **Tổng số Use Cases Nghiệp vụ:** 25 Use Cases
- **Tổng số Sơ đồ PlantUML:** 44 Sơ đồ
- **Tỷ lệ Render Thành công:** 100% PASS (44 PNG, 44 SVG, 0 zero-byte errors)
- **Chuẩn Bố cục:** Strict Orthogonal (`linetype ortho`), font chữ tiếng Việt rõ nét, mã UC & Tên hiển thị trực quan.
