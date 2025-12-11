"""
Audio Streamer - A LAN audio streaming solution.

This package provides modular components for streaming Windows system audio
over WebSocket to browser clients.
"""

from .config import ServerConfig, load_config, validate_config
from .audio_capture import AudioCapture
from .connection_manager import ConnectionManager, ClientInfo
from .ws_server import AudioWebSocketServer
from .http_server import create_app

__all__ = [
    'ServerConfig',
    'load_config',
    'validate_config',
    'AudioCapture',
    'ConnectionManager',
    'ClientInfo',
    'AudioWebSocketServer',
    'create_app',
]
