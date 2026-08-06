// Mixin: snap-to-grid / smart alignment guide lines
export const SnapGuideMixin = {

    // Keep the snap feel consistent in screen pixels while the slide is
    // zoomed to fit the editor viewport.
    getSnapThreshold() {
        const scale = Number.isFinite(this.currentScale) && this.currentScale > 0
            ? this.currentScale
            : 1;
        return Math.max(6, 8 / scale);
    },

    getSnapBounds(el) {
        if (this.getElementBounds) {
            const b = this.getElementBounds(el);
            return {
                left: b.left,
                top: b.top,
                width: b.width,
                height: b.height,
            };
        }
        return {
            left: el.offsetLeft,
            top: el.offsetTop,
            width: el.offsetWidth,
            height: el.offsetHeight,
        };
    },

    snapToGuides(el, x, y) {
        const guides = [];
        const dragBounds = this.getSnapBounds(el);
        const elW = dragBounds.width;
        const elH = dragBounds.height;
        const canvasW = this.canvas.offsetWidth || 1920;
        const canvasH = this.canvas.offsetHeight || 1080;
        const threshold = this.getSnapThreshold();

        // Each object exposes three alignment anchors per axis: start,
        // center and end. The dragged object is tested against all of them.
        const dX = [x, x + elW / 2, x + elW];
        const dY = [y, y + elH / 2, y + elH];
        const xCandidates = [];
        const yCandidates = [];

        const addTarget = (left, top, width, height, priority) => {
            const targetX = [left, left + width / 2, left + width];
            const targetY = [top, top + height / 2, top + height];

            dX.forEach((dragAnchor, dragIndex) => {
                targetX.forEach(targetAnchor => {
                    xCandidates.push({
                        distance: Math.abs(dragAnchor - targetAnchor),
                        value: targetAnchor - [0, elW / 2, elW][dragIndex],
                        guide: {
                            type: 'vertical',
                            pos: targetAnchor,
                            from: 0,
                            to: canvasH,
                        },
                        priority,
                    });
                });
            });

            dY.forEach((dragAnchor, dragIndex) => {
                targetY.forEach(targetAnchor => {
                    yCandidates.push({
                        distance: Math.abs(dragAnchor - targetAnchor),
                        value: targetAnchor - [0, elH / 2, elH][dragIndex],
                        guide: {
                            type: 'horizontal',
                            pos: targetAnchor,
                            from: 0,
                            to: canvasW,
                        },
                        priority,
                    });
                });
            });
        };

        // Slide edges and center are always available targets.
        addTarget(0, 0, canvasW, canvasH, 1);

        // Align against every other top-level selectable element. Object
        // alignment wins ties against a slide-wide target.
        const otherElements = Array.from(this.canvas.querySelectorAll('[data-selectable]'))
            .filter(other => !this.selectedElements.includes(other))
            .filter(other => other !== el && !other.classList?.contains('smart-guide'));

        otherElements.forEach(other => {
            const bounds = this.getSnapBounds(other);
            if (bounds.width > 0 && bounds.height > 0) {
                addTarget(bounds.left, bounds.top, bounds.width, bounds.height, 2);
            }
        });

        const best = (candidates) => candidates
            .filter(candidate => candidate.distance <= threshold)
            .sort((a, b) => a.distance - b.distance || b.priority - a.priority)[0] || null;

        const bestX = best(xCandidates);
        const bestY = best(yCandidates);
        if (bestX) {
            x = bestX.value;
            guides.push(bestX.guide);
        }
        if (bestY) {
            y = bestY.value;
            guides.push(bestY.guide);
        }

        return { x, y, guides };
    },

    drawSmartGuides(guides) {
        if (this._guideTimeout) {
            clearTimeout(this._guideTimeout);
            this._guideTimeout = null;
        }

        if (!guides || guides.length === 0) {
            this.clearSmartGuides();
            return;
        }

        const incoming = new Map();
        guides.forEach(guide => {
            const key = `${guide.type}-${Math.round(guide.pos)}`;
            if (!incoming.has(key)) incoming.set(key, guide);
        });

        // Reuse existing line nodes to avoid flicker during fast pointer moves.
        this.canvas.querySelectorAll('.smart-guide').forEach(line => {
            const key = line.dataset.guideKey;
            if (!incoming.has(key)) {
                line.remove();
                return;
            }

            const guide = incoming.get(key);
            if (guide.type === 'vertical') {
                line.style.top = `${guide.from ?? 0}px`;
                line.style.height = `${(guide.to ?? this.canvas.offsetHeight) - (guide.from ?? 0)}px`;
            } else {
                line.style.left = `${guide.from ?? 0}px`;
                line.style.width = `${(guide.to ?? this.canvas.offsetWidth) - (guide.from ?? 0)}px`;
            }
            incoming.delete(key);
        });

        incoming.forEach((guide, key) => {
            const line = document.createElement('div');
            line.className = 'smart-guide';
            line.dataset.guideKey = key;
            line.style.position = 'absolute';
            line.style.backgroundColor = '#ff3d82';
            line.style.pointerEvents = 'none';
            line.style.zIndex = '10000';
            line.style.borderRadius = '999px';
            line.style.opacity = '0.9';

            if (guide.type === 'vertical') {
                const from = guide.from ?? 0;
                const to = guide.to ?? this.canvas.offsetHeight;
                line.style.left = `${guide.pos}px`;
                line.style.top = `${from}px`;
                line.style.width = '2px';
                line.style.height = `${to - from}px`;
                line.style.boxShadow = '0 0 6px 1px rgba(255, 61, 130, 0.65)';
            } else {
                const from = guide.from ?? 0;
                const to = guide.to ?? this.canvas.offsetWidth;
                line.style.top = `${guide.pos}px`;
                line.style.left = `${from}px`;
                line.style.height = '2px';
                line.style.width = `${to - from}px`;
                line.style.boxShadow = '0 0 6px 1px rgba(255, 61, 130, 0.65)';
            }

            this.canvas.appendChild(line);
        });
    },

    clearSmartGuides() {
        if (this._guideTimeout) {
            clearTimeout(this._guideTimeout);
            this._guideTimeout = null;
        }
        this.canvas.querySelectorAll('.smart-guide').forEach(guide => guide.remove());
    },
};
