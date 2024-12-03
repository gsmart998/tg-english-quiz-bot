import os

from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from database.database import Session
from app.logger_config import get_logger
from app.tg_bot import bot
from app.quiz import start_quiz

log = get_logger(__name__)  # get configured logger

# configure scheduler
load_dotenv()
jobstores = {'default': SQLAlchemyJobStore(url=os.getenv("DATABASE_URL"))}
scheduler = BackgroundScheduler(jobstores=jobstores)


def test():
    print("hello, world")


def schedule_user_job(user_id: int):
    job_id = f"user_{user_id}_job"

    scheduler.add_job(
        func=start_quiz,
        trigger='interval',
        seconds=30,
        id=job_id,
        args=[user_id],
        replace_existing=True,
    )

# scheduler.remove_job
# schedule_user_job(user_id=6365321203)
