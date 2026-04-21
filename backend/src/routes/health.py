from fastapi import APIRouter

from src.core.config import settings


router = APIRouter(tags=["health"])

# Just to check if the server is up and healthy

@router.get("/")
async def health_check():
    return {"status": "online", "model": settings.model_name, "service": settings.app_name}
