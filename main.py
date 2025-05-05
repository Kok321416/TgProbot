# import webbrowser
#
# import telebot
# from telebot import types
# import config
#
# bot = telebot.TeleBot('7792987674:AAEyIJg1OqnRpks2TLoUCKHuMqDU_FRu1qo')
#
#
# @bot.message_handler(commands=["start"])
# def hellow_message(message):
#     bot.send_message(message.chat.id, f'Привет!, {message.from_user.first_name} {message.from_user.last_name}. Хочешь больше узнать о специалистах тыкни /s')
#     markup = types.InlineKeyboardMarkup()
#     markup.add(types.InlineKeyboardButton('Перейти на сайт '))
#
# @bot.message_handler(commands=["s"])
# def irl_for_zapis(message):
#     bot.send_message(message.chat.id,
#                      '\n Записаться Андриевский А.А. кабинет 325 /zAA'
#                      '\n Записаться Степанец В.П. кабинет 324 /zVP ')
#
#
# @bot.message_handler(commands=["zAA"])
# def irl_for_zapisАА(message):
#     webbrowser.open('https://app.fasti.me/user/kok321416x/event/psihologicheskaya_konsultaciya')
#
#
# @bot.message_handler(commands=["zVP"])
# def irl_for_zapisVP(message):
#     webbrowser.open('https://app.fasti.me/user/valeriaa.stepanets/event/individualnaya_konsultaciya?eventTypeId=624eb451-855d-440e-aaaa-1e83d85aadd9')
#
#
#
# bot.polling(none_stop=True)
from os import getenv
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
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
loading = load_dotenv()
logger = logging.getLogger(__name__)
token_bot = getenv("TOKEN")


# Состояния для навигации
(MAIN_MENU, PSYCHOLOGISTS_MENU, SOCIAL_PEDAGOGUES_MENU) = range(3)

# Хранение состояний пользователей
user_states = {}


def get_main_reply_markup():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("🚀 СТАРТ")]], resize_keyboard=True, is_persistent=True
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_states[user_id] = MAIN_MENU

    await update.message.reply_text(
        "Добро пожаловать! Нажмите кнопку СТАРТ для продолжения:",
        reply_markup=get_main_reply_markup(),
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if update.message.text == "🚀 СТАРТ":
        user_states[user_id] = MAIN_MENU
        await show_main_menu(update)
    else:
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки меню для навигации",
            reply_markup=get_main_reply_markup(),
        )


async def show_main_menu(update: Update):
    user_id = update.effective_user.id
    user_states[user_id] = MAIN_MENU

    keyboard = [
        [
            InlineKeyboardButton("👨‍⚕️ Психологи", callback_data="psychologists"),
            InlineKeyboardButton(
                "👩‍🏫 Соц.педагоги", callback_data="social_pedagogues"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Универсальный способ отправки/редактирования сообщения
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text="Выберите категорию специалистов:", reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "Выберите категорию специалистов:", reply_markup=reply_markup
            )
    except AttributeError:
        await update.message.reply_text(
            "Выберите категорию специалистов:", reply_markup=reply_markup
        )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if query.data == "back":
        if (
            user_states.get(user_id) == PSYCHOLOGISTS_MENU
            or user_states.get(user_id) == SOCIAL_PEDAGOGUES_MENU
        ):
            await show_main_menu(update)
    elif query.data == "psychologists":
        user_states[user_id] = PSYCHOLOGISTS_MENU
        await show_psychologists_menu(update)
    elif query.data == "social_pedagogues":
        user_states[user_id] = SOCIAL_PEDAGOGUES_MENU
        await show_social_pedagogues_menu(update)


async def show_psychologists_menu(update: Update):
    user_id = update.effective_user.id
    user_states[user_id] = PSYCHOLOGISTS_MENU

    message = (
        "👨‍⚕️ Психологи:\n\n"
        "• Андриевский А.А. (325 кабинет)\n"
        "• Степанец В.П. (324 кабинет)\n\n"
        "Запись производится по ссылке ниже ⬇️"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "📅 Записаться к Артему",
                url="https://app.fasti.me/user/kok321416x/event/psihologicheskaya_konsultaciya",
            ),
            InlineKeyboardButton(
                "📅 Записаться к Валерии",
                url="https://app.fasti.me/user/valeriaa.stepanets/event/individualnaya_konsultaciya?eventTypeId=624eb451-855d-440e-aaaa-1e83d85aadd9",
            ),
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=message, reply_markup=reply_markup
    )


async def show_social_pedagogues_menu(update: Update):
    user_id = update.effective_user.id
    user_states[user_id] = SOCIAL_PEDAGOGUES_MENU

    message = (
        "👩‍🏫 Социальные педагоги:\n\n"
        "• Дунаевская Е.Н. (5 Железнодорожная)\n"
        "• Тепляшин Д.В. (Булавина 10)\n\n"
        "Вы можете написать им напрямую:"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "💬 Написать Дунаевской Е.Н.", url="https://t.me/lina_dunaevskya"
            ),
            InlineKeyboardButton(
                "💬 Написать Тепляшину Д.В.", url="https://t.me/DVteplyi"
            ),
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=message, reply_markup=reply_markup
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Произошла ошибка. Пожалуйста, попробуйте снова.",
        reply_markup=get_main_reply_markup(),
    )


def main() -> None:
    application = Application.builder().token(token_bot).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
