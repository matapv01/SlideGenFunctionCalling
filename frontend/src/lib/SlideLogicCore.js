// File: frontend/src/lib/SlideLogicCore.js
// Main entry — imports mixins and composes the SlideEditorLogic class.

import { EventHandlersMixin } from './mixins/EventHandlersMixin.js';
import { SnapGuideMixin      } from './mixins/SnapGuideMixin.js';
import { SelectionMixin      } from './mixins/SelectionMixin.js';
import { HistoryMixin        } from './mixins/HistoryMixin.js';
import { ElementAPIMixin     } from './mixins/ElementAPIMixin.js';

export class SlideEditorLogic {
    constructor(rootElement, onElementSelect, onChange) {
        this.root             = rootElement;
        this.onElementSelect  = onElementSelect;
        this.onChange         = onChange;

        // Prefer the stable outer wrapper produced by processHTML
        this.canvas = this.root.querySelector('.slide-bg-wrapper') ||
                      this.root.querySelector('.slide-container')  ||
                      this.root;

        // --- Internal state ---
        this.selectedElements  = [];
        this.smartGuides       = [];
        this.snapThreshold     = 8;
        this.isDragging        = false;
        this.isResizing        = false;
        this.isPreparedForDrag = false;
        this.pendingSelectElement = null;
        this.pendingSelectMode = null;
        this.draggedElement    = null;
        this.dragStart         = null;
        this.elementsStartPos  = new Map();
        this.dragPlaceholders  = new Map();
        this.resizeHandle      = null;
        this.history           = [];
        this.historyIndex      = -1;
        this.currentScale      = 1;
        this.isEditingText     = false;
        this._guideTimeout    = null;
        this._inputTimer      = null;

        this.init();
    }

    init() {
        console.log('[SlideLogicCore] Initializing with root:', this.root);

        this.root.addEventListener('mousedown', (e) => this.handleMouseDown(e), true);
        this.root.addEventListener('dblclick',  (e) => this.handleDoubleClick(e), true);

        // Real-time text-edit save: trigger saveHistory+onChange on every keystroke
        // Debounced 300ms so we don't hammer the API on every character
        this.boundInput = (e) => {
            if (!e.target || !e.target.hasAttribute('contenteditable')) return;
            if (this._inputTimer) clearTimeout(this._inputTimer);
            this._inputTimer = setTimeout(() => {
                this._inputTimer = null;
                this.saveHistory(); // triggers onChange → auto-save
            }, 300);
        };
        this.root.addEventListener('input', this.boundInput, true);

        this.boundMouseMove = (e) => this.handleMouseMove(e);
        this.boundMouseUp   = (e) => this.handleMouseUp(e);
        window.addEventListener('mousemove', this.boundMouseMove);
        window.addEventListener('mouseup',   this.boundMouseUp);

        this.applyBaseStyles();
        this.makeElementsSelectable();
        this.saveHistory(true); // silent initial snapshot
    }

    applyBaseStyles() {
        if (this.canvas) {
            this.canvas.style.position  = 'relative';
            this.canvas.style.width     = '100%';
            this.canvas.style.height    = '100%';
            this.canvas.style.minHeight = '1080px';
        }
    }

    setScale(s) {
        this.currentScale = s || 1;
        console.log('[SlideLogicCore] Scale updated:', this.currentScale);
    }

    destroy() {
        console.log('[SlideLogicCore] Destroying...');
        window.removeEventListener('mousemove', this.boundMouseMove);
        window.removeEventListener('mouseup',   this.boundMouseUp);
        if (this.boundInput) this.root.removeEventListener('input', this.boundInput, true);
        if (this._inputTimer) { clearTimeout(this._inputTimer); this._inputTimer = null; }
        if (this._guideTimeout) { clearTimeout(this._guideTimeout); this._guideTimeout = null; }
        if (this.clearDragPlaceholders) this.clearDragPlaceholders();
        this.deselectAll();
        this.clearSmartGuides();
    }
}

// Compose all mixins onto the prototype
Object.assign(
    SlideEditorLogic.prototype,
    EventHandlersMixin,
    SnapGuideMixin,
    SelectionMixin,
    HistoryMixin,
    ElementAPIMixin,
);
