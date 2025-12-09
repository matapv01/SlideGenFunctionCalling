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

// Initialize immediately or wait for DOM
const initEditor = () => {
console.log('🎬 Initializing editor...');
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

// Check if we have project_id from URL to load from database
console.log('🚀 init.js loaded, checking URL parameters...');
const urlParams = new URLSearchParams(window.location.search);
const projectId = urlParams.get('id');
const projectName = urlParams.get('project');
const source = urlParams.get('source');

console.log('📋 URL params:', { projectId, projectName, source });

if (projectId) {
    console.log('🎯 Found project_id in URL:', projectId);
    // Wait a bit for editor to be fully initialized
    setTimeout(() => {
        console.log('📥 Starting to load project from database...');
        loadProjectFromDatabase(projectId);
    }, 800);
} else if (projectName && source === 'generated') {
    console.log('🎯 Found generated project in URL:', projectName, source);
    // This is from streaming workflow, load from API
    setTimeout(() => {
        console.log('📞 Calling loadGeneratedSlidesIfAvailable...');
        loadGeneratedSlidesIfAvailable();
    }, 500);
} else {
    console.log('ℹ️ No project info in URL, checking sessionStorage...');
    // Check if we have generated slides to load from sessionStorage
    setTimeout(() => {
        console.log('📞 Calling loadGeneratedSlidesIfAvailable (no URL params)...');
        loadGeneratedSlidesIfAvailable();
    }, 500);
}
};

// Run immediately if DOM ready, otherwise wait
if (document.readyState === 'loading') {
    console.log('⏳ DOM still loading, adding event listener...');
    document.addEventListener('DOMContentLoaded', initEditor);
} else {
    console.log('✅ DOM already loaded, initializing now...');
    initEditor();
}

        // Function to load project from database
        async function loadProjectFromDatabase(projectId) {
            console.log('🔄 Loading project from database, ID:', projectId);
            const token = localStorage.getItem('access_token');
            if (!token) {
                console.error('❌ No access token found');
                alert('Please login first');
                window.location.href = 'login.html';
                return;
            }

            try {
                // Use config.BACKEND_URL for consistent API calls
                const apiUrl = window.config?.BACKEND_URL || 'http://localhost:3000';
                
                console.log('📡 Fetching slides from:', `${apiUrl}/api/projects/${projectId}/slides`);
                const response = await fetch(`${apiUrl}/api/projects/${projectId}/slides`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                console.log('📥 Response status:', response.status, response.statusText);
                if (!response.ok) {
                    throw new Error(`Failed to load project: ${response.status} ${response.statusText}`);
                }

                const data = await response.json();
                const slides = data.slides || [];
                
                console.log(`Loaded ${slides.length} slides from database`);
                
                // Database has converted HTML - extract ONLY absolute positioned elements (not wrappers)
                const editorSlides = slides.map((slide, index) => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(slide.html_content, 'text/html');
                    
                    // Get all styles from head (exclude script tags)
                    const headStyles = Array.from(doc.head.querySelectorAll('style, link[rel="stylesheet"]'))
                        .map(el => el.outerHTML)
                        .join('\n');
                    
                    // Extract background color - priority order:
                    // 1. Body inline style
                    // 2. .content-wrapper inline style
                    // 3. .slide-container CSS
                    // 4. body CSS
                    // 5. Default white
                    let bgColor = 'white';
                    
                    if (doc.body?.style?.backgroundColor && doc.body.style.backgroundColor !== 'transparent') {
                        bgColor = doc.body.style.backgroundColor;
                    } else {
                        const contentWrapper = doc.querySelector('.content-wrapper');
                        if (contentWrapper?.style?.backgroundColor && contentWrapper.style.backgroundColor !== 'transparent') {
                            bgColor = contentWrapper.style.backgroundColor;
                        } else {
                            // Try to extract from CSS
                            const styleText = Array.from(doc.querySelectorAll('style')).map(s => s.textContent).join(' ');
                            
                            // Check .slide-container first (common in converted slides)
                            const containerMatch = styleText.match(/\.slide-container[^{]*\{[^}]*background(?:-color)?\s*:\s*([^;]+)/i);
                            if (containerMatch && containerMatch[1].trim() !== 'transparent') {
                                bgColor = containerMatch[1].trim();
                            } else {
                                // Fallback to body CSS
                                const bodyMatch = styleText.match(/body[^{]*\{[^}]*background(?:-color)?\s*:\s*([^;]+)/i);
                                if (bodyMatch && bodyMatch[1].trim() !== 'transparent') {
                                    bgColor = bodyMatch[1].trim();
                                }
                            }
                        }
                    }
                    
                    // Extract ONLY children inside content-wrapper (the absolute positioned elements)
                    const contentWrapper = doc.querySelector('.content-wrapper');
                    const elementsHTML = contentWrapper ? contentWrapper.innerHTML : '';
                    
                    // Remove script tags from elementsHTML
                    const cleanHTML = elementsHTML.replace(/<script[^>]*>.*?<\/script>/gs, '');
                    
                    console.log(`📄 Slide ${index + 1}: bg=${bgColor}, ${headStyles.length} chars styles, ${cleanHTML.length} chars elements`);
                    
                    return {
                        id: `slide_${index + 1}`,
                        name: slide.title || `Slide ${index + 1}`,
                        content: headStyles + cleanHTML, // Styles + absolute positioned elements only
                        backgroundColor: bgColor,
                        zIndexCounter: 200
                    };
                });

                // Load slides into editor
                if (editorSlides.length > 0 && window.slideEditor) {
                    console.log(`📚 Loading ${editorSlides.length} slides into editor`);
                    window.slideEditor.slides = editorSlides;
                    window.slideEditor.currentSlideIndex = 0;
                    window.slideEditor.currentProjectId = projectId; // Set project ID for auto-save
                    
                    // Store slide IDs for save
                    window.slideEditor.slideIds = slides.map(slide => slide.id);
                    console.log('💾 Stored slide IDs:', window.slideEditor.slideIds);
                    
                    // IMPORTANT: Reset history when loading from database
                    // This prevents undo from going back to the default welcome slide
                    window.slideEditor.history = [];
                    window.slideEditor.historyIndex = -1;
                    
                    window.slideEditor.renderSlidesList();
                    if (editorSlides.length > 0) {
                        window.slideEditor.loadSlide(0);
                    }
                    
                    // Save initial state AFTER loading from database
                    window.slideEditor.saveState();
                    
                    showNotification(`Loaded ${editorSlides.length} slides successfully`, 'success');
                }
            } catch (error) {
                console.error('Error loading project:', error);
                showNotification('Failed to load project: ' + error.message, 'error');
            }
        }

        // Function to load slides generated from DOCX
