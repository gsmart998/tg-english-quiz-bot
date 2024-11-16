from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(String(64), unique=True)
    user_name = Column(String(128))
    user_score = Column(Integer())

    quiz_results = relationship("QuizResults", back_populates="user")
    user_translations = relationship("UserTranslations", back_populates="user")


class Translations(Base):
    __tablename__ = "translations"
    id = Column(Integer, primary_key=True)
    en_text = Column(String(255))
    ru_text = Column(String(255))

    quiz_results = relationship("QuizResults", back_populates="translation")
    user_translations = relationship(
        "UserTranslations", back_populates="translation")


class QuizResults(Base):
    __tablename__ = "quiz_results"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    translation_id = Column(Integer, ForeignKey("translations.id"))
    positive_tries = Column(Integer)
    negative_tries = Column(Integer)

    user = relationship("Users", back_populates="quiz_results")
    translation = relationship("Translations", back_populates="quiz_results")


class UserTranslations(Base):
    __tablename__ = "user_translations"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    translation_id = Column(Integer, ForeignKey(
        "translations.id"), primary_key=True)

    user = relationship("Users", back_populates="user_translations")
    translation = relationship(
        "Translations", back_populates="user_translations")
