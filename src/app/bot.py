import os

from dotenv import load_dotenv
import telebot

load_dotenv()
bot = telebot.TeleBot(os.getenv("TG_TOKEN"), parse_mode="Markdown")
