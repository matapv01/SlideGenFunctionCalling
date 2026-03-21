// Mixin: mouse event handlers (mousedown, mousemove, mouseup, dblclick)
export const EventHandlersMixin = {

    normalizeEventTarget(target) {
        if (target instanceof HTMLElement) return target;
        if (target instanceof Text) return target.parentElement;
        return null;
    },

    ensureElementAbsolutePosition(el, providedBounds = null) {
        if (!el) return null;

        const bounds = providedBounds || (this.getElementBounds
            ? this.getElementBounds(el)
            : { left: el.offsetLeft, top: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight });

        const computedPosition = window.getComputedStyle(el).position;
        if (computedPosition !== 'absolute') {
            console.log('[SlideLogicCore][Layout] Converting element to absolute', {
                id: el.id || null,
                computedPosition,
                left: bounds.left,
                top: bounds.top,
                width: bounds.width,
                height: bounds.height,
            });
            el.style.setProperty('position', 'absolute', 'important');
            el.style.left = `${bounds.left}px`;
            el.style.top = `${bounds.top}px`;
            el.style.width = `${bounds.width}px`;
            el.style.height = `${bounds.height}px`;
        }

        return bounds;
    },

    freezeSelectableSiblingsLayout(targetElement) {
        if (!targetElement || !(targetElement instanceof HTMLElement)) return;

        const parent = targetElement.parentElement;
        if (!parent) return;

        const siblingsToFreeze = Array.from(parent.children)
            .filter((node) => node instanceof HTMLElement)
            .filter((node) =>
                node.hasAttribute('data-selectable') || node.classList.contains('element')
            )
            .filter((node) => !this.isCanvasChromeElement || !this.isCanvasChromeElement(node));

        if (siblingsToFreeze.length === 0) return;

        // Snapshot all bounds first so converting one element cannot shift others.
        const snapshots = siblingsToFreeze.map((el) => {
            const bounds = this.getElementBounds
                ? this.getElementBounds(el)
                : { left: el.offsetLeft, top: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight };
            return { el, bounds };
        });

        console.log('[SlideLogicCore][Layout] Freezing sibling layout before drag/update', {
            targetId: targetElement.id || null,
            parentTag: parent.tagName,
            siblingCount: snapshots.length,
            siblingIds: snapshots.map(({ el }) => el.id || null),
        });

        snapshots.forEach(({ el, bounds }) => {
            this.ensureElementAbsolutePosition(el, bounds);
        });
    },

    handleDoubleClick(e) {
        const target = e.target;

        // ── Equation: activate MathLive field ───────────────────────────────
        let eqElement = target;
        while (eqElement && eqElement !== this.root) {
            if (eqElement.dataset?.type === 'equation') break;
            eqElement = eqElement.parentElement;
        }
        if (eqElement && eqElement !== this.root && eqElement.dataset.type === 'equation') {
            this.activateEquationEditor(eqElement);
            e.preventDefault();
            e.stopPropagation();
            return;
        }

        // ── Text contenteditable: existing behavior ──────────────────────────
        let textElement = target;
        while (textElement && textElement !== this.root) {
            if (textElement.hasAttribute('contenteditable')) break;
            textElement = textElement.parentElement;
        }
        const target = this.normalizeEventTarget(e.target);
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

    activateEquationEditor(el) {
        if (el._mathfieldActive) return;

        import('mathlive').then(() => {
            el._mathfieldActive = true;
            this.isEditingText = true;
            this.selectElement(el);
            this.hideSelectionUI();

            // Keep the existing <math-field> if present; otherwise create it.
            let mf = el.querySelector('math-field');
            if (!mf) {
                mf = document.createElement('math-field');
                mf.value = el.dataset.latex || '';
                el.innerHTML = '';
                el.appendChild(mf);
            }

            // Hide selection overlay to allow interaction with MathLive
            const overlay = el.querySelector('.equation-overlay');
            if (overlay) overlay.style.display = 'none';

            // Ensure edit mode
            mf.removeAttribute('read-only');
            mf.style.pointerEvents = 'auto';
            mf.style.cursor = 'text';

            // Attach handlers only once per equation element.
            if (!mf._equationInputHandler) {
                const onInput = () => {
                    el.dataset.latex = mf.value;
                    mf.setAttribute('value', mf.value);
                    if (this._inputTimer) clearTimeout(this._inputTimer);
                    this._inputTimer = setTimeout(() => {
                        this._inputTimer = null;
                        this.saveHistory();
                    }, 300);
                };
                mf._equationInputHandler = onInput;
                mf.addEventListener('input', onInput);
            }

            if (!mf._equationFocusOutHandler) {
                const onFocusOut = () => {
                    setTimeout(() => {
                        if (el._mathfieldActive && !mf.hasFocus?.()) {
                            this.exitEquationEditor(el);
                        }
                    }, 150);
                };
                mf._equationFocusOutHandler = onFocusOut;
                mf.addEventListener('focusout', onFocusOut);
            }

            mf.focus();
        }).catch(() => {
            el._mathfieldActive = false;
            this.isEditingText = false;
        });
    },

    exitEquationEditor(el) {
        if (!el || !el._mathfieldActive) return;

        const mf = el.querySelector('math-field');
        if (mf) {
            // Capture final LaTeX before blur.
            const prevLatex = el.dataset.latex;
            const nextLatex = mf.value || el.dataset.latex || '';
            if (nextLatex !== el.dataset.latex) {
                el.dataset.latex = nextLatex;
            }

            // Only unfocus: keep MathLive field in place.
            try { mf.blur?.(); } catch {}

            // If user changed LaTeX but debounce hasn't fired yet, persist it.
            if (prevLatex !== nextLatex) {
                this.saveHistory();
            }

            mf.style.pointerEvents = 'none';

            // Show selection overlay again
            const overlay = el.querySelector('.equation-overlay');
            if (overlay) overlay.style.display = 'block';
        }

        el._mathfieldActive = false;
        this.isEditingText = false;
        el.style.cursor = 'move';

        // Re-show selection handles after unfocus.
        const selected = this.root.querySelector('.selected');
        if (selected) {
            selected.querySelectorAll('.resize-handle, .drag-handle')
                .forEach(h => h.style.display = '');
        }
    },

    handleMouseDown(e) {
        const target = this.normalizeEventTarget(e.target);
        if (!target) return;

        console.log('[SlideLogicCore][Drag] MouseDown', {
            targetTag: target.tagName,
            targetId: target.id || null,
            targetClasses: target.className || null,
            selectedIds: this.selectedElements.map((el) => el.id || null),
            isEditingText: this.isEditingText,
            clientX: e.clientX,
            clientY: e.clientY,
        });

        // If guides are lingering from a previous drag, clear them immediately
        if (this._guideTimeout) { clearTimeout(this._guideTimeout); this._guideTimeout = null; }
        this.clearSmartGuides();

        // Allow ongoing text/equation editing to continue unless clicking outside
        if (this.isEditingText) {
            // Check if click is inside an active equation editor
            const activeEqEl = this.selectedElements.find?.(sel => sel._mathfieldActive);
            if (activeEqEl) {
                let clickedEl = target;
                while (clickedEl && clickedEl !== this.root) {
                    if (clickedEl === activeEqEl) return; // click inside equation — let MathLive handle
                    clickedEl = clickedEl.parentElement;
                }
                // Click outside: just unfocus equation, then continue normal selection.
                this.exitEquationEditor(activeEqEl);
                return;
            }

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

        let targetElement = target.closest('[data-selectable="true"]');
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

        const normalizedTarget = targetElement.closest('[data-selectable="true"]');
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

            // Freeze ALL selectable siblings to absolute so resizing one
            // element doesn't cause layout reflow in CSS flex/grid layouts.
            this.freezeSelectableSiblingsLayout(el);

            let bounds = this.getElementBounds
                ? this.getElementBounds(el)
                : { left: el.offsetLeft, top: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight };

            bounds = this.ensureElementAbsolutePosition(el, bounds) || bounds;
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
        this.draggedElement = targetElement;
        this._layoutFrozenForInteraction = false;
        this.dragStart = { x: e.clientX, y: e.clientY };

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
        // Start real drag only after moving > 5px to avoid accidental drags.
        if (this.isPreparedForDrag && !this.isDragging && this.dragStart) {
            const distanceMoved = Math.sqrt(
                Math.pow(e.clientX - this.dragStart.x, 2) +
                Math.pow(e.clientY - this.dragStart.y, 2)
            );

            if (distanceMoved > 5) {
                this.isDragging = true;
                this.isPreparedForDrag = false;
                this.disableTemplateDrag = true;

                // Freeze ALL selectable siblings to absolute positioning
                // right before drag begins. This preserves CSS layout during
                // display but ensures elements can be freely moved.
                if (!this._layoutFrozenForInteraction && this.draggedElement) {
                    this.freezeSelectableSiblingsLayout(this.draggedElement);
                    this._layoutFrozenForInteraction = true;
                }

                console.log('[SlideLogicCore][Drag] Drag started', {
                    draggedId: this.draggedElement?.id || null,
                    start: this.dragStart,
                    current: { x: e.clientX, y: e.clientY },
                    thresholdDistance: distanceMoved,
                    scale: this.currentScale,
                });
            } else {
                return;
            }
        }

        if (this.isResizing) {
            if (this.selectedElements.length !== 1) return;

            const targetElement = this.selectedElements[0];
            const dx = (e.clientX - this.dragStart.x) / this.currentScale;
            const dy = (e.clientY - this.dragStart.y) / this.currentScale;
            const el = targetElement;
            const startRect = this.elementsStartPos.get(el);
            if (!startRect) return;
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
            if (this.emitSelectedElementData) this.emitSelectedElementData(el);
            return;
        }

        if (this.isDragging && this.selectedElements.length > 0) {
            this.clearSmartGuides();

            let finalDx = (e.clientX - this.dragStart.x) / this.currentScale;
            let finalDy = (e.clientY - this.dragStart.y) / this.currentScale;

            const primaryElement = this.selectedElements[0];
            const startPos = this.elementsStartPos.get(primaryElement);
            if (!startPos) return;

            this.ensureElementAbsolutePosition(primaryElement, {
                left: startPos.x,
                top: startPos.y,
                width: startPos.width,
                height: startPos.height,
            });

            const snapped = this.snapToGuides(primaryElement, startPos.x + finalDx, startPos.y + finalDy);
            finalDx = snapped.x - startPos.x;
            finalDy = snapped.y - startPos.y;

            this.selectedElements.forEach((el) => {
                const elStartPos = this.elementsStartPos.get(el);
                if (!elStartPos) return;

                this.ensureElementAbsolutePosition(el, {
                    left: elStartPos.x,
                    top: elStartPos.y,
                    width: elStartPos.width,
                    height: elStartPos.height,
                });

                el.style.left = `${elStartPos.x + finalDx}px`;
                el.style.top = `${elStartPos.y + finalDy}px`;
            });

            this.drawSmartGuides(snapped.guides);

            if (this.selectedElements.length === 1 && this.emitSelectedElementData) {
                this.emitSelectedElementData(this.selectedElements[0]);
            }
        }
    },

    handleMouseUp(e) {
        this.isTextSelecting = false;

        this.root.querySelectorAll('.dragging, .drag-preview').forEach((el) => {
            el.classList.remove('dragging', 'drag-preview');
        });
        this.clearSmartGuides();

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

        const endedDrag = this.isDragging;
        const endedResize = this.isResizing;
        const activeElement = this.selectedElements[0] || null;

        if (this.isDragging || this.isResizing) {
            let hasActualChange = false;

            if (this.dragStart && e) {
                const distanceMoved = Math.sqrt(
                    Math.pow(e.clientX - this.dragStart.x, 2) +
                    Math.pow(e.clientY - this.dragStart.y, 2)
                );
                hasActualChange = distanceMoved > 3;
            }

            if (hasActualChange) {
                this.justFinishedDragging = true;
                setTimeout(() => {
                    this.justFinishedDragging = false;
                }, 100);

                this.saveHistory();
                if (this.emitSelectedElementData && this.selectedElements.length === 1) {
                    this.emitSelectedElementData(this.selectedElements[0]);
                }
            }

            console.log('[SlideLogicCore][Drag] MouseUp after interaction', {
                mode: endedResize ? 'resize' : (endedDrag ? 'drag' : 'unknown'),
                hasActualChange,
                elementId: activeElement?.id || null,
                left: activeElement?.style?.left || null,
                top: activeElement?.style?.top || null,
                width: activeElement?.style?.width || null,
                height: activeElement?.style?.height || null,
            });
        }

        this.isDragging = false;
        this.isResizing = false;
        this.isPreparedForDrag = false;
        this.resizeHandle = null;
        this.pendingSelectElement = null;
        this.draggedElement = null;
        this.disableTemplateDrag = false;
        this.elementsStartPos.clear();
        this.dragStart = null;
    },
};
