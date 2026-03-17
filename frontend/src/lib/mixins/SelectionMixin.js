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

        this.onElementSelect({
            id: el.id,
            tagName: el.tagName,
            dataType: el.dataset.type || 'shape',
            innerHTML: el.innerHTML,
            textContent: el.textContent,
            content: el.textContent || el.innerHTML,
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
            },
        });
    },

    makeElementsSelectable() {
        // Reset previously tagged nodes to avoid stale nested selectable targets.
        this.canvas.querySelectorAll('[data-selectable="true"]').forEach(el => {
            el.removeAttribute('data-selectable');
            if (el.style?.cursor === 'move') el.style.removeProperty('cursor');
        });

        const selectableElements = this.canvas.querySelectorAll(
            '.element, [data-type], ' +
            '[style*="position: absolute"], [style*="position:absolute"], ' +
            'h1, h2, h3, p, img, .text-block, .image-block'
        );

        selectableElements.forEach(el => {
            if (this.isCanvasChromeElement(el)) return;
            if (!el.id) el.id = this.getNextElementId();

            el.style.cursor = 'move';
            el.setAttribute('data-selectable', 'true');

            const isTextElement =
                el.dataset.type === 'text' ||
                ['H1', 'H2', 'H3', 'P'].includes(el.tagName) ||
                el.classList.contains('text-block');

            if (isTextElement && !el.querySelector('img')) {
                el.setAttribute('contenteditable', 'true');
            } else if (el.hasAttribute('contenteditable')) {
                el.removeAttribute('contenteditable');
            }
        });
    },

    selectElement(el) {
        if (!el) { this.deselectAll(); return; }

        if (!this.canvas.contains(el)) {
            const topLevelSelectable = el.closest('[data-selectable="true"], .element');
            if (!topLevelSelectable || !this.canvas.contains(topLevelSelectable)) {
                this.deselectAll();
                return;
            }
            el = topLevelSelectable;
        }

        this.selectedElements = [el];
        this.selectedElementId = el.id;

        this.highlightElement(el);
        this.emitSelectedElementData(el);
    },

    toggleSelection(el) {
        // Keep API compatibility but enforce single-select behavior.
        this.selectElement(el);
    },

    deselectAll() {
        if (this.isEditingText) this.exitEditMode();

        this.root.querySelectorAll('.selected').forEach(el => {
            el.classList.remove('selected');
            el.querySelectorAll('.resize-handle, .drag-handle').forEach(h => h.remove());
        });

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
        this.selectedElements = this.selectedElements.filter(el => !!el && el.isConnected);

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

        let handlesHTML = `
            <div class="resize-handle tl"></div>
            <div class="resize-handle tr"></div>
            <div class="resize-handle bl"></div>
            <div class="resize-handle br"></div>
        `;

        if (element.dataset.type === 'text' || element.hasAttribute('contenteditable')) {
            handlesHTML += `<div class="drag-handle" title="Drag to move">⠿</div>`;
        }

        element.insertAdjacentHTML('beforeend', handlesHTML);
    },

    updateSelectionUI() {
        if (this.selectedElements.length === 0) return;
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
