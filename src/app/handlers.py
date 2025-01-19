import random

from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton as IBtn,
    CallbackQuery,
)

from database.crud import (
    get_translations_by_user,
    get_translation_by_id,
    update_user_score,
)
from app.logger_config import get_logger
from app.tg_bot import bot
from app.app_config import BUTTONS_NUM
from app.text_templates import MSG_START_QUIZ_ERROR


log = get_logger(__name__)  # get configured logger


def start_quiz(tg_id: int):
    """Fetch user's translations from DB and prepare it.
    Then sends the prepared quiz to the user.
    """
    log.info(f"User {tg_id=} started the quiz")

    quiz_words = get_translations_by_user(tg_id=tg_id)
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
    translation = get_translation_by_id(translation_id=translation_id)

    message_text = f"Как переводится *'{
        translation["en_text"]}'* ?\nВаш ответ: *'{user_answer}'* "

    if user_answer == translation["ru_text"]:
        message_text += f"✅\nОтлично, вы заработали 1 балл! 🎉"
        log.info(f"User {call.message.chat.id} answered correctly")
        update_user_score(tg_id=call.message.chat.id, num=1)

    else:
        message_text += f"❌\nПравильный ответ: *'{translation["ru_text"]}*'"
        log.info(f"User {call.message.chat.id} answered incorrectly")

    markup = InlineKeyboardMarkup()
    markup.add(IBtn(text="Ещё квиз", callback_data="/quiz"))

    bot.edit_message_text(
        text=message_text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
    )
