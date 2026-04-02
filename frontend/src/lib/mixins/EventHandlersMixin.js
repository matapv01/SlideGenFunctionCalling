// Mixin: mouse event handlers (mousedown, mousemove, mouseup, dblclick)
export const EventHandlersMixin = {

    /**
     * Normalize event target to handle Shadow DOM (e.g., MathLive's math-field)
     * @param {EventTarget} target - The raw event target
     * @param {Event} event - The original event (optional, for composedPath)
     */
    normalizeEventTarget(target, event = null) {
        // If we have the event, use composedPath to find math-field across shadow boundaries
        if (event && typeof event.composedPath === 'function') {
            const path = event.composedPath();
            // Debug: log the path to see structure
            console.log('[SlideLogicCore] composedPath tags:', path.slice(0, 10).map(el => el?.tagName || el?.nodeName || 'unknown'));
            
            for (const el of path) {
                if (el && el.tagName === 'MATH-FIELD') {
                    console.log('[SlideLogicCore] Found MATH-FIELD in composedPath');
                    return el;
                }
            }

            // Some MathLive internals may expose only shadow children in path.
            // In that case, recover the structured equation wrapper directly.
            for (const el of path) {
                if (el instanceof HTMLElement && el.dataset?.type === 'equation') {
                    console.log('[SlideLogicCore] Found equation wrapper in composedPath:', el.id || null);
                    return el;
                }
            }

            for (const el of path) {
                if (el instanceof HTMLElement && el.hasAttribute?.('data-inline-equation')) {
                    console.log('[SlideLogicCore] Found inline equation in composedPath');
                    return el;
                }
            }
        }
        
        if (target instanceof HTMLElement) {
            // Fallback: check if target is inside a math-field
            const mathField = target.closest?.('math-field');
            if (mathField) return mathField;
            return target;
        }
        if (target instanceof Text) return target.parentElement;
        return null;
    },

    ensureElementAbsolutePosition(el, providedBounds = null) {
        if (!el) return null;

        const bounds = providedBounds || (this.getElementBounds
            ? this.getElementBounds(el)
            : { left: el.offsetLeft, top: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight });

        const computedPosition = window.getComputedStyle(el).position;
        if (computedPosition !== 'absolute') {
            console.log('[SlideLogicCore][Layout] Converting element to absolute', {
                id: el.id || null,
                computedPosition,
                left: bounds.left,
                top: bounds.top,
                width: bounds.width,
                height: bounds.height,
            });
            el.style.setProperty('position', 'absolute', 'important');
            el.style.left = `${bounds.left}px`;
            el.style.top = `${bounds.top}px`;
            el.style.width = `${bounds.width}px`;
            el.style.height = `${bounds.height}px`;
        }

        return bounds;
    },

    freezeSelectableSiblingsLayout(targetElement) {
        if (!targetElement || !(targetElement instanceof HTMLElement)) return;

        const parent = targetElement.parentElement;
        if (!parent) return;

        const siblingsToFreeze = Array.from(parent.children)
            .filter((node) => node instanceof HTMLElement)
            .filter((node) =>
                node.hasAttribute('data-selectable') || node.classList.contains('element')
            )
            .filter((node) => !this.isCanvasChromeElement || !this.isCanvasChromeElement(node));

        if (siblingsToFreeze.length === 0) return;

        // Snapshot all bounds first so converting one element cannot shift others.
        const snapshots = siblingsToFreeze.map((el) => {
            const bounds = this.getElementBounds
                ? this.getElementBounds(el)
                : { left: el.offsetLeft, top: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight };
            return { el, bounds };
        });

        console.log('[SlideLogicCore][Layout] Freezing sibling layout before drag/update', {
            targetId: targetElement.id || null,
            parentTag: parent.tagName,
            siblingCount: snapshots.length,
            siblingIds: snapshots.map(({ el }) => el.id || null),
        });

        snapshots.forEach(({ el, bounds }) => {
            this.ensureElementAbsolutePosition(el, bounds);
        });
    },

    handleDoubleClick(e) {
        const target = this.normalizeEventTarget(e.target, e);
        if (!target) return;

        console.log('[SlideLogicCore] handleDoubleClick', {
            targetTag: target.tagName,
            targetId: target.id,
            targetClasses: target.className,
        });

        // ── Check if clicking directly on math-field ───────────────────────────
        // Use Properties panel as the primary equation editing flow.
        if (target.tagName === 'MATH-FIELD') {
            console.log('[SlideLogicCore] Clicked on math-field directly, selecting for properties');
            // Find parent equation element if exists
            let eqParent = target.parentElement;
            while (eqParent && eqParent !== this.root) {
                if (eqParent.dataset?.type === 'equation') break;
                eqParent = eqParent.parentElement;
            }
            
            if (eqParent && eqParent.dataset?.type === 'equation') {
                this.activateEquationEditor(eqParent);
            } else {
                // Inline math-field inside text block: focus cursor in equation box.
                this.activateInlineEquationEditor(target);
            }
            e.preventDefault();
            e.stopPropagation();
            return;
        }

        // ── Equation: activate MathLive field ───────────────────────────────
        let eqElement = target;
        while (eqElement && eqElement !== this.root) {
            if (eqElement.dataset?.type === 'equation') break;
            eqElement = eqElement.parentElement;
        }
        if (eqElement && eqElement !== this.root && eqElement.dataset.type === 'equation') {
            console.log('[SlideLogicCore] Found equation element, selecting', {
                eqId: eqElement.id,
                dataLatex: eqElement.dataset.latex,
            });
            this.activateEquationEditor(eqElement);
            e.preventDefault();
            e.stopPropagation();
            return;
        }

        // ── Text contenteditable: existing behavior ──────────────────────────
        const textElement = target.closest('[contenteditable]');
        if (textElement && (textElement.classList.contains('element') || textElement.hasAttribute('data-selectable'))) {
            this.isEditingText = true;
            textElement.style.cursor = 'text';
            textElement.focus();

            this.hideSelectionUI();

            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(textElement);
            range.collapse(false);
            selection.removeAllRanges();
            selection.addRange(range);

            e.preventDefault();
            e.stopPropagation();
        }
    },

    activateEquationEditor(el) {
        console.log('[SlideLogicCore] activateEquationEditor called', {
            elId: el?.id,
            tagName: el?.tagName,
            dataType: el?.dataset?.type,
            mathfieldActive: el?._mathfieldActive,
            hasMathField: !!el?.querySelector?.('math-field'),
        });

        if (el._mathfieldActive) return;

        import('mathlive').then((ml) => {
            const fontsUrl = window.location.origin + '/fonts';
            if (ml.setOptions) ml.setOptions({ fontsDirectory: fontsUrl });
            else if (window.MathLive?.setOptions) window.MathLive.setOptions({ fontsDirectory: fontsUrl });
            
            console.log('[SlideLogicCore] MathLive imported, font path:', fontsUrl);
            el._mathfieldActive = true;
            this.isEditingText = true;
            this.selectElement(el);
            this.hideSelectionUI();

            // Keep the existing <math-field> if present; otherwise create it.
            let mf = el.querySelector('math-field');
            if (!mf) {
                console.log('[SlideLogicCore] Creating new math-field element');
                mf = document.createElement('math-field');
                mf.value = el.dataset.latex || '';
                el.innerHTML = '';
                el.appendChild(mf);
            } else {
                console.log('[SlideLogicCore] Using existing math-field');
            }

            console.log('[SlideLogicCore] Math-field state:', {
                tagName: mf.tagName,
                value: mf.value,
                parentId: el.id,
            });

            // Hide selection overlay to allow interaction with MathLive
            const overlay = el.querySelector('.equation-overlay');
            if (overlay) overlay.style.display = 'none';

            // Ensure edit mode, keep equation tool in Properties as primary input
            mf.removeAttribute('read-only');
            mf.mathVirtualKeyboardPolicy = 'manual';
            mf.style.pointerEvents = 'auto';
            mf.style.cursor = 'text';

            // Attach handlers only once per equation element.
            if (!mf._equationInputHandler) {
                const onInput = () => {
                    el.dataset.latex = mf.value;
                    mf.setAttribute('value', mf.value);
                    if (this._inputTimer) clearTimeout(this._inputTimer);
                    this._inputTimer = setTimeout(() => {
                        this._inputTimer = null;
                        this.saveHistory();
                    }, 300);
                };
                mf._equationInputHandler = onInput;
                mf.addEventListener('input', onInput);
            }

            if (!mf._equationFocusOutHandler) {
                const onFocusOut = () => {
                    setTimeout(() => {
                        if (el._mathfieldActive && !mf.hasFocus?.()) {
                            this.exitEquationEditor(el);
                        }
                    }, 150);
                };
                mf._equationFocusOutHandler = onFocusOut;
                mf.addEventListener('focusout', onFocusOut);
            }

            mf.focus();
        }).catch(() => {
            el._mathfieldActive = false;
            this.isEditingText = false;
        });
    },

    activateInlineEquationEditor(mf) {
        console.log('[SlideLogicCore] activateInlineEquationEditor triggered for:', mf);
        if (mf._mathfieldActive) return;

        import('mathlive').then((ml) => {
            const fontsUrl = window.location.origin + '/fonts';
            if (ml.setOptions) ml.setOptions({ fontsDirectory: fontsUrl });
            else if (window.MathLive?.setOptions) window.MathLive.setOptions({ fontsDirectory: fontsUrl });
            
            console.log('[SlideLogicCore] MathLive imported for inline, font path:', fontsUrl);
            // Clear selected textbox/frame so only equation is highlighted
            this.root.querySelectorAll?.('.selected').forEach((el) => {
                el.classList.remove('selected');
                el.querySelectorAll?.('.resize-handle, .drag-handle').forEach((h) => h.remove());
            });
            this.selectedElements = [];
            this.selectedElementId = null;

            mf._mathfieldActive = true;
            this.isEditingText = true;
            this.hideSelectionUI();

            mf.removeAttribute('read-only');
            mf.mathVirtualKeyboardPolicy = 'manual';
            mf.style.pointerEvents = 'auto';
            mf.style.cursor = 'text';

            // Emit equation data to PropertiesPanel so it shows the equation editor tool
            if (this.onElementSelect) {
                const computedStyle = window.getComputedStyle(mf);
                const latex = mf.value || mf.textContent || '';
                this.onElementSelect({
                    id: mf.id || ('inline_mf_' + Date.now()),
                    tagName: 'MATH-FIELD',
                    dataType: 'equation',
                    type: 'equation',
                    innerHTML: mf.innerHTML,
                    textContent: latex,
                    content: latex,
                    x: 0, y: 0, width: 0, height: 0,
                    style: {
                        color: computedStyle.color || '#333333',
                        backgroundColor: 'transparent',
                        fontSize: parseFloat(computedStyle.fontSize) || 32,
                        fontFamily: 'inherit',
                        fontWeight: 'normal',
                        fontStyle: 'normal',
                        textDecoration: 'none',
                        textAlign: 'center',
                        left: 0, top: 0, width: 0, height: 0,
                        position: 'static',
                        zIndex: 0,
                        opacity: 1,
                    },
                    // Reference to the actual math-field for Insert Math actions
                    _inlineMathField: mf,
                });
            }

            if (!mf._equationInputHandler) {
                const onInput = () => {
                    mf.setAttribute('value', mf.value);
                    if (this._inputTimer) clearTimeout(this._inputTimer);
                    this._inputTimer = setTimeout(() => {
                        this._inputTimer = null;
                        this.saveHistory();
                    }, 300);
                };
                mf._equationInputHandler = onInput;
                mf.addEventListener('input', onInput);
            }

            if (!mf._equationFocusOutHandler) {
                const onFocusOut = () => {
                    setTimeout(() => {
                        if (mf._mathfieldActive && !mf.hasFocus?.()) {
                            mf._mathfieldActive = false;
                            this.isEditingText = false;
                            mf.setAttribute('read-only', 'true');
                            mf.style.cursor = 'pointer';
                            const activeEl = document.activeElement;
                            const inPropertiesPanel = !!(activeEl && activeEl.closest?.('[data-properties-panel="true"]'));

                            // Keep selection only while interacting with Properties panel tools.
                            // Otherwise clear stale inline selection so blue box does not stick.
                            if (this._selectedInlineMathField === mf && inPropertiesPanel) {
                                this.selectInlineEquationForProperties(mf);
                            } else if (this._selectedInlineMathField === mf) {
                                mf.classList?.remove('inline-equation-selected');
                                this._selectedInlineMathField = null;
                                if (this.onElementSelect) this.onElementSelect(null);
                            }
                        }
                    }, 150);
                };
                mf._equationFocusOutHandler = onFocusOut;
                mf.addEventListener('focusout', onFocusOut);
            }

            mf.focus();
        }).catch(() => {
            mf._mathfieldActive = false;
            this.isEditingText = false;
        });
    },

    // Keep equation editing UX inside Properties panel (Insert Math), including inline equations.
    selectInlineEquationForProperties(mf) {
        if (!mf || !this.onElementSelect) return;
        // Remove textbox selected frame so it doesn't overlap with inline equation frame
        this.root.querySelectorAll?.('.selected').forEach((el) => {
            el.classList.remove('selected');
            el.querySelectorAll?.('.resize-handle, .drag-handle').forEach((h) => h.remove());
        });
        this.selectedElements = [];
        this.selectedElementId = null;

        // Clear previous visual selection
        this.root.querySelectorAll?.('math-field[data-inline-equation].inline-equation-selected')
            .forEach((el) => el.classList.remove('inline-equation-selected'));
        mf.classList.add('inline-equation-selected');

        const computedStyle = window.getComputedStyle(mf);
        const latex = mf.value || mf.textContent || '';
        this._selectedInlineMathField = mf;
        this.onElementSelect({
            id: mf.id || ('inline_mf_' + Date.now()),
            tagName: 'MATH-FIELD',
            dataType: 'equation',
            type: 'equation',
            innerHTML: mf.innerHTML,
            textContent: latex,
            content: latex,
            x: 0, y: 0, width: 0, height: 0,
            style: {
                color: computedStyle.color || '#333333',
                backgroundColor: 'transparent',
                fontSize: parseFloat(computedStyle.fontSize) || 32,
                fontFamily: 'inherit',
                fontWeight: 'normal',
                fontStyle: 'normal',
                textDecoration: 'none',
                textAlign: 'center',
                left: 0, top: 0, width: 0, height: 0,
                position: 'static',
                zIndex: 0,
                opacity: 1,
            },
            _inlineMathField: mf,
        });
    },

    exitEquationEditor(el) {
        if (!el || !el._mathfieldActive) return;

        const mf = el.querySelector('math-field');
        if (mf) {
            // Capture final LaTeX before blur.
            const prevLatex = el.dataset.latex;
            const nextLatex = mf.value || el.dataset.latex || '';
            if (nextLatex !== el.dataset.latex) {
                el.dataset.latex = nextLatex;
            }

            // Only unfocus: keep MathLive field in place.
            try { mf.blur?.(); } catch {}

            // If user changed LaTeX but debounce hasn't fired yet, persist it.
            if (prevLatex !== nextLatex) {
                this.saveHistory();
            }

            mf.style.pointerEvents = 'none';

            // Show selection overlay again
            const overlay = el.querySelector('.equation-overlay');
            if (overlay) overlay.style.display = 'block';
        }

        el._mathfieldActive = false;
        this.isEditingText = false;
        el.style.cursor = 'move';

        // Re-show selection handles after unfocus.
        const selected = this.root.querySelector('.selected');
        if (selected) {
            selected.querySelectorAll('.resize-handle, .drag-handle')
                .forEach(h => h.style.display = '');
        }
    },

    handleMouseDown(e) {
        const target = this.normalizeEventTarget(e.target, e);
        if (!target) return;

        console.log('[SlideLogicCore][Drag] MouseDown', {
            targetTag: target.tagName,
            targetId: target.id || null,
            targetClasses: target.className || null,
            selectedIds: this.selectedElements.map((el) => el.id || null),
            isEditingText: this.isEditingText,
            clientX: e.clientX,
            clientY: e.clientY,
        });

        // If guides are lingering from a previous drag, clear them immediately
        if (this._guideTimeout) { clearTimeout(this._guideTimeout); this._guideTimeout = null; }
        this.clearSmartGuides();

        // If an inline equation editor is active, ANY click outside that exact equation
        // should drop caret/edit mode immediately.
        const activeInlineMf = this._selectedInlineMathField;
        if (activeInlineMf && activeInlineMf._mathfieldActive) {
            const path = (typeof e.composedPath === 'function') ? e.composedPath() : [];
            const clickedInsideSameInline = path.includes(activeInlineMf) || target === activeInlineMf;
            if (!clickedInsideSameInline) {
                try { activeInlineMf.blur?.(); } catch {}
                activeInlineMf._mathfieldActive = false;
                activeInlineMf.setAttribute('read-only', 'true');
                activeInlineMf.style.cursor = 'pointer';
                this.isEditingText = false;
                activeInlineMf.classList?.remove('inline-equation-selected');
                this._selectedInlineMathField = null;
            }
        }

        // Highest priority: clicking inline equation always switches active/selected target
        // to that exact equation (clear previous one first).
        if (target.tagName === 'MATH-FIELD' && target.hasAttribute('data-inline-equation')) {
            const prevInline = this._selectedInlineMathField;
            if (prevInline && prevInline !== target) {
                try { prevInline.blur?.(); } catch {}
                prevInline._mathfieldActive = false;
                prevInline.setAttribute?.('read-only', 'true');
                prevInline.classList?.remove('inline-equation-selected');
            }

            this.exitEditMode?.();
            this.deselectAll?.();
            this.selectInlineEquationForProperties(target);

            // If not active yet, enter edit mode so caret is in this equation.
            if (!target._mathfieldActive || target.hasAttribute('read-only')) {
                this.activateInlineEquationEditor(target);
            }

            this._suppressNextTextSelection = true;
            e.stopPropagation();
            return;
        }

        if (this._suppressNextTextSelection) {
            this._suppressNextTextSelection = false;
            return;
        }

        // Allow ongoing text/equation editing to continue unless clicking outside
        if (this.isEditingText) {
            // Check if click is inside an active equation editor
            const activeEqEl = this.selectedElements.find?.(sel => sel._mathfieldActive);
            if (activeEqEl) {
                let clickedEl = target;
                while (clickedEl && clickedEl !== this.root) {
                    if (clickedEl === activeEqEl) return; // click inside equation — let MathLive handle
                    clickedEl = clickedEl.parentElement;
                }
                // Click outside: just unfocus equation, then continue normal selection.
                this.exitEquationEditor(activeEqEl);
                return;
            }

            let clickedElement = target;
            let isClickingEditableElement = false;
            while (clickedElement && clickedElement !== this.root) {
                if (clickedElement.hasAttribute('contenteditable') && this.selectedElements.includes(clickedElement)) {
                    isClickingEditableElement = true;
                    break;
                }
                clickedElement = clickedElement.parentElement;
            }
            // Keep text edit mode active, but continue handling click so inline formulas
            // inside the text block can still be selected/converted.
            if (!isClickingEditableElement) this.exitEditMode();
        }

        const isDragHandle  = target.classList && target.classList.contains('drag-handle');
        const isResizeHandle = target.classList && target.classList.contains('resize-handle');
        const isMultiSelectIntent = e.shiftKey || e.ctrlKey || e.metaKey;
        void isMultiSelectIntent;

        // Click on canvas background → deselect
        const isCanvasBackground = !isResizeHandle && !isDragHandle && (
            target.classList.contains('slide-bg-wrapper') ||
            target.classList.contains('slide-container') ||
            target.classList.contains('slide-inner-container') ||
            target.classList.contains('outer-wrapper') ||
            target.classList.contains('content-wrapper') ||
            target.classList.contains('wrapper') ||
            target.classList.contains('scale-container') ||
            target.classList.contains('slide-wrapper')
        );

        if (isCanvasBackground) {
            this.root.querySelectorAll?.('math-field[data-inline-equation].inline-equation-selected')
                .forEach((el) => el.classList.remove('inline-equation-selected'));
            this._selectedInlineMathField = null;
            this.deselectAll();
            return;
        }

        // Fallback: if user clicks a text node containing Unicode-style formula
        // (e.g. ax² + bx + c = 0), convert that snippet to inline math-field
        // so Properties equation tool can edit it.
        const clickableText = (target.closest && target.closest('[contenteditable="true"]')) || null;
        if (clickableText && clickableText instanceof HTMLElement) {
            const raw = clickableText.textContent || '';
            const hasUnicodeFormula = /[₀-₉⁰¹²³⁴⁵⁶⁷⁸⁹√∞≤≥≠±]/.test(raw) && /[=+\-*]/.test(raw);
            if (hasUnicodeFormula && !clickableText.querySelector('math-field[data-inline-equation]')) {
                const SUP = { '⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9','ⁿ':'n' };
                const SUB = { '₀':'0','₁':'1','₂':'2','₃':'3','₄':'4','₅':'5','₆':'6','₇':'7','₈':'8','₉':'9' };
                const toLatex = (s) => {
                    let out = s;
                    out = out.replace(/([A-Za-z0-9\)\]])([⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ]+)/g, (_, b, sup) => `${b}^${[...sup].map(c => SUP[c] || c).join('')}`);
                    out = out.replace(/([A-Za-z0-9\)\]])([₀₁₂₃₄₅₆₇₈₉]+)/g, (_, b, sub) => `${b}_${[...sub].map(c => SUB[c] || c).join('')}`);
                    out = out.replace(/√\s*([A-Za-z0-9_]+)/g, String.raw`\sqrt{$1}`);
                    return out;
                };

                const allTextNodes = [];
                const walker = document.createTreeWalker(clickableText, NodeFilter.SHOW_TEXT);
                let n = walker.nextNode();
                while (n) {
                    allTextNodes.push(n);
                    n = walker.nextNode();
                }

                for (const textNode of allTextNodes) {
                    const source = textNode.nodeValue || '';
                    const m = source.match(/[A-Za-z0-9₀-₉⁰¹²³⁴⁵⁶⁷⁸⁹\(\)\s+\-*=√∞≤≥≠±]{3,}/);
                    if (!m) continue;

                    const formula = m[0].trim();
                    const latex = toLatex(formula);
                    const mf = document.createElement('math-field');
                    mf.setAttribute('value', latex);
                    mf.setAttribute('read-only', 'true');
                    mf.setAttribute('data-inline-equation', 'true');
                    mf.style.display = 'inline-block';
                    mf.style.verticalAlign = 'middle';
                    mf.style.cursor = 'pointer';
                    mf.style.border = 'none';
                    mf.style.background = 'transparent';
                    mf.style.fontSize = 'inherit';
                    mf.style.color = 'inherit';

                    const frag = document.createDocumentFragment();
                    const idx = source.indexOf(formula);
                    if (idx > 0) frag.appendChild(document.createTextNode(source.slice(0, idx)));
                    frag.appendChild(mf);
                    if (idx + formula.length < source.length) frag.appendChild(document.createTextNode(source.slice(idx + formula.length)));
                    textNode.parentNode?.replaceChild(frag, textNode);

                    this.selectInlineEquationForProperties(mf);
                    e.preventDefault();
                    e.stopPropagation();
                    return;
                }
            }
        }

        // Special handling for clicking on math-field (inside equation element OR inline in text)
        // math-field may not have data-selectable, but its parent equation div does
        if (target.tagName === 'MATH-FIELD') {
            // Check if it's an inline equation in text
            const isInlineEquation = target.hasAttribute('data-inline-equation');
            
            if (isInlineEquation) {
                // Inline equation in text: enter edit mode with cursor
                console.log('[SlideLogicCore] Click on inline math-field, activating editor');
                this.activateInlineEquationEditor(target);
                this.selectInlineEquationForProperties(target);
                e.preventDefault();
                e.stopPropagation();
                
                return;
            }
            
            // Standard equation element: find parent and select it
            let eqParent = target.parentElement;
            while (eqParent && eqParent !== this.root) {
                if (eqParent.dataset?.type === 'equation' && eqParent.dataset?.selectable === 'true') {
                    console.log('[SlideLogicCore] Click on math-field, selecting parent equation:', eqParent.id);
                    this.activateEquationEditor(eqParent);
                    e.preventDefault();
                    e.stopPropagation();
                    return;
                }
                eqParent = eqParent.parentElement;
            }
        }

        let targetElement = target.closest('[data-selectable="true"]');
        if ((isResizeHandle || isDragHandle) && !targetElement) {
            // Handles always belong to a selectable parent; if not, ignore.
            return;
        }

        // Allow ongoing text editing to continue unless clicking outside
        if (this.isEditingText) {
            const clickedElement = target.closest('[contenteditable]');
            const isClickingEditableElement = !!(
                clickedElement &&
                clickedElement.hasAttribute('contenteditable') &&
                this.selectedElements.includes(clickedElement)
            );
            // Keep text edit mode active, but continue handling click so inline formulas
            // inside the text block can still be selected/converted.
            if (!isClickingEditableElement) this.exitEditMode();
        }

        if (!targetElement) {
            this.deselectAll();
            return;
        }

        const normalizedTarget = targetElement.closest('[data-selectable="true"]');
        if (!normalizedTarget || !this.canvas.contains(normalizedTarget)) {
            this.deselectAll();
            return;
        }
        targetElement = normalizedTarget;

        // RESIZE: grab handle info and prepare
        if (isResizeHandle && this.selectedElements.length > 0) {
            const el = this.selectedElements[0];
            this.isResizing = true;
            this.resizeHandle = target.classList[1]; // e.g. 'tl', 'tr', 'bl', 'br'
            this.dragStart = { x: e.clientX, y: e.clientY };

            // Imported text blocks often include max-width/max-height (inline or class CSS),
            // which clamps growth while resizing. Explicitly remove these constraints.
            el.style.setProperty('max-width', 'none', 'important');
            el.style.setProperty('max-height', 'none', 'important');

            // Freeze ALL selectable siblings to absolute so resizing one
            // element doesn't cause layout reflow in CSS flex/grid layouts.
            this.freezeSelectableSiblingsLayout(el);

            let bounds = this.getElementBounds
                ? this.getElementBounds(el)
                : { left: el.offsetLeft, top: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight };

            bounds = this.ensureElementAbsolutePosition(el, bounds) || bounds;
            this.elementsStartPos.clear();
            this.elementsStartPos.set(el, {
                x: bounds.left,
                y: bounds.top,
                width: bounds.width,
                height: bounds.height,
            });
            e.preventDefault();
            e.stopPropagation();
            return;
        }

        const isAlreadySelected = this.selectedElements.includes(targetElement);

        // Not yet selected → defer selection to mouseup (cancel if drag happens)
        if (!isAlreadySelected && !isDragHandle) {
            this.pendingSelectElement = targetElement;
            this.dragStart = { x: e.clientX, y: e.clientY };
            return;
        }

        // Always collapse to exactly one element for drag.
        if (this.selectedElements.length > 1 || !isAlreadySelected) {
            this.selectElement(targetElement);
        }

        // Already selected or drag handle → prepare for drag
        if (isDragHandle && !isAlreadySelected) {
            this.selectElement(targetElement);
        }

        this.isPreparedForDrag = true;
        this.draggedElement = targetElement;
        this._layoutFrozenForInteraction = false;
        this.dragStart = { x: e.clientX, y: e.clientY };

        this.elementsStartPos.clear();
        const bounds = this.getElementBounds
            ? this.getElementBounds(targetElement)
            : { left: targetElement.offsetLeft, top: targetElement.offsetTop, width: targetElement.offsetWidth, height: targetElement.offsetHeight };

        this.elementsStartPos.set(targetElement, {
            x: bounds.left,
            y: bounds.top,
            width: bounds.width,
            height: bounds.height,
        });
    },

    handleMouseMove(e) {
        // Start real drag only after moving > 5px to avoid accidental drags.
        if (this.isPreparedForDrag && !this.isDragging && this.dragStart) {
            const distanceMoved = Math.sqrt(
                Math.pow(e.clientX - this.dragStart.x, 2) +
                Math.pow(e.clientY - this.dragStart.y, 2)
            );

            if (distanceMoved > 5) {
                this.isDragging = true;
                this.isPreparedForDrag = false;
                this.disableTemplateDrag = true;

                // Freeze ALL selectable siblings to absolute positioning
                // right before drag begins. This preserves CSS layout during
                // display but ensures elements can be freely moved.
                if (!this._layoutFrozenForInteraction && this.draggedElement) {
                    this.freezeSelectableSiblingsLayout(this.draggedElement);
                    this._layoutFrozenForInteraction = true;
                }

                console.log('[SlideLogicCore][Drag] Drag started', {
                    draggedId: this.draggedElement?.id || null,
                    start: this.dragStart,
                    current: { x: e.clientX, y: e.clientY },
                    thresholdDistance: distanceMoved,
                    scale: this.currentScale,
                });
            } else {
                return;
            }
        }

        if (this.isResizing) {
            if (this.selectedElements.length !== 1) return;

            const targetElement = this.selectedElements[0];
            const dx = (e.clientX - this.dragStart.x) / this.currentScale;
            const dy = (e.clientY - this.dragStart.y) / this.currentScale;
            const el = targetElement;
            const startRect = this.elementsStartPos.get(el);
            if (!startRect) return;
            const { x, y, width, height } = startRect;

            if (this.resizeHandle.includes('r')) {
                el.style.width = `${Math.max(20, width + dx)}px`;
            }
            if (this.resizeHandle.includes('l')) {
                el.style.width = `${Math.max(20, width - dx)}px`;
                el.style.left = `${x + dx}px`;
            }
            if (this.resizeHandle.includes('b')) {
                el.style.height = `${Math.max(20, height + dy)}px`;
            }
            if (this.resizeHandle.includes('t')) {
                el.style.height = `${Math.max(20, height - dy)}px`;
                el.style.top = `${y + dy}px`;
            }

            this.updateSelectionUI();
            if (this.emitSelectedElementData) this.emitSelectedElementData(el);
            return;
        }

        if (this.isDragging && this.selectedElements.length > 0) {
            this.clearSmartGuides();

            let finalDx = (e.clientX - this.dragStart.x) / this.currentScale;
            let finalDy = (e.clientY - this.dragStart.y) / this.currentScale;

            const primaryElement = this.selectedElements[0];
            const startPos = this.elementsStartPos.get(primaryElement);
            if (!startPos) return;

            this.ensureElementAbsolutePosition(primaryElement, {
                left: startPos.x,
                top: startPos.y,
                width: startPos.width,
                height: startPos.height,
            });

            const snapped = this.snapToGuides(primaryElement, startPos.x + finalDx, startPos.y + finalDy);
            finalDx = snapped.x - startPos.x;
            finalDy = snapped.y - startPos.y;

            this.selectedElements.forEach((el) => {
                const elStartPos = this.elementsStartPos.get(el);
                if (!elStartPos) return;

                this.ensureElementAbsolutePosition(el, {
                    left: elStartPos.x,
                    top: elStartPos.y,
                    width: elStartPos.width,
                    height: elStartPos.height,
                });

                el.style.left = `${elStartPos.x + finalDx}px`;
                el.style.top = `${elStartPos.y + finalDy}px`;
            });

            this.drawSmartGuides(snapped.guides);

            if (this.selectedElements.length === 1 && this.emitSelectedElementData) {
                this.emitSelectedElementData(this.selectedElements[0]);
            }
        }
    },

    handleMouseUp(e) {
        this.isTextSelecting = false;

        this.root.querySelectorAll('.dragging, .drag-preview').forEach((el) => {
            el.classList.remove('dragging', 'drag-preview');
        });
        this.clearSmartGuides();

        if (this.pendingSelectElement) {
            let shouldSelect = true;

            if (this.dragStart && e) {
                const distanceMoved = Math.sqrt(
                    Math.pow(e.clientX - this.dragStart.x, 2) +
                    Math.pow(e.clientY - this.dragStart.y, 2)
                );
                shouldSelect = distanceMoved <= 2;
            }

            if (shouldSelect) {
                this.selectElement(this.pendingSelectElement);
            }

            this.pendingSelectElement = null;
            this.dragStart = null;
            return;
        }

        const endedDrag = this.isDragging;
        const endedResize = this.isResizing;
        const activeElement = this.selectedElements[0] || null;

        if (this.isDragging || this.isResizing) {
            let hasActualChange = false;

            if (this.dragStart && e) {
                const distanceMoved = Math.sqrt(
                    Math.pow(e.clientX - this.dragStart.x, 2) +
                    Math.pow(e.clientY - this.dragStart.y, 2)
                );
                hasActualChange = distanceMoved > 3;
            }

            if (hasActualChange) {
                this.justFinishedDragging = true;
                setTimeout(() => {
                    this.justFinishedDragging = false;
                }, 100);

                this.saveHistory();
                if (this.emitSelectedElementData && this.selectedElements.length === 1) {
                    this.emitSelectedElementData(this.selectedElements[0]);
                }
            }

            console.log('[SlideLogicCore][Drag] MouseUp after interaction', {
                mode: endedResize ? 'resize' : (endedDrag ? 'drag' : 'unknown'),
                hasActualChange,
                elementId: activeElement?.id || null,
                left: activeElement?.style?.left || null,
                top: activeElement?.style?.top || null,
                width: activeElement?.style?.width || null,
                height: activeElement?.style?.height || null,
            });
        }

        this.isDragging = false;
        this.isResizing = false;
        this.isPreparedForDrag = false;
        this.resizeHandle = null;
        this.pendingSelectElement = null;
        this.draggedElement = null;
        this.disableTemplateDrag = false;
        this.elementsStartPos.clear();
        this.dragStart = null;
    },
};
