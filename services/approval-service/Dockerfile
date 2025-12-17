FROM python:3.11-slim

WORKDIR /app

# Copy shared module
COPY ../shared /app/shared

# Copy service files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Create uploads directory
RUN mkdir -p /app/uploads

EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
