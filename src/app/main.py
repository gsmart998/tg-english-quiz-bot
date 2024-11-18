import os

from dotenv import load_dotenv
import telebot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton as IBtn,
)
from database.database import init_db
from database.crud import create_user, get_translation, validate_translation


load_dotenv()
bot = telebot.TeleBot(os.getenv("TG_TOKEN"))


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
    bot.reply_to(message, "Вы запустили квиз!")

    words = get_translation(message.chat.id)
    word_id = words["id"]
    en_word = words["en_word"]
    ru_word_1 = words["option_1"]
    ru_word_2 = words["option_2"]
    ru_word_3 = words["option_3"]

    # Создаем клавиатуру - кнопки в сообщении
    markup = InlineKeyboardMarkup()
    btn_1 = IBtn(ru_word_1, callback_data=f"{word_id}:{ru_word_1}")
    btn_2 = IBtn(ru_word_2, callback_data=f"{word_id}:{ru_word_2}")
    btn_3 = IBtn(ru_word_3, callback_data=f"{word_id}:{ru_word_3}")

    markup.add(btn_1)
    markup.add(btn_2)
    markup.add(btn_3)

    bot.send_message(
        message.chat.id,
        parse_mode="Markdown",
        text=f"Как переводится *{en_word}* ?",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    translation_id, ru_text = call.data.split(":")
    if validate_translation(translation_id=int(translation_id), ru_text=ru_text):
        bot.edit_message_text(
            text="Правильный ответ! 🎉",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None,
        )
    else:
        bot.edit_message_text(
            text="Неправильный ответ. 😢",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None,
        )


if __name__ == "__main__":
    init_db()

    print("Бот запущен...")
    bot.polling(none_stop=True)


# TODO поправить отображение вопроса после отправки ответа пользователем
