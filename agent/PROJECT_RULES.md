# PROJECT & SECURITY RULES

1. Environment & Secrets:
   - Tuyệt đối không commit API keys, DB password, secret token lên Git.
   - Luôn sử dụng file `.env` cho cấu hình cục bộ và `.env.example` làm template.

2. Git & Commit Guidelines:
   - Format commit: `<type>(<scope>): <short description>`
   - Các type hợp lệ: feat, fix, docs, refactor, test, chore.
   - Ví dụ: `feat(backend): add stock price repository with supabase connection`

3. Directory Isolation:
   - `/backend`: Chỉ chứa mã nguồn FastAPI, API REST, Service và Repository.
   - `/ml`: Chỉ chứa mã nguồn huấn luyện, xử lý feature, đánh giá và lưu trữ artifacts mô hình.
   - `/backtesting`: Chứa engine giả lập chiến lược giao dịch.