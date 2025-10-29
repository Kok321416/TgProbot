# 🔧 Настройка SSH ключа для GitHub Actions

## Проблема
```
ssh: handshake failed: ssh: unable to authenticate
```

## Решение

### 1. На сервере выполните команды:

```bash
# Посмотрите публичный ключ
cat ~/.ssh/id_rsa.pub

# Добавьте его в authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# Проверьте права
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_rsa
```

### 2. Добавьте секреты в GitHub:

Откройте: https://github.com/Kok321416/TgProbot/settings/secrets/actions

Добавьте:
- **SERVER_HOST** — IP вашего сервера (например, `vps-3444` или IP адрес)
- **SERVER_USER** — `root`
- **SERVER_SSH_KEY** — приватный ключ (вся эта строка целиком):

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAACFwAAAAdzc2gtcn
...
СОДЕРЖИМОЕ КЛЮЧА
...
BA==
-----END OPENSSH PRIVATE KEY-----
```

- **SERVER_PORT** — `22`

### 3. Проверьте, что публичный ключ есть на сервере:

```bash
# На сервере
cat ~/.ssh/id_rsa.pub
```

Должен быть ключ типа: `ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQ...`

### 4. Если ключа нет, создайте новый:

```bash
# На сервере
ssh-keygen -t rsa -b 4096 -C "github-actions"

# Скопируйте публичный ключ
cat ~/.ssh/id_rsa.pub

# Добавьте его в authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

### 5. Проверьте подключение вручную:

С вашего компьютера попробуйте:
```bash
ssh -i путь_к_приватному_ключу root@ваш_сервер
```

## Важно!

1. **Приватный ключ** (`id_rsa`) → в GitHub Secrets как `SERVER_SSH_KEY`
2. **Публичный ключ** (`id_rsa.pub`) → в `~/.ssh/authorized_keys` на сервере
3. Права должны быть: `chmod 600` для файлов и `chmod 700` для директории

После настройки GitHub Actions сможет подключиться к серверу! 🚀


