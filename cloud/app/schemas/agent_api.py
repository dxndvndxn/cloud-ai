from typing import Literal, Optional, List
from pydantic import BaseModel, Field, HttpUrl


class AgentAPIRequest(BaseModel):
    """Схема запроса для инициации API агента."""

    base_endpoint: str = Field(
        description="Тестируемый URL",
        max_length=100
    )

    tags: List[str] = Field(
        description="Тэги разделов спецификации через запятую",
        max_length=100
    )

    token: str = Field(
        description="Тэги разделов спецификации через запятую",
        max_length=100
    )

    text: str = Field(
        description="Требования",
        max_length=10000
    )


class AgentAPIResponse(BaseModel):
    """Схема ответа от API агента."""

    success: bool = Field(
        ...,
        description="Успешность операции",
        example=True
    )