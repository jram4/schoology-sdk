# app/mcp_server/server.py

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
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

# CORS is still important for development and communication with ChatGPT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        # The .model_dump() method handles serialization correctly
        return result.model_dump(mode="json", by_alias=True)
    return result

@app.post("/mcp")
async def mcp_endpoint(request: Request, db: Session = Depends(get_db)):
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
            uri = params.get("uri") or (params.get("params", {})).get("uri")
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