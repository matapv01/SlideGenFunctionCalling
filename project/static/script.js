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

        const response = await fetch('/api/upload-docx', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload DOCX failed');
        }

        const data = await response.json();
        if (data.slides && data.slides.length > 0) {
            const slideList = document.getElementById('slideList');
            slideList.innerHTML = '';

            data.slides.forEach((slide, index) => {
                addNewSlide(slide.content, slide.preview, index + 1);
            });

            selectFirstSlide();
            showEditor();
            showToast('Import DOCX thành công!', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Lỗi khi import file DOCX', 'error');
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

        const response = await fetch('/api/upload-zip', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload ZIP failed');
        }

        const data = await response.json();
        if (data.slides && data.slides.length > 0) {
            const slideList = document.getElementById('slideList');
            slideList.innerHTML = '';

            data.slides.forEach((slide, index) => {
                addNewSlide(slide.content, slide.preview, index + 1);
            });

            selectFirstSlide();
            showEditor();
            showToast('Import ZIP thành công!', 'success');
        } else {
            showToast('Không tìm thấy slide nào trong ZIP', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Lỗi khi import file ZIP', 'error');
    } finally {
        hideLoading();
    }
}

function createNewSlide() {
    const slideList = document.getElementById('slideList');
    const slideCount = slideList.children.length + 1;
    addNewSlide('<h2>New Slide</h2><p>Click to edit this slide.</p>', null, slideCount);
    showEditor();
}

function addNewSlide(content, preview, index) {
    const slideList = document.getElementById('slideList');
    const slideDiv = document.createElement("div");
    slideDiv.className = "slide-item";
    slideDiv.innerHTML = `
        <div class="slide-title">Slide ${index}</div>
        <div class="slide-content" style="display: none;">
            ${content}
        </div>
        ${preview ? `<img class="preview" src="${preview}" alt="Slide Preview">` : ''}
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
            
            const slideContent = this.querySelector(".slide-content");
            const slideContainer = document.getElementById('slideContainer');
            if (slideContent && slideContainer) {
                slideContainer.innerHTML = slideContent.innerHTML;
                makeContentEditable(slideContainer);
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
        const slideContent = firstSlide.querySelector(".slide-content");
        const slideContainer = document.getElementById('slideContainer');
        if (slideContent && slideContainer) {
            slideContainer.innerHTML = slideContent.innerHTML;
            makeContentEditable(slideContainer);
        }
    }
}

function makeContentEditable(container) {
    container.contentEditable = true;
    container.focus();
    container.addEventListener('input', updateSlideContent);
}

function applyTextColor() {
    const color = document.getElementById('colorPicker').value;
    const selection = window.getSelection();
    if (selection.rangeCount) {
        const range = selection.getRangeAt(0);
        if (!range.collapsed) {
            const span = document.createElement('span');
            span.style.color = color;
            range.surroundContents(span);
            updateSlideContent();
        } else {
            showToast('Vui lòng bôi đen văn bản trước!', 'error');
        }
    }
}

function changeFontSize() {
    const size = document.getElementById('fontSizeSelect').value;
    const selection = window.getSelection();
    if (selection.rangeCount) {
        const range = selection.getRangeAt(0);
        if (!range.collapsed) {
            const span = document.createElement('span');
            span.style.fontSize = `${size}px`;
            range.surroundContents(span);
            updateSlideContent();
        } else {
            showToast('Vui lòng bôi đen văn bản trước!', 'error');
        }
    }
}

function changeFontFamily() {
    const font = document.getElementById('fontFamilySelect').value;
    const selection = window.getSelection();
    if (selection.rangeCount) {
        const range = selection.getRangeAt(0);
        if (!range.collapsed) {
            const span = document.createElement('span');
            span.style.fontFamily = font;
            range.surroundContents(span);
            updateSlideContent();
        } else {
            showToast('Vui lòng bôi đen văn bản trước!', 'error');
        }
    }
}

function updateSlideContent() {
    const activeSlide = document.querySelector(".slide-item.active");
    if (activeSlide) {
        const slideContent = activeSlide.querySelector(".slide-content");
        const slideContainer = document.getElementById('slideContainer');
        slideContent.innerHTML = slideContainer.innerHTML;
    }
}

function updateToolbarFromSelection() {
    const selection = window.getSelection();
    if (selection.rangeCount) {
        const range = selection.getRangeAt(0);
        if (!range.collapsed) {
            const parentElement = range.commonAncestorContainer.parentElement;
            const computedStyle = window.getComputedStyle(parentElement);

            // Cập nhật màu
            const color = computedStyle.color;
            const rgbMatch = color.match(/rgb\((\d+), (\d+), (\d+)\)/);
            if (rgbMatch) {
                const r = parseInt(rgbMatch[1]).toString(16).padStart(2, '0');
                const g = parseInt(rgbMatch[2]).toString(16).padStart(2, '0');
                const b = parseInt(rgbMatch[3]).toString(16).padStart(2, '0');
                document.getElementById('colorPicker').value = `#${r}${g}${b}`;
            }

            // Cập nhật kích thước chữ
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

            // Cập nhật font chữ
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
            if (!fontFound) fontSelect.value = 'Arial'; // Mặc định nếu không khớp
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
            timeout: 300000 // 5 phút
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