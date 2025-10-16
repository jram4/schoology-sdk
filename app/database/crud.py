# app/database/crud.py

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo  # <-- KEEP THIS FOR REFERENCE, BUT NO LONGER USED IN PARSING  # noqa: F401
from app.database import models
import re

# ---- FIXED: Remove status filter since it's not being set by sync ----
def upcoming_assignments(db: Session, window_hours: int = 48, limit: int = 20):
    """
    Return assignments due within the next `window_hours`.
    """
    now = datetime.now(timezone.utc)
    end = now + timedelta(hours=window_hours)
    q = (
        db.query(models.Assignment)
        # REMOVED: .filter(models.Assignment.status == "open")
        .filter(models.Assignment.due_at_utc != None)  # noqa: E711
        .filter(models.Assignment.due_at_utc >= now)
        .filter(models.Assignment.due_at_utc <= end)
        .order_by(models.Assignment.due_at_utc.asc())
        .limit(limit)
    )
    return q.all()

def parse_html_title(html_title: str) -> str:
    """Extracts clean text from the Schoology HTML title."""
    if not html_title:
        return "Untitled"
    clean = re.sub('<.*?>', '', html_title)
    return clean.strip()

def parse_schoology_date(date_str: str) -> datetime | None:
    """
    Parses Schoology's 'YYYY-MM-DD HH:MM:SS' into UTC.

    CRITICAL FIX: Based on empirical testing, the Schoology calendar API
    returns a string that is already effectively UTC, despite appearing as
    local time. We treat the raw string as naive UTC time to avoid the
    incorrect UTC conversion offset.
    """
    if not date_str:
        return None
    dt_naive = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return dt_naive.replace(tzinfo=timezone.utc)


def upsert_calendar_events(db: Session, events: list[dict]):
    """
    Takes a list of raw event dicts from the SchoologyClient and updates or inserts
    them into the database, distinguishing between Assignments and Events.
    """
    for item in events:
        is_assignment_type = item.get('e_type') in ['assignment', 'assessment', 'common-assessment', 'discussion']
        
        if is_assignment_type:
            # FIX: Use content_id for link construction, as item['id'] is the calendar event ID
            assignment_id_for_link = item.get('content_id') 
            if not assignment_id_for_link:
                assignment_id_for_link = item['id'] 
                
            # Use the correct assignment ID and append '/info' for robust linking
            assignment_url = f"https://classes.esdallas.org/assignment/{assignment_id_for_link}/info"
            
            existing_assignment = db.query(models.Assignment).filter(models.Assignment.id == item['id']).first()
            
            if existing_assignment:
                # Update existing assignment
                existing_assignment.title = item.get('titleText', 'Untitled Assignment')
                existing_assignment.due_at_utc = parse_schoology_date(item.get('start'))
                existing_assignment.course_name = item.get('content_title', 'Unknown Course')
                existing_assignment.url = assignment_url
                existing_assignment.status = "open"  # SET STATUS HERE
                existing_assignment.last_seen_at_utc = datetime.now(timezone.utc)
            else:
                # Create new assignment
                new_assignment = models.Assignment(
                    id=item['id'],
                    title=item.get('titleText', 'Untitled Assignment'),
                    due_at_utc=parse_schoology_date(item.get('start')),
                    course_name=item.get('content_title', 'Unknown Course'),
                    url=assignment_url,
                    course_id=item.get('realm_id'),
                    status="open",  # SET STATUS HERE
                )
                db.add(new_assignment)
        else:
            # It's a generic event, handle it in the Event table
            existing_event = db.query(models.Event).filter(models.Event.id == item['id']).first()

            if existing_event:
                # Update existing event
                existing_event.title = item.get('titleText', 'Untitled Event')
                existing_event.start_utc = parse_schoology_date(item.get('start'))
                existing_event.end_utc = parse_schoology_date(item.get('end')) if item.get('has_end') == '1' else None
                existing_event.source = item.get('content_title', 'Unknown Source')
            else:
                # Create new event
                new_event = models.Event(
                    id=item['id'],
                    title=item.get('titleText', 'Untitled Event'),
                    start_utc=parse_schoology_date(item.get('start')),
                    end_utc=parse_schoology_date(item.get('end')) if item.get('has_end') == '1' else None,
                    source=item.get('content_title', 'Unknown Source'),
                )
                db.add(new_event)
                
    db.commit()