from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.request import ProcessRequest
from app.schemas.response import ProcessResponse, ProcessedData
from app.services.agent_service import agent_init_many, agent_init_one
from app.core.logger import logger
from app.core.exceptions import ProcessingException

router = APIRouter(tags=["processing"])


@router.post(
    "/process",
    response_model=ProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Обработка ТЗ на несколько тест-кейсов",
    description="Принимает текст ТЗ, возвращает количество тест-кейсов"
)
async def process_text_and_url(
        request: ProcessRequest
) -> ProcessResponse:
    """
    Обработка URL и текста.

    Args:
        request: Запрос с URL и текстом

    Returns:
        Результат обработки
    """
    try:
        logger.info(f"Получен запрос на обработку")

        # Вызов сервиса
        if request.type == "one":
            processed_result = await agent_init_one(request)
        elif request.type == "many":
            processed_result = await agent_init_many(request)
        else:
            processed_result = []

        logger.info(f"Успешная обработка запроса")

        return ProcessResponse(
            success=True,
            message="ТЗ успешно декомпозировано",
            processed_data=processed_result
        )

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