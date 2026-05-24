FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir watchdog

COPY . .

ENV MVC_HOST=0.0.0.0

CMD ["python3", "-m", "servers.v1_runserver"]
