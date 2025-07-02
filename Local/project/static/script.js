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
    document.getElementById('homePage').style.display = 'none';
    document.getElementById('editorPage').style.display = 'block';
}

function showHome() {
    document.getElementById('editorPage').style.display = 'none';
    document.getElementById('homePage').style.display = 'block';
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

        console.log('Sending DOCX file to /api/upload-docx'); // Debug
        const response = await fetch('/api/upload-docx', {
            method: 'POST',
            body: formData
        });

        console.log('Response status:', response.status); // Debug
        if (!response.ok) {
            throw new Error(`Upload DOCX failed with status ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data); // Debug
        if (data.slides && data.slides.length > 0) {
            const slideList = document.getElementById('slideList');
            slideList.innerHTML = '';

            data.slides.forEach((slide, index) => {
                addNewSlide(slide.content, index + 1);
            });

            selectFirstSlide();
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

        console.log('Sending ZIP file to /api/upload-zip'); // Debug
        const response = await fetch('/api/upload-zip', {
            method: 'POST',
            body: formData
        });

        console.log('Response status:', response.status); // Debug
        if (!response.ok) {
            throw new Error(`Upload ZIP failed with status ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data); // Debug
        if (data.slides && data.slides.length > 0) {
            const slideList = document.getElementById('slideList');
            slideList.innerHTML = '';

            data.slides.forEach((slide, index) => {
                addNewSlide(slide.content, index + 1);
            });

            selectFirstSlide();
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

function createNewSlide() {
    const slideList = document.getElementById('slideList');
    const slideCount = slideList.children.length + 1;
    const defaultContent = `
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {
                        margin: 0;
                        padding: 0;
                        width: 1920px;
                        height: 1080px;
                        background-color: #1a2526;
                        color: #fff;
                        font-family: Arial, sans-serif;
                    }
                    .slide-container {
                        width: 1920px;
                        height: 1080px;
                        display: flex;
                        flex-direction: row;
                    }
                    .left-container {
                        min-width: 600px;
                        height: 100%;
                        flex: 1;
                        padding: 32px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    }
                    .right-container {
                        height: 100%;
                        flex: 2;
                        padding: 32px;
                    }
                    .title {
                        font-size: 32px;
                        white-space: nowrap;
                        margin-bottom: 16px;
                    }
                    .subtitle {
                        font-size: 24px;
                        white-space: nowrap;
                        margin-bottom: 16px;
                    }
                    p {
                        font-size: 20px;
                        line-height: 1.5;
                    }
                </style>
            </head>
            <body>
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
            </body>
        </html>
    `;
    addNewSlide(defaultContent, slideCount);
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
    const iframe = document.createElement('iframe');
    iframe.style.width = '1920px';
    iframe.style.height = '1080px';
    iframe.style.border = 'none';
    iframe.style.pointerEvents = 'none'; // Cho phép nhấp qua iframe

    const blob = new Blob([content], { type: 'text/html' });
    let url = URL.createObjectURL(blob);
    iframe.src = url;

    const parser = new DOMParser();
    const doc = parser.parseFromString(content, 'text/html');
    const bodyContent = doc.body.innerHTML;
    const styles = Array.from(doc.head.getElementsByTagName('style')).map(style => style.outerHTML).join('');
    const bodyStyle = doc.body.getAttribute('style') || '';

    const editorDiv = document.createElement('div');
    editorDiv.className = 'slide-editor';
    editorDiv.contentEditable = true;
    editorDiv.innerHTML = bodyContent;
    editorDiv.style.cssText = bodyStyle + '; width: 1920px; height: 1080px; display: none;';

    container.innerHTML = `
        <div class="slide-wrapper">
            ${styles}
        </div>
    `;
    const wrapper = container.querySelector('.slide-wrapper');
    wrapper.appendChild(iframe);
    wrapper.appendChild(editorDiv);

    editorDiv.addEventListener('input', function() {
        const updatedContent = `
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="UTF-8">
                    ${styles}
                </head>
                <body style="${bodyStyle}">
                    ${editorDiv.innerHTML}
                </body>
            </html>
        `;
        const newBlob = new Blob([updatedContent], { type: 'text/html' });
        const newUrl = URL.createObjectURL(newBlob);
        iframe.src = newUrl;
        updateSlideContent(updatedContent);
        URL.revokeObjectURL(url);
        url = newUrl;
    });

    let isEditing = false;
    container.addEventListener('dblclick', function(e) {
        console.log('Double-click detected on slideContainer'); // Debug
        isEditing = !isEditing;
        iframe.style.display = isEditing ? 'none' : 'block';
        iframe.style.pointerEvents = isEditing ? 'none' : 'auto'; // Bật/tắt tương tác với iframe
        editorDiv.style.display = isEditing ? 'block' : 'none';
        if (isEditing) {
            editorDiv.focus();
            console.log('Switched to edit mode'); // Debug
        } else {
            console.log('Switched to view mode'); // Debug
        }
    });
}

function updateSlideContent(updatedContent) {
    const activeSlide = document.querySelector(".slide-item.active");
    if (activeSlide) {
        const slideContent = activeSlide.querySelector(".slide-content");
        slideContent.innerHTML = updatedContent;
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
    const slides = Array.from(document.querySelectorAll('.slide-item')).map(item => {
        return { content: item.querySelector('.slide-content').innerHTML };
    });

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
    const slides = Array.from(document.querySelectorAll('.slide-item')).map(item => {
        return { content: item.querySelector('.slide-content').innerHTML };
    });

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