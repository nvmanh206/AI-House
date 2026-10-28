# Rules cho AI Coding Agent

Chuẩn hóa ngày 29/10/2026, không tự thay system prompt Gemini của sản phẩm.

1. [Coding conventions](01-coding-conventions.md)
2. [Kiến trúc/dữ liệu](02-architecture.md)
3. [SDLC/dấu vết](03-sdlc.md)
4. [Chất lượng/bảo mật](04-quality-security.md)
5. [Minh chứng AI](05-ai-evidence.md)

Rule runtime hiện có tại backend/app/ai/rules/ và instruction tại backend/app/ai/gemini_structured.py. Cần đọc caller thực tế, không mặc định mọi markdown runtime đều được chat hiện tại nạp.

Yêu cầu agent đọc rule bằng đường dẫn phù hợp. Thư mục rules không bảo đảm mọi host agent tự nạp.
