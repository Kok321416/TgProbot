#!/bin/bash

# Скрипт настройки Git SSH на сервере
# Использование: ./setup-git-ssh.sh

set -e

echo "🔑 Настройка Git SSH доступа"

# Проверяем наличие Git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен. Устанавливаем..."
    sudo apt update
    sudo apt install -y git
else
    echo "✅ Git установлен"
fi

# Проверяем существование SSH ключа
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "🔑 Создаём SSH ключ..."
    read -p "Введите email для SSH ключа: " email
    ssh-keygen -t rsa -b 4096 -C "$email" -f ~/.ssh/id_rsa -N ""
    echo "✅ SSH ключ создан"
else
    echo "✅ SSH ключ уже существует"
fi

# Добавляем SSH ключ в ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

# Показываем публичный ключ
echo ""
echo "📋 Ваш публичный SSH ключ:"
echo "============================================"
cat ~/.ssh/id_rsa.pub
echo "============================================"
echo ""
echo "📝 Следующие шаги:"
echo "1. Скопируйте ключ выше"
echo "2. Откройте https://github.com/settings/keys"
echo "3. Нажмите 'New SSH key'"
echo "4. Вставьте скопированный ключ"
echo "5. Сохраните"
echo ""
echo "После добавления ключа повторите команду git clone"
