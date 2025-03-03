from sqlalchemy import func

from src.database.models import Users, Translations, UserTranslations
from src.database.database import Session
from src.app.logger_config import get_logger
from src.app.app_config import BUTTONS_NUM

log = get_logger(__name__)  # get configured logger


def create_user(name: str, tg_id: int):
    """Creates new user in the database if given Telegram id does not exist.
    """
    with Session() as session:
        user_exists = session.query(
            session.query(Users).filter(Users.tg_id == tg_id).exists()
        ).scalar()
        if not user_exists:
            new_user = Users(tg_id=tg_id, name=name)
            session.add(new_user)
            session.commit()
            log.info(f"User created: {tg_id=}, {name=}")

        else:
            log.info(f"User with {tg_id=} already exist!")


def get_translation_by_id(translation_id: int) -> dict | None:
    """Fetch one translation by id and return it as dict.
    """
    with Session() as session:
        row = session.query(Translations).filter(
            Translations.id == translation_id
        ).one_or_none()

        translation = {
            "id": row.id,
            "en_text": row.en_text,
            "ru_text": row.ru_text
        }

    return translation


def get_translations_by_user(tg_id: int) -> dict | None:
    """Fetch user's translations and return it as dict.
    Number of options is configured in app_config.py, default num = 3.
    Return None if user does not have enough translations to start the quiz.

    {
    'id': translation_id,
    'en_text': translation.en_text,
    'ru_option_1': translation.ru_text(correct),
    'ru_option_2': translation.ru_text(wrong),
    'ru_option_3': translation.ru_text(wrong)
    }
    """

    with Session() as session:
        translations = session.query(Translations).join(
            UserTranslations, UserTranslations.translation_id == Translations.id
        ).filter(
            UserTranslations.user_id == tg_id
        ).order_by(func.random()).limit(BUTTONS_NUM).all()

        if len(translations) < BUTTONS_NUM:
            return

        quiz_words = {}
        for i, t in enumerate(translations):
            if i == 0:
                quiz_words["id"] = t.id
                quiz_words["en_word"] = t.en_text
            quiz_words[f"ru_option_{i+1}"] = t.ru_text

    return quiz_words


def add_translations(translations: dict[str, str], tg_id: int) -> int:
    """
    Add new translations to the database and links them to the specified user.

    Steps:
    1. Checks which translations already exist in the database.
    2. Adds new translations that are not present.
    3. Links all translations (existing and new) to the user, avoiding duplicates.
    Return num of new added user tranlations.
    """
    with Session() as session:
        # find existing translations in db
        existing_translations = session.query(Translations).filter(
            Translations.en_text.in_(translations.keys())
        ).all()

        existing_en_texts = {t.en_text for t in existing_translations}
        existing_translation_ids = {t.id for t in existing_translations}

        # add new translations
        new_translations = [
            Translations(en_text=en_text, ru_text=ru_text)
            for en_text, ru_text in translations.items()
            if en_text not in existing_en_texts
        ]
        session.bulk_save_objects(new_translations)
        session.commit()

        log.info(f"New translations added: {len(new_translations)}")

        # get new translations ids
        new_translation_ids = {
            t.id for t in session.query(Translations).filter(
                Translations.en_text.in_(translations.keys())
            ).all()
        }

        # merge tranlations ids
        all_translations_ids = existing_translation_ids.union(
            new_translation_ids)

        # find existing relationships in UserTranslations
        existing_user_translation_ids = set(
            row.translation_id for row in session.query(UserTranslations.translation_id)
            .filter(UserTranslations.user_id == tg_id)
            .all()
        )

        # add new relationships to UserTranslations
        new_user_translations = [
            UserTranslations(user_id=tg_id, translation_id=translation_id)
            for translation_id in all_translations_ids
            if translation_id not in existing_user_translation_ids
        ]
        session.bulk_save_objects(new_user_translations)
        session.commit()

        log.info(
            f"For user {tg_id=} added new translations: {
                len(new_user_translations)}"
        )
        return len(new_user_translations)


def get_user_score(tg_id: int) -> int | None:
    with Session() as session:
        return session.query(Users.score).filter(Users.tg_id == tg_id).scalar()


def update_user_score(tg_id: int, num: int) -> bool:
    with Session() as session:
        user = session.query(Users).filter(Users.tg_id == tg_id).one_or_none()
        if user:
            user.score += num
            session.commit()
            return True
        return False
