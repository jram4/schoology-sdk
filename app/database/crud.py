# app/database/crud.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from app.database import models
import re
import logging

def upcoming_assignments(db: Session, window_hours: int = 48, limit: int = 20):
    now = datetime.now(timezone.utc)
    end = now + timedelta(hours=window_hours)
    q. Skipping material sync.")
        else:
            course_ids = [int(cid.strip()) for cid in course_ids_str.split(',') if cid.strip()]
            logging.info(f"Found {len(course_ids)} course(s) to sync for materials.")
            
            for course_id in course_ids:
                try:
                    # THE FIX: Get the course name from the DB after calendar sync
                    course_name = crud.get_course_name_from_id(db, course_id)
                    if not course_name:
                        logging.warning(f"Could not find a name for course ID {course_id}. Skipping material sync for this course.")
                        continue
                    
                    logging.info(f"Starting material sync for course: '{course_name}' (ID: {course_id})")
                    materials_data = client.get_course_materials(course_id)
                    
                    if materials_data:
                        # Pass the course_name to the upsert function
                         = (
        db.query(models.Assignment)
        .filter(models.Assignment.due_at_utc != None)
        .filter(models.Assignment.due_at_utc >= now)
        .filter(models.Assignment.due_at_utc <= end)
        .order_by(models.Assignment.due_at_utc.asc())
        .limit(limit)
    )
    return q.all()

def parse_schoology_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    dt_naive = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return dt_naive.replace(tzinfo=timezone.utc)

def upsert_calendar_events(db: Session, events: list[dict]):
    # This function is correct and unchanged
    for item in events:
        is_assignment_type = item.get('e_type') in ['crud.upsert_resources(db, course_id, course_name, materials_data)
                    else:
                        logging.info(f"No materials found for course {course_name}. Nothing to sync.")
                except Exception as e:
                    logging.error(f"Failed to sync materials for course {course_id}: {e}", exc_info=True)
                    continue

        logging.info("Sync job completed successfully.")
        return {"ok": True}

    except Exception as e:
        logging.error(f"A critical error occurred during the sync job: {e}", exc_info=True)
        db.rollback()
        return {"ok": False, "error": str(e)}