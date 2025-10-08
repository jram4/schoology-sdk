from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database import crud

def list_tools():
    return [
        {
            "name": "system.ping",
            "title": "Ping tool",
            "description": "Use this to verify the MCP server is reachable.",
            "inputSchema": {"type": "object", "properties": {}},
            "annotations": {"readOnlyHint": True},
            "_meta": {
                # No UI for ping
            },
        },
        {
            "name": "briefing.get",
            "title": "Daily Briefing",
            "description": "Use this when the user asks what's important today/this week.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "range": {
                        "type": "string",
                        "enum": ["today", "48h", "week"],
                        "default": "today",
                    }
                },
                "additionalProperties": False,
            },
            "annotations": {"readOnlyHint": True},
            "_meta": {
                "openai/outputTemplate": "ui://widget/briefing.html",
            },
        },
    ]

def call_tool(name: str, args: dict, db: Session):
    if name == "system.ping":
        return {
            "structuredContent": {"pong": True, "now": datetime.now(timezone.utc).isoformat()},
            "content": [{"type": "text", "text": "pong"}],
            "_meta": {},
        }

    if name == "briefing.get":
        window = (args.get("range") or "today").lower()
        synonyms = {
            "today": ["today", "now", "tonight"],
            "48h": ["48h", "2d", "two days", "next 48 hours", "today and tomorrow"],
            "week": ["week", "this week", "7d", "next 7 days"]
        }
        def pick_range(s):
            for key, vals in synonyms.items():
                if s == key or s in vals:
                    return key
            return "today"

        r = pick_range(window)
        hours = 24 if r == "today" else (48 if r == "48h" else 7 * 24)
        assignments = crud.upcoming_assignments(db, window_hours=hours, limit=10)
        items = [
            {
                "type": "assignment",
                "id": a.id,
                "title": a.title,
                "dueAt": a.due_at_utc.isoformat() if a.due_at_utc else None,
                "course": a.course_name,
                "url": a.url,
            }
            for a in assignments
        ]
        return {
            "structuredContent": {
                "highPriority": items,
                "announcements": [],
                "events": [],
                "generatedAt": datetime.now(timezone.utc).isoformat(),
            },
            "content": [{"type": "text", "text": "Here's your current briefing."}],
            "_meta": {},
        }

    # unknown tool
    return {
        "error": {"message": f"Unknown tool: {name}"},
        "structuredContent": {},
        "_meta": {},
    }
