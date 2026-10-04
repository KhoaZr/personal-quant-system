# PYTHON CODING STANDARDS

1. Type Hints:
   - Bắt buộc khai báo Type Hints cho toàn bộ tham số đầu vào và giá trị trả về của function/method.
   - Ví dụ: `def get_stock_by_symbol(symbol: str, db: Session) -> Optional[Stock]:`

2. Data Validation & Schemas:
   - Sử dụng Pydantic v2 cho toàn bộ request/response DTOs (Data Transfer Objects).
   - Đặt tên Schema rõ ràng: `StockCreate`, `StockResponse`, `IndicatorCalculateRequest`.

3. Exception Handling:
   - Không catch Exception chung chung (`except Exception:`).
   - Bắt chính xác lỗi đặc thù (`SQLAlchemyError`, `KeyError`) và chuyển đổi thành `HTTPException` tương ứng tại tầng API Router.