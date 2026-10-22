# Personal Quant System

> **Hệ thống nghiên cứu định lượng và hỗ trợ quyết định đầu tư cá
> nhân**\
> Python · FastAPI · Supabase PostgreSQL · Machine Learning · Technical
> Analysis · Paper Trading

Personal Quant System là dự án cá nhân hỗ trợ nghiên cứu dữ liệu chứng
khoán, xây dựng đặc trưng, tạo tín hiệu và đánh giá chiến lược bằng giao
dịch mô phỏng. Hệ thống được thiết kế để hỗ trợ người dùng ra quyết
định.

> **Trạng thái dự án:** Backend, thu thập dữ liệu, chỉ báo kỹ thuật,
> pipeline ML, tạo tín hiệu và Paper Trading đang được phát triển.
> Dashboard frontend, tự động hóa lịch chạy và triển khai hạ tầng là các
> bước tiếp theo.

------------------------------------------------------------------------

## Mục lục

-   [Mục tiêu và nguyên tắc](#mục-tiêu-và-nguyên-tắc)
-   [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
-   [Công nghệ sử dụng](#công-nghệ-sử-dụng)
-   [Cấu trúc repository](#cấu-trúc-repository)
-   [Cài đặt và chạy local](#cài-đặt-và-chạy-local)
-   [API chính](#api-chính)
-   [Machine Learning và retraining](#machine-learning-và-retraining)
-   [Quản lý model artifacts](#quản-lý-model-artifacts)
-   [Roadmap](#roadmap)
-   [Giới hạn và tuyên bố miễn trừ](#giới-hạn-và-tuyên-bố-miễn-trừ)

------------------------------------------------------------------------

## Mục tiêu và nguyên tắc

### Mục tiêu

Hệ thống hướng tới quy trình nghiên cứu khép kín:

1.  Thu thập dữ liệu giá chứng khoán.
2.  Kiểm tra và lưu dữ liệu vào PostgreSQL.
3.  Tính toán chỉ báo kỹ thuật và xây dựng feature dataset.
4.  Huấn luyện, đánh giá và lưu phiên bản mô hình Machine Learning.
5.  Kết hợp kết quả mô hình với quy tắc kỹ thuật để tạo tín hiệu và kế
    hoạch giao dịch.
6.  Ghi nhận giao dịch mô phỏng, giá vào/ra và kết quả PnL.
7.  Dùng kết quả giao dịch để phân tích, kiểm định và cải thiện quy
    trình trong các phiên bản tương lai.

### Nguyên tắc thiết kế

-   **Decision support, not auto-execution:** hệ thống hỗ trợ phân tích;
    người dùng tự quyết định giao dịch.
-   **Time-aware evaluation:** giữ thứ tự thời gian khi chia train và
    out-of-sample (OOS); tránh dùng thông tin tương lai để tạo feature.
-   **Reproducibility:** lưu metric, tham số và version của model để có
    thể truy vết.
-   **Risk awareness:** đánh giá chiến lược bằng kết quả sau chi phí,
    drawdown và các chỉ số giao dịch, không chỉ bằng metric phân loại.
-   **Secrets management:** không commit thông tin kết nối, mật khẩu
    hoặc dữ liệu nhạy cảm lên repository.

------------------------------------------------------------------------

## Kiến trúc hệ thống

``` text
        Market Data / Yahoo Finance
                    |
                    v
       Data Collection & Validation
                    |
                    v
          Supabase PostgreSQL
                    |
                    v
      Feature Engineering / Indicators
                    |
                    v
          ML Model / Prediction
                    |
                    v
        Signal & Risk Management
                    |
                    v
            Trade Plan
                    |
                    v
          Paper Trading
                    |
                    v
       PnL / Feedback Records
                    |
                    v
        Evaluation & Retraining
```

Đây là kiến trúc mục tiêu. Những bước như tự động lập lịch, triển khai
production và tích hợp feedback vào quá trình huấn luyện cần được xác
minh theo trạng thái code hiện tại trước khi xem là đã hoàn tất.

------------------------------------------------------------------------

## Công nghệ sử dụng

  -----------------------------------------------------------------------
  Thành phần              Công nghệ               Vai trò
  ----------------------- ----------------------- -----------------------
  Backend API             Python, FastAPI,        Cung cấp REST API
                          Uvicorn                 

  Database                Supabase PostgreSQL     Lưu dữ liệu giá, chỉ
                                                  báo, tín hiệu, giao
                                                  dịch và metadata

  ORM                     SQLAlchemy              Truy vấn và quản lý dữ
                                                  liệu

  Dependency management   `uv`                    Quản lý môi trường và
                                                  thư viện Python

  Data processing         pandas, NumPy           Làm sạch và xử lý dữ
                                                  liệu

  Technical analysis      `ta` và các phép tính   Tính chỉ báo kỹ thuật
                          chỉ báo trong dự án     

  Machine Learning        scikit-learn            Huấn luyện và đánh giá
                                                  mô hình

  Model serialization     joblib                  Lưu và tải model
                                                  artifacts

  Code quality            Ruff, Mypy              Kiểm tra code và kiểu
                                                  dữ liệu

  Schema validation       Pydantic                Xác thực
                                                  request/response

  Frontend dự kiến        React, Vite, Tailwind   Dashboard theo dõi tín
                          CSS                     hiệu và kết quả
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## Cấu trúc repository

``` text
personal-quant-system/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # REST API endpoints
│   │   ├── core/             # Cấu hình và kết nối database
│   │   ├── models/           # SQLAlchemy models
│   │   ├── repositories/     # Data access layer
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── main.py           # FastAPI application
│   ├── .env.example          # Mẫu biến môi trường, không chứa secrets
│   └── pyproject.toml        # Dependencies và cấu hình backend
├── ml/
│   ├── models/               # Model artifacts sinh ra tại local
│   ├── experiments/          # Notebook và thử nghiệm
│   └── training/
│       ├── prep_data.py
│       ├── train_pipeline.py
│       └── retrain_pipeline.py
├── frontend/                 # Dashboard frontend (đang phát triển)
├── docs/                     # Tài liệu thiết kế
├── .gitignore
└── README.md
```

Cấu trúc trên là cấu trúc tham chiếu; tên file/thư mục thực tế có thể
thay đổi theo tiến độ phát triển.

------------------------------------------------------------------------

## Cài đặt và chạy local

### Yêu cầu

-   Git
-   Python phiên bản tương thích với dự án (khuyến nghị kiểm tra
    `requires-python` trong `backend/pyproject.toml`)
-   `uv`
-   Tài khoản Supabase và PostgreSQL connection string

### 1. Clone repository

Thay URL bằng URL repository thực tế của bạn:

``` bash
git clone https://github.com/<your-username>/personal-quant-system.git
cd personal-quant-system
```

### 2. Cấu hình biến môi trường

Tạo file `backend/.env` trên máy local. Không commit file này.

Ví dụ:

``` dotenv
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

Sử dụng đúng connection string do Supabase cung cấp. Không đưa mật khẩu
thật vào README, source code hoặc commit.

Nếu backend có thêm biến môi trường bắt buộc, hãy khai báo tên và giá
trị mẫu trong `backend/.env.example`; không lưu secrets trong file mẫu.

### 3. Cài dependencies backend

``` bash
cd backend
uv sync
```

Nếu dự án chưa có môi trường ảo, `uv` có thể tạo `.venv` theo cấu hình
dự án. Thực hiện các lệnh tiếp theo tại đúng thư mục backend.

### 4. Khởi chạy API

``` bash
uv run --active uvicorn app.main:app --reload
```

Mở Swagger UI:

-   API docs: `http://127.0.0.1:8000/docs`
-   OpenAPI schema: `http://127.0.0.1:8000/openapi.json`
-   Health check: `http://127.0.0.1:8000/health` (nếu endpoint được đăng
    ký tại đường dẫn này)

Nếu lệnh không chạy, hãy kiểm tra `app.main:app`, cấu hình database và
các biến môi trường bắt buộc.

### 5. Chạy pipeline Machine Learning

Từ thư mục gốc repository, sử dụng môi trường Python đã cài dependencies
cần thiết:

``` bash
uv run --active python ml/training/train_pipeline.py
uv run --active python ml/training/retrain_pipeline.py
```

Chỉ chạy pipeline retraining khi dữ liệu đầu vào đã được kiểm tra và bạn
hiểu điều kiện deploy của script hiện tại.

------------------------------------------------------------------------

## API chính

Các endpoint dưới đây phản ánh những chức năng được thiết kế/phát triển
trong dự án. Đường dẫn và phương thức chính xác nên được xác nhận tại
Swagger UI `/docs` của phiên bản đang chạy.

  -----------------------------------------------------------------------------------
  Endpoint                            Phương thức             Chức năng
  ----------------------------------- ----------------------- -----------------------
  `/health`                           `GET`                   Kiểm tra tình trạng API

  `/api/v1/stocks/`                   `GET` / `POST`          Liệt kê hoặc thêm mã
                                                              chứng khoán

  `/api/v1/stocks/collect`            `POST`                  Thu thập dữ liệu giá

  `/api/v1/indicators/calculate`      `POST`                  Tính chỉ báo kỹ thuật

  `/api/v1/predictions/predict`       `POST`                  Dự đoán bằng model
                                                              active

  `/api/v1/trades/generate-signals`   `POST`                  Sinh tín hiệu và kế
                                                              hoạch giao dịch

  `/api/v1/paper-trades/open`         `POST`                  Mở giao dịch mô phỏng

  `/api/v1/paper-trades/close`        `POST`                  Đóng giao dịch mô phỏng
                                                              và tính kết quả
  
  -----------------------------------------------------------------------------------

Swagger UI là nguồn tham chiếu chính xác nhất cho request schema,
response schema và mã lỗi của phiên bản hiện tại.

------------------------------------------------------------------------

## Machine Learning và retraining

### Feature dataset

Pipeline hiện tại sử dụng các feature được khai báo bởi
`get_feature_columns()` trong `ml/training/prep_data.py`. Danh sách
feature đã được sử dụng trong lần retraining gần đây:

-   `close`, `volume`
-   `sma20`, `sma50`, `ema20`, `ema50`
-   `rsi14`, `macd`, `macd_signal`, `macd_hist`, `atr14`
-   `price_to_sma20`, `price_to_sma50`
-   `return_1d`, `return_5d`, `return_20d`

Target, thời hạn dự đoán và cách tạo nhãn cần được xác minh trong
`prep_data.py`; không nên suy luận target chỉ từ tên feature.

### Quy trình retraining

Pipeline retraining hiện được thiết kế để:

1.  Đọc dữ liệu giá và chỉ báo từ Supabase.
2.  Xây dựng feature dataset.
3.  Làm sạch `NaN`, `inf` và `-inf`.
4.  Chia dữ liệu theo thứ tự thời gian thành Train và OOS.
5.  Fit imputer và scaler trên Train, sau đó áp dụng lên OOS.
6.  Huấn luyện Random Forest và tính Precision, F1, AUC.
7.  So sánh Candidate với model active và lưu artifacts nếu điều kiện
    deploy được đáp ứng.
8.  Ghi metadata phiên bản vào bảng `ModelVersion`.

**Lưu ý:** phiên bản script cần được kiểm tra để bảo đảm dữ liệu từ
`FeedbackDataset` thực sự được đưa vào huấn luyện. Việc tạo feedback
record sau khi đóng paper trade không tự động có nghĩa pipeline đã sử
dụng các record đó.


### Điều kiện deploy

Không nên chỉ dựa vào F1 đã làm tròn để quyết định thay model active.
Quy trình triển khai nên:

-   So sánh model cũ và Candidate trên cùng tập kiểm tra.
-   Lưu metric với độ chính xác đầy đủ.
-   Yêu cầu mức cải thiện tối thiểu đã định trước.
-   Kiểm tra AUC, Precision, Recall, confusion matrix và kết quả
    backtest.
-   Giữ khả năng quay lại model trước nếu bản mới có vấn đề.
-   Đảm bảo model, imputer và scaler được tải cùng một phiên bản.

------------------------------------------------------------------------

## Quản lý model artifacts

Các file `.joblib` là artifacts được sinh ra khi huấn luyện. Theo mặc
định, không nên commit chúng vào Git nếu không có yêu cầu rõ ràng về
việc lưu model cùng repository.

Ví dụ `.gitignore` tại thư mục gốc:

``` gitignore
# Python environments and cache
.venv/
venv/
__pycache__/
*.py[cod]

# Secrets
.env
.env.*
!.env.example

# Generated model artifacts
ml/models/*.joblib
ml/models/*.pkl
ml/models/*.pickle

# Logs and notebooks cache
*.log
.ipynb_checkpoints/
```

Giữ code, cấu hình mẫu và tài liệu trong Git. Lưu artifacts cần dùng khi
inference tại máy local, ổ lưu trữ bền vững trên server hoặc kho
artifact riêng. Metadata như version, metric và parameters có thể lưu
trong database; tránh đưa secrets vào metadata hoặc log.

------------------------------------------------------------------------

## Roadmap

-   [x] Xây dựng cấu trúc backend và SQLAlchemy models.
-   [x] Xây dựng quy trình thu thập dữ liệu giá.
-   [x] Tính toán chỉ báo kỹ thuật.
-   [x] Xây dựng feature engineering và baseline ML pipeline.
-   [x] Phát triển logic tín hiệu và kế hoạch giao dịch.
-   [x] Phát triển các endpoint Paper Trading.
-   [x] Xây dựng pipeline retraining Candidate và lưu model artifacts.
-   [ ] Hoàn thiện kiểm định chất lượng dữ liệu và kiểm tra look-ahead
    bias.
-   [ ] Chuẩn hóa benchmark để so sánh model trên cùng tập OOS.
-   [ ] Tích hợp và xác thực quy trình sử dụng Feedback Dataset trong
    retraining.
-   [ ] Backtest có tính phí giao dịch, trượt giá và quản trị rủi ro.
-   [ ] Xây dựng React + Vite dashboard.
-   [ ] Lập lịch chạy tự động và giám sát pipeline.
-   [ ] Hoàn thiện Docker, triển khai AWS EC2 và CI/CD.

------------------------------------------------------------------------

## Giới hạn và tuyên bố miễn trừ

Personal Quant System là dự án nghiên cứu và hỗ trợ quyết định đầu tư cá
nhân. Dữ liệu thị trường có thể thiếu, trễ hoặc sai; mô hình Machine
Learning có thể dự đoán sai và kết quả backtest không bảo đảm hiệu quả
tương lai.

Các tín hiệu BUY/HOLD/SELL, kế hoạch giao dịch, xác suất dự đoán và
metric chỉ mang tính tham khảo kỹ thuật, không phải lời khuyên đầu tư
tài chính. Người dùng chịu trách nhiệm tự đánh giá rủi ro và quyết định
giao dịch. Không sử dụng hệ thống này như một cơ chế tự động đặt lệnh
tiền thật nếu chưa được kiểm định và bảo vệ đầy đủ.
