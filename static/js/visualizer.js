/**
 * Audio Visualizer - Renders real-time audio visualization.
 * 
 * @module visualizer
 */

/**
 * Renders audio visualization on a canvas element.
 */
export class AudioVisualizer {
    /**
     * Create a visualizer.
     * @param {HTMLCanvasElement} canvasElement - Canvas to render on.
     * @param {Object} options - Configuration options.
     * @param {number} options.barCount - Number of frequency bars (default: 32).
     * @param {string} options.barColor - Bar color (default: gradient).
     */
    constructor(canvasElement, options = {}) {
        this.canvas = canvasElement;
        this.ctx = canvasElement.getContext('2d');
        this.barCount = options.barCount || 32;
        this.barColor = options.barColor || null;
        
        // Check for reduced motion preference
        this.prefersReducedMotion = window.matchMedia(
            '(prefers-reduced-motion: reduce)'
        ).matches;
        
        // Listen for preference changes
        window.matchMedia('(prefers-reduced-motion: reduce)')
            .addEventListener('change', (e) => {
                this.prefersReducedMotion = e.matches;
            });
    }
    
    /**
     * Update visualization with frequency data.
     * @param {Uint8Array} frequencyData - Frequency data from analyser.
     */
    update(frequencyData) {
        if (!frequencyData || !this.ctx) return;
        
        if (this.prefersReducedMotion) {
            // Calculate average level for simple meter
            const sum = frequencyData.reduce((a, b) => a + b, 0);
            const average = sum / frequencyData.length;
            this.renderSimpleMeter(average / 255);
            return;
        }
        
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, width, height);
        
        // Calculate bar dimensions
        const barWidth = (width / this.barCount) * 0.8;
        const gap = (width / this.barCount) * 0.2;
        
        // Sample frequency data
        const step = Math.floor(frequencyData.length / this.barCount);
        
        for (let i = 0; i < this.barCount; i++) {
            const value = frequencyData[i * step] / 255;
            const barHeight = value * height;
            const x = i * (barWidth + gap);
            const y = height - barHeight;
            
            // Create gradient for bar
            if (!this.barColor) {
                const gradient = this.ctx.createLinearGradient(x, height, x, y);
                gradient.addColorStop(0, 'rgba(0, 230, 118, 0.8)');
                gradient.addColorStop(1, 'rgba(0, 200, 83, 0.4)');
                this.ctx.fillStyle = gradient;
            } else {
                this.ctx.fillStyle = this.barColor;
            }
            
            // Draw rounded bar
            this.ctx.beginPath();
            this.ctx.roundRect(x, y, barWidth, barHeight, 3);
            this.ctx.fill();
        }
    }
    
    /**
     * Render simplified level meter for reduced motion preference.
     * @param {number} level - Audio level from 0.0 to 1.0.
     */
    renderSimpleMeter(level) {
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, width, height);
        
        // Draw background bar
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.fillRect(0, height / 2 - 10, width, 20);
        
        // Draw level indicator
        const levelWidth = level * width;
        const gradient = this.ctx.createLinearGradient(0, 0, levelWidth, 0);
        gradient.addColorStop(0, 'rgba(0, 230, 118, 0.8)');
        gradient.addColorStop(1, 'rgba(0, 200, 83, 0.6)');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, height / 2 - 10, levelWidth, 20);
    }
    
    /**
     * Clear visualization to idle state.
     */
    clear() {
        if (!this.ctx) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}
