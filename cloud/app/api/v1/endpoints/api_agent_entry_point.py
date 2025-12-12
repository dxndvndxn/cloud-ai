from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.agent_api import AgentAPIRequest, AgentAPIResponse
from app.schemas.response import ProcessResponse, ProcessedData
from app.services.agent_service import api_agent_init
from app.core.logger import logger
from app.core.exceptions import ProcessingException

router = APIRouter(tags=["processing"])


@router.post(
    "/api_agent_entry_point",
    response_model=ProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Запуск API агента",
    description="Принимает базовый endpoint, URL в свободной текстовой форме"
)
async def process_text_and_url(
        request: AgentAPIRequest
) -> AgentAPIResponse:
    """
    Обработка URL и текста.

    Args:
        request: Запрос с URL и текстом

    Returns:
        Результат обработки
    """
    try:
        logger.info(f"Получен запрос на обработку API агентом")
        processed_result = await api_agent_init(request)
        logger.info(f"Успешная обработка запроса")
        return processed_result

    except ValueError as e:
        logger.warning(f"Ошибка валидации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except ProcessingException as e:
        logger.error(f"Ошибка обработки: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )