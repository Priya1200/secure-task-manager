FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --only-upgrade zlib1g && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip uninstall -y setuptools wheel
COPY app.py .
RUN useradd -m appuser
USER appuser
EXPOSE 5000
CMD ["python", "app.py"]
