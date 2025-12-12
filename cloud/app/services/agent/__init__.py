import os
import json
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dataclasses import dataclass


# Определяем структуру для тест-кейса
class TestCase(BaseModel):
    """Модель тест-кейса"""
    id: str = Field(description="Уникальный идентификатор тест-кейса")
    title: str = Field(description="Название тест-кейса")
    description: str = Field(description="Подробное описание тест-кейса")
    steps: List[str] = Field(description="Шаги для выполнения теста")
    expected_result: str = Field(description="Ожидаемый результат")
    priority: str = Field(description="Приоритет (High/Medium/Low)")
    test_type: str = Field(description="Тип теста (Functional/UI/API/Integration, etc.)")


class TestCaseList(BaseModel):
    """Список тест-кейсов"""
    test_cases: List[TestCase]


@dataclass
class TestCaseResult:
    """Результат обработки тест-кейсов"""
    success: bool
    test_cases: List[Dict[str, Any]]
    error_message: str = None


def create_test_cases_agent(user_input: str) -> TestCaseResult:
    """
    Агент для создания тест-кейсов на основе текстового описания задачи.

    Args:
        user_input: Текст с описанием задачи для разработки тест-кейсов

    Returns:
        TestCaseResult: Объект с результатами обработки
    """

    # Системный промпт для агента
    system_prompt = """Ты - эксперт по тестированию программного обеспечения. 
    Твоя задача - анализировать описание функциональности или требования 
    и создавать подробные, структурированные тест-кейсы.

    Инструкции:
    1. Внимательно проанализируй предоставленное описание
    2. Декомпозируй задачу на конкретные тест-кейсы
    3. Для каждого тест-кейса укажи:
       - Уникальный ID (например, TC001, TC002)
       - Четкое название
       - Подробное описание
       - Пошаговые инструкции
       - Ожидаемый результат
       - Приоритет (High/Medium/Low)
       - Тип теста

    4. Учни различные аспекты тестирования:
       - Позитивные сценарии
       - Негативные сценарии
       - Граничные случаи
       - Валидация данных

    5. Верни результат в строго заданном JSON формате.

    Пример формата вывода:
    {
        "test_cases": [
            {
                "id": "TC001",
                "title": "Успешная авторизация с валидными данными",
                "description": "Проверка возможности входа в систему с корректными учетными данными",
                "steps": ["1. Открыть страницу логина", "2. Ввести валидный email", "3. Ввести валидный пароль", "4. Нажать кнопку 'Войти'"],
                "expected_result": "Пользователь успешно авторизован, происходит редирект на главную страницу",
                "priority": "High",
                "test_type": "Functional"
            }
        ]
    }
    """

    try:
        # Инициализация клиента с использованием LangChain
        api_key = os.environ.get("API_KEY")
        base_url = "https://foundation-models.api.cloud.ru/v1"

        if not api_key:
            return TestCaseResult(
                success=False,
                test_cases=[],
                error_message="API_KEY не найден в переменных окружения"
            )

        # Создаем LLM клиент
        llm = ChatOpenAI(
            model="Qwen/Qwen3-235B-A22B-Instruct-2507",
            openai_api_key=api_key,
            base_url=base_url,
            temperature=0.5,
            max_tokens=2500,
            top_p=0.95,
            presence_penalty=0
        )

        # Создаем парсер для структурированного вывода
        parser = PydanticOutputParser(pydantic_object=TestCaseList)

        # Формируем сообщения
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"{user_input}\n\n{parser.get_format_instructions()}")
        ]

        # Отправляем запрос к модели
        response = llm.invoke(messages)

        # Парсим ответ
        result = parser.parse(response.content)

        # Конвертируем Pydantic модели в словари
        test_cases_dict = []
        for test_case in result.test_cases:
            test_cases_dict.append(test_case.dict())

        return TestCaseResult(
            success=True,
            test_cases=test_cases_dict
        )

    except json.JSONDecodeError as e:
        return TestCaseResult(
            success=False,
            test_cases=[],
            error_message=f"Ошибка парсинга JSON: {str(e)}"
        )
    except Exception as e:
        return TestCaseResult(
            success=False,
            test_cases=[],
            error_message=f"Произошла ошибка: {str(e)}"
        )