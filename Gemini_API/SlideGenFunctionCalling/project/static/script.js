document.addEventListener('DOMContentLoaded', function() {
    const docxInput = document.getElementById('docxFile');
    if (docxInput) {
        docxInput.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                handleDocxImport();
            }
        });
    }

    const zipInput = document.getElementById('zipFile');
    if (zipInput) {
        zipInput.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                handleZipImport();
            }
        });
    }

    const slideContainer = document.getElementById('slideContainer');
    if (slideContainer) {
        slideContainer.addEventListener('mouseup', updateToolbarFromSelection);
    }
});

function showEditor() {
    window.location.href = '/edit';
}

function showHome() {
    window.location.href = '/';
}

function showLoading(message) {
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    text.textContent = message;
    overlay.style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showToast(message, type) {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0`;
    toast.role = 'alert';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    setTimeout(() => toast.remove(), 3000);
}

async function handleDocxImport() {
    const docxInput = document.getElementById('docxFile');
    if (docxInput.files.length === 0) {
        showToast('Vui lòng chọn file DOCX!', 'error');
        return;
    }

    const file = docxInput.files[0];
    try {
        showLoading("Đang xử lý file DOCX...");
        const formData = new FormData();
        formData.append('file', file);

        console.log('Sending DOCX file to /api/upload-docx');
        const response = await fetch('/api/upload-docx', {
            method: 'POST',
            body: formData
        });

        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`Upload DOCX failed with status ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data);
        if (data.slides && data.slides.length > 0) {
            const slides = data.slides.map(slide => ({
                content: scopeSlideCSS(slide.content, `slide-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`),
                type: slide.type,
                preview: slide.preview
            }));
            sessionStorage.setItem('slides', JSON.stringify(slides));
            showEditor();
            showToast('Import DOCX thành công!', 'success');
        }
    } catch (error) {
        console.error('Error in handleDocxImport:', error);
        showToast(`Lỗi khi import file DOCX: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function handleZipImport() {
    const zipInput = document.getElementById('zipFile');
    if (zipInput.files.length === 0) {
        showToast('Vui lòng chọn file ZIP!', 'error');
        return;
    }

    const file = zipInput.files[0];
    try {
        showLoading("Đang xử lý file ZIP...");
        const formData = new FormData();
        formData.append('file', file);

        console.log('Sending ZIP file to /api/upload-zip');
        const response = await fetch('/api/upload-zip', {
            method: 'POST',
            body: formData
        });

        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`Upload ZIP failed with status ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data);
        if (data.slides && data.slides.length > 0) {
            const slides = data.slides.map(slide => ({
                content: scopeSlideCSS(slide.content, `slide-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`),
                type: slide.type,
                preview: slide.preview
            }));
            sessionStorage.setItem('slides', JSON.stringify(slides));
            showEditor();
            showToast('Import ZIP thành công!', 'success');
        } else {
            showToast('Không tìm thấy slide nào trong ZIP', 'error');
        }
    } catch (error) {
        console.error('Error in handleZipImport:', error);
        showToast(`Lỗi khi import file ZIP: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

function scopeSlideCSS(htmlContent, slideId) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    
    // Create a wrapper div with a unique class
    const wrapper = doc.createElement('div');
    wrapper.className = `slide-scope-${slideId}`;
    
    // Move body content into the wrapper
    const bodyContent = doc.body.innerHTML;
    wrapper.innerHTML = bodyContent;
    doc.body.innerHTML = '';
    doc.body.appendChild(wrapper);
    
    // Process styles to scope them to the wrapper
    const styleElements = doc.head.getElementsByTagName('style');
    for (let style of styleElements) {
        let cssText = style.textContent;
        // Prefix all selectors with the wrapper class
        cssText = cssText.replace(/(^|\{|\})\s*([^{}]+)\s*{/g, (match, prefix, selector) => {
            // Avoid scoping pseudo-elements and pseudo-classes directly
            if (selector.trim().startsWith(':') || selector.trim().startsWith('::')) {
                return match;
            }
            // Split selectors and add the wrapper class
            const scopedSelectors = selector.split(',').map(s => {
                s = s.trim();
                if (s === 'body' || s === 'html') {
                    return `.slide-scope-${slideId}`;
                }
                return `.slide-scope-${slideId} ${s}`;
            }).join(', ');
            return `${prefix} ${scopedSelectors} {`;
        });
        style.textContent = cssText;
    }
    
    // Add minimal reset styles to prevent leakage
    const resetStyle = doc.createElement('style');
    resetStyle.textContent = `
        html, body {
            margin: 0;
            padding: 0;
            width: 1920px;
            height: 1080px;
            background: transparent;
        }
        .slide-scope-${slideId} {
            width: 100%;
            height: 100%;
        }
    `;
    doc.head.appendChild(resetStyle);
    
    return doc.documentElement.outerHTML;
}

function createNewSlide() {
    const slideList = document.getElementById('slideList');
    const slideCount = slideList ? slideList.children.length + 1 : 1;
    const slideId = `slide-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const defaultContent = `
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    .slide-scope-${slideId} {
                        margin: 0;
                        padding: 0;
                        width: 1920px;
                        height: 1080px;
                        background-color: #1a2526;
                        color: #fff;
                        font-family: Arial, sans-serif;
                    }
                    .slide-scope-${slideId} .slide-container {
                        width: 1920px;
                        height: 1080px;
                        display: flex;
                        flex-direction: row;
                    }
                    .slide-scope-${slideId} .left-container {
                        min-width: 600px;
                        height: 100%;
                        flex: 1;
                        padding: 32px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    }
                    .slide-scope-${slideId} .right-container {
                        height: 100%;
                        flex: 2;
                        padding: 32px;
                    }
                    .slide-scope-${slideId} .title {
                        font-size: 32px;
                        white-space: nowrap;
                        margin-bottom: 16px;
                    }
                    .slide-scope-${slideId} .subtitle {
                        font-size: 24px;
                        white-space: nowrap;
                        margin-bottom: 16px;
                    }
                    .slide-scope-${slideId} p {
                        font-size: 20px;
                        line-height: 1.5;
                    }
                </style>
            </head>
            <body>
                <div class="slide-scope-${slideId}">
                    <div class="slide-container">
                        <div class="left-container">
                            <h1 class="title">New Slide</h1>
                            <h2 class="subtitle">Click to edit this slide</h2>
                            <p>Start adding your content here.</p>
                        </div>
                        <div class="right-container">
                            <!-- Nội dung bên phải có thể để trống hoặc thêm hình ảnh -->
                        </div>
                    </div>
                </div>
            </body>
        </html>
    `;
    let slides = JSON.parse(sessionStorage.getItem('slides') || '[]');
    slides.push({ content: defaultContent });
    sessionStorage.setItem('slides', JSON.stringify(slides));
    showEditor();
}

function addNewSlide(content, index) {
    const slideList = document.getElementById('slideList');
    const slideDiv = document.createElement("div");
    slideDiv.className = "slide-item";
    slideDiv.innerHTML = `
        <div class="slide-title">Slide ${index}</div>
        <div class="slide-content" style="display: none;">
            ${content}
        </div>
        <button class="btn btn-sm btn-light delete-slide" title="Xóa slide">
            <i class="bi bi-x-lg"></i>
        </button>
    `;

    slideDiv.addEventListener("click", function(e) {
        if (!e.target.closest('.delete-slide')) {
            document.querySelectorAll(".slide-item").forEach(item => {
                item.classList.remove("active");
            });
            this.classList.add("active");
            
            const slideContent = this.querySelector(".slide-content").innerHTML;
            const slideContainer = document.getElementById('slideContainer');
            if (slideContainer) {
                renderSlideInContainer(slideContent, slideContainer);
            }
        }
    });

    const deleteBtn = slideDiv.querySelector(".delete-slide");
    deleteBtn.addEventListener("click", function(e) {
        e.stopPropagation();
        if (confirm("Bạn có chắc muốn xóa slide này?")) {
            slideDiv.remove();
            let slides = JSON.parse(sessionStorage.getItem('slides') || '[]');
            slides.splice(index - 1, 1);
            sessionStorage.setItem('slides', JSON.stringify(slides));
        }
    });

    slideList.appendChild(slideDiv);
}

function selectFirstSlide() {
    const firstSlide = document.querySelector(".slide-item");
    if (firstSlide) {
        firstSlide.classList.add("active");
        const slideContent = firstSlide.querySelector(".slide-content").innerHTML;
        const slideContainer = document.getElementById('slideContainer');
        if (slideContainer) {
            renderSlideInContainer(slideContent, slideContainer);
        }
    }
}

function renderSlideInContainer(content, container) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(content, 'text/html');
    const slideId = doc.body.firstElementChild?.className || `slide-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const iframe = document.createElement('iframe');
    iframe.className = 'slide-iframe';
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';
    iframe.style.pointerEvents = 'none';

    // Update html and body styles to ensure width and height are 100%
    const htmlStyle = doc.documentElement.getAttribute('style') || '';
    const updatedHtmlStyle = `width: 100%; height: 100%; margin: 0; padding: 0; ${htmlStyle}`.replace(/;;+/g, ';').trim();
    const bodyStyle = doc.body.getAttribute('style') || '';
    const updatedBodyStyle = `width: 100%; height: 100%; margin: 0; padding: 0; ${bodyStyle}`.replace(/;;+/g, ';').trim();
    
    // Create updated content with modified html and body styles
    const updatedContent = `
        <!DOCTYPE html>
        <html style="${updatedHtmlStyle}">
            <head>
                <meta charset="UTF-8">
                ${Array.from(doc.head.getElementsByTagName('style')).map(style => style.outerHTML).join('')}
            </head>
            <body style="${updatedBodyStyle}">
                ${doc.body.innerHTML}
            </body>
        </html>
    `;
    
    const blob = new Blob([updatedContent], { type: 'text/html' });
    let url = URL.createObjectURL(blob);
    iframe.src = url;

    const bodyContent = doc.body.innerHTML;
    const styles = Array.from(doc.head.getElementsByTagName('style')).map(style => style.outerHTML).join('');

    const editorDiv = document.createElement('div');
    editorDiv.className = `slide-editor slide-scope-${slideId}`;
    editorDiv.contentEditable = true;
    editorDiv.innerHTML = bodyContent;
    editorDiv.style.cssText = updatedBodyStyle + '; display: none;';

    container.innerHTML = `
        <div class="slide-wrapper">
            ${styles}
        </div>
    `;
    const wrapper = container.querySelector('.slide-wrapper');
    wrapper.appendChild(iframe);
    wrapper.appendChild(editorDiv);

    editorDiv.addEventListener('input', function() {
        const updatedEditorContent = `
            <!DOCTYPE html>
            <html style="${updatedHtmlStyle}">
                <head>
                    <meta charset="UTF-8">
                    ${styles}
                </head>
                <body style="${updatedBodyStyle}">
                    ${editorDiv.innerHTML}
                </body>
            </html>
        `;
        const newBlob = new Blob([updatedEditorContent], { type: 'text/html' });
        const newUrl = URL.createObjectURL(newBlob);
        iframe.src = newUrl;
        updateSlideContent(updatedEditorContent);
        URL.revokeObjectURL(url);
        url = newUrl;
    });

    let isEditing = false;
    container.addEventListener('dblclick', function(e) {
        console.log('Double-click detected on slideContainer');
        isEditing = !isEditing;
        iframe.style.display = isEditing ? 'none' : 'block';
        iframe.style.pointerEvents = isEditing ? 'none' : 'auto';
        editorDiv.style.display = isEditing ? 'block' : 'none';
        if (isEditing) {
            editorDiv.focus();
            console.log('Switched to edit mode');
        } else {
            console.log('Switched to view mode');
        }
    });
}

function updateSlideContent(updatedContent) {
    const activeSlide = document.querySelector(".slide-item.active");
    if (activeSlide) {
        const slideContent = activeSlide.querySelector(".slide-content");
        slideContent.innerHTML = updatedContent;
        const index = Array.from(document.querySelectorAll('.slide-item')).indexOf(activeSlide);
        let slides = JSON.parse(sessionStorage.getItem('slides') || '[]');
        slides[index].content = updatedContent;
        sessionStorage.setItem('slides', JSON.stringify(slides));
    }
}

function applyTextColor() {
    const colorPicker = document.getElementById('colorPicker');
    if (!colorPicker) {
        console.error('Không tìm thấy #colorPicker trong DOM');
        showToast('Lỗi: Thanh công cụ chưa sẵn sàng!', 'error');
        return;
    }
    const color = colorPicker.value;
    const slideContainer = document.getElementById('slideContainer');
    const editorDiv = slideContainer.querySelector('.slide-editor');
    if (!editorDiv || editorDiv.style.display !== 'block') {
        showToast('Vui lòng nhấp đúp để vào chế độ chỉnh sửa!', 'error');
        return;
    }
    const selection = window.getSelection();
    if (selection.rangeCount) {
        const range = selection.getRangeAt(0);
        if (!range.collapsed) {
            const span = document.createElement('span');
            span.style.color = color;
            range.surroundContents(span);
            editorDiv.dispatchEvent(new Event('input'));
        } else {
            showToast('Vui lòng bôi đen văn bản trước!', 'error');
        }
    }
}

function changeFontSize() {
    const fontSizeSelect = document.getElementById('fontSizeSelect');
    if (!fontSizeSelect) {
        console.error('Không tìm thấy #fontSizeSelect trong DOM');
        showToast('Lỗi: Thanh công cụ chưa sẵn sàng!', 'error');
        return;
    }
    const size = fontSizeSelect.value;
    const slideContainer = document.getElementById('slideContainer');
    const editorDiv = slideContainer.querySelector('.slide-editor');
    if (!editorDiv || editorDiv.style.display !== 'block') {
        showToast('Vui lòng nhấp đúp để vào chế độ chỉnh sửa!', 'error');
        return;
    }
    const selection = window.getSelection();
    if (selection.rangeCount) {
        const range = selection.getRangeAt(0);
        if (!range.collapsed) {
            const span = document.createElement('span');
            span.style.fontSize = `${size}px`;
            range.surroundContents(span);
            editorDiv.dispatchEvent(new Event('input'));
        } else {
            showToast('Vui lòng bôi đen văn bản trước!', 'error');
        }
    }
}

function changeFontFamily() {
    const fontFamilySelect = document.getElementById('fontFamilySelect');
    if (!fontFamilySelect) {
        console.error('Không tìm thấy #fontFamilySelect trong DOM');
        showToast('Lỗi: Thanh công cụ chưa sẵn sàng!', 'error');
        return;
    }
    const font = fontFamilySelect.value;
    const slideContainer = document.getElementById('slideContainer');
    const editorDiv = slideContainer.querySelector('.slide-editor');
    if (!editorDiv || editorDiv.style.display !== 'block') {
        showToast('Vui lòng nhấp đúp để vào chế độ chỉnh sửa!', 'error');
        return;
    }
    const selection = window.getSelection();
    if (selection.rangeCount) {
        const range = selection.getRangeAt(0);
        if (!range.collapsed) {
            const span = document.createElement('span');
            span.style.fontFamily = font;
            range.surroundContents(span);
            editorDiv.dispatchEvent(new Event('input'));
        } else {
            showToast('Vui lòng bôi đen văn bản trước!', 'error');
        }
    }
}

function updateToolbarFromSelection() {
    const slideContainer = document.getElementById('slideContainer');
    const editorDiv = slideContainer.querySelector('.slide-editor');
    if (!editorDiv || editorDiv.style.display !== 'block') return;
    const selection = window.getSelection();
    if (selection.rangeCount) {
        const range = selection.getRangeAt(0);
        if (!range.collapsed) {
            const parentElement = range.commonAncestorContainer.parentElement;
            const computedStyle = window.getComputedStyle(parentElement);

            const color = computedStyle.color;
            const rgbMatch = color.match(/rgb\((\d+), (\d+), (\d+)\)/);
            if (rgbMatch) {
                const r = parseInt(rgbMatch[1]).toString(16).padStart(2, '0');
                const g = parseInt(rgbMatch[2]).toString(16).padStart(2, '0');
                const b = parseInt(rgbMatch[3]).toString(16).padStart(2, '0');
                document.getElementById('colorPicker').value = `#${r}${g}${b}`;
            }

            const fontSize = parseInt(computedStyle.fontSize);
            const sizeSelect = document.getElementById('fontSizeSelect');
            let closestSize = 12;
            for (let option of sizeSelect.options) {
                const value = parseInt(option.value);
                if (Math.abs(value - fontSize) < Math.abs(closestSize - fontSize)) {
                    closestSize = value;
                }
            }
            sizeSelect.value = closestSize;

            const fontFamily = computedStyle.fontFamily.split(',')[0].replace(/['"]/g, '');
            const fontSelect = document.getElementById('fontFamilySelect');
            let fontFound = false;
            for (let option of fontSelect.options) {
                if (option.value.toLowerCase() === fontFamily.toLowerCase()) {
                    fontSelect.value = option.value;
                    fontFound = true;
                    break;
                }
            }
            if (!fontFound) fontSelect.value = 'Arial';
        }
    }
}

