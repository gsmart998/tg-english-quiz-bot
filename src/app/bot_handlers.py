import re

from telebot.types import (
    BotCommand,
    CallbackQuery,
)

from app.bot import bot
from app import text_templates, handlers
from database.crud import (
    create_user,
    get_user_score,
)
from app.logger_config import get_logger


log = get_logger(__name__)  # get configured logger


bot_commands = [
    BotCommand("start", "Начать работу с ботом"),
    BotCommand("quiz", "Запуск нового квиза"),
    BotCommand("score", "Показать баланс"),
    BotCommand("add", "Добавить новые переводы"),
    BotCommand("settings", "Настройка бота"),
    BotCommand("help", "Список доступных команд"),
]


@bot.message_handler(commands=["start"])
def send_welcome(message):
    name = message.from_user.first_name
    tg_id = message.from_user.id
    create_user(name=name, tg_id=tg_id)

    bot.send_message(
        chat_id=tg_id,
        text=text_templates.MSG_WELCOME,
    )


@bot.message_handler(commands=["help"])
def send_help(message):
    help_text = "Вот список доступных комманд:\n"
    commands = bot.get_my_commands()
    for command in commands:
        help_text += f"/{command.command} - {command.description}\n"
    bot.send_message(
        chat_id=message.chat.id,
        text=help_text,
    )


@bot.message_handler(commands=["settings"])
def send_settings(message):
    bot.send_message(
        chat_id=message.chat.id,
        reply_markup=handlers.prepare_settings_keyboard(tg_id=message.chat.id),
        text=text_templates.MSG_SETTINGS,
    )


@bot.message_handler(commands=["quiz"])
def send_quiz(message):
    handlers.start_quiz(tg_id=message.chat.id)


@bot.message_handler(commands=["score"])
def send_score(message):
    score = get_user_score(tg_id=message.chat.id)
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Ваш счет: *{score}*"
    )


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text == "/add":
        bot.send_message(
            chat_id=message.chat.id,
            text=text_templates.MSG_ADD_INFO,
        )
        return

    # handle multiline /add commands
    full_text = message.text
    index = full_text.find("\n")
    command = full_text[:index]
    text = full_text[index:]
    if command == "/add":
        handlers.add_translations(text=text, tg_id=message.chat.id)
    else:
        bot.reply_to(
            message,
            f"Неизвестная команда!\n/help для справки."
        )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call: CallbackQuery):
    call_data = call.data
    tg_id = call.message.chat.id

    # handle new quiz button click
    if call_data == "/quiz":
        handlers.start_quiz(tg_id=tg_id)
        bot.edit_message_reply_markup(
            chat_id=tg_id,
            message_id=call.message.id,
            reply_markup=None,
        )

    # handle user answer button click
    elif re.match(r"^\d+:.+$", call_data):
        handlers.validate_quiz(call=call)

    # handle settings auto quiz on
    elif call_data[:-3] == "/settings:auto_on":
        timeout = int(call_data[-2:-1])
        handlers.schedule_user_job(user_id=tg_id, timeout=timeout)
        bot.edit_message_text(
            chat_id=tg_id,
            message_id=call.message.id,
            text="🔥 Вы подписались на рассылку квизов!"
        )

    # handle settings auto quiz off
    elif call_data == "/settings:auto_off":
        handlers.disable_user_job(user_id=tg_id)
        bot.edit_message_text(
            chat_id=tg_id,
            message_id=call.message.id,
            text="😞 Вы отключили рассылку квизов."
        )

    else:
        log.info(f"Unsupported callback query: {call_data}")
