FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --only-upgrade zlib1g && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip uninstall -y setuptools wheel
COPY app ./app
COPY wsgi.py .
# run as a normal user (fixed numeric id, so Kubernetes can verify it), with one writable folder for the database
RUN useradd -m -u 10001 appuser && mkdir -p /app/instance && chown appuser /app/instance
USER appuser
ENV DATABASE_URL=sqlite:////app/instance/taskmanager.db
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')"
# --preload: the app (and the database tables) are created once, before the workers start
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--preload", "wsgi:app"]
