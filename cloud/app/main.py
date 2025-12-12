from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Запуск приложения
    logger.info(f"Запуск приложения {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Режим отладки: {'ВКЛ' if settings.DEBUG else 'ВЫКЛ'}")

    # Здесь можно инициализировать подключения к БД, кэшу и т.д.
    # async with lifespan_manager():
    #     yield

    yield

    # Остановка приложения
    # Здесь можно закрывать подключения к БД, кэшу и т.д.
    logger.info("Остановка приложения...")


def create_application() -> FastAPI:
    """Фабрика для создания приложения FastAPI."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="API для обработки текста и URL",
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5174", "http://localhost:5173", "http://100.114.47.28:5173/"],   #settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключение роутеров
    app.include_router(api_router)

    # Корневой эндпоинт
    @app.get("/")
    async def root():
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs" if settings.DEBUG else None
        }

    return app


# Создание экземпляра приложения
app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_config=None,  # Используем наш собственный логгер
        access_log=False  # Отключаем логирование доступа от uvicorn
    )