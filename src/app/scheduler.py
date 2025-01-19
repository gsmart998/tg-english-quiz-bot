import os

from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from database.database import Session
from app.logger_config import get_logger
from app.tg_bot import bot
from app.handlers import start_quiz

log = get_logger(__name__)  # get configured logger

# configure scheduler
load_dotenv()
jobstores = {'default': SQLAlchemyJobStore(url=os.getenv("DATABASE_URL"))}
scheduler = BackgroundScheduler(jobstores=jobstores)


def schedule_user_job(user_id: int, timeout: int = 1):
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
    job_id = f"user_{user_id}_job"
    scheduler.remove_job(job_id=job_id)


def check_user_job(user_id: int) -> bool:
    job_id = f"user_{user_id}_job"
    if scheduler.get_job(job_id=job_id) is None:
        return False
    return True
