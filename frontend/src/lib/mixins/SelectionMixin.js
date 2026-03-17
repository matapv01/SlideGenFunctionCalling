// Mixin: element selection, highlight, resize handles, text-edit mode
import { rgbToHex } from '../utils/colorUtils.js';

export const SelectionMixin = {

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
            },
        });
    },

    makeElementsSelectable() {
        const selectableElements = this.root.querySelectorAll(
            '.element, [data-type], ' +
            '.content-wrapper > *, .slide-container > *, .slide-inner-container > *, ' +
            '[style*="position: absolute"], [style*="position:absolute"], ' +
            'h1, h2, h3, p, img, .text-block, .image-block'
        );

        console.log('[makeElementsSelectable] Found', selectableElements.length, 'candidate elements');

        let idCounter = 1;
        let taggedCount = 0;
        selectableElements.forEach(el => {
            if (el.classList.contains('resize-handle') ||
                el.classList.contains('drag-handle') ||
                el.classList.contains('slide-bg-wrapper') ||
                el.classList.contains('slide-container') ||
                el.classList.contains('slide-inner-container') ||
                el.classList.contains('outer-wrapper') ||
                el.classList.contains('content-wrapper') ||
                el.classList.contains('wrapper') ||
                el.classList.contains('scale-container') ||
                el.classList.contains('slide-wrapper')) return;

            // Check if nested inside an already-selectable container
            let isNested = false;
            let ancestor = el.parentElement;
            while (ancestor && ancestor !== this.root) {
                if (ancestor.hasAttribute('data-selectable') || ancestor.classList.contains('element')) {
                    isNested = true;
                    break;
                }
                ancestor = ancestor.parentElement;
            }

            if (isNested) {
                // Nested text elements still need contenteditable so double-click positions
                // the cursor at the exact clicked element — but they must NOT become drag targets.
                const isTextEl = ['H1', 'H2', 'H3', 'P', 'SPAN'].includes(el.tagName);
                if (isTextEl && !el.querySelector('img') && !el.hasAttribute('contenteditable')) {
                    el.setAttribute('contenteditable', 'true');
                }
                return; // skip id, cursor:move, data-selectable
            }

            if (!el.id) el.id = `element-${idCounter++}`;

            el.style.cursor = 'move';
            el.setAttribute('data-selectable', 'true');
            taggedCount++;
            console.log('[makeElementsSelectable] Tagged:', el.tagName, el.id, 'type:', el.dataset?.type);

            const isTextElement = ['H1', 'H2', 'H3', 'P', 'SPAN', 'DIV'].includes(el.tagName);
            if (isTextElement && !el.querySelector('img')) {
                el.setAttribute('contenteditable', 'true');
            }
        });
    },

    selectElement(el) {
        if (!el) { this.deselectAll(); return; }
        console.log('[SlideLogicCore] Selecting element:', el);

        this.selectedElements = [el];
        this.selectedElementId = el.id;

        this.highlightElement(el);
        this.emitSelectedElementData(el);
    },

    toggleSelection(el) {
        if (!el) return;

        const idx = this.selectedElements.indexOf(el);
        if (idx >= 0) {
            this.selectedElements.splice(idx, 1);
        } else {
            this.selectedElements.push(el);
            this.selectedElementId = el.id;
        }

        const primary = this.getPrimarySelectedElement();
        this.selectedElementId = primary?.id ?? null;
        this.refreshSelectionVisuals();

        if (primary) {
            this.emitSelectedElementData(primary);
        } else if (this.onElementSelect) {
            this.onElementSelect(null);
        }
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

        console.log('[highlightElement] Selected:', el.tagName, el.id, 'classes:', el.className);
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
