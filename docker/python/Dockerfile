# docker/python/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Set up a non-root user for better security
RUN useradd -m appuser
USER appuser

COPY function.py /app/
CMD ["python", "function.py"]