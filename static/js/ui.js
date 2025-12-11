/**
 * UI Controller - Manages UI state and user interactions.
 * 
 * @module ui
 */

import { ConnectionHandler, ConnectionStatus } from './connection.js';
import { AudioEngine } from './audio.js';
import { AudioVisualizer } from './visualizer.js';
import { StatsCollector } from './stats.js';

/**
 * Main UI controller integrating all components.
 */
export class UIController {
    /**
     * Create a UI controller.
     * @param {Object} elements - DOM element references.
     */
    constructor(elements) {
        this.elements = elements;
        this.connectionHandler = null;
        this.audioEngine = null;
        this.visualizer = null;
        this.statsCollector = null;
        this.isPlaying = false;
    }
    
    /**
     * Initialize all components and event listeners.
     * @param {Object} config - Configuration from server.
     */
    initialize(config) {
        const wsUrl = `ws://${config.host || location.hostname}:${config.ws_port || 8765}`;
        
        // Initialize stats collector
        this.statsCollector = new StatsCollector();
        
        // Initialize audio engine
        this.audioEngine = new AudioEngine({
            sampleRate: config.sample_rate || 44100,
            channels: config.channels || 2
        });
        
        // Initialize visualizer if canvas exists
        if (this.elements.visualizer) {
            this.visualizer = new AudioVisualizer(this.elements.visualizer);
        }
        
        // Initialize connection handler
        this.connectionHandler = new ConnectionHandler({
            wsUrl: wsUrl,
            onData: (data) => this._handleAudioData(data),
            onStatusChange: (status, details) => this._handleStatusChange(status, details)
        });
        
        // Set up event listeners
        this._setupEventListeners();
        
        // Start visualization loop
        this._startVisualizationLoop();
    }
    
    /**
     * Update status display.
     * @param {string} status - Status text.
     * @param {string} details - Additional details (optional).
     */
    updateStatus(status, details = '') {
        if (this.elements.status) {
            this.elements.status.textContent = status;
        }
        if (this.elements.statusDetails && details) {
            this.elements.statusDetails.textContent = details;
        }
    }
    
    /**
     * Update statistics display.
     * @param {Object} stats - Statistics object.
     */
    updateStats(stats) {
        if (this.elements.packetsPerSecond) {
            this.elements.packetsPerSecond.textContent = stats.packetsPerSecond;
        }
        if (this.elements.latency) {
            this.elements.latency.textContent = `${stats.latencyMs}ms`;
        }
        if (this.elements.quality) {
            this.elements.quality.textContent = stats.quality;
            this.elements.quality.className = `quality-${stats.quality}`;
        }
    }
    
    /**
     * Display error message with suggestions.
     * @param {string} message - Error message.
     * @param {string[]} suggestions - Suggested actions.
     */
    showError(message, suggestions = []) {
        this.updateStatus(message);
        
        if (this.elements.errorContainer) {
            this.elements.errorContainer.innerHTML = '';
            
            if (suggestions.length > 0) {
                const list = document.createElement('ul');
                suggestions.forEach(s => {
                    const li = document.createElement('li');
                    li.textContent = s;
                    list.appendChild(li);
                });
                this.elements.errorContainer.appendChild(list);
            }
        }
    }
    
    /**
     * Set up event listeners for controls.
     * @private
     */
    _setupEventListeners() {
        // Play button
        if (this.elements.playBtn) {
            this.elements.playBtn.addEventListener('click', () => this._handlePlay());
        }
        
        // Pause button
        if (this.elements.pauseBtn) {
            this.elements.pauseBtn.addEventListener('click', () => this._handlePause());
        }
        
        // Stop button
        if (this.elements.stopBtn) {
            this.elements.stopBtn.addEventListener('click', () => this._handleStop());
        }
        
        // Mute button
        if (this.elements.muteBtn) {
            this.elements.muteBtn.addEventListener('click', () => this._handleMute());
        }
        
        // Volume slider
        if (this.elements.volumeSlider) {
            this.elements.volumeSlider.addEventListener('input', (e) => {
                const volume = parseInt(e.target.value, 10) / 100;
                this.audioEngine?.setVolume(volume);
            });
        }
        
        // Stats hover
        if (this.elements.statsArea) {
            this.elements.statsArea.addEventListener('mouseenter', () => {
                if (this.elements.statsDetails) {
                    this.elements.statsDetails.style.display = 'block';
                }
            });
            this.elements.statsArea.addEventListener('mouseleave', () => {
                if (this.elements.statsDetails) {
                    this.elements.statsDetails.style.display = 'none';
                }
            });
        }
    }
    
