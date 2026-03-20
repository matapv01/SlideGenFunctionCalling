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

            // Intentionally treat each eligible node as an independent editable/draggable element.
            // Do not short-circuit nested nodes based on selectable ancestors.

            if (!el.id) el.id = `element-${idCounter++}`;

            el.style.cursor = 'move';
            el.setAttribute('data-selectable', 'true');
            taggedCount++;
            console.log('[makeElementsSelectable] Tagged:', el.tagName, el.id, 'type:', el.dataset?.type);

            const isTextElement = ['H1', 'H2', 'H3', 'P', 'SPAN', 'DIV'].includes(el.tagName);
            const dataType = el.dataset.type;
            const isNonTextType = dataType === 'equation' || dataType === 'shape' || dataType === 'image';
            
            if (isTextElement && !el.querySelector('img') && !isNonTextType) {
                el.setAttribute('contenteditable', 'true');
            }
        });

        // Leaf-only selectable policy: if a node contains other selectable nodes,
        // keep interaction on the deepest descendants to avoid parent "group frame".
        const tagged = Array.from(this.root.querySelectorAll('[data-selectable="true"], .element'));
        const INLINE_FORMATTING_TAGS = new Set([
            'SPAN', 'STRONG', 'B', 'EM', 'I', 'U', 'MARK', 'SMALL',
            'SUB', 'SUP', 'CODE', 'KBD', 'SAMP', 'VAR', 'A',
            'FONT', 'INS', 'DEL', 'S', 'ABBR', 'CITE', 'Q', 'TIME',
            'BR', 'WBR', 'HR'
        ]);

        // Never make inline formatting fragments draggable/selectable blocks.
        tagged.forEach(el => {
            if (!INLINE_FORMATTING_TAGS.has(el.tagName)) return;
            el.classList.remove('selected');
            el.classList.remove('element');
            el.removeAttribute('data-selectable');
            el.removeAttribute('data-type');
            if (el.hasAttribute('contenteditable')) el.removeAttribute('contenteditable');
            if (el.style?.cursor === 'move') el.style.removeProperty('cursor');
            el.querySelectorAll('.resize-handle, .drag-handle').forEach(h => h.remove());
        });

        tagged.forEach(el => {
            const childSelectable = !!el.querySelector('[data-selectable="true"], .element');

            if (!childSelectable) return;

            el.classList.remove('selected');
            el.classList.remove('element');
            el.removeAttribute('data-selectable');
            // Parent text containers should not stay editable when child nodes are independently editable.
            if (el.hasAttribute('contenteditable')) {
                el.removeAttribute('contenteditable');
            }
            el.querySelectorAll('.resize-handle, .drag-handle').forEach(h => h.remove());
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
