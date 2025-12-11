"""
HTTP server module for the Audio Streamer.

Serves the client UI and status endpoints.
"""

import os
import socket
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, send_from_directory, jsonify

from .config import ServerConfig
from .connection_manager import ConnectionManager


# Server start time for uptime calculation
_start_time: Optional[datetime] = None

# Get the project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def get_local_ip() -> str:
    """
    Get the local IP address of this machine.
    
    Returns:
        Local IP address string.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def create_app(
    connection_manager: ConnectionManager,
    config: ServerConfig,
    audio_device_info: Optional[dict] = None
) -> Flask:
    """
    Create Flask app with routes.
    
    Args:
        connection_manager: Connection manager instance.
        config: Server configuration.
        audio_device_info: Optional audio device information.
        
    Returns:
        Configured Flask application.
    """
    global _start_time
    _start_time = datetime.now()
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """Serve the client HTML page."""
        return send_from_directory(PROJECT_ROOT, 'client.html')
    
    @app.route('/static/js/<path:filename>')
    def serve_js(filename):
        """Serve JavaScript files."""
        return send_from_directory(PROJECT_ROOT / 'static' / 'js', filename)
    
    @app.route('/status')
    def status():
        """Return JSON with server health metrics."""
        uptime = (datetime.now() - _start_time).total_seconds() if _start_time else 0
        client_stats = connection_manager.get_stats()
        
        return jsonify({
            "status": "running",
            "uptime_seconds": int(uptime),
            "clients": {
                "connected": client_stats["connected"],
                "total_served": client_stats["total_served"]
            },
            "audio": audio_device_info or {
                "device": "Unknown",
                "sample_rate": config.sample_rate,
                "channels": config.channels
            },
            "server": {
                "http_port": config.http_port,
                "ws_port": config.ws_port
            }
        })
    
    @app.route('/config')
    def get_config():
        """Return client-relevant configuration."""
        return jsonify({
            "ws_port": config.ws_port,
            "sample_rate": config.sample_rate,
            "channels": config.channels,
            "host": get_local_ip()
        })
    
    return app
