import re

from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton as IBtn,
    CallbackQuery,
)
from app.tg_bot import bot
from database.database import init_db
from database.crud import (
    create_user,
    add_translations,
)
from app.logger_config import get_logger
from app.quiz import start_quiz, validate_quiz
from app.scheduler import scheduler, schedule_user_job

log = get_logger(__name__)  # get configured logger


@bot.message_handler(commands=["start"])
def send_welcome(message):
    name = message.from_user.first_name
    tg_id = message.from_user.id
    create_user(name=name, tg_id=tg_id)
    bot.reply_to(
        message,
        f"Перед началом работы с ботом необходимо добавить ваши переводы\n/add для добавления переводов\n/help для помощи"
    )


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="Введите команду:\n/add для добавления новых переводов\n/quiz для запуска квиза\n/settings для настройки бота\n"
    )


@bot.message_handler(commands=["settings"])
def send_settings(message):
    markup = InlineKeyboardMarkup()
    markup.add(IBtn(text="Включить авто квиз", callback_data="/settings:auto"))

    bot.send_message(
        chat_id=message.chat.id,
        text="Меню для настройки бота",
        reply_markup=markup,
    )


@bot.message_handler(commands=["quiz"])
def send_quiz(message):
    start_quiz(tg_id=message.chat.id)


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # handle multiline commands
    full_text = message.text
    index = full_text.find("\n")
    command = full_text[:index]
    text = full_text[index:]
    if command == "/add":
        words_to_add = {}
        for row in text.split("\n"):
            if len(row) < 4:  # skip empty row
                continue
            en_text, ru_text = row.split("  ")
            words_to_add[en_text] = ru_text

        log.info(f"{words_to_add=}")

        add_translations(
            translations=words_to_add,
            tg_id=message.chat.id,
        )

    else:
        bot.reply_to(
            message,
            f"Неизвестная команда!\n/help для помощи."
        )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call: CallbackQuery):
    call_data = call.data
    tg_id = call.message.chat.id
    # handle new quiz button click
    if call_data == "/quiz":
        start_quiz(tg_id=tg_id)

    # handle user answer button click
    elif re.match(r"^\d+:.+$", call_data):
        validate_quiz(call=call)

    # handle settings button click
    elif call_data == "/settings:auto":
        schedule_user_job(user_id=tg_id)
        bot.send_message(
            chat_id=tg_id,
            text="Вы подписались на автоматическую рассылку квиза"
        )
    else:
        log.info(f"Unsupported callback query: {call_data}")


if __name__ == "__main__":
    init_db()
    scheduler.start()

    # bot.set_my_commands()  # add commands list
    log.info("Бот запущен...")
    bot.polling(non_stop=True)


# done кнопка под ответом квиза для рестарта
# TODO scheduler
# TODO миграция БД
# TODO очки за правильные ответы
