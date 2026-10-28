# Kho tri thức công khai Nhà Mình

Code nằm trong `backend/app/knowledge`. Database `knowledge` chạy trên PostgreSQL 16 + pgvector riêng, `127.0.0.1:5435`. Database nghiệp vụ giữ nguyên. Không đưa ảnh hóa đơn, hồ sơ hoặc chỉ số hộ gia đình vào chỉ mục công khai.

## Khởi tạo

Chạy từ thư mục `website` bằng PowerShell:

```powershell
.\backend\.venv\Scripts\python.exe scripts/knowledge.py prepare
docker compose up -d knowledge-postgres
.\backend\.venv\Scripts\python.exe scripts/knowledge.py migrate
.\backend\.venv\Scripts\python.exe scripts/knowledge.py preflight
.\backend\.venv\Scripts\python.exe scripts/knowledge.py seed
.\backend\.venv\Scripts\python.exe scripts/knowledge.py crawl
```

`prepare` tạo mật khẩu ngẫu nhiên trong `.local/knowledge-password`, cập nhật cấu hình backend và đăng ký pgAdmin. Không in secret. Không chạy `configure_pgadmin.py` cũ sau bước này vì script cũ chỉ đăng ký database nghiệp vụ; chạy lại `knowledge.py prepare` nếu cần khôi phục cấu hình hai server.

Nhập đăng ký vào pgAdmin đang chạy (không replace server cũ):

```powershell
docker exec nha-minh-pgadmin /venv/bin/python3 /pgadmin4/setup.py load-servers /pgadmin4/servers.json --user admin@example.com
```

Nếu chuẩn bị file trước lần đầu tạo container pgAdmin, cấu hình server được mount sẵn. Khi nhập lại, pgAdmin có thể tạo đăng ký trùng; kiểm tra trước trong giao diện.

## Vận hành và bật/tắt

```powershell
.\backend\.venv\Scripts\python.exe scripts/knowledge.py status
.\backend\.venv\Scripts\python.exe scripts/knowledge.py enable
.\backend\.venv\Scripts\python.exe scripts/knowledge.py worker
```

Sau khi đổi flag phải khởi động lại API. Với stack Docker, recreate backend/scheduler để nhận env file mới. Chỉ chạy **một** cách lập lịch: worker CLI riêng hoặc `app.scheduler`; không cần cả hai. Khóa PostgreSQL vẫn ngăn hai worker crawl đồng thời.

`worker` kiểm tra hàng đợi mỗi phút; nguồn giá định kỳ 6 giờ, nguồn khác 24 giờ. Lỗi có giới hạn retry; lần tiếp theo sớm nhất sau một giờ. Tối đa 10 bài chính và 2 PDF đính kèm mỗi bài mỗi lượt. Không cam kết quét toàn bộ lịch sử EVN trong một lượt.

Rollback chức năng:

```powershell
.\backend\.venv\Scripts\python.exe scripts/knowledge.py disable
```

Khởi động lại API và dừng worker. Không xóa volume hoặc tài liệu. Giữ nguyên chỉ số, hóa đơn, thanh toán và database nghiệp vụ. Nếu embedding lỗi, chat đang bật RAG dùng từ khóa với cảnh báo; nếu Gemini hội thoại lỗi, API trả lỗi dịch vụ.

## Quản trị

Trang `/admin/knowledge` và API `/api/admin/knowledge/*` yêu cầu admin thật. Có thể thêm/sửa/tắt nguồn, xếp hàng crawl, xem lịch sử/phiên bản, tải bản gốc, duyệt/chặn và thử truy xuất. Tài liệu đã công bố từ nguồn bị tắt không được truy xuất.

Lệnh `seed` đăng ký cả EVN và hai nguồn SAWACO: thông tin dịch vụ cấp nước và giá nước/hỏi đáp. Với nguồn ngoài EVN chọn “Đọc trực tiếp URL tài liệu”; cấu hình utility WATER và khu vực phục vụ có căn cứ. SAWACO được giới hạn Hồ Chí Minh. Tài liệu hướng dẫn nước có thể dùng trong chat sau công bố; trang biểu giá chưa đạt kiểm tra vẫn chờ duyệt. Không dùng hướng dẫn/giá của nhà cung cấp này làm quy định cho địa phương khác. Bằng chứng kiểm thử nước nằm tại `.local/water-acceptance.json`.

