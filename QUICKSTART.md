# 🚀 Быстрый старт на Ubuntu сервере

## Подготовка

### 1. Подключитесь к серверу
```bash
ssh ваш_пользователь@ваш_сервер_ip
```

### 2. Установите базовые пакеты
```bash
sudo apt update
sudo apt install -y git curl
```

### 3. Установите Docker
```bash
# Установка Docker
sudo apt install -y docker.io docker-compose

# Запуск и автозапуск
sudo systemctl enable docker
sudo systemctl start docker

# Добавьте пользователя в группу docker (чтобы не использовать sudo)
sudo usermod -aG docker $USER

# Выйдите и войдите снова, чтобы изменения вступили в силу
# Или выполните:
newgrp docker
```

### 4. Клонируйте репозиторий

#### Вариант A: Через HTTPS (самый простой, требует только логин/пароль)
```bash
cd /opt
sudo git clone https://github.com/ваш_username/tgprobot.git
cd /opt/tgprobot
sudo chown -R $USER:$USER .
```

#### Вариант B: Через SSH (если настроен SSH ключ)
```bash
cd /opt
sudo git clone git@github.com:ваш_username/tgprobot.git
cd /opt/tgprobot
sudo chown -R $USER:$USER .
```

**Если получили ошибку "Permission denied (publickey)":**
```bash
# 1. Создайте SSH ключ
chmod +x scripts/setup-git-ssh.sh
./scripts/setup-git-ssh.sh

# 2. Скопируйте выведенный ключ и добавьте на GitHub:
# https://github.com/settings/keys

# 3. Повторите git clone через SSH
```

#### Вариант C: Копирование файлов через SCP (без Git)
```bash
# На вашем компьютере выполните:
scp -r ./* ваш_пользователь@ваш_сервер:/opt/tgprobot/

# На сервере:
cd /opt/tgprobot
```

### 5. Создайте файл .env
```bash
cp env.production.example .env
nano .env
```

**Обязательно заполните:**
```env
TOKEN=ваш_токен_бота_от_BotFather
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USER=ваш_email@yandex.ru
EMAIL_PASSWORD=пароль_приложения_от_yandex
EMAIL_TO=куда_отправлять@yandex.ru
```

**Важно:** Для Yandex используйте пароль приложения, не обычный пароль!
Как получить пароль приложения: https://yandex.ru/support/id/authorization/app-passwords.html

### 6. Запустите проект

#### Способ 1: Используя готовый скрипт
```bash
chmod +x scripts/simple-deploy.sh
./scripts/simple-deploy.sh
```

#### Способ 2: Вручную
```bash
# Остановите старые контейнеры (если есть)
docker-compose down

# Соберите образ
docker-compose build

# Запустите
docker-compose up -d

# Посмотрите логи
docker-compose logs -f
```

## Проверка работы

```bash
# Статус контейнера
docker-compose ps

# Логи бота
docker-compose logs tgprobot

# Логи в реальном времени
docker-compose logs -f tgprobot
```

## Управление

```bash
# Остановить
docker-compose down

# Перезапустить
docker-compose restart

# Посмотреть логи
docker-compose logs -f

# Обновить проект
git pull
docker-compose up -d --build
```

## Устранение проблем

### Бот не отвечает
```bash
# Проверьте логи
docker-compose logs tgprobot

# Проверьте переменные окружения
docker-compose exec tgprobot env | grep TOKEN
```

### Ошибка подключения к email
- Проверьте пароль приложения в `.env`
- Убедитесь, что включена двухфакторная аутентификация
- Проверьте настройки SMTP сервера

### Контейнер падает
```bash
# Посмотрите подробные логи
docker-compose logs tgprobot

# Пересоберите образ
docker-compose build --no-cache
docker-compose up -d
```

## Автозапуск при перезагрузке сервера

```bash
# Создайте systemd сервис
sudo nano /etc/systemd/system/tgprobot.service
```

Вставьте:
```ini
[Unit]
Description=TgProbot Telegram Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/tgprobot
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=ваш_пользователь
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Активируйте:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tgprobot
sudo systemctl start tgprobot
```

## Полезные команды

```bash
# Мониторинг ресурсов
docker stats

# Очистка старых образов
docker system prune -a

# Резервная копия
tar -czf backup_$(date +%Y%m%d).tar.gz /opt/tgprobot
```

## Поддержка

Если что-то не работает:
1. Проверьте логи: `docker-compose logs tgprobot`
2. Убедитесь, что `.env` файл заполнен правильно
3. Проверьте, что Docker запущен: `sudo systemctl status docker`
