from telebot.types import CallbackQuery

from app.tg_bot import bot
from database.database import init_db
from database.crud import (
    create_user,
    get_translations_by_user,
)
from app.logger_config import get_logger
from app.quiz import start_quiz, validate_quiz

log = get_logger(__name__)  # get configured logger


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я ваш Telegram-бот. Чем могу помочь?")
    name = message.from_user.first_name
    user_id = message.from_user.id
    create_user(name=name, tg_id=user_id)


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(
        message,
        """
        Введите команду:
        /add для добавления новых переводов
        /quiz для запуска квиза
        /settings для настройки бота
        """
    )


@bot.message_handler(commands=["quiz"])
def launch_quiz(message):
    message_text, markup = start_quiz(tg_id=message.chat.id)

    bot.send_message(
        chat_id=message.chat.id,
        text=message_text,
        reply_markup=markup
    )
    log.info(f"Quiz for user {message.chat.id=} was successfully sent")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call: CallbackQuery):
    message_text = validate_quiz(call_data=call.data)

    bot.edit_message_text(
        text=message_text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=None,
    )


if __name__ == "__main__":
    init_db()

    # bot.set_my_commands()  # add commands list
    log.info("Бот запущен...")
    bot.polling(non_stop=True)


# DONE добавлен логгер
# DONE поправить отображение вопроса после отправки ответа пользователем

# TODO очки за правильные ответы
