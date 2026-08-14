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

    getOperationElements(targetId = null) {
        let target = null;
        const resolvedId = targetId || this.selectedElementId;

        if (resolvedId) {
            target = this.selectedElements.find(node => node.id === resolvedId) || null;
            if (!target) {
                try {
                    target = this.root.querySelector(`#${CSS.escape(resolvedId)}`);
                } catch {
                    target = this.root.querySelector(`[id="${resolvedId}"]`);
                }
            }
        }
        target ||= this.selectedElements[0] || null;
        if (!target) return [];

        if (this.selectedElements.length > 1 && this.selectedElements.includes(target)) {
            return this.selectedElements.filter(node => node && this.canvas.contains(node));
        }

        const groupId = target.dataset?.editorGroup;
        if (!groupId) return [target];
        return Array.from(this.canvas.querySelectorAll('[data-editor-group]'))
            .filter(node => node.dataset?.editorGroup === groupId);
    },

    getSelectionInfo() {
        const primary = this.getPrimarySelectedElement?.() || this.selectedElements[0] || null;
        return {
            count: this.selectedElements.length,
            selectedIds: this.selectedElements.map(node => node.id).filter(Boolean),
            groupId: primary?.dataset?.editorGroup || null,
            isGroup: !!primary?.dataset?.editorGroup && this.selectedElements.length > 1,
        };
    },

    groupSelectedElements() {
        const elements = this.selectedElements.filter(node => node && this.canvas.contains(node));
        if (elements.length < 2) return false;

        const groupId = `group_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
        elements.forEach(node => {
            node.dataset.editorGroup = groupId;
        });

        const primary = this.getPrimarySelectedElement?.() || elements[0];
        this.selectedElements = [primary, ...elements.filter(node => node !== primary)];
        this.selectedElementId = primary.id;
        this.refreshSelectionVisuals?.();
        this.emitSelectedElementData?.(primary);
        this.saveHistory();
        return true;
    },

    ungroupSelectedElements() {
        const groupIds = new Set(
            this.selectedElements
                .map(node => node?.dataset?.editorGroup)
                .filter(Boolean)
        );
        if (groupIds.size === 0) return false;

        const affected = Array.from(this.canvas.querySelectorAll('[data-editor-group]'))
            .filter(node => groupIds.has(node.dataset?.editorGroup));
        affected.forEach(node => delete node.dataset.editorGroup);

        const primary = this.getPrimarySelectedElement?.() || affected[0] || null;
        this.selectedElements = primary
            ? [primary, ...affected.filter(node => node !== primary)]
            : [];
        this.selectedElementId = primary?.id || null;
        this.refreshSelectionVisuals?.();
        if (primary) this.emitSelectedElementData?.(primary);
        this.saveHistory();
        return true;
    },

    deleteElement(targetId = null) {
        const elements = this.getOperationElements(targetId);
        if (elements.length === 0) return [];

        const deletedIds = elements.map(node => node.id).filter(Boolean);
        elements.forEach(node => node.remove());
        this.deselectAll();
        this.saveHistory();
        return deletedIds;
    },

    duplicateElement(targetId = null, offsetX = 24, offsetY = 24) {
        const sources = this.getOperationElements(targetId);
        if (sources.length === 0) return [];

        const originalGroupIds = new Set(sources.map(node => node.dataset?.editorGroup).filter(Boolean));
        const newGroupId = originalGroupIds.size === 1 && sources.length > 1
            ? `group_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`
            : null;
        const baseZ = this.getMaxZIndex() + 1;
        const clones = sources.map((source, index) => {
            const clone = source.cloneNode(true);
            this.normalizeElementForCanvas(clone);
            clone.id = `el_${Date.now()}_${index}_${Math.random().toString(36).slice(2, 7)}`;
            if (newGroupId) clone.dataset.editorGroup = newGroupId;
            else delete clone.dataset.editorGroup;

            const left = this.getStyleNumber(source, 'left', source.offsetLeft || 0);
            const top = this.getStyleNumber(source, 'top', source.offsetTop || 0);
            if (!clone.style.position) clone.style.position = source.style.position || 'absolute';
            clone.style.left = `${left + offsetX}px`;
            clone.style.top = `${top + offsetY}px`;
            clone.style.zIndex = String(baseZ + index);
            this.canvas.appendChild(clone);
            return clone;
        });

        this.selectedElements = clones;
        this.selectedElementId = clones[0].id;
        this.refreshSelectionVisuals?.();
        this.emitSelectedElementData?.(clones[0]);
        this.saveHistory();
        return clones.map(node => node.id);
    },

    copySelectedElement(targetId = null) {
        const sources = this.getOperationElements(targetId);
        if (sources.length === 0) return false;

        this.clipboardElementsHTML = sources.map((source) => {
            const clone = source.cloneNode(true);
            this.normalizeElementForCanvas(clone);
            clone.removeAttribute('id');
            return clone.outerHTML;
        });
        return true;
    },

    pasteElement(offsetX = 24, offsetY = 24) {
        const htmlItems = this.clipboardElementsHTML || [];
        if (htmlItems.length === 0) return [];

        const groupIdMap = new Map();
        const baseZ = this.getMaxZIndex() + 1;
        const pasted = htmlItems.map((html, index) => {
            const temp = document.createElement('div');
            temp.innerHTML = html.trim();
            const el = temp.firstElementChild;
            if (!el || !(el instanceof HTMLElement)) return null;

            this.normalizeElementForCanvas(el);
            el.id = `el_${Date.now()}_${index}_${Math.random().toString(36).slice(2, 7)}`;
            const oldGroupId = el.dataset.editorGroup;
            if (oldGroupId) {
                if (!groupIdMap.has(oldGroupId)) {
                    groupIdMap.set(oldGroupId, `group_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`);
                }
                el.dataset.editorGroup = groupIdMap.get(oldGroupId);
            }

            const left = this.getStyleNumber(el, 'left', 0);
            const top = this.getStyleNumber(el, 'top', 0);
            if (!el.style.position) el.style.position = 'absolute';
            el.style.left = `${left + offsetX}px`;
            el.style.top = `${top + offsetY}px`;
            el.style.zIndex = String(baseZ + index);
            this.canvas.appendChild(el);
            return el;
        }).filter(Boolean);
        if (pasted.length === 0) return [];

        this.selectedElements = pasted;
        this.selectedElementId = pasted[0].id;
        this.refreshSelectionVisuals?.();
        this.emitSelectedElementData?.(pasted[0]);
        this.saveHistory();
        return pasted.map(node => node.id);
    },

    bringToFront(targetId = null) {
        const elements = this.getOperationElements(targetId);
        if (elements.length === 0) return;
        const baseZ = this.getMaxZIndex() + 1;
        elements.forEach((node, index) => { node.style.zIndex = String(baseZ + index); });
        this.updateSelectionUI();
        this.emitSelectedElementData(elements[0]);
        this.saveHistory();
    },

    sendToBack(targetId = null) {
        const elements = this.getOperationElements(targetId);
        if (elements.length === 0) return;
        elements.forEach((node, index) => { node.style.zIndex = String(index); });
        this.updateSelectionUI();
        this.emitSelectedElementData(elements[0]);
        this.saveHistory();
    },

    bringForward(targetId = null) {
        const elements = this.getOperationElements(targetId);
        if (elements.length === 0) return;
        elements.forEach(node => {
            node.style.zIndex = String((parseInt(node.style.zIndex, 10) || 0) + 1);
        });
        this.emitSelectedElementData(elements[0]);
        this.saveHistory();
    },

    sendBackward(targetId = null) {
        const elements = this.getOperationElements(targetId);
        if (elements.length === 0) return;
        elements.forEach(node => {
            node.style.zIndex = String(Math.max(0, (parseInt(node.style.zIndex, 10) || 0) - 1));
        });
        this.emitSelectedElementData(elements[0]);
        this.saveHistory();
    },

    updateSelectedElementStyle(newStyles, targetId = null) {
        console.log('[SlideLogicCore][Properties] updateSelectedElementStyle called', {
            targetId,
            selectedElementId: this.selectedElementId || null,
            selectedIds: this.selectedElements.map((node) => node?.id || null),
            styles: newStyles,
        });

        if (!this.selectedElements.length && !this.selectedElementId && !targetId) {
            console.warn('[SlideLogicCore] No element selected to update');
            return;
        }

        let el = this.selectedElements[0];
        if (el && (!el.isConnected || !this.root.contains(el))) {
            el = null;
        }

        const resolvedId = targetId || this.selectedElementId;
        if (!el && resolvedId) {
            try {
                el = this.root.querySelector(`#${CSS.escape(resolvedId)}`);
            } catch {
                el = this.root.querySelector(`[id="${resolvedId}"]`);
            }
            if (el) {
                this.selectedElements = [el];
                this.selectedElementId = el.id;
            }
        }

        if (!el) {
            console.warn('[SlideLogicCore][Properties] Could not find element to update', {
                targetId,
                selectedElementId: this.selectedElementId || null,
            });
            return;
        }

        const hasPositionalUpdate =
            Object.prototype.hasOwnProperty.call(newStyles, 'left') ||
            Object.prototype.hasOwnProperty.call(newStyles, 'top') ||
            Object.prototype.hasOwnProperty.call(newStyles, 'width') ||
            Object.prototype.hasOwnProperty.call(newStyles, 'height');

        if (hasPositionalUpdate) {
            const computedPosition = window.getComputedStyle(el).position;
            if (computedPosition !== 'absolute') {
                const bounds = this.getElementBounds
                    ? this.getElementBounds(el)
                    : { left: el.offsetLeft, top: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight };

                el.style.setProperty('position', 'absolute', 'important');
                if (!Object.prototype.hasOwnProperty.call(newStyles, 'left')) {
                    el.style.left = `${bounds.left}px`;
                }
                if (!Object.prototype.hasOwnProperty.call(newStyles, 'top')) {
                    el.style.top = `${bounds.top}px`;
                }
                if (!Object.prototype.hasOwnProperty.call(newStyles, 'width')) {
                    el.style.width = `${bounds.width}px`;
                }
                if (!Object.prototype.hasOwnProperty.call(newStyles, 'height')) {
                    el.style.height = `${bounds.height}px`;
                }
            }
        }

        console.log('[SlideLogicCore][Properties] Applying styles to element', {
            id: el.id,
            computedPosition: window.getComputedStyle(el).position,
            styles: newStyles,
        });

        Object.entries(newStyles).forEach(([key, value]) => {
            if (key === 'innerHTML' || key === 'textContent' || key === 'content') {
                el.innerHTML = value;
            } else if (key === 'mediaSrc') {
                const media = el.matches('img, video') ? el : el.querySelector('img, video');
                if (media) media.setAttribute('src', String(value || ''));
            } else {
                el.style[key] = value;
            }
        });

        this.updateSelectionUI();
        if (this.emitSelectedElementData) this.emitSelectedElementData(el);
        console.log('[SlideLogicCore][Properties] Applied styles result', {
            id: el.id,
            left: el.style.left || null,
            top: el.style.top || null,
            width: el.style.width || null,
            height: el.style.height || null,
            transform: el.style.transform || null,
            position: el.style.position || null,
        });
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

    getCursorPositionInCanvas() {
        const selection = window.getSelection();
        if (!selection || selection.rangeCount === 0) {
            console.warn('[SlideLogicCore] No selection found for cursor position');
            return null;
        }

        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        
        if (!this.canvas) {
            console.warn('[SlideLogicCore] Canvas not available');
            return null;
        }

        const canvasRect = this.canvas.getBoundingClientRect();
        
        // Calculate position relative to canvas
        const x = rect.left - canvasRect.left;
        const y = rect.top - canvasRect.top;
        
        // Handle collapsed range (cursor position) vs selection
        const isCollapsed = range.collapsed;
        
        console.log('[SlideLogicCore] Cursor position calculated', {
            x,
            y,
            isCollapsed,
            rectLeft: rect.left,
            rectTop: rect.top,
            canvasLeft: canvasRect.left,
            canvasTop: canvasRect.top,
        });

        return { x, y, isCollapsed, range, canvasRect };
    },
};
