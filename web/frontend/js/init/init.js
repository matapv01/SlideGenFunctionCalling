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
    // Always load from database if we have project ID (even if source=generated)
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
                
                // First fetch project info
                console.log('📡 Fetching project info from:', `${apiUrl}/api/projects/${projectId}`);
                const projectResponse = await fetch(`${apiUrl}/api/projects/${projectId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (!projectResponse.ok) {
                    throw new Error(`Failed to load project info: ${projectResponse.status}`);
                }
                
                const projectData = await projectResponse.json();
                const project = projectData.project || projectData; // Handle both formats
                console.log('📋 Project info:', project);
                
                // Then fetch slides
                console.log('📡 Fetching slides from:', `${apiUrl}/api/projects/${projectId}/slides`);
                const response = await fetch(`${apiUrl}/api/projects/${projectId}/slides`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                console.log('📥 Response status:', response.status, response.statusText);
                if (!response.ok) {
                    throw new Error(`Failed to load slides: ${response.status} ${response.statusText}`);
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
                    window.slideEditor.currentProjectTitle = project.title; // Store project title
                    
                    // Store slide IDs for save
                    window.slideEditor.slideIds = slides.map(slide => slide.id);
                    console.log('💾 Stored slide IDs:', window.slideEditor.slideIds);
                    console.log('📌 Project title:', project.title);
                    
                    // Update project name display
                    updateProjectNameDisplay(project.title);
                    
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

        // Project name editing functionality
        function updateProjectNameDisplay(name) {
            const projectNameText = document.getElementById('projectNameText');
            if (projectNameText) {
                projectNameText.textContent = name || 'Untitled Project';
                console.log('📝 Updated project name display to:', name);
            } else {
                console.warn('⚠️ projectNameText element not found, retrying...');
                // Retry after a short delay if element not ready
                setTimeout(() => {
                    const elem = document.getElementById('projectNameText');
                    if (elem) {
                        elem.textContent = name || 'Untitled Project';
                        console.log('📝 Updated project name display to:', name);
                    }
                }, 100);
            }
        }

        function initProjectNameEditor() {
            const projectNameDisplay = document.getElementById('projectNameDisplay');
            const projectNameText = document.getElementById('projectNameText');
            
            if (!projectNameDisplay || !projectNameText) return;

            // Double-click to edit
            projectNameDisplay.addEventListener('dblclick', () => {
                const currentName = projectNameText.textContent;
                
                // Create input
                const input = document.createElement('input');
                input.type = 'text';
                input.id = 'projectNameInput';
                input.value = currentName;
                input.style.width = Math.max(150, currentName.length * 10) + 'px';
                
                // Replace text with input
                projectNameDisplay.classList.add('editing');
                projectNameText.replaceWith(input);
                input.focus();
                input.select();
                
                // Save on blur or enter
                const saveProjectName = async () => {
                    const newName = input.value.trim() || currentName;
                    
                    // Replace input with text
                    const newText = document.createElement('span');
                    newText.id = 'projectNameText';
                    newText.textContent = newName;
                    input.replaceWith(newText);
                    projectNameDisplay.classList.remove('editing');
                    
                    // Save to database - create project if not exists
                    if (newName !== currentName) {
                        const apiUrl = window.config?.BACKEND_URL || 'http://localhost:3000';
                        const token = localStorage.getItem('access_token');
                        
                        if (!token) {
                            showNotification('⚠️ Please login to save project', 'warning');
                            return;
                        }
                        
                        try {
                            // If no project ID, create new project first
                            if (!window.slideEditor?.currentProjectId) {
                                console.log('📝 Creating new project in database...');
                                const createResponse = await fetch(`${apiUrl}/api/projects`, {
                                    method: 'POST',
                                    headers: {
                                        'Authorization': `Bearer ${token}`,
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({
                                        title: newName,
                                        description: '',
                                        source_type: 'manual'
                                    })
                                });
                                
                                if (createResponse.ok) {
                                    const data = await createResponse.json();
                                    window.slideEditor.currentProjectId = data.id;
                                    window.slideEditor.currentProjectTitle = newName;
                                    
                                    // Create all existing slides in database
                                    for (let i = 0; i < window.slideEditor.slides.length; i++) {
                                        const slide = window.slideEditor.slides[i];
                                        const htmlContent = `
                                            <div class="slide-container">
                                                <div class="content-wrapper" style="background: ${slide.backgroundColor};">
                                                    ${slide.content}
                                                </div>
                                            </div>
                                        `;
                                        
                                        const slideResponse = await fetch(`${apiUrl}/api/projects/${data.id}/slides`, {
                                            method: 'POST',
                                            headers: {
                                                'Authorization': `Bearer ${token}`,
                                                'Content-Type': 'application/json'
                                            },
                                            body: JSON.stringify({
                                                slide_index: i,
                                                slide_type: 'content',
                                                title: slide.name,
                                                html_content: htmlContent
                                            })
                                        });
                                        
                                        if (slideResponse.ok) {
                                            const slideData = await slideResponse.json();
                                            window.slideEditor.slideIds.push(slideData.id);
                                        }
                                    }
                                    
                                    showNotification('✓ Project created and saved', 'success');
                                    console.log('✅ Project created with ID:', data.id);
                                    
                                    // Update URL with project ID
                                    const newUrl = new URL(window.location);
                                    newUrl.searchParams.set('id', data.id);
                                    window.history.replaceState({}, '', newUrl);
                                } else {
                                    showNotification('✗ Failed to create project', 'error');
                                }
                            } else {
                                // Update existing project
                                const response = await fetch(`${apiUrl}/api/projects/${window.slideEditor.currentProjectId}`, {
                                    method: 'PUT',
                                    headers: {
                                        'Authorization': `Bearer ${token}`,
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ title: newName })
                                });
                                
                                if (response.ok) {
                                    window.slideEditor.currentProjectTitle = newName;
                                    showNotification('✓ Project name updated', 'success');
                                    console.log('✅ Project name updated:', newName);
                                } else {
                                    showNotification('✗ Failed to update project name', 'error');
                                }
                            }
                        } catch (error) {
                            console.error('Error saving project:', error);
                            showNotification('✗ Error saving project', 'error');
                        }
                    }
                };
                
                input.addEventListener('blur', saveProjectName);
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        input.blur();
                    } else if (e.key === 'Escape') {
                        input.value = currentName;
                        input.blur();
                    }
                });
            });
        }

        // Initialize project name editor
        initProjectNameEditor();

        // Function to load slides generated from DOCX
