# app/mcp_server/server.py

from fastapi import FastAPI, Depends, Request, HTTPException, Header
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.mcp_server.tools import list_tools as _list_tools, call_tool as _call_tool
from typing import Dict, Any
import os

app = FastAPI(title="Schoology Co-Pilot MCP")

@app.get("/healthz")
def healthz():
    return {"ok": True}

# --- JSON-RPC Helper Functions ---

def create_success_response(request_id: str | int, result: Dict[str, Any]) -> Dict[str, Any]:
    """Wraps a successful result in the JSON-RPC 2.0 envelope."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result
    }

def create_error_response(request_id: str | int | None, code: int, message: str) -> Dict[str, Any]:
    """Wraps an error in the JSON-RPC 2.0 envelope."""
    # Use -1 as ID if the original request ID is unknown (e.g., parse error)
    return {
        "jsonrpc": "2.0",
        "id": request_id if request_id is not None else -1,
        "error": {
            "code": code,
            "message": message
        }
    }

# --- MCP Endpoint (Modified) ---

@app.post("/mcp")
async def mcp(
    request: Request,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    # OPTIONAL: simple bearer auth if MCP_TOKEN is set (safe when port-forwarding)
    expected = os.getenv("MCP_TOKEN")
    if expected:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Missing bearer token")
        token = authorization.split(" ", 1)[1]
        if token != expected:
            raise HTTPException(status_code=403, detail="Invalid token")
    try:
        body = await request.json()
    except Exception:
        # JSON Parse Error (-32700)
        return create_error_response(None, -32700, "Invalid JSON received")

    # Extract required JSON-RPC fields (id, method)
    jsonrpc_version = body.get("jsonrpc")
    request_id = body.get("id")
    method = body.get("method")

    # Validate basic JSON-RPC structure
    if jsonrpc_version != "2.0" or request_id is None or method is None:
        # Invalid Request (-32600)
        return create_error_response(request_id or None, -32600, "Invalid Request structure. Must contain jsonrpc:'2.0', id, and method.")

    try:
        # --- MCP initialize handshake ---
        if method == "initialize":
            # Minimal viable MCP response
            return create_success_response(request_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "tools": {"listChanged": True},
                    "sampling": {},
                    "elicitation": {}
                },
                "serverInfo": {"name": "schoology-copilot", "version": "0.1.0"}
            })

        # --- Tool listing (both our legacy name and MCP name) ---
        if method in ("list_tools", "tools/list"):
            tools = _list_tools()
            # The result for list_tools is an object containing the 'tools' key
            return create_success_response(request_id, {"tools": tools})

        # --- Tool calling (both our legacy name and MCP name) ---
        if method in ("call_tool", "tools/call"):
            params = body.get("params", {})
            name = params.get("name")
            # Support both MCP `arguments` and our earlier `args`
            args = params.get("arguments") or params.get("args") or {}
            
            if not name:
                # Invalid Params (-32602)
                return create_error_response(request_id, -32602, "Tool name is required in params.")

            result = _call_tool(name, args, db)
            
            # The result from _call_tool already contains structuredContent, content, and _meta.
            # We place this raw result directly into the JSON-RPC 'result' envelope.
            return create_success_response(request_id, result)
        
        # Method Not Found (-32601)
        return create_error_response(request_id, -32601, f"Unsupported method: {method}")

    except Exception as e:
        # Internal Server Error (-32603)
        import traceback
        traceback.print_exc() # Log the error on the server side
        return create_error_response(request_id, -32603, f"Internal error during MCP execution: {type(e).__name__}")