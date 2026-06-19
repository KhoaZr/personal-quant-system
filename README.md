# Personal Quant System

## Mục tiêu
Xây dựng hệ thống hỗ trợ đầu tư chứng khoán cá nhân.

## Giai đoạn hiện tại
- Thu thập dữ liệu từ Yahoo Finance.
- Xử lý dữ liệu.
- Lưu vào PostgreSQL.

## Luồng dữ liệu (Data Flow)
Yahoo Finance -> Fetch Layer -> Processing Layer -> Database Layer

## Cấu trúc thư mục

```text
├── fetch/
│   └── yahoo_finance.py (Có hàm lấy dữ liệu cổ phiếu của mã symbol theo ngày)
├── process/
│   └── stock_processor.py (Chuẩn hóa dữ liệu)
├── database/
│   └── (Các file mã nguồn kết nối và quản lý PostgreSQL)
└── main.py