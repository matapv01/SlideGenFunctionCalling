// File: frontend/src/lib/SlideLogicCore.js

function rgbToHex(color) {
    if (!color || color === 'transparent') return '#000000';
    if (color.startsWith('#')) return color;
    
    // Lấy các số từ chuỗi rgb(r, g, b)
    const nums = color.match(/\d+/g);
    if (!nums || nums.length < 3) return '#000000';
    
    // Convert sang hex
    const r = parseInt(nums[0]).toString(16).padStart(2, '0');
    const g = parseInt(nums[1]).toString(16).padStart(2, '0');
    const b = parseInt(nums[2]).toString(16).padStart(2, '0');
    
    return `#${r}${g}${b}`;
}

export class SlideEditorLogic {
    constructor(rootElement, onElementSelect) {
        // Core Logic: Scope lại phạm vi hoạt động vào Shadow DOM
        this.root = rootElement; 
        this.onElementSelect = onElementSelect; // Callback gọi về React

        // Thay vì document.getElementById, ta tìm trong root (ShadowDOM)
        this.canvas = this.root.querySelector('.slide-container') || 
                      this.root.querySelector('.slide-bg-wrapper') ||
                      this.root;
        
        // State nội bộ (giữ nguyên logic của edit.js)
        this.selectedElements = [];
        this.smartGuides = [];
        this.snapThreshold = 5;
        this.isDragging = false;
        this.isResizing = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.elementStartPos = { x: 0, y: 0 };
        this.resizeHandle = null;
        this.history = [];
        this.historyIndex = -1;
        this.currentScale = 1;
        this.isEditingText = false;
        // Khởi tạo
        this.init();
    }

    init() {
        console.log('[SlideLogicCore] Initializing with root:', this.root);
        
        // Gắn sự kiện vào root thay vì document
        this.root.addEventListener('mousedown', (e) => this.handleMouseDown(e), true);
        this.root.addEventListener('dblclick', (e) => this.handleDoubleClick(e), true);
        
        // Mouse move/up cần gắn window để kéo thả mượt mà khi trượt ra ngoài khung
        this.boundMouseMove = (e) => this.handleMouseMove(e);
        this.boundMouseUp = (e) => this.handleMouseUp(e);
        
        window.addEventListener('mousemove', this.boundMouseMove);
        window.addEventListener('mouseup', this.boundMouseUp);

        // Logic cũ: convert style inline nếu cần
        this.applyBaseStyles();
        
        // Làm cho tất cả elements có thể select được
        this.makeElementsSelectable();
    }

    applyBaseStyles() {
        // Đảm bảo container có position relative để con cái absolute theo nó
        if(this.canvas) {
            this.canvas.style.position = 'relative';
            this.canvas.style.width = '100%';
            this.canvas.style.height = '100%';
            this.canvas.style.minHeight = '1080px';
        }
    }

    makeElementsSelectable() {
        // Tìm tất cả elements có thể chọn (có vị trí absolute hoặc là text/image blocks)
        const selectableElements = this.root.querySelectorAll(
            '[style*="position: absolute"], [style*="position:absolute"], h1, h2, h3, p, img, .text-block, .image-block'
        );
        
        let idCounter = 1;
        selectableElements.forEach(el => {
            if (!el.classList.contains('editor-overlay') && 
                !el.classList.contains('slide-bg-wrapper') &&
                !el.classList.contains('slide-container')) {
                
                // Gán ID nếu chưa có
                if (!el.id) {
                    el.id = `element-${idCounter++}`;
                }
                
                el.style.cursor = 'move';
                el.setAttribute('data-selectable', 'true');
                
                // Enable contentEditable cho text elements (chỉ khi double-click)
                const isTextElement = ['H1', 'H2', 'H3', 'P', 'SPAN', 'DIV'].includes(el.tagName);
                if (isTextElement && !el.querySelector('img')) {
                    el.setAttribute('contenteditable', 'true');
                    el.style.outline = 'none'; // Remove outline khi focus
                }
            }
        });
    }

