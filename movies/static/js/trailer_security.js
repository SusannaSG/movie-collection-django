/**
 * Secure YouTube Trailer Embedding System
 * Handles lazy loading, XSS prevention, and performance optimization
 */

class SecureTrailerManager {
    constructor(options = {}) {
        this.options = {
            lazyLoadThreshold: options.lazyLoadThreshold || '50px',
            loadTimeout: options.loadTimeout || 3000,
            allowedDomains: ['youtube.com', 'youtube-nocookie.com'],
            ...options
        };

        this.observer = null;
        this.loadedTrailers = new Set();
        this.failedTrailers = new Set();
    }

    init() {
        this._setupIntersectionObserver();
        this._validateExistingIframes();
        this._setupErrorHandling();
        this._monitorPerformance();
    }

    _setupIntersectionObserver() {
        const options = {
            rootMargin: this.options.lazyLoadThreshold,
            threshold: 0.01
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this._loadTrailer(entry.target);
                    this.observer.unobserve(entry.target);
                }
            });
        }, options);

        document.querySelectorAll('[data-trailer-container]').forEach(container => {
            this.observer.observe(container);
        });
    }

    _loadTrailer(container) {
        const videoId = container.dataset.videoId;
        const contentDiv = container.querySelector('[data-trailer-content]');

        if (!contentDiv) return;

        const loadingDiv = container.querySelector('[data-trailer-loading]');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }

        contentDiv.style.display = 'block';
        this.loadedTrailers.add(videoId);
    }

    _validateExistingIframes() {
        const iframes = document.querySelectorAll('iframe[data-trailer-iframe]');

        iframes.forEach(iframe => {
            if (!this._isValidIframeSrc(iframe.src)) {
                console.error('🔒 Security Alert: Blocked potentially malicious iframe');
                iframe.style.display = 'none';

                const container = iframe.closest('[data-trailer-container]');
                if (container) {
                    this._showErrorMessage(container, 'Iframe validation failed');
                    this.failedTrailers.add(container.dataset.videoId);
                }
            }
        });
    }

    _isValidIframeSrc(src) {
        if (!src) return false;

        if (!src.startsWith('https://')) {
            return false;
        }

        const isAllowedDomain = this.options.allowedDomains.some(domain =>
            src.includes(domain)
        );

        if (!isAllowedDomain) {
            return false;
        }

        const videoIdMatch = src.match(/[/=]([a-zA-Z0-9_-]{11})/);
        if (!videoIdMatch) {
            return false;
        }

        return true;
    }

    _setupErrorHandling() {
        document.addEventListener('error', (event) => {
            if (event.target.tagName === 'IFRAME' && event.target.dataset.trailerIframe) {
                const container = event.target.closest('[data-trailer-container]');
                if (container) {
                    this.failedTrailers.add(container.dataset.videoId);
                    this._showErrorMessage(container, 'Failed to load trailer');
                }
            }
        }, true);

        const trailerContainers = document.querySelectorAll('[data-trailer-container]');
        trailerContainers.forEach(container => {
            const timeout = setTimeout(() => {
                if (!this.loadedTrailers.has(container.dataset.videoId)) {
                    const loadingDiv = container.querySelector('[data-trailer-loading]');
                    if (loadingDiv && loadingDiv.style.display !== 'none') {
                        this._showErrorMessage(container, 'Trailer loading timed out');
                    }
                }
            }, this.options.loadTimeout);

            container.dataset.loadTimeout = timeout;
        });
    }

    _showErrorMessage(container, message) {
        const loadingDiv = container.querySelector('[data-trailer-loading]');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }

        const contentDiv = container.querySelector('[data-trailer-content]');
        if (contentDiv) {
            contentDiv.style.display = 'none';
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'trailer-error-fallback';
        errorDiv.style.cssText = `
            background: #fee;
            color: #c33;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #c33;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-family: system-ui, -apple-system, sans-serif;
        `;
        errorDiv.innerHTML = `
            <div>
                <p style="font-weight: bold; margin-bottom: 10px;">⚠️ Trailer Unavailable</p>
                <p>${this._escapeHtml(message)}</p>
                <p style="margin-top: 10px; font-size: 0.9em; opacity: 0.8;">
                    The trailer could not be loaded. It may have been removed or made unavailable.
                </p>
            </div>
        `;

        container.appendChild(errorDiv);
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    _monitorPerformance() {
        if (!window.PerformanceObserver) return;

        try {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.name.includes('youtube')) {
                        console.log('🎬 Trailer Resource Timing:', {
                            name: entry.name,
                            duration: entry.duration.toFixed(2) + 'ms',
                            size: entry.transferSize ? entry.transferSize + ' bytes' : 'cached'
                        });
                    }
                }
            });

            observer.observe({ entryTypes: ['resource'] });
        } catch (e) {
            console.warn('Performance monitoring unavailable');
        }
    }

    getStats() {
        return {
            loaded: this.loadedTrailers.size,
            failed: this.failedTrailers.size,
            failedIds: Array.from(this.failedTrailers)
        };
    }

    loadTrailerById(videoId) {
        const container = document.querySelector(`[data-video-id="${this._escapeHtml(videoId)}"]`);
        if (container) {
            this._loadTrailer(container);
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const trailerManager = new SecureTrailerManager({
        lazyLoadThreshold: '100px',
        loadTimeout: 5000
    });

    trailerManager.init();
    window.trailerManager = trailerManager;
});