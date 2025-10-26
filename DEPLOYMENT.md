# 🚀 Руководство по развертыванию TgProbot

## 📋 Обзор

Этот документ описывает процесс настройки CI/CD pipeline для автоматического тестирования и развертывания Telegram бота на сервер.

## 🏗️ Архитектура

```
GitHub Repository
       ↓
GitHub Actions (CI/CD)
       ↓
Docker Hub Registry
       ↓
Production Server
```

## 🔧 Настройка GitHub Actions

### 1. Создайте секреты в GitHub

Перейдите в **Settings** → **Secrets and variables** → **Actions** и добавьте:

#### Docker Hub
- `DOCKER_USERNAME` - ваш логин на Docker Hub
- `DOCKER_PASSWORD` - токен доступа Docker Hub

#### Сервер
- `SERVER_HOST` - IP адрес или домен сервера
- `SERVER_USER` - пользователь для SSH (например, `root` или `ubuntu`)
- `SERVER_SSH_KEY` - приватный SSH ключ для доступа к серверу
- `SERVER_PORT` - порт SSH (обычно 22)

#### Тестирование
- `TEST_BOT_TOKEN` - токен тестового бота для тестов

### 2. Настройте ветки

- `main` - продакшн ветка (автоматический деплой)
- `develop` - ветка разработки (только тесты)

## 🐳 Настройка Docker

### Локальная разработка

```bash
# Создайте .env файл
cp env.production.example .env
# Отредактируйте .env с вашими настройками

# Запустите локально
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Сборка образа

```bash
# Сборка образа
docker build -t tgprobot .

# Запуск контейнера
docker run -d --name tgprobot --env-file .env tgprobot
```

## 🖥️ Настройка сервера

### 1. Подготовка сервера

```bash
# Загрузите скрипт настройки
wget https://raw.githubusercontent.com/your-username/tgprobot/main/scripts/setup-server.sh

# Сделайте исполняемым
chmod +x setup-server.sh

# Запустите настройку (требует sudo)
sudo ./setup-server.sh
```

### 2. Настройка SSH ключей

```bash
# На сервере создайте пользователя для деплоя
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# Создайте SSH ключ на вашем компьютере
ssh-keygen -t rsa -b 4096 -C "github-actions"

# Скопируйте публичный ключ на сервер
ssh-copy-id -i ~/.ssh/id_rsa.pub deploy@your-server.com

# Добавьте приватный ключ в GitHub Secrets как SERVER_SSH_KEY
cat ~/.ssh/id_rsa
```

### 3. Настройка проекта на сервере

```bash
# Войдите на сервер
ssh deploy@your-server.com

# Склонируйте репозиторий
git clone https://github.com/your-username/tgprobot.git /opt/tgprobot

# Создайте .env файл
cd /opt/tgprobot
cp env.production.example .env
nano .env  # Отредактируйте с реальными настройками

# Установите права
sudo chown -R deploy:deploy /opt/tgprobot
```

## 🔄 Процесс деплоя

### Автоматический деплой

1. **Сделайте изменения** в коде
2. **Создайте Pull Request** в ветку `main`
3. **GitHub Actions автоматически**:
   - Запустит тесты
   - Проверит код (linting, formatting)
   - Соберет Docker образ
   - Загрузит в Docker Hub
   - Развернет на сервер

### Ручной деплой

```bash
# На сервере
cd /opt/tgprobot
./scripts/deploy.sh production
```

## 📊 Мониторинг

### Проверка статуса

```bash
# Статус сервиса
systemctl status tgprobot

# Статус контейнеров
docker-compose ps

# Логи
docker-compose logs -f
```

### Health Check

```bash
# Проверка здоровья бота
curl -X GET "https://api.telegram.org/bot$TOKEN/getMe"
```

## 🛠️ Разработка

### Локальная разработка

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/tgprobot.git
cd tgprobot

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Создайте .env файл
cp env.production.example .env
# Отредактируйте .env

# Запустите бота
python main.py
```

### Тестирование

```bash
# Запуск тестов
pytest

# Запуск с покрытием
pytest --cov=.

# Проверка кода
flake8 .
black --check .
```

## 🚨 Устранение неполадок

### Проблемы с Docker

```bash
# Очистка Docker
docker system prune -a

# Пересборка образов
docker-compose build --no-cache
```

### Проблемы с GitHub Actions

1. Проверьте **Secrets** в настройках репозитория
2. Убедитесь, что **SSH ключи** настроены правильно
3. Проверьте **логи** в разделе Actions

### Проблемы с ботом

```bash
# Проверка логов
docker-compose logs tgprobot

# Перезапуск
docker-compose restart tgprobot

# Проверка переменных окружения
docker-compose exec tgprobot env
```

## 📝 Полезные команды

### Docker

```bash
# Просмотр всех контейнеров
docker ps -a

# Просмотр образов
docker images

# Очистка неиспользуемых ресурсов
docker system prune -a

# Просмотр логов
docker logs tgprobot
```

### Git

```bash
# Создание новой ветки
git checkout -b feature/new-feature

# Отправка изменений
git add .
git commit -m "Описание изменений"
git push origin feature/new-feature
```

## 🔐 Безопасность

### Рекомендации

1. **Никогда не коммитьте** файлы `.env`
2. **Используйте сильные пароли** для всех сервисов
3. **Регулярно обновляйте** зависимости
4. **Настройте firewall** на сервере
5. **Используйте HTTPS** для всех соединений

### Backup

```bash
# Создание бэкапа
tar -czf backup_$(date +%Y%m%d).tar.gz /opt/tgprobot

# Восстановление из бэкапа
tar -xzf backup_20231201.tar.gz -C /
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте **логи** GitHub Actions
2. Проверьте **логи** на сервере
3. Убедитесь, что все **Secrets** настроены правильно
4. Проверьте **сетевое соединение** между сервисами
