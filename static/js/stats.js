/**
 * Stats Collector - Tracks connection quality metrics.
 * 
 * @module stats
 */

/**
 * Collects and calculates connection statistics.
 */
export class StatsCollector {
    constructor() {
        this.packetsReceived = 0;
        this.lastPacketTime = 0;
        this.latencyEstimate = 0;
        this.packetsPerSecond = 0;
        this.bufferUnderruns = 0;
        
        // Track recent packet timestamps for PPS calculation
        this._recentTimestamps = [];
        this._windowMs = 1000; // 1 second window
    }
    
    /**
     * Record a received packet.
     * @param {number} timestamp - Packet timestamp (optional, uses Date.now() if not provided).
     */
    recordPacket(timestamp = Date.now()) {
        this.packetsReceived++;
        this.lastPacketTime = timestamp;
        
        // Add to recent timestamps
        this._recentTimestamps.push(timestamp);
        
        // Remove timestamps outside the window
        const cutoff = timestamp - this._windowMs;
        while (this._recentTimestamps.length > 0 && this._recentTimestamps[0] < cutoff) {
            this._recentTimestamps.shift();
        }
        
        // Calculate packets per second
        this.packetsPerSecond = this._recentTimestamps.length;
    }
    
    /**
     * Record a buffer underrun event.
     */
    recordUnderrun() {
        this.bufferUnderruns++;
    }
    
    /**
     * Get current statistics.
     * @returns {Object} Statistics object.
     */
    getStats() {
        return {
            packetsReceived: this.packetsReceived,
            packetsPerSecond: this.packetsPerSecond,
            latencyMs: this.latencyEstimate,
            bufferUnderruns: this.bufferUnderruns,
            quality: this._calculateQuality()
        };
    }
    
    /**
     * Reset all counters.
     */
    reset() {
        this.packetsReceived = 0;
        this.lastPacketTime = 0;
        this.latencyEstimate = 0;
        this.packetsPerSecond = 0;
        this.bufferUnderruns = 0;
        this._recentTimestamps = [];
    }
    
    /**
     * Calculate connection quality based on metrics.
     * @returns {string} Quality rating: 'good', 'degraded', or 'poor'.
     * @private
     */
    _calculateQuality() {
        // Quality based on recent underruns and packet rate
        if (this.bufferUnderruns > 10 || this.packetsPerSecond < 20) {
            return 'poor';
        }
        if (this.bufferUnderruns > 3 || this.packetsPerSecond < 35) {
            return 'degraded';
        }
        return 'good';
    }
}
