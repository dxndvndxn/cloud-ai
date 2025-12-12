from typing import Dict, Any, List, Set
from datetime import datetime
import requests
import os
import sys
import json
import yaml
import re
import zipfile
import shutil
from pathlib import Path
import asyncio
import websockets
from typing import List, Dict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import AsyncSessionLocal
from app.models.models import Case
from app.api.v1.endpoints.ws_manager import manager

from openai import OpenAI

from app.core.logger import logger
from app.schemas.request import ProcessRequest
from app.schemas.agent_ui import AgentUIRequest, AgentUIResponse
from app.schemas.agent_api import AgentAPIRequest, AgentAPIResponse


def create_files_from_json(structure, base_path="."):
    """
    Рекурсивно создаёт директории и файлы на основе JSON-структуры.

    :param structure: dict — JSON-структура (вложенные словари = каталоги, строки = файлы)
    :param base_path: str — базовый путь, откуда начинать создание
    """
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # Это директория — создаём её и рекурсивно обрабатываем содержимое
            os.makedirs(path, exist_ok=True)
            create_files_from_json(content, path)
        elif isinstance(content, str):
            # Это файл — создаём его и записываем содержимое
            # Убеждаемся, что родительская директория существует
            parent_dir = os.path.dirname(path)
            os.makedirs(parent_dir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            raise ValueError(f"Неподдерживаемый тип содержимого для '{name}': {type(content)}")


def delete_directory_structure(structure: Dict[str, Any], root_path: str = ".") -> None:
    """
    Удаляет папки и файлы, описанные в структуре directory_structure,
    начиная с указанного корневого пути.

    :param structure: Словарь с ключом "directory_structure", содержащий вложенную структуру.
    :param root_path: Путь, относительно которого удаляются файлы и папки (по умолчанию — текущая директория).
    """
    directory_structure = structure.get("directory_structure", {})

    def _delete_recursive(current_path: str, items: Dict[str, Any]) -> None:
        for name, content in items.items():
            full_path = os.path.join(current_path, name)
            if isinstance(content, dict):
                # Это папка — рекурсивно обрабатываем её содержимое
                _delete_recursive(full_path, content)
                # После рекурсивного удаления содержимого — удаляем саму папку
                if os.path.exists(full_path):
                    shutil.rmtree(full_path)
            else:
                # Это файл — удаляем его
                if os.path.exists(full_path):
                    os.remove(full_path)

    _delete_recursive(root_path, directory_structure)


import yaml
from typing import Any, Dict, List, Set
import re

# Глобальное хранилище для рекурсивных ссылок
all_refs: Set[str] = set()

def extract_refs(obj: Any) -> None:
    """Рекурсивно собирает все $ref из объекта."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == '$ref' and isinstance(value, str):
                all_refs.add(value)
            else:
                extract_refs(value)
    elif isinstance(obj, list):
        for item in obj:
            extract_refs(item)

def resolve_schema_name(ref: str) -> str:
    """Извлекает имя схемы из $ref вида '#/components/schemas/Name'."""
    match = re.match(r'^#/(components/[^/]+/)(.+)$', ref)
    if match:
        return match.group(2)  # Например, "User", "ErrorResponse"
    return ref

def filter_components(original_components: Dict[str, Any], used_refs: Set[str]) -> Dict[str, Any]:
    """Оставляет в components только те элементы, на которые есть ссылки."""
    if not original_components:
        return {}

    filtered = {}
    # Поддерживаемые секции: schemas, responses, parameters, examples, requestBodies и т.д.
    for comp_type, items in original_components.items():
        if not isinstance(items, dict):
            continue
        filtered[comp_type] = {}
        for name, item in items.items():
            full_ref = f"#/components/{comp_type}/{name}"
            if full_ref in used_refs:
                filtered[comp_type][name] = item
                # Также ищем ссылки внутри самого компонента (например, схема ссылается на другую)
                extract_refs(item)
    return filtered

def filter_openapi_full(openapi_data: Dict[str, Any], selected_tags: List[str]) -> Dict[str, Any]:
    global all_refs
    all_refs = set()

    # 1. Фильтруем paths по тегам
    filtered_paths = {}
    for path, path_item in openapi_data.get('paths', {}).items():
        filtered_path_item = {}
        for method, operation in path_item.items():
            operation_tags = operation.get('tags', [])
            if any(tag in selected_tags for tag in operation_tags):
                filtered_path_item[method] = operation
                extract_refs(operation)
        if filtered_path_item:
            filtered_paths[path] = filtered_path_item

    # 2. Извлекаем компоненты, на которые есть ссылки (рекурсивно)
    original_components = openapi_data.get('components', {})
    used_refs = set(all_refs)
    # Повторяем проходы, пока не перестанут находиться новые ссылки (до фиксированной точки)
    prev_len = -1
    while len(used_refs) != prev_len:
        prev_len = len(used_refs)
        temp_filtered = {}
        for comp_type, items in original_components.items():
            if not isinstance(items, dict):
                continue
            for name, item in items.items():
                full_ref = f"#/components/{comp_type}/{name}"
                if full_ref in used_refs:
                    extract_refs(item)  # Может добавить новые $ref
        used_refs.update(all_refs)

    # 3. Формируем результат
    result = {
        'openapi': openapi_data.get('openapi'),
        'info': openapi_data.get('info'),
    }

    # Опционально копируем глобальные секции
    for key in ['servers', 'security', 'tags', 'externalDocs']:
        if key in openapi_data:
            result[key] = openapi_data[key]

    result['paths'] = filtered_paths

    # Фильтруем components
    filtered_comp = {}
    for comp_type, items in original_components.items():
        if not isinstance(items, dict):
            continue
        filtered_items = {}
        for name, item in items.items():
            full_ref = f"#/components/{comp_type}/{name}"
            if full_ref in used_refs:
                filtered_items[name] = item
        if filtered_items:
            filtered_comp[comp_type] = filtered_items

    if filtered_comp:
        result['components'] = filtered_comp

    return result


async def insert_case(item: Dict[str, str], request: ProcessRequest) -> Dict[str, Any]:
    """
    Асинхронная вставка кейсов в базу данных
    Возвращает словарь со всеми полями созданной записи
    """
    if not item:
        return {}

    async with AsyncSessionLocal() as session:
        try:
            if request.caseType == "ui":
                ct = False
            else:
                ct = True

            case = Case(
                name=item["name"],
                description=item["description"],
                allure=item["allure"],
                type=ct,
            )

            session.add(case)
            await session.flush()  # Получаем ID

            # Обновляем объект из БД, чтобы получить все поля
            await session.refresh(case)

            await session.commit()

            # Преобразуем объект Case в словарь
            case_dict = {
                "id": case.id,
                "name": case.name,
                "description": case.description,
                "caseType": case.type,
                "status": "alure_done",
                "allureCode": case.allure,
                "code": ""
                # Добавьте другие поля вашей модели, если они есть
                # "created_at": case.created_at,
                # "updated_at": case.updated_at,
            }

            logger.info(f"✅ Успешно добавлена запись с ID: {case.id}")
            return case_dict

        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Ошибка при вставке данных: {e}")
            raise  # Пробрасываем исключение дальше, чтобы обработать на уровне выше


async def insert_cases_batch(data: List[Dict[str, str]]) -> list:
    """
    Асинхронная вставка кейсов в базу данных
    """
    if not data:
        return 0

    inserted_count = 0
    async with AsyncSessionLocal() as session:
        try:
            inserted_cases = []

            for item in data:
                case = Case(name=item["name"], description=item["description"])
                session.add(case)
                await session.flush()  # Получаем ID без коммита
                inserted_cases.append(case)

            await session.commit()

            # Теперь у всех объектов есть ID
            inserted_ids = [case.id for case in inserted_cases]
            logger.info(f"✅ Успешно добавлено {len(inserted_ids)} записей с ID: {inserted_ids}")
            return inserted_ids

        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Ошибка при вставке данных: {e}")


async def ui_agent_init(request: AgentUIRequest) -> AgentUIResponse | None:

    logger.info(f"Начало работы агента планировщика")

    ui_url = request.ui_url
    text = request.text

    try:

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        response = requests.get(ui_url, headers=headers, timeout=10)
        site_page_html = response.text
        site_page_html = re.sub(r'<path\b[^>]*>', '', site_page_html, flags=re.IGNORECASE)
        site_page_html = re.sub(r'<svg\b[^>]*>', '', site_page_html, flags=re.IGNORECASE)
        logger.info(f"{ui_url}")
        logger.info(f"{site_page_html}")


        api_key = "ZDRmY2QzMGUtODNlYi00YWY4LWI2NjEtYmNiZjcwZTYxNjRj.a131dc7c5942fbe66d1ecb8cae5f9ac4"
        url = "https://foundation-models.api.cloud.ru/v1"

        client = OpenAI(
            api_key=api_key,
            base_url=url
        )

        response_plan = client.chat.completions.create(
            model="Qwen/Qwen3-Next-80B-A3B-Instruct",
            max_tokens=10000,
            temperature=0.1,
            presence_penalty=0,
            top_p=0.95,
            messages=[
                {
                    "role": "system",
                    "content": f"""Напиши подробный тест-план UI страницы по следующему ТЗ: {text}.
URL тестируемой страницы: {ui_url}.
HTML тестируемой страницы: {site_page_html}.
План верни в формате markdown.""",
                }
            ]
        )

        logger.info(f"Ответ от модели-планировщика получен")


        result_plan = response_plan.choices[0].message.content
        with open("test_plan.yaml", "w", encoding="utf-8") as f:
            yaml.dump(result_plan, f, allow_unicode=True, default_flow_style=False)
        await manager.broadcast({"test_plan": result_plan})
        logger.info(f"Тест-план записан в файл и передан в сокет")


        logger.info(f"Начало работы кодового агента")
        await manager.broadcast({"status": "Идет генерация кода"})

        response_code = client.chat.completions.create(
            model="Qwen/Qwen3-Coder-480B-A35B-Instruct",
            max_tokens=50000,
            temperature=0.3,
            presence_penalty=0,
            top_p=0.95,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": f"""
Ты — автогенератор тестов. На вход ты получаешь:

Тест-план в виде структурированного текста (например, список сценариев с шагами и ожидаемыми результатами).
HTML-код тестируемой веб-страницы.
Твоя задача — сгенерировать полностью рабочие автоматизированные тесты с использованием Playwright, pytest и Allure. Все тесты должны быть организованы в строго заданной структуре директорий, чтобы их можно было переиспользовать в разных проектах. Сгенерированный код должен корректно запускаться одной и той же командой: pytest --alluredir=./allure-results

Ты обязан вернуть только один JSON-объект со следующей структурой:

В корне — ключ "directory_structure".
Значение этого ключа — вложенный словарь, отражающий иерархию папок и файлов.
Каждый листовой элемент (файл) содержит полный исполняемый код этого файла как строку.
Все импорты, конфигурации и фикстуры должны быть включены.
Используй page object model (POM): каждый уникальный элемент страницы — в отдельном классе.
Все тесты должны быть покрыты Allure-декораторами (@allure.feature, @allure.story, @allure.step и т.д.).
В корне проекта должен быть pytest.ini или conftest.py, если это необходимо для запуска.
Убедись, что Playwright инициализируется и закрывается корректно через фикстуры.
Не включай внешние зависимости, кроме playwright, pytest, allure-pytest.

ФОРМАТ ВЫВОДЫ СТРОГО JSON:
{{
  "directory_structure": {{
    "pages/": {{...}},
    "tests/": {{...}},
  }},
}}


Важно:

Никакого пояснительного текста вне JSON.
Никаких markdown-блоков.
Ответ должен быть валидным JSON, пригодным для немедленного сохранения на диск и запуска.
Все пути и имена файлов должны быть на английском языке, в snake_case.
Сгенерируй структуру и код на основе предоставленного тест-плана и HTML.""",
                },
                {
                    "role": "user",
                    "content": f"""Тест-план: {result_plan} \n\n HTML-код: {site_page_html}"""
                }
            ]
        )

        logger.info(f"Ответ от кодовой модели получен")

        result_code = json.loads(response_code.choices[0].message.content)
        await manager.broadcast(result_code)
        logger.info(f"Каталог с тестами передан в сокет")
        await manager.broadcast({"status": "Идет проверка кода"})


        import subprocess

        code_arr = [result_code]
        tries = 0

        test_done = False
        while test_done == False & tries < 3:

            try:

                create_files_from_json(code_arr[-1]["directory_structure"])
                logger.info(f"Каталог с тестами создан на диске")

                # Выполняем команду pytest с опцией --alluredir
                result = subprocess.run(
                    ["pytest", "--alluredir=./allure-results"],
                    capture_output=True,  # Захватываем stdout и stderr
                    text=True  # Возвращаем строки, а не байты
                )

                # Проверяем код возврата
                if result.returncode <= 1:
                    print("Тесты прошли успешно.")
                    test_done = True
                    await manager.broadcast({"status": f"Код исправолен, можно скачать архив с тестами"})
                else:
                    print("Тесты завершились с ошибками.")
                    delete_directory_structure(code_arr[-1])
                    print("Директории удалены.")

                    await manager.broadcast({"status": f"В коде обнаружены ошибки. Попытка исправить №{tries + 1}"})

                    new_response_code = client.chat.completions.create(
                        model="Qwen/Qwen3-Coder-480B-A35B-Instruct",
                        max_tokens=50000,
                        temperature=0.3,
                        presence_penalty=0,
                        top_p=0.95,
                        response_format={"type": "json_object"},
                        messages=[
                            {
                                "role": "system",
                                "content": f"""Тесты в этих директориях запускаются с ошибками. Найди и исправь ошибки. В ответ верни строго JSON с исправленным содержанием каталогов и файлов. Внимательно следи за импортами, пустыми папками и правильными названиями функций и классов. В корне json обязательно должен быть ключ 'directory_structure'""",
                            },
                            {
                                "role": "system",
                                "content": f"""{code_arr[-1]}""",
                            },
                        ]
                    )
                    print("Исправленный код получен")
                    new_result_code = json.loads(new_response_code.choices[0].message.content)
                    code_arr.append(new_result_code)
                    print("json распарсился")
                    await manager.broadcast(code_arr[-1])
                    logger.info(f"Каталог с исправленными тестами передан в сокет")
                    await manager.broadcast({"status": "Проверка исправленного кода"})

            except FileNotFoundError:
                print("Ошибка: pytest не найден. Убедитесь, что он установлен и доступен в PATH.")
            except Exception as e:
                print(f"Произошла непредвиденная ошибка: {e}")

            tries = (tries + 1)

        if test_done == True:
            await manager.broadcast({"status": f"Код исправолен, можно скачать архив с тестами"})
        else:
            await manager.broadcast({"status": f"Лимит попыток исчерпан, код лучше проверить вручную"})

        create_files_from_json(code_arr[-1]["directory_structure"])
        logger.info(f"Каталог с тестами создан на диске")

        return AgentUIResponse(success=True)


    except Exception as e:
        logger.error(f"Ошибка при обработке: {str(e)}")
        raise



async def api_agent_init(request: AgentAPIRequest) -> AgentAPIResponse | None:
    logger.info(f"Начало работы агента планировщика")

    base_endpoint = request.base_endpoint
    token = request.token
    text = request.text

    input_file = 'openapi.yaml'
    selected_tags = request.tags

    with open(input_file, 'r', encoding='utf-8') as f:
        openapi_data = yaml.safe_load(f)

    open_api = filter_openapi_full(openapi_data, selected_tags)

    try:

        api_key = "ZDRmY2QzMGUtODNlYi00YWY4LWI2NjEtYmNiZjcwZTYxNjRj.a131dc7c5942fbe66d1ecb8cae5f9ac4"
        url = "https://foundation-models.api.cloud.ru/v1"

        client = OpenAI(
            api_key=api_key,
            base_url=url
        )

        response_plan = client.chat.completions.create(
            model="Qwen/Qwen3-Next-80B-A3B-Instruct",
            max_tokens=10000,
            temperature=0.1,
            presence_penalty=0,
            top_p=0.95,
            messages=[
                {
                    "role": "system",
                    "content": f"""Ты — эксперт по ручному тестированию REST API. На вход тебе передаются:

        1. **base_endpoint** — базовый URL тестируемого API (например: https://api.example.com/v1/)
        2. **open_api** — релевантная часть документации OpenAPI/Swagger для тестируемых эндпоинтов
        3. **token** — Bearer токен для авторизации (если требуется)
        4. **text** — краткое описание задания и требований к тестированию

        Твоя задача:
        Создать подробный, структурированный план ручных тест-кейсов для API в формате, подходящем для последующей автоматизации. План должен:

        1. **Следовать шаблону AAA (Arrange–Act–Assert)** в каждом тест-кейсе
        2. **Включать мета-информацию**, совместимую с Allure TestOps:
           - Уникальный ID или тег (например: TC_API_USERS_01)
           - Заголовок (краткое название теста)
           - Приоритет (high, medium, low)
           - Эпик / фича (определи на основе текста задания и OpenAPI)
           - Описание (опционально — пояснение цели теста)
        3. **Быть достаточно точным и недвусмысленным**, чтобы его можно было напрямую использовать другим LLM-агентом для генерации автоматизированных тестов (например, на Pytest/Requests)
        4. **Покрывать следующие аспекты**:
           - Позитивные сценарии (валидные запросы)
           - Негативные сценарии:
             - Невалидные/отсутствующие обязательные параметры
             - Неправильные типы данных
             - Выход за граничные значения
             - Невалидные форматы данных
             - Ошибки авторизации/аутентификации
           - Валидацию кодов ответа HTTP
           - Валидацию схемы ответа (структура JSON)
           - Проверку бизнес-логики, если указана в требованиях

        **Формат вывода:**,
        markdown

        ...

        **Важные правила:**

        1. **Используй только документацию из open_api** — не выдумывай эндпоинты, параметры или схемы, которых нет в предоставленной спецификации
        2. **Учитывай авторизацию** — используй токен только если он указан и требуется для тестируемых эндпоинтов
        3. **Определяй приоритеты разумно**:
           - High: основные happy-path сценарии, критичная бизнес-логика
           - Medium: валидации полей, граничные значения
           - Low: дополнительные проверки, негативные сценарии с маловероятными данными
        4. **Указывай полные URL** — используй base_endpoint для построения полных путей к API
        5. **Будь конкретен в проверках** — вместо "проверить ответ" указывай конкретные поля, значения, типы данных
        6. **Тестируй ошибки** — включай тесты на 400, 401, 403, 404, 422 и другие релевантные коды ошибок
        7. **Учитывай зависимости** — если для теста нужны предварительные данные (например, созданный ресурс), отрази это в шагах Arrange

        **Теперь сгенерируй план тест-кейсов на основе следующих входных данных:**
        Base endpoint: {base_endpoint}
        OpenAPI документация: {open_api}
        Token: {token}
        Требования к тестированию: {text}"""
                }
            ]
        )

        logger.info(f"Ответ от модели-планировщика получен")


        result_plan = response_plan.choices[0].message.content
        with open("test_plan.yaml", "w", encoding="utf-8") as f:
            yaml.dump(result_plan, f, allow_unicode=True, default_flow_style=False)
        await manager.broadcast({"test_plan": result_plan})
        logger.info(f"Тест-план записан в файл и передан в сокет")


        logger.info(f"Начало работы кодового агента")
        await manager.broadcast({"status": "Идет генерация кода"})

        response_code = client.chat.completions.create(
            model="Qwen/Qwen3-Coder-480B-A35B-Instruct",
            max_tokens=50000,
            temperature=0.1,
            presence_penalty=0,
            top_p=0.95,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": f"""Ты — эксперт по автоматизации API-тестов на Python с использованием pytest, requests и Allure Report (v2+).
        По предоставленному плану тест-кейсов ты должен сгенерировать полностью рабочие автоматизированные тесты, следуя строгим требованиям ниже.

        **Ключевые правила:**
        - **Язык**: Python 3.9+
        - **Фреймворки**: pytest, requests, allure-pytest, pydantic (для валидации схем)
        - **Архитектура**: Client-Service Pattern — API-клиенты в отдельных классах, бизнес-логика в сервисах
        - **Тестовые данные**: Фикстуры pytest для подготовки данных

        **Allure-декораторы** (используй только актуальные):
        - `@allure.title("...")` → из title тест-плана
        - `@allure.feature("...")` → значение из поля epic или feature тест-плана
        - `@allure.story("...")` → значение из title или логической группы
        - `@allure.tag("CRITICAL" | "NORMAL" | "LOW")` → на основе priority:
          - high → "CRITICAL"
          - medium → "NORMAL"
          - low → "LOW"
        - `@allure.label("priority", priority)` → передавай исходное значение (high/medium/low)
        - `@allure.label("owner", "automation-team")`
        - `@allure.link(url, name="JIRA")` → если в тест-плане есть jira_id

        **Структура тестов:**
        - **Шаги теста**: Каждый шаг из AAA должен быть обёрнут в `with allure.step("..."):`
          - "Arrange: ...", "Act: ...", "Assert: ..."
          - Или по смыслу: "Prepare test data", "Send POST request", "Validate response status code"
        - **Имена тестов**:
          - Функция: `def test_<id_snake_case>(...)` — например, `test_tc_users_create_01(...)`
          - Класс: `class Test<FeatureName>:` — например, `class TestUsers:`
        - **Валидация ответов**:
          - Проверка HTTP-кодов: `assert response.status_code == 200`
          - Валидация JSON-схемы (если есть спецификация)
          - Проверка бизнес-логики

        **Формат вывода:**
        Верни JSON-объект с полной структурой проекта:
        ```json
        {{
          "directory_structure": {{
            "tests/": {{
              "api/": {{
                "clients/": {{
                  "users_client.py": "...",
                  "base_client.py": "..."
                }},
                "schemas/": {{
                  "users_schemas.py": "..."
                }},
                "test_users.py": "..."
              }},
              "conftest.py": "...",
              "test_data/": {{
                "users_data.py": "..."
              }}
            }}
          }}
        }}
        Содержимое файлов:

        conftest.py:

        Фикстура base_url с поддержкой командной строки (--base-url)

        Фикстура auth_headers для передачи токена авторизации

        Фикстура api_client для инициализации API-клиентов

        clients/base_client.py:

        Базовый класс API-клиента с методами для отправки запросов

        Обработка заголовков, токенов, базового URL

        Логирование запросов/ответов для Allure

        clients/<resource>_client.py:

        Класс с методами для конкретного ресурса API

        Например: UsersClient с методами create_user(), get_user(), update_user(), delete_user()

        schemas/<resource>_schemas.py:

        Pydantic-модели для валидации запросов и ответов

        Схемы для валидных и ошибочных ответов

        test_data/<resource>_data.py:

        Тестовые данные: валидные, невалидные, граничные значения

        Генераторы тестовых данных

        test_<resource>.py:

        Непосредственно тесты, использующие клиенты и фикстуры

        Следование паттерну AAA

        Запрещено:

        Использовать @allure.manual, @mark.manual — это автоматизированные тесты!

        Хардкодить URL, параметры, токены — используй фикстуры и конфигурацию

        Дублировать логику отправки запросов — выноси в клиенты

        Проверять "сырые" JSON без валидации схемы

        Использовать sleep/таймауты без необходимости

        Обработка авторизации:

        Если в плане указан токен, используй его в заголовках Authorization: Bearer {token}

        Если токен динамический, реализуй фикстуру для его получения

        Тестируй сценарии с невалидным/отсутствующим токеном

        Валидация ответов:

        Код статуса HTTP

        Схема JSON-ответа

        Конкретные значения полей

        Заголовки ответа (если важно)

        Время ответа (если есть требования к производительности)

        Пример теста:
        @allure.feature("Users Management")
        @allure.story("Create new user")
        @allure.tag("CRITICAL")
        @allure.label("priority", "high")
        def test_tc_users_create_01(api_client):
            with allure.step("Arrange: Prepare valid user data"):
                test_data = valid_user_data()

            with allure.step("Act: Send POST request to create user"):
                response = api_client.users.create_user(test_data)

            with allure.step("Assert: Verify response"):
                assert response.status_code == 201
                assert response.json()["email"] == test_data["email"]
                UserResponse.validate(response.json())  # валидация схемы

        Теперь сгенерируй структуру проекта и код на Python на основе следующего тест-плана:
        {result_plan}

        Дополнительная информация:

        Base endpoint: {base_endpoint}

        OpenAPI спецификация: {open_api}

        Token: {token}""",
                }
            ]
        )

        logger.info(f"Ответ от кодовой модели получен")

        result_code = json.loads(response_code.choices[0].message.content)
        await manager.broadcast(result_code)
        logger.info(f"Каталог с тестами передан в сокет")
        await manager.broadcast({"status": "Идет проверка кода"})


        import subprocess

        code_arr = [result_code]
        tries = 0

        test_done = False
        while test_done == False & tries < 3:

            try:

                create_files_from_json(code_arr[-1]["directory_structure"])
                logger.info(f"Каталог с тестами создан на диске")

                # Выполняем команду pytest с опцией --alluredir
                result = subprocess.run(
                    ["pytest", "--alluredir=./allure-results"],
                    capture_output=True,  # Захватываем stdout и stderr
                    text=True  # Возвращаем строки, а не байты
                )

                # Проверяем код возврата
                if result.returncode <= 1:
                    print("Тесты прошли успешно.")
                    test_done = True
                    await manager.broadcast({"status": f"Код исправолен, можно скачать архив с тестами"})
                else:
                    print("Тесты завершились с ошибками.")
                    delete_directory_structure(code_arr[-1])
                    print("Директории удалены.")

                    await manager.broadcast({"status": f"В коде обнаружены ошибки. Попытка исправить №{tries + 1}"})

                    new_response_code = client.chat.completions.create(
                        model="Qwen/Qwen3-Coder-480B-A35B-Instruct",
                        max_tokens=50000,
                        temperature=0.3,
                        presence_penalty=0,
                        top_p=0.95,
                        response_format={"type": "json_object"},
                        messages=[
                            {
                                "role": "system",
                                "content": f"""Тесты в этих директориях запускаются с ошибками. Найди и исправь ошибки. В ответ верни строго JSON с исправленным содержанием каталогов и файлов. Внимательно следи за импортами, пустыми папками и правильными названиями функций и классов. В корне json обязательно должен быть ключ 'directory_structure'""",
                            },
                            {
                                "role": "system",
                                "content": f"""{code_arr[-1]}""",
                            },
                        ]
                    )
                    print("Исправленный код получен")
                    new_result_code = json.loads(new_response_code.choices[0].message.content)
                    code_arr.append(new_result_code)
                    print("json распарсился")
                    await manager.broadcast(code_arr[-1])
                    logger.info(f"Каталог с исправленными тестами передан в сокет")
                    await manager.broadcast({"status": "Проверка исправленного кода"})

            except FileNotFoundError:
                print("Ошибка: pytest не найден. Убедитесь, что он установлен и доступен в PATH.")
            except Exception as e:
                print(f"Произошла непредвиденная ошибка: {e}")

            tries = (tries + 1)

        if test_done == True:
            await manager.broadcast({"status": f"Код исправолен, можно скачать архив с тестами"})
        else:
            await manager.broadcast({"status": f"Лимит попыток исчерпан, код лучше проверить вручную"})

        create_files_from_json(code_arr[-1]["directory_structure"])
        logger.info(f"Каталог с тестами создан на диске")

        return AgentAPIResponse(success=True)


    except Exception as e:
        logger.error(f"Ошибка при обработке: {str(e)}")
        raise