from sqlalchemy import func

from database.models import Users, Translations, UserTranslations
from database.database import Session


def create_user(name: str, tg_id: int):
    with Session() as session:
        user = session.query(Users).filter(
            Users.user_tg_id == tg_id).one_or_none()
        if user is None:
            new_user = Users(user_tg_id=tg_id, user_name=name)
            session.add(new_user)
            session.commit()
            print("User created!")

        else:
            print(f"User with {tg_id=} already exist!")


def get_translation(tg_id: int) -> dict | None:
    """Fetch users translations and return dict {
    'id': translation_id,
    'en_text': translation.en_text,
    'option_1': translation.ru_text(correct),
    'option_2': translation.ru_text(wrong),
    'option_3': translation.ru_text(wrong)
    }
    """
    with Session() as session:
        translations = session.query(Translations).join(
            UserTranslations, UserTranslations.translation_id == Translations.id
        ).join(
            Users, Users.id == UserTranslations.user_id
        ).filter(
            Users.user_tg_id == tg_id
        ).order_by(func.random()).limit(3).all()

        if len(translations) < 3:
            print("User needs to add more translations!")
            return

        quiz_words = {}
        for i, t in enumerate(translations):
            if i == 0:
                quiz_words["id"] = t.id
                quiz_words["en_word"] = t.en_text
            quiz_words[f"option_{i+1}"] = t.ru_text

    return quiz_words


def validate_translation(translation_id: int, ru_text: str) -> bool:
    with Session() as session:
        translation: Translations = session.query(Translations).filter(
            Translations.id == translation_id).one_or_none()
        if translation.ru_text == ru_text:
            return True
        return False
