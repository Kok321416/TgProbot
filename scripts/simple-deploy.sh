#!/bin/bash

# Простой скрипт деплоя TgProbot на Ubuntu сервер
# Использование: ./simple-deploy.sh

set -e

echo "🚀 Простой деплой TgProbot на Ubuntu"

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Устанавливаем..."
    sudo apt update
    sudo apt install -y docker.io docker-compose
    sudo systemctl enable docker
    sudo systemctl start docker
else
    echo "✅ Docker установлен"
fi

# Проверяем наличие Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Устанавливаем..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose установлен"
fi

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден"
    echo "📝 Создайте файл .env из примера:"
    echo "   cp env.production.example .env"
    echo "   nano .env"
    exit 1
fi

echo "✅ Файл .env найден"

# Останавливаем старые контейнеры
echo "🛑 Останавливаем старые контейнеры..."
docker-compose down || true

# Обновляем проект (если это git репозиторий)
if [ -d .git ]; then
    echo "📥 Обновляем код из Git..."
    git pull || echo "⚠️  Не удалось обновить из Git"
fi

# Собираем и запускаем контейнеры
echo "🐳 Собираем Docker образы..."
docker-compose build

echo "🚀 Запускаем контейнеры..."
docker-compose up -d

# Ждем запуска
echo "⏳ Ждем запуска сервисов..."
sleep 10

# Показываем статус
echo "📊 Статус контейнеров:"
docker-compose ps

echo ""
echo "📋 Последние логи:"
docker-compose logs --tail=30

echo ""
echo "✅ Деплой завершен!"
echo "📝 Для просмотра логов в реальном времени используйте:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Для остановки используйте:"
echo "   docker-compose down"
echo ""
echo "🔄 Для перезапуска используйте:"
echo "   docker-compose restart"
