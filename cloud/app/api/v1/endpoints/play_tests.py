from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
import pytest
import zipfile
import subprocess
import sys
import os
import webbrowser

router = APIRouter(tags=["processing"])


@router.post(
    "/play_tests",
    status_code=status.HTTP_200_OK,
    summary="Скачать тесты",
    description="Скачать тесты"
)
async def process_text_and_url() -> FileResponse:
    """
    Скачать тесты

    Returns:
        Архив с тестами
    """
    try:
    # Запускаем pytest
        paths_to_archive = [
            'tests',
            'pages',
            'requirements.txt',
            'pytest.ini'
        ]

        archive_name = 'tests_from_agent.zip'

        def add_to_zip(zipf, path):
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Сохраняем относительный путь внутри архива
                        arcname = os.path.relpath(file_path, start='.')
                        zipf.write(file_path, arcname=arcname)
            elif os.path.isfile(path):
                zipf.write(path, arcname=os.path.basename(path))
            else:
                print(f"Предупреждение: {path} не найден и будет пропущен.")

        # Создаём архив
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for path in paths_to_archive:
                add_to_zip(zipf, path)

        print(f"Архив '{archive_name}' успешно создан.")

        return FileResponse(
            path="tests_from_agent.zip",
            media_type='application/zip',
            filename="tests_from_agent.zip"  # имя файла, которое увидит пользователь
        )


    except Exception as e:
        print(f"❌ Ошибка при запуске pytest: {e}")

    return 0
