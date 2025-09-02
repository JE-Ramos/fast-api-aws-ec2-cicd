FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

# Secrets Manager is always enabled in production environments
ENV USE_SECRETS_MANAGER=true

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]