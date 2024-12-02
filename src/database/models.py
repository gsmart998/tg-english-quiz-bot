from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    tg_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String(128))
    score = Column(Integer, default=0)

    quiz_results = relationship("QuizResults", back_populates="user")
    user_translations = relationship("UserTranslations", back_populates="user")

    def __init__(self, tg_id: int, name: str):
        self.tg_id = tg_id
        self.name = name


class Translations(Base):
    __tablename__ = "translations"
    id = Column(Integer, primary_key=True)
    en_text = Column(String(255), nullable=False)
    ru_text = Column(String(255), nullable=False)

    quiz_results = relationship("QuizResults", back_populates="translation")
    user_translations = relationship(
        "UserTranslations", back_populates="translation")

    def __init__(self, en_text: str, ru_text: str):
        self.en_text = en_text
        self.ru_text = ru_text


class QuizResults(Base):
    __tablename__ = "quiz_results"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.tg_id"))
    translation_id = Column(Integer, ForeignKey("translations.id"))
    positive_tries = Column(Integer)
    negative_tries = Column(Integer)

    user = relationship("Users", back_populates="quiz_results")
    translation = relationship("Translations", back_populates="quiz_results")


class UserTranslations(Base):
    __tablename__ = "user_translations"
    user_id = Column(Integer, ForeignKey("users.tg_id"), primary_key=True)
    translation_id = Column(Integer, ForeignKey(
        "translations.id"), primary_key=True)

    user = relationship("Users", back_populates="user_translations")
    translation = relationship(
        "Translations", back_populates="user_translations")
