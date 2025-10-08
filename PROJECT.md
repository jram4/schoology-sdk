# `PROJECT.md`

## Project Name: Schoology Co-Pilot

### 1. Project Goal

To create a conversational agent within ChatGPT that provides a unified, proactive interface to a student's Schoology data. This project will be implemented as a single, self-contained Python application running locally on a desktop PC. It will handle data fetching, storage, and serving requests from the OpenAI Apps SDK via the Model Context Protocol (MCP).

### 2. Core Architecture

The application consists of three primary, concurrently operating components:

1.  **Data Synchronizer:** A background scheduler (`apscheduler`) that periodically fetches data from Schoology's internal web APIs.
2.  **Local Data Mirror:** A single-file SQLite database (`schoology.db`) that stores a structured, clean version of the fetched data. SQLAlchemy will be used as the ORM.
3.  **MCP Server:** A FastAPI application running on Uvicorn that exposes a `/mcp` endpoint. It serves near-instantaneous responses to ChatGPT by querying the local SQLite database, not by making live requests to Schoology.

### 3. Tech Stack

*   **Backend Framework:** FastAPI with Uvicorn
*   **Web Client:** `requests`
*   **HTML Parsing:** `beautifulsoup4`
*   **Scheduling:** `apscheduler`
*   **Database/ORM:** SQLite with SQLAlchemy
*   **Configuration:** `python-dotenv`
*   **Frontend (UI Component):** React (This part is separate and will be built in the `web/` directory)

### 4. Project Structure

```
schoology-copilot/
├── app/
│   ├── database/
│   │   ├── crud.py         # Data access functions (Create, Read, Update).
│   │   ├── database.py     # SQLAlchemy engine and session management.
│   │   └── models.py       # SQLAlchemy ORM models (tables).
│   ├── mcp_server/
│   │   ├── server.py       # FastAPI app definition and /mcp route.
│   │   └── tools.py        # Logic for each MCP tool (e.g., get_daily_briefing).
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

### 5. Implementation Details & Data Flow

#### **Step 1: Configuration (`.env`)**

*   Authentication with Schoology will be handled via a session cookie.
*   The `.env` file must contain:
    *   `SCHOOLOGY_COOKIE`: The full cookie string copied from a logged-in browser session.
    *   `SCHOOLOGY_USER_ID`: The user's unique ID found in Schoology URLs.
    *   `SCHOOLOGY_COURSE_IDS`: A comma-separated list of numeric course IDs for targeted scraping.

#### **Step 2: Schoology Client (`app/schoology_client/client.py`)**

*   A `SchoologyClient` class will encapsulate all web requests.
*   It will initialize with headers containing the `SCHOOLOGY_COOKIE` from the `.env` file.
*   It must implement methods to fetch key data points. Start with:
    *   `get_calendar_events(start_ts, end_ts)`: Hits the `/calendar/...` endpoint. This returns structured JSON directly.
    *   `get_feed_updates()`: Hits the `/home/feed` endpoint. This returns JSON containing an HTML blob that must be parsed with BeautifulSoup.
    *   `get_grades(course_id)`: (Endpoint to be discovered) Fetches grades for a specific course.
    *   `get_course_assignments(course_id)`: Hits the `/course/.../materials?list_filter=assignments` endpoint. This returns JSON with HTML to be parsed.

#### **Step 3: Database Models (`app/database/models.py`)**

*   Define SQLAlchemy ORM models for each data type. All models should inherit from a declarative `Base`.
*   **`Assignment` Model:** `id` (Schoology's ID, primary key), `title`, `due_date`, `course_name`, `url`.
*   **`Event` Model:** `id`, `title`, `start_time`, `end_time`, `source` (e.g., 'Class of 2026').
*   **`Update` Model:** `id`, `author`, `content_html`, `timestamp`, `source`.
*   **`Grade` Model:** `id`, `assignment_title`, `score_raw` (e.g., "92/100"), `course_name`.

#### **Step 4: Data Synchronization (`app/scheduler/sync_job.py`)**

*   The `sync_schoology_data()` function is the core of the cron job.
*   On each run, it will:
    1.  Instantiate `SchoologyClient`.
    2.  Get a new database session (`SessionLocal()`).
    3.  Call the client's fetch methods to get fresh data.
    4.  Iterate through the results. For each item (e.g., an assignment), use a `crud` function to perform an "upsert":
        *   If an assignment with that ID already exists in the database, update its fields.
        *   If it doesn't exist, create a new record.
    5.  Commit the session and close it.

#### **Step 5: MCP Server (`app/mcp_server/`)**

*   The `server.py` file will define the FastAPI application.
*   It will have a single POST route: `/mcp`.
*   This route will handle `list_tools` and `call_tool` requests.
*   The logic for `call_tool` will be delegated to functions in `tools.py`.
*   **Tool Functions (e.g., `build_daily_briefing(db: Session)`) will exclusively query the local SQLite database via `crud` functions.** They must **NOT** call the `SchoologyClient`. This ensures speed.
*   The tool function will format the data from the database into the required `structuredContent` JSON payload for the MCP response.

#### **Step 6: Main Entry Point (`main.py`)**

*   This script ties everything together. It will:
    1.  Load environment variables from `.env` using `dotenv`.
    2.  Initialize the database tables using `Base.metadata.create_all(bind=engine)`.
    3.  Instantiate and start the `apscheduler` in a background thread, configured to run `sync_schoology_data()` every 5 minutes.
    4.  Run the FastAPI application using `uvicorn.run()`.