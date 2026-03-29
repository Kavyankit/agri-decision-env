# Use a slim Python base image to keep container size lower.
FROM python:3.12-slim

# Keep logs unbuffered and avoid writing .pyc files in container layers.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for better Docker layer caching.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project source.
COPY . /app

# Run service under a non-root user for better container security posture.
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# API service port.
EXPOSE 7860

# Container-level healthcheck against API health endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/health', timeout=3)"

# Run FastAPI app through uvicorn.
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
