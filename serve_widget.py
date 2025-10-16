#!/usr/bin/env python3
"""
Simple static file server for the widget assets.
Run this script to serve your built React widget on localhost:8080
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def main():
    # Check if dist folder exists
    dist_path = Path("web/briefing-widget/dist")
    if not dist_path.exists():
        print("❌ Error: dist folder not found at web/briefing-widget/dist")
        print("Please run: cd web/briefing-widget && npm run build")
        sys.exit(1)
    
    # Change to dist directory
    os.chdir(dist_path)
    
    PORT = 8080
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(dist_path), **kwargs)
        
        def end_headers(self):
            # Add CORS headers for ChatGPT
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 Widget server running at http://localhost:{PORT}")
        print(f"📁 Serving files from: {dist_path.absolute()}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Widget server stopped")

if __name__ == "__main__":
    main()

