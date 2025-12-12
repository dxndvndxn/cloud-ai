import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    # Настройки приложения
    APP_NAME: str = "AI DevTools Hack"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Настройки сервера
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5174", "http://localhost:5173", "http://10.108.73.203:5173"]

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Время жизни (если понадобится для токенов, сессий и т.д.)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class ConfigDict:
        env_file = ".env"
        case_sensitive = True


settings = Settings()