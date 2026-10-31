FROM python:3.10-slim

# Hugging Face Spaces runs containers as uid 1000, so use a matching non-root user.
RUN useradd -m -u 1000 user
WORKDIR /app
RUN chown user:user /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user backend/ ./backend/
COPY --chown=user ml/model/ ./ml/model/
COPY --chown=user frontend/ ./frontend/

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

USER user
EXPOSE 8000

# exec so uvicorn receives stop signals; PORT is honoured when the platform sets it
CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
