#!/bin/bash

# macOS/Linux auto-restart script for LAN Audio Server

while true; do
    echo "Starting LAN Audio Server..."
    # Try python3 first, fallback to python if python3 doesn't exist
    if command -v python3 &> /dev/null; then
        python3 server.py
    else
        python server.py
    fi
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "Server stopped normally."
        break
    else
        echo "Server crashed. Restarting in 3 seconds..."
        sleep 3
    fi
done

