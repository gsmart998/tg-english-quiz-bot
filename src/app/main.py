import re

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton as Btn,
    InlineKeyboardMarkup,
    InlineKeyboardButton as IBtn,
    CallbackQuery,
)
from app.tg_bot import bot, bot_commands
from database.database import init_db
from database.crud import (
    create_user,
    add_translations,
)
from app.logger_config import get_logger
from app.quiz import start_quiz, validate_quiz
from app.scheduler import (
    scheduler,
    schedule_user_job,
    check_user_job,
    disable_user_job,
)

log = get_logger(__name__)  # get configured logger


@bot.message_handler(commands=["start"])
def send_welcome(message):
    name = message.from_user.first_name
    tg_id = message.from_user.id
    create_user(name=name, tg_id=tg_id)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(Btn("/add"), Btn("/quiz"))
    markup.row(Btn("/settings"), Btn("/help"))

    bot.send_message(
        chat_id=tg_id,
        text=f"Перед началом работы с ботом необходимо добавить ваши переводы\n/add для добавления переводов\n/help для помощи",
        reply_markup=markup,
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
    if check_user_job(user_id=message.chat.id):
        markup.add(
            IBtn(text="Выключить авто квиз", callback_data="/settings:auto_off")
        )
        markup.add(
            IBtn(text="Изменить интервал между квизами:", callback_data=" "),
        )
        markup.row(
            IBtn(text="1 ч.", callback_data="/settings:auto_on_1h"),
            IBtn(text="2 ч.", callback_data="/settings:auto_on_2h"),
            IBtn(text="4 ч.", callback_data="/settings:auto_on_4h"),
            IBtn(text="6 ч.", callback_data="/settings:auto_on_6h"),
        )

    else:
        markup.add(
            IBtn(
                text="Включить авто квиз", callback_data="/settings:auto_on_1h"
            )
        )

    bot.send_message(
        chat_id=message.chat.id,
        text="Здесь вы можете включить/выключить автоматическую рассылку квизов и изменить интервал отправки:",
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
        bot.edit_message_reply_markup(
            chat_id=tg_id,
            message_id=call.message.id,
            reply_markup=None,
        )

    # handle user answer button click
    elif re.match(r"^\d+:.+$", call_data):
        validate_quiz(call=call)

    # handle settings auto quiz on
    elif call_data[:-3] == "/settings:auto_on":
        timeout = int(call_data[-2:-1])
        schedule_user_job(user_id=tg_id, timeout=timeout)
        bot.edit_message_text(
            chat_id=tg_id,
            message_id=call.message.id,
            text="🔥 Вы подписались на рассылку квизов!"
        )

    # handle settings auto quiz off
    elif call_data == "/settings:auto_off":
        disable_user_job(user_id=tg_id)
        bot.edit_message_text(
            chat_id=tg_id,
            message_id=call.message.id,
            text="😞 Вы отключили рассылку квизов."
        )

    else:
        log.info(f"Unsupported callback query: {call_data}")


if __name__ == "__main__":
    init_db()
    scheduler.start()

    bot.set_my_commands(bot_commands)
    log.info("Бот запущен...")
    bot.polling(non_stop=True)
