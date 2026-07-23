import React, { useRef, useEffect, useImperativeHandle, forwardRef } from 'react';
import { SlideEditorLogic } from '@/lib/SlideLogicCore';

interface SlideCanvasProps {
  slideId: string;
  htmlContent: string;
  backgroundColor?: string;
  backgroundImage?: string;
  onElementSelect?: (data: any) => void;
  onChange?: () => void;
  zoom?: number;
  /** When true, only renders the slide — no drag/resize/edit logic is initialized */
  readOnly?: boolean;
}

export interface SlideCanvasHandle {
  updateElement: (styles: any, targetId?: string) => void;
  getHTML: () => string;
  undo: () => void;
  redo: () => void;
  canUndo: () => boolean;
  canRedo: () => boolean;
  execFormat: (command: string, value?: string) => void;
  getSelectedZIndex: () => number;
  getMaxZIndex: () => number;
  injectElement: (html: string) => void;
  deleteElement: (id?: string) => void;
  duplicateElement: (id?: string) => void;
  copySelectedElement: (id?: string) => boolean;
  pasteElement: () => void;
  bringToFront: (id?: string) => void;
  sendToBack: (id?: string) => void;
  isTextEditing: () => boolean;
  activateEquationById: (id: string) => void;
  insertMath: (latex: string) => void;
  insertEquationAtCursor: () => void;
  saveHistory: (silent?: boolean) => void;
  reselectById: (id: string) => void;
  getHistoryState: () => any;
  restoreHistoryState: (state: any) => void;
}

