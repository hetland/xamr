#!/usr/bin/env python3
"""
Simple script to serve the built documentation locally.
Run: python serve_docs.py
Then open: http://localhost:8000
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Change to the build directory
docs_dir = Path(__file__).parent
build_dir = docs_dir / "_build" / "html"

if not build_dir.exists():
    print("Documentation not built yet. Please run 'make html' first.")
    exit(1)

os.chdir(build_dir)

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving documentation at http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    
    # Try to open the browser automatically
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except:
        pass
    
    httpd.serve_forever()
