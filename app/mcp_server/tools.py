# app/mcp_server/tools.py

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Any, Dict, List
import logging
from app.database import crud
import mcp.types as types
from collections import defaultdict

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
    return [
        {
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
        },
        {
            "name": "resources.get_all",
            "title": "Get All Course Resources",
            "description": "Performs a 'context dump' of all known materials (files, links, assignments) for a specific course, allowing the model to perform a semantic search.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "course_name": {
                        "type": "string",
                        "description": "The name of the course to fetch materials for, e.g., 'AP English' or 'Calculus'."
                    }
                },
                "required": ["course_name"],
                "additionalProperties": False
            }
        }
    ]

def _fmt_display(dt: datetime | None) -> str:
    if not dt:
        return ""
    try:
        return dt.strftime("%a, %b %d @ %-I:%M %p").replace('AM', 'am').replace('PM', 'pm')
    except ValueError:
        return dt.strftime("%a, %b %d @ %I:%M %p").replace('AM', 'am').replace('PM', 'pm')

def get_assignment_type(title: str) -> str:
    title_lower = title.lower()
    if "test" in title_lower: return "Test"
    if "quiz" in title_lower: return "Quiz"
    if "project" in title_lower: return "Project"
    if "essay" in title_lower or "paper" in title_lower: return "Paper"
    return "Homework"

def _call_briefing_get(args: dict, db: Session) -> types.CallToolResult:
    """Handles the logic for the briefing.get tool."""
    window = args.get("range", "today").lower().strip()
    hours_map = {"today": 24, "48h": 48, "week": 168}
    hours = hours_map.get(window, 24)
    label_map = {"today": "today", "48h": "the next 48h", "week": "the next 7 days"}
    label = label_map.get(window, "soon")
    
    assignments = crud.upcoming_assignments(db, window_hours=hours, limit=50)
    
    ui_items = [{
        "id": a.id, "title": a.title, "course": a.course_name, "url": a.url,
        "dueAt": a.due_at_utc.isoformat() if a.due_at_utc else None,
        "dueAtDisplay": _fmt_display(a.due_at_utc),
        "type": get_assignment_type(a.title)
    } for a in assignments]
    
    model_summary_items = [{
        "title": a.title, "course": a.course_name,
        "due": _fmt_display(a.due_at_utc)
    } for a in assignments[:5]]

    structured = { "summary": { "count": len(assignments), "rangeLabel": label, "assignments": model_summary_items } }
    
    meta_for_ui = {
        "assignments": ui_items,
        "count": len(assignments),
        "range": window,
        "rangeLabel": label,
        "generatedAt": datetime.now(timezone.utc).isoformat()
    }
    
    widget_resource = _embedded_widget_resource()
    
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Found {len(assignments)} assignment(s) due {label}.")],
        structuredContent=structured,
        _meta={
            **_tool_meta(),
            "openai.com/widget": widget_resource.model_dump(mode="json"),
            "ui": meta_for_ui
        }
    )

def _call_resources_get_all(args: dict, db: Session) -> types.CallToolResult:
    """Handles the logic for the new resources.get_all tool."""
    course_name = args.get("course_name")
    if not course_name:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text="Error: course_name is required.")],
            isError=True,
            _meta={} # THE FIX: Ensure _meta is present
        )

    resources = crud.get_resources_by_course_name(db, course_name)
    
    if not resources:
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"I couldn't find any materials for a course named '{course_name}'. Please check the name or wait for the next sync.")],
            _meta={} # THE FIX: Ensure _meta is present
        )
        
    grouped_resources = defaultdict(list)
    for res in resources:
        key = res.parent_folder or "Course Materials" 
        grouped_resources[key].append({
            "title": res.title,
            "type": res.resource_type,
            "url": res.url,
        })
        
    context_dump = {
        "courseName": course_name,
        "materialCount": len(resources),
        "structure": dict(grouped_resources)
    }
    
    return types.CallToolResult(
        content=[types.TextContent(
            type="text",
            text=f"I've retrieved all {len(resources)} materials for {course_name}. I will now use this information to find the specific resource you requested."
        )],
        structuredContent=context_dump,
        _meta={} # THE FIX: Ensure _meta is present, even if empty
    )

def call_tool(name: str, args: dict, db: Session) -> types.CallToolResult:
    """Router to execute the correct tool based on its name."""
    if name == "briefing.get":
        return _call_briefing_get(args, db)
    
    if name == "resources.get_all":
        return _call_resources_get_all(args, db)
    
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f"Unknown tool: {name}")],
        isError=True,
        _meta={} # THE FIX: Ensure _meta is present
    )