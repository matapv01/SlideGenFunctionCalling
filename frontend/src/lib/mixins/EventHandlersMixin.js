// Mixin: mouse event handlers (mousedown, mousemove, mouseup, dblclick)
export const EventHandlersMixin = {

    handleDoubleClick(e) {
        const target = e.target instanceof HTMLElement ? e.target : null;
        if (!target) return;

        const textElement = target.closest('[contenteditable]');
        if (textElement && (textElement.classList.contains('element') || textElement.hasAttribute('data-selectable'))) {
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
        const target = e.target instanceof HTMLElement ? e.target : null;
        if (!target) return;

        // If guides are lingering from a previous drag, clear them immediately
        if (this._guideTimeout) { clearTimeout(this._guideTimeout); this._guideTimeout = null; }
        this.clearSmartGuides();

        const isDragHandle = target.classList.contains('drag-handle');
        const isResizeHandle = target.classList.contains('resize-handle');
        const isCanvasBackground = !isResizeHandle && !isDragHandle && (
            target.classList.contains('slide-bg-wrapper') ||
            target.classList.contains('slide-container') ||
            target.classList.contains('slide-inner-container') ||
            target.classList.contains('outer-wrapper') ||
            target.classList.contains('content-wrapper') ||
            target.classList.contains('wrapper') ||
            target.classList.contains('scale-container') ||
            target.classList.contains('slide-wrapper')
        );

        if (isCanvasBackground) {
            this.deselectAll();
            return;
        }

        let targetElement = target.closest('.element, [data-selectable]');
        if ((isResizeHandle || isDragHandle) && !targetElement) {
            // Handles always belong to a selectable parent; if not, ignore.
            return;
        }

        // Allow ongoing text editing to continue unless clicking outside
        if (this.isEditingText) {
            const clickedElement = target.closest('[contenteditable]');
            const isClickingEditableElement = !!(
                clickedElement &&
                clickedElement.hasAttribute('contenteditable') &&
                this.selectedElements.includes(clickedElement)
            );
            if (isClickingEditableElement) return;
            this.exitEditMode();
        }

        if (!targetElement) {
            this.deselectAll();
            return;
        }

        const normalizedTarget = targetElement.closest('[data-selectable="true"], .element');
        if (!normalizedTarget || !this.canvas.contains(normalizedTarget)) {
            this.deselectAll();
            return;
        }
        targetElement = normalizedTarget;

        // RESIZE: grab handle info and prepare
        if (isResizeHandle && this.selectedElements.length > 0) {
            const el = this.selectedElements[0];
            this.isResizing = true;
            this.resizeHandle = target.classList[1]; // e.g. 'tl', 'tr', 'bl', 'br'
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

        // Not yet selected → defer selection to mouseup (cancel if drag happens)
        if (!isAlreadySelected && !isDragHandle) {
            this.pendingSelectElement = targetElement;
            this.dragStart = { x: e.clientX, y: e.clientY };
            return;
        }

        // Always collapse to exactly one element for drag.
        if (this.selectedElements.length > 1 || !isAlreadySelected) {
            this.selectElement(targetElement);
        }

        // Already selected or drag handle → prepare for drag
        if (isDragHandle && !isAlreadySelected) {
            this.selectElement(targetElement);
        }

        this.isPreparedForDrag = true;
        this.draggedElement    = targetElement;
        this.dragStart         = { x: e.clientX, y: e.clientY };

        this.elementsStartPos.clear();
        const bounds = this.getElementBounds
            ? this.getElementBounds(targetElement)
            : { left: targetElement.offsetLeft, top: targetElement.offsetTop, width: targetElement.offsetWidth, height: targetElement.offsetHeight };

        this.elementsStartPos.set(targetElement, {
            x: bounds.left,
            y: bounds.top,
            width: bounds.width,
            height: bounds.height,
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

        if (!this.isDragging || !this.draggedElement) return;
        e.preventDefault();

        const primaryElement = this.draggedElement;
        const startPos       = this.elementsStartPos.get(primaryElement);
        if (!startPos) return;

        let finalDx = (e.clientX - this.dragStart.x) / this.currentScale;
        let finalDy = (e.clientY - this.dragStart.y) / this.currentScale;

        // Snap & guide lines
        const snapped = this.snapToGuides(primaryElement, startPos.x + finalDx, startPos.y + finalDy);
        finalDx = snapped.x - startPos.x;
        finalDy = snapped.y - startPos.y;

        primaryElement.style.left = `${startPos.x + finalDx}px`;
        primaryElement.style.top  = `${startPos.y + finalDy}px`;

        this.updateSelectionUI();
        if (this.emitSelectedElementData) {
            this.emitSelectedElementData(primaryElement);
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
                shouldSelect = dist <= 2;
            }
            if (shouldSelect) {
                this.selectElement(this.pendingSelectElement);
            }
            this.pendingSelectElement = null;
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

        this.isDragging         = false;
        this.isResizing         = false;
        this.isPreparedForDrag  = false;
        this.resizeHandle       = null;
        this.pendingSelectElement = null;
        this.draggedElement     = null;
        this.elementsStartPos.clear();
        this.dragStart          = null;
        // Keep guides visible briefly after release so user can confirm alignment
        if (this._guideTimeout) clearTimeout(this._guideTimeout);
        this._guideTimeout = setTimeout(() => this.clearSmartGuides(), 400);
    },
};
