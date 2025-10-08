#!/usr/bin/env python3
"""
Test script for MCP methods
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5544/mcp"

def test_mcp_method(method, params=None):
    """Test an MCP method"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method
    }
    if params:
        payload["params"] = params
    
    try:
        response = requests.post(BASE_URL, json=payload, headers={"Content-Type": "application/json"})
        print(f"\n=== Testing {method} ===")
        print(f"Request: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error testing {method}: {e}")
        return None

if __name__ == "__main__":
    print("Testing MCP methods...")
    
    # Test initialize
    test_mcp_method("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0"}
    })
    
    # Test tools/list
    test_mcp_method("tools/list")
    
    # Test tools/call
    test_mcp_method("tools/call", {
        "name": "briefing.get",
        "arguments": {"range": "48h"}
    })
    
    # Test legacy methods for backward compatibility
    test_mcp_method("list_tools")
    test_mcp_method("call_tool", {
        "name": "briefing.get",
        "args": {"range": "48h"}
    })
