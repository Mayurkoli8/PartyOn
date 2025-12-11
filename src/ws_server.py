"""
WebSocket server module for the Audio Streamer.

Handles WebSocket connections and audio broadcasting.
"""

import asyncio
import logging
from typing import Optional

import websockets

from .config import ServerConfig
from .audio_capture import AudioCapture
from .connection_manager import ConnectionManager


class AudioWebSocketServer:
    """Handles WebSocket connections and audio broadcasting."""
    
    def __init__(
        self,
        config: ServerConfig,
        audio_capture: AudioCapture,
        connection_manager: ConnectionManager,
        logger: logging.Logger
    ):
        """
        Initialize the WebSocket server.
        
        Args:
            config: Server configuration.
            audio_capture: Audio capture module.
            connection_manager: Connection manager.
            logger: Logger instance.
        """
        self.config = config
        self.audio_capture = audio_capture
        self.connection_manager = connection_manager
        self.logger = logger
        self.server: Optional[websockets.WebSocketServer] = None
        self.is_running: bool = False
        self._broadcast_task: Optional[asyncio.Task] = None
    
    async def handler(self, websocket: websockets.WebSocketServerProtocol) -> None:
        """
        Handle individual WebSocket connection.
        
        Args:
            websocket: The WebSocket connection.
        """
        client_id = self.connection_manager.add_client(websocket)
        
        try:
            # Keep connection open until client disconnects
            await asyncio.Future()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.debug(f"Client handler error for {client_id}: {e}")
        finally:
            self.connection_manager.remove_client(client_id)
    
    async def broadcast_loop(self) -> None:
        """Main loop for capturing and broadcasting audio."""
        self.logger.info("Starting audio broadcast loop")
        
        while self.is_running:
            data = self.audio_capture.read_block()
            
            if data:
                await self.connection_manager.broadcast(data)
            
            # Let event loop breathe
            await asyncio.sleep(0)
    
    async def start(self, host: str = "0.0.0.0") -> None:
        """
        Start the WebSocket server.
        
        Args:
            host: Host address to bind to.
        """
        self.is_running = True
        
        self.server = await websockets.serve(
            self.handler,
            host,
            self.config.ws_port,
            max_size=None
        )
        
        self.logger.info(f"WebSocket server started on ws://{host}:{self.config.ws_port}")
        
        # Start broadcast loop
        self._broadcast_task = asyncio.create_task(self.broadcast_loop())
    
    async def stop(self) -> None:
        """Stop the server gracefully."""
        self.logger.info("Stopping WebSocket server")
        self.is_running = False
        
        # Cancel broadcast task
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass
        
        # Close all client connections
        await self.connection_manager.close_all()
        
        # Close server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        self.logger.info("WebSocket server stopped")
