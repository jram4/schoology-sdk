# app/mcp_server/resources.py

import os
import logging
from pathlib import Path

MIME_TYPE = "text/html+skybridge"
WIDGET_URI = "ui://widget/briefing.html"

# Store asset content in memory to avoid reading from disk on every request
_WIDGET_HTML_CACHE = None

def get_widget_html() -> str:
    """
    Reads the built React JS and CSS from the /dist folder and injects
    them into an HTML shell. This is the "inline" pattern from the official docs.
    """
    global _WIDGET_HTML_CACHE
    if _WIDGET_HTML_CACHE:
        return _WIDGET_HTML_CACHE

    try:
        # Find the path to the 'dist' directory relative to this file
        dist_path = Path(__file__).parent.parent.parent / "web" / "briefing-widget" / "dist"
        
        # Find the specific JS and CSS files Vite generates (they have hashes)
        assets_path = dist_path / "assets"
        # Use next() with a generator expression to find the first match
        js_file = next(assets_path.glob("index-*.js"))
        css_file = next(assets_path.glob("index-*.css"))

        js_content = js_file.read_text()
        css_content = css_file.read_text()
        
        html = f"""
<div id="root"></div>
<style>{css_content}</style>
<script type="module">{js_content}</script>
        """.strip()

        _WIDGET_HTML_CACHE = html
        logging.info(f"✅ Successfully loaded and cached widget assets from {dist_path}")
        return html

    except (FileNotFoundError, StopIteration) as e:
        error_msg = "FATAL: Widget asset files not found. Did you run 'npm run build' in /web/briefing-widget?"
        logging.error(f"{error_msg} - {e}")
        return f"""<div style="font-family: sans-serif; padding: 2em; color: red;">
                       <h2>Widget Error</h2><p>{error_msg}</p>
                   </div>"""

def list_resources() -> list[dict]:
    """Return list of resource definitions as dicts."""
    return [{
        "uri": WIDGET_URI,
        "mimeType": MIME_TYPE,
        "name": "Daily Briefing Widget",
        "description": "Interactive daily briefing with assignments"
    }]

def read_resource(uri: str) -> dict | None:
    """Read a resource and return its contents."""
    if uri != WIDGET_URI:
        return None
    
    return {
        "contents": [{
            "uri": WIDGET_URI,
            "mimeType": MIME_TYPE,
            "text": get_widget_html(),
        }]
    }