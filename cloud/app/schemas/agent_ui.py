from typing import Literal, Optional
from pydantic import BaseModel, Field, HttpUrl


class AgentUIRequest(BaseModel):
    """Схема запроса для инициации UI агента."""

    ui_url: str = Field(
        description="Тестируемый URL",
        max_length=100
    )

    text: str = Field(
        description="UI-спецификация",
        max_length=10000
    )


class AgentUIResponse(BaseModel):
    """Схема ответа от UI агента."""

    success: bool = Field(
        ...,
        description="Успешность операции",
        example=True
    )