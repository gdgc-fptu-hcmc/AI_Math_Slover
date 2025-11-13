#!/usr/bin/env python3
"""
Math Animation AI - Backend Server Runner
"""

import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Import and run the app
import uvicorn
from app.main import app

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    print("=" * 60)
    print("🎓 Math Animation AI - Backend Server")
    print("=" * 60)
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔗 URL:  http://localhost:{port}")
    print(f"📖 Docs: http://localhost:{port}/docs")
    print("=" * 60)
    print()

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
    )
