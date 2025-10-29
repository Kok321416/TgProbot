# Проверка Docker на сервере

## 1. Проверьте, установлен ли Docker

```bash
docker --version
```

Если команда не работает, установите Docker:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
```

## 2. Проверьте, запущен ли Docker

```bash
sudo systemctl status docker
```

Должно быть: `Active: active (running)`

## 3. Добавьте текущего пользователя в группу docker

```bash
sudo usermod -aG docker $USER
# Выйдите и войдите снова, или:
newgrp docker
```

## 4. Проверьте права доступа

```bash
docker ps
```

Если не работает, используйте `sudo docker ps`

## 5. После установки продолжите деплой

```bash
cd /opt/TgProbot
cp env.production.example .env
nano .env
docker-compose up -d --build
```
