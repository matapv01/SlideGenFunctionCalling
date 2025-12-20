// Backend API base URL
// Use global config loaded from config.js in head
const config = window.config || { BACKEND_URL: 'http://localhost:12008' };

// Authentication helper
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? {
        'Authorization': `Bearer ${token}`
    } : {};
}

// Toggle checkbox function for dropdown
window.toggleCheckbox = function (checkboxId, event) {
    const checkbox = document.getElementById(checkboxId);
    if (checkbox && event.target !== checkbox) {
        checkbox.checked = !checkbox.checked;
    }
};

document.addEventListener('DOMContentLoaded', function () {
    // Check VIP status and update UI
    checkVIPStatus();

    // Get checkbox values (no default setting)
    const transitionCheckbox = document.getElementById('enableTransitionSlides');
    const thankYouCheckbox = document.getElementById('enableThankYouSlide');
    console.log('✅ Checkbox states:', {
        transition: transitionCheckbox?.checked,
        thankYou: thankYouCheckbox?.checked
    });

    const docxInput = document.getElementById('docxFile');
    if (docxInput) {
        docxInput.addEventListener('change', function (e) {
            if (this.files.length > 0) {
                handleDocxImport();
            }
        });
    }

    const zipInput = document.getElementById('zipFile');
    if (zipInput) {
        zipInput.addEventListener('change', function (e) {
            if (this.files.length > 0) {
                handleZipImport();
            }
        });
    }

    const slideContainer = document.getElementById('slideContainer');
    if (slideContainer) {
        slideContainer.addEventListener('mouseup', updateToolbarFromSelection);
    }

    // Attach createNewSlide to all buttons
    document.querySelectorAll('button[onclick*="createNewSlide"]').forEach(btn => {
        btn.removeAttribute('onclick');
        btn.addEventListener('click', createNewSlide);
    });

    // Attach showHome to back button
    document.querySelectorAll('button[onclick*="showHome"]').forEach(btn => {
        btn.removeAttribute('onclick');
        btn.addEventListener('click', showHome);
    });

    // Attach exportToPDF
    document.querySelectorAll('button[onclick*="exportToPDF"]').forEach(btn => {
        btn.removeAttribute('onclick');
        btn.addEventListener('click', exportToPDF);
    });

    // Attach exportToZip
    document.querySelectorAll('button[onclick*="exportToZip"]').forEach(btn => {
        btn.removeAttribute('onclick');
        btn.addEventListener('click', exportToZip);
    });

    // Attach VIP upgrade button handler
    const upgradeVipBtn = document.getElementById('upgradeVipBtn');
    if (upgradeVipBtn) {
        upgradeVipBtn.addEventListener('click', handleUpgradeVIP);
    }

    // Attach workflow mode change handlers for UI toggle
    document.querySelectorAll('input[name="workflowMode"]').forEach(radio => {
        radio.addEventListener('change', updateAddSlideVisibility);
    });

    // Initial check for visibility
    updateAddSlideVisibility();
});

