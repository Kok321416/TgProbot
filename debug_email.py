#!/usr/bin/env python3
"""
Скрипт для диагностики проблем с email
"""

import os
import sys
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def check_env_file():
    """Проверяет наличие и содержимое .env файла"""
    print("Проверка файла .env...")

    if not os.path.exists(".env"):
        print("ОШИБКА: Файл .env не найден!")
        print("Создайте файл .env со следующим содержимым:")
        print(
            """
TOKEN=your_bot_token_here
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USER=your_email@yandex.ru
EMAIL_PASSWORD=your_email_password
EMAIL_TO=recipient@example.com
        """
        )
        return False

    print("OK: Файл .env найден")
    return True


def check_env_variables():
    """Проверяет загрузку переменных окружения"""
    print("\nПроверка переменных окружения...")

    load_dotenv(override=True)

    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.yandex.ru")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_TO = os.getenv("EMAIL_TO")
    TOKEN = os.getenv("TOKEN")

    print(f"EMAIL_HOST: {EMAIL_HOST}")
    print(f"EMAIL_PORT: {EMAIL_PORT}")
    print(f"EMAIL_USER: {'OK' if EMAIL_USER else 'ОШИБКА'}")
    print(f"EMAIL_PASSWORD: {'OK' if EMAIL_PASSWORD else 'ОШИБКА'}")
    print(f"EMAIL_TO: {'OK' if EMAIL_TO else 'ОШИБКА'}")
    print(f"TOKEN: {'OK' if TOKEN else 'ОШИБКА'}")

    if not all([EMAIL_USER, EMAIL_PASSWORD, EMAIL_TO, TOKEN]):
        print("ОШИБКА: Не все переменные окружения загружены!")
        return False, None, None, None, None, None

    print("OK: Все переменные окружения загружены")
    return True, EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, EMAIL_TO


def test_smtp_connection(host, port, user, password):
    """Тестирует подключение к SMTP серверу"""
    print(f"\nТестирование SMTP подключения к {host}:{port}...")

    try:
        with smtplib.SMTP_SSL(host, port, timeout=30) as server:
            print("OK: Подключение к SMTP серверу успешно")

            print("Попытка аутентификации...")
            server.login(user, password)
            print("OK: Аутентификация успешна")

        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"ОШИБКА аутентификации: {e}")
        print("Проверьте:")
        print("   - Правильность email адреса")
        print("   - Пароль приложения (не основной пароль)")
        return False
    except smtplib.SMTPException as e:
        print(f"ОШИБКА SMTP: {e}")
        return False
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return False


def test_email_sending(host, port, user, password, to_email):
    """Тестирует отправку тестового email"""
    print(f"\nТестирование отправки email...")

    try:
        msg = MIMEMultipart()
        msg["From"] = user
        msg["To"] = to_email
        msg["Subject"] = "Тестовое сообщение от TgProbot"

        body = "Это тестовое сообщение для проверки работы email системы TgProbot."
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP_SSL(host, port, timeout=30) as server:
            server.login(user, password)
            server.send_message(msg)

        print("OK: Тестовый email успешно отправлен!")
        return True

    except Exception as e:
        print(f"ОШИБКА при отправке тестового email: {e}")
        return False


def main():
    """Основная функция диагностики"""
    print("TgProbot - Диагностика Email")
    print("=" * 40)

    # Проверка файла .env
    if not check_env_file():
        return

    # Проверка переменных окружения
    success, host, port, user, password, to_email = check_env_variables()
    if not success:
        return

    # Тестирование SMTP подключения
    if not test_smtp_connection(host, port, user, password):
        return

    # Тестирование отправки email
    if test_email_sending(host, port, user, password, to_email):
        print("\nУСПЕХ: Все проверки пройдены! Email система работает корректно.")
    else:
        print("\nОШИБКА: Обнаружены проблемы с отправкой email.")


if __name__ == "__main__":
    main()
