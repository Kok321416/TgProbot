#!/bin/bash

# Скрипт настройки сервера для TgProbot
# Запускать с правами root или через sudo

set -e

echo "🔧 Настройка сервера для TgProbot..."

# Обновляем систему
echo "📦 Обновляем систему..."
apt-get update
apt-get upgrade -y

# Устанавливаем необходимые пакеты
echo "📦 Устанавливаем необходимые пакеты..."
apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Устанавливаем Docker
echo "🐳 Устанавливаем Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

# Устанавливаем Docker Compose
echo "🐳 Устанавливаем Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Создаем пользователя для приложения
echo "👤 Создаем пользователя для приложения..."
if ! id "tgprobot" &>/dev/null; then
    useradd -m -s /bin/bash tgprobot
    usermod -aG docker tgprobot
fi

# Создаем директории
echo "📁 Создаем директории..."
mkdir -p /opt/tgprobot
mkdir -p /opt/backups/tgprobot
mkdir -p /var/log/tgprobot

# Устанавливаем права
echo "🔐 Устанавливаем права..."
chown -R tgprobot:tgprobot /opt/tgprobot
chown -R tgprobot:tgprobot /opt/backups/tgprobot
chown -R tgprobot:tgprobot /var/log/tgprobot

# Создаем systemd сервис для автозапуска
echo "⚙️ Создаем systemd сервис..."
cat > /etc/systemd/system/tgprobot.service << EOF
[Unit]
Description=TgProbot Telegram Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/tgprobot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=tgprobot
Group=tgprobot

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd
systemctl daemon-reload
systemctl enable tgprobot

# Настраиваем firewall (если используется ufw)
if command -v ufw &> /dev/null; then
    echo "🔥 Настраиваем firewall..."
    ufw allow ssh
    ufw allow 80
    ufw allow 443
    ufw --force enable
fi

# Создаем cron задачу для очистки логов
echo "⏰ Настраиваем cron для очистки логов..."
cat > /etc/cron.daily/tgprobot-cleanup << EOF
#!/bin/bash
# Очистка старых логов и Docker образов
find /var/log/tgprobot -name "*.log" -mtime +7 -delete
docker system prune -f
EOF
chmod +x /etc/cron.daily/tgprobot-cleanup

echo "✅ Настройка сервера завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Склонируйте репозиторий: git clone <your-repo> /opt/tgprobot"
echo "2. Создайте файл .env с настройками"
echo "3. Запустите: systemctl start tgprobot"
echo "4. Проверьте статус: systemctl status tgprobot"
