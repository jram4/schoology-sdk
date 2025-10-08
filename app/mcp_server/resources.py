# app/mcp_server/resources.py

from typing import Dict, Any, List
from datetime import datetime

def render_briefing_widget(assignments: List[Dict[str, Any]], generated_at: str) -> str:
    """
    Server-side render the briefing widget with actual data.
    """
    
    def format_datetime(iso_str: str) -> str:
        """Format ISO datetime for display"""
        if not iso_str:
            return ""
        try:
            dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
            return dt.strftime('%b %d, %Y — %I:%M %p UTC')
        except:
            return iso_str
    
    # Build assignment HTML
    if not assignments:
        assignments_html = '<div style="opacity:.7;">No urgent assignments.</div>'
    else:
        items_html = []
        for item in assignments:
            title = item.get('title', 'Untitled')
            course = item.get('course', '')
            due_at = format_datetime(item.get('dueAt', ''))
            url = item.get('url', '')
            
            course_html = f' — <em>{course}</em>' if course else ''
            link_html = f'<a href="{url}" target="_blank" rel="noopener noreferrer" style="font-size:12px; text-decoration:none; color:#0066cc;">View Assignment →</a>' if url else ''
            
            items_html.append(f'''
                <div style="padding:8px 0; border-top:1px solid rgba(0,0,0,.08);">
                    <div style="display:flex; justify-content:space-between; gap:8px;">
                        <div style="min-width:0;">
                            <strong style="word-break:break-word;">{title}</strong>{course_html}
                        </div>
                        <div style="white-space:nowrap; opacity:.8; font-size:12px;">{due_at}</div>
                    </div>
                    {link_html}
                </div>
            ''')
        assignments_html = ''.join(items_html)
    
    gen_text = f'Generated: {format_datetime(generated_at)}' if generated_at else ''
    
    return f'''
<div id="briefing-root" style="font: 14px/1.35 system-ui, -apple-system, Segoe UI, Roboto, sans-serif; padding: 8px 12px;">
    <h3 style="margin:0 0 8px;">Daily Briefing</h3>
    <div style="opacity:.7; font-size:12px; margin-bottom:8px;">{gen_text}</div>
    <div id="assignments">{assignments_html}</div>
</div>
    '''.strip()


def get_briefing_resource(assignments: List[Dict[str, Any]], generated_at: str) -> Dict[str, Any]:
    """Generate the briefing resource with rendered HTML"""
    html = render_briefing_widget(assignments, generated_at)
    
    return {
        "contents": [
            {
                "uri": "ui://widget/briefing.html",
                "mimeType": "text/html+skybridge",
                "text": html,
                "_meta": {
                    "openai/widgetDescription": (
                        "Displays upcoming assignments within the requested time range. "
                        "The widget shows a prioritized list of assignments with due dates and links."
                    ),
                    "openai/widgetPrefersBorder": True,
                }
            }
        ]
    }


# Static resource list (for resources/list calls)
def list_resources():
    return [{
        "name": "briefing-widget",
        "uri": "ui://widget/briefing.html",
        "mimeType": "text/html+skybridge",
        "description": "Daily Briefing component (dynamically rendered)"
    }]


def list_templates():
    return list_resources()

# --- ADDED: The missing read_resource function ---
def read_resource(uri: str) -> Dict[str, Any] | None:
    """
    Handles 'resources/read' calls. Since our widget is dynamic, we return
    an empty-state version of it if requested directly.
    """
    if uri == "ui://widget/briefing.html":
        # Return the widget with no assignments (its base state)
        return get_briefing_resource(assignments=[], generated_at="")
    
    # No other known resources
    return None