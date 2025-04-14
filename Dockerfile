FROM python:3.9-slim

# Встановлюємо lm-sensors
RUN apt-get update && \
    apt-get install -y lm-sensors && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY main.py .

# Встановлення залежностей Python
RUN pip install psutil requests

CMD ["python", "main.py"]
