from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import mcp.types as types
import logging

from app.database.database import get_db, init_db
from app.scheduler.scheduler import start_scheduler, stop_scheduler
from app.mcp_server import tools, resources

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up...")
    load_dotenv()
    init_db()
    start_scheduler()
    yield
    print("👋 Shutting down...")
    stop_scheduler()

app = FastAPI(title="Schoology Co-Pilot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

widget_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'web', 'briefing-widget', 'dist'))
if os.path.exists(widget_dist_path):
    app.mount("/widget", StaticFiles(directory=widget_dist_path, html=True), name="widget")
    logging.info(f"✅ Widget assets mounted at /widget from {widget_dist_path}")
else:
    logging.error(f"❌ Widget 'dist' folder not found at {widget_dist_path}")
    logging.error("   Please run: cd web/briefing-widget && npm run build")

@app.get("/healthz")
def health():
    return {"ok": True}

def json_rpc_response(request_id, result=None, error=None):
    """Helper to build JSON-RPC 2.0 responses."""
    resp = {"jsonrpc": "2.0", "id": request_id}
    if error:
        resp["error"] = error
    else:
        resp["result"] = result
    return resp

def serialize_mcp_result(result):
    """Convert MCP types to JSON-serializable dicts."""
    if isinstance(result, types.CallToolResult):
        return {
            "content": [
                {"type": c.type, "text": c.text}
                for c in result.content
            ],
            "structuredContent": result.structuredContent,
            "isError": result.isError,
            "_meta": result.meta
        }
    return result

@app.get("/mcp")
async def mcp_get_handler():
    """
    Handles GET requests to the MCP endpoint, typically from health checks.
    Returns a simple 200 OK response.
    """
    return {
        "status": "ok",
        "message": "MCP server is running. Use POST for JSON-RPC requests."
    }

@app.post("/mcp")
async def mcp_endpoint(request: Request, db: Session = Depends(get_db)):
    """
    Handles POST requests to the MCP endpoint for the main JSON-RPC protocol.
    """
    try:
        body = await request.json()
    except:
        return json_rpc_response(None, error={"code": -32700, "message": "Parse error"})

    method = body.get("method")
    req_id = body.get("id", -1)
    params = body.get("params", {})

    try:
        if method == "initialize":
            return json_rpc_response(req_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": "schoology-copilot", "version": "0.1.0"}
            })
        
        elif method in ("tools/list", "list_tools"):
            tool_dicts = tools.list_tools()
            return json_rpc_response(req_id, {"tools": tool_dicts})
        
        elif method in ("tools/call", "call_tool"):
            name = params.get("name")
            args = params.get("arguments") or params.get("args", {})
            
            result_object = tools.call_tool(name, args, db)
            serialized = serialize_mcp_result(result_object)
            return json_rpc_response(req_id, serialized)
        
        elif method in ("resources/list", "list_resources"):
            return json_rpc_response(req_id, {"resources": resources.list_resources()})
        
        elif method in ("resources/read", "read_resource"):
            uri = params.get("uri")
            if not uri:
                return json_rpc_response(req_id, error={"code": -32602, "message": "Missing uri parameter"})
            result = resources.read_resource(uri)
            if result:
                return json_rpc_response(req_id, result)
            return json_rpc_response(req_id, error={"code": 1, "message": "Not found"})
        
        else:
            return json_rpc_response(req_id, error={"code": -32601, "message": f"Method not found: {method}"})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return json_rpc_response(req_id, error={"code": -32603, "message": str(e)})