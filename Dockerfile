# Stage 1: Build & wheels
FROM python:3.11-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Minimal runtime image
FROM python:3.11-slim as runner

WORKDIR /app

# Low-RAM arena parameters
ENV OMP_NUM_THREADS=2 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/hf_cache \
    PORT=10000

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY src/ ./src/
COPY pyproject.toml .

# Create cache directory for model downloads
RUN mkdir -p /app/hf_cache

# Expose Render default port
EXPOSE 10000

# Start FastAPI server on the container port
CMD ["sh", "-c", "uvicorn src.auto_translate.api:app --host 0.0.0.0 --port ${PORT}"]
