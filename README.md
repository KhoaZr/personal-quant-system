### 1. Tổng quan cấu trúc thư mục

    personal-quant-system/
    ├── .env
    ├── .gitignore
    ├── main.py
    ├── README.md
    ├── requirements.txt
    ├── data/
    │   ├── clean/
    │   │   ├── FPT.VN.cleaned.csv
    │   │   ├── ml_dataset.csv
    │   │   ├── test.csv
    │   │   ├── train.csv
    │   │   └── validation.csv
    │   └── raw/
    │       ├── data_a_day.csv
    │       └── FPT.VN.csv
    ├── doc/
    │   ├── database/
    │   │   ├── database_Stock.pdf
    │   │   └── database_Stock.png
    │   └── notebook/
    │       ├── EDA.ipynb
    │       └── Personal_Quant_System_Master_Project_Plan_v2.pdf
    ├── scripts/
    │   └── run_clean_fpt.py
    └── src/
        ├── database/
        │   ├── create_table.py
        │   ├── db.py
        │   ├── load_to_postgres.py
        │   └── models.py
        ├── fetch/
        │   └── yahoo_finance.py
        ├── process/
        │   └── stock_processor.py
        ├── indicators/
        │   ├── __init__.py
        │   ├── calculate_indicators.py
        │   ├── personal_quant_system_ml_notes.md
        │   ├── save_indicators.py
        │   └── technical_indicators.py
        └── ml/
            ├── prepare_ml_dataset.py
            ├── split_dataset.py
            └── train.py
  ──────
  ### 2. Chức năng chi tiết của từng file

  #### 📂 Thư mục gốc (Root)

  • README.md: Mô tả tổng quan dự án, mục tiêu hệ thống và luồng xử lý dữ liệu (Yahoo Finance -> Fetch -> Processing -> Database).
  • requirements.txt: Khai báo danh sách các thư viện Python phụ thuộc như yfinance, pandas, SQLAlchemy, psycopg2-binary, python-dotenv.
  • .env: File cấu hình biến môi trường cục bộ (chứa URI kết nối cơ sở dữ liệu DATABASE_URL).
  • .gitignore: Khai báo các file/thư mục Git sẽ bỏ qua (như môi trường ảo .venv, bộ nhớ tạm __pycache__, file dữ liệu cá nhân...).
  • main.py: File khởi chạy mẫu/thử nghiệm. Hiện tại chứa code tải dữ liệu FPT từ Yahoo Finance, xử lý dữ liệu thô và vẽ biểu đồ Ma trận tương quan
  (Correlation Matrix) giữa các chỉ số OHLCV.
  ──────
  #### 📂 Thư mục data/ (Dữ liệu)

  • data/raw/: Chứa dữ liệu thô thu thập ban đầu từ Yahoo Finance.
      • FPT.VN.csv: Dữ liệu giá lịch sử dạng thô của mã cổ phiếu FPT.
      • data_a_day.csv: Dữ liệu giao dịch thô trong ngày của danh mục các mã chứng khoán.
  • data/clean/: Chứa dữ liệu đã được làm sạch và dữ liệu phục vụ Machine Learning.
      • FPT.VN.cleaned.csv: Dữ liệu lịch sử cổ phiếu FPT đã chuẩn hóa cột, loại bỏ trùng lặp và dị biệt.
      • ml_dataset.csv: Tập dữ liệu tổng hợp (kết hợp giá OHLCV + các chỉ báo kỹ thuật + nhãn target xu hướng giá ngày tiếp theo).
      • train.csv: Tập dữ liệu huấn luyện ML (chiếm 70% dữ liệu theo thứ tự thời gian).
      • validation.csv: Tập dữ liệu kiểm định ML (chiếm 15% thời gian kế tiếp).
      • test.csv: Tập dữ liệu kiểm thử ML độc lập (chiếm 15% thời gian gần nhất).

  ──────
  #### 📂 Thư mục doc/ (Tài liệu thiết kế & Phân tích)

  • doc/database/:
      • database_Stock.pdf & database_Stock.png: Sơ đồ thiết kế CSDL mối quan hệ giữa các bảng cổ phiếu (stocks, stock_prices,...).
  • doc/notebook/:
      • EDA.ipynb: Jupyter Notebook phân tích dữ liệu khám phá (Exploratory Data Analysis).
      • Personal_Quant_System_Master_Project_Plan_v2.pdf: Kế hoạch tổng thể triển khai dự án Master Plan (v2).

  ──────
  #### 📂 Thư mục scripts/ (Kịch bản thực thi)

  • run_clean_fpt.py: Script thực thi độc lập gọi module làm sạch dữ liệu để biến đổi data/raw/FPT.VN.csv thành data/clean/FPT.VN.cleaned.csv.
  ──────
  #### 📂 Thư mục src/ (Mã nguồn chính của hệ thống)

  ##### 1. src/database/ (Tương tác Cơ sở dữ liệu PostgreSQL)

  • db.py: Đọc biến môi trường DATABASE_URL từ file .env và khởi tạo kết nối SQLAlchemy Engine tới PostgreSQL.
  • models.py: Định nghĩa các ORM class (bảng Stock lưu thông tin mã chứng khoán/ngành/sàn và bảng StockPrice lưu thông tin giá giao dịch hàng ngày OHLCV).
  • create_table.py: Script tự động tạo các bảng trong PostgreSQL dựa theo định nghĩa ORM trong models.py.
  • load_to_postgres.py: Đọc file CSV đã làm sạch và đẩy dữ liệu giao dịch mới vào bảng stock_prices trong PostgreSQL.

  ##### 2. src/fetch/ (Thu thập dữ liệu)

  • yahoo_finance.py: Chứa các hàm giao tiếp với thư viện yfinance để tải giá chứng khoán theo ngày (get_data_today) hoặc tải chuỗi lịch sử từ năm 2010
  đến hiện tại (get_data).

  ##### 3. src/process/ (Xử lý & Làm sạch dữ liệu)

  • stock_processor.py: Bộ công cụ xử lý dữ liệu nâng cao:
      • Làm phẳng MultiIndex columns từ yfinance.
      • Chuẩn hóa tên cột thành định dạng lower_snake_case.
      • Xóa bỏ dữ liệu trùng lặp (symbol, date), loại bỏ các hàng NaN hoặc có giá không hợp lệ (Open, High, Low, Close ≤ 0).
      • Kiểm tra tính logic của giá (ví dụ: High ≥ Low, High ≥ Close).


  ##### 4. src/indicators/ (Tính toán chỉ báo kỹ thuật)

  • \_\_init\_\_.py: Đánh dấu gói Python package.
  • technical_indicators.py: Định nghĩa công thức tính toán toán học cho các chỉ báo kỹ thuật phổ biến trên Pandas DataFrame:
      • Xu hướng: SMA (20, 50), EMA (20, 50).
      • Động lượng: RSI (14), MACD (Line, Signal, Histogram).
      • Biến động & Khối lượng: ATR (14), OBV (On-Balance Volume), Bollinger Bands (Upper, Middle, Lower).
  • calculate_indicators.py: Đọc dữ liệu OHLCV từ PostgreSQL, thực hiện tính chỉ báo độc lập cho từng mã chứng khoán để tránh rò rỉ dữ liệu giữa các mã,
  sau đó validate ràng buộc dữ liệu (RSI trong [0, 100], ATR ≥ 0).
  • save_indicators.py: Xóa dữ liệu cũ và ghi các chỉ báo kỹ thuật đã tính toán vào bảng technical_indicators trong PostgreSQL.
  • personal_quant_system_ml_notes.md: Tài liệu hướng dẫn thiết kế bài toán Machine Learning: Lưu ý tránh Data Leakage, hướng dẫn tạo Target, quy chuẩn
  chia tập dữ liệu Time-series và lộ trình phát triển mô hình từ Logistic Regression tới Deep Learning.

  ##### 5. src/ml/ (Machine Learning Pipeline)

  • prepare_ml_dataset.py:
      • INNER JOIN dữ liệu từ 2 bảng stock_prices và technical_indicators.
      • Tạo nhãn dự đoán target (1 nếu giá ngày mai tăng so với hôm nay, 0 nếu giảm/đi ngang).
      • Loại bỏ các dòng bị khuyết dữ liệu (do cửa sổ trượt của chỉ báo) và export ra file data/clean/ml_dataset.csv.
  • split_dataset.py:
      • Chia dữ liệu thành 3 tập Train (70%), Validation (15%), Test (15%) theo thứ tự thời gian (không chọn ngẫu nhiên để tuân thủ tính chất chuỗi thời
      gian time-series).
      • Lưu thành các file train.csv, validation.csv, test.csv.
  • train.py:
      • Đọc train.csv và validation.csv.
      • Sử dụng StandardScaler (chỉ fit trên tập Train) để chuẩn hóa đặc trưng.
      • Huấn luyện mô hình baseline Logistic Regression.
      • Đánh giá hiệu năng trên tập Validation qua các chỉ số: Accuracy, Precision, Recall, F1-score, ROC-AUC và Confusion Matrix.