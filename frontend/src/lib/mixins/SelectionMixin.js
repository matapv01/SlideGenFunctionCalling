// Mixin: element selection, highlight, resize handles, text-edit mode
import { rgbToHex } from '../utils/colorUtils.js';

export const SelectionMixin = {

    makeElementsSelectable() {
        const selectableElements = this.root.querySelectorAll(
            '[style*="position: absolute"], [style*="position:absolute"], h1, h2, h3, p, img, .text-block, .image-block'
        );

        let idCounter = 1;
        selectableElements.forEach(el => {
            if (el.classList.contains('resize-handle') ||
                el.classList.contains('drag-handle') ||
                el.classList.contains('slide-bg-wrapper') ||
                el.classList.contains('slide-container')) return;

            if (!el.id) el.id = `element-${idCounter++}`;

            el.style.cursor = 'move';
            el.setAttribute('data-selectable', 'true');

            const isTextElement = ['H1', 'H2', 'H3', 'P', 'SPAN', 'DIV'].includes(el.tagName);
            if (isTextElement && !el.querySelector('img')) {
                el.setAttribute('contenteditable', 'true');
                el.style.outline = 'none';
            }
        });
    },

    selectElement(el) {
        if (!el) { this.deselectAll(); return; }
        console.log('[SlideLogicCore] Selecting element:', el);

        this.deselectAll();
        this.selectedElements = [el];

        this.highlightElement(el);

        if (this.onElementSelect) {
            const computedStyle = window.getComputedStyle(el);
            const rect          = el.getBoundingClientRect();

            this.selectedElementId = el.id;

            const colorHex = rgbToHex(computedStyle.color);
            const bgHex    = rgbToHex(computedStyle.backgroundColor);

            const fw      = computedStyle.fontWeight;
            const isBold  = fw === 'bold' || parseInt(fw) >= 700;
            const isItalic = computedStyle.fontStyle === 'italic';

            const decoration  = computedStyle.textDecoration || computedStyle.textDecorationLine || '';
            const isUnderline = decoration.includes('underline');

            const fontSizeVal    = parseFloat(computedStyle.fontSize) || 16;
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
                style: {
                    color:           colorHex,
                    backgroundColor: bgHex,
                    fontSize:        fontSizeVal,
                    fontFamily:      fontFamilyClean,
                    fontWeight:      isBold    ? 'bold'      : 'normal',
                    fontStyle:       isItalic  ? 'italic'    : 'normal',
                    textDecoration:  isUnderline ? 'underline' : 'none',
                    textAlign:       computedStyle.textAlign,
                    left:    parseFloat(el.style.left)   || 0,
                    top:     parseFloat(el.style.top)    || 0,
                    width:   parseFloat(el.style.width)  || rect.width,
                    height:  parseFloat(el.style.height) || rect.height,
                    position: computedStyle.position,
                },
            });
        }
    },

    deselectAll() {
        if (this.isEditingText) this.exitEditMode();

        this.root.querySelectorAll('.selected').forEach(el => {
            el.classList.remove('selected');
            el.querySelectorAll('.resize-handle, .drag-handle').forEach(h => h.remove());
        });

        this.selectedElements = [];
        if (this.onElementSelect) this.onElementSelect(null);
    },

    highlightElement(el) {
        // Remove selection from any previously selected elements
        this.root.querySelectorAll('.selected').forEach(old => {
            old.classList.remove('selected');
            old.querySelectorAll('.resize-handle, .drag-handle').forEach(h => h.remove());
        });

        if (!el.classList.contains('element')) el.classList.add('element');
        el.classList.add('selected');

        console.log('[highlightElement] Selected:', el.tagName, el.id, 'classes:', el.className);

        this.addResizeHandles(el);
    },

    addResizeHandles(element) {
        if (element.classList.contains('group-container') ||
            element.querySelector('.resize-handle')) return;

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
        this.highlightElement(this.selectedElements[0]);
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