async function exportToPDF() {
    let slides = JSON.parse(sessionStorage.getItem('slides') || '[]');
    try {
        showLoading("Đang xuất PDF...");
        const response = await fetch('/api/export-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(slides),
            timeout: 300000
        });

        if (!response.ok) {
            throw new Error('Export PDF failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'slides.pdf';
        a.click();
        window.URL.revokeObjectURL(url);
        showToast('Xuất PDF thành công!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Lỗi khi xuất PDF', 'error');
    } finally {
        hideLoading();
    }
}

async function exportToZip() {
    let slides = JSON.parse(sessionStorage.getItem('slides') || '[]');
    try {
        showLoading("Đang xuất ZIP...");
        const response = await fetch('/api/save-slides', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(slides)
        });

        if (!response.ok) {
            throw new Error('Export ZIP failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'slides.zip';
        a.click();
        window.URL.revokeObjectURL(url);
        showToast('Xuất ZIP thành công!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showToast('Lỗi khi xuất ZIP', 'error');
    } finally {
        hideLoading();
    }
}

// Load slides on edit page
if (window.location.pathname === '/edit') {
    let slides = JSON.parse(sessionStorage.getItem('slides') || '[]');
    slides.forEach((slide, index) => {
        addNewSlide(slide.content, index + 1);
    });
    selectFirstSlide();
}