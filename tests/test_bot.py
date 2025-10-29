"""
Тесты для TgProbot
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import send_email, get_main_reply_markup


class TestTgProbot:
    """Тесты для основных функций бота"""

    def test_get_main_reply_markup(self):
        """Тест создания главного меню"""
        markup = get_main_reply_markup()
        assert markup is not None
        assert len(markup.keyboard) == 2  # Две строки кнопок
        assert len(markup.keyboard[0]) == 1  # Одна кнопка в первой строке
        assert len(markup.keyboard[1]) == 1  # Одна кнопка во второй строке
        assert markup.keyboard[0][0].text == "🚀 Главное меню 🚀"
        assert markup.keyboard[1][0].text == "✉️ Написать сообщение"

    @pytest.mark.asyncio
    async def test_send_email_success(self):
        """Тест успешной отправки email"""
        with patch("smtplib.SMTP_SSL") as mock_smtp:
            # Настраиваем мок
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            # Устанавливаем переменные окружения
            with patch.dict(
                os.environ,
                {
                    "EMAIL_HOST": "smtp.test.com",
                    "EMAIL_PORT": "587",
                    "EMAIL_USER": "test@test.com",
                    "EMAIL_PASSWORD": "test_password",
                    "EMAIL_TO": "recipient@test.com",
                },
            ):
                result = await send_email("Test Subject", "Test Message")
                assert result is True
                mock_server.login.assert_called_once()
                mock_server.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_missing_config(self):
        """Тест отправки email с отсутствующими настройками"""
        with patch.dict(os.environ, {}, clear=True):
            result = await send_email("Test Subject", "Test Message")
            assert result is False

    @pytest.mark.asyncio
    async def test_send_email_smtp_error(self):
        """Тест обработки ошибки SMTP"""
        with patch("smtplib.SMTP_SSL") as mock_smtp:
            mock_smtp.side_effect = Exception("SMTP Error")

            with patch.dict(
                os.environ,
                {
                    "EMAIL_HOST": "smtp.test.com",
                    "EMAIL_PORT": "587",
                    "EMAIL_USER": "test@test.com",
                    "EMAIL_PASSWORD": "test_password",
                    "EMAIL_TO": "recipient@test.com",
                },
            ):
                result = await send_email("Test Subject", "Test Message")
                assert result is False


class TestEnvironmentSetup:
    """Тесты настройки окружения"""

    def test_required_environment_variables(self):
        """Тест наличия необходимых переменных окружения"""
        required_vars = [
            "TOKEN",
            "EMAIL_HOST",
            "EMAIL_PORT",
            "EMAIL_USER",
            "EMAIL_PASSWORD",
            "EMAIL_TO",
        ]

        # Проверяем, что переменные определены в коде
        from main import (
            EMAIL_HOST,
            EMAIL_PORT,
            EMAIL_USER,
            EMAIL_PASSWORD,
            EMAIL_TO,
            token_bot,
        )

        # В тестовом окружении они могут быть None, но переменные должны быть определены
        assert EMAIL_HOST is not None
        assert EMAIL_PORT is not None
        # Остальные могут быть None в тестах, но должны быть определены


if __name__ == "__main__":
    pytest.main([__file__])
