# Stage 1: Build dependencies & wheels
FROM python:3.11-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Minimal runtime image with pre-baked models
FROM python:3.11-slim as runner

WORKDIR /app

# Optimal 0.1 CPU & low-RAM configuration
ENV OMP_NUM_THREADS=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/hf_cache \
    CACHE_DIR=/app/hf_cache \
    BEAM_SIZE=1 \
    PORT=10000

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application source code and pre-load script
COPY pyproject.toml .
COPY src/ ./src/
COPY preload_models.py .

# Pre-download all INT8 translation models directly into the Docker image layers
# This guarantees models exist on disk and will NEVER re-download on container restart or sleep/wake
RUN python preload_models.py

# Expose server port
EXPOSE 10000

# Start FastAPI server
CMD ["sh", "-c", "uvicorn src.auto_translate.api:app --host 0.0.0.0 --port ${PORT}"]
