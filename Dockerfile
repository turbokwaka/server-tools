FROM python:3.11-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends lm-sensors tzdata \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Спочатку залежності (кращий кеш)
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Потім код
COPY *.py ./
COPY .env ./

ENV PYTHONUNBUFFERED=1
CMD ["python", "-u", "scheduler.py"]
