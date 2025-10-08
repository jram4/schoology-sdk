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
            "title": "Get Briefing",
            "description": (
                "Retrieves upcoming assignments and deadlines. "
                "Use 'today' for urgent items due in the next 24 hours, "
                "'48h' for the next 2 days, or 'week' for the next 7 days. "
                "Defaults to 'today' if not specified. "
                "When the user asks for a 'weekly briefing' or 'this week', use range='week'."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "range": {
                        "type": "string",
                        "enum": ["today", "48h", "week"],
                        "default": "today",
                        "description": "Time window: 'today' (24h), '48h' (2 days), or 'week' (7 days)"
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
        # Get the range parameter and normalize it
        window = (args.get("range") or "today").lower().strip()
        
        # Map various phrasings to our three canonical ranges
        synonyms = {
            "today": ["today", "now", "tonight", "current", "urgent"],
            "48h": ["48h", "2d", "two days", "next 48 hours", "tomorrow", "next two days"],
            "week": ["week", "weekly", "this week", "7d", "next 7 days", "seven days", "next week"]
        }
        
        def pick_range(s):
            """Match the input string to a time range, defaulting to 'today'."""
            s_lower = s.lower().strip()
            for key, vals in synonyms.items():
                if s_lower == key or s_lower in vals:
                    return key
            return "today"

        r = pick_range(window)
        hours = 24 if r == "today" else (48 if r == "48h" else 168)
        assignments = crud.upcoming_assignments(db, window_hours=hours, limit=10)
        
        # Build structured data
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
        
        generated_at = datetime.now(timezone.utc).isoformat()
        
        # Import here to avoid circular dependency
        from app.mcp_server.resources import get_briefing_resource
        
        # Generate the widget HTML with actual data
        widget_resource = get_briefing_resource(items, generated_at)
        
        return {
            "structuredContent": {
                "highPriority": items,
                "announcements": [],
                "events": [],
                "generatedAt": generated_at,
            },
            "content": [{"type": "text", "text": "Here's your current briefing."}],
            "_meta": {
                "openai/outputTemplate": "ui://widget/briefing.html",
                # Embed the rendered widget
                "openai/embeddedResource": widget_resource
            },
        }

    # unknown tool
    return {
        "error": {"message": f"Unknown tool: {name}"},
        "structuredContent": {},
        "_meta": {},
    }
