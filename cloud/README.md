# Cloud Backend - Локальная разработка

AI DevTools Hack - Backend API сервис на FastAPI.

## Требования

- Python 3.8+
- pip

## Быстрый запуск

### 1. Установка зависимостей

```bash
cd cloud
pip install -r requirements.txt
```

### 2. Запуск сервера

```bash
python run.py
```

Сервер запустится на `http://localhost:8000`

### 3. Проверка работы

- API документация: http://localhost:8000/docs
- Статус API: http://localhost:8000/

## Разработка

### Запуск в режиме разработки с автоперезагрузкой

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Настройка переменных среды

Создайте файл `.env` в папке `cloud`:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

## API Endpoints

- `GET /` - Информация о сервисе
- `GET /api/v1/health` - Проверка здоровья
- `POST /api/v1/ui-agent` - UI агент
- `POST /api/v1/api-agent` - API агент
- `WS /api/v1/ws` - WebSocket

## Troubleshooting

### Порт занят

```bash
lsof -i :8000
kill -9 <PID>
```

### Ошибки зависимостей

```bash
pip install --upgrade -r requirements.txt
