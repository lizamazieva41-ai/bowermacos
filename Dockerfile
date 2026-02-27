FROM python:3.11-slim

LABEL maintainer="Bower Team"
LABEL description="Antidetect Browser - Stealth Browser Automation"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r bower && useradd -r -g bower bower

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium --with-deps && \
    playwright install-deps chromium

COPY . .

RUN chown -R bower:bower /app

USER bower

EXPOSE 8000

ENV PORT=8000 \
    HOST=0.0.0.0 \
    DATA_DIR=/app/data \
    LOGS_DIR=/app/logs

RUN mkdir -p ${DATA_DIR} ${LOGS_DIR}

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
