// Mixin: public API for React to manipulate elements (style updates, z-order, inject, etc.)
export const ElementAPIMixin = {

    updateSelectedElementStyle(newStyles) {
        if (!this.selectedElements.length && !this.selectedElementId) {
            console.warn('[SlideLogicCore] No element selected to update');
            return;
        }

        let el = this.selectedElements[0];
        if (!el && this.selectedElementId) {
            el = this.root.querySelector(`#${this.selectedElementId}`);
            if (el) this.selectedElements = [el];
        }

        if (!el) {
            console.warn('[SlideLogicCore] Could not find element to update');
            return;
        }

        console.log('[SlideLogicCore] Updating element style:', { id: el.id, styles: newStyles });

        Object.entries(newStyles).forEach(([key, value]) => {
            if (key === 'innerHTML' || key === 'textContent' || key === 'content') {
                el.innerHTML = value;
            } else {
                el.style[key] = value;
            }
        });

        this.updateSelectionUI();
        this.saveHistory();
    },

    execFormat(command, value = null) {
        document.execCommand(command, false, value);
        this.saveHistory();
    },

    getSelectedZIndex() {
        const el = this.selectedElements[0];
        return el ? (parseInt(el.style.zIndex) || 0) : 0;
    },

    getMaxZIndex() {
        let max = 0;
        this.canvas.querySelectorAll('[data-selectable="true"], .element').forEach(el => {
            if (el.classList.contains('resize-handle') ||
                el.classList.contains('drag-handle') ||
                el.classList.contains('smart-guide')) return;
            const z = parseInt(el.style.zIndex) || 0;
            if (z > max) max = z;
        });
        return max;
    },

    injectElement(html) {
        const temp = document.createElement('div');
        temp.innerHTML = html.trim();
        const el = temp.firstElementChild;
        if (!el || !(el instanceof HTMLElement)) return;

        el.style.zIndex = String(this.getMaxZIndex() + 1);

        if (!el.id) el.id = `el_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
        if (!el.hasAttribute('data-selectable')) el.setAttribute('data-selectable', 'true');
        if (!el.classList.contains('element')) el.classList.add('element');
        el.style.cursor = 'move';

        this.canvas.appendChild(el);
        this.selectElement(el);
        this.saveHistory();
    },

    getSelectedElement() {
        return this.selectedElements.length > 0 ? this.selectedElements[0] : null;
    },

    getHTML() {
        // Clone and strip all editor-only artifacts so the saved HTML is clean
        const _clone = this.canvas.cloneNode(true);
        _clone.querySelectorAll('.resize-handle, .drag-handle, .smart-guide').forEach(el => el.remove());
        _clone.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
        _clone.querySelectorAll('[contenteditable]').forEach(el => el.removeAttribute('contenteditable'));
        _clone.querySelectorAll('[data-selectable]').forEach(el => el.removeAttribute('data-selectable'));
        _clone.querySelectorAll('[data-guide-key]').forEach(el => el.removeAttribute('data-guide-key'));
        _clone.querySelectorAll('*').forEach(el => {
            if (el.style && el.style.cursor === 'move') el.style.cursor = '';
        });
        return _clone.innerHTML;
    },
};
