import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from .config import settings


def setup_logger(
        name: str = __name__,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None
) -> logging.Logger:
    """
    Настройка логгера.

    Args:
        name: Имя логгера
        log_level: Уровень логирования
        log_file: Файл для записи логов

    Returns:
        Настроенный логгер
    """
    if log_level is None:
        log_level = "DEBUG" if settings.DEBUG else "INFO"

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Форматтер
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Файловый обработчик (если указан файл)
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Отключаем логирование от других библиотек, если не в режиме DEBUG
    if not settings.DEBUG:
        logging.getLogger("uvicorn.access").disabled = True

    return logger


# Глобальный логгер
logger = setup_logger(settings.APP_NAME)