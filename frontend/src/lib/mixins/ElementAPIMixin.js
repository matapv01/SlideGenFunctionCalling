export const ElementAPIMixin = {

    resolveTargetElement(targetId = null) {
        let el = this.selectedElements[0] || null;
        if (el) return el;

        const id = targetId || this.selectedElementId;
        if (!id) return null;

        try {
            el = this.root.querySelector(`#${CSS.escape(id)}`);
        } catch {
            el = this.root.querySelector(`[id="${id}"]`);
        }

        if (el) this.selectedElements = [el];
        return el;
    },

    getStyleNumber(el, styleName, fallback = 0) {
        const direct = parseFloat(el.style?.[styleName]);
        if (Number.isFinite(direct)) return direct;
        const computed = parseFloat(window.getComputedStyle(el)?.[styleName]);
        return Number.isFinite(computed) ? computed : fallback;
    },

    normalizeElementForCanvas(el) {
        el.classList.remove('selected');
        el.querySelectorAll('.resize-handle, .drag-handle, .smart-guide').forEach(h => h.remove());
        el.removeAttribute('data-guide-key');
        el.querySelectorAll('[data-guide-key]').forEach(node => node.removeAttribute('data-guide-key'));

        if (!el.id) el.id = `el_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
        if (!el.classList.contains('element')) el.classList.add('element');
        if (!el.hasAttribute('data-selectable')) el.setAttribute('data-selectable', 'true');
        el.style.cursor = 'move';
    },

    deleteElement(targetId = null) {
        const el = this.resolveTargetElement(targetId);
        if (!el) return;

        el.remove();
        this.deselectAll();
        this.saveHistory();
    },

    duplicateElement(targetId = null, offsetX = 24, offsetY = 24) {
        const source = this.resolveTargetElement(targetId);
        if (!source) return null;

        const clone = source.cloneNode(true);
        this.normalizeElementForCanvas(clone);
        clone.id = `el_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;

        const left = this.getStyleNumber(source, 'left', source.offsetLeft || 0);
        const top = this.getStyleNumber(source, 'top', source.offsetTop || 0);

        if (!clone.style.position) clone.style.position = source.style.position || 'absolute';
        clone.style.left = `${left + offsetX}px`;
        clone.style.top = `${top + offsetY}px`;
        clone.style.zIndex = String(this.getMaxZIndex() + 1);

        this.canvas.appendChild(clone);
        this.selectElement(clone);
        this.saveHistory();
        return clone.id;
    },

    copySelectedElement(targetId = null) {
        const source = this.resolveTargetElement(targetId);
        if (!source) return false;

        const clone = source.cloneNode(true);
        this.normalizeElementForCanvas(clone);
        clone.removeAttribute('id');

        this.clipboardElementHTML = clone.outerHTML;
        return true;
    },

    pasteElement(offsetX = 24, offsetY = 24) {
        if (!this.clipboardElementHTML) return null;

        const temp = document.createElement('div');
        temp.innerHTML = this.clipboardElementHTML.trim();
        const el = temp.firstElementChild;
        if (!el || !(el instanceof HTMLElement)) return null;

        this.normalizeElementForCanvas(el);
        el.id = `el_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;

        const left = this.getStyleNumber(el, 'left', 0);
        const top = this.getStyleNumber(el, 'top', 0);
        if (!el.style.position) el.style.position = 'absolute';
        el.style.left = `${left + offsetX}px`;
        el.style.top = `${top + offsetY}px`;
        el.style.zIndex = String(this.getMaxZIndex() + 1);

        this.canvas.appendChild(el);
        this.selectElement(el);
        this.saveHistory();
        return el.id;
    },

    bringToFront(targetId = null) {
        const el = this.resolveTargetElement(targetId);
        if (!el) return;
        el.style.zIndex = String(this.getMaxZIndex() + 1);
        this.updateSelectionUI();
        this.emitSelectedElementData(el);
        this.saveHistory();
    },

    sendToBack(targetId = null) {
        const el = this.resolveTargetElement(targetId);
        if (!el) return;
        el.style.zIndex = '0';
        this.updateSelectionUI();
        this.emitSelectedElementData(el);
        this.saveHistory();
    },

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
