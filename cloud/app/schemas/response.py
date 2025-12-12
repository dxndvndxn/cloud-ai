from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class HealthResponse(BaseModel):
    """Схема ответа для проверки здоровья."""

    status: str = Field(
        ...,
        description="Статус приложения",
        example="healthy"
    )

    timestamp: datetime = Field(
        ...,
        description="Время проверки"
    )


class ProcessedData(BaseModel):
    """Схема обработанных данных."""

    cases_count: int = Field(
        ...,
        description="Количество тест-кейсов после декомпозиции",
        example=5
    )



class ProcessResponse(BaseModel):
    """Схема ответа для обработки данных."""

    success: bool = Field(
        ...,
        description="Успешность операции",
        example=True
    )

    message: str = Field(
        ...,
        description="Сообщение о результате",
        example="Данные успешно обработаны"
    )

    processed_data: list = Field(
        None,
        description="Обработанные данные"
    )

    error: Optional[str] = Field(
        None,
        description="Описание ошибки (если есть)"
    )