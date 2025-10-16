#!/bin/bash

echo "🚀 Starting Schoology Co-Pilot"
echo ""

# Build the widget
echo "📦 Building widget..."
cd web/briefing-widget
npm run build
cd ../..

# Start the widget server in background
echo "🌐 Starting widget server on :8080..."
python3 web/briefing-widget/serve.py &
WIDGET_PID=$!

# Wait for server to start
sleep 2

echo ""
echo "✅ Widget server running on http://localhost:8080"
echo ""
echo "📝 In another terminal, run:"
echo "   ngrok start --all"
echo ""
echo "Then get your widget URL from ngrok dashboard and update .env:"
echo "   WIDGET_BASE_URL=\"https://your-widget-tunnel.ngrok-free.app\""
echo ""
echo "Finally, start the MCP server in a third terminal:"
echo "   python main.py"
echo ""
echo "Press Ctrl+C to stop widget server"

# Wait for interrupt
trap "kill $WIDGET_PID; exit" INT
wait