export const SlideCanvas = forwardRef<SlideCanvasHandle, SlideCanvasProps>((props, ref) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const shadowRootRef = useRef<ShadowRoot | null>(null);
  const logicInstanceRef = useRef<SlideEditorLogic | null>(null);
  // Store slide-specific CSS so it can be round-tripped when saving
  const slideCSSRef = useRef<string>('');
  // Store <link> tags (e.g. Google Fonts) so they survive the save/reload cycle
  const slideLinkTagsRef = useRef<string>('');
  // Only converter-generated slides use --scale centering logic on .content-wrapper.
  const needsConverterScaleFallbackRef = useRef<boolean>(false);

  // Use refs so SlideEditorLogic always calls the latest callbacks without needing re-init
  const onElementSelectRef = useRef<(data: any) => void>(props.onElementSelect);
  const onChangeRef = useRef<(() => void) | undefined>(props.onChange);
  const zoomRef = useRef<number>(props.zoom ?? 1);
  // Update refs on every render (no deps needed — this is intentional)
  onElementSelectRef.current = props.onElementSelect;
  onChangeRef.current = props.onChange;
  zoomRef.current = props.zoom ?? 1;

  // Apply fallback background to host element (visible when slide CSS has no bg)
  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.style.backgroundColor = props.backgroundColor || '';
    containerRef.current.style.backgroundImage = props.backgroundImage || '';
    containerRef.current.style.backgroundPosition = props.backgroundImage ? 'center center' : '';
    containerRef.current.style.backgroundSize = props.backgroundImage ? 'cover' : '';
    containerRef.current.style.backgroundRepeat = props.backgroundImage ? 'no-repeat' : '';
  }, [props.backgroundColor, props.backgroundImage]);

  // Expose các method cho component cha (SlideEditor.tsx) gọi
  useImperativeHandle(ref, () => ({
    updateElement: (styles: any, targetId?: string) => {
      logicInstanceRef.current?.updateSelectedElementStyle(styles, targetId ?? null);
    },
    getHTML: () => {
      const canvasHTML = logicInstanceRef.current?.getHTML() || '';
      // Prepend <link> tags and slide-specific CSS so they survive save/reload cycles.
      // Re-remap Shadow DOM selectors back to standard CSS selectors so the
      // stored html_content works correctly in a normal iframe/browser context.
      const linkTags = slideLinkTagsRef.current;
      const css = slideCSSRef.current;
      let result = '';
      if (linkTags && linkTags.trim()) {
        result += linkTags + '\n';
      }
      if (css && css.trim()) {
        const standardCSS = css
          .replace(/\.slide-bg-wrapper\s*\{/g, 'body {')
          .replace(/\.slide-bg-wrapper\b/g, 'body')
          .replace(/:host\s*\{/g, 'html {')
          .replace(/:host\b/g, 'html');
        result += `<style>${standardCSS}</style>\n`;
      }
      result += canvasHTML;
      return result;
    },
    undo: () => {
      logicInstanceRef.current?.undo();
    },
    redo: () => {
      logicInstanceRef.current?.redo();
    },
    canUndo: () => logicInstanceRef.current?.canUndo() ?? false,
    canRedo: () => logicInstanceRef.current?.canRedo() ?? false,
    execFormat: (command: string, value?: string) => {
      logicInstanceRef.current?.execFormat(command, value ?? null);
    },
    getSelectedZIndex: () => {
      return logicInstanceRef.current?.getSelectedZIndex() ?? 0;
    },
    getMaxZIndex: () => {
      return logicInstanceRef.current?.getMaxZIndex() ?? 0;
    },
    injectElement: (html: string) => {
      logicInstanceRef.current?.injectElement(html);
    },
    deleteElement: (id?: string) => {
      logicInstanceRef.current?.deleteElement(id ?? null);
    },
    duplicateElement: (id?: string) => {
      logicInstanceRef.current?.duplicateElement(id ?? null);
    },
    copySelectedElement: (id?: string) => {
      return logicInstanceRef.current?.copySelectedElement(id ?? null) ?? false;
    },
    pasteElement: () => {
      logicInstanceRef.current?.pasteElement();
    },
    bringToFront: (id?: string) => {
      logicInstanceRef.current?.bringToFront(id ?? null);
    },
    sendToBack: (id?: string) => {
      logicInstanceRef.current?.sendToBack(id ?? null);
    },
    isTextEditing: () => {
      return !!logicInstanceRef.current?.isEditingText;
    },
    activateEquationById: (id: string) => {
      try {
        const root = shadowRootRef.current;
        const logic: any = logicInstanceRef.current;
        const el = root?.querySelector<HTMLElement>(`#${CSS.escape(id)}`) ?? null;
        if (!root || !logic?.activateEquationEditor || !el) return;
        logic.activateEquationEditor(el);
      } catch {
        // no-op
      }
    },
    insertMath: (latex: string) => {
      const logic: any = logicInstanceRef.current;
      if (!logic) return;

      // Highest priority: inline equation selected via Properties-panel flow
      const selectedInlineMf = logic._selectedInlineMathField as any;
      if (selectedInlineMf && selectedInlineMf.isConnected) {
        selectedInlineMf.removeAttribute('read-only');
        selectedInlineMf.mathVirtualKeyboardPolicy = 'manual';
        selectedInlineMf.insert(latex, { focus: true });
        selectedInlineMf.setAttribute('value', selectedInlineMf.value);
        selectedInlineMf.setAttribute('read-only', 'true');
        logic.saveHistory();
        return;
      }

      // Try to find an active inline math-field first (from activateInlineEquationEditor)
      const inlineMf = shadowRootRef.current?.querySelector<any>('math-field[data-inline-equation][read-only="false"], math-field[data-inline-equation]:not([read-only])');
      if (inlineMf) {
        inlineMf.insert(latex, { focus: true });
        inlineMf.setAttribute('value', inlineMf.value);
        logic.saveHistory();
        return;
      }

      // Fall back to structured equation div
      const selectedEl = logic.getSelectedElement();
      if (!selectedEl || selectedEl.getAttribute('data-type') !== 'equation') return;

      const mf = selectedEl.querySelector('math-field') as any;
      if (mf) {
        mf.insert(latex, { focus: true });
        selectedEl.dataset.latex = mf.value;
        mf.setAttribute('value', mf.value);
        logic.saveHistory();
      } else {
        logic.activateEquationEditor(selectedEl);
        setTimeout(() => {
          const newMf = selectedEl.querySelector('math-field') as any;
          if (newMf) {
            newMf.insert(latex, { focus: true });
            selectedEl.dataset.latex = newMf.value;
            newMf.setAttribute('value', newMf.value);
            logic.saveHistory();
          }
        }, 50);
      }
    },
    insertEquationAtCursor: async () => {
      const logic: any = logicInstanceRef.current;
      if (!logic) {
        console.warn('[SlideCanvas] insertEquationAtCursor: logic not initialized');
        return;
      }

      // Get cursor position BEFORE any DOM changes
      const cursorPos = logic.getCursorPositionInCanvas?.();
      if (!cursorPos) {
        console.warn('[SlideCanvas] insertEquationAtCursor: no cursor position found');
        return;
      }

      const { x, y } = cursorPos;

      // Blur the active text element
      const activeElement = document.activeElement;
      if (activeElement instanceof HTMLElement && activeElement.hasAttribute('contenteditable')) {
        activeElement.blur();
      }

      // Create equation element at cursor position
      // DON'T create math-field here - let activateEquationEditor() handle it
      const eqDiv = document.createElement('div');
      eqDiv.setAttribute('data-type', 'equation');
      eqDiv.setAttribute('data-latex', '');
      eqDiv.style.cssText = `
        position: absolute;
        left: ${Math.max(0, x)}px;
        top: ${Math.max(0, y)}px;
        width: 300px;
        height: 80px;
        font-size: 32px;
        color: #ffffff;
      `;

      // Add to canvas
      if (!logic.canvas) {
        console.warn('[SlideCanvas] insertEquationAtCursor: canvas not available');
        return;
      }

      logic.canvas.appendChild(eqDiv);
      logic.normalizeElementForCanvas(eqDiv);

      console.log('[SlideCanvas] Equation element created', { id: eqDiv.id, x, y });

      // Activate equation editor - this will create math-field and focus it
      // activateEquationEditor() handles: import mathlive, create math-field, focus, attach handlers
      if (logic.activateEquationEditor) {
        logic.activateEquationEditor(eqDiv);
      }

      // Save to history
      logic.saveHistory();
    },
    saveHistory: (silent = false) => {
      logicInstanceRef.current?.saveHistory(silent);
    },
    reselectById: (id: string) => {
      logicInstanceRef.current?.reselectById(id);
    },
    getHistoryState: () => {
      return logicInstanceRef.current?.getHistoryState?.() ?? null;
    },
    restoreHistoryState: (state: any) => {
      logicInstanceRef.current?.restoreHistoryState?.(state);
    },
  }));

  // The converter's resize JS (var(--scale,1)) doesn't execute via innerHTML.
  // Fallback for readOnly mode: set --scale from measured dimensions.
  const applyConverterScaleFallback = (shadowRoot: ShadowRoot) => {
    if (!needsConverterScaleFallbackRef.current) return;

    setTimeout(() => {
      const cw = shadowRoot.querySelector('.content-wrapper') as HTMLElement | null;
      if (!cw) return;
      const w = cw.offsetWidth;
      const h = cw.offsetHeight;
      if (w > 0 && h > 0) {
        const scale = Math.min(1920 / w, 1080 / h);
        cw.style.transform = `translate(-50%, -50%) scale(${scale})`;
      }
    }, 50);
  };

  /**
   * Parse a CSS rule body into a key→value map.
   * E.g. "margin: 0; background: red;" → { margin: "0", background: "red" }
   */
  const parseCSSProperties = (ruleBody: string): Record<string, string> => {
    const props: Record<string, string> = {};
    // Split on semicolons, but be careful with values that contain parentheses
    // (like linear-gradient) — those don't contain semicolons so simple split works.
    const parts = ruleBody.split(';');
    for (const part of parts) {
      const trimmed = part.trim();
      if (!trimmed) continue;
      const colonIdx = trimmed.indexOf(':');
      if (colonIdx <= 0) continue;
      const key = trimmed.substring(0, colonIdx).trim();
      const value = trimmed.substring(colonIdx + 1).trim();
      if (key && value) {
        props[key] = value;
      }
    }
    return props;
  };

  // Remap top-level page selectors so imported HTML/CSS keeps browser parity in Shadow DOM.
  const remapCssSelectorsForShadowDom = (css: string): string => {
    return css.replace(/([^{}]+)\{/g, (fullMatch, selectorChunk: string) => {
      const trimmed = selectorChunk.trim();
      // Keep at-rules intact: @media, @keyframes, @font-face, etc.
      if (trimmed.startsWith('@')) return fullMatch;

      const remappedSelectors = selectorChunk
        .split(',')
        .map((selector) => selector
          // Normalize any persisted :host from previous editor saves back to html first.
          .replace(/:host\b/g, 'html')
          // In Shadow DOM, map :root custom-properties to :host.
          .replace(/:root\b/g, 'html')
          // Then map browser selectors to Shadow DOM equivalents.
          .replace(/\bhtml\b/g, ':host')
          .replace(/\bbody\b/g, '.slide-bg-wrapper')
        )
        .join(',');

      return `${remappedSelectors}{`;
    });
  };

  /**
   * Renders equation elements as read-only MathLive math-field elements.
   * Imports the browser mathlive bundle (registering the custom element).
   * Works in both editor (static display) and readOnly (presentation) modes.
   */
  const renderEquationsInRoot = async (root: ShadowRoot | HTMLElement) => {
    // Load MathLive to register the <math-field> custom element globally.
    // This is needed for BOTH `[data-type="equation"]` divs AND bare inline `<math-field>` tags.
    try {
      const ml = await import('mathlive') as any; // registers <math-field> custom element globally
      
      // Robust font path — use absolute URL to ensure we hit /fonts on the server
      const fontsUrl = window.location.origin + '/fonts';
      console.log('[SlideCanvas] Setting fontsDirectory to:', fontsUrl);
      
      if (ml && ml.setOptions) {
        ml.setOptions({ fontsDirectory: fontsUrl });
      } else if ((window as any).MathLive?.setOptions) {
        (window as any).MathLive.setOptions({ fontsDirectory: fontsUrl });
      }
    } catch (e) {
      console.warn('[SlideCanvas] mathlive unavailable:', e);
      return;
    }

    // --- Render structured equation elements (from Add Equation tool) ---
    const allEquationNodes = Array.from(
      root.querySelectorAll<HTMLElement>('[data-type="equation"]')
    );
    allEquationNodes.forEach(node => {
      let mf = node.querySelector('math-field') as HTMLElement & { value?: string };
      if (!mf) {
        const latex = node.dataset.latex || '';
        node.innerHTML = '';
        mf = document.createElement('math-field') as HTMLElement & { value: string };
        mf.setAttribute('read-only', '');
        mf.style.cssText = [
          'width:fit-content',
          'max-width:100%',
          'min-height:30px',
          'border:none',
          'background:transparent',
          'font-size:inherit',
          'color:inherit',
          'outline:none',
        ].join(';');
        node.appendChild(mf);
        (mf as any).value = latex;
      }
      if (!node.querySelector('.equation-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'equation-overlay';
        node.insertBefore(overlay, mf);
      }
    });

    // --- Render bare inline math-field tags (from LLM-generated content) ---
    // These are NOT inside [data-type="equation"] wrappers.
    // MathLive is now registered so the custom element will upgrade automatically.
    // We just need to ensure read-only and styling.
    root.querySelectorAll<HTMLElement>('math-field').forEach(mf => {
      const parent = mf.parentElement;
      if (parent && parent.getAttribute('data-type') === 'equation') {
        return; // handled above
      }
      // Ensure read-only for display
      mf.setAttribute('read-only', 'true');
      mf.setAttribute('data-inline-equation', 'true');
      mf.style.display = 'inline-block';
      mf.style.verticalAlign = 'middle';
      mf.style.cursor = 'pointer';
      mf.style.border = '1px solid transparent';
      mf.style.background = 'transparent';
      mf.style.borderRadius = '4px';
      mf.style.padding = '2px 4px';
      mf.style.margin = '0 1px';
      mf.style.fontSize = 'inherit';
      mf.style.color = 'inherit';
      mf.style.pointerEvents = 'auto';
      // Attach robust pointer handlers directly to math-field so it works with
      // MathLive shadow DOM and regardless of click synthesis quirks.
      const mfAny = mf as any;
      if (!mfAny._inlineClickHandler) {
        mfAny._inlineClickHandler = (ev?: Event) => {
          // Let browser/MathLive place caret at exact click position.
          // Only bootstrap selection when NOT already in active equation edit mode.
          if (mf.hasAttribute('read-only')) {
            ev?.stopPropagation?.();
          } else {
            return; // already editing: let MathLive handle mouse/caret naturally
          }
          mf.dispatchEvent(new CustomEvent('inline-equation-click', {
            bubbles: true,
            composed: true,
            detail: { mathField: mf, originalEventType: ev?.type },
          }));
        };
        // Pointerdown/mousedown prioritize equation over textbox selection.
        mf.addEventListener('pointerdown', mfAny._inlineClickHandler, true);
        mf.addEventListener('mousedown', mfAny._inlineClickHandler, true);
        mf.addEventListener('touchstart', mfAny._inlineClickHandler, true);
      }
    });
  };


  // Xử lý HTML & CSS Isolation
  const processHTML = (rawHTML: string, isReadOnly = false): string => {
    // Fix viewport units to absolute pixels (vw/vh refer to page viewport in Shadow DOM)
    const fixedHTML = rawHTML
      .replace(/(\d+(?:\.\d+)?)\s*vw/gi, (_, n) => `${(parseFloat(n) * 1920 / 100).toFixed(2)}px`)
      .replace(/(\d+(?:\.\d+)?)\s*vh/gi, (_, n) => `${(parseFloat(n) * 1080 / 100).toFixed(2)}px`)
      .replace(/(\d+(?:\.\d+)?)\s*vmin/gi, (_, n) => `${(parseFloat(n) * 1080 / 100).toFixed(2)}px`)
      .replace(/(\d+(?:\.\d+)?)\s*vmax/gi, (_, n) => `${(parseFloat(n) * 1920 / 100).toFixed(2)}px`);

    // Parse HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(fixedHTML, 'text/html');

    // --- 1. Collect all CSS ---
    const styleElements = Array.from(doc.querySelectorAll('style'));
    let collectedCSS = styleElements.map(s => s.textContent || '').join('\n');

    // Converted HTML from the parser uses transform: ... scale(var(--scale, 1))
    // and a script that sets --scale at runtime. We only apply Shadow DOM
    // scale fallback for this converter-specific pattern.
    const hasConverterScalePattern =
      /\.content-wrapper\s*\{[^}]*scale\(var\(--scale\s*,\s*1\)\)/is.test(collectedCSS) ||
      /setProperty\(\s*['"]--scale['"]/i.test(rawHTML);
    needsConverterScaleFallbackRef.current = hasConverterScalePattern;

    // Collect <link rel="stylesheet"> elements (e.g. Google Fonts) so they
    // can be injected into the Shadow DOM and preserved across save/reload.
    const linkElements = Array.from(doc.querySelectorAll('link[rel="stylesheet"]'));
    const linkTagsHTML = linkElements.map(l => l.outerHTML).join('\n');

    // --- 2. Preserve body visual fidelity ---
    // Keep browser-authored body CSS in collectedCSS after selector remap, and only
    // carry body inline style + minimal fallbacks on the wrapper element.
    const mergedBodyProps: Record<string, string> = parseCSSProperties(doc.body.getAttribute('style') || '');

    if (!mergedBodyProps['position']) mergedBodyProps['position'] = 'relative';
    if (!mergedBodyProps['width']) mergedBodyProps['width'] = '100%';
    if (!mergedBodyProps['height']) mergedBodyProps['height'] = '100%';
    if (!mergedBodyProps['box-sizing']) mergedBodyProps['box-sizing'] = 'border-box';
    // In editor mode, hide imported body scrollbars so the slide surface stays clean.
    mergedBodyProps['overflow'] = 'hidden';
    mergedBodyProps['overflow-x'] = 'hidden';
    mergedBodyProps['overflow-y'] = 'hidden';

    // Build inline style string from merged body properties
    const wrapperInlineStyle = Object.entries(mergedBodyProps)
      .map(([k, v]) => `${k}:${v}`)
      .join(';');

    // --- 3. Remap CSS selectors for Shadow DOM ---
    // body {} → .slide-bg-wrapper {} (class on wrapper div)
    // html {} → :host
    // body .child → .slide-bg-wrapper .child (descendant combinator)
    collectedCSS = remapCssSelectorsForShadowDom(collectedCSS);

    // Persist CSS for getHTML() round-trip
    slideCSSRef.current = collectedCSS;
    slideLinkTagsRef.current = linkTagsHTML;

    // --- 4. Remove style elements from body to avoid duplicates ---
    styleElements.forEach(s => s.remove());

    // --- 5. Auto-enhance elements from converter HTML ---
    // Process ALL descendants (not just direct children) so elements inside
    // .content-wrapper / .outer-wrapper from the converter also get enhanced.
    const tempContainer = document.createElement('div');
    tempContainer.innerHTML = doc.body.innerHTML;

    // --- 5a. Convert plain Unicode math text snippets to inline <math-field> ---
    // Example: "ax² + bx + c = 0" -> <math-field value="ax^2 + bx + c = 0">
    const SUPERSCRIPT_MAP: Record<string, string> = {
      '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
      '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
      '⁺': '+', '⁻': '-', '⁼': '=', '⁽': '(', '⁾': ')', 'ⁿ': 'n',
    };
    const SUBSCRIPT_MAP: Record<string, string> = {
      '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
      '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
      '₊': '+', '₋': '-', '₌': '=', '₍': '(', '₎': ')',
    };

    const toLatexFromUnicodeMath = (input: string): string => {
      let out = input;
      out = out.replace(/([A-Za-z0-9\)\]])([⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ]+)/g, (_, base, sup) => {
        const supText = [...sup].map((c) => SUPERSCRIPT_MAP[c] ?? c).join('');
        return `${base}^${supText}`;
      });
      out = out.replace(/([A-Za-z0-9\)\]])([₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎]+)/g, (_, base, sub) => {
        const subText = [...sub].map((c) => SUBSCRIPT_MAP[c] ?? c).join('');
        return `${base}_${subText}`;
      });
      out = out.replace(/√\s*([A-Za-z0-9_]+)/g, String.raw`\sqrt{$1}`);
      out = out.replace(/∞/g, String.raw`\infty`);
      out = out.replace(/≤/g, String.raw`\leq`);
      out = out.replace(/≥/g, String.raw`\geq`);
      out = out.replace(/≠/g, String.raw`\neq`);
      out = out.replace(/±/g, String.raw`\pm`);
      return out.trim();
    };

    const looksLikeFormula = (s: string): boolean => {
      const text = s.trim();
      if (text.length < 3 || text.length > 140) return false;
      const hasUnicodeMath = /[₀-₉⁰¹²³⁴⁵⁶⁷⁸⁹√∞≤≥≠±∫∑∏]/.test(text);
      const hasEquationShape = /[A-Za-z]\s*[\^_]?\s*[0-9₀-₉⁰¹²³⁴⁵⁶⁷⁸⁹]|\=/.test(text);
      const hasMathOps = /[=+\-*]/.test(text);
      return (hasUnicodeMath || hasEquationShape) && hasMathOps;
    };

    const formulaCandidateRegex = /([A-Za-zÀ-ỹΑ-Ωα-ω0-9₀-₉⁰¹²³⁴⁵⁶⁷⁸⁹\(\)\[\]\{\}\s+\-*/=<>≤≥≠±√∞∫∑∏.,]{3,})/g;
    const walker = doc.createTreeWalker(tempContainer, NodeFilter.SHOW_TEXT);
    const textNodes: Text[] = [];
    let cur = walker.nextNode();
    while (cur) {
      textNodes.push(cur as Text);
      cur = walker.nextNode();
    }
    textNodes.forEach((textNode) => {
      const parent = textNode.parentElement;
      if (!parent) return;
      if (parent.closest('math-field, style, script, [data-type="equation"]')) return;
      const raw = textNode.nodeValue || '';
      if (!/[₀-₉⁰¹²³⁴⁵⁶⁷⁸⁹√∞≤≥≠±=]/.test(raw)) return;

      const frag = document.createDocumentFragment();
      let last = 0;
      const matches = [...raw.matchAll(formulaCandidateRegex)];
      if (!matches.length) return;

      matches.forEach((m) => {
        const full = m[0];
        const start = m.index ?? 0;
        const end = start + full.length;
        if (start > last) frag.appendChild(document.createTextNode(raw.slice(last, start)));

        if (looksLikeFormula(full)) {
          const mf = document.createElement('math-field');
          const latex = toLatexFromUnicodeMath(full);
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
          mf.style.pointerEvents = 'auto';
          mf.style.minWidth = '1.2em';
          frag.appendChild(mf);
        } else {
          frag.appendChild(document.createTextNode(full));
        }
        last = end;
      });
      if (last < raw.length) frag.appendChild(document.createTextNode(raw.slice(last)));
      textNode.parentNode?.replaceChild(frag, textNode);
    });

    // --- 5b. Convert <math-field> tags ---
    // AI sometimes generates <math-field>latex</math-field> directly inline.
    // We strictly keep these inline so they flow correctly in text elements or grid layouts.
    // Only elements generated by the "Add Equation" tool are wrapped in `data-type="equation"`.
    tempContainer.querySelectorAll('math-field').forEach((mf) => {
      const parent = mf.parentElement;
      if (parent && parent.getAttribute('data-type') === 'equation') {
        // Already a structured canvas equation (e.g. from Add Equation tool)
        return; 
      }
      
      // Keep math-field inline exactly where LLM placed it, render read-only
      // Click on it will open equation editor (handled by EventHandlersMixin)
      (mf as HTMLElement).setAttribute('read-only', 'true');
      (mf as HTMLElement).setAttribute('data-inline-equation', 'true');
      (mf as HTMLElement).style.display = 'inline-block';
      (mf as HTMLElement).style.verticalAlign = 'middle';
      (mf as HTMLElement).style.cursor = 'pointer';
    });

    // Layout containers: skip these (don't tag as elements), but their
    // children still get iterated/processed by querySelectorAll('*').
    const LAYOUT_CONTAINERS = new Set([
      'outer-wrapper', 'content-wrapper', 'slide-container',
      'slide-inner-container', 'wrapper', 'scale-container',
      'slide-wrapper',
    ]);

    const INLINE_FORMATTING_TAGS = new Set([
      'span', 'strong', 'b', 'em', 'i', 'u', 'mark', 'small',
      'sub', 'sup', 'code', 'kbd', 'samp', 'var', 'a',
      'font', 'ins', 'del', 's', 'abbr', 'cite', 'q', 'time',
      // Keep list items attached to their list container; dragging LI directly causes list reflow.
      'li',
      'br', 'wbr', 'hr',
    ]);

    Array.from(tempContainer.querySelectorAll('*')).forEach(node => {
      if (!(node instanceof HTMLElement)) return;

      const tag = node.tagName.toLowerCase();
      if (['style', 'script', 'link', 'meta', 'svg', 'defs', 'path', 'rect', 'circle', 'ellipse', 'line', 'polygon', 'polyline', 'g', 'use', 'clippath', 'lineargradient', 'radialgradient', 'stop', 'pattern', 'mask', 'text'].includes(tag)) return;
      // Skip layout wrappers — they're not slide "elements"
      if ([...node.classList].some(c => LAYOUT_CONTAINERS.has(c))) return;
      // Keep inline formatting inside text flow; dragging these would detach styled fragments.
      if (INLINE_FORMATTING_TAGS.has(tag)) {
        node.classList.remove('element');
        delete node.dataset.selectable;
        if (node.dataset.type) delete node.dataset.type;
        if (node.style?.cursor === 'move') node.style.removeProperty('cursor');
        return;
      }

      // Preserve equation data-type — never reclassify equation elements
      if (node.dataset.type === 'equation' || node.classList.contains('equation')) {
        node.dataset.type = 'equation';
        if (!node.classList.contains('element')) node.classList.add('element');
        node.dataset.selectable = 'true';
        if (!isReadOnly) node.style.cursor = 'move';
        if (!node.id) node.id = `element_equation_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        // Ensure equation has proper structure for renderEquationsInRoot
        // If generator created a bare div with data-latex, keep it clean — renderEquationsInRoot will populate it
        // If it has existing math-field, preserve it
        const existingMF = node.querySelector('math-field');
        if (!existingMF && node.innerHTML.trim() === '') {
          // Bare equation div from generator — leave empty for renderEquationsInRoot to fill
          // Store latex in data attribute for renderEquationsInRoot to find
          const latex = node.dataset.latex || 'x = y';
          node.dataset.latex = latex;
        }
        return;
      }

      // Wrap bare <img> in a container div so it can receive resize handles
      // (void elements like <img> cannot have children).
      if (tag === 'img') {
        const imgW = node.style.width || (node.getAttribute('width') ? node.getAttribute('width') + 'px' : '');
        const imgH = node.style.height || (node.getAttribute('height') ? node.getAttribute('height') + 'px' : '');
        const imgL = node.style.left || '0px';
        const imgT = node.style.top || '0px';
        if (imgW && imgH) {
          const wrapper = document.createElement('div');
          wrapper.style.cssText = `position:absolute;left:${imgL};top:${imgT};width:${imgW};height:${imgH};overflow:hidden;cursor:move;`;
          if (node.style.zIndex) wrapper.style.zIndex = node.style.zIndex;
          wrapper.classList.add('element');
          wrapper.dataset.type = 'image';
          wrapper.dataset.selectable = 'true';
          wrapper.id = node.id || `element_image_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          node.style.position = 'static';
          node.style.left = '';
          node.style.top = '';
          node.style.width = '100%';
          node.style.height = '100%';
          node.style.objectFit = 'cover';
          node.style.pointerEvents = 'none';
          node.removeAttribute('id');
          node.parentElement!.insertBefore(wrapper, node);
          wrapper.appendChild(node);
          return;
        }
      }

      // Only make absolute-positioned elements independently selectable/draggable.
      // Non-absolute elements (flex/grid children, static flow) keep their CSS
      // layout and are NOT draggable — this preserves visual fidelity.
      const inlinePosition = node.style.position;
      const isAbsolute = inlinePosition === 'absolute';

      if (isAbsolute) {
        if (!node.classList.contains('element')) {
          node.classList.add('element');
        }
        node.dataset.selectable = 'true';
        if (!isReadOnly) node.style.cursor = 'move';

        if (!node.dataset.type) {
          let elementType: 'text' | 'image' | 'video' | 'shape' = 'shape';

          const hasImage = node.querySelector('img') || tag === 'img';
          const hasVideo = node.querySelector('video') || tag === 'video';
          const textContent = node.textContent?.trim() || '';
          const hasSignificantText = textContent.length > 3;

          const explicitTextTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'blockquote', 'pre', 'a'];
          const isDivWithText = tag === 'div' && hasSignificantText;
          const hasBackgroundStyling = node.style.background || node.style.backgroundColor ||
            node.style.backgroundImage || node.style.borderRadius;

          if (hasImage) {
            elementType = 'image';
          } else if (hasVideo) {
            elementType = 'video';
          } else if (explicitTextTags.includes(tag) && hasSignificantText) {
            elementType = 'text';
          } else if (isDivWithText && !hasBackgroundStyling) {
            elementType = 'text';
          } else if (hasSignificantText && !hasBackgroundStyling) {
            elementType = 'text';
          } else {
            elementType = 'shape';
          }

          node.dataset.type = elementType;
        }

        if (!isReadOnly && node.dataset.type === 'text' && !node.hasAttribute('contenteditable')) {
          node.setAttribute('contenteditable', 'true');
        }

        if (!node.id) {
          node.id = `element_${node.dataset.type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        }
      } else {
        // Non-absolute elements: strip any stale editor attributes
        node.classList.remove('element');
        delete node.dataset.selectable;
        if (node.style?.cursor === 'move') node.style.removeProperty('cursor');
      }
    });

    // In read-only mode: strip editor-only artifacts and render equations as static math
    if (isReadOnly) {
      tempContainer.querySelectorAll('.resize-handle, .drag-handle, .smart-guide').forEach(el => el.remove());
      tempContainer.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
      tempContainer.querySelectorAll('[contenteditable]').forEach(el => el.removeAttribute('contenteditable'));
      tempContainer.querySelectorAll('[data-selectable]').forEach(el => el.removeAttribute('data-selectable'));
      tempContainer.querySelectorAll('[data-guide-key]').forEach(el => el.removeAttribute('data-guide-key'));
      tempContainer.querySelectorAll<HTMLElement>('*').forEach(el => {
        if (el.style && el.style.cursor === 'move') el.style.removeProperty('cursor');
      });

      // Equation nodes rendered after DOM injection — see renderEquationsInRoot()
    }

    let bodyContent = tempContainer.innerHTML;

    if (!bodyContent.trim()) {
      bodyContent = '<div style="width: 100%; height: 100%; min-height: 1080px; position: relative;"></div>';
    }

    // --- 6. Build Shadow DOM CSS ---
    // baseShadowCSS only handles :host and editor UI — body/wrapper styling is ALL inline.
    const baseShadowCSS = `
      :host {
        display: block;
        width: 100%;
        height: 100%;
        overflow: hidden;
        /* NOTE: No default font-family here — let the slide's own CSS control fonts */
      }

      .slide-container {
        width: 100%;
        height: 100%;
        position: relative;
      }

      .slide-bg-wrapper,
      .slide-bg-wrapper * {
        scrollbar-width: none;
      }

      .slide-bg-wrapper::-webkit-scrollbar,
      .slide-bg-wrapper *::-webkit-scrollbar {
        width: 0 !important;
        height: 0 !important;
        display: none;
      }

      ${isReadOnly ? '' : `
      [contenteditable] {
        outline: none;
      }

      .selected, [data-selectable].selected {
        box-shadow: 0 0 0 3px #3b82f6 !important;
        outline: none !important;
      }

      .resize-handle {
        position: absolute;
        width: 12px;
        height: 12px;
        background: white;
        border: 2px solid #3b82f6;
        border-radius: 50%;
        display: none;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
        z-index: 100;
        pointer-events: auto !important;
      }

      .selected .resize-handle {
        display: block;
      }

      .resize-handle:hover {
        transform: scale(1.2);
        background: #3b82f6;
        border-color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
      }

      .resize-handle.tl { top: -8px; left: -8px; cursor: nwse-resize; }
      .resize-handle.tr { top: -8px; right: -8px; cursor: nesw-resize; }
      .resize-handle.bl { bottom: -8px; left: -8px; cursor: nesw-resize; }
      .resize-handle.br { bottom: -8px; right: -8px; cursor: nwse-resize; }

      .drag-handle { display: none !important; }
      `}

      .smart-guide { opacity: 0.7; }

      /* ── Equation element ── */
      [data-type="equation"] {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 60px;
        overflow: visible;
        position: relative;
      }
      .equation-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 5;
        background: transparent;
        cursor: move;
      }
      [data-type="equation"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center; /* default */
        padding: 0 16px;
      }
      /* Align Left */
      [data-type="equation"][style*="text-align: left"],
      [data-type="equation"][style*="text-align:left"],
      [data-type="equation"][style*="text-align: flex-start"] { 
        justify-content: flex-start !important; 
      }
      /* Align Center */
      [data-type="equation"][style*="text-align: center"],
      [data-type="equation"][style*="text-align:center"] { 
        justify-content: center !important; 
      }
      /* Align Right */
      [data-type="equation"][style*="text-align: right"],
      [data-type="equation"][style*="text-align:right"],
      [data-type="equation"][style*="text-align: flex-end"] { 
        justify-content: flex-end !important; 
      }

      [data-type="equation"] math-field {
        width: fit-content;
        max-width: 100%;
        min-height: 60px;
        border: none;
        background: transparent;
        font-size: inherit;
        color: inherit;
        outline: none;
      }
      [data-type="equation"] math-field::part(menu-toggle),
      [data-type="equation"] math-field::part(virtual-keyboard-toggle) {
        display: none !important;
        visibility: hidden;
      }
      math-field::part(menu-toggle),
      math-field::part(virtual-keyboard-toggle) {
        display: none !important;
        visibility: hidden;
      }
      /* MathLive static markup sizing and colors */
      [data-type="equation"] math-field,
      [data-type="equation"] .ML__base,
      [data-type="equation"] .ML__mathlive {
        font-size: inherit !important;
        color: inherit !important;
      }

      ${isReadOnly ? '' : `
      [data-selectable="true"] { cursor: move; }

      [contenteditable="true"]:focus {
        outline: none !important;
        cursor: text !important;
      }

      [contenteditable="true"]:empty:before {
        content: attr(data-placeholder);
        color: #999;
      }

      /* Inline equation visual affordance inside text */
      math-field[data-inline-equation] {
        transition: border-color .15s ease, box-shadow .15s ease, background-color .15s ease;
      }
      math-field[data-inline-equation]:hover {
        border-color: #3b82f6 !important;
        background-color: rgba(59, 130, 246, 0.08) !important;
        box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.25) inset;
      }
      math-field[data-inline-equation].inline-equation-selected {
        border-color: #2563eb !important;
        background-color: rgba(37, 99, 235, 0.12) !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.35) inset;
      }
      `}
      ${isReadOnly ? `
      * { pointer-events: none !important; cursor: default !important; }
      ` : ''}
    `;

    // --- 7. Compute content-wrapper scale from CSS dimensions ---
    // The converter's resize <script> doesn't execute via innerHTML in Shadow DOM,
    // so we need to compute the scale statically from the CSS dimensions.
    let scaleOverrideCSS = '';
    if (hasConverterScalePattern) {
      const allCwMatches = [...collectedCSS.matchAll(/\.content-wrapper\s*\{([^}]+)\}/gs)];
      for (const m of allCwMatches) {
        const ruleBody = m[1];
        const wMatch = ruleBody.match(/\bwidth\s*:\s*([\d.]+)px/);
        const hMatch = ruleBody.match(/\bheight\s*:\s*([\d.]+)px/);
        if (wMatch && hMatch) {
          const cwW = parseFloat(wMatch[1]);
          const cwH = parseFloat(hMatch[1]);
          if (cwW > 0 && cwH > 0) {
            const scale = Math.min(1920 / cwW, 1080 / cwH);
            scaleOverrideCSS = `
      .content-wrapper {
        transform: translate(-50%, -50%) scale(${scale.toFixed(6)}) !important;
      }`;
          }
        }
      }
    }

    // --- 8. Assemble final Shadow DOM HTML ---
    // The wrapper div gets ALL merged body properties as inline styles.
    // This avoids any CSS cascade issues between baseShadowCSS and collectedCSS.
    // collectedCSS is still included so descendant selectors (body .child → .slide-bg-wrapper .child)
    // and non-body rules (.content-wrapper, .outer-wrapper, element classes) continue to work.
    return `
      ${linkTagsHTML}
      <style>
        ${baseShadowCSS}
        ${collectedCSS}
        ${scaleOverrideCSS}
      </style>
      <div class="slide-bg-wrapper" style="${wrapperInlineStyle}">
        ${bodyContent}
      </div>
    `;
  };

  /**
   * Inject Google Fonts (and preconnect) <link> tags from the slide HTML into
   * document.head so that @font-face rules are available at the page level.
   * Shadow DOM cannot use fonts loaded only inside the shadow tree.
   * Tags are deduplicated by href to avoid duplicate requests.
   */
  const injectFontLinksToDocumentHead = (rawHTML: string) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(rawHTML, 'text/html');
    const linkEls = Array.from(doc.querySelectorAll('link[rel="stylesheet"], link[rel="preconnect"]'));
    linkEls.forEach((el) => {
      const href = el.getAttribute('href');
      if (!href) return;
      // Deduplicate — skip if already injected
      const existing = document.head.querySelector(`link[href="${CSS.escape(href)}"]`);
      if (existing) return;
      const clone = el.cloneNode(true) as HTMLLinkElement;
      document.head.appendChild(clone);
    });
  };

  useEffect(() => {
    if (!containerRef.current) return;
    let initLogicTimer: ReturnType<typeof setTimeout> | null = null;

    // Attach Shadow DOM (once)
    if (!shadowRootRef.current) {
      try {
        shadowRootRef.current = containerRef.current.attachShadow({ mode: 'open' });
      } catch (e) {
        console.error('[SlideCanvas] Failed to attach shadow DOM:', e);
        return;
      }
    }

    // Inject processed HTML
    try {
      const processedHTML = processHTML(props.htmlContent, props.readOnly);
      shadowRootRef.current.innerHTML = processedHTML;

      // Google Fonts @font-face rules must live at the document level to be
      // usable inside Shadow DOM. Inject <link> tags into document.head too.
      injectFontLinksToDocumentHead(props.htmlContent);

      // The converter's resize <script> doesn't execute via innerHTML in Shadow DOM,
      // so apply the scale fallback for both readOnly and editor modes.
      applyConverterScaleFallback(shadowRootRef.current);
      // Render equation elements as static MathLive markup
      renderEquationsInRoot(shadowRootRef.current);
    } catch (e) {
      console.error('[SlideCanvas] Failed to process/inject HTML:', e);
      return;
    }

    // Skip editor logic in read-only mode
    if (props.readOnly) return;

    // Wait one tick for DOM to render
    initLogicTimer = setTimeout(() => {
      if (logicInstanceRef.current) {
        logicInstanceRef.current.destroy();
      }

      try {
        logicInstanceRef.current = new SlideEditorLogic(
          shadowRootRef.current!,
          (data: any) => onElementSelectRef.current?.(data),
          () => onChangeRef.current?.(),
          () => renderEquationsInRoot(shadowRootRef.current!)
        );
        logicInstanceRef.current.setScale(zoomRef.current);
      } catch (e) {
        console.error('[SlideCanvas] Failed to initialize Logic Core:', e);
      }
    }, 10);

    return () => {
      if (initLogicTimer) {
        clearTimeout(initLogicTimer);
        initLogicTimer = null;
      }
      if (logicInstanceRef.current) {
        logicInstanceRef.current.destroy();
        logicInstanceRef.current = null;
      }
    };
  }, [props.slideId, props.readOnly]);

  // For readOnly instances: re-inject when htmlContent changes.
  useEffect(() => {
    if (!props.readOnly || !shadowRootRef.current) return;
    shadowRootRef.current.innerHTML = processHTML(props.htmlContent, true);
    injectFontLinksToDocumentHead(props.htmlContent);
    applyConverterScaleFallback(shadowRootRef.current);
    renderEquationsInRoot(shadowRootRef.current);
  }, [props.htmlContent]); // eslint-disable-line react-hooks/exhaustive-deps

  // Sync zoom to logic instance
  useEffect(() => {
    if (props.zoom !== undefined) {
      logicInstanceRef.current?.setScale(props.zoom);
    }
  }, [props.zoom]);

  return (
    <div
      ref={containerRef}
      className="w-full h-full shadow-2xl"
      style={{
        width: '1920px',
        height: '1080px',
        minWidth: '1920px',
        minHeight: '1080px',
        position: 'relative'
      }}
    />
  );
});

SlideCanvas.displayName = "SlideCanvas";
