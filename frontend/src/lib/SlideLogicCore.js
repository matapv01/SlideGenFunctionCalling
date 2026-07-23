// File: frontend/src/lib/SlideLogicCore.js
// Main entry — imports mixins and composes the SlideEditorLogic class.

import { EventHandlersMixin } from './mixins/EventHandlersMixin.js';
import { SnapGuideMixin      } from './mixins/SnapGuideMixin.js';
import { SelectionMixin      } from './mixins/SelectionMixin.js';
import { HistoryMixin        } from './mixins/HistoryMixin.js';
import { ElementAPIMixin     } from './mixins/ElementAPIMixin.js';

export class SlideEditorLogic {
    constructor(rootElement, onElementSelect, onChange, onRerenderEquations = null) {
        this.root             = rootElement;
        this.onElementSelect  = onElementSelect;
        this.onChange         = onChange;
        this.onRerenderEquations = onRerenderEquations;

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
        this.draggedElement    = null;
        this.dragStart         = null;
        this.elementsStartPos  = new Map();
        this.resizeHandle      = null;
        this.history           = [];
        this.historyIndex      = -1;
        this.currentScale      = 1;
        this._lastLoggedScale  = null;
        this.isEditingText     = false;
        this._guideTimeout    = null;
        this._inputTimer      = null;

        this.init();
    }

    init() {
        console.log('[SlideLogicCore] Initializing with root:', this.root);

        this.boundMouseDown = (e) => this.handleMouseDown(e);
        this.boundDoubleClick = (e) => this.handleDoubleClick(e);
        this.root.addEventListener('mousedown', this.boundMouseDown, true);
        this.root.addEventListener('dblclick', this.boundDoubleClick, true);

        // Listen for inline equation clicks dispatched directly from math-field elements.
        // This bypasses MathLive's Shadow DOM which can swallow mouse events.
        this.boundInlineEquationClick = (e) => {
            const mf = e.detail?.mathField;
            if (!mf) return;
            if (mf._mathfieldActive || !mf.hasAttribute?.('read-only')) return;

            // Always prioritize equation interaction over textbox selection.
            if (typeof this.exitEditMode === 'function') this.exitEditMode();
            if (typeof this.deselectAll === 'function') this.deselectAll();

            // Enter equation edit mode so caret is inside formula.
            if (typeof this.activateInlineEquationEditor === 'function') {
                this.activateInlineEquationEditor(mf);
            }

            // Keep properties panel in equation mode.
            if (typeof this.selectInlineEquationForProperties === 'function') {
                this.selectInlineEquationForProperties(mf);
            }

            e.stopPropagation?.();
        };
        this.root.addEventListener('inline-equation-click', this.boundInlineEquationClick, true);

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

        const roundedScale = Math.round(this.currentScale * 100) / 100;
        if (this._lastLoggedScale === null || Math.abs(roundedScale - this._lastLoggedScale) >= 0.05) {
            this._lastLoggedScale = roundedScale;
            console.log('[SlideLogicCore] Scale updated:', roundedScale);
        }
    }

    destroy() {
        console.log('[SlideLogicCore] Destroying...');
        if (this.boundMouseDown) {
            this.root.removeEventListener('mousedown', this.boundMouseDown, true);
        }
        if (this.boundDoubleClick) {
            this.root.removeEventListener('dblclick', this.boundDoubleClick, true);
        }
        if (this.boundInlineEquationClick) {
            this.root.removeEventListener('inline-equation-click', this.boundInlineEquationClick, true);
        }
        window.removeEventListener('mousemove', this.boundMouseMove);
        window.removeEventListener('mouseup',   this.boundMouseUp);
        if (this.boundInput) this.root.removeEventListener('input', this.boundInput, true);
        if (this._inputTimer) { clearTimeout(this._inputTimer); this._inputTimer = null; }
        if (this._guideTimeout) { clearTimeout(this._guideTimeout); this._guideTimeout = null; }
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
