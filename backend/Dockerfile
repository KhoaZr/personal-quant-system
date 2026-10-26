# backend/Dockerfile

FROM python:3.12-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Ngăn Python tạo file .pyc và bật log realtime
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend:/app

# Cài đặt các công cụ hệ thống cần thiết
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy cấu hình dự án để cài đặt dependencies trước
# (Tận dụng Docker cache)
COPY backend/pyproject.toml backend/uv.lock* /app/backend/

# Đồng bộ cài đặt thư viện vào hệ thống
WORKDIR /app/backend

RUN uv pip install --system -r pyproject.toml

# Quay lại thư mục gốc và copy mã nguồn backend và ML
WORKDIR /app

COPY backend/ /app/backend/
COPY ml/ /app/ml/

# Mở cổng 8000 cho FastAPI
EXPOSE 8000

# Chạy Backend Server
WORKDIR /app/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]