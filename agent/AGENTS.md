# AI AGENT WORKFLOW & DIRECTIVES

## Quy trình 8 bước bắt buộc cho mọi công việc:
1. READ: Đọc kỹ tài liệu quy chuẩn trong \`/agent\` và kiến trúc tại \`/docs\`.
2. INSPECT: Kiểm tra mã nguồn hiện có trước khi đề xuất viết mới.
3. PLAN: Đề xuất Kế hoạch ngắn (Small Plan) và chờ xác nhận phạm vi.
4. SCOPE: Chỉ lập trình đúng phạm vi được yêu cầu, tuyệt đối không tự ý refactor các file không liên quan.
5. ARCHITECTURE: Tuân thủ nghiêm ngặt luồng: Router -&gt; Schema -&gt; Service -&gt; Repository -&gt; Database.
6. QUALITY: Chạy Linter (Ruff), Type Checker (Mypy) và Pytest trước khi hoàn tất.
7. DIFF: Review diff cẩn thận, đảm bảo không còn secret/hardcoded key.
8. DOCUMENT: Cập nhật tài liệu tương ứng tại \`/docs\` khi có sự thay đổi kiến trúc/API.

## Quy tắc cốt lõi (Core Principles):

- Database: Mọi thay đổi DB schema phải thông qua Alembic Migration. 
- ML Integrity: Triệt tiêu hoàn toàn Data Leakage trong dữ liệu chuỗi thời gian (Time-series). 
- Configuration: Dùng Pydantic BaseSettings đọc từ file \`.env\`.