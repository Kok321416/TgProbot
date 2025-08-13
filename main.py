from os import getenv, path
import logging
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv(override=True)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации из переменных окружения
EMAIL_HOST = getenv("EMAIL_HOST", "smtp.yandex.ru")
EMAIL_PORT = int(getenv("EMAIL_PORT", "465"))
EMAIL_USER = getenv("EMAIL_USER")
EMAIL_PASSWORD = getenv("EMAIL_PASSWORD")
EMAIL_TO = getenv("EMAIL_TO")
token_bot = getenv("TOKEN")

# Проверка загрузки критических переменных
if not all([EMAIL_USER, EMAIL_PASSWORD, EMAIL_TO, token_bot]):
    logger.error("Не все обязательные переменные окружения загружены!")
    logger.error(f"EMAIL_USER: {'✓' if EMAIL_USER else '✗'}")
    logger.error(f"EMAIL_PASSWORD: {'✓' if EMAIL_PASSWORD else '✗'}")
    logger.error(f"EMAIL_TO: {'✓' if EMAIL_TO else '✗'}")
    logger.error(f"TOKEN: {'✓' if token_bot else '✗'}")
    sys.exit(1)

print(f"Настройки загружены: {EMAIL_USER}@{EMAIL_HOST}:{EMAIL_PORT}")

# Константы
DATA_DIR = "./data"
(MAIN_MENU, PSYCHOLOGISTS_MENU, SOCIAL_PEDAGOGUES_MENU, DOCUMENTS_MENU, AWAITING_MESSAGE) = range(5)
user_states = {}

# Проверяем существование папки data
if not path.exists(DATA_DIR):
    logger.warning(f"Папка {DATA_DIR} не найдена. Создаем...")
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        logger.info(f"Папка {DATA_DIR} создана")
    except Exception as e:
        logger.error(f"Не удалось создать папку {DATA_DIR}: {e}")


async def send_email(subject: str, message_text: str) -> bool:
    try:
        # Проверяем, что все необходимые переменные загружены
        if not all([EMAIL_USER, EMAIL_PASSWORD, EMAIL_TO, EMAIL_HOST, EMAIL_PORT]):
            logger.error("Не все email настройки загружены")
            return False
            
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        msg.attach(MIMEText(message_text, 'plain', 'utf-8'))

        logger.info(f"Попытка подключения к SMTP серверу: {EMAIL_HOST}:{EMAIL_PORT}")
        
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, timeout=30) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            logger.info("Email успешно отправлен")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Ошибка аутентификации SMTP: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"Ошибка SMTP: {e}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке email: {e.__class__.__name__}: {e}")
        return False

# Убираем дублирующий print, так как он уже есть выше

def get_main_reply_markup():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🚀 Главное меню 🚀")],
            [KeyboardButton("✉️ Написать сообщение")]  # Основная кнопка для запросов
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Выберите действие..."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_states[user_id] = MAIN_MENU
    
    welcome_message = (
        "👋 **Добро пожаловать в TgProbot!**\n\n"
        "🤖 **Что умеет этот бот:**\n"
        "• 📅 **Записаться на консультацию** к психологам и социальным педагогам\n"
        "• 🧠 **Пройти психологические тесты** для самодиагностики\n"
        "• 📄 **Получить документы** (заявления, памятки, инструкции)\n"
        "• 💬 **Написать сообщение** специалистам с вопросами\n"
        "• 🏢 **Узнать контакты** и расположение кабинетов специалистов\n\n"
        "🚀 **Нажмите кнопку СТАРТ, чтобы начать работу!**"
    )
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_reply_markup(),
        parse_mode='Markdown'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_states.get(user_id) == AWAITING_MESSAGE:
        user = update.message.from_user
        # Формируем контактные данные
        contact_info = []
        if user.first_name:
            contact_info.append(f"Имя: {user.first_name}")
        if user.last_name:
            contact_info.append(f"Фамилия: {user.last_name}")
        if user.username:
            contact_info.append(f"Телеграм: @{user.username}")

        # Можно добавить запрос номера телефона
        contact_text = "\n".join(contact_info) if contact_info else "Контактные данные не указаны"

        subject = f"Сообщение от пользователя Telegram"
        message = f"""
        КОНТАКТНАЯ ИНФОРМАЦИЯ:
        {contact_text}

        СООБЩЕНИЕ:
        {update.message.text}

        ДОПОЛНИТЕЛЬНО:
        ID пользователя: {user.id}
        Дата отправки: {update.message.date}
        """

        if await send_email(subject, message):
            await update.message.reply_text(
                "✅ Ваше сообщение успешно отправлено! С вами свяжутся в ближайшее время.",
                reply_markup=get_main_reply_markup()
            )
        else:
            await update.message.reply_text(
                "❌ Произошла ошибка при отправке. Пожалуйста, попробуйте позже.",
                reply_markup=get_main_reply_markup()
            )

        user_states[user_id] = MAIN_MENU
    elif update.message.text == "🚀 Главное меню 🚀":
        await show_main_menu(update)
    elif update.message.text == "✉️ Написать сообщение":
        user_states[user_id] = AWAITING_MESSAGE
        await update.message.reply_text(
            "✍️ **Отправьте ваше сообщение специалистам:**\n\n"
            "📋 **Что указать в сообщении:**\n"
            "• Ваше ФИО (если требуется обращение по имени)\n"
            "• Контактный телефон (если нужен обратный звонок)\n"
            "• Суть вашего вопроса или проблемы\n\n"
            "📧 **Ваше сообщение будет автоматически отправлено специалистам**\n"
            "✅ **Мы обработаем запрос и свяжемся с вами в ближайшее время!**",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Отмена")]], resize_keyboard=True),
            parse_mode='Markdown'
        )
    elif update.message.text == "🔙 Отмена":
        user_states[user_id] = MAIN_MENU
        await update.message.reply_text(
            "Действие отменено",
            reply_markup=get_main_reply_markup()
        )
    else:
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки меню для навигации",
            reply_markup=get_main_reply_markup(),
        )


