"""
Veritas - Fake News Detection Engine
Production-grade FastAPI backend
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging
import uvicorn
from routers import verify

from contextlib import asynccontextmanager
from routers import analyze, history, health
from utils.logger import setup_logger


logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app):
    logger.info("🚀 Veritas API starting up...")
    from services.model_service import ModelService
    ModelService.get_instance()
    logger.info("✅ ML models loaded successfully")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    lifespan=lifespan,
    title="Veritas API",
    description="Production-grade fake news detection powered by DistilBERT + TF-IDF ensemble",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__}
    )

# Include routers
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(history.router, prefix="/api/v1", tags=["History"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(verify.router, prefix="/api/v1", tags=["Verification"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
