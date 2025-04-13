from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from prometheus_client import make_asgi_app
from contextlib import asynccontextmanager
from backend.metrics import REQUEST_COUNT, REQUEST_LATENCY, FUNCTION_EXECUTIONS, FUNCTION_EXECUTION_TIME
import time

# Import routers from api folder
from backend.api.routes_execution import router as execution_router
from backend.api.routes_functions import router as function_router  # Assuming this exists
from backend.engine.docker_utils import check_docker_availability, check_docker_permissions

# make sure you are in root directory and then run uvicorn backend.main:app --reload
# Configure logging
log_level = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
# Add FastAPI startup event
@asynccontextmanager
async def lifespan(app: FastAPI):
    import sys
    if not check_docker_availability():
        sys.exit("Docker is required but not available")
    if not check_docker_permissions():
        sys.exit("Insufficient permissions to use Docker")
    yield  # Application lifespan continues here

app = FastAPI(
    title="Serverless Functions Platform",
    description="API for deploying and executing serverless functions",
    version="0.1.0",
    lifespan=lifespan # Use the lifespan context manager
)


# Add middleware to track request metrics
@app.middleware("http")
async def track_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    # Record request latency
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(latency)

    # Record request count
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        http_status=response.status_code
    ).inc()

    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(function_router, prefix="/functions", tags=["functions"])
app.include_router(execution_router, tags=["execution"])

# Define root endpoint
@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "message": "Serverless Functions API is running"}

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount(os.getenv("PROMETHEUS_METRICS_PATH", "/metrics"), metrics_app)


# Main entrypoint for Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