    setScale(s) {
        this.currentScale = s || 1;
        console.log('[SlideLogicCore] Scale updated:', this.currentScale);
    }

    handleDoubleClick(e) {
        const target = e.target;
        
        // Tìm element text có thể edit
        let textElement = target;
        while (textElement && textElement !== this.root) {
            if (textElement.hasAttribute('contenteditable')) {
                break;
            }
            textElement = textElement.parentElement;
        }
        
        if (textElement && textElement !== this.root && textElement.hasAttribute('contenteditable')) {
            // Vào chế độ edit text
            this.isEditingText = true;
            textElement.style.cursor = 'text';
            textElement.focus();
            
            // Ẩn bounding box khi đang edit
            this.hideSelectionUI();
            
            // Đặt con trỏ ở cuối text (không select all)
            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(textElement);
            range.collapse(false); // false = collapse to end
            selection.removeAllRanges();
            selection.addRange(range);
            
            e.preventDefault();
            e.stopPropagation();
        }
    }

    handleMouseDown(e) {
        const target = e.target;
        
        // Bỏ qua nếu đang edit text - cho phép click trong text để di chuyển cursor
        if (this.isEditingText) {
            // Kiểm tra nếu click ra ngoài element đang edit thì thoát edit mode
            let clickedElement = target;
            let isClickingEditableElement = false;
            while (clickedElement && clickedElement !== this.root) {
                if (clickedElement.hasAttribute('contenteditable') && this.selectedElements.includes(clickedElement)) {
                    isClickingEditableElement = true;
                    break;
                }
                clickedElement = clickedElement.parentElement;
            }
            
            if (isClickingEditableElement) {
                // Cho phép click trong element đang edit text
                return;
            } else {
                // Thoát edit mode khi click ra ngoài
                this.exitEditMode();
            }
        }
        
        // Kiểm tra nếu click vào resize handle
        if (target.classList && target.classList.contains('resize-handle')) {
            this.isResizing = true;
            this.resizeHandle = target.dataset.handle;
            this.dragStartX = e.clientX;
            this.dragStartY = e.clientY;
            
            if (this.selectedElements.length > 0) {
                const el = this.selectedElements[0];
                
                // Đảm bảo element đã có position absolute
                const computedStyle = window.getComputedStyle(el);
                if (computedStyle.position !== 'absolute') {
                    const rect = el.getBoundingClientRect();
                    const canvasRect = this.canvas.getBoundingClientRect();
                    el.style.position = 'absolute';
                    el.style.left = `${(rect.left - canvasRect.left) / this.currentScale}px`; // Fix scale khi convert
                    el.style.top = `${(rect.top - canvasRect.top) / this.currentScale}px`;
                    el.style.width = `${rect.width / this.currentScale}px`;
                }
                
                // Lấy kích thước hiện tại
                const finalStyle = window.getComputedStyle(el);
                this.elementStartPos = {
                    x: parseFloat(finalStyle.left) || 0,
                    y: parseFloat(finalStyle.top) || 0,
                    width: parseFloat(finalStyle.width),
                    height: parseFloat(finalStyle.height)
                };
            }
            e.preventDefault();
            e.stopPropagation();
            return;
        }
        
        // Bỏ qua nếu click vào overlay hoặc vùng background
        if (target.classList && (
            target.classList.contains('editor-overlay') ||
            target.classList.contains('slide-bg-wrapper') ||
            target.classList.contains('slide-container')
        )) {
            this.deselectAll();
            return;
        }

        // Tìm element có thể select gần nhất
        let selectableElement = target;
        while (selectableElement && selectableElement !== this.root) {
            if (selectableElement.hasAttribute('data-selectable') ||
                ['H1', 'H2', 'H3', 'P', 'IMG', 'DIV'].includes(selectableElement.tagName)) {
                break;
            }
            selectableElement = selectableElement.parentElement;
        }

        if (selectableElement && selectableElement !== this.root) {
            // Chọn element
            this.selectElement(selectableElement);
            
            // Bắt đầu logic Drag (setup tọa độ ban đầu)
            this.isDragging = true;
            this.dragStartX = e.clientX;
            this.dragStartY = e.clientY;
            
            // QUAN TRỌNG: Nếu element chưa có position absolute, convert ngay
            const computedStyle = window.getComputedStyle(selectableElement);
            if (computedStyle.position !== 'absolute') {
                const rect = selectableElement.getBoundingClientRect();
                const canvasRect = this.canvas.getBoundingClientRect();
                
                selectableElement.style.position = 'absolute';
                selectableElement.style.left = `${rect.left - canvasRect.left}px`;
                selectableElement.style.top = `${rect.top - canvasRect.top}px`;
                selectableElement.style.width = `${rect.width}px`;
                selectableElement.style.height = `${rect.height}px`;
            }
            
            // Lấy vị trí sau khi đã convert
            const finalStyle = window.getComputedStyle(selectableElement);
            this.elementStartPos = {
                x: parseFloat(finalStyle.left) || 0,
                y: parseFloat(finalStyle.top) || 0
            };

            e.preventDefault();
            e.stopPropagation();
        } else {
            this.deselectAll();
        }
    }

