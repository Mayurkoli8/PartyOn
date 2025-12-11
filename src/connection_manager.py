"""
Connection manager for the Audio Streamer server.

Tracks connected clients and handles lifecycle events.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional

import websockets


@dataclass
class ClientInfo:
    """Information about a connected client."""
    
    websocket: websockets.WebSocketServerProtocol
    connected_at: datetime
    last_activity: datetime
    address: str
    packets_sent: int = 0


class ConnectionManager:
    """Tracks connected clients and handles lifecycle events."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize the connection manager.
        
        Args:
            logger: Logger instance for this module.
        """
        self.clients: Dict[str, ClientInfo] = {}
        self.logger = logger
        self.total_served: int = 0
    
    def add_client(self, websocket: websockets.WebSocketServerProtocol) -> str:
        """
        Register new client.
        
        Args:
            websocket: The WebSocket connection.
            
        Returns:
            Client ID string.
        """
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        now = datetime.now()
        
        self.clients[client_id] = ClientInfo(
            websocket=websocket,
            connected_at=now,
            last_activity=now,
            address=client_id
        )
        self.total_served += 1
        
        self.logger.info(f"Client connected: {client_id}")
        return client_id
    
    def remove_client(self, client_id: str) -> None:
        """
        Remove client from active set.
        
        Args:
            client_id: The client ID to remove.
        """
        if client_id in self.clients:
            del self.clients[client_id]
            self.logger.info(f"Client disconnected: {client_id}")
    
    def get_active_clients(self) -> List[ClientInfo]:
        """
        Return list of active clients.
        
        Returns:
            List of ClientInfo objects.
        """
        return list(self.clients.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Return connection statistics.
        
        Returns:
            Dictionary with connection stats.
        """
        return {
            "connected": len(self.clients),
            "total_served": self.total_served,
            "clients": [
                {
                    "address": c.address,
                    "connected_at": c.connected_at.isoformat(),
                    "packets_sent": c.packets_sent
                }
                for c in self.clients.values()
            ]
        }
    
    async def broadcast(self, data: bytes) -> None:
        """
        Send data to all connected clients, removing failed ones.
        
        Args:
            data: Raw audio bytes to broadcast.
        """
        failed_clients = []
        
        for client_id, client_info in self.clients.items():
            try:
                await client_info.websocket.send(data)
                client_info.packets_sent += 1
                client_info.last_activity = datetime.now()
            except Exception as e:
                self.logger.debug(f"Failed to send to {client_id}: {e}")
                failed_clients.append(client_id)
        
        # Remove failed clients
        for client_id in failed_clients:
            self.remove_client(client_id)
    
    async def close_all(self, reason: str = "Server shutting down") -> None:
        """
        Close all client connections gracefully.
        
        Args:
            reason: Reason message to send to clients.
        """
        self.logger.info(f"Closing all connections: {reason}")
        
        for client_id, client_info in list(self.clients.items()):
            try:
                await client_info.websocket.close(1001, reason)
            except Exception as e:
                self.logger.debug(f"Error closing {client_id}: {e}")
        
        self.clients.clear()
