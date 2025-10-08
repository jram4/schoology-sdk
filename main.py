# main.py

import uvicorn
import os
from dotenv import load_dotenv
from app.database.database import init_db
from app.scheduler.scheduler import start_scheduler
from app.mcp_server.server import app

def main():
    """Main entry point to run the application."""
    # Load environment variables from .env
    load_dotenv()

    # Initialize the database (creates tables if they don't exist)
    init_db()

    # Start the background scheduler in a separate thread
    start_scheduler()

    # Get host and port from environment, with defaults
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    
    print(f"🚀 Starting MCP server on http://{host}:{port}")
    # Run the FastAPI app using uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()