async def show_main_menu(update: Update):
    user_states[update.effective_user.id] = MAIN_MENU
    keyboard = [
        [
            InlineKeyboardButton("👨‍⚕️ Психологическая служба", callback_data="psychologists"),
            InlineKeyboardButton("👩‍🏫 Социально-педагогическая служба", callback_data="social_pedagogues"),
        ]
        # Убрана кнопка "✉️ Обратиться с запросом"
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text="Выберите категорию специалистов:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "🎯 **Вас приветствует отдел социально-психологической работы, мы часть отдела воспитательной работы\n"
            "Выберите, что вас интересует, мы постараемся вам помочь:**\n\n"
            "👨‍⚕️ **Психологическая служба** - консультации, тесты, диагностика\n"
            "👩‍🏫 **Социально-педагогическая служба** - документы, контакты специалистов\n\n"
            "💬 **Используйте кнопку «Написать сообщение» для отправки запроса на электронную почту нашего отдела, вы всегда можете написать\n"
            "- жалобы(студентов, педагогов)\n"
            "- для педагогов, запрос на работу с группой или студентом\n"
            "- другие комментарии о воспитательном процессе**"
            "Запрос будет обработан и ответ будет направлен вам в сообщения.\n\n",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    current_state = user_states.get(user_id)

    if query.data == "back":
        if current_state in (PSYCHOLOGISTS_MENU, SOCIAL_PEDAGOGUES_MENU):
            await show_main_menu(update)
        elif current_state == DOCUMENTS_MENU:
            await show_social_pedagogues_menu(update)
    elif query.data == "psychologists":
        user_states[user_id] = PSYCHOLOGISTS_MENU
        await show_psychologists_menu(update)
    elif query.data == "social_pedagogues":
        user_states[user_id] = SOCIAL_PEDAGOGUES_MENU
        await show_social_pedagogues_menu(update)
    elif query.data == "documents":
        user_states[user_id] = DOCUMENTS_MENU
        await show_documents_menu(update)
    elif query.data == "get_guide":
        await send_photo(update, context)
    elif query.data == "get_application":
        await send_document(update, context)
    elif query.data == "psycho_tests":
        await show_psycho_test_menu(update)
    # Убрана обработка query.data == "send_message"
    elif query.data == "cancel_message":
        await show_main_menu(update)


async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        photo_path = path.join(DATA_DIR, "guide.jpg")
        if not path.exists(photo_path):
            await query.edit_message_text("Извините, изображение временно недоступно.")
            return
            
        with open(photo_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=photo,
                caption="Памятка на документы для социальных выплат"
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        await query.edit_message_text("Произошла ошибка при отправке изображения.")


async def send_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        doc_path = path.join(DATA_DIR, "application.docx")
        if not path.exists(doc_path):
            await query.edit_message_text("Извините, документ временно недоступен.")
            return
            
        with open(doc_path, 'rb') as doc:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=doc,
                filename="Заявление на мат. помощь.docx",
                caption="Заявление на материальную помощь"
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке документа: {e}")
        await query.edit_message_text("Произошла ошибка при отправке документа.")


async def show_psychologists_menu(update: Update):
    user_states[update.effective_user.id] = PSYCHOLOGISTS_MENU
    message = (
        "👨‍⚕️ Психологи:\n\n"
        "• Андриевский А.А. - 5-Железнодорожная (325 кабинет)\n"
        "• Степанец В.П. - 5-Железнодорожная (324 кабинет)\n\n"
        "• Теплякова Е.Н. - ул. Звездинская (215 кабинет)\n\n"
        "У Андриевского А.А. и Степанец В.П. запись производится по ссылке ниже\n\n"
        "У Тепляковой Е.Н. запись производится через сообщения в Телеграм:\n\n"
    )
    keyboard = [
        [
            InlineKeyboardButton(
                "📅 Андриевский записаться",
                url="https://app.fasti.me/user/[username]/event/[event_type]",
            ),
            InlineKeyboardButton(
                "📅 Степанец записаться",
                url="https://app.fasti.me/user/[username]/event/[event_type]",
            ),
            InlineKeyboardButton("📅 Теплякова записаться", url="https://t.me/[username]"),
        ],
        [InlineKeyboardButton("🧠 Диагностика", callback_data="psycho_tests")],

        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_psycho_test_menu(update: Update):
    user_states[update.effective_user.id] = PSYCHOLOGISTS_MENU
    message = ("🧠 Психологическая диагностика:\nВыберите тест:")

    keyboard = [
        [
            InlineKeyboardButton("ИРКПО платформа для тестирования", url="https://irkpo.ru/test/psy"),
            InlineKeyboardButton("СПС (состояния)", url="https://psytests.org/emo/eyespsy-run.html?ysclid=makjgxwmo6267738449")
        ],
        [
            InlineKeyboardButton("Депрессия (Бека)", url="https://psytests.org/depr/bdi-run.html"),
            InlineKeyboardButton("Способы совладающего поведения", url="https://psytests.org/coping/wcq-run.html")
        ],
        [
            InlineKeyboardButton("Опросник Акцент-2-90", url="https://psytests.org/accent/shmi90acc-run.html?ysclid=makklskzii872720319"),
            InlineKeyboardButton("СОП", url="https://psytests.org/parent/osopFf-run.html?ysclid=m6q6vdbfac18846130")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="psychologists")]  # Возврат в меню психологов
    ]

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_social_pedagogues_menu(update: Update):
    user_states[update.effective_user.id] = SOCIAL_PEDAGOGUES_MENU
    message = (
        "👩‍🏫 Социальные педагоги:\n\n"
        "• Дунаевская Елена Николаевна Ул. 5-ая Железнодорожная, д. 53 каб. 216\n"
        "• Тепляшин Данила Владимирович Ул. Булавина, д. 10, каб. 304\n\n"
        "• Першина Юлия Викторовна Ул. Звездинская, д. 12, каб.215\n\n"
        "Вы можете написать им напрямую или получить документы:"
    )
    keyboard = [
        [
            InlineKeyboardButton(
                "💬 Дунаевская Е.Н.",
                url="https://t.me/[username]"
            ),
            InlineKeyboardButton(
                "💬 Тепляшин Д.В.",
                url="https://t.me/[username]"
            ),
            InlineKeyboardButton(
                "💬 Першина Ю.В.",
                url="https://t.me/[username]"
            )
        ],
        [InlineKeyboardButton("📄 Документы", callback_data="documents")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_documents_menu(update: Update):
    user_states[update.effective_user.id] = DOCUMENTS_MENU
    message = "📄 Документы от социальных педагогов:"
    keyboard = [
        [InlineKeyboardButton(
            "📝 Памятка на документы для социальных выплат",
            callback_data="get_guide"
        )],
        [InlineKeyboardButton(
            "📝 Заявление на мат. помощь",
            callback_data="get_application"
        )],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.error(f"Ошибка: {context.error}", exc_info=context.error)

        if update and hasattr(update, 'effective_chat'):  # Проверяем наличие объекта effective_chat
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Произошла ошибка. Пожалуйста, попробуйте снова.",
                reply_markup=get_main_reply_markup()
            )
        else:
            logger.error("Update или effective_chat отсутствует")
    except Exception as e:
        logger.error(f"Ошибка в error_handler: {e}")


def main() -> None:
    try:
        # Проверяем, что токен загружен
        if not token_bot:
            logger.error("Токен бота не загружен!")
            sys.exit(1)
            
        logger.info("Запуск Telegram бота...")
        
        application = Application.builder().token(token_bot).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(button_click))
        application.add_error_handler(error_handler)
        
        logger.info("Бот запущен и готов к работе!")
        application.run_polling(
            poll_interval=1.0,  # Увеличиваем интервал для стабильности
            timeout=30,          # Увеличиваем timeout
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
