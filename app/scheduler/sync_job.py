# app/scheduler/sync_job.py

from sqlalchemy.orm import Session
from app.schoology_client.client import SchoologyClient
from app.database import crud
from datetime import datetime, timedelta, timezone

def sync_schoology_data(db: Session):
    print(f"[{datetime.now()}] Starting Schoology sync job...")
    client = SchoologyClient()

    try:
        # --- 1. Sync Calendar Events ---
        now = datetime.now(timezone.utc)
        # Fetch a wide window: from 1 week ago to 60 days in the future
        start_date = now - timedelta(days=7)
        end_date = now + timedelta(days=60)
        
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())
        
        events_data = client.get_calendar_events(start_ts=start_ts, end_ts=end_ts)
        
        if events_data:
            print(f"  -> Fetched {len(events_data)} calendar items. Upserting into database...")
            crud.upsert_calendar_events(db, events_data)
        else:
            print("  -> No calendar items returned from Schoology client.")

        # TODO: Add calls to sync feed, grades, etc. here in the future
        
        print(f"[{datetime.now()}] Sync job completed successfully.")
        return {"ok": True}

    except Exception as e:
        print(f"❌ An error occurred during the sync job: {e}")
        db.rollback() # Rollback any partial changes on error
        return {"ok": False, "error": str(e)}