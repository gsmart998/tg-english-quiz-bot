import os

import telebot
from dotenv import load_dotenv


load_dotenv()
bot = telebot.TeleBot(os.getenv("TG_TOKEN"), parse_mode="Markdown")
