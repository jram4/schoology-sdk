# app/scheduler/sync_job.py

import logging
import os
from sqlalchemy.orm import Session
from app.schoology_client.client import SchoologyClient
from app.database import crud
from datetime import datetime, timedelta, timezone

def sync_schoology_data(db: Session):
    logging.info("Starting Schoology sync job...")
    client = SchoologyClient()

    try:
        # --- 1. Sync Calendar Events (Existing) ---
        now = datetime.now(timezone.utc)
        # Fetch a wide window: from 1 week ago to 60 days in the future
        start_date = now - timedelta(days=7)
        end_date = now + timedelta(days=60)
        
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())
        
        events_data = client.get_calendar_events(start_ts=start_ts, end_ts=end_ts)
        
        if events_data:
            logging.info(f"Fetched {len(events_data)} calendar items. Upserting into database...")
            crud.upsert_calendar_events(db, events_data)
        else:
            logging.warning("No calendar items returned from Schoology client.")

        # --- 2. Sync Course Materials (New) ---
        course_ids_str = os.getenv("SCHOOLOGY_COURSE_IDS")
        if not course_ids_str:
            logging.warning("SCHOOLOGY_COURSE_IDS not set in .env. Skipping material sync.")
        else:
            course_ids = [int(cid.strip()) for cid in course_ids_str.split(',') if cid.strip()]
            logging.info(f"Found {len(course_ids)} course(s) to sync for materials.")
            
            for course_id in course_ids:
                try:
                    materials_data = client.get_course_materials(course_id)
                    if materials_data:
                        crud.upsert_resources(db, course_id, materials_data)
                    else:
                        logging.info(f"No materials found for course {course_id}. Nothing to sync.")
                except Exception as e:
                    logging.error(f"Failed to sync materials for course {course_id}: {e}", exc_info=True)
                    # Continue to the next course even if one fails
                    continue
        
        logging.info("Sync job completed successfully.")
        return {"ok": True}

    except Exception as e:
        logging.error(f"A critical error occurred during the sync job: {e}", exc_info=True)
        db.rollback() # Rollback any partial changes on error
        return {"ok": False, "error": str(e)}