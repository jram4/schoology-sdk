# app/scheduler/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.scheduler.sync_job import sync_schoology_data
import random
import logging
from datetime import datetime, timezone # <-- ADD THIS

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
    
    logging.info("Initializing and starting background scheduler...")
    _scheduler = BackgroundScheduler(timezone="UTC")
    # Run every 5 minutes with jitter
    _scheduler.add_job(
        _job_wrapper, 
        IntervalTrigger(minutes=5, jitter=random.randint(0, 60)),
        id="schoology_sync_job",
        replace_existing=True,
        misfire_grace_time=300 # 5 minutes grace period
    )
    _scheduler.start()
    # Trigger the first run immediately
    _scheduler.get_job('schoology_sync_job').modify(next_run_time=datetime.now(timezone.utc))
    logging.info("Scheduler started and first sync triggered.")
    return _scheduler

def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        logging.info("Shutting down background scheduler...")
        _scheduler.shutdown()
        logging.info("Scheduler shut down.")