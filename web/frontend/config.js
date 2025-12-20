/**
 * Frontend Configuration
 * Centralized configuration for API endpoints and settings
 */

// Detect if running in development or production
// Determine environment and backend URL
function getBackendURL() {
    const currentOrigin = window.location.origin;
    const currentHost = window.location.hostname;

    console.log('🔍 Detecting environment:', {
        origin: currentOrigin,
        hostname: currentHost,
        port: window.location.port
    });

    // If accessing via production domain (not localhost)
    if (currentHost !== 'localhost' && currentHost !== '127.0.0.1') {
        // Use current origin (same domain:port) for production
        const backendURL = currentOrigin;
        console.log('🌐 Production mode - Using same origin:', backendURL);
        return backendURL;
    }

    // Development mode - use localhost with specific port
    const backendURL = 'http://localhost:12008';
    console.log('🛠️ Development mode - Using localhost:', backendURL);
    return backendURL;
}

const BACKEND_URL = getBackendURL();

const config = {
    /**
     * Backend API URL
     * Auto-detected based on current environment:
     * - Production: Uses same origin as frontend
     * - Development: Uses http://localhost:12008
     */
    BACKEND_URL: BACKEND_URL,
    API_BASE_URL: BACKEND_URL,

    /**
     * API Endpoints
     */
    endpoints: {
        captureSlide: `${BACKEND_URL}/api/capture-slide`,
        captureSlidesBatch: `${BACKEND_URL}/api/capture-slides-batch`,
        exportSlidesPdf: `${BACKEND_URL}/api/export-slides-pdf`
    },

    /**
     * Frontend mode indicator
     */
    MODE: window.location.hostname === 'localhost' ? 'development' : 'production'
};

// Log configuration on load
console.log('✅ SlideGen Config loaded:', config);
console.log(`🛠️ Frontend running in ${config.MODE} mode.`);

// Make available as global for non-module scripts
window.config = config;
window.API_CONFIG = config; // Legacy compatibility