    /**
     * Handle play button click.
     * @private
     */
    _handlePlay() {
        if (this.isPlaying) {
            this.audioEngine?.resume();
            return;
        }
        
        if (!this.audioEngine?.initialize()) {
            this.showError('Audio not supported', [
                'Try using Chrome or Firefox',
                'Check browser audio permissions'
            ]);
            return;
        }
        
        this.connectionHandler?.connect();
        this.isPlaying = true;
    }
    
    /**
     * Handle pause button click.
     * @private
     */
    _handlePause() {
        this.audioEngine?.pause();
        this.updateStatus('Paused');
    }
    
    /**
     * Handle stop button click.
     * @private
     */
    _handleStop() {
        this.connectionHandler?.disconnect();
        this.audioEngine?.stop();
        this.statsCollector?.reset();
        this.visualizer?.clear();
        this.isPlaying = false;
        this.updateStatus('Idle');
    }
    
    /**
     * Handle mute button click.
     * @private
     */
    _handleMute() {
        if (!this.audioEngine) return;
        
        const isMuted = !this.audioEngine.isMuted;
        this.audioEngine.setMuted(isMuted);
        
        if (this.elements.muteBtn) {
            this.elements.muteBtn.textContent = isMuted ? 'Unmute' : 'Mute';
        }
    }
    
    /**
     * Handle incoming audio data.
     * @param {ArrayBuffer} data - Raw audio data.
     * @private
     */
    _handleAudioData(data) {
        this.statsCollector?.recordPacket();
        this.audioEngine?.processAudioData(data);
    }
    
    /**
     * Handle connection status changes.
     * @param {string} status - New status.
     * @param {Object} details - Status details.
     * @private
     */
    _handleStatusChange(status, details) {
        switch (status) {
            case ConnectionStatus.CONNECTED:
                this.updateStatus('Streaming…');
                break;
            case ConnectionStatus.CONNECTING:
                this.updateStatus('Connecting…');
                break;
            case ConnectionStatus.RECONNECTING:
                this.updateStatus(`Reconnecting… (${details.attempts}/${details.maxAttempts})`);
                break;
            case ConnectionStatus.DISCONNECTED:
                this.updateStatus('Disconnected');
                break;
            case ConnectionStatus.FAILED:
                this.showError('Connection failed', [
                    'Check that the server is running',
                    'Verify network connectivity',
                    'Click Play to try again'
                ]);
                break;
        }
    }
    
    /**
     * Start visualization update loop.
     * @private
     */
    _startVisualizationLoop() {
        const update = () => {
            if (this.visualizer && this.audioEngine?.isInitialized) {
                const data = this.audioEngine.getVisualizationData();
                if (data) {
                    this.visualizer.update(data);
                }
            }
            
            // Update stats display periodically
            if (this.statsCollector && this.isPlaying) {
                this.updateStats(this.statsCollector.getStats());
            }
            
            requestAnimationFrame(update);
        };
        update();
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    // Fetch config from server
    let config = { ws_port: 8765, sample_rate: 44100, channels: 2 };
    
    try {
        const response = await fetch('/config');
        if (response.ok) {
            config = await response.json();
        }
    } catch (e) {
        console.warn('Could not fetch config, using defaults');
    }
    
    // Get DOM elements
    const elements = {
        playBtn: document.getElementById('playBtn'),
        pauseBtn: document.getElementById('pauseBtn'),
        stopBtn: document.getElementById('stopBtn'),
        muteBtn: document.getElementById('muteBtn'),
        volumeSlider: document.getElementById('volumeSlider'),
        status: document.getElementById('st'),
        statusDetails: document.getElementById('statusDetails'),
        visualizer: document.getElementById('visualizer'),
        statsArea: document.getElementById('statsArea'),
        statsDetails: document.getElementById('statsDetails'),
        packetsPerSecond: document.getElementById('pps'),
        latency: document.getElementById('latency'),
        quality: document.getElementById('quality'),
        errorContainer: document.getElementById('errorContainer')
    };
    
    // Initialize UI controller
    const ui = new UIController(elements);
    ui.initialize(config);
});
