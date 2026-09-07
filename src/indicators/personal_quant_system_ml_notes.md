# Personal Quant System — Ghi chú quan trọng trước khi xây dựng ML

## 1. Trạng thái hiện tại

Đã hoàn thành:

- Thu thập dữ liệu giá từ Yahoo Finance.
- Làm sạch dữ liệu.
- Lưu dữ liệu OHLCV vào PostgreSQL, bảng `stock_prices`.
- Tính technical indicators.
- Lưu indicators vào PostgreSQL, bảng `technical_indicators`.
- Đã kiểm tra số dòng, symbol, khoảng thời gian, NaN, RSI, ATR và duplicate `symbol + date`.

Pipeline hiện tại:

```text
Yahoo Finance
      ↓
stock_prices
      ↓
calculate indicators
      ↓
technical_indicators
```

---

## 2. Bước tiếp theo: tạo ML Dataset

Không nên train model ngay.

Trước tiên cần kết hợp:

```text
stock_prices
+
technical_indicators
      ↓
ML Dataset
```

Ví dụ dataset:

```text
symbol
date
open
high
low
close
volume
sma20
sma50
ema20
ema50
rsi14
macd
macd_signal
macd_hist
atr14
obv
bollinger_upper
bollinger_middle
bollinger_lower
```

Có thể JOIN hai bảng bằng:

```sql
ON stock_prices.symbol = technical_indicators.symbol
AND stock_prices.date = technical_indicators.date
```

---

## 3. Phải xác định Target

ML cần biết rõ đang dự đoán cái gì.

Một hướng khởi đầu đơn giản:

### Dự đoán giá ngày mai tăng hay giảm

```text
target = 1 → giá ngày mai tăng
target = 0 → giá ngày mai giảm
```

Ví dụ:

```python
df["future_close"] = df["close"].shift(-1)

df["target"] = (
    df["future_close"] > df["close"]
).astype(int)
```

Khi đó:

```text
X = Features
y = Target
```

---

## 4. Cực kỳ chú ý Data Leakage

Đây là vấn đề rất quan trọng với dữ liệu chứng khoán.

Khi dự đoán ngày mai, model chỉ được sử dụng thông tin đã biết tại ngày hôm nay.

Đúng:

```text
Thông tin ngày hôm nay
        ↓
      Model
        ↓
Dự đoán ngày mai
```

Không được:

```text
Thông tin ngày mai
        ↓
      Model
        ↓
Dự đoán ngày mai
```

Không được để feature chứa thông tin tương lai.

Đặc biệt cần kiểm tra:

- `shift()`
- rolling features
- target
- cách chia train/test
- preprocessing/scaling

---

## 5. Các Features hiện tại

### Price / Volume

```text
open
high
low
close
volume
```

### Technical Indicators

```text
sma20
sma50

ema20
ema50

rsi14

macd
macd_signal
macd_hist

atr14

obv

bollinger_upper
bollinger_middle
bollinger_lower
```

Tổng cộng hiện tại:

```text
5 price/volume features
+
13 technical indicators
=
18 features
```

18 features là đủ tốt cho model đầu tiên.

Không cần cố tạo hàng trăm features ngay từ đầu.

---

## 6. Xử lý NaN

Một số indicators có NaN ở những dòng đầu vì cần dữ liệu lịch sử.

Ví dụ:

```text
SMA20 → cần 20 phiên
SMA50 → cần 50 phiên
RSI14 → cần dữ liệu của period 14
```

Không nên tùy tiện thay NaN bằng `0`.

Ví dụ:

```text
RSI = 0
```

khác hoàn toàn với:

```text
RSI chưa đủ dữ liệu để tính
```

Sau khi tạo ML Dataset có thể loại bỏ các dòng không đủ dữ liệu:

```python
df = df.dropna(
    subset=feature_columns + ["target"]
)
```

---

## 7. Chia Train / Validation / Test

### Không random split dữ liệu chứng khoán

Không nên sử dụng kiểu:

```python
train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)
```

theo cách random thông thường.

Lý do: dữ liệu chứng khoán có thứ tự thời gian.

Ví dụ nên chia:

```text
2010 ───────── 2022
      TRAIN

2023 ─── 2024
   VALIDATION

2025 ─── 2026
     TEST
```

Hoặc chia theo tỷ lệ nhưng vẫn giữ thứ tự thời gian:

```text
70% → Train
15% → Validation
15% → Test
```

Nguyên tắc:

> Model không được học dữ liệu tương lai để dự đoán quá khứ.

---

## 8. Thứ tự model nên thử

Không nên bắt đầu ngay bằng Deep Learning.

Nên đi từ đơn giản đến phức tạp:

