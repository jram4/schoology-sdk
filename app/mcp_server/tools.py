# app/mcp_server/tools.py

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Any, Dict, List
import logging
from app.database import crud
import mcp.types as types

WIDGET_URI = "ui://widget/briefing.html"
MIME_TYPE = "text/html+skybridge"

def _tool_meta():
    """Metadata that tells ChatGPT this tool produces a widget."""
    return {
        "openai/outputTemplate": WIDGET_URI,
        "openai/toolInvocation/invoking": "Gathering your assignments...",
        "openai/toolInvocation/invoked": "Here's your briefing",
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": False,
            "readOnlyHint": True,
        }
    }

def _embedded_widget_resource() -> types.EmbeddedResource:
    """Returns the embedded widget resource as proper MCP type."""
    from app.mcp_server.resources import get_widget_html
    
    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=WIDGET_URI,
            mimeType=MIME_TYPE,
            text=get_widget_html(),
            title="Daily Briefing",
        )
    )

def list_tools() -> List[Dict[str, Any]]:
    """Return list of tool definitions as dicts."""
    return [{
        "name": "briefing.get",
        "title": "Get Daily Briefing",
        "description": "Returns an interactive list of upcoming assignments",
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
            "additionalProperties": False
        },
        "_meta": _tool_meta()
    }]

def _fmt_display(dt: datetime | None) -> str:
    if not dt:
        return ""
    try:
        # Use '%-I' on Unix-like systems for non-padded hour, fallback to '%I'
        return dt.strftime("%a, %b %d @ %-I:%M %p").replace('AM', 'am').replace('PM', 'pm')
    except ValueError:
        return dt.strftime("%a, %b %d @ %I:%M %p").replace('AM', 'am').replace('PM', 'pm')

def call_tool(name: str, args: dict, db: Session) -> types.CallToolResult:
    """Execute tool and return proper MCP result."""
    
    if name != "briefing.get":
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Unknown tool: {name}")],
            isError=True
        )
    
    window = args.get("range", "today").lower().strip()
    hours_map = {"today": 24, "48h": 48, "week": 168}
    hours = hours_map.get(window, 24)
    label_map = {"today": "today", "48h": "the next 48h", "week": "the next 7 days"}
    label = label_map.get(window, "soon")
    
    assignments = crud.upcoming_assignments(db, window_hours=hours, limit=50)
    
    # Data for the UI (_meta): The full, detailed list
    ui_items = [{
        "id": a.id, "title": a.title, "course": a.course_name, "url": a.url,
        "dueAt": a.due_at_utc.isoformat() if a.due_at_utc else None,
        "dueAtDisplay": _fmt_display(a.due_at_utc)
    } for a in assignments]
    
    # Data for the Model (structuredContent): A concise summary
    model_summary_items = [{
        "title": a.title, "course": a.course_name,
        "due": _fmt_display(a.due_at_utc)
    } for a in assignments[:5]] # Only show top 5 to the model

    # Build the final payloads
    structured = {
        "summary": {
            "count": len(assignments),
            "rangeLabel": label,
            "assignments": model_summary_items
        }
    }
    
    meta_for_ui = {
        "assignments": ui_items,
        "count": len(assignments),
        "range": window,
        "rangeLabel": label,
        "generatedAt": datetime.now(timezone.utc).isoformat()
    }
    
    widget_resource = _embedded_widget_resource()
    
    return types.CallToolResult(
        content=[types.TextContent(
            type="text",
            text=f"Found {len(assignments)} assignment(s) due {label}."
        )],
        structuredContent=structured,
        # ✅ THE FIX IS HERE: `_meta=` instead of `meta=`
        _meta={
            **_tool_meta(),
            "openai.com/widget": widget_resource.model_dump(mode="json"),
            "ui": meta_for_ui # Nest all UI-specific data here
        }
    )