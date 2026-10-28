# Nguồn gốc bundle tùy biến

Trạng thái RECONSTRUCTED_FROM_INSTALLER, thu thập 29/10/2026 bằng ast.literal_eval từ dictionary FILES của script cài đặt local; không chạy bộ cài. Hash nguồn nằm trong ../legacy-manifest.json. Script cá nhân không được đưa lên Git.

Gồm system-design-orchestrator, uml-use-case, uml-code-tracer, architecture-c4 và diagram-renderer. Snapshot bộ cài không bảo đảm giống bản đã cài/chỉnh trong mọi agent. Prompt usecase và report render có sản phẩm liên quan, không có transcript đầy đủ xác nhận agent/phiên bản chạy.

GitHub upstream và giấy phép của bundle không được khai báo trong nguồn đã thu thập; không tự gắn MIT/Apache. Lưu như tài nguyên nội bộ do người dùng cung cấp, chưa xác nhận quyền cấp phép lại. Kiểm tra quyền sở hữu trước khi phân phối ngoài phạm vi đồ án.

Đọc SKILL.md từng thư mục. Helper render cần Python, Java, PlantUML/Graphviz theo toolchain. Không tự tải hoặc chạy công cụ. Kiểm tra cú pháp Python không chứng minh đã render sơ đồ mới.
