FROM python:3.9-slim

WORKDIR /app

# Copy requirements.txt if it exists and install dependencies
COPY requirements.txt* .
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Ensure the container gracefully handles the absence of function.py
CMD ["sh", "-c", "if [ -f function.py ]; then python function.py; else echo 'Error: function.py not found'; exit 1; fi"]