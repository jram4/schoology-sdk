#!/bin/bash
# Test script for MCP methods using curl

echo "Testing MCP methods with curl..."

echo -e "\n=== Testing initialize ==="
curl -s -X POST http://127.0.0.1:5544/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"1"}}}' | jq .

echo -e "\n=== Testing tools/list ==="
curl -s -X POST http://127.0.0.1:5544/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | jq .

echo -e "\n=== Testing tools/call (briefing.get) ==="
curl -s -X POST http://127.0.0.1:5544/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"briefing.get","arguments":{"range":"48h"}}}' | jq .

echo -e "\n=== Testing legacy list_tools ==="
curl -s -X POST http://127.0.0.1:5544/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":4,"method":"list_tools"}' | jq .

echo -e "\n=== Testing legacy call_tool ==="
curl -s -X POST http://127.0.0.1:5544/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":5,"method":"call_tool","params":{"name":"briefing.get","args":{"range":"48h"}}}' | jq .
