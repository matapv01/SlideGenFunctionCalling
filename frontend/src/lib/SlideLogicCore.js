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
    constructor(rootElement, onElementSelect, onChange) {
        // Core Logic: Scope lại phạm vi hoạt động vào Shadow DOM
        this.root = rootElement; 
        this.onElementSelect = onElementSelect; // Callback gọi về React khi select element
        this.onChange = onChange; // Callback gọi về React khi có thay đổi content

        // Thay vì document.getElementById, ta tìm trong root (ShadowDOM)
        // Prefer .slide-bg-wrapper (stable outer wrapper from processHTML) to avoid
        // the .slide-container fallback text leaking into saved HTML
        this.canvas = this.root.querySelector('.slide-bg-wrapper') ||
                      this.root.querySelector('.slide-container') ||
                      this.root;
        
        // State nội bộ (giữ nguyên logic của edit.js)
        this.selectedElements = [];
        this.smartGuides = [];
        this.snapThreshold = 5;
        this.isDragging = false;
        this.isResizing = false;
        this.isPreparedForDrag = false;   // true after mousedown, becomes isDragging after 5px (like webfix)
        this.pendingSelectElement = null; // element to select on mouseup if no drag happened
        this.draggedElement = null;
        this.dragStart = null;            // { x, y } of mousedown position
        this.elementsStartPos = new Map(); // Map<element, {x,y,width,height}> like webfix
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
            if (!el.classList.contains('resize-handle') &&
                !el.classList.contains('drag-handle') && 
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

        // Allow text editing interactions — only exit when clicking outside
        if (this.isEditingText) {
            let clickedElement = target;
            let isClickingEditableElement = false;
            while (clickedElement && clickedElement !== this.root) {
                if (clickedElement.hasAttribute('contenteditable') && this.selectedElements.includes(clickedElement)) {
                    isClickingEditableElement = true;
                    break;
                }
                clickedElement = clickedElement.parentElement;
            }
            if (isClickingEditableElement) return;
            this.exitEditMode();
        }

        const isDragHandle = target.classList && target.classList.contains('drag-handle');
        const isResizeHandle = target.classList && target.classList.contains('resize-handle');

        // Click on canvas background → deselect
        if (!isResizeHandle && !isDragHandle && target.classList && (
            target.classList.contains('slide-bg-wrapper') ||
            target.classList.contains('slide-container')
        )) {
            this.deselectAll();
            return;
        }

        // Find closest selectable ancestor (or stop at handle)
        let targetElement = target;
        while (targetElement && targetElement !== this.root) {
            if (targetElement.hasAttribute('data-selectable') ||
                targetElement.classList.contains('element') ||
                targetElement.classList.contains('resize-handle') ||
                targetElement.classList.contains('drag-handle')) {
                break;
            }
            targetElement = targetElement.parentElement;
        }

        if (!targetElement || targetElement === this.root) {
            this.deselectAll();
            return;
        }

        // Resolve handle clicks to their parent .element
        if (isResizeHandle || isDragHandle) {
            const parentEl = target.closest('.element, [data-selectable]');
            if (parentEl) targetElement = parentEl;
        }

        // RESIZE — like webfix: read handle class directly ('tl','tr','bl','br')
        if (isResizeHandle && this.selectedElements.length > 0) {
            const el = this.selectedElements[0];
            this.isResizing = true;
            this.resizeHandle = target.classList[1]; // 'tl', 'tr', 'bl', 'br'
            this.dragStart = { x: e.clientX, y: e.clientY };
            if (el.style.position !== 'absolute') {
                el.style.position = 'absolute';
                el.style.left = `${el.offsetLeft}px`;
                el.style.top = `${el.offsetTop}px`;
                el.style.width = `${el.offsetWidth}px`;
            }
            this.elementsStartPos.clear();
            this.elementsStartPos.set(el, { x: el.offsetLeft, y: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight });
            e.preventDefault();
            e.stopPropagation();
            return;
        }

        const isAlreadySelected = this.selectedElements.includes(targetElement);

        // Not yet selected → pending select (confirmed on mouseup if no drag, like webfix)
        // No stopPropagation here — allows contenteditable cursor positioning naturally
        if (!isAlreadySelected && !isDragHandle) {
            this.pendingSelectElement = targetElement;
            this.dragStart = { x: e.clientX, y: e.clientY };
            return;
        }

        // Already selected or drag handle → prepare for drag
        if (isDragHandle) {
            this.selectElement(targetElement);
        }

        this.isPreparedForDrag = true;
        this.draggedElement = targetElement;
        this.dragStart = { x: e.clientX, y: e.clientY };

        this.elementsStartPos.clear();
        this.selectedElements.forEach(el => {
            if (el.style.position !== 'absolute') {
                el.style.position = 'absolute';
                el.style.left = `${el.offsetLeft}px`;
                el.style.top = `${el.offsetTop}px`;
            }
            this.elementsStartPos.set(el, { x: el.offsetLeft, y: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight });
        });
    }

    handleMouseMove(e) {
        // Activation threshold: only start drag after 5px movement (like webfix)
        if (this.isPreparedForDrag && !this.isDragging && this.dragStart) {
            const distanceMoved = Math.sqrt(
                Math.pow(e.clientX - this.dragStart.x, 2) +
                Math.pow(e.clientY - this.dragStart.y, 2)
            );
            if (distanceMoved > 5) {
                this.isDragging = true;
                this.isPreparedForDrag = false;
            } else {
                return;
            }
        }

        // RESIZE — like webfix: use includes() on handle class letters ('t','b','l','r')
        if (this.isResizing && this.selectedElements.length > 0) {
            e.preventDefault();
            const el = this.selectedElements[0];
            const startRect = this.elementsStartPos.get(el);
            if (!startRect) return;

            const dx = (e.clientX - this.dragStart.x) / this.currentScale;
            const dy = (e.clientY - this.dragStart.y) / this.currentScale;
            const { x, y, width, height } = startRect;

            if (this.resizeHandle.includes('r')) {
                el.style.width = `${Math.max(20, width + dx)}px`;
            }
            if (this.resizeHandle.includes('l')) {
                el.style.width = `${Math.max(20, width - dx)}px`;
                el.style.left = `${x + dx}px`;
            }
            if (this.resizeHandle.includes('b')) {
                el.style.height = `${Math.max(20, height + dy)}px`;
            }
            if (this.resizeHandle.includes('t')) {
                el.style.height = `${Math.max(20, height - dy)}px`;
                el.style.top = `${y + dy}px`;
            }

            this.updateSelectionUI();
            return;
        }

        if (!this.isDragging || !this.selectedElements.length) return;
        e.preventDefault();

        const primaryElement = this.selectedElements[0];
        const startPos = this.elementsStartPos.get(primaryElement);
        if (!startPos) return;

        let finalDx = (e.clientX - this.dragStart.x) / this.currentScale;
        let finalDy = (e.clientY - this.dragStart.y) / this.currentScale;

        // Snap
        const snapped = this.snapToGuides(primaryElement, startPos.x + finalDx, startPos.y + finalDy);
        finalDx = snapped.x - startPos.x;
        finalDy = snapped.y - startPos.y;

        // Move all selected elements (supports multi-select drag like webfix)
        this.selectedElements.forEach(el => {
            const elStartPos = this.elementsStartPos.get(el);
            if (elStartPos) {
                el.style.left = `${elStartPos.x + finalDx}px`;
                el.style.top = `${elStartPos.y + finalDy}px`;
            }
        });

        this.updateSelectionUI();
        this.drawSmartGuides(snapped.guides);
    }

    handleMouseUp(e) {
        // Pending select: confirm selection if mouse barely moved (it was a click, not a drag)
        if (this.pendingSelectElement) {
            let shouldSelect = true;
            if (this.dragStart && e) {
                const distanceMoved = Math.sqrt(
                    Math.pow(e.clientX - this.dragStart.x, 2) +
                    Math.pow(e.clientY - this.dragStart.y, 2)
                );
                shouldSelect = distanceMoved <= 2;
            }
            if (shouldSelect) {
                this.selectElement(this.pendingSelectElement);
            }
            this.pendingSelectElement = null;
            this.dragStart = null;
            return;
        }

        if (this.isDragging || this.isResizing) {
            // Only save history if there was actual movement (like webfix: > 3px threshold)
            let hasActualChange = false;
            if (this.dragStart && e) {
                const distanceMoved = Math.sqrt(
                    Math.pow(e.clientX - this.dragStart.x, 2) +
                    Math.pow(e.clientY - this.dragStart.y, 2)
                );
                hasActualChange = distanceMoved > 3;
            }
            if (hasActualChange) {
                this.saveHistory();
            }
        }

        this.isDragging = false;
        this.isResizing = false;
        this.isPreparedForDrag = false;
        this.resizeHandle = null;
        this.pendingSelectElement = null;
        this.draggedElement = null;
        this.elementsStartPos.clear();
        this.dragStart = null;
        this.clearSmartGuides();
    }

    snapToGuides(el, x, y) {
        const guides = [];
        
        // Snap to canvas edges
        if (Math.abs(x) < this.snapThreshold) {
            x = 0;
            guides.push({ type: 'vertical', pos: 0 });
        }
        if (Math.abs(y) < this.snapThreshold) {
            y = 0;
            guides.push({ type: 'horizontal', pos: 0 });
        }
        
        // Snap to center — use offset* to avoid broken getBoundingClientRect under CSS transforms
        const elW = el.offsetWidth;
        const elH = el.offsetHeight;
        const centerX = this.canvas.offsetWidth / 2;
        const centerY = this.canvas.offsetHeight / 2;
        const elCenterX = x + elW / 2;
        const elCenterY = y + elH / 2;
        
        if (Math.abs(elCenterX - centerX) < this.snapThreshold) {
            x = centerX - elW / 2;
            guides.push({ type: 'vertical', pos: centerX });
        }
        if (Math.abs(elCenterY - centerY) < this.snapThreshold) {
            y = centerY - elH / 2;
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
        if (!el) { this.deselectAll(); return; }
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
                dataType: el.dataset.type || 'shape',
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
        
        // Remove .selected class và xóa handles
        const oldSelected = this.root.querySelectorAll('.selected');
        oldSelected.forEach(el => {
            el.classList.remove('selected');
            const handles = el.querySelectorAll('.resize-handle, .drag-handle');
            handles.forEach(h => h.remove());
        });
        
        this.selectedElements = [];
        
        // Báo về React là không chọn gì cả
        if (this.onElementSelect) this.onElementSelect(null);
    }

    highlightElement(el) {
        // Xóa .selected class từ các element cũ
        const oldSelected = this.root.querySelectorAll('.selected');
        oldSelected.forEach(old => {
            old.classList.remove('selected');
            // Xóa resize handles cũ
            const oldHandles = old.querySelectorAll('.resize-handle, .drag-handle');
            oldHandles.forEach(h => h.remove());
        });
        
        // Đảm bảo element có class .element (CSS selector cần .element.selected)
        if (!el.classList.contains('element')) {
            el.classList.add('element');
        }
        
        // Add .selected class (CSS sẽ tự động tạo outline + animation)
        el.classList.add('selected');
        
        console.log('[highlightElement] Selected:', el.tagName, el.id, 'classes:', el.className);
        
        // Thêm resize handles trực tiếp vào element (như Legacy version)
        this.addResizeHandles(el);
    }

    addResizeHandles(element) {
        // Nếu đã có handles hoặc là group container thì skip
        if (element.classList.contains('group-container') || 
            element.querySelector('.resize-handle')) {
            return;
        }

        let handlesHTML = `
            <div class="resize-handle tl"></div>
            <div class="resize-handle tr"></div>
            <div class="resize-handle bl"></div>
            <div class="resize-handle br"></div>
        `;

        // Thêm drag handle cho text elements
        if (element.dataset.type === 'text' || element.hasAttribute('contenteditable')) {
            handlesHTML += `<div class="drag-handle" title="Drag to move">⠿</div>`;
        }

        element.insertAdjacentHTML('beforeend', handlesHTML);
    }

    updateSelectionUI() {
        if (this.selectedElements.length === 0) return;
        
        const el = this.selectedElements[0];
        this.highlightElement(el);
    }

    hideSelectionUI() {
        // Ẩn khung selection và handles khi đang edit text
        const selected = this.root.querySelector('.selected');
        if (selected) {
            // Tạm ẩn resize handles
            const handles = selected.querySelectorAll('.resize-handle, .drag-handle');
            handles.forEach(h => h.style.display = 'none');
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
        const selected = this.root.querySelector('.selected');
        if (selected) {
            const handles = selected.querySelectorAll('.resize-handle, .drag-handle');
            handles.forEach(h => h.style.display = '');
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

    execFormat(command, value = null) {
        document.execCommand(command, false, value);
        this.saveHistory();
    }

    getSelectedZIndex() {
        const el = this.selectedElements[0];
        if (!el) return 0;
        return parseInt(el.style.zIndex) || 0;
    }

    getMaxZIndex() {
        let max = 0;
        const elements = this.canvas.querySelectorAll('[data-selectable="true"], .element');
        elements.forEach(el => {
            if (el.classList.contains('resize-handle') ||
                el.classList.contains('drag-handle') ||
                el.classList.contains('smart-guide')) return;
            const z = parseInt(el.style.zIndex) || 0;
            if (z > max) max = z;
        });
        return max;
    }

    injectElement(html) {
        const temp = document.createElement('div');
        temp.innerHTML = html.trim();
        const el = temp.firstElementChild;
        if (!el || !(el instanceof HTMLElement)) return;

        // Always put new element on top
        const maxZ = this.getMaxZIndex();
        el.style.zIndex = String(maxZ + 1);

        // Ensure it has an ID
        if (!el.id) {
            el.id = `el_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
        }

        // Ensure selectable
        if (!el.hasAttribute('data-selectable')) el.setAttribute('data-selectable', 'true');
        el.style.cursor = 'move';
        if (!el.classList.contains('element')) el.classList.add('element');

        // Append to canvas
        this.canvas.appendChild(el);

        // Select it immediately so user can drag/edit
        this.selectElement(el);

        // Save to undo history
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
        
        // Notify React about changes
        if (this.onChange) {
            this.onChange();
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
