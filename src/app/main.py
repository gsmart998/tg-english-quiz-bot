import os

from dotenv import load_dotenv
import telebot

from database.database import Session, init_db
from database.crud import create_user


load_dotenv()
bot = telebot.TeleBot(os.getenv("TG_TOKEN"))


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я ваш Telegram-бот. Чем могу помочь?")
    name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    user_id = message.from_user.id
    print(f"{name=} {last_name=} {username=} {user_id=}")
    create_user(name=name, tg_id=user_id)


@bot.message_handler(commands=["quiz"])
def launch_quiz(message):
    bot.reply_to(message, "Вы запустили квиз!")


if __name__ == "__main__":
    init_db()
    # with Session() as session:
    #     users = session.query(Users).all()
    #     if not users:
    #         print("users not found!")
    #     for user in users:
    #         print(f"{user.user_tg_id=} {user.user_name=}")

    print("Бот запущен...")
    bot.polling(none_stop=True)
