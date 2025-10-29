# 🔑 Настройка доступа к GitHub

Если вы получили ошибку "Permission denied (publickey)" при клонировании репозитория, есть три способа решения:

## ✅ Способ 1: HTTPS (самый простой)

Используйте HTTPS вместо SSH:

```bash
# Вместо:
git clone git@github.com:user/repo.git

# Используйте:
git clone https://github.com/user/repo.git
```

Вас попросят ввести логин и пароль от GitHub.

## ✅ Способ 2: Настроить SSH ключ

### На вашем компьютере:

```bash
# 1. Создайте SSH ключ (если ещё нет)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 2. Скопируйте публичный ключ
cat ~/.ssh/id_rsa.pub
```

### Добавьте ключ на GitHub:

1. Откройте https://github.com/settings/keys
2. Нажмите "New SSH key"
3. Вставьте скопированный ключ
4. Сохраните

### Скопируйте ключ на сервер:

```bash
# С вашего компьютера
scp ~/.ssh/id_rsa* ваш_пользователь@сервер:~/.ssh/
```

### На сервере:

```bash
# Проверьте подключение
ssh -T git@github.com
```

## ✅ Способ 3: Personal Access Token

Если HTTPS не работает, используйте токен:

### Создайте токен на GitHub:

1. Откройте https://github.com/settings/tokens
2. Нажмите "Generate new token (classic)"
3. Выберите `repo` права
4. Скопируйте токен

### Используйте токен при клонировании:

```bash
git clone https://токен@github.com/user/repo.git
```

## 🚀 Для нашего проекта рекомендую:

Используйте **HTTPS** с вашим логином/паролем:

```bash
cd /opt
sudo git clone https://github.com/ваш_username/tgprobot.git
```

Это самый простой способ и работает везде!
