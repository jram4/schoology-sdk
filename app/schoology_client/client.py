# app/schoology_client/client.py

import os
import requests
import time
import logging
import re
import random
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from collections import deque # <-- NEW IMPORT

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

        # --- NEW RATE-LIMITING INSTANCE VARIABLES ---
        self.request_timestamps = deque()
        self.RATE_LIMIT_COUNT = 15
        self.RATE_LIMIT_SECONDS = 5
    
    # --- NEW RATE-LIMITING METHOD ---
    def _rate_limited_get(self, *args, **kwargs):
        """
        A wrapper for requests.get that enforces the 15 requests/5 sec rule.
        """
        now = time.monotonic()
        
        # Remove timestamps older than our time window
        while self.request_timestamps and now - self.request_timestamps[0] > self.RATE_LIMIT_SECONDS:
            self.request_timestamps.popleft()
            
        # If we have hit the request limit, calculate wait time and sleep
        if len(self.request_timestamps) >= self.RATE_LIMIT_COUNT:
            oldest_request_time = self.request_timestamps[0]
            time_since_oldest = now - oldest_request_time
            wait_time = self.RATE_LIMIT_SECONDS - time_since_oldest
            
            if wait_time > 0:
                logging.info(f"Rate limit reached. Waiting for {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        
        # Make the request and record the timestamp
        response = self.s.get(*args, **kwargs)
        self.request_timestamps.append(time.monotonic())
        return response

    def _parse_material_rows(self, soup: BeautifulSoup, resource_type: str) -> List[Dict[str, Any]]:
        # ... (this method is unchanged) ...
        materials = []
        rows = soup.find_all('div', class_='filtered-view-list-row')
        for row in rows:
            try:
                title_element = row.find('div', class_='s-common-block_title').find('a')
                if not title_element: continue
                title = title_element.get_text(strip=True)
                relative_url = title_element['href']
                absolute_url = f"{self.base_url}{relative_url}"
                schoology_id_match = re.search(r'/(\d+)$', relative_url)
                if not schoology_id_match: schoology_id_match = re.search(r'/(\d+)/', relative_url)
                schoology_id = int(schoology_id_match.group(1)) if schoology_id_match else None
                parent_folder = None
                parent_folder_element = row.find('div', class_='materials-filtered-parent-folder')
                if parent_folder_element:
                    tooltip = parent_folder_element.find('span', attrs={'role': 'tooltip'})
                    if tooltip and tooltip.has_attr('aria-label'): parent_folder = tooltip['aria-label'].strip()
                materials.append({"schoology_id": schoology_id, "title": title, "url": absolute_url, "resource_type": resource_type, "parent_folder": parent_folder})
            except Exception as e:
                logging.warning(f"Could not parse a material row. Error: {e}", exc_info=True)
                continue
        return materials

    def get_course_materials(self, course_id: int) -> List[Dict[str, Any]]:
        # ... (this method is updated to use the new rate-limiter) ...
        logging.info(f"Starting material sync for course ID: {course_id}")
        all_materials = []
        filter_map = {"assignments": "Assignment", "assessments": "Assessment", "documents_files": "File", "documents_links": "Link", "discussion": "Discussion", "pages": "Page"}
        url = f"{self.base_url}/course/{course_id}/materials"
        
        for filter_name, resource_type in filter_map.items():
            params = {"list_filter": filter_name, "ajax": 1, "style": "full", "_": int(time.time() * 1000)}
            logging.info(f"Fetching '{resource_type}' materials for course {course_id}...")
            
            try:
                # --- USE THE RATE-LIMITED GETTER ---
                response = self._rate_limited_get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data or not isinstance(data, dict) or not data.values():
                    logging.info(f"No content returned for filter '{filter_name}'. Skipping.")
                    continue
                
                html_content = list(data.values())[0]
                soup = BeautifulSoup(html_content, 'html.parser')
                parsed_items = self._parse_material_rows(soup, resource_type)
                if parsed_items:
                    logging.info(f"Found {len(parsed_items)} item(s) of type '{resource_type}'.")
                    all_materials.extend(parsed_items)
                
                # We no longer need the static sleep here
                # time.sleep(random.uniform(2, 4)) 

            except requests.RequestException as e:
                logging.error(f"Network error fetching materials for course {course_id} with filter {filter_name}: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred for course {course_id} with filter {filter_name}: {e}", exc_info=True)
        
        logging.info(f"Completed material sync for course {course_id}. Found {len(all_materials)} total items.")
        return all_materials

    def get_calendar_events(self, start_ts: int, end_ts: int) -> List[Dict[str, Any]]:
        # ... (this method is updated to use the new rate-limiter) ...
        view_id = "2025-91"
        url = f"{self.base_url}/calendar/{self.user_id}/{view_id}"
        params = {"ajax": 1, "start": start_ts, "end": end_ts, "_": int(time.time() * 1000)}
        logging.info(f"ATTEMPTING TO FETCH URL: {url}")
        
        response = None 
        try:
            # --- USE THE RATE-LIMITED GETTER ---
            response = self._rate_limited_get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"AN EXCEPTION OCCURRED: {type(e).__name__} - {e}")
            if response is not None:
                logging.error(f"RESPONSE STATUS CODE: {response.status_code}")
                logging.error(f"--- RAW SERVER RESPONSE TEXT ---\n{response.text}\n--- END ---")
            else:
                logging.error("Request failed before a response was received.")
        return []

    # --- Stubs for future implementation ---
    def get_feed_updates(self): return []
    def get_grades(self, course_id: int): return []
    def get_course_assignments(self, course_id: int): return []