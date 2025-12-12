from fastapi import HTTPException, status
from typing import Any, Optional


class APIException(HTTPException):
    """Базовое исключение для API."""

    def __init__(
            self,
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail: Any = None,
            headers: Optional[dict] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ValidationException(APIException):
    """Исключение для ошибок валидации."""

    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "Ошибка валидации данных"
        )


class ProcessingException(APIException):
    """Исключение для ошибок обработки."""

    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail or "Ошибка обработки данных"
        )