from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.scheduler.sync_job import sync_schoology_data
import random

_scheduler: BackgroundScheduler | None = None

def _job_wrapper():
    db: Session = SessionLocal()
    try:
        sync_schoology_data(db)
    finally:
        db.close()

def start_scheduler():
    global _scheduler
    if _scheduler:
        return _scheduler
    _scheduler = BackgroundScheduler(timezone="UTC")
    # jitter to avoid thundering herd; run every 5 minutes
    _scheduler.add_job(_job_wrapper, IntervalTrigger(minutes=5, jitter=random.randint(0, 60)))
    _scheduler.start()
    return _scheduler
