FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p ml/model backend data reports/figures reports/screenshots docs

COPY backend/ ./backend/
COPY ml/model/ ./ml/model/

# Set env vars
ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql://user:password@db:5432/fraud_db

EXPOSE 8000

CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
