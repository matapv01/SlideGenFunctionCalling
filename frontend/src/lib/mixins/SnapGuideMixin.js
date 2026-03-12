// Mixin: snap-to-grid / smart alignment guide lines
export const SnapGuideMixin = {

    snapToGuides(el, x, y) {
        const guides = [];
        const elW     = el.offsetWidth;
        const elH     = el.offsetHeight;
        const canvasW = this.canvas.offsetWidth;
        const canvasH = this.canvas.offsetHeight;

        // --- Canvas edge snaps ---
        if (Math.abs(x) < this.snapThreshold) {
            x = 0;
            guides.push({ type: 'vertical', pos: 0, from: 0, to: canvasH });
        }
        if (Math.abs(x + elW - canvasW) < this.snapThreshold) {
            x = canvasW - elW;
            guides.push({ type: 'vertical', pos: canvasW, from: 0, to: canvasH });
        }
        if (Math.abs(y) < this.snapThreshold) {
            y = 0;
            guides.push({ type: 'horizontal', pos: 0, from: 0, to: canvasW });
        }
        if (Math.abs(y + elH - canvasH) < this.snapThreshold) {
            y = canvasH - elH;
            guides.push({ type: 'horizontal', pos: canvasH, from: 0, to: canvasW });
        }

        // --- Canvas center snaps ---
        const centerX = canvasW / 2;
        const centerY = canvasH / 2;
        if (Math.abs(x + elW / 2 - centerX) < this.snapThreshold) {
            x = centerX - elW / 2;
            guides.push({ type: 'vertical', pos: centerX, from: 0, to: canvasH });
        }
        if (Math.abs(y + elH / 2 - centerY) < this.snapThreshold) {
            y = centerY - elH / 2;
            guides.push({ type: 'horizontal', pos: centerY, from: 0, to: canvasW });
        }

        // --- Element-to-element snapping ---
        const otherElements = Array.from(this.canvas.querySelectorAll('[data-selectable]'))
            .filter(other => !this.selectedElements.includes(other));

        if (otherElements.length > 0) {
            let snapX = null, snapY = null;
            let minDistX = this.snapThreshold, minDistY = this.snapThreshold;
            let pendingXGuide = null, pendingYGuide = null;

            const dL = x,       dR  = x + elW,     dCX = x + elW / 2;
            const dT = y,       dB  = y + elH,     dCY = y + elH / 2;

            otherElements.forEach(other => {
                const oL  = other.offsetLeft;
                const oT  = other.offsetTop;
                const oW  = other.offsetWidth;
                const oH  = other.offsetHeight;
                const oR  = oL + oW;
                const oB  = oT + oH;
                const oCX = oL + oW / 2;
                const oCY = oT + oH / 2;

                // X-axis: 3 dragged points × 3 target points = 9 combinations
                [
                    { dragPt: dL,  snapPt: oL,  newX: oL },
                    { dragPt: dL,  snapPt: oCX, newX: oCX },
                    { dragPt: dL,  snapPt: oR,  newX: oR },
                    { dragPt: dCX, snapPt: oL,  newX: oL  - elW / 2 },
                    { dragPt: dCX, snapPt: oCX, newX: oCX - elW / 2 },
                    { dragPt: dCX, snapPt: oR,  newX: oR  - elW / 2 },
                    { dragPt: dR,  snapPt: oL,  newX: oL  - elW },
                    { dragPt: dR,  snapPt: oCX, newX: oCX - elW },
                    { dragPt: dR,  snapPt: oR,  newX: oR  - elW },
                ].forEach(({ dragPt, snapPt, newX }) => {
                    const dist = Math.abs(dragPt - snapPt);
                    if (dist < minDistX) {
                        minDistX = dist;
                        snapX    = newX;
                        pendingXGuide = {
                            type: 'vertical', pos: snapPt,
                            from: Math.min(dT, oT),
                            to:   Math.max(dB, oB),
                        };
                    }
                });

                // Y-axis: 3 × 3 combinations
                [
                    { dragPt: dT,  snapPt: oT,  newY: oT },
                    { dragPt: dT,  snapPt: oCY, newY: oCY },
                    { dragPt: dT,  snapPt: oB,  newY: oB },
                    { dragPt: dCY, snapPt: oT,  newY: oT  - elH / 2 },
                    { dragPt: dCY, snapPt: oCY, newY: oCY - elH / 2 },
                    { dragPt: dCY, snapPt: oB,  newY: oB  - elH / 2 },
                    { dragPt: dB,  snapPt: oT,  newY: oT  - elH },
                    { dragPt: dB,  snapPt: oCY, newY: oCY - elH },
                    { dragPt: dB,  snapPt: oB,  newY: oB  - elH },
                ].forEach(({ dragPt, snapPt, newY }) => {
                    const dist = Math.abs(dragPt - snapPt);
                    if (dist < minDistY) {
                        minDistY = dist;
                        snapY    = newY;
                        pendingYGuide = {
                            type: 'horizontal', pos: snapPt,
                            from: Math.min(dL, oL),
                            to:   Math.max(dR, oR),
                        };
                    }
                });
            });

            if (snapX !== null) { x = snapX; if (pendingXGuide) guides.push(pendingXGuide); }
            if (snapY !== null) { y = snapY; if (pendingYGuide) guides.push(pendingYGuide); }
        }

        return { x, y, guides };
    },

    drawSmartGuides(guides) {
        // Cancel any pending post-drag clear — guides are actively needed
        if (this._guideTimeout) {
            clearTimeout(this._guideTimeout);
            this._guideTimeout = null;
        }

        if (!guides || guides.length === 0) {
            this.clearSmartGuides();
            return;
        }

        // Build deduplicated key → guide map
        const incoming = new Map();
        guides.forEach(g => {
            const key = `${g.type}-${Math.round(g.pos)}`;
            if (!incoming.has(key)) incoming.set(key, g);
        });

        // Update existing guides in-place (prevents 1-frame flicker), remove stale ones
        this.canvas.querySelectorAll('.smart-guide').forEach(el => {
            const key = el.dataset.guideKey;
            if (!incoming.has(key)) {
                el.remove();
            } else {
                // Update span so the line stretches correctly as element moves
                const guide = incoming.get(key);
                if (guide.type === 'vertical') {
                    const from = guide.from ?? 0;
                    const to   = guide.to   ?? this.canvas.offsetHeight;
                    el.style.top    = `${from}px`;
                    el.style.height = `${to - from}px`;
                } else {
                    const from = guide.from ?? 0;
                    const to   = guide.to   ?? this.canvas.offsetWidth;
                    el.style.left  = `${from}px`;
                    el.style.width = `${to - from}px`;
                }
                incoming.delete(key); // already handled
            }
        });

        // Create brand-new guide elements for keys not yet on canvas
        incoming.forEach((guide, key) => {
            const line = document.createElement('div');
            line.className        = 'smart-guide';
            line.dataset.guideKey = key;
            line.style.position       = 'absolute';
            line.style.backgroundColor = '#ff3d82';
            line.style.pointerEvents   = 'none';
            line.style.zIndex          = '10000';

            if (guide.type === 'vertical') {
                const from = guide.from ?? 0;
                const to   = guide.to   ?? this.canvas.offsetHeight;
                line.style.left      = `${guide.pos}px`;
                line.style.top       = `${from}px`;
                line.style.width     = '1.5px';
                line.style.height    = `${to - from}px`;
                line.style.boxShadow = '0 0 5px 1px rgba(255, 61, 130, 0.7)';
            } else {
                const from = guide.from ?? 0;
                const to   = guide.to   ?? this.canvas.offsetWidth;
                line.style.top       = `${guide.pos}px`;
                line.style.left      = `${from}px`;
                line.style.height    = '1.5px';
                line.style.width     = `${to - from}px`;
                line.style.boxShadow = '0 0 5px 1px rgba(255, 61, 130, 0.7)';
            }

            this.canvas.appendChild(line);
        });
    },

    clearSmartGuides() {
        // Cancel any scheduled clear first
        if (this._guideTimeout) {
            clearTimeout(this._guideTimeout);
            this._guideTimeout = null;
        }
        this.canvas.querySelectorAll('.smart-guide').forEach(g => g.remove());
    },
};
