# Widget Setup Guide

## Overview

Your Schoology Co-Pilot widget has been simplified to use the **CDN pattern** instead of inline HTML. This approach is more reliable and easier to debug.

## How It Works

1. **Widget HTML Shell**: The widget serves a simple HTML shell that loads your React app from `localhost:8080`
2. **Asset Server**: A separate Python script serves your built React assets
3. **MCP Integration**: ChatGPT loads the widget and fetches data from your MCP server

## Setup Instructions

### Step 1: Build Your React Widget

```bash
cd web/briefing-widget
npm run build
```

### Step 2: Start the Widget Asset Server

In a separate terminal:

```bash
# From the project root
python serve_widget.py
```

This will serve your built React app on `http://localhost:8080`

### Step 3: Start Your MCP Server

In another terminal:

```bash
# From the project root
python main.py
```

### Step 4: Test the Widget

Your widget should now be accessible through ChatGPT. The widget will:
- Load the HTML shell from your MCP server
- Fetch React assets from `localhost:8080`
- Display your interactive briefing widget

## File Changes Made

### `app/mcp_server/resources.py`
- ✅ Simplified to use CDN pattern
- ✅ Removed complex inline HTML generation
- ✅ Uses simple HTML shell that loads from localhost:8080

### `app/mcp_server/tools.py`
- ✅ Updated to use proper widget metadata
- ✅ Added embedded resource support
- ✅ Simplified tool response format

### `app/mcp_server/server.py`
- ✅ Removed SSE endpoints (not needed)
- ✅ Simplified JSON-RPC handling
- ✅ Cleaner, more maintainable code

## Troubleshooting

### Widget Not Loading?
1. Make sure `serve_widget.py` is running on port 8080
2. Check that `web/briefing-widget/dist` exists
3. Verify your React build completed successfully

### CORS Issues?
The widget server includes CORS headers for ChatGPT compatibility.

### Port Conflicts?
If port 8080 is in use, you can modify the port in both:
- `serve_widget.py` (line with `PORT = 8080`)
- `app/mcp_server/resources.py` (the localhost URLs)

## Benefits of This Approach

1. **Reliability**: No more complex file reading and inlining
2. **Debugging**: Easy to inspect network requests in browser dev tools
3. **Development**: Hot reload works with your React dev server
4. **Maintainability**: Cleaner separation of concerns

## Next Steps

1. Test the widget through ChatGPT
2. Verify data loading and display works correctly
3. Customize the React widget as needed
4. Deploy both servers when ready for production

