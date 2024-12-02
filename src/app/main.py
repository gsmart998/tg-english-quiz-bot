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

log = get_logger(__name__)  # get configured logger


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я ваш Telegram-бот. Чем могу помочь?")
    name = message.from_user.first_name
    tg_id = message.from_user.id
    create_user(name=name, tg_id=tg_id)


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="Введите команду:\n/add для добавления новых переводов\n/quiz для запуска квиза\n/settings для настройки бота\n"
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


# handle user answers to quiz
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call: CallbackQuery):
    call_data = call.data

    # handle new quiz button click
    if call_data == "/quiz":
        launch_quiz(message=call.message)
    else:
        # handle user answer button click
        message_text = validate_quiz(call_data=call_data)
        markup = InlineKeyboardMarkup()
        markup.add(IBtn(text="Ещё квиз", callback_data="/quiz"))

        bot.edit_message_text(
            text=message_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
        )


if __name__ == "__main__":
    init_db()

    # bot.set_my_commands()  # add commands list
    log.info("Бот запущен...")
    bot.polling(non_stop=True)


# done кнопка под ответом квиза для рестарта
# TODO scheduler
# TODO миграция БД
# TODO очки за правильные ответы
