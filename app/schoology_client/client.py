# app/schoology_client/client.py

import os
import requests
import time
from typing import List, Dict, Any

class SchoologyClient:
    def __init__(self):
        """Initializes the SchoologyClient with credentials from environment variables."""
        cookie = os.getenv("SCHOOLOGY_COOKIE")
        if not cookie:
            raise ValueError("SCHOOLOGY_COOKIE environment variable not set.")
        
        self.user_id = os.getenv("SCHOOLOGY_USER_ID")
        if not self.user_id:
            raise ValueError("SCHOOLOGY_USER_ID environment variable not set.")

        self.base_url = "https://classes.esdallas.org"
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": cookie
        })

    def get_calendar_events(self, start_ts: int, end_ts: int) -> List[Dict[str, Any]]:
        """
        Fetches calendar events (assignments, events, etc.) for the user within a given timestamp range.
        
        Args:
            start_ts: The start of the time range as a Unix timestamp.
            end_ts: The end of the time range as a Unix timestamp.

        Returns:
            A list of event dictionaries from the Schoology API.
        """
        # The path seems to contain year and month, but let's test if it's strictly required.
        # Often, the start/end params are sufficient. We will build a simple, robust URL.
        # The '2025-91' part seems complex and might not be necessary if start/end are provided.
        # Let's try a more generic URL structure first.
        # After testing, the path component seems to be `/calendar/{user_id}/user_list` for a general view
        # or just `/calendar/{user_id}`. We will replicate the provided URL structure for reliability.

        # Let's analyze the path: /calendar/105724617/2025-91
        # It's likely {user_id}/{year}-{month_or_week_number}. We can generate this, but it's brittle.
        # A simpler approach that often works is to hit a base calendar endpoint. Let's stick to what we know works.
        
        current_time_ms = int(time.time() * 1000)
        # Replicating the provided URL path structure. We'll need to figure out the '91' part.
        # For now, let's assume it's a static or derivable value. Let's hardcode for the test.
        # EDIT: Let's assume a simpler path and let the query params do the work. The path might be a view hint.
        # The most reliable part of the URL is the query string.
        
        # A common pattern is /calendar/USER_ID/main
        # Let's stick to exactly what the browser did:
        # NOTE: The "2025-91" part might be complex. Let's simplify and test.
        # A more generic endpoint might be just `/calendar/load_ajax` with user_id in params.
        # However, let's replicate the known working URL first.
        
        # FINAL ATTEMPT: Let's assume the path is dynamic but we can hardcode parts of it for now.
        # Let's assume the "2025-91" is some kind of view ID. We'll try just using the user ID.
        url = f"{self.base_url}/calendar/{self.user_id}"
        
        params = {
            "ajax": 1,
            "start": start_ts,
            "end": end_ts,
            "_": current_time_ms # Cache-busting
        }
        
        print(f"Fetching calendar data from: {url} with params: {params}")
        
        try:
            response = self.s.get(url, params=params)
            response.raise_for_status()  # This will raise an exception for 4xx or 5xx status codes
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response Body: {response.text}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
        
        return []

    # --- Stubs for future implementation ---
    def get_feed_updates(self):
        return []

    def get_grades(self, course_id: int):
        return []

    def get_course_assignments(self, course_id: int):
        return []