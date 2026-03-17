// Mixin: mouse event handlers (mousedown, mousemove, mouseup, dblclick)
export const EventHandlersMixin = {

    ensureDragPlaceholder(el, startPos) {
        if (!el || !el.parentElement) return;
        if (!this.dragPlaceholders) this.dragPlaceholders = new Map();
        if (this.dragPlaceholders.has(el)) return;

        const computed = window.getComputedStyle(el);
        const placeholder = document.createElement('div');
        placeholder.setAttribute('data-drag-placeholder', 'true');
        placeholder.style.visibility = 'hidden';
        placeholder.style.pointerEvents = 'none';
        placeholder.style.width = `${startPos.width}px`;
        placeholder.style.height = `${startPos.height}px`;
        placeholder.style.marginTop = computed.marginTop;
        placeholder.style.marginRight = computed.marginRight;
        placeholder.style.marginBottom = computed.marginBottom;
        placeholder.style.marginLeft = computed.marginLeft;
        placeholder.style.display = computed.display === 'inline' ? 'inline-block' : computed.display;

        el.parentElement.insertBefore(placeholder, el);
        this.dragPlaceholders.set(el, placeholder);
    },

    clearDragPlaceholders() {
        if (!this.dragPlaceholders) return;
        this.dragPlaceholders.forEach((placeholder) => {
            if (placeholder && placeholder.parentElement) placeholder.remove();
        });
        this.dragPlaceholders.clear();
    },

    handleDoubleClick(e) {
        const target = e.target;

        let textElement = target;
        while (textElement && textElement !== this.root) {
            if (textElement.hasAttribute('contenteditable')) break;
            textElement = textElement.parentElement;
        }

        if (textElement && textElement !== this.root && textElement.hasAttribute('contenteditable')) {
            this.isEditingText = true;
            textElement.style.cursor = 'text';
            textElement.focus();

            this.hideSelectionUI();

            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(textElement);
            range.collapse(false);
            selection.removeAllRanges();
            selection.addRange(range);

            e.preventDefault();
            e.stopPropagation();
        }
    },

    handleMouseDown(e) {
        const target = e.target;

        // If guides are lingering from a previous drag, clear them immediately
        if (this._guideTimeout) { clearTimeout(this._guideTimeout); this._guideTimeout = null; }
        this.clearSmartGuides();

        // Allow ongoing text editing to continue unless clicking outside
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

        const isDragHandle  = target.classList && target.classList.contains('drag-handle');
        const isResizeHandle = target.classList && target.classList.contains('resize-handle');
        const isMultiSelectIntent = e.shiftKey || e.ctrlKey || e.metaKey;

        // Click on canvas background → deselect
        if (!isResizeHandle && !isDragHandle && target.classList && (
            target.classList.contains('slide-bg-wrapper') ||
            target.classList.contains('slide-container') ||
            target.classList.contains('slide-inner-container') ||
            target.classList.contains('outer-wrapper') ||
            target.classList.contains('content-wrapper') ||
            target.classList.contains('wrapper') ||
            target.classList.contains('scale-container') ||
            target.classList.contains('slide-wrapper')
        )) {
            this.deselectAll();
            return;
        }

        // Walk up to find the closest selectable ancestor
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

        console.log('[handleMouseDown] target:', target.tagName, target.className, '→ resolved:', targetElement?.tagName, targetElement?.className, 'selectable:', targetElement?.hasAttribute?.('data-selectable'));

        if (!targetElement || targetElement === this.root) {
            this.deselectAll();
            return;
        }

        // Resolve handle clicks to their parent selectable element
        if (isResizeHandle || isDragHandle) {
            const parentEl = target.closest('.element, [data-selectable]');
            if (parentEl) targetElement = parentEl;
        }

        // RESIZE: grab handle info and prepare
        if (isResizeHandle && this.selectedElements.length > 0) {
            const el = this.selectedElements[0];
            this.isResizing = true;
            this.resizeHandle = target.classList[1]; // e.g. 'tl', 'tr', 'bl', 'br'
            this.pendingSelectMode = null;
            this.dragStart = { x: e.clientX, y: e.clientY };
            const bounds = this.getElementBounds
                ? this.getElementBounds(el)
                : { left: el.offsetLeft, top: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight };

            if (el.style.position !== 'absolute') {
                el.style.position = 'absolute';
                el.style.left  = `${bounds.left}px`;
                el.style.top   = `${bounds.top}px`;
                el.style.width = `${bounds.width}px`;
                el.style.height = `${bounds.height}px`;
            }
            this.elementsStartPos.clear();
            this.elementsStartPos.set(el, {
                x: bounds.left,
                y: bounds.top,
                width: bounds.width,
                height: bounds.height,
            });
            e.preventDefault();
            e.stopPropagation();
            return;
        }

        const isAlreadySelected = this.selectedElements.includes(targetElement);

        if (isMultiSelectIntent && !isDragHandle && !isResizeHandle) {
            this.pendingSelectElement = targetElement;
            this.pendingSelectMode = 'toggle';
            this.dragStart = { x: e.clientX, y: e.clientY };
            return;
        }

        // Not yet selected → defer selection to mouseup (cancel if drag happens)
        if (!isAlreadySelected && !isDragHandle) {
            this.pendingSelectElement = targetElement;
            this.pendingSelectMode = 'single';
            this.dragStart = { x: e.clientX, y: e.clientY };
            return;
        }

        // Normal drag (no Ctrl/Shift): always collapse to exactly one element.
        // This avoids accidental multi-selection causing unrelated elements to move.
        if (!isMultiSelectIntent && this.selectedElements.length > 1) {
            this.selectElement(targetElement);
        }

        // Already selected or drag handle → prepare for drag
        if (isDragHandle && !isAlreadySelected) {
            this.selectElement(targetElement);
        }

        this.isPreparedForDrag = true;
        this.draggedElement    = targetElement;
        this.pendingSelectMode = null;
        this.dragStart         = { x: e.clientX, y: e.clientY };

        this.elementsStartPos.clear();
        this.selectedElements.forEach(el => {
            const bounds = this.getElementBounds
                ? this.getElementBounds(el)
                : { left: el.offsetLeft, top: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight };

            this.elementsStartPos.set(el, {
                x: bounds.left,
                y: bounds.top,
                width: bounds.width,
                height: bounds.height,
            });
        });
    },

    handleMouseMove(e) {
        // Only start real drag after moving > 5px (prevents accidental drags)
        if (this.isPreparedForDrag && !this.isDragging && this.dragStart) {
            const dist = Math.sqrt(
                Math.pow(e.clientX - this.dragStart.x, 2) +
                Math.pow(e.clientY - this.dragStart.y, 2)
            );
            if (dist > 5) {
                this.isDragging      = true;
                this.isPreparedForDrag = false;

                // Convert CSS-positioned elements to absolute only when drag actually starts
                this.selectedElements.forEach(el => {
                    if (el.style.position !== 'absolute') {
                        const startPos = this.elementsStartPos.get(el);
                        if (startPos) {
                            // Keep a hidden placeholder in normal flow so sibling layout doesn't jump.
                            this.ensureDragPlaceholder(el, startPos);
                            el.style.position = 'absolute';
                            el.style.left = `${startPos.x}px`;
                            el.style.top  = `${startPos.y}px`;
                            el.style.width = `${startPos.width}px`;
                            el.style.height = `${startPos.height}px`;
                        }
                    }
                });
            } else {
                return;
            }
        }

        // RESIZE
        if (this.isResizing && this.selectedElements.length > 0) {
            e.preventDefault();
            const el        = this.selectedElements[0];
            const startRect = this.elementsStartPos.get(el);
            if (!startRect) return;

            const dx = (e.clientX - this.dragStart.x) / this.currentScale;
            const dy = (e.clientY - this.dragStart.y) / this.currentScale;
            const { x, y, width, height } = startRect;

            if (this.resizeHandle.includes('r')) el.style.width  = `${Math.max(20, width  + dx)}px`;
            if (this.resizeHandle.includes('l')) { el.style.width  = `${Math.max(20, width  - dx)}px`; el.style.left = `${x + dx}px`; }
            if (this.resizeHandle.includes('b')) el.style.height = `${Math.max(20, height + dy)}px`;
            if (this.resizeHandle.includes('t')) { el.style.height = `${Math.max(20, height - dy)}px`; el.style.top  = `${y + dy}px`; }

            this.updateSelectionUI();
            if (this.emitSelectedElementData) this.emitSelectedElementData(el);
            return;
        }

        if (!this.isDragging || !this.selectedElements.length) return;
        e.preventDefault();

        const primaryElement = this.selectedElements[0];
        const startPos       = this.elementsStartPos.get(primaryElement);
        if (!startPos) return;

        let finalDx = (e.clientX - this.dragStart.x) / this.currentScale;
        let finalDy = (e.clientY - this.dragStart.y) / this.currentScale;

        // Snap & guide lines
        const snapped = this.snapToGuides(primaryElement, startPos.x + finalDx, startPos.y + finalDy);
        finalDx = snapped.x - startPos.x;
        finalDy = snapped.y - startPos.y;

        // Move all selected elements (multi-select support)
        this.selectedElements.forEach(el => {
            const elStartPos = this.elementsStartPos.get(el);
            if (elStartPos) {
                el.style.left = `${elStartPos.x + finalDx}px`;
                el.style.top  = `${elStartPos.y + finalDy}px`;
            }
        });

        this.updateSelectionUI();
        if (this.emitSelectedElementData && this.selectedElements.length === 1) {
            this.emitSelectedElementData(this.selectedElements[0]);
        }
        this.drawSmartGuides(snapped.guides);
    },

    handleMouseUp(e) {
        // Confirm pending selection if the mouse barely moved (it was a click, not a drag)
        if (this.pendingSelectElement) {
            let shouldSelect = true;
            if (this.dragStart && e) {
                const dist = Math.sqrt(
                    Math.pow(e.clientX - this.dragStart.x, 2) +
                    Math.pow(e.clientY - this.dragStart.y, 2)
                );
                shouldSelect = dist <= 5;
            }
            if (shouldSelect) {
                if (this.pendingSelectMode === 'toggle') {
                    this.toggleSelection(this.pendingSelectElement);
                } else {
                    this.selectElement(this.pendingSelectElement);
                }
            }
            this.pendingSelectElement = null;
            this.pendingSelectMode = null;
            this.dragStart            = null;
            return;
        }

        if (this.isDragging || this.isResizing) {
            let hasActualChange = false;
            if (this.dragStart && e) {
                const dist = Math.sqrt(
                    Math.pow(e.clientX - this.dragStart.x, 2) +
                    Math.pow(e.clientY - this.dragStart.y, 2)
                );
                hasActualChange = dist > 3;
            }
            if (hasActualChange) {
                this.saveHistory();
                if (this.emitSelectedElementData && this.selectedElements.length === 1) {
                    this.emitSelectedElementData(this.selectedElements[0]);
                }
            }
        }

        this.clearDragPlaceholders();

        this.isDragging         = false;
        this.isResizing         = false;
        this.isPreparedForDrag  = false;
        this.resizeHandle       = null;
        this.pendingSelectElement = null;
        this.pendingSelectMode  = null;
        this.draggedElement     = null;
        this.elementsStartPos.clear();
        this.dragStart          = null;
        // Keep guides visible briefly after release so user can confirm alignment
        if (this._guideTimeout) clearTimeout(this._guideTimeout);
        this._guideTimeout = setTimeout(() => this.clearSmartGuides(), 400);
    },
};
