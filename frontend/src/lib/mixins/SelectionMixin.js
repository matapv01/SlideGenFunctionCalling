// Mixin: element selection, highlight, resize handles, text-edit mode
import { rgbToHex } from '../utils/colorUtils.js';

export const SelectionMixin = {

    isCanvasChromeElement(el) {
        return el.classList.contains('resize-handle') ||
            el.classList.contains('drag-handle') ||
            el.classList.contains('slide-bg-wrapper') ||
            el.classList.contains('slide-container') ||
            el.classList.contains('slide-inner-container') ||
            el.classList.contains('outer-wrapper') ||
            el.classList.contains('content-wrapper') ||
            el.classList.contains('wrapper') ||
            el.classList.contains('scale-container') ||
            el.classList.contains('slide-wrapper');
    },

    getNextElementId() {
        const ids = new Set(
            Array.from(this.root.querySelectorAll('[id]')).map(node => node.id)
        );
        let idCounter = 1;
        while (ids.has(`element-${idCounter}`)) idCounter += 1;
        return `element-${idCounter}`;
    },

    readNumeric(value) {
        const n = parseFloat(value);
        return Number.isFinite(n) ? n : null;
    },

    readRotation(transform) {
        if (!transform || transform === 'none') return 0;
        try {
            const matrix = new DOMMatrixReadOnly(transform);
            return Math.round(Math.atan2(matrix.b, matrix.a) * (180 / Math.PI) * 100) / 100;
        } catch {
            const match = String(transform).match(/rotate\(([-\d.]+)deg\)/i);
            return match ? (parseFloat(match[1]) || 0) : 0;
        }
    },

    getElementBounds(element) {
        const computed = window.getComputedStyle(element);

        const left = this.readNumeric(element.style.left)
            ?? this.readNumeric(computed.left)
            ?? element.offsetLeft;

        const top = this.readNumeric(element.style.top)
            ?? this.readNumeric(computed.top)
            ?? element.offsetTop;

        const width = this.readNumeric(element.style.width)
            ?? this.readNumeric(computed.width)
            ?? element.offsetWidth;

        const height = this.readNumeric(element.style.height)
            ?? this.readNumeric(computed.height)
            ?? element.offsetHeight;

        return { left, top, width, height };
    },

    emitSelectedElementData(el) {
        if (!this.onElementSelect || !el) return;

        const computedStyle = window.getComputedStyle(el);
        const bounds = this.getElementBounds(el);

        const colorHex = rgbToHex(computedStyle.color);
        const bgHex = rgbToHex(computedStyle.backgroundColor);

        const fw = computedStyle.fontWeight;
        const isBold = fw === 'bold' || parseInt(fw) >= 700;
        const isItalic = computedStyle.fontStyle === 'italic';

        const decoration = computedStyle.textDecoration || computedStyle.textDecorationLine || '';
        const isUnderline = decoration.includes('underline');

        const computedZ = parseInt(computedStyle.zIndex, 10);
        const inlineZ = parseInt(el.style?.zIndex, 10);
        const resolvedZIndex = Number.isFinite(computedZ)
            ? computedZ
            : (Number.isFinite(inlineZ) ? inlineZ : 0);

        const fontSizeVal = parseFloat(computedStyle.fontSize) || 16;
        const fontFamilyClean = computedStyle.fontFamily
            ? computedStyle.fontFamily.replace(/['"]/g, '')
            : 'Nunito';
        const mediaElement = el.matches('img, video') ? el : el.querySelector('img, video');
        const mediaSrc = mediaElement?.getAttribute('src') || '';

        this.onElementSelect({
            id: el.id,
            tagName: el.tagName,
            dataType: el.dataset.type || 'shape',
            innerHTML: el.innerHTML,
            textContent: el.textContent,
            content: el.textContent || el.innerHTML,
            src: mediaSrc,
            selectedIds: this.selectedElements.map(node => node.id).filter(Boolean),
            selectionCount: this.selectedElements.length,
            groupId: el.dataset.editorGroup || null,
            isGroup: !!el.dataset.editorGroup && this.selectedElements.length > 1,
            type: el.tagName.toLowerCase(),
            x: bounds.left,
            y: bounds.top,
            width: bounds.width,
            height: bounds.height,
            style: {
                color: colorHex,
                backgroundColor: bgHex,
                fontSize: fontSizeVal,
                fontFamily: fontFamilyClean,
                fontWeight: isBold ? 'bold' : 'normal',
                fontStyle: isItalic ? 'italic' : 'normal',
                textDecoration: isUnderline ? 'underline' : 'none',
                textAlign: computedStyle.textAlign,
                left: bounds.left,
                top: bounds.top,
                width: bounds.width,
                height: bounds.height,
                position: computedStyle.position,
                zIndex: resolvedZIndex,
                opacity: parseFloat(computedStyle.opacity) || 1,
                rotation: this.readRotation(computedStyle.transform || el.style.transform),
            },
        });
    },

    makeElementsSelectable() {
        // Reset previously tagged nodes to avoid stale nested selectable targets.
        this.canvas.querySelectorAll('[data-selectable="true"]').forEach(el => {
            el.removeAttribute('data-selectable');
            if (el.style?.cursor === 'move') el.style.removeProperty('cursor');
        });

        // Only tag absolute-positioned elements as selectable/draggable.
        // Non-absolute elements (flex/grid/static layout) keep their CSS layout
        // and are NOT interactive — this preserves visual fidelity with HTML.
        const selectableElements = this.canvas.querySelectorAll(
            '.element, [data-type], ' +
            '[style*="position: absolute"], [style*="position:absolute"], ' +
            'h1, h2, h3, p, img, .text-block, .image-block'
        );

        selectableElements.forEach(el => {
            if (this.isCanvasChromeElement(el)) return;

            // Only make absolute-positioned elements selectable
            const computedPosition = window.getComputedStyle(el).position;
            if (computedPosition !== 'absolute') return;

            if (!el.id) el.id = this.getNextElementId();

            el.style.cursor = 'move';
            el.setAttribute('data-selectable', 'true');

            const dataType = el.dataset.type;
            const isNonTextType = dataType === 'equation' || dataType === 'shape' || dataType === 'image';

            const isTextElement =
                el.dataset.type === 'text' ||
                ['H1', 'H2', 'H3', 'P'].includes(el.tagName) ||
                el.classList.contains('text-block');

            if (isTextElement && !el.querySelector('img') && !isNonTextType) {
                el.setAttribute('contenteditable', 'true');
            } else if (el.hasAttribute('contenteditable')) {
                el.removeAttribute('contenteditable');
            }
        });

        // NOTE: Do NOT freeze elements to absolute positioning here.
        // Elements keep their original CSS layout (flex/grid/static) so the
        // slide looks identical to the original HTML. Absolute conversion
        // happens lazily in handleMouseMove when the user starts dragging.
    },

    selectElement(el) {
        if (!el) { this.deselectAll(); return; }

        if (!this.canvas.contains(el)) {
            const topLevelSelectable = el.closest('[data-selectable="true"]');
            if (!topLevelSelectable || !this.canvas.contains(topLevelSelectable)) {
                this.deselectAll();
                return;
            }
            el = topLevelSelectable;
        }

        const groupId = el.dataset?.editorGroup;
        const groupMembers = groupId
            ? Array.from(this.canvas.querySelectorAll('[data-editor-group]'))
                .filter(node => node.dataset?.editorGroup === groupId)
            : [];
        const selection = groupMembers.length > 1
            ? [el, ...groupMembers.filter(node => node !== el)]
            : [el];

        this.selectedElements = selection;
        this.selectedElementId = el.id;
        this.refreshSelectionVisuals();
        this.emitSelectedElementData(el);
    },

    toggleSelection(el) {
        if (!el) return;

        const groupId = el.dataset?.editorGroup;
        const candidates = groupId
            ? Array.from(this.canvas.querySelectorAll('[data-editor-group]'))
                .filter(node => node.dataset?.editorGroup === groupId)
            : [el];
        const allSelected = candidates.every(node => this.selectedElements.includes(node));

        if (allSelected) {
            this.selectedElements = this.selectedElements.filter(node => !candidates.includes(node));
        } else {
            this.selectedElements = [
                ...candidates,
                ...this.selectedElements.filter(node => !candidates.includes(node)),
            ];
        }

        if (this.selectedElements.length === 0) {
            this.deselectAll();
            return;
        }

        const primary = allSelected
            ? this.selectedElements[0]
            : (this.selectedElements.includes(el) ? el : this.selectedElements[0]);
        this.selectedElements = [
            primary,
            ...this.selectedElements.filter(node => node !== primary),
        ];
        this.selectedElementId = primary.id;
        this.refreshSelectionVisuals();
        this.emitSelectedElementData(primary);
    },

    deselectAll() {
        if (this.isEditingText) this.exitEditMode();

        this.root.querySelectorAll('.selected').forEach(el => {
            el.classList.remove('selected');
            el.querySelectorAll('.resize-handle, .drag-handle').forEach(h => h.remove());
        });
        this.root.querySelectorAll('math-field[data-inline-equation].inline-equation-selected')
            .forEach((el) => el.classList.remove('inline-equation-selected'));
        this._selectedInlineMathField = null;

        this.selectedElements = [];
        this.selectedElementId = null;
        if (this.onElementSelect) this.onElementSelect(null);
    },

    getPrimarySelectedElement() {
        if (!this.selectedElements.length) return null;

        if (this.selectedElementId) {
            const byId = this.selectedElements.find(el => el.id === this.selectedElementId);
            if (byId) return byId;
        }

        return this.selectedElements[this.selectedElements.length - 1];
    },

    refreshSelectionVisuals() {
        this.selectedElements = this.selectedElements.filter(el => !!el && this.root.contains(el));

        this.root.querySelectorAll('.selected').forEach(old => {
            old.classList.remove('selected');
            old.querySelectorAll('.resize-handle, .drag-handle').forEach(h => h.remove());
        });

        if (!this.selectedElements.length) return;

        this.selectedElements.forEach(el => {
            el.classList.add('selected');
        });

        const primary = this.getPrimarySelectedElement();
        if (primary) this.addResizeHandles(primary);
    },

    highlightElement(el) {
        if (!el) return;

        if (!this.selectedElements.includes(el)) {
            this.selectedElements = [el];
        }

        this.selectedElementId = el.id;
        this.refreshSelectionVisuals();
    },

    addResizeHandles(element) {
        // Void elements cannot have children — skip
        if (['IMG', 'INPUT', 'BR', 'HR'].includes(element.tagName)) return;
        if (element.querySelector('.resize-handle')) return;

        console.log('[SlideLogicCore][Selection] Injecting handles', {
            id: element.id || null,
            tag: element.tagName,
            type: element.dataset.type || null,
            contentEditable: element.getAttribute('contenteditable'),
            childCountBefore: element.childNodes.length,
        });

        const createHandle = (className, title = null, text = '') => {
            const handle = document.createElement('span');
            handle.className = className;
            handle.setAttribute('contenteditable', 'false');
            handle.setAttribute('data-editor-handle', 'true');
            handle.setAttribute('aria-hidden', 'true');
            // Keep handles out of document flow even before CSS class rules apply.
            handle.style.position = 'absolute';
            if (title) handle.setAttribute('title', title);
            if (text) handle.textContent = text;
            return handle;
        };

        const fragment = document.createDocumentFragment();
        fragment.appendChild(createHandle('resize-handle tl'));
        fragment.appendChild(createHandle('resize-handle tr'));
        fragment.appendChild(createHandle('resize-handle bl'));
        fragment.appendChild(createHandle('resize-handle br'));

        if (element.dataset.type === 'text' || element.hasAttribute('contenteditable')) {
            fragment.appendChild(createHandle('drag-handle', 'Drag to move', '⠿'));
        }

        element.appendChild(fragment);

        console.log('[SlideLogicCore][Selection] Handles injected', {
            id: element.id || null,
            childCountAfter: element.childNodes.length,
            resizeHandleCount: element.querySelectorAll('.resize-handle').length,
        });
    },

    updateSelectionUI() {
        if (this.selectedElements.length === 0) return;
        if (this.isDragging || this.isResizing) return;
        const primary = this.getPrimarySelectedElement();
        if (primary) this.highlightElement(primary);
    },

    hideSelectionUI() {
        const selected = this.root.querySelector('.selected');
        if (selected) {
            selected.querySelectorAll('.resize-handle, .drag-handle')
                .forEach(h => h.style.display = 'none');
        }
    },

    exitEditMode() {
        // Handle equation editor exit
        const activeEqEl = this.selectedElements.find?.(el => el._mathfieldActive) ||
            (this.selectedElements[0]?._mathfieldActive ? this.selectedElements[0] : null);
        if (activeEqEl) {
            this.exitEquationEditor(activeEqEl);
            return;
        }

        if (!this.isEditingText) return;

        this.isEditingText = false;

        if (this.selectedElements.length > 0) {
            const el = this.selectedElements[0];
            if (el.hasAttribute('contenteditable')) {
                el.style.cursor = 'move';
                el.blur();
            }
        }

        const selected = this.root.querySelector('.selected');
        if (selected) {
            selected.querySelectorAll('.resize-handle, .drag-handle')
                .forEach(h => h.style.display = '');
        }

        window.getSelection()?.removeAllRanges();
        this.saveHistory();
    },
};
