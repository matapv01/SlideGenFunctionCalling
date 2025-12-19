/**
 * Frontend Configuration
 * Centralized configuration for API endpoints and settings
 */

// Detect if running in development or production
// const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'|| window.location.hostname === '0.0.0.0';
const isDevelopment = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1') || window.location.origin.includes('0.0.0.0');
console.log(`🛠️ Frontend running in ${isDevelopment ? 'development' : 'production'} mode.`);

// Backend API URL
const API_BASE_URL = isDevelopment 
    ? 'http://localhost:12008/api'  // Development: backend on port 12008
    : window.location.origin;                       // Production: same origin

// Backend download URL
const BACKEND_URL = isDevelopment
    ? 'http://localhost:12008'       // Development
    : window.location.origin;                           // Production: same origin

const config = {
    // API endpoints
    API_BASE_URL,
    BACKEND_URL,
    
    // Specific endpoints
    endpoints: {
        captureSlide: `${API_BASE_URL}/capture-slide`,
        captureSlidesBatch: `${API_BASE_URL}/capture-slides-batch`,
        exportSlidePdf: `${API_BASE_URL}/export-slide-pdf`,
        exportSlidesPdf: `${API_BASE_URL}/export-slides-pdf`,
        downloadCapture: (filename) => `${BACKEND_URL}/api/download-capture/${filename}`,
    },
    
    // Other settings
    settings: {
        isDevelopment,
        defaultTimeout: 120080, // 30 seconds
    }
};

// Log configuration in development
if (isDevelopment) {
    console.log('🔧 Frontend Config:', config);
}

// Export for ES6 modules
export { config };

// Also make available as global for non-module scripts
window.config = config;
