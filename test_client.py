# test_client.py

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from app.schoology_client.client import SchoologyClient

def test_calendar_fetch():
    """
    Loads environment variables and fetches calendar events for the next 30 days.
    """
    # Load .env file from the project root
    print("Loading environment variables...")
    load_dotenv()

    # Check if credentials are loaded
    cookie = os.getenv("SCHOOLOGY_COOKIE")
    user_id = os.getenv("SCHOOLOGY_USER_ID")
    if not cookie or not user_id:
        print("❌ ERROR: SCHOOLOGY_COOKIE and SCHOOLOGY_USER_ID must be set in your .env file.")
        return

    print("Credentials loaded. Initializing Schoology Client...")
    client = SchoologyClient()

    # Define the time range: from now to 30 days from now
    now = datetime.now(timezone.utc)
    end_date = now + timedelta(days=30)
    
    start_timestamp = int(now.timestamp())
    end_timestamp = int(end_date.timestamp())

    print(f"\nFetching events from {now.isoformat()} to {end_date.isoformat()}...")
    events = client.get_calendar_events(start_ts=start_timestamp, end_ts=end_timestamp)

    if not events:
        print("\n❌ No events returned. Check the following:")
        print("   1. Is your SCHOOLOGY_COOKIE valid and not expired?")
        print("   2. Is the SCHOOLOGY_USER_ID correct?")
        print("   3. Is there an issue with the constructed URL or network connectivity?")
        return

    print(f"\n✅ Successfully fetched {len(events)} events!")
    print("--- Sample Events ---")
    
    for i, event in enumerate(events[:5]): # Print the first 5 events
        event_type = event.get('e_type', 'N/A')
        title = event.get('titleText', 'No Title')
        source = event.get('content_title', 'N/A')
        start_time = event.get('start', 'N/A')
        
        print(f"\nEvent {i+1}:")
        print(f"  Title: {title}")
        print(f"  Type: {event_type}")
        print(f"  Source: {source}")
        print(f"  Start Time: {start_time}")
    
    print("\n--- End of Sample ---")


if __name__ == "__main__":
    test_calendar_fetch()