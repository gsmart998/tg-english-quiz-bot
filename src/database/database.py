import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base
from src.app.logger_config import get_logger


log = get_logger(__name__)  # get configured logger


try:
    load_dotenv()
    engine = create_engine(os.getenv("DATABASE_URL"))
    log.info("Engine created!")
except Exception as ex:
    log.error(f"Engine not created! {ex}")


# create tables
def init_db():
    Base.metadata.create_all(bind=engine)
    log.info("The database has been initialized")


Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
