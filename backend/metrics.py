from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

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
