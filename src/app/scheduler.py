import os

from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


# configure scheduler
load_dotenv()
jobstores = {'default': SQLAlchemyJobStore(url=os.getenv("DATABASE_URL"))}
scheduler = BackgroundScheduler(jobstores=jobstores)
