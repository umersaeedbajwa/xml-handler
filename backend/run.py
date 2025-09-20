#!/usr/bin/env python3
"""
Startup script for the Queue Manager application.
Allows easy configuration of host and port.
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment variables or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    
    print(f"Starting Queue Manager on {host}:{port}")
    print(f"Reload mode: {reload}")
    print(f"API docs available at: http://{host}:{port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload
    )
