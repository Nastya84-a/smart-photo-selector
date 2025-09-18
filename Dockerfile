FROM python:3.10-slim

# рабочая директория внутри контейнера
WORKDIR /app

# устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# скопируем упрощенные зависимости
COPY requirements_docker.txt .

# установка зависимостей
RUN pip install --no-cache-dir -r requirements_docker.txt

# скопируем весь проект внутрь контейнера
COPY . .

# запускаем Flask
CMD ["python", "app_simple.py"]