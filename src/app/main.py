from app.bot import bot
from app.bot_handlers import bot_commands
from database.database import init_db
from app.logger_config import get_logger
from app.scheduler import scheduler


log = get_logger(__name__)  # get configured logger


if __name__ == "__main__":
    try:
        init_db()
        scheduler.start()
        bot.set_my_commands(bot_commands)
        log.info("The bot is running...")
        bot.infinity_polling()

    except Exception as e:
        log.error(f"Error occured: {e}")
