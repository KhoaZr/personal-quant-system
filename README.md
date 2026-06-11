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
│   └── (Các file mã nguồn lấy dữ liệu từ API)
├── process/
│   └── (Các file mã nguồn làm sạch và xử lý dữ liệu)
├── database/
│   └── (Các file mã nguồn kết nối và quản lý PostgreSQL)
└── main.py