    handleMouseMove(e) {
        if (this.isResizing && this.selectedElements.length > 0) {
            e.preventDefault();
            const el = this.selectedElements[0];
            
            // [SỬA LẠI] Chia delta chuột cho scale
            const dx = (e.clientX - this.dragStartX) / this.currentScale;
            const dy = (e.clientY - this.dragStartY) / this.currentScale;
            
            let newWidth = this.elementStartPos.width;
            let newHeight = this.elementStartPos.height;
            let newX = this.elementStartPos.x;
            let newY = this.elementStartPos.y;
            
            switch(this.resizeHandle) {
                case 'se': // bottom-right
                    newWidth = Math.max(20, this.elementStartPos.width + dx);
                    newHeight = Math.max(20, this.elementStartPos.height + dy);
                    break;
                case 'sw': // bottom-left
                    newWidth = Math.max(20, this.elementStartPos.width - dx);
                    newHeight = Math.max(20, this.elementStartPos.height + dy);
                    newX = this.elementStartPos.x + dx;
                    break;
                case 'ne': // top-right
                    newWidth = Math.max(20, this.elementStartPos.width + dx);
                    newHeight = Math.max(20, this.elementStartPos.height - dy);
                    newY = this.elementStartPos.y + dy;
                    break;
                case 'nw': // top-left
                    newWidth = Math.max(20, this.elementStartPos.width - dx);
                    newHeight = Math.max(20, this.elementStartPos.height - dy);
                    newX = this.elementStartPos.x + dx;
                    newY = this.elementStartPos.y + dy;
                    break;
            }
            
            el.style.width = `${newWidth}px`;
            el.style.height = `${newHeight}px`;
            el.style.left = `${newX}px`;
            el.style.top = `${newY}px`;
            
            this.updateSelectionUI();
            return;
        }
        
        if (!this.isDragging || !this.selectedElements.length) return;
        
        e.preventDefault();
        
        const el = this.selectedElements[0];
        
        // Tính toán vị trí mới
        const dx = (e.clientX - this.dragStartX) / this.currentScale;
        const dy = (e.clientY - this.dragStartY) / this.currentScale;
        
        let newX = this.elementStartPos.x + dx;
        let newY = this.elementStartPos.y + dy;
        
        // Snap to guides (optional, có thể bật/tắt)
        const snapped = this.snapToGuides(el, newX, newY);
        newX = snapped.x;
        newY = snapped.y;
        
        // Update position
        el.style.position = 'absolute';
        el.style.left = `${newX}px`;
        el.style.top = `${newY}px`;
        
        // Update selection UI
        this.updateSelectionUI();
        
        // Draw smart guides
        this.drawSmartGuides(snapped.guides);
    }

