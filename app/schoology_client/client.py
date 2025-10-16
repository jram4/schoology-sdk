# app/schoology_client/client.py

import os
import requests
import time
import logging
from typing import List, Dict, Any
from datetime import datetime

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
            "Cookie": cookie,
            "Referer": f"{self.base_url}/home"
        })

    def get_calendar_events(self, start_ts: int, end_ts: int) -> List[Dict[str, Any]]:
        """
        Fetches calendar events (assignments, events, etc.) for the user within a given timestamp range.
        """
        view_id = "2025-91" # From your captured network request
        url = f"{self.base_url}/calendar/{self.user_id}/{view_id}"
        
        params = {
            "ajax": 1,
            "start": start_ts,
            "end": end_ts,
            "_": int(time.time() * 1000)
        }
        
        # --- NEW: VERBOSE LOGGING ---
        logging.info(f"ATTEMPTING TO FETCH URL: {url}")
        logging.info(f"WITH PARAMS: {params}")
        logging.info(f"WITH HEADERS: {self.s.headers}")
        # --- END NEW LOGGING ---

        response = None # Define response here to be available in except block
        try:
            response = self.s.get(url, params=params)
            response.raise_for_status()
            
            # If we get here, the request was successful (2xx status code)
            # Now, try to parse it as JSON
            return response.json()

        except Exception as e:
            logging.error(f"AN EXCEPTION OCCURRED: {type(e).__name__} - {e}")
            
            # --- NEW: VERBOSE ERROR LOGGING ---
            if response is not None:
                logging.error(f"RESPONSE STATUS CODE: {response.status_code}")
                logging.error("--- RAW SERVER RESPONSE TEXT ---")
                # We are logging the raw text to see if it's an HTML login page
                logging.error(f"\n{response.text}\n")
                logging.error("--- END RAW SERVER RESPONSE TEXT ---")
            else:
                logging.error("Request failed before a response was received.")
            # --- END NEW ERROR LOGGING ---
        
        return []

    # --- Stubs for future implementation ---
    def get_feed_updates(self):
        return []

    def get_grades(self, course_id: int):
        return []

    def get_course_assignments(self, course_id: int):
        return []