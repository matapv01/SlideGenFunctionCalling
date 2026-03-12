// Mixin: undo/redo history management
export const HistoryMixin = {

    saveHistory(silent = false) {
        // Clone and strip transient guide elements so they don't get baked into history
        const _clone = this.canvas.cloneNode(true);
        _clone.querySelectorAll('.smart-guide').forEach(el => el.remove());
        const currentHTML = _clone.innerHTML;

        // Skip if nothing changed since the last snapshot
        if (this.history.length > 0 && this.history[this.historyIndex]?.html === currentHTML) {
            return;
        }

        this.history = this.history.slice(0, this.historyIndex + 1);
        this.history.push({ timestamp: Date.now(), html: currentHTML });
        this.historyIndex++;

        // Cap history at 50 entries
        if (this.history.length > 50) {
            this.history.shift();
            this.historyIndex--;
        }

        if (!silent && this.onChange) this.onChange();
    },

    /**
     * Re-select an element by ID after undo/redo so the React properties panel
     * refreshes to reflect the restored DOM values.
     */
    reselectById(id) {
        if (!id) return;
        const el = this.canvas.querySelector(`#${CSS.escape(id)}`);
        if (el) this.selectElement(el);
    },

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.canvas.innerHTML = this.history[this.historyIndex].html;
            this.makeElementsSelectable();
            this.deselectAll();
            if (this.onChange) this.onChange();
        }
    },

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.canvas.innerHTML = this.history[this.historyIndex].html;
            this.makeElementsSelectable();
            this.deselectAll();
            if (this.onChange) this.onChange();
        }
    },
};
