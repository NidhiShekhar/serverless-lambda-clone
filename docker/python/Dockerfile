FROM python:3.9-slim

WORKDIR /app

# Don't try to copy function.py at build time
# Just copy requirements.txt if it exists
COPY requirements.txt* .
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# The actual function.py will be mounted at runtime
CMD ["python", "function.py"]