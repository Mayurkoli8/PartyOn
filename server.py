"""
Audio Streamer Server - Main entry point.

Streams Windows system audio over LAN to browser clients via WebSocket.
"""

import asyncio
import logging
import signal
import sys
from threading import Thread
from typing import Optional

from src.config import load_config, ServerConfig
from src.audio_capture import AudioCapture
from src.connection_manager import ConnectionManager
from src.ws_server import AudioWebSocketServer
from src.http_server import create_app, get_local_ip


def setup_logger(log_level: str) -> logging.Logger:
    """
    Set up the application logger.
    
    Args:
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR).
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("audio_streamer")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


class AudioStreamerServer:
    """Main server class orchestrating all components."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the audio streamer server.
        
        Args:
            config_path: Path to configuration file.
        """
        self.config = load_config(config_path)
        self.logger = setup_logger(self.config.log_level)
        
        self.audio_capture = AudioCapture(self.config, self.logger)
        self.connection_manager = ConnectionManager(self.logger)
        self.ws_server: Optional[AudioWebSocketServer] = None
        self.is_shutting_down = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def setup_signal_handlers(self) -> None:
        """Register handlers for SIGINT/SIGTERM."""
        if sys.platform != 'win32':
            self._loop.add_signal_handler(signal.SIGINT, self._signal_handler)
            self._loop.add_signal_handler(signal.SIGTERM, self._signal_handler)
        else:
            signal.signal(signal.SIGINT, lambda s, f: self._signal_handler())
            signal.signal(signal.SIGTERM, lambda s, f: self._signal_handler())
    
    def _signal_handler(self) -> None:
        """Handle shutdown signals."""
        if not self.is_shutting_down:
            self.logger.info("Shutdown signal received")
            asyncio.create_task(self.shutdown())
    
    async def shutdown(self) -> None:
        """Graceful shutdown sequence."""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        self.logger.info("Initiating graceful shutdown")
        
        # Stop WebSocket server
        if self.ws_server:
            await self.ws_server.stop()
        
        # Stop audio capture
        self.audio_capture.stop()
        
        self.logger.info("Shutdown complete")
        sys.exit(0)
    
    def _start_http_server(self) -> None:
        """Start the HTTP server in a separate thread."""
        host = get_local_ip()
        app = create_app(
            self.connection_manager,
            self.config,
            self.audio_capture.get_device_info()
        )
        self.logger.info(f"HTTP server: http://{host}:{self.config.http_port}")
        app.run(host="0.0.0.0", port=self.config.http_port, threaded=True)
    
    async def _run_async(self) -> None:
        """Run the async components."""
        self._loop = asyncio.get_event_loop()
        self.setup_signal_handlers()
        
        # Initialize audio capture
        if not self.audio_capture.initialize():
            self.logger.error("Failed to initialize audio capture")
            sys.exit(1)
        
        # Create and start WebSocket server
        self.ws_server = AudioWebSocketServer(
            self.config,
            self.audio_capture,
            self.connection_manager,
            self.logger
        )
        
        host = get_local_ip()
        self.logger.info(f"WebSocket server: ws://{host}:{self.config.ws_port}")
        
        await self.ws_server.start()
        
        # Keep running until shutdown
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass
    
    def run(self) -> None:
        """Start all server components."""
        self.logger.info("Starting Audio Streamer Server")
        
        # Start HTTP server in background thread
        http_thread = Thread(target=self._start_http_server, daemon=True)
        http_thread.start()
        
        # Run async components
        asyncio.run(self._run_async())


if __name__ == "__main__":
    server = AudioStreamerServer()
    server.run()
