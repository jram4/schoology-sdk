# app/mcp_server/resources.py

from typing import Dict, Any

BRIEFING_HTML = """
<div id="briefing-root" style="font: 14px/1.35 system-ui, -apple-system, Segoe UI, Roboto, sans-serif; padding: 8px 12px;">
  <h3 style="margin:0 0 8px;">Daily Briefing</h3>
  <div id="generatedAt" style="opacity:.7; font-size:12px; margin-bottom:8px;"></div>
  <div id="assignments"></div>
  <div id="empty" style="opacity:.7; display:none;">No urgent assignments.</div>
</div>

<script type="module">
  const root = document.getElementById("assignments");
  const empty = document.getElementById("empty");
  const gen = document.getElementById("generatedAt");

  function fmt(dt) {
    try { return new Date(dt).toLocaleString(window.openai?.locale || undefined); }
    catch { return dt; }
  }

  function getOutput() {
    return window.openai?.toolOutput ?? {};
  }

  function render() {
    const out = getOutput();
    const list = Array.isArray(out.highPriority) ? out.highPriority : [];
    gen.textContent = out.generatedAt ? "Generated: " + fmt(out.generatedAt) : "";

    if (!list.length) {
      empty.style.display = "block";
      root.innerHTML = "";
      return;
    }

    empty.style.display = "none";
    root.innerHTML = list.map(item => {
      const due = item.dueAt ? fmt(item.dueAt) : "";
      const course = item.course ? ` — <em>${item.course}</em>` : "";
      const href = item.url ? ` href="${item.url}" target="_blank" rel="noopener noreferrer"` : "";
      return `
        <div style="padding:8px 0; border-top:1px solid rgba(0,0,0,.08);">
          <div style="display:flex; justify-content:space-between; gap:8px;">
            <div style="min-width:0;">
              <strong style="word-break:break-word;">${item.title ?? "Untitled"}</strong>${course}
            </div>
            <div style="white-space:nowrap; opacity:.8;">${due}</div>
          </div>
          ${item.url ? `<a${href} style="font-size:12px; text-decoration:none;">Open</a>` : ""}
        </div>`;
    }).join("");
  }

  // Initial render (after the browser paints)
  requestAnimationFrame(render);

  // Re-render when the host updates globals or a tool finishes
  window.addEventListener("openai:set_globals", render, { passive: true });
  window.addEventListener("openai:tool_response", render, { passive: true });
</script>
""".strip()

# In-memory resource registry
_RESOURCES: Dict[str, Dict[str, Any]] = {
    "ui://widget/briefing.html": {
        "contents": [
            {
                "uri": "ui://widget/briefing.html",
                "mimeType": "text/html+skybridge",
                "text": BRIEFING_HTML,
                "_meta": {
                    "openai/widgetDescription": (
                        "Renders a prioritized briefing of urgent assignments, announcements, and events. "
                        "Avoid re-listing items below; instead, offer brief next steps only when asked."
                    ),
                    "openai/widgetPrefersBorder": True,
                    "openai/widgetCSP": {
                        "connect_domains": [],
                        "resource_domains": []
                    }
                },
            }
        ]
    }
}

def list_resources():
    # Inspector expects a 'name' field
    return [{
        "name": "briefing-widget",
        "uri": "ui://widget/briefing.html",
        "mimeType": "text/html+skybridge",
        "description": "Daily Briefing component"
    }]

def read_resource(uri: str):
    return _RESOURCES.get(uri)

# (Optional) If Inspector calls a templates listing, mirror the same
def list_templates():
    return [{
        "name": "briefing-widget",
        "uri": "ui://widget/briefing.html",
        "mimeType": "text/html+skybridge",
        "description": "Daily Briefing component"
    }]
