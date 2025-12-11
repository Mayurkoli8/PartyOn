/**
 * Connection Handler - Manages WebSocket connection with reconnection logic.
 * 
 * @module connection
 */

/**
 * Connection status enum.
 */
export const ConnectionStatus = {
    DISCONNECTED: 'disconnected',
    CONNECTING: 'connecting',
    CONNECTED: 'connected',
    RECONNECTING: 'reconnecting',
    FAILED: 'failed'
};

/**
 * Manages WebSocket connection with automatic reconnection.
 */
export class ConnectionHandler {
    /**
     * Create a connection handler.
     * @param {Object} options - Configuration options.
     * @param {string} options.wsUrl - WebSocket URL.
     * @param {Function} options.onData - Callback for received data.
     * @param {Function} options.onStatusChange - Callback for status changes.
     */
    constructor(options) {
        this.wsUrl = options.wsUrl;
        this.onData = options.onData || (() => {});
        this.onStatusChange = options.onStatusChange || (() => {});
        
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.baseDelay = 1000;
        this.maxDelay = 30000;
        this.reconnectTimer = null;
        this.status = ConnectionStatus.DISCONNECTED;
    }
    
    /**
     * Calculate reconnection delay with exponential backoff.
     * @param {number} attempt - Current attempt number (0-indexed).
     * @returns {number} Delay in milliseconds.
     */
    getReconnectDelay(attempt) {
        return Math.min(this.baseDelay * Math.pow(2, attempt), this.maxDelay);
    }
    
    /**
     * Establish WebSocket connection.
     */
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return;
        }
        
        this._setStatus(ConnectionStatus.CONNECTING);
        
        try {
            this.ws = new WebSocket(this.wsUrl);
            this.ws.binaryType = 'arraybuffer';
            
            this.ws.onopen = () => {
                this.reconnectAttempts = 0;
                this._setStatus(ConnectionStatus.CONNECTED);
            };
            
            this.ws.onmessage = (event) => {
                this.onData(event.data);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            this.ws.onclose = (event) => {
                if (this.status !== ConnectionStatus.DISCONNECTED) {
                    this.scheduleReconnect();
                }
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.scheduleReconnect();
        }
    }
    
    /**
     * Clean disconnect from server.
     */
    disconnect() {
        this._setStatus(ConnectionStatus.DISCONNECTED);
        
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        if (this.ws) {
            this.ws.close(1000, 'User disconnect');
            this.ws = null;
        }
        
        this.reconnectAttempts = 0;
    }
    
    /**
     * Schedule reconnection with exponential backoff.
     */
    scheduleReconnect() {
        if (this.status === ConnectionStatus.DISCONNECTED) {
            return;
        }
        
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            this._setStatus(ConnectionStatus.FAILED);
            return;
        }
        
        this._setStatus(ConnectionStatus.RECONNECTING);
        
        const delay = this.getReconnectDelay(this.reconnectAttempts);
        this.reconnectAttempts++;
        
        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, delay);
    }
    
    /**
     * Update status and notify callback.
     * @param {string} status - New status.
     * @private
     */
    _setStatus(status) {
        this.status = status;
        this.onStatusChange(status, {
            attempts: this.reconnectAttempts,
            maxAttempts: this.maxReconnectAttempts
        });
    }
    
    /**
     * Get current connection status.
     * @returns {string} Current status.
     */
    getStatus() {
        return this.status;
    }
}