Tài liệu giá thiếu căn cứ hiệu lực/phạm vi hoặc có mâu thuẫn ở trạng thái chờ duyệt. Ngày ký, ngày đăng và ngày crawl không thay cho ngày hiệu lực. Khi duyệt có thể bổ sung metadata nhưng phải có trích dẫn nguyên văn trong nội dung. Không hạ phân loại tài liệu giá thành hướng dẫn để bỏ kiểm tra. Bản scan/ảnh chưa đọc được tiếp tục chờ; hiện chưa tự OCR tài liệu nguồn.

Backend xác minh địa phương phải thực sự nằm trong câu trích, ngày phải là biểu thức ngày hoàn chỉnh sau chỉ dẫn hiệu lực và khoảng ngày phải hợp lệ. `fetched_at`/`observed_hash` ghi lần tải mới nhất; `checked_at` chỉ cập nhật khi xác minh đúng nội dung đang công bố hoặc công bố bản mới. Nếu nội dung nguồn đã đổi mà bản mới chưa đạt kiểm tra, không dùng giá cũ để khẳng định hiện hành. Việc chồng thời gian chưa chứng minh mâu thuẫn: chỉ đánh dấu conflict khi cùng loại khách hàng, ngày hiệu lực, nhãn và đơn vị nhưng số giá có căn cứ khác nhau; nguồn bị tắt không có quyền chặn nguồn đang bật.

Bản gốc HTML luôn tải dạng attachment, không render như HTML của ứng dụng. Kho lưu ở `.local/knowledge`; cần sao lưu cùng volume `knowledge_data` để giữ căn cứ. Trong Docker, thư mục này mount tại `/data/knowledge`.

## Embedding và phiên bản

Mặc định `gemini-embedding-2`, 768 chiều. Truy vấn và tài liệu dùng chỉ dẫn retrieval riêng, không truyền `task_type` của model cũ. Không âm thầm đổi model.

Khi đổi `KNOWLEDGE_EMBEDDING_MODEL`: tắt RAG, kiểm tra model mới thực sự hỗ trợ 768 chiều, chạy `preflight`, rồi `reindex`, đánh giá lại trước khi bật. Việc cập nhật vector theo từng phiên bản là atomic; retrieval lọc đúng model, không trộn không gian embedding. Giá và công nợ vẫn tính bằng code Decimal của nghiệp vụ.

## Kiểm chứng

```powershell
.\backend\.venv\Scripts\python.exe scripts/test_postgres.py
.\backend\.venv\Scripts\python.exe scripts/evaluate_knowledge.py
.\backend\.venv\Scripts\python.exe scripts/knowledge_system.py serve
# Terminal khác:
.\backend\.venv\Scripts\python.exe scripts/knowledge_system.py exercise
```

`test_postgres.py` dùng database `utility_app_test` và `knowledge_test`; test rollback dữ liệu. Không chạy trực tiếp test trên database nghiệp vụ. `knowledge_system.py` chỉ dùng database System đã chuẩn bị bằng workflow `system_test.py`, API 8112/cookie riêng. Script từ chối tên database không phải test. Frontend thử nghiệm dùng API 8112 và port 3112.

Bộ 50 câu có 44 câu đối chiếu đoạn trích từ hai tài liệu EVN về VNeID/xác minh nợ điện và 6 câu giá nước không có nguồn phù hợp. Đây là phép đo truy xuất trên corpus ban đầu, không phải chứng nhận độ phủ toàn quốc hoặc độ đúng của mọi câu Gemini sinh ra. Kết quả nằm trong `.local/knowledge-evaluation.json`; fixture chỉ phục vụ kiểm thử, không đưa đáp án vào ứng dụng.

Kiểm tra trực tiếp UI, API, server, system và transform; lưu ảnh/bằng chứng trong `.local` và ghi mốc tiếp tục vào `IMPLEMENTATION_PROGRESS.md`. Chưa coi câu trả lời số liệu giá là được nghiệm thu nếu chưa có tài liệu giá đủ điều kiện và kiểm tra từng khẳng định với nguồn.