    handleMouseUp(e) {
        if (this.isDragging || this.isResizing) {
            // Save to history
            this.saveHistory();
        }
        
        this.isDragging = false;
        this.isResizing = false;
        this.resizeHandle = null;
        this.clearSmartGuides();
    }

    snapToGuides(el, x, y) {
        const guides = [];
        const canvasRect = this.canvas.getBoundingClientRect();
        
        // Snap to canvas edges
        if (Math.abs(x) < this.snapThreshold) {
            x = 0;
            guides.push({ type: 'vertical', pos: 0 });
        }
        if (Math.abs(y) < this.snapThreshold) {
            y = 0;
            guides.push({ type: 'horizontal', pos: 0 });
        }
        
        // Snap to center
        const elRect = el.getBoundingClientRect();
        const centerX = canvasRect.width / 2;
        const centerY = canvasRect.height / 2;
        const elCenterX = x + elRect.width / 2;
        const elCenterY = y + elRect.height / 2;
        
        if (Math.abs(elCenterX - centerX) < this.snapThreshold) {
            x = centerX - elRect.width / 2;
            guides.push({ type: 'vertical', pos: centerX });
        }
        if (Math.abs(elCenterY - centerY) < this.snapThreshold) {
            y = centerY - elRect.height / 2;
            guides.push({ type: 'horizontal', pos: centerY });
        }
        
        return { x, y, guides };
    }

    drawSmartGuides(guides) {
        this.clearSmartGuides();
        
        if (!guides || guides.length === 0) return;
        
        guides.forEach(guide => {
            const line = document.createElement('div');
            line.className = 'smart-guide';
            line.style.position = 'absolute';
            line.style.backgroundColor = '#3b82f6';
            line.style.pointerEvents = 'none';
            line.style.zIndex = '10000';
            
            if (guide.type === 'vertical') {
                line.style.left = `${guide.pos}px`;
                line.style.top = '0';
                line.style.width = '1px';
                line.style.height = '100%';
            } else {
                line.style.top = `${guide.pos}px`;
                line.style.left = '0';
                line.style.height = '1px';
                line.style.width = '100%';
            }
            
            this.canvas.appendChild(line);
        });
    }

    clearSmartGuides() {
        const guides = this.root.querySelectorAll('.smart-guide');
        guides.forEach(g => g.remove());
    }

