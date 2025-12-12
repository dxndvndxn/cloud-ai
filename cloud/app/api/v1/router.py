from fastapi import APIRouter

from app.api.v1.endpoints import health, play_tests, websocket, ui_agent_entry_point, api_agent_entry_point
from app.core.config import settings

api_router = APIRouter(prefix=settings.API_V1_PREFIX)

# Подключаем эндпоинты
api_router.include_router(health.router)
api_router.include_router(websocket.router)
api_router.include_router(ui_agent_entry_point.router)
api_router.include_router(api_agent_entry_point.router)
api_router.include_router(play_tests.router)