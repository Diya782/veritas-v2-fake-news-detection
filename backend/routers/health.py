from fastapi import APIRouter
from services.model_service import ModelService
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    ms = ModelService.get_instance()
    return {
        "status": "healthy",
        "models_loaded": ms.models_ready,
        "version": "2.0.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
