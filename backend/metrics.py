# Import Prometheus libraries (Counter, Histogram)

# Define Counter metric for:
# - Total API requests
# - Total function execution requests
# - Total failed executions

# Define Histogram metric for:
# - Function execution time (seconds)

# In each API route:
# - Increment relevant counters
# - Observe execution time in histograms

# Optional:
# Add custom labels like:
# - function_name
# - execution_status (success/failure)


from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

# Define metrics
REQUEST_COUNT = Counter(
    'app_request_count',
    'Application Request Count',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Application Request Latency',
    ['method', 'endpoint']
)

FUNCTION_EXECUTIONS = Counter(
    'serverless_function_executions_total',
    'Number of serverless function executions',
    ['language', 'status']
)

FUNCTION_EXECUTION_TIME = Histogram(
    'serverless_function_execution_seconds',
    'Time spent executing serverless functions',
    ['language', 'function_name', 'status']
)