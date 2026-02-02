
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create logs directory
RUN mkdir -p logs && chmod 777 logs

# Expose ports (mapped in docker-compose)
EXPOSE 2222 2223 8000


# Security: Run as non-root
RUN useradd -m cyanide
USER cyanide

# Run
CMD ["python", "main.py"]
