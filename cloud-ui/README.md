# Cloud UI - Локальная разработка

React frontend приложение для AI DevTools Hack.

## Требования

- Node.js ^20.19.0 || >=22.12.0
- npm или yarn

## Быстрый запуск

### 1. Установка зависимостей

```bash
cd cloud-ui
npm install
```

### 2. Запуск в режиме разработки

```bash
npm run dev
```

Приложение запустится на `http://localhost:5173`

### 3. Сборка для продакшена

```bash
npm run build
```

### 4. Предварительный просмотр сборки

```bash
npm run preview
```

## Настройка

### Переменные среды

Файл `.env` для разработки:
```env
VITE_APP_API=localhost:8000
```

Файл `.env.production` для продакшена:
```env
VITE_APP_API=your-production-api-url
```

## Доступные команды

- `npm run dev` - Запуск в режиме разработки
- `npm run build` - Сборка для продакшена
- `npm run preview` - Предварительный просмотр сборки
- `npm run lint` - Проверка кода линтером

## Структура проекта

```
cloud-ui/
├── src/
│   ├── app/                # Основное приложение
│   ├── pages/              # Страницы
│   ├── shared/             # Общие компоненты
│   └── constants/          # Константы
├── public/                 # Статические файлы
└── package.json           # Зависимости
```

## Технологии

- React 18
- TypeScript
- Vite
- SCSS Modules
- MobX
- Snack UI Kit

## Troubleshooting

### Порт занят

```bash
lsof -i :5173
kill -9 <PID>
```

### Ошибки зависимостей

```bash
rm -rf node_modules package-lock.json
npm install
```

### Проблемы с API

Убедитесь, что backend запущен на `http://localhost:8000` и переменная `VITE_APP_API` настроена правильно.
