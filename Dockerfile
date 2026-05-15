FROM python:3.11-slim

WORKDIR /app

# Встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код
COPY marvel_bot.py .

# Запускаємо бота
CMD ["python", "marvel_bot.py"]
