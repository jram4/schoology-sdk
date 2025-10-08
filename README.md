# Schoology Co-Pilot

A conversational agent that transforms the fragmented Schoology platform into a unified, proactive assistant for students within ChatGPT.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the `.env` file and fill in your Schoology credentials:

```bash
cp .env .env.local
# Edit .env.local with your actual values
```

Required environment variables:
- `SCHOOLOGY_COOKIE`: Your session cookie from a logged-in browser
- `SCHOOLOGY_USER_ID`: Your user ID (found in Schoology URLs)
- `SCHOOLOGY_COURSE_IDS`: Comma-separated list of course IDs to monitor

### 3. Seed Sample Data (Optional)

For testing purposes, you can add sample assignments:

```bash
python seed_data.py
```

### 4. Run the Application

```bash
python main.py
```

The MCP server runs at `http://<APP_HOST>:<APP_PORT>` (defaults in `.env`).
Example with your `.env`: `http://0.0.0.0:5544`

## Project Structure

```
schoology-copilot/
├── app/
│   ├── database/          # SQLAlchemy models and database setup
│   ├── mcp_server/        # FastAPI MCP server and tools
│   ├── scheduler/         # Background data synchronization
│   └── schoology_client/  # Schoology API client
├── web/                   # React frontend (future)
├── main.py               # Application entry point
├── seed_data.py          # Sample data seeder
└── requirements.txt      # Python dependencies
```

## Features

### Current (Stub Implementation)
- **System Ping**: Basic connectivity test
- **Daily Briefing**: Shows upcoming assignments (with sample data)

### Planned
- **Performance Dashboard**: Grade tracking and trends
- **Interactive Planner**: Kanban-style task management
- **Proactive Alerts**: Real-time notifications for new grades/assignments

## Development

The application consists of three main components:

1. **Data Synchronizer**: Background scheduler that fetches data from Schoology
2. **Local Data Mirror**: SQLite database storing structured data
3. **MCP Server**: FastAPI server exposing tools to ChatGPT

## API Endpoints

- `GET /healthz` - Health check
- `POST /mcp` - MCP protocol endpoint (JSON-RPC 2.0)

## MCP Tools (JSON-RPC 2.0)
**List tools**
```bash
curl -s -X POST http://127.0.0.1:5544/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"list_tools"}'
```
**Call `system.ping`**
```bash
curl -s -X POST http://127.0.0.1:5544/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"call_tool","params":{"name":"system.ping"}}'
```
**Call `briefing.get`**
```bash
curl -s -X POST http://127.0.0.1:5544/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":3,"method":"call_tool","params":{"name":"briefing.get","args":{"range":"48h"}}}'
```

## Next Steps

1. Implement real Schoology API endpoints in `SchoologyClient`
2. Add grade tracking and performance dashboard
3. Build interactive planner with Kanban board
4. Create React frontend components
5. Add real-time notifications and alerts