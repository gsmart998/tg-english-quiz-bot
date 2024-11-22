import random

from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton as IBtn,
)

from database.crud import (
    get_translations_by_user,
    get_translation_by_id,
)
from app.logger_config import get_logger
from app.app_config import BUTTONS_NUM


log = get_logger(__name__)  # get configured logger


def start_quiz(tg_id: int) -> tuple | None:
    """Fetch user's translations from DB and prepare it.
    Return message_text and reply_markup
    """
    log.info(f"User {tg_id=} started the quiz")

    quiz_words = get_translations_by_user(tg_id=tg_id)
    if quiz_words is None:
        # TODO handle this case
        log.error("User needs to add more translations!")
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

    return message_text, markup


def validate_quiz(call_data: str) -> str:
    """Validate user's answer and return message_text based on it
    """
    translation_id, user_answer = call_data.split(":")

    translation = get_translation_by_id(translation_id=translation_id)

    message_text = f"Как переводится *'{
        translation["en_text"]}'* ?\nВаш ответ: *'{user_answer}'* "

    if user_answer == translation["ru_text"]:
        message_text += f"✅\nОтлично, вы заработали 1 балл! 🎉"

    else:
        message_text += f"❌\nПравильный ответ: *'{translation["ru_text"]}*'"

    return message_text
