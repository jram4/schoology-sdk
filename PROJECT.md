# `PROJECT.md`

## Project Name: Schoology Co-Pilot

### 1. Project Goal

To create a conversational agent within ChatGPT that provides a unified, proactive interface to a student's Schoology data. This project will be implemented as a single, self-contained Python application running locally on a desktop PC. It will handle data fetching, storage, and serving requests from the OpenAI Apps SDK via the Model Context Protocol (MCP).

### 2. Core Architecture

The application consists of three primary, concurrently operating components:

1.  **Data Synchronizer:** A background scheduler (`apscheduler`) that periodically fetches data from Schoology's internal web APIs, creating a complete local mirror.
2.  **Local Data Mirror:** A single-file SQLite database (`schoology.db`) that stores a structured, clean, and *semantically indexed* version of the fetched data, including full course material hierarchies. SQLAlchemy will be used as the ORM.
3.  **MCP Server:** A FastAPI application running on Uvicorn that exposes a `/mcp` endpoint. It serves near-instantaneous responses to ChatGPT by querying the local SQLite database.

### 3. Tech Stack

*   **Backend Framework:** FastAPI with Uvicorn
*   **Web Client:** `requests`
*   **HTML Parsing:** `beautifulsoup4` (Critical for updates and course materials)
*   **Scheduling:** `apscheduler`
*   **Database/ORM:** SQLite with SQLAlchemy
*   **Configuration:** `python-dotenv`
*   **Frontend (UI Component):** React (using the official **Inline HTML Serving Pattern** for portability)

### 4. Project Structure (No Change Needed Here)

```
schoology-copilot/
├── app/
│   ├── database/
│   │   ├── crud.py         # Data access functions (Create, Read, Update).
│   │   ├── database.py     # SQLAlchemy engine and session management.
│   │   └── models.py       # SQLAlchemy ORM models (tables).
│   ├── mcp_server/
│   │   ├── server.py       # FastAPI app definition and /mcp route.
│   │   └── tools.py        # Logic for each MCP tool (e.g., briefing.get).
│   ├── scheduler/
│   │   ├── scheduler.py    # APScheduler initialization and management.
│   │   └── sync_job.py     # The main synchronization task function.
│   └── schoology_client/
│       └── client.py       # Class-based client for making requests to Schoology.
├── web/                      # React frontend components (handled separately).
├── main.py                   # Main application entry point.
├── schoology.db              # Local SQLite database file.
├── requirements.txt
├── .env
└── .gitignore
```

### 5. Implementation Details & Data Flow (Revised)

#### **Step 1: Configuration (`.env`)**

*   Authentication with Schoology will be handled via a session cookie.
*   The `.env` file must contain:
    *   `SCHOOLOGY_COOKIE`: The full cookie string copied from a logged-in browser session.
    *   `SCHOOLOGY_USER_ID`: The user's unique ID found in Schoology URLs.
    *   `SCHOOLOGY_COURSE_IDS`: A comma-separated list of numeric course IDs for targeted synchronization.

#### **Step 2: Schoology Client (`app/schoology_client/client.py`)**

*   A `SchoologyClient` class will encapsulate all web requests.
*   It must implement methods to fetch key data points:
    *   `get_calendar_events(start_ts, end_ts)`: Fetches calendar items (assignments/events).
    *   `get_feed_updates()`: Fetches recent activity/announcements feed (requires HTML parsing).
    *   `get_course_materials(course_id)`: **(NEW)** Fetches all materials (files, links, folders) for a specific course page (requires extensive HTML parsing to extract hierarchy and links).
    *   `get_grades(course_id)`: (Endpoint to be discovered) Fetches grades for a specific course.

#### **Step 3: Database Models (`app/database/models.py`)**

*   Define SQLAlchemy ORM models, including new models for state and resources:
    *   **`Assignment` Model:** (Existing) For calendar assignments.
    *   **`Event` Model:** (Existing) For calendar events.
    *   **`Update` Model:** (Existing) For feed posts/announcements.
    *   **`Resource` Model:** **(NEW)** To store all course materials (title, URL, type, course ID, folder/unit).
    *   **`UserState` Model:** **(NEW)** To store non-academic user state, such as `last_seen_updates_utc` for tracking unread announcements.
    *   **`Grade` Model:** (Existing) For grade tracking.

#### **Step 4: Data Synchronization (`app/scheduler/sync_job.py`)**

*   The `sync_schoology_data()` function is the core cron job.
*   It performs a complete, multi-step sync and upsert:
    1.  Sync Calendar Events.
    2.  Sync Feed Updates.
    3.  **Sync Course Materials:** Loops through all `SCHOOLOGY_COURSE_IDS`, calls `client.get_course_materials()`, and performs a structured upsert into the `Resource` table.

#### **Step 5: MCP Server (`app/mcp_server/`)**

*   The `server.py` file defines the FastAPI application and handles the JSON-RPC routing.
*   The `tools.py` file implements the core logic, using the local database exclusively for speed.
*   **New Tool:** `resources.get_all(course_name)`: Queries the `Resource` table and returns a dense, structured JSON payload (a "Context Dump") containing all materials for the specified course. **This tool returns no UI.**
*   **New Tool:** `updates.get_new()`: Queries the `Update` table relative to the user's `UserState.last_seen_updates_utc` and returns a text summary, updating the timestamp afterward.

#### **Step 6: Main Entry Point (`main.py`)**

*   This script ties everything together: loading config, initializing the database, starting the background scheduler, and running the FastAPI/MCP server.