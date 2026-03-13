// Helper Functions

// Function to load slides generated from DOCX or streaming workflow
export async function loadGeneratedSlidesIfAvailable() {
// Check URL parameters for project name
const urlParams = new URLSearchParams(window.location.search);
const projectName = urlParams.get('project');
const source = urlParams.get('source');

// If we have project name from URL, load from API (converted HTML from database)
if (projectName && source === 'generated') {
    console.log('📥 Loading converted slides from database API for project:', projectName);
    try {
        const response = await fetch(`${window.config?.BACKEND_URL || 'http://localhost:3000'}/api/projects/by-name/${projectName}/slides`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();
        const slides = data.slides;
        
        console.log(`✅ Loaded ${slides.length} converted slides from API`);
        
        // Parse converted HTML - extract ONLY absolute positioned elements (not wrappers)
        const editorSlides = slides.map((slide, index) => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(slide.content, 'text/html');
            
            // Get all styles from head (exclude script tags)
            const headStyles = Array.from(doc.head.querySelectorAll('style, link[rel="stylesheet"]'))
                .map(el => el.outerHTML)
                .join('\n');
            
            // Extract background color from body inline style or CSS
            let bgColor = 'white';
            if (doc.body?.style?.backgroundColor) {
                bgColor = doc.body.style.backgroundColor;
            } else {
                // Try to extract from style tags
                const styleText = Array.from(doc.querySelectorAll('style')).map(s => s.textContent).join(' ');
                const bgMatch = styleText.match(/body[^{]*\{[^}]*background(?:-color)?\s*:\s*([^;]+)/i);
                if (bgMatch && bgMatch[1].trim() !== 'transparent') {
                    bgColor = bgMatch[1].trim();
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

        if (!window.slideEditor) {
            console.error('❌ slideEditor not initialized!');
            showNotification('Editor not ready', 'error');
            return;
        }

        window.slideEditor.slides = editorSlides;
        window.slideEditor.currentSlideIndex = 0;

        window.slideEditor.renderSlidesList();
        if (editorSlides.length > 0) {
            window.slideEditor.loadSlide(0);
        }

        showNotification(`Successfully loaded ${editorSlides.length} slides!`, 'success');
        
        // Clear sessionStorage after successful API load
        sessionStorage.removeItem('streamingState');
        return;
    } catch (error) {
        console.error('❌ Error loading slides from API:', error);
        console.log('⚠️ Falling back to sessionStorage...');
    }
}

// Try sessionStorage first (from streaming workflow)
let storedData = sessionStorage.getItem('streamingState');
let apiSlides = null;

if (storedData) {
    try {
        const state = JSON.parse(storedData);
        apiSlides = state.slides;
        console.log('📥 Loading slides from sessionStorage (streaming):', apiSlides?.length, 'slides');
        // Clear after loading
        sessionStorage.removeItem('streamingState');
    } catch (e) {
        console.error('Error parsing streamingState:', e);
    }
}

// Fallback to localStorage (legacy)
if (!apiSlides) {
    storedData = localStorage.getItem('generatedSlides');
    if (storedData) {
        try {
            apiSlides = JSON.parse(storedData);
            console.log('📥 Loading slides from localStorage (legacy):', apiSlides?.length, 'slides');
            localStorage.removeItem('generatedSlides');
        } catch (e) {
            console.error('Error parsing generatedSlides:', e);
        }
    }
}

if (!apiSlides || apiSlides.length === 0) {
    console.log('ℹ️ No slides found in storage');
    return;
}

try {
    const editorSlides = apiSlides.map((slide, index) => convertApiSlideToEditorFormat(slide, index));
    
    if (!window.slideEditor) {
        console.error('❌ slideEditor not initialized!');
        showNotification('Editor not ready', 'error');
        return;
    }

    window.slideEditor.slides = editorSlides;
    window.slideEditor.currentSlideIndex = 0;

    window.slideEditor.renderSlidesList();
    if (editorSlides.length > 0) {
        window.slideEditor.loadSlide(0);
    }

    showNotification(`Successfully loaded ${editorSlides.length} generated slides!`, 'success');

} catch (error) {
    console.error('Error loading generated slides:', error);
    showNotification('Error loading generated slides', 'error');
}
        }

        // Function to convert API slide format to editor format
export function convertApiSlideToEditorFormat(apiSlide, index) {
const slideId = `slide_${index + 1}`;
const slideName = apiSlide.title || `Slide ${index + 1}`;

console.log('Converting slide:', apiSlide); // Debug

// Render HTML content as actual slide (not source code)
let editorContent = '';

if (apiSlide.content && apiSlide.content.trim()) {
    console.log('Rendering HTML content as editable elements for', index + 1);

    // Prepare complete HTML document
    let completeHtml = apiSlide.content;
    if (!completeHtml.trim().startsWith('<!DOCTYPE')) {
        completeHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    ${completeHtml}
</head>
<body>
</body>
</html>`;
    }

    // Parse HTML and convert to editor elements
    const parser = new DOMParser();
    const doc = parser.parseFromString(completeHtml, 'text/html');
    const container = doc.body || doc.documentElement;

    // Preserve inline <style> from head (converted HTML already has proper styles)
    const headStyles = Array.from(doc.head ? doc.head.querySelectorAll('style') : [])
        .map(s => `<style>${s.textContent || ''}</style>`)
        .join('');

    // Convert to draggable editor elements
    const elementsHtml = convertHtmlToEditorElements(container, index) || '';
    console.log(`Slide ${index + 1}: Converted ${elementsHtml ? 'success' : 'EMPTY'}, length: ${elementsHtml.length}`);

    // No need for background element - converted HTML already has it
    editorContent = `${headStyles}${elementsHtml}`;
} else {
    console.log('Creating text-based slide for slide', index + 1);

    // Create editable text content from title or create new slide
    const slideText = apiSlide.title || `Slide ${index + 1}`;
    editorContent = `
        <div class="element" style="position: absolute; left: 100px; top: 100px; width: 600px; height: 80px; font-size: 32px; font-weight: bold; color: #333; text-align: center; z-index: 1; cursor: move; padding: 20px; border: 2px dashed #ddd; background: #f9f9f9;" data-type="heading" contenteditable="true">
            ${slideText}
        </div>
        <div class="element" style="position: absolute; left: 100px; top: 220px; width: 600px; height: 200px; font-size: 16px; color: #666; line-height: 1.6; z-index: 2; cursor: move; padding: 20px; border: 2px dashed #ddd; background: #f9f9f9;" data-type="text" contenteditable="true">
            Click here to add content...
        </div>
    `;
}

const result = {
    id: slideId,
    name: slideName,
    content: editorContent,
    backgroundColor: apiSlide.backgroundColor || 'white',
    zIndexCounter: 10,
    originalData: apiSlide // Keep original data for reference
};

console.log(`✅ Slide ${index + 1} converted:`, {
    id: result.id,
    contentLength: result.content?.length || 0,
    hasContent: !!result.content
});

return result;
        }

        // Function to convert HTML to editor elements
export function convertHtmlToEditorElements(htmlContainer, slideIndex) {
console.log('Converting HTML elements for slide', slideIndex + 1, htmlContainer);

let elements = '';
let yOffset = 100;
let zIndex = 1;

// New: handle converted absolute-position HTML (from converter.js)
try {
    const absWrapper = htmlContainer.querySelector('.content-wrapper');
    if (absWrapper) {
        const children = Array.from(absWrapper.children).filter(n => n.tagName && !['SCRIPT', 'STYLE', 'META', 'LINK', 'TITLE'].includes(n.tagName));
        const extract = (styleStr, key) => {
            const m = styleStr.match(new RegExp(key + '\\s*:\\s*([^;]+)'));
            return m ? m[1].trim() : '';
        };
        children.forEach((node, idx) => {
            const rawStyle = node.getAttribute('style') || '';
            const left = extract(rawStyle, 'left') || '0px';
            const top = extract(rawStyle, 'top') || '0px';
            const width = extract(rawStyle, 'width') || (node.getAttribute('width') ? node.getAttribute('width') + 'px' : '200px');
            const height = extract(rawStyle, 'height') || (node.getAttribute('height') ? node.getAttribute('height') + 'px' : '50px');
            const zi = extract(rawStyle, 'z-index') || (100 + idx);

            // preserve key visual props; strip absolute box props
            const keepProps = [
                'color', 'background', 'background-color', 'background-image', 'background-size', 'background-position', 'background-repeat', 'background-clip', 'background-attachment',
                'font-family', 'font-size', 'font-weight', 'font-style', 'line-height', 'letter-spacing', 'word-spacing', 'text-align', 'text-transform', 'text-decoration', 'text-shadow', 'white-space',
                'border', 'border-top', 'border-right', 'border-bottom', 'border-left', 'border-radius', 'box-shadow', 'filter', 'opacity',
                'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left', 'margin', 'outline', 'clip-path',
                'transform', 'transform-origin', 'writing-mode'
            ];
            const pick = (styleStr, prop) => {
                const m = styleStr.match(new RegExp(prop + '\\s*:\\s*([^;]+)'));
                return m ? `${prop}: ${m[1].trim()}; ` : '';
            };
            let innerStyle = '';
            keepProps.forEach(p => innerStyle += pick(rawStyle, p));

            // clone node html with cleaned style
            const cloned = node.cloneNode(true);
            if (innerStyle) cloned.setAttribute('style', innerStyle); else cloned.removeAttribute('style');
            // normalize image srcs
            if (cloned.querySelectorAll) {
                cloned.querySelectorAll('img').forEach(img => {
                    const src = img.getAttribute('src') || '';
                    if (src && !/^https?:\/\//i.test(src) && !/^\//.test(src) && !/^data:/i.test(src)) {
                        img.setAttribute('src', `/api/images/${src}`);
                    }
                });
            }
            const inner = cloned.outerHTML;

            elements += `
                <div class="element" data-type="content" style="position: absolute; left: ${left}; top: ${top}; width: ${width}; height: ${height}; z-index: ${zi};">
                    ${inner}
                </div>
            `;
        });

        // If we handled absolute HTML, return early
        if (elements.trim()) {
            return elements;
        }
    }
} catch (e) {
    console.warn('Absolute HTML import branch failed:', e);
}

// First, try to find slide-container or main content area
let contentElements = htmlContainer.querySelectorAll('.slide-container, .content, main, article, section');

if (contentElements.length === 0) {
    // If no containers, get direct children
    contentElements = htmlContainer.children;
}

if (contentElements.length === 0) {
    // If still no elements, create from text content
    const textContent = htmlContainer.textContent.trim();
    if (textContent) {
        elements = `
            <div class="element" style="position: absolute; left: 100px; top: 100px; width: 700px; height: auto; min-height: 200px; font-size: 16px; color: #333; line-height: 1.6; z-index: 1; cursor: move; padding: 30px; border: 2px solid #e2e8f0; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" data-type="text" contenteditable="true">
                ${textContent}
            </div>
        `;
    }
    return elements;
}

// Process each content element
for (let i = 0; i < contentElements.length; i++) {
    const element = contentElements[i];
    const elementType = element.tagName.toLowerCase();

    // Skip empty elements
    if (!element.textContent.trim() && !element.querySelector('img')) {
        continue;
    }

    let elementHtml = '';
    let width = 700;
    let height = 60;

    switch (elementType) {
        case 'h1':
            height = 80;
            elementHtml = `
                <div class="element" style="position: absolute; left: 100px; top: ${yOffset}px; width: ${width}px; min-height: ${height}px; font-size: 28px; font-weight: bold; color: #2d3748; text-align: center; z-index: ${zIndex}; cursor: move; padding: 20px; border: 2px solid transparent; background: rgba(255,255,255,0.9); border-radius: 8px;" data-type="heading" contenteditable="true">
                    ${element.innerHTML}
                </div>
            `;
            yOffset += height + 40;
            break;

        case 'h2':
            height = 60;
            elementHtml = `
                <div class="element" style="position: absolute; left: 100px; top: ${yOffset}px; width: ${width}px; min-height: ${height}px; font-size: 22px; font-weight: bold; color: #2d3748; z-index: ${zIndex}; cursor: move; padding: 15px; border: 2px solid transparent; background: rgba(255,255,255,0.9); border-radius: 8px;" data-type="heading" contenteditable="true">
                    ${element.innerHTML}
                </div>
            `;
            yOffset += height + 30;
            break;

        case 'h3':
            height = 50;
            elementHtml = `
                <div class="element" style="position: absolute; left: 100px; top: ${yOffset}px; width: ${width}px; min-height: ${height}px; font-size: 18px; font-weight: bold; color: #4a5568; z-index: ${zIndex}; cursor: move; padding: 12px; border: 2px solid transparent; background: rgba(255,255,255,0.9); border-radius: 8px;" data-type="heading" contenteditable="true">
                    ${element.innerHTML}
                </div>
            `;
            yOffset += height + 25;
            break;

        case 'p':
            const textLength = element.textContent.length;
            height = Math.max(60, Math.ceil(textLength / 100) * 25 + 40);
            elementHtml = `
                <div class="element" style="position: absolute; left: 100px; top: ${yOffset}px; width: ${width}px; min-height: ${height}px; font-size: 16px; color: #4a5568; line-height: 1.6; z-index: ${zIndex}; cursor: move; padding: 20px; border: 2px solid transparent; background: rgba(255,255,255,0.9); border-radius: 8px;" data-type="text" contenteditable="true">
                    ${element.innerHTML}
                </div>
            `;
            yOffset += height + 20;
            break;

        case 'ul':
        case 'ol':
            const listItems = element.children.length;
            height = Math.max(100, listItems * 30 + 60);
            elementHtml = `
                <div class="element" style="position: absolute; left: 100px; top: ${yOffset}px; width: ${width}px; min-height: ${height}px; font-size: 16px; color: #4a5568; line-height: 1.8; z-index: ${zIndex}; cursor: move; padding: 20px; border: 2px solid transparent; background: rgba(255,255,255,0.9); border-radius: 8px;" data-type="list" contenteditable="true">
                    ${element.outerHTML}
                </div>
            `;
            yOffset += height + 25;
            break;

        case 'img':
            height = 300;
            elementHtml = `
                <div class="element" style="position: absolute; left: 100px; top: ${yOffset}px; width: ${width}px; height: ${height}px; z-index: ${zIndex}; cursor: move; border: 2px solid transparent; border-radius: 8px; overflow: hidden;" data-type="image">
                    <img src="${element.src}" alt="${element.alt || ''}" style="width: 100%; height: 100%; object-fit: contain;">
                </div>
            `;
            yOffset += height + 30;
            break;

        case 'div':
        case 'section':
        case 'article':
            // Handle container elements
            const containerContent = element.innerHTML.trim();
            if (containerContent) {
                // Estimate height based on content
                const estimatedHeight = Math.max(150, Math.ceil(element.textContent.length / 120) * 30 + 100);
                elementHtml = `
                    <div class="element" style="position: absolute; left: 100px; top: ${yOffset}px; width: ${width}px; min-height: ${estimatedHeight}px; font-size: 16px; color: #4a5568; line-height: 1.6; z-index: ${zIndex}; cursor: move; padding: 25px; border: 2px solid transparent; background: rgba(255,255,255,0.95); border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" data-type="container" contenteditable="true">
                        ${containerContent}
                    </div>
                `;
                yOffset += estimatedHeight + 30;
            }
            break;

        default:
            // Generic elements
            if (element.innerHTML.trim()) {
                const estimatedHeight = Math.max(60, Math.ceil(element.textContent.length / 100) * 25 + 40);
                elementHtml = `
                    <div class="element" style="position: absolute; left: 100px; top: ${yOffset}px; width: ${width}px; min-height: ${estimatedHeight}px; font-size: 16px; color: #4a5568; z-index: ${zIndex}; cursor: move; padding: 20px; border: 2px solid transparent; background: rgba(255,255,255,0.9); border-radius: 8px;" data-type="content" contenteditable="true">
                        ${element.innerHTML}
                    </div>
                `;
                yOffset += estimatedHeight + 20;
            }
            break;
    }

    if (elementHtml) {
        elements += elementHtml;
        zIndex++;
    }
}

// Add CSS for better element interaction
elements += `
    <style>
        .element {
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .element:hover {
            border-color: #667eea !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
        }
        .element[contenteditable="true"]:focus {
            border-color: #667eea !important;
            outline: none !important;
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3) !important;
        }
        .element::before {
            content: attr(data-type);
            position: absolute;
            top: -8px;
            left: 8px;
            background: #667eea;
            color: white;
            padding: 2px 8px;
            font-size: 10px;
            border-radius: 4px;
            opacity: 0;
            transition: opacity 0.2s ease;
            pointer-events: none;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .element:hover::before {
            opacity: 1;
        }
        /* Styles for raw HTML container */
        .raw-html-container {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            font-family: inherit;
            line-height: 1.6;
        }
        .raw-html-container h1, .raw-html-container h2, .raw-html-container h3 {
            margin-top: 0;
            margin-bottom: 1rem;
        }
        .raw-html-container p {
            margin-bottom: 1rem;
        }
        .raw-html-container ul, .raw-html-container ol {
            margin-bottom: 1rem;
            padding-left: 2rem;
        }
        .raw-html-container img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }
        .raw-html-container::before {
            content: "RAW HTML";
            background: #f59e0b;
        }
    </style>
`;

console.log('Generated', elements.split('<div class="element"').length - 1, 'editable elements');
return elements;
        }

        // Function to show notification
export function showNotification(message, type = 'info') {
const notification = document.createElement('div');
notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === 'success' ? '#48bb78' : type === 'error' ? '#f56565' : '#4299e1'};
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    z-index: 10000;
    font-weight: 500;
    max-width: 300px;
    animation: slideIn 0.3s ease-out;
`;
notification.textContent = message;

// Add animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);

document.body.appendChild(notification);

setTimeout(() => {
    notification.style.animation = 'slideIn 0.3s ease-out reverse';
    setTimeout(() => notification.remove(), 300);
}, 4000);
        }

        // Helper functions for slide viewer
export function toggleSlideView(iframeId) {
const iframe = document.getElementById(iframeId);
const container = iframe.closest('.slide-renderer');
const sourceView = container.querySelector('.source-view');
const button = container.querySelector('button');

if (iframe.style.display === 'none') {
    iframe.style.display = 'block';
    sourceView.style.display = 'none';
    button.textContent = 'View Source';
    button.style.background = '#007bff';
} else {
    iframe.style.display = 'none';
    sourceView.style.display = 'block';
    button.textContent = 'View Rendered';
    button.style.background = '#28a745';
}
        }
export function openSlideInNewTab(iframeId) {
const iframe = document.getElementById(iframeId);
const htmlContent = iframe.getAttribute('srcdoc');
const blob = new Blob([htmlContent], { type: 'text/html' });
const url = URL.createObjectURL(blob);
window.open(url, '_blank');
        }
