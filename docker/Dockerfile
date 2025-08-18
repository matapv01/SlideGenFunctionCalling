FROM python:3.10

# Cài các dependency hệ thống
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 xdg-utils libgbm1 \
    libgtk-3-0 libvulkan1 libxkbcommon0 libatspi2.0-0

WORKDIR /app

# Thêm thư mục gốc của ứng dụng vào PYTHONPATH
ENV PYTHONPATH=/app

# COPY . .
COPY requirements.txt .

RUN pip install -r requirements.txt
RUN playwright install

CMD ["python", "main.py"]
