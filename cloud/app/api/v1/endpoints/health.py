from datetime import datetime

from fastapi import APIRouter, Depends
from app.schemas.response import HealthResponse
from app.core.logger import logger

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Проверка здоровья приложения.

    Returns:
        Статус приложения
    """
    logger.debug("Вызов health check")
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow()
    )