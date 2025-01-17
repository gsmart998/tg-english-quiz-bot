import os

import telebot
from telebot.types import BotCommand
from dotenv import load_dotenv


load_dotenv()
bot = telebot.TeleBot(os.getenv("TG_TOKEN"), parse_mode="Markdown")

bot_commands = [
    BotCommand("start", "Начать работу с ботом"),
    BotCommand("add", "Добавить новые переводы"),
    BotCommand("settings", "Настройка бота"),
    BotCommand("quiz", "Запуск нового квиза"),
    BotCommand("score", "Показать баланс"),
]
