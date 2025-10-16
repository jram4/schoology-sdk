# main.py

import uvicorn
import os
import logging
from app.mcp_server.server import app

def main():
    """Main entry point to run the application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s'
    )

    # Get host and port from environment, with defaults
    # Note: load_dotenv() is now called inside the lifespan manager
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "5544")) # Default to your port
    
    logging.info(f"🚀 Starting Uvicorn server process on http://{host}:{port}")
    # Run the FastAPI app using uvicorn
    # The 'app' object now contains the lifespan logic
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()