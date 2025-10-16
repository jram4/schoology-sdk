#!/bin/bash

set -e  # Exit on any error

echo "🚀 Building and Starting Schoology Co-Pilot"
echo ""

# Build the widget
echo "📦 Building React widget..."
cd web/briefing-widget
npm run build
cd ../..

echo "✅ Widget built successfully"
echo ""
echo "🌐 Starting MCP server (serves widget at /widget)..."
echo ""
python main.py