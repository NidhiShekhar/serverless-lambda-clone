from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from prometheus_client import make_asgi_app

# Import routers from api folder
from api.routes_execution import router as execution_router
from api.routes_functions import router as function_router  # Assuming this exists

# Configure logging
log_level = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Serverless Functions Platform",
    description="API for deploying and executing serverless functions",
    version="0.1.0"
)

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