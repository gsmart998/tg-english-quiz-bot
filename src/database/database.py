import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base


load_dotenv()
try:
    engine = create_engine(os.getenv("DATABASE_URL"))
    print("Engine created!")
except Exception as ex:
    print(f"Engine not created! {ex}")


# create tables
def init_db():
    Base.metadata.create_all(bind=engine)
    print("БД инициализирована!")


Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