// Update visibility of "Add Slide" options based on selected workflow mode
function updateAddSlideVisibility() {
    const manualModeRadio = document.getElementById('manualMode');
    const addSlideDivider = document.getElementById('addSlideDivider');
    const addSlideOptionsContainer = document.getElementById('addSlideOptionsContainer');

    if (manualModeRadio && addSlideDivider && addSlideOptionsContainer) {
        if (manualModeRadio.checked) {
            console.log('🙈 Manual mode selected: Hiding Add Slide options');
            addSlideDivider.style.display = 'none';
            addSlideOptionsContainer.style.display = 'none';
        } else {
            console.log('👁️ Auto mode selected: Showing Add Slide options');
            addSlideDivider.style.display = 'block';
            addSlideOptionsContainer.style.display = 'block';
        }
    }
}


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
    console.log('🚀 handleDocxImport called - NEW VERSION');

    const docxInput = document.getElementById('docxFile');
    if (docxInput.files.length === 0) {
        showToast('Vui lòng chọn file DOCX!', 'error');
        return;
    }

    const file = docxInput.files[0];
    try {
        // Clear previous session data to prevent loading old slides
        console.log('🧹 Clearing previous streaming state...');
        sessionStorage.removeItem('streamingState');
        localStorage.removeItem('generatedSlides');

        showLoading("Đang tải file lên...");

        // ========== READ WORKFLOW MODE ==========
        const workflowModeRadio = document.querySelector('input[name="workflowMode"]:checked');
        const workflowModeValue = workflowModeRadio ? workflowModeRadio.value : 'auto';
        const isManualMode = workflowModeValue === 'manual';

        console.log('📋 Workflow mode value:', workflowModeValue);
        console.log('📋 Is manual mode:', isManualMode);

        // ========== MANUAL MODE: Upload + Create Session → Structure Editor ==========
        if (isManualMode) {
            console.log('🔧 Manual mode: Uploading file for structure editing...');

            const formData = new FormData();
            formData.append('file', file);
            formData.append('workflow_mode', 'manual');

            // Upload file and get document structure
            const response = await fetch(config.BACKEND_URL + '/api/upload-docx-for-manual', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Tải lên thất bại với trạng thái ${response.status}`);
            }

            const data = await response.json();
            console.log('✅ Manual upload response:', data);

            if (data.session_id) {
                hideLoading();
                showToast('Đã phân tích tài liệu! Đang chuyển đến Structure Editor...', 'success');
                setTimeout(() => {
                    window.location.href = `structure-editor.html?session=${data.session_id}`;
                }, 500);
                return;
            } else {
                throw new Error('Không tìm thấy session ID');
            }
        }

        // ========== AUTO MODE: Standard workflow ==========
        console.log('🤖 Auto mode: Starting standard workflow...');

        const formData = new FormData();
        formData.append('file', file);

        // Get slide options - explicitly convert to string
        const transitionCheckbox = document.getElementById('enableTransitionSlides');
        const thankYouCheckbox = document.getElementById('enableThankYouSlide');

        console.log('🔍 Checkbox elements:', {
            transitionCheckbox,
            thankYouCheckbox,
            transitionChecked: transitionCheckbox?.checked,
            thankYouChecked: thankYouCheckbox?.checked
        });

        const enableTransitionSlides = transitionCheckbox ? transitionCheckbox.checked : false;
        const enableThankYouSlide = thankYouCheckbox ? thankYouCheckbox.checked : false;

        // Map workflow mode values to backend expected values
        // autoNoStruct (auto_no_struct) -> needs AI to create structure
        // autoWithHeading (auto) -> document has headings
        // manual -> manual review
        let backendWorkflowMode = workflowModeValue;

        // Map auto_no_struct to no_structure for backend
        if (workflowModeValue === 'auto_no_struct') {
            backendWorkflowMode = 'no_structure';
        }

        // Convert boolean to string explicitly
        formData.append('enable_transition_slides', enableTransitionSlides.toString());
        formData.append('enable_thank_you_slide', enableThankYouSlide.toString());
        formData.append('workflow_mode', backendWorkflowMode);

        console.log('Uploading DOCX file to', config.BACKEND_URL + '/api/upload-docx-for-stream');
        console.log('Options (boolean):', { enableTransitionSlides, enableThankYouSlide });
        console.log('Workflow Mode (frontend):', workflowModeValue);
        console.log('Workflow Mode (backend):', backendWorkflowMode);
        console.log('Options (string):', {
            enable_transition_slides: enableTransitionSlides.toString(),
            enable_thank_you_slide: enableThankYouSlide.toString()
        });
        const response = await fetch(config.BACKEND_URL + '/api/upload-docx-for-stream', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: formData
        });

        console.log('Response status:', response.status);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `Upload DOCX thất bại với mã lỗi ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data);

        if (data.filename) {
            // Redirect to streaming page
            hideLoading();
            showToast('Đã upload thành công! Đang chuyển đến trang xử lý...', 'success');
            setTimeout(() => {
                window.location.href = `streaming.html?filename=${encodeURIComponent(data.filename)}`;
            }, 500);
        }
    } catch (error) {
        console.error('Error in handleDocxImport:', error);
        showToast(`Lỗi khi upload file DOCX: ${error.message}`, 'error');
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

        console.log('Sending ZIP file to', config.BACKEND_URL + '/api/upload-zip');
        const response = await fetch(config.BACKEND_URL + '/api/upload-zip', {
            method: 'POST',
            body: formData
        });

        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`Upload ZIP thất bại với mã lỗi ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data);
        if (data.project_name) {
            // Lưu thông tin project vào localStorage
            localStorage.setItem('projectName', data.project_name);
            localStorage.setItem('slidesSource', 'zip-imported');

            // Chuyển hướng đến edit.html local với project name
            showToast('Import ZIP thành công! Đang chuyển đến trang edit...', 'success');
            setTimeout(() => {
                window.location.href = `edit.html?project=${encodeURIComponent(data.project_name)}&source=generated`;
            }, 1500);
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

// createNewSlide() is now defined in index.html inline script

function addNewSlide(content, index) {
    const slideList = document.getElementById('slideList');
    const slideDiv = document.createElement("div");
    slideDiv.className = "slide-item";
    slideDiv.innerHTML = `
        <div class="slide-content" style="display: none;">
            ${content}
        </div>
        <button class="btn btn-sm btn-light delete-slide" title="Xóa slide">
            <i class="bi bi-x-lg"></i>
        </button>
    `;

    slideDiv.addEventListener("click", function (e) {
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
    deleteBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        showDeleteSlideConfirmation(slideDiv, index);
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
    iframe.style.width = '100%';
    iframe.style.height = '100%';
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
    editorDiv.style.cssText = bodyStyle + '; width: 100%; height: 100%; display: none;';

    container.innerHTML = `
        <div class="slide-wrapper">
            ${styles}
        </div>
    `;
    const wrapper = container.querySelector('.slide-wrapper');
    wrapper.appendChild(iframe);
    wrapper.appendChild(editorDiv);

    editorDiv.addEventListener('input', function () {
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
    container.addEventListener('dblclick', function (e) {
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
            throw new Error('Xuất PDF thất bại');
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
            throw new Error('Xuất ZIP thất bại');
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

// Show idea modal
window.showIdeaModal = function () {
    const modal = new bootstrap.Modal(document.getElementById('ideaModal'));
    modal.show();
};

// Generate slides from idea
window.generateFromIdea = async function () {
    const title = document.getElementById('ideaTitle').value.trim();
    const prompt = document.getElementById('ideaPrompt').value.trim();
    const contentLength = document.getElementById('ideaContentLength').value;
    const enableTransitions = document.getElementById('ideaEnableTransitions').checked;
    const enableThankYou = document.getElementById('ideaEnableThankYou').checked;

    // Validation
    if (!title) {
        showToast('Vui lòng nhập tiêu đề presentation', 'error');
        return;
    }
    if (!prompt) {
        showToast('Vui lòng nhập ý tưởng của bạn', 'error');
        return;
    }

    try {
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('ideaModal'));
        modal.hide();

        // Show loading
        showLoading("Đang tạo slide từ ý tưởng của bạn...");

        // Call backend API
        const apiUrl = `${config.BACKEND_URL}/api/generate-from-idea`;
        console.log('📡 Calling API:', apiUrl);
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()  // Add authentication token
            },
            body: JSON.stringify({
                title: title,
                prompt: prompt,
                content_length: contentLength,
                enable_transition_slides: enableTransitions,
                enable_thank_you_slide: enableThankYou
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Không thể tạo slide từ ý tưởng này');
        }

        const result = await response.json();

        // Redirect to streaming page with session_id
        if (result.session_id) {
            window.location.href = `streaming.html?session=${result.session_id}`;
        } else {
            throw new Error('Không nhận được session ID từ server');
        }

    } catch (error) {
        console.error('Error generating from idea:', error);
        showToast(`Lỗi: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
};

// Delete slide confirmation modal
function showDeleteSlideConfirmation(slideDiv, slideIndex) {
    const slideNumber = slideIndex !== undefined ? slideIndex + 1 :
        Array.from(slideDiv.parentElement.children).indexOf(slideDiv) + 1;

    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'delete-slide-modal-overlay';
    overlay.style.cssText = `
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        background: rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(4px) !important;
        z-index: 99999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        animation: fadeIn 0.2s ease !important;
    `;

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'delete-slide-modal';
    modal.style.cssText = `
        background: white !important;
        border-radius: 16px !important;
        padding: 32px !important;
        max-width: 450px !important;
        width: 90% !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3) !important;
        animation: slideUp 0.3s ease !important;
        position: relative !important;
        z-index: 100000 !important;
    `;

    modal.innerHTML = `
        <style>
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        </style>
        <div style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">🗑️</div>
            <h3 style="margin: 0 0 12px 0; font-size: 24px; color: #1f2937;">Xóa Slide?</h3>
            <p style="margin: 0 0 24px 0; color: #6b7280; font-size: 14px;">
                Bạn có chắc muốn xóa <strong>Slide ${slideNumber}</strong>?<br>
                Hành động này không thể hoàn tác.
            </p>
            <div style="display: flex; gap: 12px; justify-content: center;">
                <button id="cancelDeleteSlide" style="
                    padding: 12px 24px;
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    background: white;
                    color: #6b7280;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                ">Hủy</button>
                <button id="confirmDeleteSlide" style="
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    background: #ef4444;
                    color: white;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                ">Xóa Slide</button>
            </div>
        </div>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // Add hover effects
    const cancelBtn = modal.querySelector('#cancelDeleteSlide');
    const confirmBtn = modal.querySelector('#confirmDeleteSlide');

    cancelBtn.onmouseover = () => cancelBtn.style.background = '#f9fafb';
    cancelBtn.onmouseout = () => cancelBtn.style.background = 'white';

    confirmBtn.onmouseover = () => confirmBtn.style.background = '#dc2626';
    confirmBtn.onmouseout = () => confirmBtn.style.background = '#ef4444';

    // Handle buttons
    cancelBtn.onclick = () => {
        overlay.style.animation = 'fadeOut 0.2s ease';
        setTimeout(() => overlay.remove(), 200);
    };

    confirmBtn.onclick = () => {
        overlay.remove();
        slideDiv.remove();
        showToast('✓ Đã xóa slide thành công', 'success');
    };

    // Close on overlay click
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            overlay.style.animation = 'fadeOut 0.2s ease';
            setTimeout(() => overlay.remove(), 200);
        }
    };
}

// ========================== VIP FUNCTIONS ==========================

// Global VIP status
let isVIP = false;

async function checkVIPStatus() {
    console.log('🔍 Checking VIP status...');
    const token = localStorage.getItem('access_token');

    if (!token) {
        console.log('\u26a0\ufe0f  No token found, user not logged in');
        // Not logged in - show VIP restrictions for non-VIP
        updateVIPUI(false);
        return;
    }

    try {
        const response = await fetch(config.BACKEND_URL + '/api/user/me', {
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const userData = await response.json();
            isVIP = userData.is_vip || false;
            console.log(`\u2705 User VIP status: ${isVIP}`);
            updateVIPUI(isVIP);
        } else {
            console.log('\u26a0\ufe0f  Failed to get user info, treating as non-VIP');
            updateVIPUI(false);
        }
    } catch (error) {
        console.error('Error checking VIP status:', error);
        updateVIPUI(false);
    }
}

function updateVIPUI(isVIP) {
    const autoNoStructRadio = document.getElementById('autoNoStruct'); // Auto workflow mode (VIP)
    const autoWithHeadingRadio = document.getElementById('autoWithHeading'); // Auto With Doc Heading

    const autoNoStructVipBadge = document.getElementById('autoNoStructVipBadge');

    const vipUpgradeSection = document.getElementById('vipUpgradeSection');
    const vipUpgradeOption = document.getElementById('vipUpgradeOption');

    if (isVIP) {
        // VIP user - enable Auto workflow mode
        if (autoNoStructRadio) autoNoStructRadio.disabled = false;

        // Hide VIP badge
        if (autoNoStructVipBadge) autoNoStructVipBadge.style.display = 'none';

        // Hide upgrade button
        if (vipUpgradeSection) vipUpgradeSection.style.display = 'none';
        if (vipUpgradeOption) vipUpgradeOption.style.display = 'none';
    } else {
        // Non-VIP user - restrict Auto workflow mode only
        if (autoNoStructRadio) {
            autoNoStructRadio.disabled = true;
            // Switch to Auto With Doc Heading if Auto was selected
            if (autoNoStructRadio.checked && autoWithHeadingRadio) {
                autoWithHeadingRadio.checked = true;
            }
        }

        // Show VIP badge on Auto workflow mode
        if (autoNoStructVipBadge) autoNoStructVipBadge.style.display = 'inline';

        // Show upgrade button
        if (vipUpgradeSection) vipUpgradeSection.style.display = 'block';
        if (vipUpgradeOption) vipUpgradeOption.style.display = 'block';
    }

    // Toggle badges in Sidebar and Avatar
    const sidebarBadge = document.getElementById('sidebarVipBadge');
    const floatingBadge = document.getElementById('floatingVipBadge');

    // Function to update a badge element
    const updateBadge = (badge) => {
        if (!badge) return;
        badge.style.display = 'flex'; // Always show

        if (isVIP) {
            // VIP Style
            badge.classList.remove('free-tier');
            badge.innerHTML = '<i class="bi bi-patch-check-fill"></i> VIP';
        } else {
            // Free Style
            badge.classList.add('free-tier');
            badge.innerHTML = '<i class="bi bi-person"></i> FREE';
        }
    };

    updateBadge(sidebarBadge);
    updateBadge(floatingBadge);
}

async function handleUpgradeVIP() {
    console.log('⭐ Upgrading to VIP...');
    const token = localStorage.getItem('access_token');

    if (!token) {
        showToast('Vui lòng đăng nhập trước!', 'error');
        return;
    }

    try {
        const response = await fetch(config.BACKEND_URL + '/api/user/upgrade-vip', {
            method: 'POST',
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const result = await response.json();
            isVIP = true;
            updateVIPUI(true);
            showToast('\u2728 Chúc mừng! Bạn đã trở thành thành viên VIP!', 'success');
        } else {
            throw new Error('Nâng cấp lên VIP thất bại');
        }
    } catch (error) {
        console.error('Error upgrading to VIP:', error);
        showToast('Nâng cấp lên VIP thất bại. Vui lòng thử lại.', 'error');
    }
}