    selectElement(el) {
        console.log('[SlideLogicCore] Selecting element:', el);
        
        this.deselectAll();
        this.selectedElements = [el];
        
        // Vẽ overlay selection (border xanh, resize handles)
        this.highlightElement(el);

        // QUAN TRỌNG: Báo về React để hiện properties
        if (this.onElementSelect) {
            const computedStyle = window.getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            
            // Store element ID
            this.selectedElementId = el.id;

            // --- BẮT ĐẦU LOGIC MAP PROPERTIES (PHẦN BẠN ĐANG THIẾU) ---

            // 1. Xử lý Màu (Convert RGB -> Hex)
            // Nếu không dùng hàm này, Input Color của React sẽ bị đen xì
            const colorHex = rgbToHex(computedStyle.color);
            const bgHex = rgbToHex(computedStyle.backgroundColor);

            // 2. Xử lý Bold (Trình duyệt trả về "700" hoặc "bold")
            const fw = computedStyle.fontWeight;
            const isBold = fw === 'bold' || parseInt(fw) >= 700;

            // 3. Xử lý Italic
            const isItalic = computedStyle.fontStyle === 'italic';

            // 4. Xử lý Underline (Trình duyệt trả về chuỗi phức tạp "underline solid...")
            const decoration = computedStyle.textDecoration || computedStyle.textDecorationLine || '';
            const isUnderline = decoration.includes('underline');

            // 5. Xử lý Font Size (Bỏ chữ 'px', lấy số)
            const fontSizeVal = parseFloat(computedStyle.fontSize) || 16;

            // 6. Xử lý Font Family (Bỏ dấu ngoặc kép thừa)
            const fontFamilyClean = computedStyle.fontFamily ? computedStyle.fontFamily.replace(/['"]/g, '') : 'Nunito';

            // Gửi dữ liệu ĐÃ LÀM SẠCH về React
            this.onElementSelect({
                id: el.id, 
                tagName: el.tagName,
                innerHTML: el.innerHTML,
                textContent: el.textContent,
                content: el.textContent || el.innerHTML,
                type: el.tagName.toLowerCase(), 
                style: {
                    // --- Dữ liệu đã chuẩn hóa ---
                    color: colorHex,             // Trả về #RRGGBB
                    backgroundColor: bgHex,      // Trả về #RRGGBB
                    fontSize: fontSizeVal,       // Trả về Number (vd: 24)
                    fontFamily: fontFamilyClean,
                    
                    fontWeight: isBold ? 'bold' : 'normal',       // Trả về 'bold'/'normal'
                    fontStyle: isItalic ? 'italic' : 'normal',    // Trả về 'italic'/'normal'
                    textDecoration: isUnderline ? 'underline' : 'none', // Trả về 'underline'/'none'
                    
                    textAlign: computedStyle.textAlign,
                    
                    // Các thông số vị trí giữ nguyên
                    left: parseFloat(el.style.left) || 0,
                    top: parseFloat(el.style.top) || 0,
                    width: parseFloat(el.style.width) || rect.width,
                    height: parseFloat(el.style.height) || rect.height,
                    position: computedStyle.position
                }
            });
        }
    }

    deselectAll() {
        // Thoát edit mode nếu đang edit
        if (this.isEditingText) {
            this.exitEditMode();
        }
        
        this.selectedElements = [];
        
        // Xóa các UI overlay (resize handles...)
        const overlays = this.root.querySelectorAll('.editor-overlay, .resize-handle');
        overlays.forEach(el => el.remove());
        
        // Báo về React là không chọn gì cả
        if (this.onElementSelect) this.onElementSelect(null);
    }

    highlightElement(el) {
        // Xóa overlay cũ
        const oldOverlays = this.root.querySelectorAll('.editor-overlay, .resize-handle');
        oldOverlays.forEach(o => o.remove());
        
        // Sử dụng position từ computed style (cho elements đã absolute)
        const computedStyle = window.getComputedStyle(el);
        
        let left, top, width, height;
        
        if (computedStyle.position === 'absolute') {
            // Lấy trực tiếp từ style
            left = parseFloat(computedStyle.left) || 0;
            top = parseFloat(computedStyle.top) || 0;
            width = parseFloat(computedStyle.width) || el.offsetWidth;
            height = parseFloat(computedStyle.height) || el.offsetHeight;
        } else {
            // Tính từ bounding rect (cho elements chưa absolute)
            const elRect = el.getBoundingClientRect();
            const canvasRect = this.canvas.getBoundingClientRect();
            left = elRect.left - canvasRect.left;
            top = elRect.top - canvasRect.top;
            width = elRect.width;
            height = elRect.height;
        }
        
        console.log('[highlightElement]', { 
            element: el.tagName,
            id: el.id,
            position: computedStyle.position,
            left, top, width, height
        });
        
        // Tạo overlay border
        const overlay = document.createElement('div');
        overlay.className = 'editor-overlay';
        overlay.style.position = 'absolute';
        overlay.style.left = `${left}px`;
        overlay.style.top = `${top}px`;
        overlay.style.width = `${width}px`;
        overlay.style.height = `${height}px`;
        overlay.style.border = '2px solid #3b82f6';
        overlay.style.pointerEvents = 'none';
        overlay.style.zIndex = '9999';
        overlay.style.boxSizing = 'border-box';
        
        this.canvas.appendChild(overlay);
        
        // Thêm resize handles đơn giản (SE only demo)
        const handle = document.createElement('div');
        handle.className = 'resize-handle';
        handle.dataset.handle = 'se';
        handle.style.position = 'absolute';
        handle.style.right = '-5px';
        handle.style.bottom = '-5px';
        handle.style.width = '10px';
        handle.style.height = '10px';
        handle.style.background = 'white';
        handle.style.border = '1px solid #3b82f6';
        handle.style.cursor = 'se-resize';
        handle.style.pointerEvents = 'auto'; // Quan trọng để bắt event
        overlay.appendChild(handle);
    }

    updateSelectionUI() {
        if (this.selectedElements.length === 0) return;
        
        const el = this.selectedElements[0];
        this.highlightElement(el);
    }

    hideSelectionUI() {
        // Ẩn khung selection khi đang edit text
        const existingOverlay = this.root.querySelector('.editor-overlay');
        if (existingOverlay) {
            existingOverlay.style.display = 'none';
        }
    }

    exitEditMode() {
        if (!this.isEditingText) return;
        
        this.isEditingText = false;
        
        // Reset cursor của element đang edit
        if (this.selectedElements.length > 0) {
            const el = this.selectedElements[0];
            if (el.hasAttribute('contenteditable')) {
                el.style.cursor = 'move';
                el.blur();
            }
        }
        
        // Hiện lại selection UI
        const existingOverlay = this.root.querySelector('.editor-overlay');
        if (existingOverlay) {
            existingOverlay.style.display = 'block';
        }
        
        // Clear text selection
        window.getSelection()?.removeAllRanges();
        
        // Save history sau khi edit xong
        this.saveHistory();
    }

    // --- API để React gọi ngược vào ---
    updateSelectedElementStyle(newStyles) {
        if (!this.selectedElements.length && !this.selectedElementId) {
            console.warn('[SlideLogicCore] No element selected to update');
            return;
        }
        
        // Tìm element bằng ID nếu chưa có trong selectedElements
        let el = this.selectedElements[0];
        if (!el && this.selectedElementId) {
            el = this.root.querySelector(`#${this.selectedElementId}`);
            if (el) {
                this.selectedElements = [el];
            }
        }
        
        if (!el) {
            console.warn('[SlideLogicCore] Could not find element to update');
            return;
        }
        
        console.log('[SlideLogicCore] Updating element style:', { id: el.id, styles: newStyles });
        
        // Apply styles
        Object.entries(newStyles).forEach(([key, value]) => {
            if (key === 'innerHTML' || key === 'textContent') {
                el.innerHTML = value;
            } else if (key === 'content') {
                el.innerHTML = value;
            } else {
                el.style[key] = value;
            }
        });
        
        // Update lại khung xanh selection
        this.updateSelectionUI();
        
        // Save history
        this.saveHistory();
    }

    getSelectedElement() {
        return this.selectedElements.length > 0 ? this.selectedElements[0] : null;
    }

    saveHistory() {
        // Simple history implementation
        const state = {
            timestamp: Date.now(),
            html: this.canvas.innerHTML
        };
        
        this.history = this.history.slice(0, this.historyIndex + 1);
        this.history.push(state);
        this.historyIndex++;
        
        // Limit history size
        if (this.history.length > 50) {
            this.history.shift();
            this.historyIndex--;
        }
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.canvas.innerHTML = this.history[this.historyIndex].html;
            this.makeElementsSelectable();
            this.deselectAll();
        }
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.canvas.innerHTML = this.history[this.historyIndex].html;
            this.makeElementsSelectable();
            this.deselectAll();
        }
    }

    getHTML() {
        return this.canvas.innerHTML;
    }
    
    destroy() {
        console.log('[SlideLogicCore] Destroying...');
        
        // Cleanup event listeners
        window.removeEventListener('mousemove', this.boundMouseMove);
        window.removeEventListener('mouseup', this.boundMouseUp);
        
        // Clear overlays
        this.deselectAll();
        this.clearSmartGuides();
    }
}
