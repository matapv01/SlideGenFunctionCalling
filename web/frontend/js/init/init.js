// Application Initialization
import { SlideEditor } from '../core/SlideEditor.js';
import { loadGeneratedSlidesIfAvailable, convertApiSlideToEditorFormat, convertHtmlToEditorElements, showNotification, toggleSlideView, openSlideInNewTab } from '../utils/utils.js';

// Make functions globally accessible
window.loadGeneratedSlidesIfAvailable = loadGeneratedSlidesIfAvailable;
window.convertApiSlideToEditorFormat = convertApiSlideToEditorFormat;
window.convertHtmlToEditorElements = convertHtmlToEditorElements;
window.showNotification = showNotification;
window.toggleSlideView = toggleSlideView;
window.openSlideInNewTab = openSlideInNewTab;

document.addEventListener('DOMContentLoaded', () => {
window.slideEditor = new SlideEditor();

// Global debug functions for console testing
window.testCapture = () => {
    return window.slideEditor.testCapture();
};

window.getSlideHTML = () => {
    return window.slideEditor.slideCapture.getCurrentSlideHTML();
};

window.logSlideData = () => {
    return window.slideEditor.debugLogSlideData();
};

console.log('🚀 SlideEditor loaded! Available debug functions:');
console.log('  - debugSlide() - Get current slide HTML');
console.log('  - testCapture() - Test capture process');
console.log('  - getSlideHTML() - Get raw HTML');
console.log('  - logSlideData() - Log slide data');

// Check if we have generated slides to load
setTimeout(() => {
    loadGeneratedSlidesIfAvailable();
}, 500);
        });

        // Function to load slides generated from DOCX
