// Mixin: undo/redo history management
export const HistoryMixin = {

    saveHistory(silent = false) {
        // Clone and strip transient UI state so it doesn't get baked into history snapshots
        const _clone = this.canvas.cloneNode(true);
        _clone.querySelectorAll('.smart-guide').forEach(el => el.remove());
        _clone.querySelectorAll('.selected').forEach((el) => {
            el.classList.remove('selected');
            el.querySelectorAll('.resize-handle, .drag-handle').forEach((h) => h.remove());
        });
        _clone.querySelectorAll('math-field[data-inline-equation].inline-equation-selected')
            .forEach((el) => el.classList.remove('inline-equation-selected'));
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

    resetTransientSelectionState() {
        this.canvas.querySelectorAll('.selected').forEach((el) => {
            el.classList.remove('selected');
            el.querySelectorAll('.resize-handle, .drag-handle').forEach((h) => h.remove());
        });
        this.canvas.querySelectorAll('math-field[data-inline-equation].inline-equation-selected')
            .forEach((el) => el.classList.remove('inline-equation-selected'));

        this.selectedElements = [];
        this.selectedElementId = null;
        this._selectedInlineMathField = null;
    },

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.canvas.innerHTML = this.history[this.historyIndex].html;
            this.makeElementsSelectable();
            this.resetTransientSelectionState();
            if (this.onElementSelect) this.onElementSelect(null);
            if (this.onRerenderEquations) this.onRerenderEquations();
            if (this.onChange) this.onChange();
        }
    },

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.canvas.innerHTML = this.history[this.historyIndex].html;
            this.makeElementsSelectable();
            this.resetTransientSelectionState();
            if (this.onElementSelect) this.onElementSelect(null);
            if (this.onRerenderEquations) this.onRerenderEquations();
            if (this.onChange) this.onChange();
        }
    },

    getHistoryState() {
        return {
            history: this.history,
            historyIndex: this.historyIndex,
        };
    },

    restoreHistoryState(state) {
        if (!state || !Array.isArray(state.history)) return;
        this.history = state.history;
        this.historyIndex = Math.max(0, Math.min(state.historyIndex, state.history.length - 1));
    },

    canUndo() {
        return this.historyIndex > 0;
    },

    canRedo() {
        return this.historyIndex < this.history.length - 1;
    },
};
