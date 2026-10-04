# ARCHITECTURE DESIGN RULES

1. Layer Responsibilities:
   - Router (`app/api/v1`): Chỉ tiếp nhận HTTP Request, validate qua Schema, gọi Service và trả về Response.
   - Service (`app/services`): Chứa toàn bộ Business Logic, thuật toán tính toán chỉ báo, xử lý dữ liệu.
   - Repository (`app/repositories`): Chỉ chịu trách nhiệm truy vấn CSDL (SQLAlchemy/Supabase). Không chứa Business Logic.
   - Models (`app/models`): Khai báo ORM Entities.

2. Anti-Patterns (Cấm thực hiện):
   - CẤM viết câu lệnh SQL hoặc ORM query trực tiếp trong API Router.
   - CẤM gọi trực tiếp CSDL từ tầng Frontend hoặc các kịch bản ML thô.