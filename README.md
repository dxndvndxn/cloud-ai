# Cloud Hack - Docker Setup

Этот проект состоит из двух основных компонентов:
- **cloud** - Python/FastAPI backend
- **cloud-ui** - React frontend

## Предварительные требования

- Docker
- Docker Compose
- Свободные порты 8000 (backend) и 5173 (frontend)

## Быстрый старт

### 1. Клонирование и переход в директорию проекта

```bash
cd /path/to/cloud-hack
```

### 2. Запуск всех сервисов

```bash
docker-compose up --build -d
```

Эта команда:
- Соберет образы для обоих сервисов
- Запустит контейнеры в фоновом режиме
- Настроит сеть между сервисами

### 3. Проверка статуса

```bash
docker-compose ps
```

Ожидаемый вывод:
```
NAME                IMAGE                      COMMAND                  SERVICE             STATUS
cloud-backend       cloud-hack-cloud-backend   "python run.py"          cloud-backend       Up (healthy)
cloud-ui            cloud-hack-cloud-ui        "docker-entrypoint.s…"   cloud-ui            Up
```

### 4. Доступ к приложениям

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs (в режиме отладки)

## Управление контейнерами

### Остановка сервисов

```bash
docker-compose down
```

### Остановка с удалением volumes и orphan контейнеров

```bash
docker-compose down --remove-orphans --volumes
```

### Перезапуск сервисов

```bash
docker-compose restart
```

### Перезапуск конкретного сервиса

```bash
docker-compose restart cloud-backend
# или
docker-compose restart cloud-ui
```

## Сборка без кэша

Если нужно пересобрать образы без использования кэша:

```bash
# Остановить контейнеры
docker-compose down

# Очистить кэш Docker
docker system prune -a -f

# Собрать без кэша
DOCKER_BUILDKIT=0 docker-compose build --no-cache

# Запустить
docker-compose up -d
```

## Просмотр логов

### Логи всех сервисов

```bash
docker-compose logs
```

### Логи конкретного сервиса

```bash
docker-compose logs cloud-backend
docker-compose logs cloud-ui
```

### Логи в реальном времени

```bash
docker-compose logs -f cloud-backend
```

## Отладка

### Подключение к контейнеру

```bash
# Backend
docker-compose exec cloud-backend bash

# Frontend
docker-compose exec cloud-ui sh
```

### Проверка переменных среды

```bash
# В контейнере frontend
docker-compose exec cloud-ui env | grep VITE
```

### Проверка сети

```bash
# Проверить сетевые подключения
docker network ls
docker network inspect cloud-hack_cloud-network
```

## Структура проекта

```
cloud-hack/
├── cloud/                    # Backend (Python/FastAPI)
│   ├── Dockerfile           # Docker конфигурация для backend
│   ├── .dockerignore        # Исключения для Docker
│   ├── requirements.txt     # Python зависимости
│   ├── run.py              # Точка входа
│   └── app/                # Код приложения
├── cloud-ui/               # Frontend (React)
│   ├── Dockerfile          # Docker конфигурация для frontend
│   ├── .dockerignore       # Исключения для Docker
│   ├── .env                # Переменные среды для разработки
│   ├── .env.production     # Переменные среды для продакшена
│   ├── package.json        # Node.js зависимости
│   └── src/               # Код приложения
└── docker-compose.yml     # Оркестрация сервисов
```

## Переменные среды

### Backend (cloud)

Настраиваются в [`cloud/app/core/config.py`](cloud/app/core/config.py):

- `HOST` - хост сервера (по умолчанию: 0.0.0.0)
- `PORT` - порт сервера (по умолчанию: 8000)
- `DEBUG` - режим отладки (по умолчанию: true)

### Frontend (cloud-ui)

Настраиваются в [`.env`](cloud-ui/.env) файлах:

- `VITE_APP_API` - адрес backend API (localhost:8000)

## Порты

- **8000** - Backend API
- **5173** - Frontend приложение

Убедитесь, что эти порты свободны перед запуском.

## Troubleshooting

### Проблема: Порт уже используется

```bash
# Найти процесс, использующий порт
lsof -i :8000
lsof -i :5173

# Остановить процесс
kill -9 <PID>
```

### Проблема: Контейнер не запускается

```bash
# Проверить логи
docker-compose logs <service-name>

# Пересобрать образ
docker-compose build --no-cache <service-name>
```

### Проблема: Сетевые ошибки

```bash
# Очистить Docker сети
docker network prune -f

# Перезапустить с пересозданием сети
docker-compose down
docker-compose up --build
```

### Проблема: Переменные среды не передаются

```bash
# Пересобрать frontend без кэша
DOCKER_BUILDKIT=0 docker-compose build --no-cache cloud-ui
docker-compose up cloud-ui -d
```

## Полезные команды

```bash
# Показать использование ресурсов
docker stats

# Очистить неиспользуемые образы и контейнеры
docker system prune -f

# Показать все образы
docker images

# Удалить конкретный образ
docker rmi cloud-hack-cloud-backend
docker rmi cloud-hack-cloud-ui

# Показать все контейнеры
docker ps -a
```

## Разработка

Для разработки рекомендуется:

1. Запустить только backend в Docker:
   ```bash
   docker-compose up cloud-backend -d
   ```

2. Запустить frontend локально:
   ```bash
   cd cloud-ui
   npm install
   npm run dev
   ```

Это позволит использовать hot reload для frontend при сохранении изолированности backend.
