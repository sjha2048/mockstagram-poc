FROM python:3.9-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y     gcc     python3-dev     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
