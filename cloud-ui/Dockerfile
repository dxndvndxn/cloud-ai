# Используем Node.js образ версии 22.10.0
FROM node:22.10.0-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY package*.json ./

# Создаем директорию для husky
RUN mkdir -p .husky

# Устанавливаем зависимости
RUN npm ci

# Копируем исходный код
COPY . .

# Устанавливаем переменную среды для Vite
ARG VITE_APP_API=localhost:8000
ENV VITE_APP_API=$VITE_APP_API

# Открываем порт
EXPOSE 5173

# Команда запуска в режиме разработки
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
