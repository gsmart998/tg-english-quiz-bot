import random

from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton as IBtn,
    CallbackQuery,
)

from database import crud
from app.logger_config import get_logger
from app.bot_instance import bot
from app.app_config import BUTTONS_NUM
from app.text_templates import MSG_START_QUIZ_ERROR
from app.scheduler import scheduler

log = get_logger(__name__)  # get configured logger


def start_quiz(tg_id: int):
    """Fetch user's translations from DB and prepare it.
    Then sends the prepared quiz to the user.
    """
    log.info(f"User {tg_id=} started the quiz")

    quiz_words = crud.get_translations_by_user(tg_id=tg_id)
    if quiz_words is None:
        log.error("User does not have enough translations to start the quiz")
        bot.send_message(
            chat_id=tg_id,
            text=MSG_START_QUIZ_ERROR,
        )
        return

    # create and shuffle list with fetched translations
    ru_options = [quiz_words.get(f"ru_option_{i}")
                  for i in range(1, BUTTONS_NUM + 1)]
    random.shuffle(ru_options)

    # create keyboard and add buttons
    markup = InlineKeyboardMarkup()
    word_id = quiz_words["id"]
    for option in ru_options:
        markup.add(IBtn(option, callback_data=f"{word_id}:{option}"))

    message_text = f"Как переводится *'{quiz_words["en_word"]}'* ?"

    bot.send_message(
        chat_id=tg_id,
        text=message_text,
        reply_markup=markup
    )
    log.info(f"Quiz for user {tg_id=} was successfully sent")


def validate_quiz(call: CallbackQuery):
    """Validate user answer and reply on it.
    """
    translation_id, user_answer = call.data.split(":")
    translation = crud.get_translation_by_id(translation_id=translation_id)

    message_text = f"Как переводится *'{
        translation["en_text"]}'* ?\nВаш ответ: *'{user_answer}'* "

    if user_answer == translation["ru_text"]:
        message_text += f"✅\nОтлично, вы заработали 1 балл! 🎉"
        log.info(f"User {call.message.chat.id} answered correct!")
        crud.update_user_score(tg_id=call.message.chat.id, num=1)

    else:
        message_text += f"❌\nПравильный ответ: *'{translation["ru_text"]}*'"
        log.info(f"User {call.message.chat.id} answered incorrect!")

    markup = InlineKeyboardMarkup()
    markup.add(IBtn(text="Ещё квиз", callback_data="/quiz"))

    bot.edit_message_text(
        text=message_text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )


def prepare_settings_keyboard(tg_id: int) -> InlineKeyboardMarkup:
    """Generate an inline keyboard for quiz settings based on the user's
    current schedule.
    """
    markup = InlineKeyboardMarkup()
    if check_user_job(user_id=tg_id):
        markup.add(
            IBtn(text="🚫 Выключить авто квиз",
                 callback_data="/settings:auto_off")
        )
        markup.add(
            IBtn(text="⏲️ Изменить интервал отправки:", callback_data=" "),
        )
        markup.row(
            IBtn(text="1 ч.", callback_data="/settings:auto_on_1h"),
            IBtn(text="2 ч.", callback_data="/settings:auto_on_2h"),
            IBtn(text="4 ч.", callback_data="/settings:auto_on_4h"),
            IBtn(text="6 ч.", callback_data="/settings:auto_on_6h"),
        )

    else:
        button = IBtn(
            text="🔁 Включить авто квиз", callback_data="/settings:auto_on_1h"
        )
        markup.add(button)

    return markup


def add_translations(text: str, tg_id: int):
    """Parses input text to extract translations and adds them to the database
    for specified user. Sends an error message if the input format is invalid.
    """
    words_to_add = {}
    for row in text.split("\n"):
        if len(row) < 4 or "  " not in row:  # skip empty or incorrect row
            continue
        try:
            en_text, ru_text = row.split("  ", maxsplit=1)
        except ValueError:
            continue

        words_to_add[en_text] = ru_text

    log.info(f"{words_to_add=}")

    if len(words_to_add) > 0:
        crud.add_translations(
            translations=words_to_add,
            tg_id=tg_id,
        )
        return

    bot.send_message(
        chat_id=tg_id,
        text=f"Неверный формат!\n/add для справки"
    )


def schedule_user_job(user_id: int, timeout: int = 1):
    """Schedule a recurring quiz job for a specific user.

    user_id: unique identifier of the user (telegram id).
    timeout: interval in hours between job executions. Defaults to 1.
    """
    job_id = f"user_{user_id}_job"
    scheduler.add_job(
        func=start_quiz,
        trigger='interval',
        hours=timeout,
        id=job_id,
        args=[user_id],
        replace_existing=True,
    )


def disable_user_job(user_id: int):
    """Disable a scheduled quiz job for a specific user.

    user_id: unique identifier of the user (telegram id).
    """
    job_id = f"user_{user_id}_job"
    scheduler.remove_job(job_id=job_id)


def check_user_job(user_id: int) -> bool:
    """Check if a quiz job is scheduled for a specific user.

    user_id: unique identifier of the user (telegram id).
    Returns True if the job exists, False otherwise.
    """
    job_id = f"user_{user_id}_job"
    if scheduler.get_job(job_id=job_id) is None:
        return False

    return True
