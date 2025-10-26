#!/bin/bash

# Скрипт деплоя на сервер
# Использование: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
PROJECT_DIR="/opt/tgprobot"
BACKUP_DIR="/opt/backups/tgprobot"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🚀 Начинаем деплой TgProbot в окружение: $ENVIRONMENT"

# Создаем директории если не существуют
mkdir -p $PROJECT_DIR
mkdir -p $BACKUP_DIR

# Переходим в директорию проекта
cd $PROJECT_DIR

# Создаем бэкап текущей версии
if [ -f "docker-compose.yml" ]; then
    echo "📦 Создаем бэкап текущей версии..."
    tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" .
fi

# Останавливаем текущие контейнеры
echo "🛑 Останавливаем текущие контейнеры..."
docker-compose down || true

# Обновляем код из Git
echo "📥 Обновляем код из Git..."
git fetch origin
git reset --hard origin/main

# Обновляем образы Docker
echo "🐳 Обновляем Docker образы..."
docker-compose pull

# Запускаем новые контейнеры
echo "🚀 Запускаем новые контейнеры..."
docker-compose up -d

# Ждем запуска
echo "⏳ Ждем запуска сервисов..."
sleep 10

# Проверяем статус
echo "✅ Проверяем статус сервисов..."
docker-compose ps

# Проверяем логи
echo "📋 Последние логи:"
docker-compose logs --tail=20

# Очищаем старые образы
echo "🧹 Очищаем неиспользуемые образы..."
docker system prune -f

echo "🎉 Деплой завершен успешно!"