```text
Baseline
   ↓
Logistic Regression
   ↓
Random Forest
   ↓
XGBoost / LightGBM
   ↓
Deep Learning
```

### Model đầu tiên

Logistic Regression để tạo baseline.

### Model tiếp theo

Random Forest để kiểm tra khả năng học quan hệ phi tuyến.

### Model nâng cao

XGBoost hoặc LightGBM.

### Deep Learning

Sau khi đã có baseline và hiểu rõ dataset:

```text
LSTM
GRU
Transformer
```

---

## 9. Đánh giá Model

Không chỉ nhìn vào Accuracy.

Nên theo dõi:

```text
Accuracy
Precision
Recall
F1-score
ROC-AUC
Confusion Matrix
```

Với hệ thống chứng khoán, nên đánh giá thêm bằng backtest:

```text
Return
Maximum Drawdown
Sharpe Ratio
Win Rate
```

Mục tiêu không chỉ là:

> Model dự đoán đúng bao nhiêu phần trăm?

Mà còn là:

> Nếu sử dụng prediction như một tín hiệu hỗ trợ quyết định, kết quả lịch sử như thế nào?

---

## 10. Backtest

Sau khi có model, cần kiểm tra prediction trên dữ liệu chưa được dùng để train.

Pipeline:

```text
ML Model
   ↓
Prediction
   ↓
Trading Signal
   ↓
Backtest
   ↓
Performance
```

Cần tránh việc dùng dữ liệu test để điều chỉnh model nhiều lần, vì điều đó có thể làm mất tính khách quan của test set.

---

## 11. Kiến trúc project ML dự kiến

Có thể tổ chức:

```text
src/
├── database/
│   ├── db.py
│   └── load_to_postgres.py
│
├── indicators/
│   ├── technical_indicators.py
│   ├── caculate_indicators.py
│   └── save_indicators.py
│
└── ml/
    ├── prepare_ml_dataset.py
    ├── create_target.py
    ├── split_dataset.py
    ├── train.py
    └── evaluate.py
```

---

## 12. Pipeline hoàn chỉnh dự kiến

```text
                 Yahoo Finance
                      │
                      ▼
                 stock_prices
                      │
                      ▼
             Technical Indicators
                      │
                      ▼
            technical_indicators
                      │
                      ▼
              ML Dataset
                      │
                      ▼
             Feature Engineering
                      │
                      ▼
            Train / Validation
                      │
                      ▼
                  ML Model
                      │
                      ▼
                Prediction
                      │
             ┌────────┴────────┐
             ▼                 ▼
        Evaluation          Backtest
             │                 │
             └────────┬────────┘
                      ▼
                 PostgreSQL
                      │
                      ▼
                  Streamlit
```

---

## 13. Hướng phát triển về sau

Sau khi pipeline ML cơ bản hoạt động ổn định, có thể mở rộng thêm:

### Fundamental Features

```text
EPS
PE
PB
ROE
ROA
Debt Ratio
Revenue Growth
```

### News Features

Có thể bổ sung dữ liệu tin tức và sentiment.

### Deep Learning

Có thể thử:

```text
LSTM
GRU
Transformer
```

### Feedback Loop

Sau khi hệ thống có prediction thực tế, có thể lưu kết quả prediction và kết quả thực tế để đánh giá model theo thời gian.

---

## 14. Nguyên tắc quan trọng

### Không tự động giao dịch

Hệ thống có thể:

```text
Phân tích
↓
Dự đoán
↓
Đưa ra tín hiệu/thông tin
```

Nhưng quyết định giao dịch vẫn do người dùng thực hiện.

### Ưu tiên tính đúng của pipeline

Trước khi tăng độ phức tạp model, cần đảm bảo:

```text
Data đúng
↓
Feature đúng
↓
Target đúng
↓
Không leakage
↓
Split đúng
↓
Evaluation đúng
↓
Backtest đúng
```

Một model phức tạp nhưng dữ liệu hoặc cách đánh giá sai sẽ không có giá trị.

---

## 15. Việc cần làm ngay

### Bước 1

Tạo:

```text
src/ml/prepare_ml_dataset.py
```

### Bước 2

JOIN:

```text
stock_prices
+
technical_indicators
```

### Bước 3

Xử lý NaN.

### Bước 4

Tạo target.

### Bước 5

Kiểm tra Data Leakage.

### Bước 6

Chia:

```text
Train
Validation
Test
```

### Bước 7

Train Logistic Regression làm baseline.

---

> **Trạng thái hiện tại:** Database + Technical Indicators đã hoàn thành.  
> **Bước tiếp theo:** xây dựng ML Dataset và Target trước khi train model.
