from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.agent_ui import AgentUIRequest, AgentUIResponse
from app.schemas.response import ProcessResponse, ProcessedData
from app.services.agent_service import ui_agent_init
from app.core.logger import logger
from app.core.exceptions import ProcessingException

router = APIRouter(tags=["processing"])


@router.post(
    "/ui_agent_entry_point",
    response_model=AgentUIResponse,
    status_code=status.HTTP_200_OK,
    summary="Запуск UI агента",
    description="Принимает url и UI-спецификации в свободной текстовой форме"
)
async def process_text_and_url(
        request: AgentUIRequest
) -> AgentUIResponse:
    """
    Обработка URL и текста.

    Args:
        request: Запрос с URL и текстом

    Returns:
        Результат обработки
    """
    try:
        logger.info(f"Получен запрос на обработку")
        processed_result = await ui_agent_init(request)
        logger.info(f"Успешная обработка запроса")
        return AgentUIResponse(success=True)

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