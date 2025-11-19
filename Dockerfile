FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files EXCEPT the service account key
COPY . .

# Ensure the key never gets used in production
RUN rm -f serviceAccountKey.json || true

ENV PORT=8080
EXPOSE 8080

CMD ["python", "http_server.py"]
