from typing import Literal, Optional
from pydantic import BaseModel, Field, HttpUrl


class ProcessRequest(BaseModel):
    """Схема запроса для обработки данных."""

    ui_url: str | None = Field(
        default=None,
        description="one или many для пакетной или одиночной обработки",
        max_length=100
    )

    token: str | None = Field(
        default=None,
        description="Токен авторизации",
        max_length=100
    )

    openapi: str | None = Field(
        default=None,
        description="OpenAPI спецификация",
        max_length=100
    )

    endpoint: str | None = Field(
        default=None,
        description="API эндпоинт",
        max_length=100
    )

    caseType: Literal["ui", "api"] = Field(
        ...,
        description="one или many для пакетной или одиночной обработки",
        min_length=1,
        max_length=4,
        example="ui"
    )

    type: Literal["one", "many"] = Field(
        ...,
        description="one или many для пакетной или одиночной обработки",
        min_length=1,
        max_length=4,
        example="one"
    )

    text: str = Field(
        ...,
        description="ТЗ для нескольких тест-кейсов.",
        min_length=1,
        max_length=10000,
        example="Пример ТЗ для нескольких тест-кейсов. ТЗ будет декомпозировано агентом на отдельные тест-кейсы."
    )