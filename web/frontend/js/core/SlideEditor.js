// SlideEditor Main Class
import { SlideCapture } from '../capture/SlideCapture.js';
import { ExportMixin } from './mixins/ExportMixin.js';
import { PresentationMixin } from './mixins/PresentationMixin.js';
// Use global config loaded from config.js in head
const config = window.config || { BACKEND_URL: 'http://localhost:12008' };

export class SlideEditor {
    constructor() {
        this.canvas = document.getElementById('canvas');
        this.canvasContainer = document.getElementById('canvasContainer');
        this.propertiesContent = document.getElementById('propertiesContent');
        this.slidesList = document.getElementById('slidesList');

        this.verticalGuide = document.getElementById('vertical-guide');
        this.horizontalGuide = document.getElementById('horizontal-guide');
        this.snapThreshold = 5;

        // --- NEW: For Distance Guides ---
        this.isAltDown = false;
        this.distanceGuidesContainer = document.getElementById('distance-guides-container');
        // --- END NEW ---

        // Smart guides and visual feedback (Canva-style)
        this.smartGuides = [];
        this.distanceIndicators = [];
        this.isShowingGrid = false;
        this.snapZones = [];
        this.multiSelectBounds = null;

        this.slides = [];
        this.currentSlideIndex = 0;
        this.slideIdCounter = 1;

        this.selectedElements = [];
        this.clipboard = null;
        this.zIndexCounter = 1;

        // Drag & Drop for slides
        this.draggedSlideIndex = null;
        this.dragOverSlideIndex = null;

        this.isDragging = false;
        this.isResizing = false;
        this.resizeHandleType = '';
        this.draggedElement = null; // Track element being dragged
        this.disableTemplateDrag = false; // Flag to disable template drag
        this.justFinishedDragging = false; // Flag to prevent click after drag
        this.isTextSelecting = false; // Flag to allow text selection

        this.dragStart = { x: 0, y: 0 };
        this.elementsStartPos = new Map();

        this.zoomLevel = 1;
        this.mode = 'select';

        this.history = [];
        this.historyIndex = -1;

        this.savedSelectionRange = null;

        // Database auto-save
        this.currentProjectId = null; // Will be set when loading from database
        this.currentProjectTitle = null; // Store project title
        this.slideIds = []; // Store database slide IDs for each slide
        this._saveTimeout = null;

        // Presentation mode
        this.presentationMode = false;
        this.presentationSlideIndex = 0;
        this.presentationKeyboardHandler = null;
        this.fullscreenChangeHandler = null;

        // Initialize SlideCapture
        this.slideCapture = new SlideCapture(this);

        this.createFirstSlide();
        this.bindEvents();
        this.initializeSmartGuides();
        this.fitToScreen();
        this.updateProperties();
        this.renderSlidesList();
        this.updateUndoRedoButtons(); // Initialize undo/redo button states

        // Load slides từ URL params hoặc localStorage
        this.loadSlidesFromURLOrStorage();

        // Debounced functions for performance optimization - sau khi tất cả đã init
        this.debouncedUpdateConnectorLines = this.debounce(() => {
            this.updateConnectorLines();
        }, 16); // ~60fps
    }

    // Helper function to check if element type is an icon that should scale
    isIconElement(type) {
        const iconTypes = [
            // Symbols & Icons
            'star', 'star-outline', 'heart', 'heart-outline', 'check', 'cross', 'plus', 'minus',
            'exclamation', 'question', 'info', 'thumbs-up',
            // Business & Office
            'lightbulb', 'target', 'rocket', 'trophy', 'medal', 'briefcase', 'graph', 'calendar',
            'clock', 'money', 'handshake', 'key',
            // Technology
            'laptop', 'phone', 'wifi', 'database', 'cloud', 'gear', 'code', 'bug', 'shield',
            // Nature & Weather
            'sun', 'moon', 'tree', 'flower', 'leaf', 'fire', 'water', 'lightning', 'rainbow',
            // People & Emotions
            'avatar', 'team', 'smile', 'thinking', 'celebration', 'eyes', 'brain', 'muscle', 'clap',
            // Arrows
            'arrow-right', 'arrow-left', 'arrow-up', 'arrow-down', 'arrow-curved', 'arrow-double',
            'arrow-thick', 'arrow-circle', 'arrow-diagonal',
            // Decorative
            'sparkle', 'crown', 'gem', 'confetti', 'ribbon',
            // Food & Objects
            'coffee', 'pizza', 'apple', 'cake', 'book', 'music', 'gift', 'balloon',
            // Math & Science
            'infinity', 'pi', 'sum', 'delta', 'alpha', 'beta', 'microscope', 'atom', 'dna',
            // Transportation
            'car', 'airplane', 'train', 'bike', 'ship', 'bus', 'motorcycle', 'helicopter', 'satellite',
            // Sports & Activities
            'soccer', 'basketball', 'tennis', 'golf', 'swimming', 'running', 'cycling', 'weightlifting', 'yoga',
            // Charts & Diagrams
            'bar-chart', 'pie-chart', 'progress-bar'
        ];
        return iconTypes.includes(type);
    }

    // --- Helper functions for alignment guides ---
    hideGuides() {
        this.verticalGuide.style.display = 'none';
        this.horizontalGuide.style.display = 'none';
    }

    showVerticalGuide(x, y1, y2) {
        this.verticalGuide.style.display = 'block';
        this.verticalGuide.style.left = `${x * this.zoomLevel}px`;
        this.verticalGuide.style.top = `${y1 * this.zoomLevel}px`;
        this.verticalGuide.style.height = `${(y2 - y1) * this.zoomLevel}px`;
        this.verticalGuide.style.transform = `translate(${this.canvas.offsetLeft}px, ${this.canvas.offsetTop}px)`;
    }

    showHorizontalGuide(y, x1, x2) {
        this.horizontalGuide.style.display = 'block';
        this.horizontalGuide.style.top = `${y * this.zoomLevel}px`;
        this.horizontalGuide.style.left = `${x1 * this.zoomLevel}px`;
        this.horizontalGuide.style.width = `${(x2 - x1) * this.zoomLevel}px`;
        this.horizontalGuide.style.transform = `translate(${this.canvas.offsetLeft}px, ${this.canvas.offsetTop}px)`;
    }

    getElementBounds(element) {
        const left = element.offsetLeft;
        const top = element.offsetTop;
        const width = element.offsetWidth;
        const height = element.offsetHeight;
        return {
            left, top, width, height,
            hCenter: left + width / 2,
            right: left + width,
            vCenter: top + height / 2,
            bottom: top + height,
        };
    }

    // Smart Guides and Visual Feedback (Canva-style)
    initializeSmartGuides() {
        // Add canvas grid
        const grid = document.createElement('div');
        grid.className = 'canvas-grid';
        grid.id = 'canvas-grid';
        this.canvas.appendChild(grid);
    }

    createSmartGuide(type, x, y, width, height) {
        const guide = document.createElement('div');
        guide.className = `smart-guide smart-guide-${type}`;
        guide.style.position = 'absolute';
        guide.style.left = `${x}px`;
        guide.style.top = `${y}px`;
        guide.style.width = `${width}px`;
        guide.style.height = `${height}px`;
        guide.style.pointerEvents = 'none';
        guide.style.zIndex = '10000';
        this.canvasContainer.appendChild(guide);
        return guide;
    }

    createDistanceIndicator(x, y, distance, direction) {
        const indicator = document.createElement('div');
        indicator.className = 'distance-indicator';
        indicator.textContent = `${Math.round(distance)}px`;
        indicator.style.position = 'absolute';
        indicator.style.left = `${x}px`;
        indicator.style.top = `${y}px`;
        indicator.style.pointerEvents = 'none';
        indicator.style.zIndex = '10001';
        this.canvasContainer.appendChild(indicator);
        return indicator;
    }

    createDistanceLine(x, y, width, height) {
        const line = document.createElement('div');
        line.className = 'distance-line';
        line.style.position = 'absolute';
        line.style.left = `${x}px`;
        line.style.top = `${y}px`;
        line.style.width = `${width}px`;
        line.style.height = `${height}px`;
        line.style.pointerEvents = 'none';
        line.style.zIndex = '10000';
        this.canvasContainer.appendChild(line);
        return line;
    }

    showSmartGuides(draggedElement, otherElements) {
        this.hideSmartGuides();

        const draggedBounds = this.getElementBounds(draggedElement);
        const guides = [];
        const indicators = [];
        const lines = [];

        // Chỉ hiển thị guides cho 3 elements gần nhất
        const nearbyElements = otherElements
            .map(element => ({
                element,
                bounds: this.getElementBounds(element),
                distance: this.calculateDistance(draggedBounds, this.getElementBounds(element))
            }))
            .sort((a, b) => a.distance - b.distance)
            .slice(0, 3); // Chỉ lấy 3 elements gần nhất

        nearbyElements.forEach(({ element, bounds }) => {
            let hasVerticalGuide = false;
            let hasHorizontalGuide = false;

            // Vertical alignment guides - chỉ hiển thị guide quan trọng nhất
            const verticalAlignments = [
                { pos: bounds.hCenter, type: 'center', priority: 1 }, // Center alignment có priority cao nhất
                { pos: bounds.left, type: 'left', priority: 2 },
                { pos: bounds.right, type: 'right', priority: 2 }
            ].sort((a, b) => a.priority - b.priority);

            for (const { pos, type } of verticalAlignments) {
                if (!hasVerticalGuide && (
                    Math.abs(draggedBounds.left - pos) < this.snapThreshold ||
                    Math.abs(draggedBounds.hCenter - pos) < this.snapThreshold ||
                    Math.abs(draggedBounds.right - pos) < this.snapThreshold)) {

                    const guide = this.createSmartGuide('vertical',
                        pos * this.zoomLevel + this.canvas.offsetLeft,
                        Math.min(draggedBounds.top, bounds.top) * this.zoomLevel + this.canvas.offsetTop,
                        1,
                        Math.abs(Math.max(draggedBounds.bottom, bounds.bottom) - Math.min(draggedBounds.top, bounds.top)) * this.zoomLevel
                    );
                    guides.push(guide);
                    hasVerticalGuide = true;
                    break;
                }
            }

            // Horizontal alignment guides - chỉ hiển thị guide quan trọng nhất
            const horizontalAlignments = [
                { pos: bounds.vCenter, type: 'center', priority: 1 }, // Center alignment có priority cao nhất
                { pos: bounds.top, type: 'top', priority: 2 },
                { pos: bounds.bottom, type: 'bottom', priority: 2 }
            ].sort((a, b) => a.priority - b.priority);

            for (const { pos, type } of horizontalAlignments) {
                if (!hasHorizontalGuide && (
                    Math.abs(draggedBounds.top - pos) < this.snapThreshold ||
                    Math.abs(draggedBounds.vCenter - pos) < this.snapThreshold ||
                    Math.abs(draggedBounds.bottom - pos) < this.snapThreshold)) {

                    const guide = this.createSmartGuide('horizontal',
                        Math.min(draggedBounds.left, bounds.left) * this.zoomLevel + this.canvas.offsetLeft,
                        pos * this.zoomLevel + this.canvas.offsetTop,
                        Math.abs(Math.max(draggedBounds.right, bounds.right) - Math.min(draggedBounds.left, bounds.left)) * this.zoomLevel,
                        1
                    );
                    guides.push(guide);
                    hasHorizontalGuide = true;
                    break;
                }
            }

            // Distance indicators - chỉ cho element gần nhất
            if (nearbyElements.indexOf(nearbyElements.find(item => item.element === element)) === 0) {
                this.showDistanceIndicators(draggedBounds, bounds, indicators, lines);
            }
        });

        // Store guides for cleanup
        this.smartGuides = [...guides, ...indicators, ...lines];

        // Show guides with animation
        setTimeout(() => {
            this.smartGuides.forEach(guide => guide.classList.add('visible'));
        }, 10);
    }

    calculateDistance(bounds1, bounds2) {
        const centerX1 = bounds1.left + bounds1.width / 2;
        const centerY1 = bounds1.top + bounds1.height / 2;
        const centerX2 = bounds2.left + bounds2.width / 2;
        const centerY2 = bounds2.top + bounds2.height / 2;

        return Math.sqrt(Math.pow(centerX2 - centerX1, 2) + Math.pow(centerY2 - centerY1, 2));
    }

    showDistanceIndicators(draggedBounds, targetBounds, indicators, lines) {
        const canvasOffsetX = this.canvas.offsetLeft;
        const canvasOffsetY = this.canvas.offsetTop;

        // Chỉ hiển thị khoảng cách nếu >= 10px và <= 200px (những khoảng cách có ý nghĩa)
        const minDistanceToShow = 10;
        const maxDistanceToShow = 200;

        // Horizontal distance (left/right) - chỉ hiển thị khoảng cách gần nhất
        let closestHorizontalDistance = null;
        let closestHorizontalData = null;

        if (draggedBounds.right < targetBounds.left) {
            const distance = targetBounds.left - draggedBounds.right;
            if (distance >= minDistanceToShow && distance <= maxDistanceToShow) {
                closestHorizontalDistance = distance;
                closestHorizontalData = {
                    distance,
                    lineX: draggedBounds.right * this.zoomLevel + canvasOffsetX,
                    lineY: (Math.max(draggedBounds.top, targetBounds.top) + Math.min(draggedBounds.bottom, targetBounds.bottom)) / 2 * this.zoomLevel + canvasOffsetY,
                    lineWidth: distance * this.zoomLevel,
                    indicatorX: (draggedBounds.right + distance / 2) * this.zoomLevel + canvasOffsetX - 15,
                    indicatorY: (Math.max(draggedBounds.top, targetBounds.top) + Math.min(draggedBounds.bottom, targetBounds.bottom)) / 2 * this.zoomLevel + canvasOffsetY - 10
                };
            }
        }

        if (targetBounds.right < draggedBounds.left) {
            const distance = draggedBounds.left - targetBounds.right;
            if (distance >= minDistanceToShow && distance <= maxDistanceToShow) {
                if (!closestHorizontalDistance || distance < closestHorizontalDistance) {
                    closestHorizontalDistance = distance;
                    closestHorizontalData = {
                        distance,
                        lineX: targetBounds.right * this.zoomLevel + canvasOffsetX,
                        lineY: (Math.max(draggedBounds.top, targetBounds.top) + Math.min(draggedBounds.bottom, targetBounds.bottom)) / 2 * this.zoomLevel + canvasOffsetY,
                        lineWidth: distance * this.zoomLevel,
                        indicatorX: (targetBounds.right + distance / 2) * this.zoomLevel + canvasOffsetX - 15,
                        indicatorY: (Math.max(draggedBounds.top, targetBounds.top) + Math.min(draggedBounds.bottom, targetBounds.bottom)) / 2 * this.zoomLevel + canvasOffsetY - 10
                    };
                }
            }
        }

        // Hiển thị khoảng cách horizontal gần nhất
        if (closestHorizontalData) {
            const line = this.createDistanceLine(
                closestHorizontalData.lineX,
                closestHorizontalData.lineY,
                closestHorizontalData.lineWidth,
                1
            );
            lines.push(line);

            const indicator = this.createDistanceIndicator(
                closestHorizontalData.indicatorX,
                closestHorizontalData.indicatorY,
                closestHorizontalData.distance,
                'horizontal'
            );
            indicators.push(indicator);
        }

        // Vertical distance (top/bottom) - chỉ hiển thị khoảng cách gần nhất
        let closestVerticalDistance = null;
        let closestVerticalData = null;

        if (draggedBounds.bottom < targetBounds.top) {
            const distance = targetBounds.top - draggedBounds.bottom;
            if (distance >= minDistanceToShow && distance <= maxDistanceToShow) {
                closestVerticalDistance = distance;
                closestVerticalData = {
                    distance,
                    lineX: (Math.max(draggedBounds.left, targetBounds.left) + Math.min(draggedBounds.right, targetBounds.right)) / 2 * this.zoomLevel + canvasOffsetX,
                    lineY: draggedBounds.bottom * this.zoomLevel + canvasOffsetY,
                    lineHeight: distance * this.zoomLevel,
                    indicatorX: (Math.max(draggedBounds.left, targetBounds.left) + Math.min(draggedBounds.right, targetBounds.right)) / 2 * this.zoomLevel + canvasOffsetX + 5,
                    indicatorY: (draggedBounds.bottom + distance / 2) * this.zoomLevel + canvasOffsetY - 8
                };
            }
        }

        if (targetBounds.bottom < draggedBounds.top) {
            const distance = draggedBounds.top - targetBounds.bottom;
            if (distance >= minDistanceToShow && distance <= maxDistanceToShow) {
                if (!closestVerticalDistance || distance < closestVerticalDistance) {
                    closestVerticalDistance = distance;
                    closestVerticalData = {
                        distance,
                        lineX: (Math.max(draggedBounds.left, targetBounds.left) + Math.min(draggedBounds.right, targetBounds.right)) / 2 * this.zoomLevel + canvasOffsetX,
                        lineY: targetBounds.bottom * this.zoomLevel + canvasOffsetY,
                        lineHeight: distance * this.zoomLevel,
                        indicatorX: (Math.max(draggedBounds.left, targetBounds.left) + Math.min(draggedBounds.right, targetBounds.right)) / 2 * this.zoomLevel + canvasOffsetX + 5,
                        indicatorY: (targetBounds.bottom + distance / 2) * this.zoomLevel + canvasOffsetY - 8
                    };
                }
            }
        }

        // Hiển thị khoảng cách vertical gần nhất
        if (closestVerticalData) {
            const line = this.createDistanceLine(
                closestVerticalData.lineX,
                closestVerticalData.lineY,
                1,
                closestVerticalData.lineHeight
            );
            lines.push(line);

            const indicator = this.createDistanceIndicator(
                closestVerticalData.indicatorX,
                closestVerticalData.indicatorY,
                closestVerticalData.distance,
                'vertical'
            );
            indicators.push(indicator);
        }
    }

    hideSmartGuides() {
        // Remove all smart guides
        this.smartGuides.forEach(guide => guide.remove());
        this.smartGuides = [];

        // Also remove any remaining guides that might be left over
        this.canvasContainer.querySelectorAll('.smart-guide, .distance-indicator, .distance-line').forEach(el => el.remove());
    }

    showCanvasGrid() {
        const grid = document.getElementById('canvas-grid');
        if (grid) {
            grid.classList.add('visible');
            this.isShowingGrid = true;
        }
    }

    hideCanvasGrid() {
        const grid = document.getElementById('canvas-grid');
        if (grid) {
            grid.classList.remove('visible');
            this.isShowingGrid = false;
        }
    }

    addDragVisualFeedback(element) {
        element.classList.add('dragging');
    }

    removeDragVisualFeedback() {
        this.canvas.querySelectorAll('.element').forEach(el => {
            el.classList.remove('dragging', 'drag-preview');
        });

        this.hideCanvasGrid();
        this.hideSmartGuides();
    }

    getSnapPosition(draggedBounds, otherElements) {
        let snapX = null;
        let snapY = null;
        let minDistanceX = this.snapThreshold;
        let minDistanceY = this.snapThreshold;

        otherElements.forEach(element => {
            const bounds = this.getElementBounds(element);

            // Horizontal snapping
            const xAlignments = [
                bounds.left, bounds.hCenter, bounds.right
            ];
            const draggedXPoints = [
                draggedBounds.left, draggedBounds.hCenter, draggedBounds.right
            ];

            draggedXPoints.forEach(draggedX => {
                xAlignments.forEach(targetX => {
                    const distance = Math.abs(draggedX - targetX);
                    if (distance < minDistanceX) {
                        minDistanceX = distance;
                        snapX = targetX - (draggedX - draggedBounds.left);
                    }
                });
            });

            // Vertical snapping
            const yAlignments = [
                bounds.top, bounds.vCenter, bounds.bottom
            ];
            const draggedYPoints = [
                draggedBounds.top, draggedBounds.vCenter, draggedBounds.bottom
            ];

            draggedYPoints.forEach(draggedY => {
                yAlignments.forEach(targetY => {
                    const distance = Math.abs(draggedY - targetY);
                    if (distance < minDistanceY) {
                        minDistanceY = distance;
                        snapY = targetY - (draggedY - draggedBounds.top);
                    }
                });
            });
        });

        return { snapX, snapY };
    }

    // --- NEW: Functions for distance measurement guides ---
    handleAltKey(e, isDown) {
        if (e.key === 'Alt') {
            e.preventDefault();
            this.isAltDown = isDown;
            if (!isDown) {
                this.hideDistanceGuides();
            }
        }
    }

    handleElementHover(e, targetElement, eventType) {
        e.stopPropagation();
        if (eventType === 'out' || !this.isAltDown) {
            this.hideDistanceGuides();
            return;
        }

        if (this.isAltDown && this.selectedElements.length === 1) {
            const sourceElement = this.selectedElements[0];
            if (sourceElement !== targetElement) {
                this.showDistanceGuides(sourceElement, targetElement);
            }
        }
    }

    hideDistanceGuides() {
        Array.from(this.distanceGuidesContainer.children).forEach(child => child.style.display = 'none');
    }

    showDistanceGuides(sourceEl, targetEl) {
        this.hideDistanceGuides();
        const sBounds = this.getElementBounds(sourceEl);
        const tBounds = this.getElementBounds(targetEl);
        const canvasOffsetLeft = this.canvas.offsetLeft;
        const canvasOffsetTop = this.canvas.offsetTop;

        const draw = (id, styles, text) => {
            const line = document.getElementById(`dist-line-${id}`);
            const label = document.getElementById(`dist-label-${id}`);
            if (!line || !label) return;

            const finalStyles = {
                left: (val) => `${(val * this.zoomLevel) + canvasOffsetLeft}px`,
                top: (val) => `${(val * this.zoomLevel) + canvasOffsetTop}px`,
                width: (val) => `${Math.max(0, val * this.zoomLevel)}px`,
                height: (val) => `${Math.max(0, val * this.zoomLevel)}px`,
            };

            line.style.left = finalStyles.left(styles.lineLeft);
            line.style.top = finalStyles.top(styles.lineTop);
            line.style.width = finalStyles.width(styles.lineWidth);
            line.style.height = finalStyles.height(styles.lineHeight);

            label.style.left = finalStyles.left(styles.labelLeft);
            label.style.top = finalStyles.top(styles.labelTop);

            label.innerText = Math.round(text);
            line.style.display = 'block';
            label.style.display = 'block';
        };

        // BOTTOM of source to TOP of target
        const distBottom = tBounds.top - sBounds.bottom;
        if (distBottom >= 0) {
            const hCenter = (Math.max(sBounds.left, tBounds.left) + Math.min(sBounds.right, tBounds.right)) / 2;
            draw('bottom', {
                lineLeft: hCenter, lineTop: sBounds.bottom, lineWidth: 1, lineHeight: distBottom,
                labelLeft: hCenter, labelTop: sBounds.bottom + distBottom / 2
            }, distBottom);
        }

        // TOP of source to BOTTOM of target
        const distTop = sBounds.top - tBounds.bottom;
        if (distTop >= 0) {
            const hCenter = (Math.max(sBounds.left, tBounds.left) + Math.min(sBounds.right, tBounds.right)) / 2;
            draw('top', {
                lineLeft: hCenter, lineTop: tBounds.bottom, lineWidth: 1, lineHeight: distTop,
                labelLeft: hCenter, labelTop: tBounds.bottom + distTop / 2
            }, distTop);
        }

        // RIGHT of source to LEFT of target
        const distRight = tBounds.left - sBounds.right;
        if (distRight >= 0) {
            const vCenter = (Math.max(sBounds.top, tBounds.top) + Math.min(sBounds.bottom, tBounds.bottom)) / 2;
            draw('right', {
                lineLeft: sBounds.right, lineTop: vCenter, lineWidth: distRight, lineHeight: 1,
                labelLeft: sBounds.right + distRight / 2, labelTop: vCenter
            }, distRight);
        }

        // LEFT of source to RIGHT of target
        const distLeft = sBounds.left - tBounds.right;
        if (distLeft >= 0) {
            const vCenter = (Math.max(sBounds.top, tBounds.top) + Math.min(sBounds.bottom, tBounds.bottom)) / 2;
            draw('left', {
                lineLeft: tBounds.right, lineTop: vCenter, lineWidth: distLeft, lineHeight: 1,
                labelLeft: tBounds.right + distLeft / 2, labelTop: vCenter
            }, distLeft);
        }
    }
    // --- END NEW ---

    handleMouseMove(e) {
        // Nếu đang chuẩn bị drag, check xem đã di chuyển đủ xa chưa
        if (this.isPreparedForDrag && !this.isDragging && this.dragStart) {
            const distanceMoved = Math.sqrt(
                Math.pow(e.clientX - this.dragStart.x, 2) +
                Math.pow(e.clientY - this.dragStart.y, 2)
            );

            // Chỉ bắt đầu drag thật khi đã di chuyển >5px
            if (distanceMoved > 5) {
                this.isDragging = true;
                this.isPreparedForDrag = false;
                // IMPORTANT: Disable template/file drag events khi đang drag element
                this.disableTemplateDrag = true;
            } else {
                // Chưa di chuyển đủ xa, không làm gì
                return;
            }
        }

        if (this.isResizing) {
            if (this.selectedElements.length !== 1) return;

            // Store reference to prevent tampering
            const targetElement = this.selectedElements[0];

            const dx = (e.clientX - this.dragStart.x) / this.zoomLevel;
            const dy = (e.clientY - this.dragStart.y) / this.zoomLevel;
            const el = targetElement;
            const startRect = this.elementsStartPos.get(el);
            if (!startRect) return; // Safety check
            const { x, y, width, height } = startRect;

            let newWidth = width;
            let newHeight = height;

            if (this.resizeHandleType.includes('r')) {
                newWidth = Math.max(20, width + dx);
                el.style.width = `${newWidth}px`;
            }
            if (this.resizeHandleType.includes('l')) {
                newWidth = Math.max(20, width - dx);
                el.style.width = `${newWidth}px`;
                el.style.left = `${x + dx}px`;
            }
            if (this.resizeHandleType.includes('b')) {
                newHeight = Math.max(20, height + dy);
                el.style.height = `${newHeight}px`;
            }
            if (this.resizeHandleType.includes('t')) {
                newHeight = Math.max(20, height - dy);
                el.style.height = `${newHeight}px`;
                el.style.top = `${y + dy}px`;
            }

            // ONLY scale font size for the specific element being resized
            if (el.dataset.type && this.isIconElement(el.dataset.type)) {
                // Triple check this is the correct element
                if (this.selectedElements[0] !== el || targetElement !== el) {
                    console.warn('Element mismatch during resize!');
                    return;
                }

                // Get current actual dimensions
                const currentWidth = parseInt(el.style.width) || newWidth;
                const currentHeight = parseInt(el.style.height) || newHeight;
                const minDimension = Math.min(currentWidth, currentHeight);
                const fontSize = Math.max(16, Math.min(300, minDimension * 0.7));

                // Apply ONLY to this specific element
                el.style.fontSize = `${fontSize}px`;
            }

            this.updateProperties();
            return;
        }

        if (this.isDragging && this.selectedElements.length > 0) {
            // Hide old guides
            this.hideGuides();

            let finalDx = (e.clientX - this.dragStart.x) / this.zoomLevel;
            let finalDy = (e.clientY - this.dragStart.y) / this.zoomLevel;

            const primaryElement = this.selectedElements[0];
            const startPos = this.elementsStartPos.get(primaryElement);

            // Calculate current bounds for the primary element
            const currentBounds = {
                left: startPos.x + finalDx,
                top: startPos.y + finalDy,
                width: primaryElement.offsetWidth,
                height: primaryElement.offsetHeight
            };
            currentBounds.right = currentBounds.left + currentBounds.width;
            currentBounds.bottom = currentBounds.top + currentBounds.height;
            currentBounds.hCenter = currentBounds.left + currentBounds.width / 2;
            currentBounds.vCenter = currentBounds.top + currentBounds.height / 2;

            // Get snap targets (elements not being dragged)
            const snapTargets = Array.from(this.canvas.querySelectorAll(':scope > .element'))
                .filter(el => !this.selectedElements.includes(el));

            // Calculate snap position
            const snapResult = this.getSnapPosition(currentBounds, snapTargets);

            if (snapResult.snapX !== null) {
                finalDx = snapResult.snapX - startPos.x;
            }
            if (snapResult.snapY !== null) {
                finalDy = snapResult.snapY - startPos.y;
            }

            // Update element positions
            this.selectedElements.forEach(el => {
                const elStartPos = this.elementsStartPos.get(el);
                if (elStartPos) {
                    el.style.left = `${elStartPos.x + finalDx}px`;
                    el.style.top = `${elStartPos.y + finalDy}px`;
                }
            });

            // Show smart guides and distance indicators
            if (snapTargets.length > 0) {
                const updatedBounds = {
                    ...currentBounds,
                    left: startPos.x + finalDx,
                    top: startPos.y + finalDy
                };
                updatedBounds.right = updatedBounds.left + updatedBounds.width;
                updatedBounds.bottom = updatedBounds.top + updatedBounds.height;
                updatedBounds.hCenter = updatedBounds.left + updatedBounds.width / 2;
                updatedBounds.vCenter = updatedBounds.top + updatedBounds.height / 2;

                // Create temporary element for bounds calculation
                const tempElement = {
                    offsetLeft: updatedBounds.left,
                    offsetTop: updatedBounds.top,
                    offsetWidth: updatedBounds.width,
                    offsetHeight: updatedBounds.height
                };

                this.showSmartGuides(tempElement, snapTargets);
            }

            if (this.selectedElements.length === 1) this.updateProperties();

            // IMPROVED: Chỉ update connector lines khi THỰC SỰ cần thiết (khi đang drag element)
            // Không update khi chỉ hover chuột để tránh nhảy lung tung
            if (this.isDragging && (this.draggedElement && !this.draggedElement.classList.contains('connector-line'))) {
                if (this.debouncedUpdateConnectorLines) {
                    this.debouncedUpdateConnectorLines();
                } else {
                    // Fallback nếu debounced function chưa sẵn sàng
                    this.updateConnectorLines();
                }
            }
        }
    }

    handleMouseUp(e) {
        // Reset text selection flag
        this.isTextSelecting = false;

        // Clean up visual feedback
        this.removeDragVisualFeedback();
        this.hideGuides();

        // Xử lý pending select: chỉ select nếu không có kéo chuột
        if (this.pendingSelectElement) {
            let shouldSelect = true;

            if (this.dragStart && e) {
                const distanceMoved = Math.sqrt(
                    Math.pow(e.clientX - this.dragStart.x, 2) +
                    Math.pow(e.clientY - this.dragStart.y, 2)
                );
                // Nếu có kéo chuột (>2px) thì không select
                shouldSelect = distanceMoved <= 2;
            }

            if (shouldSelect) {
                this.selectElement(this.pendingSelectElement);
            }

            this.pendingSelectElement = null;
            this.dragStart = null;
            return;
        }

        if (this.isDragging || this.isResizing) {
            // Check if there was actual movement (not just a click)
            let hasActualChange = false;

            if (this.dragStart && e) {
                // Calculate distance moved
                const distanceMoved = Math.sqrt(
                    Math.pow(e.clientX - this.dragStart.x, 2) +
                    Math.pow(e.clientY - this.dragStart.y, 2)
                );

                // Only consider it a real change if moved more than 3 pixels
                // This filters out accidental tiny movements and pure clicks
                hasActualChange = distanceMoved > 3;
            }

            if (hasActualChange) {
                // Set flag để tránh click event ngay sau drag
                this.justFinishedDragging = true;
                setTimeout(() => {
                    this.justFinishedDragging = false;
                }, 100);

                // ENHANCED: Force final update cho connectors sau khi drag xong
                // Tạm thời bypass check để force update
                const wasDragging = this.isDragging;
                const wasResizing = this.isResizing;

                // Set flags để bypass the restriction
                this.forceConnectorUpdate = true;
                this.updateConnectorLinesForced();
                this.forceConnectorUpdate = false;

                // Only save state if there was actual movement
                this.saveState();
            }
        }

        this.isDragging = false;
        this.isResizing = false;
        this.isPreparedForDrag = false; // Reset prepared flag
        this.pendingSelectElement = null; // Reset pending select
        this.draggedElement = null; // Reset dragged element
        this.disableTemplateDrag = false; // Re-enable template drag
        this.elementsStartPos.clear();
        this.dragStart = null; // Reset drag start position
    }

    createFirstSlide() {
        const slide = {
            id: this.slideIdCounter++,
            name: 'Slide 1',
            content: `
            <div class="element" data-type="text" style="left: 100px; top: 200px; width: 1000px; height: auto; font-size: 84px; font-weight: 800; color: #2d3748; z-index: 1; overflow: visible;" contenteditable="true">Welcome to SlideGenius</div>
    <div class="element" data-type="text" style="left: 100px; top: 400px; width: 800px; height: auto; font-size: 32px; color: #667eea; z-index: 2; overflow: visible;" contenteditable="true">Create stunning presentations with ease</div>
        `,
            backgroundColor: 'linear-gradient(135deg, #f0f4f8 0%, #ffffff 100%)',
            zIndexCounter: 4
        };
        this.slides.push(slide);
        this.loadSlide(0);
        this.saveState();
    }

    async createNewSlide() {
        // Save current slide first
        this.saveCurrentSlide();

        const slideContent = `
        <div class="element" data-type="text" style="left: 200px; top: 300px; width: 600px; height: auto; font-size: 64px; font-weight: 700; color: #2d3748; z-index: 1;" contenteditable="true">New Slide</div>
        <div class="element" data-type="rectangle" style="position: absolute; left: 900px; top: 300px; z-index: 2; width: 300px; height: 200px; background: linear-gradient(135deg, rgb(102, 126, 234), rgb(118, 75, 162)); border-radius: 12px;"></div>
    `;

        const slide = {
            id: this.slideIdCounter++,
            name: `Slide ${this.slides.length + 1}`,
            content: slideContent,
            backgroundColor: 'linear-gradient(135deg, #ffffff 0%, #f7fafc 100%)',
            zIndexCounter: 3
        };

        // Add new slide to the array
        this.slides.push(slide);

        // Create in database if project is loaded from DB
        if (this.currentProjectId) {
            try {
                const apiUrl = window.config?.BACKEND_URL || 'http://localhost:3000';
                const token = localStorage.getItem('access_token');

                const htmlContent = `
                <div class="slide-container">
                    <div class="content-wrapper" style="background: ${slide.backgroundColor};">
                        ${slideContent}
                    </div>
                </div>
            `;

                const response = await fetch(`${apiUrl}/api/projects/${this.currentProjectId}/slides`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        slide_index: this.slides.length - 1,
                        slide_type: 'content',
                        title: slide.name,
                        html_content: htmlContent
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    this.slideIds.push(data.id);
                    console.log(`✅ Created slide in database with ID: ${data.id}`);
                } else {
                    console.error('❌ Failed to create slide in database');
                }
            } catch (error) {
                console.error('❌ Error creating slide in database:', error);
            }
        }

        // Update names for all slides
        this.updateSlideNames();

        // Switch to the new slide
        this.currentSlideIndex = this.slides.length - 1;
        this.loadSlide(this.currentSlideIndex);

        // Re-render slides list to show the new slide
        this.renderSlidesList();

        // Save state
        this.saveState();

        // Add a small visual feedback
        const newSlideElement = this.slidesList.querySelector(`.slide-item:last-child`);
        if (newSlideElement) {
            newSlideElement.style.transform = 'scale(1.05)';
            newSlideElement.style.background = 'rgba(102, 126, 234, 0.1)';
            setTimeout(() => {
                newSlideElement.style.transform = '';
                newSlideElement.style.background = '';
            }, 300);
        }
    }

    async duplicateCurrentSlide() {
        if (this.slides.length === 0) return;
        this.saveCurrentSlide();
        const currentSlide = this.slides[this.currentSlideIndex];
        const newSlide = {
            id: this.slideIdCounter++,
            name: `Slide ${this.slides.length + 1}`,
            content: currentSlide.content,
            backgroundColor: currentSlide.backgroundColor,
            zIndexCounter: currentSlide.zIndexCounter
        };
        this.slides.push(newSlide);

        // Create in database if project is loaded from DB
        if (this.currentProjectId) {
            try {
                const apiUrl = window.config?.BACKEND_URL || 'http://localhost:3000';
                const token = localStorage.getItem('access_token');

                const htmlContent = `
                <div class="slide-container">
                    <div class="content-wrapper" style="background: ${newSlide.backgroundColor};">
                        ${newSlide.content}
                    </div>
                </div>
            `;

                const response = await fetch(`${apiUrl}/api/projects/${this.currentProjectId}/slides`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        slide_index: this.slides.length - 1,
                        slide_type: 'content',
                        title: newSlide.name,
                        html_content: htmlContent
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    this.slideIds.push(data.id);
                    console.log(`✅ Duplicated slide in database with ID: ${data.id}`);
                } else {
                    console.error('❌ Failed to duplicate slide in database');
                }
            } catch (error) {
                console.error('❌ Error duplicating slide in database:', error);
            }
        }

        this.switchToSlide(this.slides.length - 1);
        this.updateSlideNames(); // Update all slide names after duplicating
    }

    deleteSlide(index) {
        if (this.slides.length <= 1) {
            this.showNotification('❌ Cannot delete the last slide', 'error');
            return;
        }

        // Show custom confirmation modal
        this.showDeleteConfirmation(index);
    }

    showDeleteConfirmation(index) {
        const slideName = this.slides[index].name || `Slide ${index + 1}`;

        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(4px);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.2s ease;
    `;

        // Create modal
        const modal = document.createElement('div');
        modal.style.cssText = `
        background: white;
        border-radius: 16px;
        padding: 32px;
        max-width: 450px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: slideUp 0.3s ease;
    `;

        modal.innerHTML = `
        <style>
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
        </style>
        <div style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">🗑️</div>
            <h3 style="margin: 0 0 12px 0; font-size: 24px; color: #1f2937;">Delete Slide?</h3>
            <p style="margin: 0 0 24px 0; color: #6b7280; font-size: 14px;">
                Are you sure you want to delete <strong>${slideName}</strong>?<br>
                This action cannot be undone.
            </p>
            <div style="display: flex; gap: 12px; justify-content: center;">
                <button id="cancelDelete" style="
                    padding: 12px 24px;
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    background: white;
                    color: #6b7280;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                ">Cancel</button>
                <button id="confirmDelete" style="
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    background: #ef4444;
                    color: white;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                ">Delete Slide</button>
            </div>
        </div>
    `;

        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        // Add hover effects
        const cancelBtn = modal.querySelector('#cancelDelete');
        const confirmBtn = modal.querySelector('#confirmDelete');

        cancelBtn.onmouseover = () => cancelBtn.style.background = '#f9fafb';
        cancelBtn.onmouseout = () => cancelBtn.style.background = 'white';

        confirmBtn.onmouseover = () => confirmBtn.style.background = '#dc2626';
        confirmBtn.onmouseout = () => confirmBtn.style.background = '#ef4444';

        // Handle buttons
        cancelBtn.onclick = () => {
            overlay.style.animation = 'fadeOut 0.2s ease';
            setTimeout(() => overlay.remove(), 200);
        };

        confirmBtn.onclick = () => {
            overlay.remove();
            this.executeDeleteSlide(index);
        };

        // Close on overlay click
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                overlay.style.animation = 'fadeOut 0.2s ease';
                setTimeout(() => overlay.remove(), 200);
            }
        };
    }

    async executeDeleteSlide(index) {
        // Delete from database if loaded from DB
        if (this.currentProjectId && this.slideIds[index]) {
            const slideId = this.slideIds[index];
            try {
                const apiUrl = window.config?.BACKEND_URL || 'http://localhost:3000';
                const token = localStorage.getItem('access_token');

                const response = await fetch(`${apiUrl}/api/slides/${slideId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to delete from database');
                }

                console.log(`✅ Deleted slide ${slideId} from database`);
            } catch (error) {
                console.error('❌ Error deleting slide from database:', error);
                this.showNotification('⚠️ Failed to delete from database', 'error');
            }
        }

        // Remove from local arrays
        this.slides.splice(index, 1);
        if (this.slideIds.length > index) {
            this.slideIds.splice(index, 1);
        }

        // Update current slide index
        if (this.currentSlideIndex >= this.slides.length) {
            this.currentSlideIndex = this.slides.length - 1;
        } else if (this.currentSlideIndex > index) {
            this.currentSlideIndex--;
        }

        this.updateSlideNames();
        this.loadSlide(this.currentSlideIndex);
        this.renderSlidesList();
        this.saveState();

        this.showNotification('✓ Slide deleted successfully', 'success');
    }

    switchToSlide(index) {
        if (index < 0 || index >= this.slides.length) return;
        this.saveCurrentSlide();
        this.currentSlideIndex = index;
        this.loadSlide(index);
        this.renderSlidesList();
        // Don't save state on slide navigation - only save on content edits
    }

    saveCurrentSlide() {
        if (this.slides.length === 0) return;

        // DELAY để đảm bảo background stable sau text operations
        clearTimeout(this.saveTimeout);
        this.saveTimeout = setTimeout(() => {
            console.log('💾 saveCurrentSlide triggered');

            const currentSlide = this.slides[this.currentSlideIndex];
            currentSlide.content = this.canvas.innerHTML;

            // IMPROVED: Lấy background từ multiple sources
            let backgroundColor = 'white';

            // Method 1: từ data attribute (most reliable)
            const dataBg = this.canvas.getAttribute('data-bg');
            if (dataBg) {
                backgroundColor = dataBg;
                console.log('💾 Saved background from data-bg:', backgroundColor);
            } else if (this.canvas.style.backgroundColor) {
                // Method 2: từ inline style
                backgroundColor = this.canvas.style.backgroundColor;
                console.log('💾 Saved background from style.backgroundColor:', backgroundColor);
            } else if (this.canvas.style.background) {
                backgroundColor = this.canvas.style.background;
                console.log('💾 Saved background from style.background:', backgroundColor);
            } else {
                // Method 3: từ computed style
                const computedBg = window.getComputedStyle(this.canvas).backgroundColor;
                if (computedBg && computedBg !== 'rgba(0, 0, 0, 0)' && computedBg !== 'transparent') {
                    backgroundColor = computedBg;
                    console.log('💾 Saved background from computed style:', backgroundColor);
                } else {
                    console.log('💾 No background found, using white');
                }
            }

            currentSlide.backgroundColor = backgroundColor;
            currentSlide.zIndexCounter = this.zIndexCounter;

            console.log('💾 Slide saved with background:', backgroundColor);
        }, 50); // 50ms delay để text operations complete
    }

    loadSlide(index) {
        if (index < 0 || index >= this.slides.length) return;
        const slide = this.slides[index];
        console.log('📋 LoadSlide: index=' + index + ', backgroundColor=' + slide.backgroundColor);

        // Store background trong slide object
        if (!slide.backgroundColor || slide.backgroundColor === 'undefined') {
            slide.backgroundColor = 'white';
        }

        // Clear any existing monitoring
        this.stopBackgroundMonitoring();

        this.canvas.innerHTML = slide.content;

        // IMPORTANT: Auto-add .element class to elements from converter HTML
        // These elements have position:absolute but no .element class yet
        Array.from(this.canvas.children).forEach(el => {
            if (el.nodeType !== 1) return; // Skip non-element nodes

            const tag = el.tagName.toLowerCase();
            // Skip non-visual elements
            if (['style', 'script', 'link', 'meta', 'svg'].includes(tag)) return;

            // Check both inline style property and style attribute
            const hasAbsolutePosition = el.style.position === 'absolute' ||
                (el.getAttribute('style') && el.getAttribute('style').includes('position: absolute'));

            if (hasAbsolutePosition) {
                // Add .element class if missing
                if (!el.classList.contains('element')) {
                    el.classList.add('element');
                    console.log('➕ Auto-added .element class to:', tag);
                }

                // Auto-detect and set data-type if missing
                if (!el.dataset.type) {
                    let elementType = 'shape'; // default

                    const hasImage = el.querySelector('img') || tag === 'img';
                    const hasVideo = el.querySelector('video') || tag === 'video';
                    const textContent = el.textContent?.trim() || '';
                    const hasSignificantText = textContent.length > 3; // At least 4 characters

                    // Explicit text tags always get text type if they have content
                    const explicitTextTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'li', 'blockquote', 'pre', 'a'];

                    // DIV only becomes text if it has significant text AND no background/decorative styling
                    const isDivWithText = tag === 'div' && hasSignificantText;
                    const hasBackgroundStyling = el.style.background || el.style.backgroundColor ||
                        el.style.backgroundImage || el.style.borderRadius;

                    if (hasImage) {
                        elementType = 'image';
                    } else if (hasVideo) {
                        elementType = 'video';
                    } else if (explicitTextTags.includes(tag) && hasSignificantText) {
                        // Explicit text tags with content are always text
                        elementType = 'text';
                    } else if (isDivWithText && !hasBackgroundStyling) {
                        // DIV with text and no decorative styling
                        elementType = 'text';
                    } else if (hasSignificantText && !hasBackgroundStyling) {
                        // Any element with text and no decoration
                        elementType = 'text';
                    } else {
                        // Everything else is a shape (decorative elements, backgrounds, etc.)
                        elementType = 'shape';
                    }

                    el.dataset.type = elementType;
                    console.log('🏷️ Auto-set data-type:', elementType, 'for', tag, `(text: "${textContent.substring(0, 30)}...")`);
                }

                // Add contenteditable ONLY for text elements
                if (el.dataset.type === 'text' && !el.hasAttribute('contenteditable')) {
                    el.setAttribute('contenteditable', 'true');
                    console.log('✏️ Auto-added contenteditable to:', tag);
                }

                // Generate unique ID if missing
                if (!el.id) {
                    el.id = `element_${el.dataset.type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
                    console.log('🆔 Generated ID:', el.id);
                }
            }
        });

        // SIMPLE BUT BULLETPROOF: Direct DOM manipulation
        this.applyDirectBackground(slide.backgroundColor);

        console.log('🎨 Applied DIRECT background:', slide.backgroundColor, 'for slide', index);

        this.zIndexCounter = slide.zIndexCounter || 1;
        this.initElements();

        // Cập nhật chiều cao cho tất cả text elements sau khi load slide
        this.updateAllTextElementsHeight();

        this.selectElement(null);
    }

    applyDirectBackground(backgroundColor) {
        console.log('🔧 Applying direct background:', backgroundColor);

        // Method 1: BRUTE FORCE - Override everything possible (ONLY for canvas)
        const canvas = this.canvas;

        // Clear all conflicting styles
        canvas.style.background = '';
        canvas.style.backgroundColor = '';
        canvas.removeAttribute('class');

        // Apply with MAXIMUM specificity (ONLY for canvas)
        canvas.setAttribute('id', 'canvas');
        canvas.setAttribute('data-bg', backgroundColor);
        canvas.style.cssText = `
        position: relative !important;
        width: 1920px !important;
        height: 1080px !important;
        background: ${backgroundColor} !important;
        background-color: ${backgroundColor} !important;
        margin: 0 auto !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1) !important;
        border-radius: 8px !important;
        transform-origin: top left !important;
        transition: transform 0.3s ease !important;
        overflow: hidden !important;
        transform: scale(${this.zoomLevel || 1}) !important;
    `;

        // Method 2: Create PERSISTENT style tag với timestamp (ONLY for canvas)
        const timestamp = Date.now();
        const styleId = `bg-${timestamp}`;

        // Remove any old background style tags
        document.querySelectorAll('style[id^="bg-"]').forEach(style => {
            style.remove();
        });

        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
        #canvas[data-bg="${backgroundColor}"] {
            background: ${backgroundColor} !important;
            background-color: ${backgroundColor} !important;
        }
        /* Ensure body background is protected */
        body {
            background: var(--bg-canvas) !important;
        }
    `;
        document.head.appendChild(style);

        // Method 3: AGGRESSIVE monitoring - check mỗi 100ms (ONLY for canvas)
        if (this.aggressiveMonitor) clearInterval(this.aggressiveMonitor);
        this.aggressiveMonitor = setInterval(() => {
            const currentBg = window.getComputedStyle(canvas).backgroundColor;
            const expectedBg = backgroundColor;

            // Check if background color changed ONLY for canvas
            if (currentBg !== expectedBg && currentBg !== 'transparent') {
                canvas.style.setProperty('background', expectedBg, 'important');
                canvas.style.setProperty('background-color', expectedBg, 'important');

                // Also update slide object immediately
                if (this.slides && this.slides[this.currentSlideIndex]) {
                    this.slides[this.currentSlideIndex].backgroundColor = expectedBg;
                }
            }

            // Ensure body background is protected
            const body = document.body;
            const currentBodyBg = window.getComputedStyle(body).backgroundColor;
            const expectedBodyBg = getComputedStyle(document.documentElement).getPropertyValue('--bg-canvas').trim();
            if (currentBodyBg !== expectedBodyBg && !currentBodyBg.includes('240, 244, 248')) {
                body.style.setProperty('background', 'var(--bg-canvas)', 'important');
            }
        }, 100);

        // Method 4: Force reapply in next tick (ONLY for canvas)
        requestAnimationFrame(() => {
            canvas.style.setProperty('background', backgroundColor, 'important');
            canvas.style.setProperty('background-color', backgroundColor, 'important');
        });

    }

    startDOMBackgroundMonitoring(backgroundColor) {
        // Clear previous monitoring
        this.stopBackgroundMonitoring();

        // Method 1: MutationObserver để track DOM changes
        this.bgObserver = new MutationObserver(() => {
            const wrapper = document.getElementById('canvas-bg-wrapper');
            if (!wrapper) {
                // Wrapper bị xóa, tạo lại
                this.createBackgroundWrapper(backgroundColor, 0);
            } else if (wrapper.style.background !== backgroundColor) {
                // Background bị đổi, restore
                wrapper.style.background = backgroundColor;
                wrapper.style.backgroundColor = backgroundColor;
            }
        });

        this.bgObserver.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class']
        });

        // Method 2: Backup interval mỗi 1 giây (slow but sure)
        this.backupBgInterval = setInterval(() => {
            const wrapper = document.getElementById('canvas-bg-wrapper');
            if (!wrapper) {
                this.createBackgroundWrapper(backgroundColor, 0);
            }
        }, 1000);

        console.log('� DOM monitoring started for:', backgroundColor);
    }

    stopBackgroundMonitoring() {
        if (this.aggressiveMonitor) {
            clearInterval(this.aggressiveMonitor);
            this.aggressiveMonitor = null;
        }
        if (this.bgObserver) {
            this.bgObserver.disconnect();
            this.bgObserver = null;
        }
        if (this.backupBgInterval) {
            clearInterval(this.backupBgInterval);
            this.backupBgInterval = null;
        }
        if (this.ultimateBgInterval) {
            clearInterval(this.ultimateBgInterval);
            this.ultimateBgInterval = null;
        }

        // Clean up old style tags
        const oldStyles = document.querySelectorAll('style[id^="bg-"]');
        oldStyles.forEach(style => style.remove());

        console.log('🧹 Background monitoring stopped and cleaned');
    }

    preserveBackgroundAfterTextEdit() {
        // Get current slide background
        const currentSlide = this.slides[this.currentSlideIndex];
        if (!currentSlide || !currentSlide.backgroundColor) return;

        const expectedBg = currentSlide.backgroundColor;
        const currentBg = window.getComputedStyle(this.canvas).backgroundColor;

        console.log('🛡️ Preserving background after text edit:', expectedBg);

        // Force reapply if background changed
        if (currentBg !== expectedBg) {
            console.log('🚨 Background lost during text edit! Restoring:', expectedBg);
            this.applyDirectBackground(expectedBg);
        } else {
            // Ensure data-bg is set even if colors match
            this.canvas.setAttribute('data-bg', expectedBg);
            this.canvas.style.setProperty('background-color', expectedBg, 'important');
        }
    }

    // Update canvas zoom - no wrapper needed anymore
    updateBackgroundWrapperZoom() {
        // Method này đã đơn giản hóa, chỉ update zoom của canvas
        if (this.canvas) {
            const currentBg = this.canvas.style.backgroundColor || 'white';
            this.canvas.style.transform = `scale(${this.zoomLevel || 1})`;
            // Force reapply background after zoom
            this.canvas.style.setProperty('background-color', currentBg, 'important');
            console.log('🔄 Updated canvas zoom and background:', this.zoomLevel, currentBg);
        }
    }

    renderSlidesList() {
        this.slidesList.innerHTML = '';
        this.slides.forEach((slide, index) => {
            const slideElement = document.createElement('div');
            slideElement.className = `slide-item ${index === this.currentSlideIndex ? 'active' : ''}`;
            slideElement.draggable = true;
            slideElement.dataset.slideIndex = index;
            slideElement.innerHTML = `
            <div class="slide-thumbnail">
                <div style="font-size: 8px; padding: 2px; color: #718096; font-weight: 600;">${index + 1}</div>
            </div>
            <div class="slide-info">
                <div class="slide-name">Slide ${index + 1}</div>
                <div class="slide-elements">${this.getSlideElementsCount(slide)} elements</div>
            </div>
            <div class="slide-actions">
                <button class="slide-action-btn" data-action="duplicate" data-slide-index="${index}" title="Duplicate">⧉</button>
                ${this.slides.length > 1 ? `<button class="slide-action-btn" data-action="delete" data-slide-index="${index}" title="Delete">🗑</button>` : ''}
            </div>
        `;

            // Drag & Drop event listeners
            slideElement.addEventListener('dragstart', (e) => this.handleSlideDragStart(e, index));
            slideElement.addEventListener('dragover', (e) => this.handleSlideDragOver(e, index));
            slideElement.addEventListener('dragleave', (e) => this.handleSlideDragLeave(e, index));
            slideElement.addEventListener('drop', (e) => this.handleSlideDrop(e, index));
            slideElement.addEventListener('dragend', (e) => this.handleSlideDragEnd(e));

            slideElement.addEventListener('click', (e) => {
                if (e.target.closest('.slide-action-btn')) {
                    return;
                }
                this.switchToSlide(index);
            });

            this.slidesList.appendChild(slideElement);
        });

        // Add global drag leave handler for the slides container
        this.slidesList.addEventListener('dragleave', (e) => {
            // Check if we're leaving the slides list entirely
            if (!this.slidesList.contains(e.relatedTarget)) {
                this.clearPreviewMovement(); // Return slides to original positions
            }
        });

        this.slidesList.querySelectorAll('.slide-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = e.currentTarget.dataset.action;
                const slideIndex = parseInt(e.currentTarget.dataset.slideIndex);

                if (action === 'duplicate') this.duplicateSlideAtIndex(slideIndex);
                else if (action === 'delete') this.deleteSlide(slideIndex);
            });
        });
    }

    duplicateSlideAtIndex(index) {
        this.saveCurrentSlide();
        const slide = this.slides[index];
        const newSlide = {
            id: this.slideIdCounter++,
            name: `Slide ${this.slides.length + 1}`,
            content: slide.content,
            backgroundColor: slide.backgroundColor,
            zIndexCounter: slide.zIndexCounter
        };
        this.slides.splice(index + 1, 0, newSlide);
        this.updateSlideNames(); // Update all slide names after duplication
        this.switchToSlide(index + 1);
    }

    updateSlideNames() {
        this.slides.forEach((slide, index) => {
            slide.name = `Slide ${index + 1}`;
        });
    }

    // Enhanced Drag & Drop handlers for slides
    handleSlideDragStart(e, index) {
        this.draggedSlideIndex = index;
        e.currentTarget.classList.add('dragging');

        // Add visual feedback to slides list
        this.slidesList.classList.add('dragging-active');

        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', index.toString());

        // Add subtle animation to other slides
        this.slidesList.querySelectorAll('.slide-item:not(.dragging)').forEach(item => {
            item.style.transition = 'transform 0.2s ease, opacity 0.2s ease';
            item.style.opacity = '0.8';
        });
    }

    handleSlideDragOver(e, index) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';

        if (this.draggedSlideIndex !== null && this.draggedSlideIndex !== index) {
            // Remove all existing drag-over classes
            this.slidesList.querySelectorAll('.slide-item').forEach(item => {
                item.classList.remove('drag-over');
            });

            // Calculate if we should insert above or below based on cursor position
            const rect = e.currentTarget.getBoundingClientRect();
            const mouseY = e.clientY;
            const itemMiddle = rect.top + rect.height / 2;

            // Determine insertion position
            let insertionIndex;
            if (mouseY < itemMiddle) {
                insertionIndex = index;
                e.currentTarget.style.borderTop = '3px solid var(--primary-color)';
                e.currentTarget.style.borderBottom = '';
            } else {
                insertionIndex = index + 1;
                e.currentTarget.style.borderBottom = '3px solid var(--primary-color)';
                e.currentTarget.style.borderTop = '';
            }

            this.dragOverSlideIndex = insertionIndex;

            // Enhanced visual feedback
            e.currentTarget.classList.add('drag-over');

            // Preview slide movement
            this.previewSlideMovement(this.draggedSlideIndex, insertionIndex);
        }
    }

    handleSlideDragLeave(e, index) {
        // Clear visual feedback when leaving
        e.currentTarget.classList.remove('drag-over');
        e.currentTarget.style.borderTop = '';
        e.currentTarget.style.borderBottom = '';

        // Only clear preview if we're leaving the entire slides list
        if (!this.slidesList.contains(e.relatedTarget)) {
            this.clearPreviewMovement();
        }
    }

    handleSlideDrop(e, dropIndex) {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-over');
        e.currentTarget.style.borderTop = '';
        e.currentTarget.style.borderBottom = '';

        if (this.draggedSlideIndex !== null && this.dragOverSlideIndex !== null) {
            const fromIndex = this.draggedSlideIndex;
            const toIndex = this.dragOverSlideIndex;

            if (fromIndex !== toIndex) {
                this.moveSlide(fromIndex, toIndex);
            }
        }
    }

    handleSlideDragEnd(e) {
        // Clean up dragging state
        e.currentTarget.classList.remove('dragging');
        this.slidesList.classList.remove('dragging-active');

        // Reset all slide opacity and transitions
        this.slidesList.querySelectorAll('.slide-item').forEach(item => {
            item.classList.remove('drag-over', 'drag-placeholder');
            item.style.opacity = '';
            item.style.transition = '';
            item.style.borderTop = '';
            item.style.borderBottom = '';
        });

        // Clean up drag state
        this.draggedSlideIndex = null;
        this.dragOverSlideIndex = null;

        // Clear animations
        this.clearPreviewMovement();
    }

    addRippleEffect(index) {
        // Add subtle ripple effect to nearby slides
        const slideItem = this.slidesList.children[index];
        if (slideItem) {
            const adjacentSlides = [
                this.slidesList.children[index - 1],
                this.slidesList.children[index + 1]
            ].filter(Boolean);

            adjacentSlides.forEach(slide => {
                slide.style.transform = 'scale(0.98)';
                slide.style.transition = 'transform 0.2s ease';

                setTimeout(() => {
                    slide.style.transform = '';
                }, 200);
            });
        }
    }

    previewSlideMovement(fromIndex, toIndex) {
        // Clear any existing preview classes
        this.slidesList.querySelectorAll('.slide-item').forEach(item => {
            item.classList.remove('preview-push-down', 'preview-push-up', 'preview-space');
        });

        // Don't preview if it's the same position
        if (fromIndex === toIndex) return;

        const slideItems = this.slidesList.querySelectorAll('.slide-item');

        // Calculate actual insertion index
        let insertIndex = toIndex;
        if (fromIndex < toIndex) {
            insertIndex = toIndex - 1;
        }

        // Preview movement animation
        slideItems.forEach((item, index) => {
            if (index === fromIndex) return; // Skip the dragged slide

            if (fromIndex < insertIndex) {
                // Moving down: slides between original and new position move up
                if (index > fromIndex && index <= insertIndex) {
                    item.classList.add('preview-push-up');
                }
            } else {
                // Moving up: slides between new and original position move down
                if (index >= insertIndex && index < fromIndex) {
                    item.classList.add('preview-push-down');
                }
            }
        });
    }

    clearPreviewMovement() {
        this.slidesList.querySelectorAll('.slide-item').forEach(item => {
            item.classList.remove('preview-push-down', 'preview-push-up', 'preview-space');
            item.style.transition = '';
            item.style.transform = '';
            item.style.marginTop = '';
        });
    }

    moveSlide(fromIndex, toIndex) {
        // Save current slide before moving
        this.saveCurrentSlide();

        // Clear any preview animations
        this.clearPreviewMovement();

        // Don't move if it's the same position
        if (fromIndex === toIndex) return;

        // Calculate actual insertion index
        let insertIndex = toIndex;
        if (fromIndex < toIndex) {
            insertIndex = toIndex - 1;
        }

        // Get the slide to move
        const slideToMove = this.slides[fromIndex];

        // Remove slide from original position
        this.slides.splice(fromIndex, 1);

        // Insert slide at new position
        this.slides.splice(insertIndex, 0, slideToMove);

        // Update current slide index
        if (this.currentSlideIndex === fromIndex) {
            // The dragged slide becomes the new current slide
            this.currentSlideIndex = insertIndex;
        } else if (fromIndex < this.currentSlideIndex && insertIndex >= this.currentSlideIndex) {
            // Slide moved from before current to after current
            this.currentSlideIndex--;
        } else if (fromIndex > this.currentSlideIndex && insertIndex <= this.currentSlideIndex) {
            // Slide moved from after current to before current
            this.currentSlideIndex++;
        }

        // Update slide names and re-render
        this.updateSlideNames();
        this.renderSlidesList();
        this.saveState();

        // Ensure current slide is loaded correctly
        this.loadSlide(this.currentSlideIndex);
    }

    getSlideElementsCount(slide) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = slide.content;

        // Count elements with .element class OR position:absolute (same logic as loadSlide auto-detect)
        let count = 0;
        Array.from(tempDiv.children).forEach(child => {
            if (child.nodeType !== 1) return; // Skip non-element nodes

            const tag = child.tagName.toLowerCase();
            // Skip non-visual elements
            if (['style', 'script', 'link', 'meta', 'svg'].includes(tag)) return;

            // Check both .element class AND position:absolute
            const hasElementClass = child.classList.contains('element');
            const hasAbsolutePosition = child.style.position === 'absolute' ||
                (child.getAttribute('style') && child.getAttribute('style').includes('position: absolute'));

            if (hasElementClass || hasAbsolutePosition) {
                count++;
            }
        });

        return count;
    }

    initElements() {
        this.canvas.querySelectorAll(':scope > .element').forEach(element => {
            this.makeElementInteractive(element);
        });
    }

    makeElementInteractive(element) {
        const newElement = element.cloneNode(true);
        element.parentNode.replaceChild(newElement, element);
        this.addResizeHandles(newElement);

        newElement.addEventListener('mousedown', (e) => this.handleMouseDown(e, newElement));

        // Detect hover near edges for cursor change
        newElement.addEventListener('mousemove', (e) => {
            if (!newElement.classList.contains('selected')) return;

            // Skip if hovering over resize handles or drag handle - LET THEM HANDLE THEIR OWN CURSOR
            if (e.target.classList.contains('resize-handle') ||
                e.target.classList.contains('drag-handle')) {
                return; // Don't interfere with handles
            }

            const isTextElement = newElement.hasAttribute('contenteditable') ||
                newElement.querySelector('[contenteditable="true"]');

            // Lấy rect của element chính (không phải contenteditable bên trong)
            const rect = newElement.getBoundingClientRect();
            const edgeThreshold = 15; // pixels from edge

            const isNearEdge =
                e.clientX - rect.left < edgeThreshold ||
                rect.right - e.clientX < edgeThreshold ||
                e.clientY - rect.top < edgeThreshold ||
                rect.bottom - e.clientY < edgeThreshold;

            // Set cursor cho tất cả các phần tử liên quan (KHÔNG BAO GỒM HANDLES)
            if (isTextElement) {
                // Tìm tất cả contenteditable elements (có thể là chính nó hoặc con)
                const editableElements = [];
                if (newElement.hasAttribute('contenteditable')) {
                    editableElements.push(newElement);
                }
                const children = newElement.querySelectorAll('[contenteditable="true"]');
                children.forEach(child => editableElements.push(child));

                // Set cursor cho tất cả
                const targetCursor = isNearEdge ? 'move' : 'text';
                editableElements.forEach(el => {
                    el.style.cursor = targetCursor;
                });
                // Don't override newElement cursor if it's not contenteditable itself
                if (!newElement.hasAttribute('contenteditable')) {
                    newElement.style.cursor = isNearEdge ? 'move' : 'default';
                }
            } else {
                // Non-text elements
                newElement.style.cursor = isNearEdge ? 'move' : 'default';
            }
        });

        newElement.addEventListener('click', (e) => {
            e.stopPropagation();
            // Special handling for curved connectors
            if (newElement.classList.contains('connector-line') && newElement.classList.contains('curved')) {
                this.selectElement(newElement);
                if (newElement._controlPoints) {
                    newElement._controlPoints.forEach(cp => {
                        cp.style.opacity = '1';
                    });
                }
            } else {
                this.selectElement(newElement);
            }
        });

        // ENHANCED: Add double-click handler for connector lines and text elements
        newElement.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            if (newElement.classList.contains('connector-line')) {
                console.log('🔄 Double-clicked connector line, showing style selector');
                this.selectElement(newElement);
                setTimeout(() => {
                    this.showConnectorTypeSelector();
                }, 10);
            } else if (newElement.hasAttribute('contenteditable')) {
                // Enter text editing mode
                e.preventDefault();
                newElement.focus();
                this.isTextSelecting = true;
                // Select all text on double-click
                if (window.getSelection) {
                    const selection = window.getSelection();
                    const range = document.createRange();
                    range.selectNodeContents(newElement);
                    selection.removeAllRanges();
                    selection.addRange(range);
                }
            }
        });

        newElement.addEventListener('contextmenu', (e) => this.showContextMenu(e, newElement));

        // --- NEW: Events for distance guides ---
        newElement.addEventListener('mouseover', (e) => this.handleElementHover(e, newElement, 'over'));
        newElement.addEventListener('mouseout', (e) => this.handleElementHover(e, newElement, 'out'));
        // --- END NEW ---

        if (newElement.hasAttribute('contenteditable')) {
            // Store original text content when element is focused
            newElement.addEventListener('focus', () => {
                newElement._originalTextContent = newElement.innerHTML;
            });

            newElement.addEventListener('blur', () => {
                this.savedSelectionRange = null;

                // PROTECTION: Ensure background is preserved after text editing
                this.preserveBackgroundAfterTextEdit();

                // Only save state if text actually changed
                if (newElement._originalTextContent !== newElement.innerHTML) {
                    this.saveState();
                }
                delete newElement._originalTextContent;
            });
            newElement.addEventListener('mouseup', () => this._saveSelection());
            newElement.addEventListener('keyup', () => this._saveSelection());

            // Additional protection for text selection/editing
            newElement.addEventListener('input', () => {
                this.preserveBackgroundAfterTextEdit();
                this.updateTextElementHeight(newElement); // Cập nhật chiều cao khi gõ
            });
            newElement.addEventListener('paste', () => {
                setTimeout(() => {
                    this.preserveBackgroundAfterTextEdit();
                    this.updateTextElementHeight(newElement); // Cập nhật chiều cao sau khi paste
                }, 10);
            });
        }

        if (newElement.classList.contains('group-container')) {
            newElement.querySelectorAll('.element').forEach(child => this.makeElementInteractive(child));
        }
    }

    addResizeHandles(element) {
        if (element.classList.contains('group-container') || element.querySelector('.resize-handle')) return;

        let handlesHTML = `
        <div class="resize-handle tl"></div> <div class="resize-handle tr"></div>
        <div class="resize-handle bl"></div> <div class="resize-handle br"></div>
    `;

        // Add drag handle for text elements
        if (element.dataset.type === 'text' || element.hasAttribute('contenteditable')) {
            handlesHTML += `<div class="drag-handle" title="Drag to move">⠿</div>`;
        }

        element.insertAdjacentHTML('beforeend', handlesHTML);
    }

    bindEvents() {
        document.getElementById('selectBtn').addEventListener('click', () => this.setMode('select'));
        document.getElementById('textBtn').addEventListener('click', () => this.setMode('text'));
        document.getElementById('propertiesBtn').addEventListener('click', () => this.toggleProperties());
        document.getElementById('toggleSlidesBtn').addEventListener('click', () => this.toggleSlides());
        document.getElementById('resetViewBtn').addEventListener('click', () => this.fitToScreen());
        document.getElementById('undoBtn').addEventListener('click', () => this.undo());
        document.getElementById('redoBtn').addEventListener('click', () => this.redo());
        // document.getElementById('exportBtn').addEventListener('click', () => this.showExportOptions());

        // Capture buttons
        // document.getElementById('captureCurrentBtn').addEventListener('click', () => this.captureCurrentSlide());
        // document.getElementById('captureAllBtn').addEventListener('click', () => this.captureAllSlides());

        // Present button - show dropdown
        const presentBtn = document.getElementById('presentBtn');
        const presentDropdown = document.getElementById('presentDropdown');

        presentBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            presentDropdown.classList.toggle('show');
        });

        // Handle dropdown items
        document.querySelectorAll('.present-dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = item.dataset.action;
                presentDropdown.classList.remove('show');

                if (action === 'from-start') {
                    this.startPresentation(true);
                } else if (action === 'from-current') {
                    this.startPresentation(false);
                }
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            presentDropdown.classList.remove('show');
        });

        // PDF export buttons
        // document.getElementById('exportPdfBtn').addEventListener('click', () => this.exportCurrentSlideToPdf());
        document.getElementById('exportAllPdfBtn').addEventListener('click', () => this.exportAllSlidesToPdf());

        document.getElementById('newSlideBtn').addEventListener('click', () => this.createNewSlide());
        document.getElementById('duplicateSlideBtn').addEventListener('click', () => this.duplicateCurrentSlide());

        document.getElementById('importBtn').addEventListener('click', () => document.getElementById('importFile').click());
        document.getElementById('importFile').addEventListener('change', (e) => this.importSlides(e));

        document.getElementById('zoomIn').addEventListener('click', () => this.zoom(this.zoomLevel * 1.2));
        document.getElementById('zoomOut').addEventListener('click', () => this.zoom(this.zoomLevel / 1.2));
        window.addEventListener('resize', () => this.fitToScreen());
        document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        document.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        document.addEventListener('keydown', (e) => { this.handleKeyDown(e); this.handleAltKey(e, true); });
        document.addEventListener('keyup', (e) => this.handleAltKey(e, false));
        this.canvasContainer.addEventListener('click', (e) => this.handleGlobalClick(e));

        document.getElementById('contextMenu').addEventListener('click', (e) => {
            const menuItem = e.target.closest('.context-menu-item');
            if (menuItem) {
                const action = menuItem.dataset.action;
                if (action) this.handleContextMenuAction(action);
            }
        });

        document.querySelectorAll('.element-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const elementType = e.currentTarget.dataset.element;
                if (elementType === 'image') document.getElementById('imageFile').click();
                else if (elementType === 'video') document.getElementById('videoFile').click();
                else this.createElement(elementType);
            });
        });

        // Template drag and drop events
        document.querySelectorAll('.template-item').forEach(item => {
            item.addEventListener('dragstart', (e) => this.handleTemplateDragStart(e));
            item.addEventListener('dragend', (e) => this.handleTemplateDragEnd(e));
        });

        // Unified canvas drag and drop events (handles both templates and files)
        this.canvas.addEventListener('dragover', (e) => this.handleUnifiedDragOver(e));
        this.canvas.addEventListener('dragleave', (e) => this.handleUnifiedDragLeave(e));
        this.canvas.addEventListener('drop', (e) => this.handleUnifiedDrop(e));
        this.canvasContainer.addEventListener('dragover', (e) => this.handleUnifiedDragOver(e));
        this.canvasContainer.addEventListener('dragleave', (e) => this.handleUnifiedDragLeave(e));
        this.canvasContainer.addEventListener('drop', (e) => this.handleUnifiedDrop(e));

        document.getElementById('imageFile').addEventListener('change', (e) => this.handleImageUpload(e));
        document.getElementById('videoFile').addEventListener('change', (e) => this.handleVideoUpload(e));

        document.querySelectorAll('.left-panel-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                // Nếu panel đang collapsed, mở rộng nó ra
                const leftPanels = document.querySelector('.left-panels');
                if (leftPanels && leftPanels.classList.contains('collapsed')) {
                    leftPanels.classList.remove('collapsed');
                    const toggleBtn = document.getElementById('toggleSlidesBtn');
                    if (toggleBtn) {
                        toggleBtn.title = 'Thu gọn Slides';
                        toggleBtn.setAttribute('aria-pressed', 'true');
                    }
                }

                document.querySelectorAll('.left-panel-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.left-panel-content').forEach(c => c.classList.remove('active'));

                tab.classList.add('active');
                document.getElementById(tab.dataset.target).classList.add('active');
            });
        });
        window.addEventListener('blur', () => {
            if (this.isAltDown) {
                this.isAltDown = false;
                this.hideDistanceGuides();
            }
            // Cleanup drag states when window loses focus
            this.cleanupDragStates();
        });

        // Additional cleanup for drag states
        document.addEventListener('dragend', () => {
            this.cleanupDragStates();
        });

        // Cleanup on mouse leave window
        document.addEventListener('mouseleave', () => {
            this.cleanupDragStates();
        });

        // Force cleanup overlay on any click outside
        document.addEventListener('click', (e) => {
            if (!this.canvasContainer.contains(e.target)) {
                this.cleanupDragStates();
            }
        });
    }

    handleMouseDown(e, element) {
        // Check if clicking on drag handle
        const isDragHandle = e.target.classList.contains('drag-handle');

        // Check if this is text selection (on text elements with contenteditable)
        const isTextElement = element.hasAttribute('contenteditable') ||
            element.querySelector('[contenteditable="true"]');
        const isClickingOnText = isTextElement && e.target.hasAttribute('contenteditable');

        const targetElement = element.closest('.group-container') || element;
        const isAlreadySelected = this.selectedElements.includes(targetElement);

        // For text elements: chỉ chặn nếu chưa selected VÀ đang click vào text area
        if (isTextElement && !isDragHandle && !e.target.classList.contains('resize-handle') && !isAlreadySelected) {
            // Allow text interaction - don't prevent default
            e.stopPropagation();

            // Focus the contenteditable element for text editing
            if (isClickingOnText) {
                this.isTextSelecting = true;
                return;
            }

            // If clicking on contenteditable but not for dragging, just select element
            if (isClickingOnText) {
                if (!this.selectedElements.includes(targetElement)) {
                    this.selectElement(targetElement);
                }
            }
            return;
        }

        e.stopPropagation();
        e.preventDefault(); // Only prevent default for drag/resize operations

        // targetElement đã được khai báo ở trên rồi
        const wasAlreadySelected = isAlreadySelected; // Dùng lại biến đã check

        if (e.shiftKey) {
            this.toggleSelection(targetElement);
        } else {
            if (!this.selectedElements.includes(targetElement)) {
                // Nếu click vào drag handle, select ngay và cho phép drag
                if (isDragHandle) {
                    this.selectElement(targetElement);
                } else {
                    // Đánh dấu là pending select - sẽ select khi mouseup nếu không kéo
                    this.pendingSelectElement = targetElement;
                    this.dragStart = { x: e.clientX, y: e.clientY };
                    return;
                }
            }
        }

        if (e.target.classList.contains('resize-handle') && this.selectedElements.length === 1) {
            this.isResizing = true;
            this.resizeHandleType = e.target.classList[1];
        } else if (wasAlreadySelected || isDragHandle) {
            // Check nếu đang click gần cạnh (có move cursor)
            const rect = targetElement.getBoundingClientRect();
            const edgeThreshold = 15;
            const isNearEdge =
                e.clientX - rect.left < edgeThreshold ||
                rect.right - e.clientX < edgeThreshold ||
                e.clientY - rect.top < edgeThreshold ||
                rect.bottom - e.clientY < edgeThreshold;

            // Chỉ cho phép drag nếu: đang click drag handle, resize handle, HOẶC gần cạnh
            if (isDragHandle || e.target.classList.contains('resize-handle') || isNearEdge) {
                this.isPreparedForDrag = true;
                this.draggedElement = targetElement; // Track element being dragged
            } else {
                // Click vào giữa element đã chọn - không làm gì
                return;
            }

            // Add visual feedback when starting to drag
            this.selectedElements.forEach(el => {
                el.classList.add('dragging');
            });

            // Add preview for non-selected elements and show grid
            this.canvas.querySelectorAll('.element:not(.selected)').forEach(el => {
                el.classList.add('drag-preview');
            });
            this.showCanvasGrid();
        }

        this.dragStart = { x: e.clientX, y: e.clientY };

        this.elementsStartPos.clear();
        this.selectedElements.forEach(el => {
            this.elementsStartPos.set(el, { x: el.offsetLeft, y: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight });
        });
    }

    selectElement(element) {
        // Hide control points of previously selected connectors
        this.selectedElements.forEach(el => {
            el.classList.remove('selected');
            if (el.classList.contains('connector-line') && el._controlPoints) {
                el._controlPoints.forEach(cp => {
                    cp.style.opacity = '0';
                });
            }
        });
        this.selectedElements = [];

        if (element) {
            this.selectedElements.push(element);
            element.classList.add('selected');

            // Show control points for curved connectors
            if (element.classList.contains('connector-line') && element.classList.contains('curved') && element._controlPoints) {
                element._controlPoints.forEach(cp => {
                    cp.style.opacity = '1';
                });
            }
        }

        if (this.selectedElements.length > 0) {
            document.getElementById('propertiesPanel').classList.add('open');
            document.getElementById('canvasContainer').classList.add('properties-open');
        }
        this.updateProperties();
    }

    toggleSelection(element) {
        const index = this.selectedElements.indexOf(element);
        if (index > -1) {
            element.classList.remove('selected');
            this.selectedElements.splice(index, 1);
        } else {
            element.classList.add('selected');
            this.selectedElements.push(element);
        }
        this.updateProperties();
    }

    updateProperties() {
        if (this.selectedElements.length === 0) {
            this.propertiesContent.innerHTML = `<div style="text-align: center; margin-top: 50px; color: #718096;"><div style="font-size: 48px; margin-bottom: 15px;">🎨</div><h3 style="margin-bottom: 10px; color: #4a5568;">No Element Selected</h3><p>Select an element to edit its properties</p></div>`;
            return;
        }

        if (this.selectedElements.length > 1) {
            this.propertiesContent.innerHTML = `<div style="text-align: center; margin-top: 50px; color: #718096;"><div style="font-size: 48px; margin-bottom: 15px;">✨</div><h3 style="margin-bottom: 10px; color: #4a5568;">${this.selectedElements.length} Elements Selected</h3><p>Press Ctrl+G to group them.</p><div class="action-buttons" style="margin-top: 20px;"><button class="action-btn" onclick="window.slideEditor.groupSelectedElements()"><span>🗃️</span> Group</button><button class="action-btn danger" onclick="window.slideEditor.deleteSelected()"><span>🗑️</span> Delete All</button></div></div>`;
            return;
        }

        const el = this.selectedElements[0];
        const style = window.getComputedStyle(el);

        // VALIDATION: Ensure data-type exists, set default if missing
        if (!el.dataset.type) {
            console.warn('⚠️ Element missing data-type, setting default to "shape"');
            el.dataset.type = 'shape';
        }

        let html = '';

        if (el.classList.contains('group-container')) {
            html += `<div class="property-group"><div class="action-buttons"><button class="action-btn" onclick="window.slideEditor.ungroupElement()"><span>↔️</span> Ungroup</button></div></div>`;
        }

        html += `
        <div class="property-group" style="background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
            <h3 style="color: white; margin-bottom: 8px;">${el.dataset.type.toUpperCase()} ELEMENT</h3>
            <p style="opacity: 0.9; font-size: 12px; margin: 0;">ID: ${el.id || 'No ID'} • Type: ${el.dataset.type}</p>
        </div>
        <div class="property-group">
            <h3>📍 Position & Transform</h3>
            <div class="property-row">
                <div class="property-col"><label class="property-label">X Position</label><input type="number" class="property-input" data-style="left" value="${parseInt(el.style.left) || 0}" step="1"></div>
                <div class="property-col"><label class="property-label">Y Position</label><input type="number" class="property-input" data-style="top" value="${parseInt(el.style.top) || 0}" step="1"></div>
            </div>
            <div class="property-row">
                <div class="property-col"><label class="property-label">Width</label><input type="number" class="property-input" data-style="width" value="${parseInt(el.style.width) || el.offsetWidth}" step="1"></div>
                <div class="property-col"><label class="property-label">Height</label><input type="number" class="property-input" data-style="height" value="${parseInt(el.style.height) || el.offsetHeight}" step="1"></div>
            </div>
            <label class="property-label">Rotation (degrees)</label>
            <div class="range-container"><input type="range" class="property-range" data-style="rotation" min="-180" max="180" value="0" step="1"><span class="range-value">0°</span></div>
        </div>
    `;

        if (el.dataset.type === 'text') {
            html += `
            <div class="property-group">
                <h3>✍️ Typography (Entire Element)</h3>
                <label class="property-label">Font Family</label>
                <select class="property-input" data-style="fontFamily">
                    <option value="Inter, sans-serif" ${style.fontFamily.includes('Inter') ? 'selected' : ''}>Inter</option>
                    <option value="Arial, sans-serif" ${style.fontFamily.includes('Arial') ? 'selected' : ''}>Arial</option>
                    <option value="Georgia, serif" ${style.fontFamily.includes('Georgia') ? 'selected' : ''}>Georgia</option>
                    <option value="'Courier New', monospace" ${style.fontFamily.includes('Courier') ? 'selected' : ''}>Courier New</option>
                    <option value="'Times New Roman', serif" ${style.fontFamily.includes('Times') ? 'selected' : ''}>Times New Roman</option>
                </select>
                <div class="property-row">
                    <div class="property-col"><label class="property-label">Font Size</label><input type="number" class="property-input" data-style="fontSize" value="${parseInt(style.fontSize)}" step="2" min="12" max="500"></div>
                    <div class="property-col"><label class="property-label">Line Height</label><input type="number" class="property-input" data-style="lineHeight" value="${parseFloat(style.lineHeight) || 1.4}" step="0.1" min="0.5" max="3"></div>
                </div>
                <label class="property-label">Font Weight</label>
                <select class="property-input" data-style="fontWeight">
                    <option value="100" ${style.fontWeight == '100' ? 'selected' : ''}>Thin</option> <option value="200" ${style.fontWeight == '200' ? 'selected' : ''}>Extra Light</option> <option value="300" ${style.fontWeight == '300' ? 'selected' : ''}>Light</option> <option value="400" ${style.fontWeight == '400' ? 'selected' : ''}>Regular</option> <option value="500" ${style.fontWeight == '500' ? 'selected' : ''}>Medium</option> <option value="600" ${style.fontWeight == '600' ? 'selected' : ''}>Semi Bold</option> <option value="700" ${style.fontWeight == '700' ? 'selected' : ''}>Bold</option> <option value="800" ${style.fontWeight == '800' ? 'selected' : ''}>Extra Bold</option> <option value="900" ${style.fontWeight == '900' ? 'selected' : ''}>Black</option>
                </select>
                <label class="property-label">Text Align</label>
                <div class="button-group">
                    <button class="style-btn ${style.textAlign === 'left' ? 'active' : ''}" data-style="textAlign" data-value="left">◀</button> <button class="style-btn ${style.textAlign === 'center' ? 'active' : ''}" data-style="textAlign" data-value="center">▣</button> <button class="style-btn ${style.textAlign === 'right' ? 'active' : ''}" data-style="textAlign" data-value="right">▶</button> <button class="style-btn ${style.textAlign === 'justify' ? 'active' : ''}" data-style="textAlign" data-value="justify">▦</button>
                </div>
            </div>
            <div class="property-group">
                <h3>📝 Text Formatting (Selected Text)</h3>
                <p class="property-label" style="margin-bottom: 10px;">Select text inside the element to apply formatting.</p>
                <div class="button-group">
                    <button class="style-btn" data-format="bold" title="Bold"><b>B</b></button> <button class="style-btn" data-format="italic" title="Italic"><i>I</i></button> <button class="style-btn" data-format="underline" title="Underline"><u>U</u></button> <button class="style-btn" data-format="strikeThrough" title="Strikethrough"><s>S</s></button> <button class="style-btn" data-format="removeFormat" title="Clear Formatting">⌫</button>
                </div>
                <div class="property-row">
                    <div class="property-col">
                        <label class="property-label">Font Size</label>
                        <input type="number" class="property-input" data-format-size="fontSize" value="${parseInt(style.fontSize)}" step="1" min="8" max="200" placeholder="Mixed">
                    </div>
                </div>
                <div class="property-row">
                    <div class="property-col"><label class="property-label">Highlight Color</label><input type="color" data-format-color="backColor" class="property-color-input" value="#ffff00" style="height: 40px;"></div>
                    <div class="property-col"><label class="property-label">Text Color</label><input type="color" data-format-color="foreColor" class="property-color-input" value="${this.rgbToHex(style.color)}" style="height: 40px;"></div>
                </div>
            </div>
            <div class="property-group">
                <h3>🎨 Text Colors (Entire Element)</h3>
                <label class="property-label">Text Color</label>
                <div class="color-input-container">
                    <input type="color" class="property-color-input" data-style="color" value="${this.rgbToHex(style.color)}"><input type="text" class="color-text-input" data-style="color" value="${this.rgbToHex(style.color)}" placeholder="#000000">
                </div>
            </div>
        `;
        }

        html += `
        <div class="property-group">
            <h3>🎭 Appearance</h3>
            <label class="property-label">Background Color</label>
            <div class="color-input-container"><input type="color" class="property-color-input" data-style="backgroundColor" value="${this.rgbToHex(style.backgroundColor)}"><input type="text" class="color-text-input" data-style="backgroundColor" value="${this.rgbToHex(style.backgroundColor)}" placeholder="#ffffff"></div>
            <label class="property-label">Border</label>
            <div class="property-row">
                <div class="property-col"><input type="number" class="property-input" data-style="borderWidth" value="${parseInt(style.borderWidth) || 0}" step="1" min="0" placeholder="Width"></div>
                <div class="property-col"><select class="property-input" data-style="borderStyle"><option value="none" ${style.borderStyle === 'none' ? 'selected' : ''}>None</option><option value="solid" ${style.borderStyle === 'solid' ? 'selected' : ''}>Solid</option><option value="dashed" ${style.borderStyle === 'dashed' ? 'selected' : ''}>Dashed</option><option value="dotted" ${style.borderStyle === 'dotted' ? 'selected' : ''}>Dotted</option></select></div>
            </div>
            <input type="color" class="property-color-input" data-style="borderColor" value="${this.rgbToHex(style.borderColor)}">
            <label class="property-label">Border Radius</label>
            <div class="range-container"><input type="range" class="property-range" data-style="borderRadius" min="0" max="100" value="${parseInt(style.borderRadius) || 0}" step="1"><span class="range-value">${parseInt(style.borderRadius) || 0}px</span></div>
            <label class="property-label">Box Shadow</label>
            <div class="shadow-controls"><div class="property-row"><div class="property-col"><input type="number" class="property-input" data-style="shadowX" value="0" step="1" placeholder="X"></div><div class="property-col"><input type="number" class="property-input" data-style="shadowY" value="0" step="1" placeholder="Y"></div></div><input type="range" class="property-range" data-style="shadowBlur" min="0" max="50" value="0" step="1"><span class="range-label">Blur: <span class="range-value">0px</span></span></div>
        </div>
        <div class="property-group">
            <h3>✨ Effects</h3>
            <label class="property-label">Opacity</label><div class="range-container"><input type="range" class="property-range" data-style="opacity" min="0" max="1" step="0.05" value="${style.opacity || 1}"><span class="range-value">${Math.round((style.opacity || 1) * 100)}%</span></div>
            <label class="property-label">Blur</label><div class="range-container"><input type="range" class="property-range" data-style="filter-blur" min="0" max="20" value="0" step="0.5"><span class="range-value">0px</span></div>
            <label class="property-label">Brightness</label><div class="range-container"><input type="range" class="property-range" data-style="filter-brightness" min="0" max="200" value="100" step="5"><span class="range-value">100%</span></div>
            <label class="property-label">Saturation</label><div class="range-container"><input type="range" class="property-range" data-style="filter-saturate" min="0" max="200" value="100" step="5"><span class="range-value">100%</span></div>
        </div>
        <div class="property-group">
            <h3>📐 Layout</h3>
            <label class="property-label">Z-Index (Layer Order)</label><div class="z-index-controls"><button class="control-btn" onclick="window.slideEditor.changeZIndex(-1)">Send Back</button><input type="number" class="property-input" data-style="zIndex" value="${style.zIndex === 'auto' ? 0 : style.zIndex}" style="width: 80px; text-align: center;"><button class="control-btn" onclick="window.slideEditor.changeZIndex(1)">Bring Front</button></div>
            <label class="property-label">Padding</label>
            <div class="spacing-controls">
                 <div class="spacing-input-group"><span class="spacing-input-label">T</span><input type="number" class="spacing-input" data-style="paddingTop" value="${parseInt(style.paddingTop) || 0}"></div>
                 <div class="spacing-input-group"><span class="spacing-input-label">R</span><input type="number" class="spacing-input" data-style="paddingRight" value="${parseInt(style.paddingRight) || 0}"></div>
                 <div class="spacing-input-group"><span class="spacing-input-label">B</span><input type="number" class="spacing-input" data-style="paddingBottom" value="${parseInt(style.paddingBottom) || 0}"></div>
                 <div class="spacing-input-group"><span class="spacing-input-label">L</span><input type="number" class="spacing-input" data-style="paddingLeft" value="${parseInt(style.paddingLeft) || 0}"></div>
            </div>
            <label class="property-label" style="margin-top: 15px;">Margin</label>
            <div class="spacing-controls">
               <div class="spacing-input-group"><span class="spacing-input-label">T</span><input type="number" class="spacing-input" data-style="marginTop" value="${parseInt(style.marginTop) || 0}"></div>
               <div class="spacing-input-group"><span class="spacing-input-label">R</span><input type="number" class="spacing-input" data-style="marginRight" value="${parseInt(style.marginRight) || 0}"></div>
               <div class="spacing-input-group"><span class="spacing-input-label">B</span><input type="number" class="spacing-input" data-style="marginBottom" value="${parseInt(style.marginBottom) || 0}"></div>
               <div class="spacing-input-group"><span class="spacing-input-label">L</span><input type="number" class="spacing-input" data-style="marginLeft" value="${parseInt(style.marginLeft) || 0}"></div>
            </div>
        </div>
        <div class="property-group">
            <h3>⚡ Quick Actions</h3>
            <div class="action-buttons"><button class="action-btn" onclick="window.slideEditor.duplicateElement()"><span>⧉</span> Duplicate</button><button class="action-btn" onclick="window.slideEditor.copySelectedElement()"><span>📋</span> Copy</button><button class="action-btn danger" onclick="window.slideEditor.deleteSelected()"><span>🗑️</span> Delete</button></div>
        </div>
    `;

        this.propertiesContent.innerHTML = html;
        this.bindPropertyEvents();
    }

    bindPropertyEvents() {
        if (this.selectedElements.length !== 1) return;
        const el = this.selectedElements[0];

        const restoreSelection = () => {
            if (this.savedSelectionRange) {
                el.focus();
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(this.savedSelectionRange);
            }
        };

        this.propertiesContent.querySelectorAll('[data-format]').forEach(btn => {
            btn.addEventListener('mousedown', (e) => {
                e.preventDefault();
                restoreSelection();
                const command = e.currentTarget.dataset.format;
                document.execCommand(command, false, null);
                this.saveState();
                el.focus();
                this._saveSelection();
            });
        });

        this.propertiesContent.querySelectorAll('[data-format-color]').forEach(colorInput => {
            colorInput.addEventListener('mousedown', (e) => {
                e.preventDefault();
                this._saveSelection();
            });
            colorInput.addEventListener('input', (e) => {
                restoreSelection();
                const command = e.currentTarget.dataset.formatColor;
                const color = e.currentTarget.value;
                document.execCommand(command, false, color);
            });
            colorInput.addEventListener('change', () => {
                this.saveState();
            });
        });

        // Font size for selected text
        this.propertiesContent.querySelectorAll('[data-format-size]').forEach(sizeInput => {
            sizeInput.addEventListener('input', (e) => {
                const value = e.target.value;
                if (value && !isNaN(value)) {
                    restoreSelection();
                    // Wrap selection in span with font size
                    const selection = window.getSelection();
                    if (selection.rangeCount > 0 && !selection.isCollapsed) {
                        const range = selection.getRangeAt(0);
                        const span = document.createElement('span');
                        span.style.fontSize = value + 'px';
                        range.surroundContents(span);
                    }
                }
            });
            sizeInput.addEventListener('change', () => {
                this.saveState();
            });
        });

        this.propertiesContent.querySelectorAll('.property-input, .property-color-input:not([data-format-color])').forEach(input => {
            input.addEventListener('input', (e) => {
                let value = e.target.value;
                let styleProp = e.target.dataset.style;

                if (['left', 'top', 'width', 'height', 'fontSize', 'borderWidth', 'borderRadius', 'letterSpacing', 'wordSpacing'].includes(styleProp) || styleProp.includes('padding') || styleProp.includes('margin')) {
                    value += 'px';
                }

                el.style[styleProp] = value;

                // Nếu thuộc tính thay đổi là fontSize, hãy cập nhật lại chiều cao
                if (styleProp === 'fontSize') {
                    this.updateTextElementHeight(el);
                }

                // Debounced save: Save state after 500ms of no changes
                clearTimeout(this._propertiesSaveTimeout);
                this._propertiesSaveTimeout = setTimeout(() => {
                    this.saveState();
                }, 500);
            });
            input.addEventListener('change', () => {
                // Clear debounced save and save immediately on change
                clearTimeout(this._propertiesSaveTimeout);
                this.saveState();
            });
        });

        this.propertiesContent.querySelectorAll('.color-text-input').forEach(input => {
            input.addEventListener('input', (e) => {
                const styleProp = e.target.dataset.style;
                el.style[styleProp] = e.target.value;
                const colorPicker = this.propertiesContent.querySelector(`input[type="color"][data-style="${styleProp}"]`);
                if (colorPicker) colorPicker.value = e.target.value;
            });
        });

        this.propertiesContent.querySelectorAll('.property-range').forEach(range => {
            range.addEventListener('input', (e) => {
                let value = e.target.value;
                let styleProp = e.target.dataset.style;
                const valueSpan = e.target.parentElement.querySelector('.range-value');

                if (styleProp === 'rotation') {
                    el.style.transform = `rotate(${value}deg)`;
                    if (valueSpan) valueSpan.textContent = `${value}°`;
                } else if (styleProp === 'opacity') {
                    el.style.opacity = value;
                    if (valueSpan) valueSpan.textContent = `${Math.round(value * 100)}%`;
                } else if (styleProp === 'borderRadius') {
                    el.style.borderRadius = `${value}px`;
                    if (valueSpan) valueSpan.textContent = `${value}px`;
                } else if (styleProp.startsWith('filter-')) {
                    const filterType = styleProp.split('-')[1];
                    let filterValue = '';

                    if (filterType === 'blur') filterValue = `blur(${value}px)`;
                    else if (filterType === 'brightness') filterValue = `brightness(${value}%)`;
                    else if (filterType === 'saturate') filterValue = `saturate(${value}%)`;

                    if (valueSpan) valueSpan.textContent = filterValue.match(/\((.*)\)/)[1];

                    const currentFilter = el.style.filter || '';
                    const filterRegex = new RegExp(`${filterType}\\([^)]*\\)`, 'g');
                    let newFilter = currentFilter.replace(filterRegex, '').trim();
                    if (parseFloat(value) !== (filterType === 'blur' ? 0 : 100)) {
                        if (newFilter) newFilter += ' ';
                        newFilter += filterValue;
                    }
                    el.style.filter = newFilter;
                } else if (styleProp === 'textShadowBlur') {
                    el.style.textShadow = `0 0 ${value}px rgba(0,0,0,0.5)`;
                    if (valueSpan) valueSpan.textContent = `${value}px`;
                } else if (styleProp === 'shadowBlur') {
                    const shadowX = this.propertiesContent.querySelector('[data-style="shadowX"]')?.value || 0;
                    const shadowY = this.propertiesContent.querySelector('[data-style="shadowY"]')?.value || 0;
                    el.style.boxShadow = `${shadowX}px ${shadowY}px ${value}px rgba(0,0,0,0.3)`;
                    if (valueSpan) valueSpan.textContent = `${value}px`;
                }

                // Debounced save for smooth slider interaction
                clearTimeout(this._propertiesSaveTimeout);
                this._propertiesSaveTimeout = setTimeout(() => {
                    this.saveState();
                }, 500);
            });
            range.addEventListener('change', () => {
                clearTimeout(this._propertiesSaveTimeout);
                this.saveState();
            });
        });

        this.propertiesContent.querySelectorAll('[data-style="shadowX"], [data-style="shadowY"]').forEach(input => {
            input.addEventListener('input', () => {
                const shadowX = this.propertiesContent.querySelector('[data-style="shadowX"]')?.value || 0;
                const shadowY = this.propertiesContent.querySelector('[data-style="shadowY"]')?.value || 0;
                const shadowBlur = this.propertiesContent.querySelector('[data-style="shadowBlur"]')?.value || 0;
                el.style.boxShadow = `${shadowX}px ${shadowY}px ${shadowBlur}px rgba(0,0,0,0.3)`;
            });
        });

        this.propertiesContent.querySelectorAll('.style-btn:not([data-format])').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const styleProp = e.currentTarget.dataset.style;
                const value = e.currentTarget.dataset.value;
                e.currentTarget.parentElement.querySelectorAll('.style-btn').forEach(sibling => sibling.classList.remove('active'));
                e.currentTarget.classList.add('active');
                el.style[styleProp] = value;
                this.saveState();
            });
        });

        this.propertiesContent.querySelectorAll('.spacing-input').forEach(input => {
            input.addEventListener('input', (e) => {
                el.style[e.target.dataset.style] = e.target.value + 'px';
            });
            input.addEventListener('change', () => this.saveState());
        });
    }

    _saveSelection() {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            this.savedSelectionRange = selection.getRangeAt(0);

            // Update properties panel with selection styles
            if (!selection.isCollapsed) {
                this.updatePropertiesForSelection(selection);
            }
        }
    }

    updatePropertiesForSelection(selection) {
        if (!selection || selection.isCollapsed) return;

        try {
            const range = selection.getRangeAt(0);
            const container = range.commonAncestorContainer;

            // Get all text nodes in selection
            const walker = document.createTreeWalker(
                range.commonAncestorContainer,
                NodeFilter.SHOW_TEXT,
                null
            );

            const styles = {
                fontSize: new Set(),
                color: new Set(),
                fontFamily: new Set(),
                fontWeight: new Set(),
                fontStyle: new Set(),
                textDecoration: new Set()
            };

            // Collect styles from all nodes in selection
            let node;
            while (node = walker.nextNode()) {
                if (range.intersectsNode(node)) {
                    const element = node.parentElement;
                    if (element) {
                        const computed = window.getComputedStyle(element);
                        styles.fontSize.add(computed.fontSize);
                        styles.color.add(computed.color);
                        styles.fontFamily.add(computed.fontFamily);
                        styles.fontWeight.add(computed.fontWeight);
                        styles.fontStyle.add(computed.fontStyle);
                        styles.textDecoration.add(computed.textDecoration);
                    }
                }
            }

            // Update input fields in properties panel
            const fontSizeInput = this.propertiesContent.querySelector('[data-style="fontSize"]');
            if (fontSizeInput) {
                if (styles.fontSize.size === 1) {
                    const value = parseInt(Array.from(styles.fontSize)[0]);
                    fontSizeInput.value = value;
                } else if (styles.fontSize.size > 1) {
                    fontSizeInput.value = '';
                    fontSizeInput.placeholder = 'Mixed';
                }
            }

            const colorInput = this.propertiesContent.querySelector('[data-style="color"]');
            if (colorInput) {
                if (styles.color.size === 1) {
                    const color = Array.from(styles.color)[0];
                    // Convert rgb to hex for color input
                    const hex = this.rgbToHex(color);
                    if (hex) colorInput.value = hex;
                } else if (styles.color.size > 1) {
                    colorInput.value = '#000000';
                    colorInput.style.opacity = '0.5';
                } else {
                    colorInput.style.opacity = '1';
                }
            }

        } catch (error) {
            console.error('Error updating properties for selection:', error);
        }
    }

    rgbToHex(rgb) {
        if (!rgb) return null;

        // Already hex
        if (rgb.startsWith('#')) return rgb;

        // Parse rgb(r, g, b) or rgba(r, g, b, a)
        const match = rgb.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (!match) return null;

        const r = parseInt(match[1]);
        const g = parseInt(match[2]);
        const b = parseInt(match[3]);

        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }

    createElement(type) {
        const el = document.createElement('div');
        el.className = 'element';
        el.dataset.type = type;
        el.id = `element_${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        el.style.position = 'absolute';
        el.style.left = '200px';
        el.style.top = '200px';
        el.style.zIndex = this.zIndexCounter++;

        switch (type) {
            case 'rectangle':
                el.style.width = '300px'; el.style.height = '200px';
                el.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
                el.style.borderRadius = '12px'; break;
            case 'circle':
                el.style.width = '200px'; el.style.height = '200px';
                el.style.background = 'linear-gradient(135deg, #48bb78, #38a169)';
                el.style.borderRadius = '50%'; break;
            case 'triangle':
                el.style.width = '150px'; el.style.height = '120px';
                el.style.background = 'transparent';
                el.style.display = 'flex';
                el.style.alignItems = 'flex-end';
                el.style.justifyContent = 'center';
                el.innerHTML = '<div style="width: 0; height: 0; border-left: 60px solid transparent; border-right: 60px solid transparent; border-bottom: 100px solid #f56565; margin: auto;"></div>'; break;
            case 'line':
                el.style.width = '400px'; el.style.height = '8px';
                el.style.background = 'linear-gradient(90deg, #ed8936, #f6ad55)';
                el.style.borderRadius = '4px'; break;
            case 'star':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '⭐'; break;
            case 'heart':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '❤️'; break;
            case 'icon-arrow':
                el.style.width = '100px'; el.style.height = '60px';
                el.style.fontSize = '48px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#4299e1'; el.innerHTML = '→'; break;
            case 'icon-check':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#48bb78'; el.innerHTML = '✓'; break;
            case 'icon-cross':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#f56565'; el.innerHTML = '✗'; break;
            case 'icon-lightbulb':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '💡'; break;
            case 'icon-target':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🎯'; break;
            case 'icon-rocket':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🚀'; break;
            case 'image':
                el.style.width = '300px'; el.style.height = '200px';
                el.style.background = 'linear-gradient(135deg, #a0aec0, #cbd5e0)';
                el.style.borderRadius = '12px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.fontSize = '48px'; el.innerHTML = '🖼️';
                el.style.border = '2px dashed #718096'; break;
            case 'video':
                el.style.width = '400px'; el.style.height = '225px';
                el.style.background = 'linear-gradient(135deg, #4299e1, #3182ce)';
                el.style.borderRadius = '12px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.fontSize = '48px'; el.style.color = 'white'; el.innerHTML = '🎥'; break;
            case 'avatar':
                el.style.width = '120px'; el.style.height = '120px';
                el.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
                el.style.borderRadius = '50%'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.fontSize = '60px'; el.style.color = 'white'; el.innerHTML = '👤'; break;
            case 'bar-chart':
                el.style.width = '400px'; el.style.height = '300px';
                el.style.background = 'linear-gradient(135deg, #48bb78, #38a169)';
                el.style.borderRadius = '12px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.fontSize = '48px'; el.style.color = 'white'; el.innerHTML = '📊'; break;
            case 'pie-chart':
                el.style.width = '300px'; el.style.height = '300px';
                el.style.background = 'linear-gradient(135deg, #ed8936, #f6ad55)';
                el.style.borderRadius = '50%'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.fontSize = '48px'; el.style.color = 'white'; el.innerHTML = '🥧'; break;
            case 'progress-bar':
                el.style.width = '300px'; el.style.height = '40px';
                el.style.background = '#e2e8f0'; el.style.borderRadius = '20px';
                el.style.position = 'relative'; el.style.overflow = 'hidden';
                const progress = document.createElement('div');
                progress.style.width = '70%'; progress.style.height = '100%';
                progress.style.background = 'linear-gradient(90deg, #4299e1, #3182ce)';
                progress.style.borderRadius = '20px'; progress.style.transition = 'width 0.3s ease';
                el.appendChild(progress); break;
            case 'badge':
                el.style.width = '120px'; el.style.height = '40px';
                el.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
                el.style.borderRadius = '20px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.fontSize = '14px'; el.style.color = 'white'; el.style.fontWeight = '600';
                el.innerHTML = 'Badge'; break;
            case 'divider':
                el.style.width = '400px'; el.style.height = '4px';
                el.style.background = 'linear-gradient(90deg, #667eea, #764ba2)';
                el.style.borderRadius = '2px'; break;
            case 'quote-box':
                el.style.width = '400px'; el.style.height = '120px';
                el.style.background = '#f7fafc'; el.style.border = '3px solid #e2e8f0';
                el.style.borderLeft = '6px solid #667eea'; el.style.borderRadius = '8px';
                el.style.padding = '20px'; el.style.fontStyle = 'italic';
                el.style.fontSize = '16px'; el.style.color = '#4a5568'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.innerHTML = '"Your inspiring quote here"'; break;
            case 'sparkle':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '✨'; break;
            case 'crown':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '👑'; break;
            case 'gem':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '💎'; break;

            // New Basic Shapes
            case 'square':
                el.style.width = '200px'; el.style.height = '200px';
                el.style.background = 'linear-gradient(45deg, #9f7aea, #805ad5)';
                el.style.borderRadius = '8px'; break;
            case 'oval':
                el.style.width = '250px'; el.style.height = '150px';
                el.style.background = 'linear-gradient(45deg, #38b2ac, #319795)';
                el.style.borderRadius = '50%'; break;
            case 'diamond':
                el.style.width = '150px'; el.style.height = '150px';
                el.style.background = '#e53e3e'; el.style.transform = 'rotate(45deg)'; break;
            case 'hexagon':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#667eea'; el.innerHTML = '⬡'; break;
            case 'pentagon':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#48bb78'; el.innerHTML = '⬟'; break;

            // Arrows
            case 'arrow-right':
                el.style.width = '120px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#4299e1'; el.innerHTML = '→'; break;
            case 'arrow-left':
                el.style.width = '120px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#4299e1'; el.innerHTML = '←'; break;
            case 'arrow-up':
                el.style.width = '80px'; el.style.height = '120px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#4299e1'; el.innerHTML = '↑'; break;
            case 'arrow-down':
                el.style.width = '80px'; el.style.height = '120px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#4299e1'; el.innerHTML = '↓'; break;
            case 'arrow-curved':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '70px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#667eea'; el.innerHTML = '↪'; break;
            case 'arrow-double':
                el.style.width = '120px'; el.style.height = '80px';
                el.style.fontSize = '50px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#ed8936'; el.innerHTML = '⇄'; break;
            case 'arrow-thick':
                el.style.width = '120px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#48bb78'; el.innerHTML = '➤'; break;
            case 'arrow-circle':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#9f7aea'; el.innerHTML = '⟲'; break;
            case 'arrow-diagonal':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#f56565'; el.innerHTML = '↗'; break;

            // More Symbols
            case 'star-outline':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#ffd700'; el.innerHTML = '☆'; break;
            case 'heart-outline':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#e53e3e'; el.innerHTML = '♡'; break;
            case 'check':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#48bb78'; el.innerHTML = '✓'; break;
            case 'cross':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#f56565'; el.innerHTML = '✗'; break;
            case 'plus':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '➕'; break;
            case 'minus':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '➖'; break;
            case 'exclamation':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '❗'; break;
            case 'question':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '❓'; break;
            case 'info':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = 'ℹ️'; break;
            case 'thumbs-up':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '👍'; break;

            // Business & Office
            case 'lightbulb':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '💡'; break;
            case 'target':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🎯'; break;
            case 'rocket':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🚀'; break;
            case 'trophy':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🏆'; break;
            case 'medal':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🏅'; break;
            case 'briefcase':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '💼'; break;
            case 'graph':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '📈'; break;
            case 'calendar':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '📅'; break;
            case 'clock':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🕐'; break;
            case 'money':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '💰'; break;
            case 'handshake':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🤝'; break;
            case 'key':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🔑'; break;

            // Technology
            case 'laptop':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '💻'; break;
            case 'phone':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '📱'; break;
            case 'wifi':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '📶'; break;
            case 'database':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🗄️'; break;
            case 'cloud':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '☁️'; break;
            case 'gear':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '⚙️'; break;
            case 'code':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '💻'; break;
            case 'bug':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🐛'; break;
            case 'shield':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🛡️'; break;

            // Nature & Weather
            case 'sun':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '☀️'; break;
            case 'moon':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🌙'; break;
            case 'tree':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🌳'; break;
            case 'flower':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🌸'; break;
            case 'leaf':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🍃'; break;
            case 'fire':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🔥'; break;
            case 'water':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '💧'; break;
            case 'lightning':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '⚡'; break;
            case 'rainbow':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🌈'; break;

            // People & Emotions  
            case 'team':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '👥'; break;
            case 'smile':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '😊'; break;
            case 'thinking':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🤔'; break;
            case 'celebration':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🎉'; break;
            case 'eyes':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '👀'; break;
            case 'brain':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🧠'; break;
            case 'muscle':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '💪'; break;
            case 'clap':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '👏'; break;

            // Additional Decorative
            case 'confetti':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🎊'; break;
            case 'ribbon':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🎀'; break;
            case 'frame':
                el.style.width = '200px'; el.style.height = '150px';
                el.style.background = 'linear-gradient(135deg, #8b5a3c, #a0522d)';
                el.style.borderRadius = '8px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.fontSize = '40px'; el.innerHTML = '🖼️'; break;

            // Food & Objects
            case 'coffee':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '☕'; break;
            case 'pizza':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🍕'; break;
            case 'apple':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🍎'; break;
            case 'cake':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🎂'; break;
            case 'book':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '📚'; break;
            case 'music':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🎵'; break;
            case 'gift':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🎁'; break;
            case 'balloon':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🎈'; break;
            case 'diamond-shape':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '♦️'; break;

            // Math & Science
            case 'infinity':
                el.style.width = '120px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#667eea'; el.innerHTML = '∞'; break;
            case 'pi':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#48bb78'; el.innerHTML = 'π'; break;
            case 'sum':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#ed8936'; el.innerHTML = 'Σ'; break;
            case 'delta':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#f56565'; el.innerHTML = 'Δ'; break;
            case 'alpha':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#9f7aea'; el.innerHTML = 'α'; break;
            case 'beta':
                el.style.width = '80px'; el.style.height = '80px';
                el.style.fontSize = '60px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.style.color = '#3182ce'; el.innerHTML = 'β'; break;
            case 'microscope':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🔬'; break;
            case 'atom':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '⚛️'; break;
            case 'dna':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🧬'; break;

            // Transportation
            case 'car':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🚗'; break;
            case 'airplane':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '✈️'; break;
            case 'train':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🚆'; break;
            case 'bike':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🚲'; break;
            case 'ship':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🚢'; break;
            case 'bus':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🚌'; break;
            case 'motorcycle':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🏍️'; break;
            case 'helicopter':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🚁'; break;
            case 'satellite':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🛰️'; break;

            // Sports & Activities
            case 'soccer':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '⚽'; break;
            case 'basketball':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🏀'; break;
            case 'tennis':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🎾'; break;
            case 'golf':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '⛳'; break;
            case 'swimming':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🏊'; break;
            case 'running':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🏃'; break;
            case 'cycling':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🚴'; break;
            case 'weightlifting':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🏋️'; break;
            case 'yoga':
                el.style.width = '100px'; el.style.height = '100px';
                el.style.fontSize = '80px'; el.style.display = 'flex';
                el.style.alignItems = 'center'; el.style.justifyContent = 'center';
                el.innerHTML = '🧘'; break;
        }

        this.canvas.appendChild(el);
        this.makeElementInteractive(el);
        this.selectElement(el);
        this.saveState();
        this.markAsChanged(); // Mark as changed for reset functionality

        // Auto zoom to fit the new element
        setTimeout(() => {
            this.fitToScreen();
        }, 100);
    }

    handleImageUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.onload = () => {
                // Calculate optimal size while maintaining aspect ratio
                const maxWidth = 800;
                const maxHeight = 600;
                let { width, height } = img;

                if (width > maxWidth) {
                    height = (height * maxWidth) / width;
                    width = maxWidth;
                }
                if (height > maxHeight) {
                    width = (width * maxHeight) / height;
                    height = maxHeight;
                }

                const el = document.createElement('div');
                el.className = 'element';
                el.dataset.type = 'image';
                el.style.position = 'absolute';
                el.style.left = '200px';
                el.style.top = '200px';
                el.style.width = width + 'px';
                el.style.height = height + 'px';
                el.style.zIndex = this.zIndexCounter++;
                el.style.borderRadius = '12px';

                const imgElement = document.createElement('img');
                imgElement.src = event.target.result;
                el.appendChild(imgElement);

                this.canvas.appendChild(el);
                this.makeElementInteractive(el);
                this.selectElement(el);
                this.saveState();

                // Auto zoom to fit the new image
                setTimeout(() => {
                    this.fitToScreen();
                }, 100);
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
        e.target.value = '';
    }

    handleVideoUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const el = document.createElement('div');
            el.className = 'element';
            el.dataset.type = 'video';
            el.style.position = 'absolute';
            el.style.left = '200px';
            el.style.top = '200px';
            el.style.width = '500px';
            el.style.height = '300px';
            el.style.zIndex = this.zIndexCounter++;
            el.style.borderRadius = '12px';
            el.style.background = '#000';

            const video = document.createElement('video');
            video.src = event.target.result;
            video.controls = true;
            el.appendChild(video);

            this.canvas.appendChild(el);
            this.makeElementInteractive(el);
            this.selectElement(el);
            this.saveState();

            // Auto zoom to fit the new video
            setTimeout(() => {
                this.fitToScreen();
            }, 100);
        };
        reader.readAsDataURL(file);
        e.target.value = '';
    }

    // Unified Drag & Drop handlers (for both templates and files)
    handleUnifiedDragOver(e) {
        // Skip template drag handling if disabled
        if (this.disableTemplateDrag && e.dataTransfer.types.includes('text/plain')) {
            return;
        }

        e.preventDefault();

        // Check if it's a file being dragged
        if (e.dataTransfer.types.includes('Files')) {
            e.dataTransfer.dropEffect = 'copy';

            // Show file drop overlay
            const overlay = document.getElementById('dragDropOverlay');
            if (overlay) {
                overlay.classList.add('active');
            }
            this.canvasContainer.classList.add('canvas-drag-over');
        }
        // Check if it's a template being dragged
        else if (e.dataTransfer.types.includes('text/plain')) {
            e.dataTransfer.dropEffect = 'copy';

            // Add template drop visual feedback
            this.canvas.style.background = 'rgba(102, 126, 234, 0.05)';
            this.canvas.style.border = '2px dashed #667eea';
        }
    }

    handleUnifiedDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();

        // Handle file drag leave
        if (e.dataTransfer.types.includes('Files')) {
            // Check if we're truly leaving the canvas container
            const rect = this.canvasContainer.getBoundingClientRect();
            const x = e.clientX;
            const y = e.clientY;

            // Only hide if mouse is completely outside the container
            if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
                const overlay = document.getElementById('dragDropOverlay');
                if (overlay) {
                    overlay.classList.remove('active');
                }
                this.canvasContainer.classList.remove('canvas-drag-over');
            }
        }
        // Handle template drag leave  
        else if (e.dataTransfer.types.includes('text/plain')) {
            // Only clear template feedback if truly leaving canvas
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX;
            const y = e.clientY;

            if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
                this.canvas.style.background = 'white';
                this.canvas.style.border = 'none';
            }
        }
    }

    handleUnifiedDrop(e) {
        // Skip template drop handling if disabled
        if (this.disableTemplateDrag && e.dataTransfer.types.includes('text/plain')) {
            return;
        }

        e.preventDefault();
        e.stopPropagation();

        // Force cleanup of all drag states first
        this.cleanupDragStates();

        // Handle file drop
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const files = Array.from(e.dataTransfer.files);

            // Get mouse position relative to canvas (considering zoom)
            const canvasRect = this.canvas.getBoundingClientRect();
            const dropX = (e.clientX - canvasRect.left) / this.zoomLevel;
            const dropY = (e.clientY - canvasRect.top) / this.zoomLevel;

            files.forEach((file, index) => {
                if (file.type.startsWith('image/')) {
                    this.createImageElementFromFile(file, dropX + (index * 20), dropY + (index * 20));
                } else if (file.type.startsWith('video/')) {
                    this.createVideoElementFromFile(file, dropX + (index * 20), dropY + (index * 20));
                }
            });

            return false;
        }
        // Handle template drop
        else if (e.dataTransfer.types.includes('text/plain')) {
            const templateType = e.dataTransfer.getData('text/plain');
            if (templateType) {
                this.createSlideFromTemplate(templateType);
            }
        }
    }

    // Clean up all drag-related visual states
    cleanupDragStates() {
        // Remove file drag overlay
        const overlay = document.getElementById('dragDropOverlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
        this.canvasContainer.classList.remove('canvas-drag-over');

        // Remove template drag feedback
        this.canvas.style.background = 'white';
        this.canvas.style.border = 'none';
    }

    // Legacy handlers (kept for backward compatibility but not used)
    handleFileDragOver(e) {
        // Check if this is actually a file being dragged
        if (e.dataTransfer.types.includes('Files')) {
            e.preventDefault();
            e.stopPropagation();
            e.dataTransfer.dropEffect = 'copy';

            // Show drag overlay
            const overlay = document.getElementById('dragDropOverlay');
            if (overlay) {
                overlay.classList.add('active');
            }
            this.canvasContainer.classList.add('canvas-drag-over');
        }
    }

    handleFileDragLeave(e) {
        // Check if this is actually a file being dragged
        if (e.dataTransfer.types.includes('Files')) {
            e.preventDefault();
            e.stopPropagation();

            // Only hide if we're actually leaving the canvas container
            if (!this.canvasContainer.contains(e.relatedTarget)) {
                const overlay = document.getElementById('dragDropOverlay');
                if (overlay) {
                    overlay.classList.remove('active');
                }
                this.canvasContainer.classList.remove('canvas-drag-over');
            }
        }
    }

    handleFileDrop(e) {
        // Check if this is actually a file being dragged
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            e.preventDefault();
            e.stopPropagation();

            // Hide drag overlay
            const overlay = document.getElementById('dragDropOverlay');
            if (overlay) {
                overlay.classList.remove('active');
            }
            this.canvasContainer.classList.remove('canvas-drag-over');

            const files = Array.from(e.dataTransfer.files);

            // Get mouse position relative to canvas (considering zoom)
            const canvasRect = this.canvas.getBoundingClientRect();
            const dropX = (e.clientX - canvasRect.left) / this.zoomLevel;
            const dropY = (e.clientY - canvasRect.top) / this.zoomLevel;

            files.forEach((file, index) => {
                if (file.type.startsWith('image/')) {
                    this.createImageElementFromFile(file, dropX + (index * 20), dropY + (index * 20));
                } else if (file.type.startsWith('video/')) {
                    this.createVideoElementFromFile(file, dropX + (index * 20), dropY + (index * 20));
                }
            });

            return false; // Prevent default behavior
        }
    }

    createImageElementFromFile(file, x, y) {
        const reader = new FileReader();
        reader.onload = (event) => {
            const el = document.createElement('div');
            el.className = 'element';
            el.dataset.type = 'image';
            el.style.position = 'absolute';
            el.style.left = `${x}px`;
            el.style.top = `${y}px`;
            el.style.width = '300px';
            el.style.height = '200px';
            el.style.zIndex = this.zIndexCounter++;
            el.style.borderRadius = '12px';
            el.style.overflow = 'hidden';
            el.style.border = '3px solid #48bb78';
            el.style.boxShadow = '0 4px 15px rgba(72, 187, 120, 0.3)';
            el.style.cursor = 'move';

            const imgElement = document.createElement('img');
            imgElement.src = event.target.result;
            imgElement.style.width = '100%';
            imgElement.style.height = '100%';
            imgElement.style.objectFit = 'cover';
            imgElement.style.display = 'block';
            imgElement.style.borderRadius = 'inherit';
            imgElement.style.pointerEvents = 'none';
            imgElement.draggable = false;
            el.appendChild(imgElement);

            // Add success animation
            el.style.transform = 'scale(0.8)';
            el.style.opacity = '0';

            this.canvas.appendChild(el);
            this.makeElementInteractive(el);
            this.selectElement(el);

            // Animate in with bounce effect
            setTimeout(() => {
                el.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                el.style.transform = 'scale(1)';
                el.style.opacity = '1';
            }, 10);

            setTimeout(() => {
                el.style.transition = '';
                this.saveState();
            }, 400);
        };
        reader.readAsDataURL(file);
    }

    createVideoElementFromFile(file, x, y) {
        const reader = new FileReader();
        reader.onload = (event) => {
            const el = document.createElement('div');
            el.className = 'element';
            el.dataset.type = 'video';
            el.style.position = 'absolute';
            el.style.left = `${x}px`;
            el.style.top = `${y}px`;
            el.style.width = '400px';
            el.style.height = '225px';
            el.style.zIndex = this.zIndexCounter++;
            el.style.borderRadius = '12px';
            el.style.background = '#000';
            el.style.border = '3px solid #4299e1';
            el.style.boxShadow = '0 4px 15px rgba(66, 153, 225, 0.3)';

            const video = document.createElement('video');
            video.src = event.target.result;
            video.controls = true;
            video.style.width = '100%';
            video.style.height = '100%';
            video.style.borderRadius = 'inherit';
            video.style.pointerEvents = 'none';
            video.draggable = false;
            el.appendChild(video);

            // Add success animation
            el.style.transform = 'scale(0.8)';
            el.style.opacity = '0';

            this.canvas.appendChild(el);
            this.makeElementInteractive(el);
            this.selectElement(el);

            // Animate in with bounce effect
            setTimeout(() => {
                el.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                el.style.transform = 'scale(1)';
                el.style.opacity = '1';
            }, 10);

            setTimeout(() => {
                el.style.transition = '';
                this.saveState();
            }, 400);
        };
        reader.readAsDataURL(file);
    }

    createTextElement(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) / this.zoomLevel;
        const y = (e.clientY - rect.top) / this.zoomLevel;

        const el = document.createElement('div');
        el.className = 'element';
        el.dataset.type = 'text';
        el.setAttribute('contenteditable', 'true');
        el.style.position = 'absolute';
        el.style.left = `${x}px`;
        el.style.top = `${y}px`;
        el.style.width = '600px';
        el.style.height = 'auto';
        el.style.fontSize = '72px';
        el.style.fontWeight = '600';
        el.style.color = '#2d3748';
        el.style.overflow = 'visible';
        el.style.zIndex = this.zIndexCounter++;
        el.style.lineHeight = '1.2';
        el.style.padding = '10px';
        el.style.background = 'rgba(255, 255, 255, 0.1)';
        el.style.backdropFilter = 'blur(5px)';
        el.style.border = '2px solid rgba(102, 126, 234, 0.2)';
        el.style.borderRadius = '8px';
        el.innerText = 'Click to edit text';

        this.canvas.appendChild(el);
        this.makeElementInteractive(el);

        // Đảm bảo chiều cao đúng ngay từ đầu
        this.updateTextElementHeight(el);

        this.selectElement(el);
        el.focus();
        this.saveState();
        this.setMode('select');

        // Auto zoom to fit the new text element
        setTimeout(() => {
            this.fitToScreen();
        }, 100);
    }

    // Hàm để tự động cập nhật chiều cao của text element
    updateTextElementHeight(element) {
        if (!element || element.dataset.type !== 'text') {
            return;
        }
        // Tạm thời bỏ height để trình duyệt tính toán chiều cao thực tế
        element.style.height = 'auto';
        // Gán chiều cao thực tế của nội dung (scrollHeight) vào style.height
        // Thêm vài pixel đệm để tránh lỗi làm tròn của trình duyệt
        element.style.height = `${element.scrollHeight + 2}px`;
    }

    // Hàm để cập nhật chiều cao cho tất cả text elements trong slide
    updateAllTextElementsHeight() {
        const textElements = this.canvas.querySelectorAll('.element[data-type="text"]');
        textElements.forEach(element => {
            this.updateTextElementHeight(element);
        });
    }

    handleKeyDown(e) {
        if (document.activeElement.hasAttribute('contenteditable') && e.key !== 'Escape') {
            if ((e.ctrlKey || e.metaKey) && ['z', 'y', 'd', 'c', 'v', 'g'].includes(e.key.toLowerCase())) {
                // Allow app shortcuts to pass through
            } else {
                return; // Block other keyboard events while typing
            }
        }

        if (this.selectedElements.length > 0 && (e.key === 'Delete' || e.key === 'Backspace')) {
            e.preventDefault();
            this.deleteSelected();
        } else if (e.ctrlKey || e.metaKey) {
            switch (e.key.toLowerCase()) {
                case 'z': e.preventDefault(); this.undo(); break;
                case 'y': e.preventDefault(); this.redo(); break;
                case 'd': e.preventDefault(); this.duplicateElement(); break;
                case 'c': e.preventDefault(); this.copySelectedElement(); break;
                case 'v': e.preventDefault(); this.pasteElement(); break;
                case 'g':
                    e.preventDefault();
                    if (e.shiftKey) this.ungroupElement();
                    else this.groupSelectedElements();
                    break;
            }
        }
    }

    handleContextMenuAction(action) {
        console.log('🎯 Context menu action:', action, 'Selected elements:', this.selectedElements.length);

        if (this.selectedElements.length === 0 && !['paste'].includes(action)) return;
        switch (action) {
            case 'group': this.groupSelectedElements(); break;
            case 'ungroup': this.ungroupElement(); break;
            case 'connectElements': this.connectTwoElements(); break;
            case 'disconnectLine': this.disconnectLine(); break;
            case 'changeConnectorType':
                console.log('📝 Calling showConnectorTypeSelector...');
                this.showConnectorTypeSelector();
                break;
            case 'copy': this.copySelectedElement(); break;
            case 'paste': this.pasteElement(); break;
            case 'duplicate': this.duplicateElement(); break;
            case 'delete': this.deleteSelected(); break;
            case 'bringForward': this.changeZIndex(1); break;
            case 'sendBackward': this.changeZIndex(-1); break;
        }
        document.getElementById('contextMenu').style.display = 'none';
    }

    groupSelectedElements() {
        if (this.selectedElements.length < 2) return;

        const groupContainer = document.createElement('div');
        groupContainer.className = 'element group-container';
        groupContainer.dataset.type = 'group';

        let minX = Infinity, minY = Infinity, maxX = 0, maxY = 0;
        this.selectedElements.forEach(el => {
            minX = Math.min(minX, el.offsetLeft);
            minY = Math.min(minY, el.offsetTop);
            maxX = Math.max(maxX, el.offsetLeft + el.offsetWidth);
            maxY = Math.max(maxY, el.offsetTop + el.offsetHeight);
        });

        const groupWidth = maxX - minX;
        const groupHeight = maxY - minY;

        groupContainer.style.left = `${minX}px`;
        groupContainer.style.top = `${minY}px`;
        groupContainer.style.width = `${groupWidth}px`;
        groupContainer.style.height = `${groupHeight}px`;
        groupContainer.style.zIndex = this.zIndexCounter++;

        this.selectedElements.forEach(el => {
            el.style.left = `${el.offsetLeft - minX}px`;
            el.style.top = `${el.offsetTop - minY}px`;
            groupContainer.appendChild(el);
        });

        this.canvas.appendChild(groupContainer);
        this.makeElementInteractive(groupContainer);
        this.selectElement(groupContainer);
        this.saveState();
    }

    ungroupElement() {
        if (this.selectedElements.length !== 1) return;
        const group = this.selectedElements[0];
        if (!group || !group.classList.contains('group-container')) return;

        const groupLeft = group.offsetLeft;
        const groupTop = group.offsetTop;

        const newSelection = [];

        while (group.firstChild) {
            const child = group.firstChild;
            if (!child.classList || !child.classList.contains('element')) {
                group.removeChild(child);
                continue;
            }
            const childLeft = parseFloat(child.style.left) || 0;
            const childTop = parseFloat(child.style.top) || 0;

            child.style.left = `${groupLeft + childLeft}px`;
            child.style.top = `${groupTop + childTop}px`;

            this.canvas.appendChild(child);
            newSelection.push(child);
        }

        group.remove();

        this.selectElement(null);
        newSelection.forEach(el => this.toggleSelection(el));

        this.saveState();
    }

    connectTwoElements(connectorType = 'straight', arrowType = 'forward') {
        if (this.selectedElements.length !== 2) return;

        const element1 = this.selectedElements[0];
        const element2 = this.selectedElements[1];

        // Assign IDs nếu chưa có
        if (!element1.dataset.id) {
            element1.dataset.id = 'element_' + Date.now() + '_1';
        }
        if (!element2.dataset.id) {
            element2.dataset.id = 'element_' + Date.now() + '_2';
        }

        // Tạo connector element
        const line = document.createElement('div');
        line.className = `element connector-line ${connectorType} arrow-${arrowType}`;
        line.dataset.type = 'connector';
        line.dataset.connectorType = connectorType;
        line.dataset.arrowType = arrowType;
        line.dataset.fromElement = element1.dataset.id;
        line.dataset.toElement = element2.dataset.id;
        line.style.position = 'absolute';
        line.style.zIndex = this.zIndexCounter++;
        line.style.cursor = 'pointer';
        line.title = `${connectorType} Connector (${arrowType} arrow) - Right click for options`;

        // Tính connection points ban đầu và lưu để tránh jumping
        const initialConnection = this.calculateNearestConnectionPoints(element1, element2);
        line._lastConnectionType = initialConnection.type;
        line._stableConnection = initialConnection;

        // Tạo connector theo loại
        if (connectorType === 'straight') {
            this.createStraightConnector(line, element1, element2, arrowType);
        } else if (connectorType === 'curved') {
            this.createCurvedConnector(line, element1, element2, arrowType);
        } else if (connectorType === 'step') {
            this.createStepConnector(line, element1, element2, arrowType);
        } else if (connectorType === 'dashed') {
            this.createDashedConnector(line, element1, element2, arrowType);
        } else if (connectorType === 'dotted') {
            this.createDottedConnector(line, element1, element2, arrowType);
        } else if (connectorType === 'thick') {
            this.createThickConnector(line, element1, element2, arrowType);
        }

        // Thêm vào canvas và make interactive
        this.canvas.appendChild(line);
        this.makeElementInteractive(line);
        this.selectElement(line);

        // Lưu trạng thái
        this.saveState();

        // Thêm listener để update line khi element di chuyển
        this.addConnectorUpdateListeners(line, element1, element2);
    }

    createStraightConnector(line, element1, element2, arrowType = 'forward') {
        console.log('📏 createStraightConnector called with arrowType:', arrowType);

        // Tính toán điểm kết nối gần nhất thay vì tâm
        const connectionPoints = this.calculateNearestConnectionPoints(element1, element2);
        const startPoint = connectionPoints.start;
        const endPoint = connectionPoints.end;

        // Tính toán góc và khoảng cách
        const deltaX = endPoint.x - startPoint.x;
        const deltaY = endPoint.y - startPoint.y;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);

        console.log('📏 Line properties:', { startPoint, endPoint, distance, angle });

        // Style cho đường thẳng
        line.style.left = `${startPoint.x}px`;
        line.style.top = `${startPoint.y - 1}px`;
        line.style.width = `${distance}px`;
        line.style.height = '2px';
        line.style.background = '#667eea';
        line.style.transformOrigin = '0 50%';
        line.style.transform = `rotate(${angle}deg)`;

        console.log('📏 About to call addArrowHeads...');

        // Thêm arrow head dựa theo arrowType với error handling
        try {
            console.log('🎯 Calling addArrowHeads with params:', { line, arrowType, angle, distance });
            this.addArrowHeads(line, arrowType, angle, distance);
            console.log('✅ addArrowHeads completed successfully');
        } catch (error) {
            console.error('❌ Error in addArrowHeads:', error);
            console.error('❌ Error stack:', error.stack);
        }

        // BACKUP: Thêm mũi tên trực tiếp nếu addArrowHeads không hoạt động
        if (line.querySelectorAll('.arrow-head').length === 0) {
            console.log('🔧 Adding backup arrow directly for type:', arrowType);
            const backupArrow = document.createElement('div');
            backupArrow.className = `arrow-head ${arrowType} backup`;

            if (arrowType === 'forward') {
                backupArrow.style.cssText = 'position: absolute; right: -8px; top: 50%; transform: translateY(-50%); width: 0; height: 0; border-left: 8px solid #667eea; border-top: 4px solid transparent; border-bottom: 4px solid transparent; z-index: 100; pointer-events: none; opacity: 1 !important; visibility: visible !important;';
            } else if (arrowType === 'circle') {
                backupArrow.style.cssText = 'position: absolute; right: -4px; top: 50%; transform: translate(-50%, -50%); width: 8px; height: 8px; border-radius: 50%; background: #667eea; border: 2px solid #667eea; z-index: 100; pointer-events: none; opacity: 1 !important; visibility: visible !important;';
                console.log('🔵 BACKUP circle arrow created with CSS:', backupArrow.style.cssText);
            } else if (arrowType === 'diamond') {
                backupArrow.style.cssText = 'position: absolute; right: -6px; top: 50%; transform: translateY(-50%) rotate(45deg); width: 8px; height: 8px; background: #667eea; border: 1px solid #667eea; z-index: 100; pointer-events: none; opacity: 1 !important; visibility: visible !important;';
            } else if (arrowType === 'square') {
                backupArrow.style.cssText = 'position: absolute; right: -4px; top: 50%; transform: translateY(-50%); width: 8px; height: 8px; background: #667eea; border: 1px solid #667eea; z-index: 100; pointer-events: none; opacity: 1 !important; visibility: visible !important;';
            } else if (arrowType === 'backward') {
                backupArrow.style.cssText = 'position: absolute; left: -8px; top: 50%; transform: translateY(-50%); width: 0; height: 0; border-right: 8px solid #667eea; border-top: 4px solid transparent; border-bottom: 4px solid transparent; z-index: 100; pointer-events: none; opacity: 1 !important; visibility: visible !important;';
            }

            line.appendChild(backupArrow);
            console.log('✅ Backup arrow added:', backupArrow);
        } else {
            console.log('✅ Arrows already exist, count:', line.querySelectorAll('.arrow-head').length);
            line.querySelectorAll('.arrow-head').forEach((arrow, index) => {
                console.log(`🔍 Existing arrow ${index}:`, arrow.className, arrow.style.cssText);
            });
        }

        // Add circle arrow when switching to circle type
        if (arrowType === 'circle') {
            console.log('🧪 Creating circle arrow');
            const testCircle = document.createElement('div');
            testCircle.className = 'arrow-head circle test-circle';
            testCircle.style.cssText = 'position: absolute; right: -20px; top: 50%; transform: translate(-50%, -50%); width: 16px; height: 16px; border-radius: 50%; background: red !important; border: 4px solid red !important; z-index: 1001; pointer-events: none; opacity: 1 !important; visibility: visible !important;';
            line.appendChild(testCircle);
            console.log('🔴 Circle arrow created:', testCircle);
        }

        // Force visibility for all arrow types
        setTimeout(() => {
            const arrows = line.querySelectorAll('.arrow-head');
            console.log('🔍 Force visibility check - found arrows:', arrows.length);

            arrows.forEach((arrow, index) => {
                arrow.style.opacity = '1';
                arrow.style.visibility = 'visible';
                arrow.style.display = 'block';

                console.log(`🔍 Arrow ${index} classes:`, arrow.className);

                // Make arrows SUPER visible for debugging
                if (arrow.classList.contains('forward')) {
                    arrow.style.borderLeft = '12px solid red !important';
                    arrow.style.borderTop = '6px solid transparent';
                    arrow.style.borderBottom = '6px solid transparent';
                    console.log('🔴 Made forward arrow RED and BIG');
                } else if (arrow.classList.contains('circle')) {
                    arrow.style.background = 'red !important';
                    arrow.style.border = '3px solid red !important';
                    arrow.style.width = '12px';
                    arrow.style.height = '12px';
                    arrow.style.zIndex = '1000';
                    console.log('🔴 Made circle arrow RED and BIG - should be VERY visible now!');
                } else if (arrow.classList.contains('diamond')) {
                    arrow.style.background = 'red !important';
                    arrow.style.border = '2px solid red !important';
                    console.log('🔴 Made diamond arrow RED');
                }

                console.log('👁️ Forcing arrow visibility:', arrow.className, arrow.style.cssText);
            });
            console.log('👁️ Total arrows found after forcing visibility:', arrows.length);

            // Also force line itself to be more visible  
            line.style.backgroundColor = '#ff0000';
            line.style.height = '4px';
            line.style.zIndex = '999';
            console.log('🔴 Made line red and thick for debugging');
        }, 50);
    }

    // Hàm tạo arrow heads cho các loại mũi tên khác nhau
    addArrowHeads(line, arrowType, angle, distance) {
        console.log('🎯 addArrowHeads called:', arrowType, 'angle:', angle); // Debug
        console.log('🎯 addArrowHeads this:', this); // Debug context
        console.log('🎯 addArrowHeads createForwardArrow exists:', typeof this.createForwardArrow); // Debug
        console.log('🔍 EXACT arrowType value:', JSON.stringify(arrowType), 'type:', typeof arrowType); // Debug
        console.log('🚨 IMPORTANT: About to process switch for arrowType:', arrowType); // Debug

        // Clear existing arrows
        line.querySelectorAll('.arrow-head').forEach(arrow => arrow.remove());

        console.log('🔍 About to enter switch statement with arrowType:', arrowType); // Debug

        switch (arrowType) {
            case 'forward':
                console.log('→ Creating forward arrow'); // Debug
                try {
                    this.createForwardArrow(line);
                    console.log('✅ createForwardArrow called successfully'); // Debug
                } catch (error) {
                    console.error('❌ Error calling createForwardArrow:', error); // Debug
                }
                break;
            case 'backward':
                console.log('← Creating backward arrow'); // Debug
                try {
                    this.createBackwardArrow(line);
                    console.log('✅ createBackwardArrow called successfully'); // Debug
                } catch (error) {
                    console.error('❌ Error calling createBackwardArrow:', error); // Debug
                }
                break;
            case 'both':
                console.log('↔ Creating both arrows'); // Debug
                try {
                    this.createForwardArrow(line);
                    this.createBackwardArrow(line);
                    console.log('✅ Both arrows called successfully'); // Debug
                } catch (error) {
                    console.error('❌ Error calling both arrows:', error); // Debug
                }
                break;
            case 'none':
                console.log('⚪ No arrows'); // Debug
                // No arrows
                break;
            case 'circle':
                console.log('● Creating circle marker'); // Debug
                try {
                    this.createCircleMarker(line, 'end');
                    console.log('✅ createCircleMarker called successfully'); // Debug
                } catch (error) {
                    console.error('❌ Error calling createCircleMarker:', error); // Debug
                }

                // 🧪 FORCE TEST CIRCLE ARROW - Always create a very visible red circle for debugging
                console.log('🧪 FORCE CREATING TEST CIRCLE ARROW FOR DEBUGGING'); // Debug
                const testCircle = document.createElement('div');
                testCircle.className = 'arrow-head circle test-debug';
                testCircle.style.position = 'absolute';
                testCircle.style.right = '-20px';
                testCircle.style.top = '50%';
                testCircle.style.transform = 'translateY(-50%)';
                testCircle.style.width = '16px';
                testCircle.style.height = '16px';
                testCircle.style.borderRadius = '50%';
                testCircle.style.background = 'red';
                testCircle.style.border = '4px solid red';
                testCircle.style.opacity = '1';
                testCircle.style.visibility = 'visible';
                testCircle.style.zIndex = '1001';
                testCircle.style.pointerEvents = 'none';
                testCircle.title = 'TEST DEBUG CIRCLE - Should be very visible';
                line.appendChild(testCircle);
                console.log('🔴 TEST CIRCLE ARROW CREATED - This should be VERY visible:', testCircle); // Debug
                break;
            case 'diamond':
                console.log('♦ Creating diamond arrow'); // Debug
                try {
                    this.createDiamondArrow(line);
                    console.log('✅ createDiamondArrow called successfully'); // Debug
                } catch (error) {
                    console.error('❌ Error calling createDiamondArrow:', error); // Debug
                }
                break;
            case 'square':
                console.log('■ Creating square marker'); // Debug
                try {
                    this.createSquareMarker(line);
                    console.log('✅ createSquareMarker called successfully'); // Debug
                } catch (error) {
                    console.error('❌ Error calling createSquareMarker:', error); // Debug
                }
                break;
            default:
                console.log('➤ Creating default forward arrow'); // Debug
                try {
                    this.createForwardArrow(line);
                    console.log('✅ Default createForwardArrow called successfully'); // Debug
                } catch (error) {
                    console.error('❌ Error calling default createForwardArrow:', error); // Debug
                }
        }

        // Final verification
        const arrowCount = line.querySelectorAll('.arrow-head').length;
        console.log('🔍 Final arrow count:', arrowCount); // Debug
    }

    createForwardArrow(line) {
        const arrowHead = document.createElement('div');
        arrowHead.className = 'arrow-head forward';
        arrowHead.style.position = 'absolute';
        arrowHead.style.right = '-60px';
        arrowHead.style.top = '50%';
        arrowHead.style.transform = 'translateY(-50%)';
        arrowHead.style.width = '0';
        arrowHead.style.height = '0';
        arrowHead.style.borderLeft = '60px solid #667eea';
        arrowHead.style.borderTop = '30px solid transparent';
        arrowHead.style.borderBottom = '30px solid transparent';
        line.appendChild(arrowHead);
        //console.log('✅ Forward arrow created:', arrowHead); // Debug
    }
    createBackwardArrow(line) {
        const arrowHead = document.createElement('div');
        arrowHead.className = 'arrow-head backward';
        arrowHead.style.position = 'absolute';
        arrowHead.style.left = '-60px';
        arrowHead.style.top = '50%';
        arrowHead.style.transform = 'translateY(-50%)';
        arrowHead.style.width = '0';
        arrowHead.style.height = '0';
        arrowHead.style.borderRight = '60px solid #667eea';
        arrowHead.style.borderTop = '30px solid transparent';
        arrowHead.style.borderBottom = '30px solid transparent';
        line.appendChild(arrowHead);
        //console.log('✅ Backward arrow created:', arrowHead); // Debug
    }

    createCircleMarker(line, position) {
        const marker = document.createElement('div');
        marker.className = 'arrow-head circle';
        marker.style.position = 'absolute';
        marker.style.width = '8px';
        marker.style.height = '8px';
        marker.style.borderRadius = '50%';
        marker.style.background = '#667eea';
        marker.style.border = '2px solid #667eea';
        marker.style.top = '50%';
        marker.style.transform = 'translate(-50%, -50%)';

        // FORCE VISIBILITY - Debug enhancement
        marker.style.opacity = '1';
        marker.style.visibility = 'visible';
        marker.style.zIndex = '1000';
        marker.style.pointerEvents = 'none';

        if (position === 'end') {
            marker.style.right = '-4px';
        } else {
            marker.style.left = '-4px';
        }

        line.appendChild(marker);
        console.log('🔵 Circle marker created:', marker, 'position:', position); // Debug
    }

    createDiamondArrow(line) {
        const diamond = document.createElement('div');
        diamond.className = 'arrow-head diamond';
        diamond.style.position = 'absolute';
        diamond.style.right = '-6px';
        diamond.style.top = '50%';
        diamond.style.transform = 'translateY(-50%) rotate(45deg)';
        diamond.style.width = '8px';
        diamond.style.height = '8px';
        diamond.style.background = '#667eea';
        diamond.style.border = '1px solid #667eea';
        line.appendChild(diamond);
    }

    createSquareMarker(line) {
        const square = document.createElement('div');
        square.className = 'arrow-head square';
        square.style.position = 'absolute';
        square.style.right = '-4px';
        square.style.top = '50%';
        square.style.transform = 'translateY(-50%)';
        square.style.width = '8px';
        square.style.height = '8px';
        square.style.background = '#667eea';
        square.style.border = '1px solid #667eea';
        line.appendChild(square);
    }

    // Tạo các loại connector mới
    createDashedConnector(line, element1, element2, arrowType) {
        this.createStraightConnector(line, element1, element2, arrowType);
        line.style.borderTop = '2px dashed #667eea';
        line.style.background = 'transparent';
        line.style.height = '0px';
    }

    createDottedConnector(line, element1, element2, arrowType) {
        this.createStraightConnector(line, element1, element2, arrowType);
        line.style.borderTop = '2px dotted #667eea';
        line.style.background = 'transparent';
        line.style.height = '0px';
    }

    createThickConnector(line, element1, element2, arrowType) {
        this.createStraightConnector(line, element1, element2, arrowType);
        line.style.height = '4px';
        line.style.background = '#667eea';
        line.style.borderRadius = '2px';
    }

    createCurvedConnector(line, element1, element2, arrowType = 'forward') {
        // Tính toán điểm kết nối gần nhất
        var connectionPoints = this.calculateNearestConnectionPoints(element1, element2);
        var startPoint = connectionPoints.start;
        var endPoint = connectionPoints.end;

        // Tính toán bounding box
        var minX = Math.min(startPoint.x, endPoint.x);
        var minY = Math.min(startPoint.y, endPoint.y);
        var maxX = Math.max(startPoint.x, endPoint.x);
        var maxY = Math.max(startPoint.y, endPoint.y);

        // Đặt vị trí container
        line.style.left = (minX - 20) + 'px';
        line.style.top = (minY - 20) + 'px';
        line.style.width = (maxX - minX + 40) + 'px';
        line.style.height = (maxY - minY + 40) + 'px';

        // Tạo SVG
        var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.style.width = '100%';
        svg.style.height = '100%';

        // Tọa độ trong SVG
        var startX = startPoint.x - minX + 20;
        var startY = startPoint.y - minY + 20;
        var endX = endPoint.x - minX + 20;
        var endY = endPoint.y - minY + 20;

        // Tính control points cho đường cong dựa trên hướng kết nối
        var distance = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
        var curvature = Math.min(distance * 0.3, 100);

        // Tính control points dựa trên vị trí relative của 2 elements
        var cp1X, cp1Y, cp2X, cp2Y;
        var startSide = connectionPoints.startSide;
        var endSide = connectionPoints.endSide;

        // Điều chỉnh control points dựa trên hướng kết nối
        if (startSide === 'right' || startSide === 'left') {
            var offsetX = startSide === 'right' ? curvature : -curvature;
            cp1X = startX + offsetX;
            cp1Y = startY;
        } else {
            var offsetY = startSide === 'bottom' ? curvature : -curvature;
            cp1X = startX;
            cp1Y = startY + offsetY;
        }

        if (endSide === 'right' || endSide === 'left') {
            var offsetX = endSide === 'left' ? curvature : -curvature;
            cp2X = endX + offsetX;
            cp2Y = endY;
        } else {
            var offsetY = endSide === 'top' ? curvature : -curvature;
            cp2X = endX;
            cp2Y = endY + offsetY;
        }

        // Tạo path
        var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        var pathData = 'M ' + startX + ' ' + startY + ' C ' + cp1X + ' ' + cp1Y + ', ' + cp2X + ' ' + cp2Y + ', ' + endX + ' ' + endY;
        path.setAttribute('d', pathData);
        path.setAttribute('stroke', '#667eea');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');

        // Thêm SVG markers cho arrows
        this.addSVGMarkers(svg, arrowType);

        // Arrow markers
        if (arrowType === 'forward' || arrowType === 'both') {
            path.setAttribute('marker-end', 'url(#arrowhead-forward)');
        }
        if (arrowType === 'backward' || arrowType === 'both') {
            path.setAttribute('marker-start', 'url(#arrowhead-backward)');
        }
        if (arrowType === 'circle') {
            path.setAttribute('marker-end', 'url(#circle-marker)');
        }
        if (arrowType === 'diamond') {
            path.setAttribute('marker-end', 'url(#diamond-marker)');
        }
        if (arrowType === 'square') {
            path.setAttribute('marker-end', 'url(#square-marker)');
        }

        svg.appendChild(path);
        line.appendChild(svg);

        // Thêm control points cho editing
        this.addControlPoints(line, cp1X + minX - 20, cp1Y + minY - 20, cp2X + minX - 20, cp2Y + minY - 20);

        // Lưu data cho update
        line.dataset.cp1X = cp1X + minX - 20;
        line.dataset.cp1Y = cp1Y + minY - 20;
        line.dataset.cp2X = cp2X + minX - 20;
        line.dataset.cp2Y = cp2Y + minY - 20;
    }

    // Hàm tạo arrow heads cho các loại mũi tên khác nhau
    addArrowHeads(line, arrowType, angle, distance) {
        // Clear existing arrows
        var arrows = line.querySelectorAll('.arrow-head');
        for (var i = 0; i < arrows.length; i++) {
            arrows[i].remove();
        }

        switch (arrowType) {
            case 'forward':
                this.createForwardArrow(line);
                break;
            case 'backward':
                this.createBackwardArrow(line);
                break;
            case 'both':
                this.createForwardArrow(line);
                this.createBackwardArrow(line);
                break;
            case 'none':
                // No arrows
                break;
            case 'circle':
                this.createCircleMarker(line, 'end');
                break;
            case 'diamond':
                this.createDiamondArrow(line);
                break;
            case 'square':
                this.createSquareMarker(line);
                break;
            default:
                this.createForwardArrow(line);
        }
    }

    createForwardArrow(line) {
        var arrowHead = document.createElement('div');
        arrowHead.className = 'arrow-head forward';
        arrowHead.style.position = 'absolute';
        arrowHead.style.right = '-6px';
        arrowHead.style.top = '50%';
        arrowHead.style.transform = 'translateY(-50%)';
        arrowHead.style.width = '0';
        arrowHead.style.height = '0';
        arrowHead.style.borderLeft = '6px solid #667eea';
        arrowHead.style.borderTop = '3px solid transparent';
        arrowHead.style.borderBottom = '3px solid transparent';
        line.appendChild(arrowHead);
    }

    createBackwardArrow(line) {
        var arrowHead = document.createElement('div');
        arrowHead.className = 'arrow-head backward';
        arrowHead.style.position = 'absolute';
        arrowHead.style.left = '-6px';
        arrowHead.style.top = '50%';
        arrowHead.style.transform = 'translateY(-50%)';
        arrowHead.style.width = '0';
        arrowHead.style.height = '0';
        arrowHead.style.borderRight = '6px solid #667eea';
        arrowHead.style.borderTop = '3px solid transparent';
        arrowHead.style.borderBottom = '3px solid transparent';
        line.appendChild(arrowHead);
    }

    createCircleMarker(line, position) {
        var marker = document.createElement('div');
        marker.className = 'arrow-head circle';
        marker.style.position = 'absolute';
        marker.style.width = '8px';
        marker.style.height = '8px';
        marker.style.borderRadius = '50%';
        marker.style.background = '#667eea';
        marker.style.border = '2px solid #667eea';
        marker.style.top = '50%';
        marker.style.transform = 'translate(-50%, -50%)';

        if (position === 'end') {
            marker.style.right = '-4px';
        } else {
            marker.style.left = '-4px';
        }

        line.appendChild(marker);
    }

    createDiamondArrow(line) {
        var diamond = document.createElement('div');
        diamond.className = 'arrow-head diamond';
        diamond.style.position = 'absolute';
        diamond.style.right = '-6px';
        diamond.style.top = '50%';
        diamond.style.transform = 'translateY(-50%) rotate(45deg)';
        diamond.style.width = '8px';
        diamond.style.height = '8px';
        diamond.style.background = '#667eea';
        diamond.style.border = '1px solid #667eea';
        line.appendChild(diamond);
    }

    createSquareMarker(line) {
        var square = document.createElement('div');
        square.className = 'arrow-head square';
        square.style.position = 'absolute';
        square.style.right = '-4px';
        square.style.top = '50%';
        square.style.transform = 'translateY(-50%)';
        square.style.width = '8px';
        square.style.height = '8px';
        square.style.background = '#667eea';
        square.style.border = '1px solid #667eea';
        line.appendChild(square);
    }

    // SVG version of addArrowHeads for SVG-based connectors
    addArrowHeads(svg, startX, startY, endX, endY, arrowType) {
        // Remove existing markers
        const existingMarkers = svg.querySelectorAll('.arrow-marker');
        existingMarkers.forEach(marker => marker.remove());

        if (arrowType === 'none') return;

        // Calculate angle for arrow direction
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);

        // Create arrow markers based on type
        switch (arrowType) {
            case 'forward':
                this.createSVGArrow(svg, endX, endY, angle, 'forward');
                break;
            case 'backward':
                this.createSVGArrow(svg, startX, startY, angle + 180, 'backward');
                break;
            case 'both':
                this.createSVGArrow(svg, endX, endY, angle, 'forward');
                this.createSVGArrow(svg, startX, startY, angle + 180, 'backward');
                break;
            case 'circle':
                this.createSVGCircle(svg, endX, endY);
                break;
            case 'diamond':
                this.createSVGDiamond(svg, endX, endY, angle);
                break;
            case 'square':
                this.createSVGSquare(svg, endX, endY);
                break;
        }
    }

    createSVGArrow(svg, x, y, angle, type) {
        const arrowGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        arrowGroup.classList.add('arrow-marker');
        arrowGroup.setAttribute('transform', `translate(${x}, ${y}) rotate(${angle})`);

        const arrow = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
        arrow.setAttribute('points', '0,0 -8,-3 -8,3');
        arrow.setAttribute('fill', '#667eea');

        arrowGroup.appendChild(arrow);
        svg.appendChild(arrowGroup);
    }

    createSVGCircle(svg, x, y) {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.classList.add('arrow-marker');
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', 4);
        circle.setAttribute('fill', '#667eea');
        circle.setAttribute('stroke', '#667eea');
        circle.setAttribute('stroke-width', 2);
        svg.appendChild(circle);
    }

    createSVGDiamond(svg, x, y, angle) {
        const diamondGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        diamondGroup.classList.add('arrow-marker');
        diamondGroup.setAttribute('transform', `translate(${x}, ${y}) rotate(${angle + 45})`);

        const diamond = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        diamond.setAttribute('x', -4);
        diamond.setAttribute('y', -4);
        diamond.setAttribute('width', 8);
        diamond.setAttribute('height', 8);
        diamond.setAttribute('fill', '#667eea');
        diamond.setAttribute('stroke', '#667eea');

        diamondGroup.appendChild(diamond);
        svg.appendChild(diamondGroup);
    }

    createSVGSquare(svg, x, y) {
        const square = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        square.classList.add('arrow-marker');
        square.setAttribute('x', x - 4);
        square.setAttribute('y', y - 4);
        square.setAttribute('width', 8);
        square.setAttribute('height', 8);
        square.setAttribute('fill', '#667eea');
        square.setAttribute('stroke', '#667eea');
        svg.appendChild(square);
    }

    // Thêm SVG markers cho các loại mũi tên
    addSVGMarkers(svg, arrowType) {
        var defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");

        // Forward arrow marker
        if (arrowType === 'forward' || arrowType === 'both') {
            var marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
            marker.setAttribute('id', 'arrowhead-forward');
            marker.setAttribute('markerWidth', '10');
            marker.setAttribute('markerHeight', '7');
            marker.setAttribute('refX', '9');
            marker.setAttribute('refY', '3.5');
            marker.setAttribute('orient', 'auto');

            var polygon = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
            polygon.setAttribute('points', '0 0, 10 3.5, 0 7');
            polygon.setAttribute('fill', '#667eea');
            marker.appendChild(polygon);
            defs.appendChild(marker);
        }

        // Backward arrow marker
        if (arrowType === 'backward' || arrowType === 'both') {
            var marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
            marker.setAttribute('id', 'arrowhead-backward');
            marker.setAttribute('markerWidth', '10');
            marker.setAttribute('markerHeight', '7');
            marker.setAttribute('refX', '1');
            marker.setAttribute('refY', '3.5');
            marker.setAttribute('orient', 'auto');

            var polygon = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
            polygon.setAttribute('points', '10 0, 0 3.5, 10 7');
            polygon.setAttribute('fill', '#667eea');
            marker.appendChild(polygon);
            defs.appendChild(marker);
        }

        // Circle marker
        if (arrowType === 'circle') {
            var marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
            marker.setAttribute('id', 'circle-marker');
            marker.setAttribute('markerWidth', '8');
            marker.setAttribute('markerHeight', '8');
            marker.setAttribute('refX', '4');
            marker.setAttribute('refY', '4');

            var circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute('cx', '4');
            circle.setAttribute('cy', '4');
            circle.setAttribute('r', '3');
            circle.setAttribute('fill', '#667eea');
            marker.appendChild(circle);
            defs.appendChild(marker);
        }

        // Diamond marker
        if (arrowType === 'diamond') {
            var marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
            marker.setAttribute('id', 'diamond-marker');
            marker.setAttribute('markerWidth', '8');
            marker.setAttribute('markerHeight', '8');
            marker.setAttribute('refX', '4');
            marker.setAttribute('refY', '4');

            var polygon = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
            polygon.setAttribute('points', '4 1, 7 4, 4 7, 1 4');
            polygon.setAttribute('fill', '#667eea');
            marker.appendChild(polygon);
            defs.appendChild(marker);
        }

        // Square marker
        if (arrowType === 'square') {
            var marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
            marker.setAttribute('id', 'square-marker');
            marker.setAttribute('markerWidth', '8');
            marker.setAttribute('markerHeight', '8');
            marker.setAttribute('refX', '4');
            marker.setAttribute('refY', '4');

            var rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            rect.setAttribute('x', '1');
            rect.setAttribute('y', '1');
            rect.setAttribute('width', '6');
            rect.setAttribute('height', '6');
            rect.setAttribute('fill', '#667eea');
            marker.appendChild(rect);
            defs.appendChild(marker);
        }

        if (defs.children.length > 0) {
            svg.appendChild(defs);
        }
    }

    createStepConnector(line, element1, element2, arrowType = 'forward') {
        // Tính toán điểm kết nối gần nhất
        var connectionPoints = this.calculateNearestConnectionPoints(element1, element2);
        var startPoint = connectionPoints.start;
        var endPoint = connectionPoints.end;

        // Tính toán bounding box
        var minX = Math.min(startPoint.x, endPoint.x);
        var minY = Math.min(startPoint.y, endPoint.y);
        var maxX = Math.max(startPoint.x, endPoint.x);
        var maxY = Math.max(startPoint.y, endPoint.y);

        line.style.left = (minX - 10) + 'px';
        line.style.top = (minY - 10) + 'px';
        line.style.width = (maxX - minX + 20) + 'px';
        line.style.height = (maxY - minY + 20) + 'px';

        // Tạo SVG cho step line
        var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.style.width = '100%';
        svg.style.height = '100%';

        var startX = startPoint.x - minX + 10;
        var startY = startPoint.y - minY + 10;
        var endX = endPoint.x - minX + 10;
        var endY = endPoint.y - minY + 10;

        // Tạo step path với logic thông minh dựa trên hướng kết nối
        var startSide = connectionPoints.startSide;
        var endSide = connectionPoints.endSide;
        var pathData;

        if (startSide === 'right' && endSide === 'left') {
            // Horizontal step
            var midX = (startX + endX) / 2;
            pathData = 'M ' + startX + ' ' + startY + ' L ' + midX + ' ' + startY + ' L ' + midX + ' ' + endY + ' L ' + endX + ' ' + endY;
        } else if (startSide === 'bottom' && endSide === 'top') {
            // Vertical step
            var midY = (startY + endY) / 2;
            pathData = 'M ' + startX + ' ' + startY + ' L ' + startX + ' ' + midY + ' L ' + endX + ' ' + midY + ' L ' + endX + ' ' + endY;
        } else {
            // Default step based on distance
            if (Math.abs(endX - startX) > Math.abs(endY - startY)) {
                var midX = (startX + endX) / 2;
                pathData = 'M ' + startX + ' ' + startY + ' L ' + midX + ' ' + startY + ' L ' + midX + ' ' + endY + ' L ' + endX + ' ' + endY;
            } else {
                var midY = (startY + endY) / 2;
                pathData = 'M ' + startX + ' ' + startY + ' L ' + startX + ' ' + midY + ' L ' + endX + ' ' + midY + ' L ' + endX + ' ' + endY;
            }
        }

        var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute('d', pathData);
        path.setAttribute('stroke', '#667eea');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');

        // Arrow head
        var arrowHead = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
        var arrowSize = 6;

        // Tính hướng của mũi tên dựa trên endSide
        if (endSide === 'right') {
            arrowHead.setAttribute('points', endX + ',' + endY + ' ' + (endX - arrowSize) + ',' + (endY - arrowSize / 2) + ' ' + (endX - arrowSize) + ',' + (endY + arrowSize / 2));
        } else if (endSide === 'left') {
            arrowHead.setAttribute('points', endX + ',' + endY + ' ' + (endX + arrowSize) + ',' + (endY - arrowSize / 2) + ' ' + (endX + arrowSize) + ',' + (endY + arrowSize / 2));
        } else if (endSide === 'bottom') {
            arrowHead.setAttribute('points', endX + ',' + endY + ' ' + (endX - arrowSize / 2) + ',' + (endY - arrowSize) + ' ' + (endX + arrowSize / 2) + ',' + (endY - arrowSize));
        } else { // top
            arrowHead.setAttribute('points', endX + ',' + endY + ' ' + (endX - arrowSize / 2) + ',' + (endY + arrowSize) + ' ' + (endX + arrowSize / 2) + ',' + (endY + arrowSize));
        }

        arrowHead.setAttribute('class', 'arrow-head');
        arrowHead.setAttribute('fill', '#667eea');

        svg.appendChild(path);
        svg.appendChild(arrowHead);
        line.appendChild(svg);
    }

    createDashedConnector(line, element1, element2, arrowType = 'forward') {
        // Tính toán điểm kết nối gần nhất
        var connectionPoints = this.calculateNearestConnectionPoints(element1, element2);
        var startPoint = connectionPoints.start;
        var endPoint = connectionPoints.end;

        // Tính toán bounding box
        var minX = Math.min(startPoint.x, endPoint.x);
        var minY = Math.min(startPoint.y, endPoint.y);
        var maxX = Math.max(startPoint.x, endPoint.x);
        var maxY = Math.max(startPoint.y, endPoint.y);

        line.style.left = (minX - 10) + 'px';
        line.style.top = (minY - 10) + 'px';
        line.style.width = (maxX - minX + 20) + 'px';
        line.style.height = (maxY - minY + 20) + 'px';

        // Tạo SVG cho dashed line
        var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.style.width = '100%';
        svg.style.height = '100%';

        var startX = startPoint.x - minX + 10;
        var startY = startPoint.y - minY + 10;
        var endX = endPoint.x - minX + 10;
        var endY = endPoint.y - minY + 10;

        var line_el = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line_el.setAttribute('x1', startX);
        line_el.setAttribute('y1', startY);
        line_el.setAttribute('x2', endX);
        line_el.setAttribute('y2', endY);
        line_el.setAttribute('stroke', '#667eea');
        line_el.setAttribute('stroke-width', '2');
        line_el.setAttribute('stroke-dasharray', '5,5');

        svg.appendChild(line_el);
        this.addArrowHeads(svg, startX, startY, endX, endY, arrowType);
        line.appendChild(svg);
    }

    createDottedConnector(line, element1, element2, arrowType = 'forward') {
        // Tính toán điểm kết nối gần nhất
        var connectionPoints = this.calculateNearestConnectionPoints(element1, element2);
        var startPoint = connectionPoints.start;
        var endPoint = connectionPoints.end;

        // Tính toán bounding box
        var minX = Math.min(startPoint.x, endPoint.x);
        var minY = Math.min(startPoint.y, endPoint.y);
        var maxX = Math.max(startPoint.x, endPoint.x);
        var maxY = Math.max(startPoint.y, endPoint.y);

        line.style.left = (minX - 10) + 'px';
        line.style.top = (minY - 10) + 'px';
        line.style.width = (maxX - minX + 20) + 'px';
        line.style.height = (maxY - minY + 20) + 'px';

        // Tạo SVG cho dotted line
        var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.style.width = '100%';
        svg.style.height = '100%';

        var startX = startPoint.x - minX + 10;
        var startY = startPoint.y - minY + 10;
        var endX = endPoint.x - minX + 10;
        var endY = endPoint.y - minY + 10;

        var line_el = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line_el.setAttribute('x1', startX);
        line_el.setAttribute('y1', startY);
        line_el.setAttribute('x2', endX);
        line_el.setAttribute('y2', endY);
        line_el.setAttribute('stroke', '#667eea');
        line_el.setAttribute('stroke-width', '2');
        line_el.setAttribute('stroke-dasharray', '2,3');

        svg.appendChild(line_el);
        this.addArrowHeads(svg, startX, startY, endX, endY, arrowType);
        line.appendChild(svg);
    }

    createThickConnector(line, element1, element2, arrowType = 'forward') {
        // Tính toán điểm kết nối gần nhất
        var connectionPoints = this.calculateNearestConnectionPoints(element1, element2);
        var startPoint = connectionPoints.start;
        var endPoint = connectionPoints.end;

        // Tính toán bounding box
        var minX = Math.min(startPoint.x, endPoint.x);
        var minY = Math.min(startPoint.y, endPoint.y);
        var maxX = Math.max(startPoint.x, endPoint.x);
        var maxY = Math.max(startPoint.y, endPoint.y);

        line.style.left = (minX - 10) + 'px';
        line.style.top = (minY - 10) + 'px';
        line.style.width = (maxX - minX + 20) + 'px';
        line.style.height = (maxY - minY + 20) + 'px';

        // Tạo SVG cho thick line
        var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.style.width = '100%';
        svg.style.height = '100%';

        var startX = startPoint.x - minX + 10;
        var startY = startPoint.y - minY + 10;
        var endX = endPoint.x - minX + 10;
        var endY = endPoint.y - minY + 10;

        var line_el = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line_el.setAttribute('x1', startX);
        line_el.setAttribute('y1', startY);
        line_el.setAttribute('x2', endX);
        line_el.setAttribute('y2', endY);
        line_el.setAttribute('stroke', '#667eea');
        line_el.setAttribute('stroke-width', '4');

        svg.appendChild(line_el);
        this.addArrowHeads(svg, startX, startY, endX, endY, arrowType);
        line.appendChild(svg);
    }

    // Tính toán điểm kết nối gần nhất với stable connection để tránh jumping
    calculateNearestConnectionPoints(element1, element2, existingLine = null) {
        const rect1 = {
            left: element1.offsetLeft,
            top: element1.offsetTop,
            right: element1.offsetLeft + element1.offsetWidth,
            bottom: element1.offsetTop + element1.offsetHeight,
            centerX: element1.offsetLeft + element1.offsetWidth / 2,
            centerY: element1.offsetTop + element1.offsetHeight / 2,
            width: element1.offsetWidth,
            height: element1.offsetHeight
        };

        const rect2 = {
            left: element2.offsetLeft,
            top: element2.offsetTop,
            right: element2.offsetLeft + element2.offsetWidth,
            bottom: element2.offsetTop + element2.offsetHeight,
            centerX: element2.offsetLeft + element2.offsetWidth / 2,
            centerY: element2.offsetTop + element2.offsetHeight / 2,
            width: element2.offsetWidth,
            height: element2.offsetHeight
        };

        // Xác định vị trí tương đối giữa 2 elements
        const deltaX = rect2.centerX - rect1.centerX;
        const deltaY = rect2.centerY - rect1.centerY;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

        // Tạo danh sách các điểm kết nối với offset
        const offset = 3;
        const getConnectionPoints = (rect) => {
            return {
                top: { x: rect.centerX, y: rect.top - offset, side: 'top' },
                right: { x: rect.right + offset, y: rect.centerY, side: 'right' },
                bottom: { x: rect.centerX, y: rect.bottom + offset, side: 'bottom' },
                left: { x: rect.left - offset, y: rect.centerY, side: 'left' }
            };
        };

        const points1 = getConnectionPoints(rect1);
        const points2 = getConnectionPoints(rect2);

        // ENHANCED STABILITY: Kiểm tra xem có stable connection từ lần trước không
        let currentConnectionType = null;
        if (existingLine && existingLine._lastConnectionType) {
            currentConnectionType = existingLine._lastConnectionType;
        }

        // IMPROVED ALGORITHM: Thuật toán ổn định với hysteresis threshold RẤT cao cho existing connections
        const baseThreshold = 1.5;  // Giảm từ 1.8 để dễ kết nối ban đầu
        const hysteresisThreshold = currentConnectionType ? 3.5 : baseThreshold; // TĂNG MẠNH từ 2.2 → 3.5 để tránh nhảy
        const absX = Math.abs(deltaX);
        const absY = Math.abs(deltaY);

        let bestConnection = null;

        // PRIORITY CHECK: Nếu có stable connection, kiểm tra nó trước tiên với tolerance RẤT cao
        if (existingLine && existingLine._stableConnection) {
            const stableConn = existingLine._stableConnection;

            // Tạo test connection với stable parameters
            const testConnection = {
                start: points1[stableConn.startSide] || points1.right,
                end: points2[stableConn.endSide] || points2.left,
                startSide: stableConn.startSide || 'right',
                endSide: stableConn.endSide || 'left',
                type: stableConn.type || 'stable'
            };

            // Tính khoảng cách của stable connection
            const stableDistance = Math.sqrt(
                Math.pow(testConnection.end.x - testConnection.start.x, 2) +
                Math.pow(testConnection.end.y - testConnection.start.y, 2)
            );

            // VERY HIGH TOLERANCE: Nếu khoảng cách không thay đổi quá nhiều, GIỮ NGUYÊN stable connection
            if (Math.abs(stableDistance - distance) < distance * 0.5) { // Tăng từ 30% → 50% tolerance
                bestConnection = testConnection;
                console.log('🔒 Maintaining stable connection:', bestConnection.type);
            }
        }

        // Nếu chưa có bestConnection, tính toán mới
        if (!bestConnection) {
            // Kiểm tra các trường hợp rõ ràng trước (horizontal/vertical)
            if (absX > absY * hysteresisThreshold) {
                // Chắc chắn là horizontal connection
                if (deltaX > 0) {
                    bestConnection = {
                        start: points1.right,
                        end: points2.left,
                        startSide: 'right',
                        endSide: 'left',
                        type: 'horizontal-right'
                    };
                } else {
                    bestConnection = {
                        start: points1.left,
                        end: points2.right,
                        startSide: 'left',
                        endSide: 'right',
                        type: 'horizontal-left'
                    };
                }
            } else if (absY > absX * hysteresisThreshold) {
                // Chắc chắn là vertical connection
                if (deltaY > 0) {
                    bestConnection = {
                        start: points1.bottom,
                        end: points2.top,
                        startSide: 'bottom',
                        endSide: 'top',
                        type: 'vertical-down'
                    };
                } else {
                    bestConnection = {
                        start: points1.top,
                        end: points2.bottom,
                        startSide: 'top',
                        endSide: 'bottom',
                        type: 'vertical-up'
                    };
                }
            } else {
                // Diagonal connection - chọn based on quadrant với priority ổn định
                if (deltaX > 0 && deltaY > 0) {
                    // Quadrant 1: Bottom-right
                    if (absX > absY) {
                        bestConnection = {
                            start: points1.right,
                            end: points2.left,
                            startSide: 'right',
                            endSide: 'left',
                            type: 'diagonal-bottom-right-h'
                        };
                    } else {
                        bestConnection = {
                            start: points1.bottom,
                            end: points2.top,
                            startSide: 'bottom',
                            endSide: 'top',
                            type: 'diagonal-bottom-right-v'
                        };
                    }
                } else if (deltaX < 0 && deltaY > 0) {
                    // Quadrant 2: Bottom-left
                    if (absX > absY) {
                        bestConnection = {
                            start: points1.left,
                            end: points2.right,
                            startSide: 'left',
                            endSide: 'right',
                            type: 'diagonal-bottom-left-h'
                        };
                    } else {
                        bestConnection = {
                            start: points1.bottom,
                            end: points2.top,
                            startSide: 'bottom',
                            endSide: 'top',
                            type: 'diagonal-bottom-left-v'
                        };
                    }
                } else if (deltaX < 0 && deltaY < 0) {
                    // Quadrant 3: Top-left
                    if (absX > absY) {
                        bestConnection = {
                            start: points1.left,
                            end: points2.right,
                            startSide: 'left',
                            endSide: 'right',
                            type: 'diagonal-top-left-h'
                        };
                    } else {
                        bestConnection = {
                            start: points1.top,
                            end: points2.bottom,
                            startSide: 'top',
                            endSide: 'bottom',
                            type: 'diagonal-top-left-v'
                        };
                    }
                } else {
                    // Quadrant 4: Top-right
                    if (absX > absY) {
                        bestConnection = {
                            start: points1.right,
                            end: points2.left,
                            startSide: 'right',
                            endSide: 'left',
                            type: 'diagonal-top-right-h'
                        };
                    } else {
                        bestConnection = {
                            start: points1.top,
                            end: points2.bottom,
                            startSide: 'top',
                            endSide: 'bottom',
                            type: 'diagonal-top-right-v'
                        };
                    }
                }
            }
        }

        // Fallback safety
        if (!bestConnection) {
            bestConnection = {
                start: points1.right,
                end: points2.left,
                startSide: 'right',
                endSide: 'left',
                type: 'fallback'
            };
        }

        // Tính toán distance cuối cùng
        bestConnection.distance = Math.sqrt(
            Math.pow(bestConnection.end.x - bestConnection.start.x, 2) +
            Math.pow(bestConnection.end.y - bestConnection.start.y, 2)
        );

        return bestConnection;
    }

    addControlPoints(line, cp1X, cp1Y, cp2X, cp2Y) {
        // Control point 1
        const cp1 = document.createElement('div');
        cp1.className = 'connector-control-point';
        cp1.style.left = `${cp1X}px`;
        cp1.style.top = `${cp1Y}px`;
        cp1.dataset.controlPoint = '1';

        // Control point 2
        const cp2 = document.createElement('div');
        cp2.className = 'connector-control-point';
        cp2.style.left = `${cp2X}px`;
        cp2.style.top = `${cp2Y}px`;
        cp2.dataset.controlPoint = '2';

        // Thêm vào canvas (không vào line để tránh bị ảnh hưởng bởi transform)
        this.canvas.appendChild(cp1);
        this.canvas.appendChild(cp2);

        // Lưu reference
        line._controlPoints = [cp1, cp2];

        // Thêm drag events cho control points
        this.makeControlPointDraggable(cp1, line);
        this.makeControlPointDraggable(cp2, line);
    }

    makeControlPointDraggable(controlPoint, line) {
        let isDragging = false;
        let startPos = { x: 0, y: 0 };

        controlPoint.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            isDragging = true;
            controlPoint.classList.add('dragging');
            startPos.x = e.clientX;
            startPos.y = e.clientY;

            const mouseMoveHandler = (e) => {
                if (!isDragging) return;

                const deltaX = (e.clientX - startPos.x) / this.zoomLevel;
                const deltaY = (e.clientY - startPos.y) / this.zoomLevel;

                const currentLeft = parseFloat(controlPoint.style.left);
                const currentTop = parseFloat(controlPoint.style.top);

                controlPoint.style.left = `${currentLeft + deltaX}px`;
                controlPoint.style.top = `${currentTop + deltaY}px`;

                startPos.x = e.clientX;
                startPos.y = e.clientY;

                // Update connector
                this.updateCurvedConnector(line);
            };

            const mouseUpHandler = () => {
                isDragging = false;
                controlPoint.classList.remove('dragging');
                document.removeEventListener('mousemove', mouseMoveHandler);
                document.removeEventListener('mouseup', mouseUpHandler);
                this.saveState();
            };

            document.addEventListener('mousemove', mouseMoveHandler);
            document.addEventListener('mouseup', mouseUpHandler);
        });
    }

    getElementId(element) {
        if (!element.dataset.id) {
            element.dataset.id = 'element_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        return element.dataset.id;
    }

    addConnectorUpdateListeners(line, element1, element2) {
        // Function để update vị trí connector với thuật toán ổn định
        const updateLine = () => {
            const connectorType = line.dataset.connectorType || 'straight';
            const arrowType = line.dataset.arrowType || 'forward';

            // Sử dụng cùng thuật toán với lúc tạo để đảm bảo consistency
            if (connectorType === 'straight') {
                this.updateStraightConnector(line, element1, element2, arrowType);
            } else if (connectorType === 'curved') {
                this.updateCurvedConnector(line, element1, element2, arrowType);
            } else if (connectorType === 'step') {
                this.updateStepConnector(line, element1, element2, arrowType);
            } else if (connectorType === 'dashed') {
                this.updateDashedConnector(line, element1, element2, arrowType);
            } else if (connectorType === 'dotted') {
                this.updateDottedConnector(line, element1, element2, arrowType);
            } else if (connectorType === 'thick') {
                this.updateThickConnector(line, element1, element2, arrowType);
            }
        };

        // Lưu reference để có thể remove listener sau này
        line._updateLine = updateLine;
        line._connectedElements = [element1, element2];

        // Thêm class để track connected elements
        element1.classList.add('has-connector');
        element2.classList.add('has-connector');

        // Store original handlers
        element1._originalMouseMove = element1.onmousemove;
        element2._originalMouseMove = element2.onmousemove;
    }

    // Các hàm update connector cụ thể cho từng loại
    updateStraightConnector(line, element1, element2, arrowType) {
        // Sử dụng stable connection với existingLine parameter
        const connectionPoints = this.calculateNearestConnectionPoints(element1, element2, line);
        const startPoint = connectionPoints.start;
        const endPoint = connectionPoints.end;

        // Update stable connection với debug logging
        const prevType = line._lastConnectionType;
        line._lastConnectionType = connectionPoints.type;
        line._stableConnection = connectionPoints;

        // Debug logging để kiểm tra switching
        if (prevType && prevType !== connectionPoints.type) {
            console.log(`🔄 Connector switched: ${prevType} → ${connectionPoints.type}`);
        }

        const deltaX = endPoint.x - startPoint.x;
        const deltaY = endPoint.y - startPoint.y;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);

        line.style.left = `${startPoint.x}px`;
        line.style.top = `${startPoint.y - 1}px`;
        line.style.width = `${distance}px`;
        line.style.height = '2px';
        line.style.transform = `rotate(${angle}deg)`;

        // Update arrow heads nếu cần
        this.addArrowHeads(line, arrowType, angle, distance);
    }

    updateDashedConnector(line, element1, element2, arrowType) {
        // Clear existing content
        line.innerHTML = '';

        // Recreate với new positions
        this.createDashedConnector(line, element1, element2, arrowType);
    }

    updateDottedConnector(line, element1, element2, arrowType) {
        // Clear existing content
        line.innerHTML = '';

        // Recreate với new positions
        this.createDottedConnector(line, element1, element2, arrowType);
    }

    updateThickConnector(line, element1, element2, arrowType) {
        // Clear existing content
        line.innerHTML = '';

        // Recreate với new positions
        this.createThickConnector(line, element1, element2, arrowType);
    }

    updateCurvedConnector(line, element1, element2, arrowType) {
        // Clear existing content
        line.innerHTML = '';

        // Recreate với new positions
        this.createCurvedConnector(line, element1, element2, arrowType);
    }

    updateStepConnector(line, element1, element2, arrowType) {
        // Clear existing content
        line.innerHTML = '';

        // Recreate với new positions
        this.createStepConnector(line, element1, element2, arrowType);
    }

    updateConnectorLines() {
        // ENHANCED: Chỉ update khi thực sự cần thiết để tránh nhảy khi hover
        if (!this.isDragging && !this.isResizing && !this.forceConnectorUpdate) {
            // Nếu không đang drag/resize, không cần update connector
            return;
        }

        // Tìm tất cả connector lines trong canvas
        const connectors = this.canvas.querySelectorAll('.connector-line');

        connectors.forEach(line => {
            const fromId = line.dataset.fromElement;
            const toId = line.dataset.toElement;
            const connectorType = line.dataset.connectorType || 'straight';

            if (!fromId || !toId) return;

            // Tìm các elements được nối
            const element1 = this.canvas.querySelector(`[data-id="${fromId}"]`);
            const element2 = this.canvas.querySelector(`[data-id="${toId}"]`);

            // Nếu cả 2 elements vẫn tồn tại, update line
            if (element1 && element2) {
                const arrowType = line.dataset.arrowType || 'forward';

                // EXTRA CHECK: Chỉ update nếu một trong 2 elements đang được drag HOẶC force update
                if (this.forceConnectorUpdate ||
                    (this.draggedElement && (element1 === this.draggedElement || element2 === this.draggedElement))) {
                    if (connectorType === 'straight') {
                        this.updateStraightConnector(line, element1, element2, arrowType);
                    } else if (connectorType === 'curved') {
                        this.updateCurvedConnector(line, element1, element2, arrowType);
                    } else if (connectorType === 'step') {
                        this.updateStepConnector(line, element1, element2, arrowType);
                    } else if (connectorType === 'dashed') {
                        this.updateDashedConnector(line, element1, element2, arrowType);
                    } else if (connectorType === 'dotted') {
                        this.updateDottedConnector(line, element1, element2, arrowType);
                    } else if (connectorType === 'thick') {
                        this.updateThickConnector(line, element1, element2, arrowType);
                    }
                }
            } else {
                // Nếu một trong 2 elements bị xóa, xóa connector và control points
                this.removeConnector(line);
            }
        });
    }

    // Force update tất cả connectors (dùng khi cần thiết như sau khi drag xong)
    updateConnectorLinesForced() {
        const connectors = this.canvas.querySelectorAll('.connector-line');

        connectors.forEach(line => {
            const fromId = line.dataset.fromElement;
            const toId = line.dataset.toElement;
            const connectorType = line.dataset.connectorType || 'straight';

            if (!fromId || !toId) return;

            const element1 = this.canvas.querySelector(`[data-id="${fromId}"]`);
            const element2 = this.canvas.querySelector(`[data-id="${toId}"]`);

            if (element1 && element2) {
                const arrowType = line.dataset.arrowType || 'forward';

                if (connectorType === 'straight') {
                    this.updateStraightConnector(line, element1, element2, arrowType);
                } else if (connectorType === 'curved') {
                    this.updateCurvedConnector(line, element1, element2, arrowType);
                } else if (connectorType === 'step') {
                    this.updateStepConnector(line, element1, element2, arrowType);
                } else if (connectorType === 'dashed') {
                    this.updateDashedConnector(line, element1, element2, arrowType);
                } else if (connectorType === 'dotted') {
                    this.updateDottedConnector(line, element1, element2, arrowType);
                } else if (connectorType === 'thick') {
                    this.updateThickConnector(line, element1, element2, arrowType);
                }
            } else {
                this.removeConnector(line);
            }
        });
    }

    updateStraightConnector(line, element1, element2) {
        // ENHANCED: Sử dụng stable connection với existingLine parameter để tránh nhảy
        const connectionPoints = this.calculateNearestConnectionPoints(element1, element2, line);
        const startPoint = connectionPoints.start;
        const endPoint = connectionPoints.end;

        // Update stable connection với debug logging
        const prevType = line._lastConnectionType;
        line._lastConnectionType = connectionPoints.type;
        line._stableConnection = connectionPoints;

        // Debug logging để kiểm tra switching (có thể tắt trong production)
        if (prevType && prevType !== connectionPoints.type) {
            console.log(`🔄 Connector switched: ${prevType} → ${connectionPoints.type}`);
        }

        const deltaX = endPoint.x - startPoint.x;
        const deltaY = endPoint.y - startPoint.y;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);

        // Chỉ update style nếu có thay đổi đáng kể để tránh re-render không cần thiết
        const currentLeft = parseFloat(line.style.left) || 0;
        const currentTop = parseFloat(line.style.top) || 0;
        const currentWidth = parseFloat(line.style.width) || 0;
        const currentAngle = line._lastAngle || 0;

        const threshold = 0.5; // Ngưỡng thay đổi tối thiểu

        if (Math.abs(currentLeft - startPoint.x) > threshold ||
            Math.abs(currentTop - (startPoint.y - 1)) > threshold ||
            Math.abs(currentWidth - distance) > threshold ||
            Math.abs(currentAngle - angle) > 0.1) {

            line.style.left = `${startPoint.x}px`;
            line.style.top = `${startPoint.y - 1}px`;
            line.style.width = `${distance}px`;
            line.style.height = '2px';
            line.style.transform = `rotate(${angle}deg)`;
            line._lastAngle = angle;

            // Update arrow heads
            const arrowType = line.dataset.arrowType || 'forward';
            this.addArrowHeads(line, arrowType, angle, distance);
        }
    }

    updateCurvedConnector(line, element1, element2) {
        if (!element1 || !element2) return;

        // Tính toán điểm kết nối gần nhất
        const connectionPoints = this.calculateNearestConnectionPoints(element1, element2);
        const startPoint = connectionPoints.start;
        const endPoint = connectionPoints.end;

        // Get current control points positions or calculate new ones
        let cp1X, cp1Y, cp2X, cp2Y;

        if (line._controlPoints && line._controlPoints.length === 2) {
            // Use current control points positions
            cp1X = parseFloat(line._controlPoints[0].style.left);
            cp1Y = parseFloat(line._controlPoints[0].style.top);
            cp2X = parseFloat(line._controlPoints[1].style.left);
            cp2Y = parseFloat(line._controlPoints[1].style.top);
        } else {
            // Calculate new control points based on connection sides
            const distance = Math.sqrt(Math.pow(endPoint.x - startPoint.x, 2) + Math.pow(endPoint.y - startPoint.y, 2));
            const curvature = Math.min(distance * 0.3, 100);

            const startSide = connectionPoints.startSide;
            const endSide = connectionPoints.endSide;

            if (startSide === 'right' || startSide === 'left') {
                const offsetX = startSide === 'right' ? curvature : -curvature;
                cp1X = startPoint.x + offsetX;
                cp1Y = startPoint.y;
            } else {
                const offsetY = startSide === 'bottom' ? curvature : -curvature;
                cp1X = startPoint.x;
                cp1Y = startPoint.y + offsetY;
            }

            if (endSide === 'right' || endSide === 'left') {
                const offsetX = endSide === 'left' ? curvature : -curvature;
                cp2X = endPoint.x + offsetX;
                cp2Y = endPoint.y;
            } else {
                const offsetY = endSide === 'top' ? curvature : -curvature;
                cp2X = endPoint.x;
                cp2Y = endPoint.y + offsetY;
            }
        }

        // Update container position
        const minX = Math.min(startPoint.x, endPoint.x, cp1X, cp2X);
        const minY = Math.min(startPoint.y, endPoint.y, cp1Y, cp2Y);
        const maxX = Math.max(startPoint.x, endPoint.x, cp1X, cp2X);
        const maxY = Math.max(startPoint.y, endPoint.y, cp1Y, cp2Y);

        line.style.left = `${minX - 20}px`;
        line.style.top = `${minY - 20}px`;
        line.style.width = `${maxX - minX + 40}px`;
        line.style.height = `${maxY - minY + 40}px`;

        // Update SVG path
        const svg = line.querySelector('svg');
        if (svg) {
            const startX = startPoint.x - minX + 20;
            const startY = startPoint.y - minY + 20;
            const endX = endPoint.x - minX + 20;
            const endY = endPoint.y - minY + 20;
            const cp1XSvg = cp1X - minX + 20;
            const cp1YSvg = cp1Y - minY + 20;
            const cp2XSvg = cp2X - minX + 20;
            const cp2YSvg = cp2Y - minY + 20;

            const path = svg.querySelector('path');
            if (path) {
                const pathData = `M ${startX} ${startY} C ${cp1XSvg} ${cp1YSvg}, ${cp2XSvg} ${cp2YSvg}, ${endX} ${endY}`;
                path.setAttribute('d', pathData);
            }

            // Update arrow head
            const arrowHead = svg.querySelector('.arrow-head');
            if (arrowHead) {
                const angle = Math.atan2(endY - cp2YSvg, endX - cp2XSvg);
                const arrowSize = 8;
                const arrow1X = endX - arrowSize * Math.cos(angle - Math.PI / 6);
                const arrow1Y = endY - arrowSize * Math.sin(angle - Math.PI / 6);
                const arrow2X = endX - arrowSize * Math.cos(angle + Math.PI / 6);
                const arrow2Y = endY - arrowSize * Math.sin(angle + Math.PI / 6);

                arrowHead.setAttribute('points', `${endX},${endY} ${arrow1X},${arrow1Y} ${arrow2X},${arrow2Y}`);
            }
        }

        // Update control points positions if they exist
        if (line._controlPoints && line._controlPoints.length === 2) {
            line._controlPoints[0].style.left = `${cp1X}px`;
            line._controlPoints[0].style.top = `${cp1Y}px`;
            line._controlPoints[1].style.left = `${cp2X}px`;
            line._controlPoints[1].style.top = `${cp2Y}px`;
        }
    }

    updateStepConnector(line, element1, element2) {
        // Tính toán điểm kết nối gần nhất
        const connectionPoints = this.calculateNearestConnectionPoints(element1, element2);
        const startPoint = connectionPoints.start;
        const endPoint = connectionPoints.end;

        const minX = Math.min(startPoint.x, endPoint.x);
        const minY = Math.min(startPoint.y, endPoint.y);
        const maxX = Math.max(startPoint.x, endPoint.x);
        const maxY = Math.max(startPoint.y, endPoint.y);

        line.style.left = `${minX - 10}px`;
        line.style.top = `${minY - 10}px`;
        line.style.width = `${maxX - minX + 20}px`;
        line.style.height = `${maxY - minY + 20}px`;

        const svg = line.querySelector('svg');
        if (svg) {
            const startX = startPoint.x - minX + 10;
            const startY = startPoint.y - minY + 10;
            const endX = endPoint.x - minX + 10;
            const endY = endPoint.y - minY + 10;

            // Tạo step path với logic thông minh dựa trên hướng kết nối
            const startSide = connectionPoints.startSide;
            const endSide = connectionPoints.endSide;
            let pathData;

            if (startSide === 'right' && endSide === 'left') {
                // Horizontal step
                const midX = (startX + endX) / 2;
                pathData = `M ${startX} ${startY} L ${midX} ${startY} L ${midX} ${endY} L ${endX} ${endY}`;
            } else if (startSide === 'bottom' && endSide === 'top') {
                // Vertical step
                const midY = (startY + endY) / 2;
                pathData = `M ${startX} ${startY} L ${startX} ${midY} L ${endX} ${midY} L ${endX} ${endY}`;
            } else {
                // Default step based on distance
                if (Math.abs(endX - startX) > Math.abs(endY - startY)) {
                    const midX = (startX + endX) / 2;
                    pathData = `M ${startX} ${startY} L ${midX} ${startY} L ${midX} ${endY} L ${endX} ${endY}`;
                } else {
                    const midY = (startY + endY) / 2;
                    pathData = `M ${startX} ${startY} L ${startX} ${midY} L ${endX} ${midY} L ${endX} ${endY}`;
                }
            }

            const path = svg.querySelector('path');
            if (path) {
                path.setAttribute('d', pathData);
            }

            // Update arrow head với hướng chính xác
            const arrowHead = svg.querySelector('.arrow-head');
            if (arrowHead) {
                const arrowSize = 6;
                const endSide = connectionPoints.endSide;

                if (endSide === 'right') {
                    arrowHead.setAttribute('points', `${endX},${endY} ${endX - arrowSize},${endY - arrowSize / 2} ${endX - arrowSize},${endY + arrowSize / 2}`);
                } else if (endSide === 'left') {
                    arrowHead.setAttribute('points', `${endX},${endY} ${endX + arrowSize},${endY - arrowSize / 2} ${endX + arrowSize},${endY + arrowSize / 2}`);
                } else if (endSide === 'bottom') {
                    arrowHead.setAttribute('points', `${endX},${endY} ${endX - arrowSize / 2},${endY - arrowSize} ${endX + arrowSize / 2},${endY - arrowSize}`);
                } else { // top
                    arrowHead.setAttribute('points', `${endX},${endY} ${endX - arrowSize / 2},${endY + arrowSize} ${endX + arrowSize / 2},${endY + arrowSize}`);
                }
            }
        }
    }

    cleanupConnector(line) {
        console.log('🧹 cleanupConnector called'); // Debug
        // Remove control points if they exist
        if (line._controlPoints) {
            line._controlPoints.forEach(cp => cp.remove());
            delete line._controlPoints;
        }
        // IMPORTANT: Don't remove the line itself here in changeConnectorType context
        // line.remove() will be called separately when needed
    }

    // NEW: Separate function for full cleanup with line removal
    removeConnector(line) {
        console.log('❌ removeConnector called'); // Debug
        this.cleanupConnector(line);
        line.remove();
    }

    disconnectLine() {
        if (this.selectedElements.length !== 1) return;

        const line = this.selectedElements[0];
        if (!line.classList.contains('connector-line')) return;

        const fromId = line.dataset.fromElement;
        const toId = line.dataset.toElement;

        // Remove connector indicators từ connected elements
        if (fromId) {
            const element1 = this.canvas.querySelector(`[data-id="${fromId}"]`);
            if (element1) {
                const remainingConnectors1 = this.canvas.querySelectorAll(`.connector-line[data-from-element="${fromId}"], .connector-line[data-to-element="${fromId}"]`);
                if (remainingConnectors1.length <= 1) { // <= 1 vì line hiện tại sắp bị xóa
                    element1.classList.remove('has-connector');
                }
            }
        }

        if (toId) {
            const element2 = this.canvas.querySelector(`[data-id="${toId}"]`);
            if (element2) {
                const remainingConnectors2 = this.canvas.querySelectorAll(`.connector-line[data-from-element="${toId}"], .connector-line[data-to-element="${toId}"]`);
                if (remainingConnectors2.length <= 1) {
                    element2.classList.remove('has-connector');
                }
            }
        }

        // Use new removeConnector function
        this.removeConnector(line);
        this.selectElement(null);
        this.saveState();
    }

    copySelectedElement() {
        if (this.selectedElements.length !== 1) return;
        this.clipboard = this.selectedElements[0].cloneNode(true);
    }

    pasteElement() {
        if (!this.clipboard) return;
        const newEl = this.clipboard.cloneNode(true);
        newEl.style.left = `${(parseInt(newEl.style.left) || 0) + 30}px`;
        newEl.style.top = `${(parseInt(newEl.style.top) || 0) + 30}px`;
        newEl.style.zIndex = this.zIndexCounter++;
        newEl.classList.remove('selected');
        this.canvas.appendChild(newEl);
        this.makeElementInteractive(newEl);
        this.selectElement(newEl);
        this.saveState();
    }

    deleteSelected() {
        if (this.selectedElements.length > 0) {
            // Trước khi xóa elements, lưu IDs của chúng để xóa connectors
            const elementIds = this.selectedElements.map(el => el.dataset.id).filter(id => id);

            // Xóa elements
            this.selectedElements.forEach(el => {
                // Nếu là connector line, cũng cần xóa reference từ connected elements
                if (el.classList.contains('connector-line')) {
                    const fromId = el.dataset.fromElement;
                    const toId = el.dataset.toElement;

                    if (fromId && toId) {
                        const element1 = this.canvas.querySelector(`[data-id="${fromId}"]`);
                        const element2 = this.canvas.querySelector(`[data-id="${toId}"]`);

                        // Remove connector indicators nếu không còn connector nào khác
                        if (element1) {
                            const remainingConnectors1 = this.canvas.querySelectorAll(`.connector-line[data-from-element="${fromId}"], .connector-line[data-to-element="${fromId}"]`);
                            if (remainingConnectors1.length <= 1) { // <= 1 vì connector hiện tại sắp bị xóa
                                element1.classList.remove('has-connector');
                            }
                        }

                        if (element2) {
                            const remainingConnectors2 = this.canvas.querySelectorAll(`.connector-line[data-from-element="${toId}"], .connector-line[data-to-element="${toId}"]`);
                            if (remainingConnectors2.length <= 1) {
                                element2.classList.remove('has-connector');
                            }
                        }
                    }
                }

                el.remove();
            });

            // Xóa tất cả connectors liên quan đến các elements đã xóa (không phải connector)
            elementIds.forEach(elementId => {
                const connectors = this.canvas.querySelectorAll(`.connector-line[data-from-element="${elementId}"], .connector-line[data-to-element="${elementId}"]`);
                connectors.forEach(connector => {
                    // Cũng cần update connected elements
                    const fromId = connector.dataset.fromElement;
                    const toId = connector.dataset.toElement;
                    const otherId = fromId === elementId ? toId : fromId;

                    if (otherId) {
                        const otherElement = this.canvas.querySelector(`[data-id="${otherId}"]`);
                        if (otherElement) {
                            const remainingConnectors = this.canvas.querySelectorAll(`.connector-line[data-from-element="${otherId}"], .connector-line[data-to-element="${otherId}"]`);
                            if (remainingConnectors.length <= 1) {
                                otherElement.classList.remove('has-connector');
                            }
                        }
                    }

                    connector.remove();
                });
            });

            this.selectElement(null);
            this.saveState();
        }
    }

    duplicateElement() {
        if (this.selectedElements.length !== 1) return;
        this.copySelectedElement();
        this.pasteElement();
    }

    changeZIndex(delta) {
        if (this.selectedElements.length === 0) return;
        this.selectedElements.forEach(el => {
            const currentZ = parseInt(el.style.zIndex) || 0;
            el.style.zIndex = Math.max(0, currentZ + delta);
        });
        this.updateProperties();
        this.saveState();
    }

    showConnectorTypeSelector() {
        console.log('🎯 showConnectorTypeSelector called'); // Debug

        if (this.selectedElements.length !== 1) {
            console.log('❌ No single element selected:', this.selectedElements.length);
            return;
        }

        if (!this.selectedElements[0].classList.contains('connector-line')) {
            console.log('❌ Selected element is not a connector line:', this.selectedElements[0].className);
            return;
        }

        const selector = document.getElementById('connectorTypeSelector');
        if (!selector) {
            console.log('❌ Selector element not found!');
            return;
        }

        const line = this.selectedElements[0];
        const currentType = line.dataset.connectorType || 'straight';
        const currentArrow = line.dataset.arrowType || 'forward';

        console.log('✅ Current connector:', currentType, currentArrow); // Debug

        // Update active buttons
        selector.querySelectorAll('[data-type]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.type === currentType);
        });

        selector.querySelectorAll('[data-arrow]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.arrow === currentArrow);
        });

        // Position selector near the connector
        const rect = line.getBoundingClientRect();
        const canvasRect = this.canvas.getBoundingClientRect();

        // Improve positioning - sử dụng canvas offset để tính toán chính xác
        const selectorLeft = Math.min(rect.left + 10, window.innerWidth - 320); // 320px là width của selector
        const selectorTop = Math.max(rect.bottom + 5, 50); // Tối thiểu 50px từ top

        selector.style.left = `${selectorLeft}px`;
        selector.style.top = `${selectorTop}px`;
        selector.style.display = 'block';
        selector.style.zIndex = '10000'; // Ensure it's on top

        console.log('✅ Selector positioned at:', selectorLeft, selectorTop); // Debug

        // Clear existing event listeners
        const oldHandleSelection = selector._handleSelection;
        const oldHandleClickOutside = selector._handleClickOutside;
        if (oldHandleSelection) selector.removeEventListener('click', oldHandleSelection);
        if (oldHandleClickOutside) document.removeEventListener('click', oldHandleClickOutside);

        // Bind click events
        const handleSelection = (e) => {
            console.log('🖱️ Selector clicked:', e.target.tagName, e.target.dataset); // Debug

            if (e.target.tagName === 'BUTTON') {
                if (e.target.dataset.type) {
                    // Line type selection
                    const newType = e.target.dataset.type;
                    const currentArrowType = line.dataset.arrowType || 'forward';
                    console.log('🔄 Changing line type to:', newType); // Debug
                    this.changeConnectorType(line, newType, currentArrowType);

                    // Update active state
                    selector.querySelectorAll('[data-type]').forEach(btn => {
                        btn.classList.toggle('active', btn.dataset.type === newType);
                    });
                } else if (e.target.dataset.arrow) {
                    // Arrow type selection
                    const newArrow = e.target.dataset.arrow;
                    const currentLineType = line.dataset.connectorType || 'straight';
                    console.log('🔄 Changing arrow type to:', newArrow); // Debug
                    this.changeConnectorType(line, currentLineType, newArrow);

                    // Update active state
                    selector.querySelectorAll('[data-arrow]').forEach(btn => {
                        btn.classList.toggle('active', btn.dataset.arrow === newArrow);
                    });
                }
            }
        };

        const handleClickOutside = (e) => {
            if (!selector.contains(e.target)) {
                console.log('🖱️ Clicked outside, hiding selector'); // Debug
                selector.style.display = 'none';
                document.removeEventListener('click', handleClickOutside);
                selector.removeEventListener('click', handleSelection);
                delete selector._handleSelection;
                delete selector._handleClickOutside;
            }
        };

        // Store references for cleanup
        selector._handleSelection = handleSelection;
        selector._handleClickOutside = handleClickOutside;

        selector.addEventListener('click', handleSelection);
        setTimeout(() => document.addEventListener('click', handleClickOutside), 100);

        console.log('✅ Event listeners attached'); // Debug
    }

    changeConnectorType(line, newType, newArrowType = null) {
        console.log('🔄 changeConnectorType called:', newType, newArrowType); // Debug

        const currentType = line.dataset.connectorType || 'straight';
        const currentArrowType = line.dataset.arrowType || 'forward';

        // Use current arrow type if not provided
        const arrowType = newArrowType || currentArrowType;

        // If both type and arrow are the same, no need to change
        if (currentType === newType && currentArrowType === arrowType) {
            console.log('⏭️ No changes needed');
            return;
        }

        const element1 = this.canvas.querySelector(`[data-id="${line.dataset.fromElement}"]`);
        const element2 = this.canvas.querySelector(`[data-id="${line.dataset.toElement}"]`);

        if (!element1 || !element2) {
            console.log('❌ Cannot find connected elements:', line.dataset.fromElement, line.dataset.toElement);
            return;
        }

        console.log('🔗 Found connected elements, updating...'); // Debug

        // Store current position and selection
        const wasSelected = line.classList.contains('selected');

        // IMPROVED: Update connector in place instead of removing and recreating
        // Update datasets
        line.dataset.connectorType = newType;
        line.dataset.arrowType = arrowType;

        // Update class names
        line.className = `element connector-line ${newType} arrow-${arrowType}`;
        if (wasSelected) line.classList.add('selected');

        // Clean up current content (but keep the line element)
        line.innerHTML = '';

        // Clean up control points only (not the line itself)
        if (line._controlPoints) {
            line._controlPoints.forEach(cp => cp.remove());
            delete line._controlPoints;
        }

        // Recreate connector with new type
        if (newType === 'straight') {
            this.createStraightConnector(line, element1, element2, arrowType);
        } else if (newType === 'curved') {
            this.createCurvedConnector(line, element1, element2, arrowType);
        } else if (newType === 'step') {
            this.createStepConnector(line, element1, element2, arrowType);
        } else if (newType === 'dashed') {
            this.createDashedConnector(line, element1, element2, arrowType);
        } else if (newType === 'dotted') {
            this.createDottedConnector(line, element1, element2, arrowType);
        } else if (newType === 'thick') {
            this.createThickConnector(line, element1, element2, arrowType);
        }

        // Restore selection if it was selected before
        if (wasSelected) {
            this.selectElement(line);
        }

        // Re-add update listeners
        this.addConnectorUpdateListeners(line, element1, element2);

        console.log('✅ Connector type changed successfully'); // Debug
        this.saveState();
    }

    setMode(mode) {
        this.mode = mode;
        document.querySelectorAll('.toolbar button').forEach(btn => btn.classList.remove('active'));
        document.getElementById(mode + 'Btn').classList.add('active');
        this.canvas.style.cursor = mode === 'text' ? 'crosshair' : 'default';
    }

    showContextMenu(e, element) {
        e.preventDefault();
        const targetElement = element.closest('.group-container') || element;
        if (!e.shiftKey && !this.selectedElements.includes(targetElement)) {
            this.selectElement(targetElement);
        }

        const menu = document.getElementById('contextMenu');
        const isConnector = this.selectedElements.length === 1 && this.selectedElements[0].classList.contains('connector-line');
        const canGroup = this.selectedElements.length > 1 && !isConnector;
        const canUngroup = this.selectedElements.length === 1 && this.selectedElements[0].classList.contains('group-container');
        const canConnect = this.selectedElements.length === 2 && !isConnector;

        menu.querySelector('[data-action="group"]').style.display = canGroup ? 'flex' : 'none';
        menu.querySelector('[data-action="ungroup"]').style.display = canUngroup ? 'flex' : 'none';
        menu.querySelector('[data-action="connectElements"]').style.display = canConnect ? 'flex' : 'none';
        menu.querySelector('[data-action="disconnectLine"]').style.display = isConnector ? 'flex' : 'none';
        menu.querySelector('[data-action="changeConnectorType"]').style.display = isConnector ? 'flex' : 'none';

        const dividers = menu.querySelectorAll('.context-menu-divider');
        dividers[0].style.display = (canGroup || canUngroup) ? 'block' : 'none';
        dividers[1].style.display = (canConnect || isConnector) ? 'block' : 'none';

        // Ẩn một số menu items cho connector
        if (isConnector) {
            menu.querySelector('[data-action="copy"]').style.display = 'none';
            menu.querySelector('[data-action="paste"]').style.display = 'none';
            menu.querySelector('[data-action="duplicate"]').style.display = 'none';
            menu.querySelector('[data-action="bringForward"]').style.display = 'none';
            menu.querySelector('[data-action="sendBackward"]').style.display = 'none';
        } else {
            menu.querySelector('[data-action="copy"]').style.display = 'flex';
            menu.querySelector('[data-action="paste"]').style.display = 'flex';
            menu.querySelector('[data-action="duplicate"]').style.display = 'flex';
            menu.querySelector('[data-action="bringForward"]').style.display = 'flex';
            menu.querySelector('[data-action="sendBackward"]').style.display = 'flex';
        }

        menu.style.display = 'block';
        menu.style.left = `${e.clientX}px`;
        menu.style.top = `${e.clientY}px`;
    }

    handleGlobalClick(e) {
        // Skip if we just finished dragging to avoid unwanted actions
        if (this.justFinishedDragging) {
            return;
        }

        // Reset text selection flag when clicking outside
        if (!e.target.hasAttribute('contenteditable')) {
            this.isTextSelecting = false;
        }

        if (e.target === this.canvasContainer || e.target === this.canvas) {
            if (this.mode === 'text' && e.target === this.canvas) {
                this.createTextElement(e);
            } else {
                this.selectElement(null);
            }
        }
        document.getElementById('contextMenu').style.display = 'none';
        document.getElementById('connectorTypeSelector').style.display = 'none';
    }

    rgbToHex(rgb) {
        if (!rgb || rgb.includes('rgba(0, 0, 0, 0)') || rgb === 'transparent') return '#ffffff';
        let a = rgb.split("(")[1].split(")")[0].split(",");
        if (a.length > 3) a = a.slice(0, 3);
        return "#" + a.map(x => {
            const hex = parseInt(x).toString(16);
            return hex.length == 1 ? "0" + hex : hex;
        }).join("");
    }

    toggleProperties() {
        const panel = document.getElementById('propertiesPanel');
        const container = document.getElementById('canvasContainer');
        const leftPanels = document.querySelector('.left-panels');

        panel.classList.toggle('open');
        container.classList.toggle('properties-open');

        // Tự động thu gọn/mở rộng left panel khi properties panel mở/đóng
        if (panel.classList.contains('open')) {
            leftPanels.classList.add('collapsed');
            container.classList.add('left-collapsed');
        } else {
            leftPanels.classList.remove('collapsed');
            container.classList.remove('left-collapsed');
        }

        // Cập nhật trạng thái nút toggle để đồng bộ với panel trái
        const toggleBtn = document.getElementById('toggleSlidesBtn');
        if (toggleBtn) {
            const isCollapsed = leftPanels.classList.contains('collapsed');
            toggleBtn.title = isCollapsed ? 'Mở rộng Slides' : 'Thu gọn Slides';
            toggleBtn.setAttribute('aria-pressed', (!isCollapsed).toString());
        }
    }

    toggleSlides() {
        const leftPanels = document.querySelector('.left-panels');
        const container = document.getElementById('canvasContainer');
        const toggleBtn = document.getElementById('toggleSlidesBtn');

        leftPanels.classList.toggle('collapsed');
        container.classList.toggle('left-collapsed');

        // Cập nhật icon nút dựa trên trạng thái
        const isCollapsed = leftPanels.classList.contains('collapsed');
        if (toggleBtn) {
            toggleBtn.title = isCollapsed ? 'Mở rộng Slides' : 'Thu gọn Slides';
            toggleBtn.setAttribute('aria-pressed', (!isCollapsed).toString());
        }
    }

    zoom(level) {
        this.zoomLevel = Math.max(0.1, Math.min(5, level));

        // Apply zoom với background persistence
        const currentBg = this.canvas.style.backgroundColor || 'white';

        this.canvas.style.cssText = `
        position: relative !important;
        width: 1920px !important;
        height: 1080px !important;
        background: ${currentBg} !important;
        background-color: ${currentBg} !important;
        margin: 0 auto !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1) !important;
        border-radius: 8px !important;
        transform-origin: top left !important;
        transition: transform 0.3s ease !important;
        overflow: hidden !important;
        transform: scale(${this.zoomLevel}) !important;
    `;

        this.updateBackgroundWrapperZoom(); // For compatibility
        document.getElementById('zoomLevel').textContent = `${Math.round(this.zoomLevel * 100)}%`;

        console.log('🔍 Zoom applied with background preserved:', this.zoomLevel, currentBg);
    }

    fitToScreen() {
        const scale = Math.min(
            (this.canvasContainer.offsetWidth - 60) / this.canvas.offsetWidth,
            (this.canvasContainer.offsetHeight - 60) / this.canvas.offsetHeight
        );
        this.zoom(scale);
        document.getElementById('zoomLevel').textContent = 'Fit';

        // Smooth zoom animation
        this.canvas.style.transition = 'transform 0.3s ease-in-out';
        setTimeout(() => {
            this.canvas.style.transition = '';
        }, 300);
    }

    saveState() {
        this.saveCurrentSlide();
        if (this.historyIndex < this.history.length - 1) this.history.splice(this.historyIndex + 1);

        // Only save slides content, NOT currentSlideIndex
        // This prevents undo from changing which slide you're viewing
        const currentState = {
            slides: JSON.parse(JSON.stringify(this.slides))
        };

        const lastState = this.history[this.historyIndex];
        if (!lastState || JSON.stringify(lastState) !== JSON.stringify(currentState)) {
            this.history.push(currentState);
            this.historyIndex++;

            // Show "Saving..." indicator
            this.showSavingIndicator();

            // Auto-save to database (debounced 1 second)
            if (this.currentProjectId) {
                clearTimeout(this._saveTimeout);
                this._saveTimeout = setTimeout(() => {
                    this.saveToDatabase();
                }, 1000);
            } else {
                // Not loaded from DB, just show saved
                this.showSaveIndicator();
            }

            this.updateUndoRedoButtons();
        }
    }

    showSavingIndicator() {
        const indicator = document.getElementById('saveIndicator');
        if (!indicator) return;

        indicator.style.display = 'inline-block';
        indicator.textContent = '💾 Saving...';
        indicator.style.color = '#f59e0b';
    }

    showSaveIndicator() {
        const indicator = document.getElementById('saveIndicator');
        if (!indicator) return;

        indicator.style.display = 'inline-block';
        indicator.textContent = '✓ Saved';
        indicator.style.color = '#10b981';

        // Don't hide - keep showing saved status
    }

    async saveToDatabase() {
        if (!this.currentProjectId || this.slideIds.length === 0) return;

        const token = localStorage.getItem('access_token');
        if (!token) return;

        try {
            const apiUrl = window.config?.BACKEND_URL || 'http://localhost:3000';

            // Save current slide being edited FIRST
            if (this.slides.length > 0 && this.currentSlideIndex >= 0) {
                const currentSlide = this.slides[this.currentSlideIndex];
                currentSlide.content = this.canvas.innerHTML;
                console.log(`💾 Saving current slide ${this.currentSlideIndex}, content length: ${currentSlide.content.length}`);
            }

            for (let i = 0; i < this.slides.length; i++) {
                const slide = this.slides[i];
                const slideId = this.slideIds[i];

                if (!slideId) {
                    console.warn(`No slide ID for slide ${i}, skipping`);
                    continue;
                }

                // Rebuild proper HTML structure matching the DB format
                // slide.content contains: <style>...</style> + absolute positioned elements
                const bgColor = slide.backgroundColor || 'white';
                const fullHTML = `<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Slide ${i + 1}</title>
<style>
body {
    margin: 0;
    padding: 0;
    width: 1920px;
    height: 1080px;
    overflow: hidden;
    font-family: 'Arial', sans-serif;
}
.slide-container {
    width: 1920px;
    height: 1080px;
    position: relative;
    background: ${bgColor};
    overflow: hidden;
}
.content-wrapper {
    width: 100%;
    height: 100%;
    position: relative;
}
</style>
</head>
<body>
<div class="slide-container">
<div class="content-wrapper">
${slide.content}
</div>
</div>
</body>
</html>`;

                console.log(`💾 Saving slide ${i} (ID: ${slideId}), content length: ${slide.content.length}, bg: ${bgColor}`);

                const response = await fetch(`${apiUrl}/api/slides/${slideId}`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        html_content: fullHTML,
                        title: slide.name || `Slide ${i + 1}`
                    })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Failed to save slide ${i + 1}: ${errorText}`);
                }
            }

            console.log('✅ Saved to database');
            this.showSaveIndicator();

        } catch (error) {
            console.error('❌ Save error:', error);
            const indicator = document.getElementById('saveIndicator');
            if (indicator) {
                indicator.style.display = 'inline-block';
                indicator.textContent = '❌ Save failed';
                indicator.style.color = '#ef4444';
            }
        }
    }

    updateUndoRedoButtons() {
        const undoBtn = document.getElementById('undoBtn');
        const redoBtn = document.getElementById('redoBtn');

        if (undoBtn) {
            if (this.historyIndex > 0) {
                undoBtn.disabled = false;
                undoBtn.style.opacity = '1';
                undoBtn.style.cursor = 'pointer';
            } else {
                undoBtn.disabled = true;
                undoBtn.style.opacity = '0.4';
                undoBtn.style.cursor = 'not-allowed';
            }
        }

        if (redoBtn) {
            if (this.historyIndex < this.history.length - 1) {
                redoBtn.disabled = false;
                redoBtn.style.opacity = '1';
                redoBtn.style.cursor = 'pointer';
            } else {
                redoBtn.disabled = true;
                redoBtn.style.opacity = '0.4';
                redoBtn.style.cursor = 'not-allowed';
            }
        }
    }

    loadStateFromHistory() {
        const state = this.history[this.historyIndex];
        if (state) {
            this.slides = JSON.parse(JSON.stringify(state.slides));
            // DON'T restore currentSlideIndex - stay on current slide
            // Only reload the current slide content
            this.loadSlide(this.currentSlideIndex);
            this.renderSlidesList();
            this.selectElement(null);
        }
        this.updateUndoRedoButtons();
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.loadStateFromHistory();
        }
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.loadStateFromHistory();
        }
    }

    importSlides(e) {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;

        let importedCount = 0;
        const totalFiles = files.length;


        files.forEach((file) => {
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const content = event.target.result;
                    const iframe = document.createElement('iframe');
                    iframe.style.display = 'none';
                    document.body.appendChild(iframe);
                    iframe.onload = () => {
                        const sourceDoc = iframe.contentDocument;
                        const sourceWindow = iframe.contentWindow;
                        // Thêm style mặc định
                        const style = sourceDoc.createElement('style');
                        style.textContent = `body { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }`;
                        sourceDoc.head.appendChild(style);
                        const sourceBody = sourceDoc.body;
                        let contentSource = sourceBody.querySelector('.content-wrapper') || sourceBody;

                        if (contentSource) {
                            const slide = {
                                id: this.slideIdCounter++,
                                name: file.name.replace('.html', ''),
                                content: '',
                                backgroundColor: 'white',
                                zIndexCounter: 1
                            };

                            const tempCanvas = document.createElement('div');
                            tempCanvas.style.position = 'relative';
                            tempCanvas.style.width = '1920px';
                            tempCanvas.style.height = '1080px';

                            // Copy tất cả <style> từ sourceDoc sang tempCanvas để giữ nguyên style list
                            sourceDoc.querySelectorAll('style').forEach(styleEl => {
                                tempCanvas.appendChild(styleEl.cloneNode(true));
                            });

                            sourceBody.querySelectorAll('svg > defs').forEach(defs => {
                                const svgWrapper = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                                svgWrapper.setAttribute('width', '0');
                                svgWrapper.setAttribute('height', '0');
                                svgWrapper.appendChild(defs.cloneNode(true));
                                tempCanvas.appendChild(svgWrapper);
                            });

                            slide.backgroundColor = this.findSolidBackgroundColor(contentSource, sourceWindow);
                            console.log('🎨 Import: slide.backgroundColor =', slide.backgroundColor);
                            this.applyCanvasBackground(contentSource, sourceWindow, tempCanvas);

                            Array.from(contentSource.children).forEach(child => {
                                if (child.tagName.toLowerCase() === 'svg' && child.querySelector('defs')) return;
                                this.processAndAppendImportedNode(child, tempCanvas, sourceWindow);
                            });

                            slide.content = tempCanvas.innerHTML;
                            slide.zIndexCounter = this.zIndexCounter;
                            this.slides.push(slide);

                            importedCount++;
                            if (importedCount === totalFiles) {
                                this.renderSlidesList();
                                this.switchToSlide(this.slides.length - totalFiles);
                                console.log('🎯 Switched to newly imported slide:', this.slides.length - totalFiles);
                            }
                        } else {
                            throw new Error("No valid content found.");
                        }
                        document.body.removeChild(iframe);
                    };
                    const doc = iframe.contentDocument;
                    doc.open(); doc.write(content); doc.close();
                } catch (error) {
                    alert(`Error importing slide ${file.name}: ${error.message}`);
                    console.error("Import failed:", error);
                    importedCount++;
                    if (importedCount === totalFiles) {
                        this.renderSlidesList();
                    }
                }
            };
            reader.readAsText(file);
        });

        e.target.value = '';
    }


    findSolidBackgroundColor(startNode, sourceWindow) {
        console.log('🔍 findSolidBackgroundColor called with:', sourceWindow?.location?.href || 'no sourceWindow');

        // Try multiple approaches to get the window/document
        let doc = sourceWindow?.document || startNode?.ownerDocument || document;
        let win = sourceWindow || startNode?.defaultView || window;

        console.log('🔍 Using document:', doc?.title || 'unknown', 'body bgColor:',
            win?.getComputedStyle?.(doc?.body)?.backgroundColor || 'none');

        // METHOD 1: Parse CSS text directly từ document để tìm body background
        if (doc && doc.head) {
            const styleElements = doc.querySelectorAll('style');
            for (let style of styleElements) {
                const cssText = style.textContent || style.innerHTML;

                // Regex để tìm body background-color
                const bodyBgMatch = cssText.match(/body[^{]*\{[^}]*background-color:\s*([^;]+);/i);
                if (bodyBgMatch) {
                    const color = bodyBgMatch[1].trim();
                    console.log('🎨 Found BODY background from CSS:', color);
                    return color;
                }

                // Regex để tìm body background (general)
                const bodyBgGeneralMatch = cssText.match(/body[^{]*\{[^}]*background:\s*([^;]+);/i);
                if (bodyBgGeneralMatch) {
                    const bgValue = bodyBgGeneralMatch[1].trim();
                    // Extract chỉ color part nếu có
                    const colorMatch = bgValue.match(/rgb\([^)]+\)|#[a-fA-F0-9]{3,6}|[a-zA-Z]+/);
                    if (colorMatch) {
                        console.log('🎨 Found BODY background (general) from CSS:', colorMatch[0]);
                        return colorMatch[0];
                    }
                }
            }
        }

        // METHOD 2: getComputedStyle approach
        const htmlElement = doc.documentElement;
        const bodyElement = doc.body;

        // Kiểm tra HTML element trước
        if (htmlElement && win.getComputedStyle) {
            const htmlStyle = win.getComputedStyle(htmlElement);
            const htmlBgColor = htmlStyle.backgroundColor;
            if (htmlBgColor && htmlBgColor !== 'rgba(0, 0, 0, 0)' && htmlBgColor !== 'transparent') {
                console.log('🎨 Found HTML background:', htmlBgColor);
                return htmlBgColor;
            }
        }

        // Sau đó kiểm tra body element  
        if (bodyElement && win.getComputedStyle) {
            const bodyStyle = win.getComputedStyle(bodyElement);
            const bodyBgColor = bodyStyle.backgroundColor;
            if (bodyBgColor && bodyBgColor !== 'rgba(0, 0, 0, 0)' && bodyBgColor !== 'transparent') {
                console.log('🎨 Found BODY background:', bodyBgColor);
                return bodyBgColor;
            }
        }

        // METHOD 3: Check iframe content có thể có background trong HTML
        if (doc && doc.documentElement) {
            const htmlContent = doc.documentElement.outerHTML;
            const bodyBgMatch = htmlContent.match(/body[^>]*style="[^"]*background[^:]*:\s*([^;"]+)/i);
            if (bodyBgMatch) {
                console.log('🎨 Found BODY background from HTML:', bodyBgMatch[1]);
                return bodyBgMatch[1].trim();
            }
        }

        console.log('🎨 No background found, using white');
        return 'white';
    }

    applyCanvasBackground(sourceElement, sourceWindow, targetCanvas) {
        targetCanvas.style.backgroundColor = this.findSolidBackgroundColor(sourceElement, sourceWindow);
        const beforeStyle = sourceWindow.getComputedStyle(sourceElement, '::before');
        if (beforeStyle.content !== 'none' && beforeStyle.backgroundImage !== 'none') {
            const pseudoBgLayer = document.createElement('div');
            pseudoBgLayer.className = 'background-pseudo-element';
            const propsToCopy = ['position', 'top', 'left', 'width', 'height', 'background-image', 'background-size', 'background-repeat', 'background-position', 'z-index', 'opacity', 'transform'];
            propsToCopy.forEach(prop => pseudoBgLayer.style[prop] = beforeStyle[prop]);
            targetCanvas.prepend(pseudoBgLayer);
        }
    }

    _determineElementType(node) {
        const tag = node.tagName.toUpperCase();
        const textTags = ['P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'BLOCKQUOTE', 'UL', 'OL', 'LI', 'PRE'];
        if (['IMG', 'PICTURE'].includes(tag)) return 'image';
        if (['VIDEO'].includes(tag)) return 'video';
        if (textTags.includes(tag)) return 'text';

        if (tag === 'DIV') {
            const hasBlockChildren = Array.from(node.children).some(child => {
                const style = window.getComputedStyle(child);
                return style.display === 'block';
            });
            if (!hasBlockChildren && node.textContent.trim().length > 0) {
                return 'text';
            }
        }
        return 'shape';
    }

    processAndAppendImportedNode(sourceNode, targetParent, sourceWindow) {
        if (['SCRIPT', 'STYLE', 'LINK', 'META', 'TITLE'].includes(sourceNode.tagName.toUpperCase())) return;
        if (sourceNode.nodeType !== Node.ELEMENT_NODE) return;

        const newEl = sourceNode.cloneNode(true);

        newEl.classList.add('element');
        this.transferComputedStyles(sourceNode, newEl, sourceWindow);

        const type = this._determineElementType(sourceNode);
        newEl.dataset.type = type;

        if (type === 'text') {
            newEl.setAttribute('contenteditable', 'true');
        } else {
            newEl.removeAttribute('contenteditable');
        }

        newEl.style.zIndex = this.zIndexCounter++;
        targetParent.appendChild(newEl);

        // Đảm bảo SVG elements được xử lý đúng cách
        if (sourceNode.tagName && sourceNode.tagName.toLowerCase() === 'svg') {
            // Copy tất cả SVG content, bao gồm defs và clipPath
            newEl.innerHTML = sourceNode.innerHTML;

            // Nếu SVG không visible, đặt width=0 height=0
            if (sourceNode.style.width === '0' || sourceNode.style.height === '0') {
                newEl.style.width = '0';
                newEl.style.height = '0';
                newEl.style.position = 'absolute';
                newEl.style.top = '0';
                newEl.style.left = '0';
            }
        }

        // Xử lý elements có clip-path reference đến SVG
        const clipPathValue = sourceWindow.getComputedStyle(sourceNode).clipPath;
        if (clipPathValue && clipPathValue.includes('url(')) {
            // Đảm bảo SVG được copy vào slide
            const clipPathId = clipPathValue.match(/url\(["']?#([^)"']+)["']?\)/);
            if (clipPathId && clipPathId[1]) {
                const referencedSVG = sourceWindow.document.querySelector(`svg #${clipPathId[1]}`);
                if (referencedSVG) {
                    let svgContainer = targetParent.querySelector('svg');
                    if (!svgContainer) {
                        svgContainer = document.createElement('svg');
                        svgContainer.style.width = '0';
                        svgContainer.style.height = '0';
                        svgContainer.style.position = 'absolute';
                        const defs = document.createElement('defs');
                        svgContainer.appendChild(defs);
                        targetParent.insertBefore(svgContainer, targetParent.firstChild);
                    }

                    const existingClipPath = svgContainer.querySelector(`#${clipPathId[1]}`);
                    if (!existingClipPath) {
                        const clonedClipPath = referencedSVG.parentElement.cloneNode(true);
                        svgContainer.querySelector('defs').appendChild(clonedClipPath);
                    }
                }
            }
        }
    }

    transferComputedStyles(sourceNode, destNode, sourceWindow) {
        const computedStyle = sourceWindow.getComputedStyle(sourceNode);
        const stylePropsToCopy = [
            'position', 'left', 'top', 'width', 'height', 'color', 'font-family', 'font-size', 'font-weight', 'font-style', 'line-height',
            'text-align', 'text-decoration', 'text-transform', 'letter-spacing', 'word-spacing', 'white-space', 'writing-mode', 'text-orientation',
            'padding', 'margin', 'border', 'border-radius', 'box-sizing',
            'box-shadow', 'opacity', 'display', 'flex-direction', 'justify-content', 'align-items', 'gap',
            'background-color', 'background-image', 'background-repeat', 'background-size', 'background-position', 'background-clip',
            'fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin', 'clip-path', 'transform', 'transform-origin',
            'object-fit', 'object-position', 'overflow'
        ];

        stylePropsToCopy.forEach(prop => {
            const value = computedStyle.getPropertyValue(prop);
            if (value && value !== 'none' && value !== 'auto' && value !== 'initial') {
                // Đặc biệt xử lý clip-path để tránh double quotes
                if (prop === 'clip-path' && value !== 'none') {
                    // Loại bỏ dấu ngoặc kép thừa trong URL nếu có
                    let cleanValue = value.replace(/url\("([^"]+)"\)/g, 'url($1)');

                    destNode.style.setProperty('-webkit-clip-path', cleanValue);
                    destNode.style.setProperty('clip-path', cleanValue);

                    // Nếu clip-path sử dụng URL (SVG), thêm fallback polygon
                    if (cleanValue.includes('url(')) {
                        // Thêm class để xử lý CSS fallback
                        destNode.classList.add('has-clip-path-url');

                        // Nếu là angled-multi-divider, thêm fallback polygon
                        if (cleanValue.includes('angled-multi-divider')) {
                            const fallbackClipPath = 'polygon(15% 0%, 100% 0%, 100% 100%, 0% 100%)';
                            destNode.style.setProperty('--clip-path-fallback', fallbackClipPath);
                        }
                    }
                } else {
                    destNode.style.setProperty(prop, value);
                }
            }
        });

        // Chuẩn hóa đường dẫn ảnh tương đối → dùng API ảnh
        if (destNode.tagName && destNode.tagName.toLowerCase() === 'img') {
            const src = destNode.getAttribute('src') || '';
            if (src && !/^https?:\/\//i.test(src) && !/^\//.test(src) && !/^data:/i.test(src)) {
                destNode.setAttribute('src', `/api/images/${src}`);
            }
        } else if (destNode.querySelectorAll) {
            destNode.querySelectorAll('img').forEach(img => {
                const src = img.getAttribute('src') || '';
                if (src && !/^https?:\/\//i.test(src) && !/^\//.test(src) && !/^data:/i.test(src)) {
                    img.setAttribute('src', `/api/images/${src}`);
                }
            });
        }

        // Đảm bảo SVG elements và clipPath được copy
        if (sourceNode.tagName && sourceNode.tagName.toLowerCase() === 'svg') {
            destNode.innerHTML = sourceNode.innerHTML;
        }
    }



    // Helper method to get slide content as clean HTML for Puppeteer
    getSlideHTMLContent(slide) {
        // Create a temporary container with slide dimensions - Zero margin/padding
        const tempContainer = document.createElement('div');
        tempContainer.className = 'slide-container';
        tempContainer.style.cssText = `
        position: relative;
        width: 1920px;
        height: 1080px;
        background: ${slide.backgroundColor || 'white'};
        overflow: hidden;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    `;

        // Parse elements from slide.content HTML instead of slide.elements array
        if (slide.content) {
            // Create temporary div to parse HTML content
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = slide.content;

            // Get all elements and clone them properly
            const elements = tempDiv.querySelectorAll('.element');
            console.log(`Found ${elements.length} elements in slide content`);

            elements.forEach(originalElement => {
                // Clone the element completely
                const elementDiv = originalElement.cloneNode(true);

                // Clean up any editor-specific classes/attributes
                elementDiv.classList.remove('selected', 'editing');
                elementDiv.removeAttribute('contenteditable');
                elementDiv.style.outline = 'none';
                elementDiv.style.border = 'none';

                // Ensure absolute positioning without extra margins
                if (!elementDiv.style.position) {
                    elementDiv.style.position = 'absolute';
                }

                // Remove resize handles if any
                const resizeHandles = elementDiv.querySelectorAll('.resize-handle, .rotation-handle');
                resizeHandles.forEach(handle => handle.remove());

                tempContainer.appendChild(elementDiv);
            });
        } else {
            // If no content, add a placeholder
            console.warn('Slide has no content');
            const placeholderDiv = document.createElement('div');
            placeholderDiv.style.cssText = `
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            color: #999;
            font-size: 24px;
            text-align: center;
        `;
            placeholderDiv.textContent = 'Empty Slide';
            tempContainer.appendChild(placeholderDiv);
        }

        return tempContainer.outerHTML;
    }

    // Template drag & drop methods
    handleTemplateDragStart(e) {
        const templateType = e.target.closest('.template-item').dataset.template;
        e.dataTransfer.setData('text/plain', templateType);
        e.dataTransfer.effectAllowed = 'copy';

        // Add visual feedback
        e.target.style.opacity = '0.5';
    }

    handleTemplateDragEnd(e) {
        e.target.style.opacity = '1';
    }

    // Legacy template handlers (replaced by unified handlers)
    handleCanvasDragOver(e) {
        // This is now handled by handleUnifiedDragOver
        return this.handleUnifiedDragOver(e);
    }

    handleCanvasDrop(e) {
        // This is now handled by handleUnifiedDrop  
        return this.handleUnifiedDrop(e);
    }

    createSlideFromTemplate(templateType) {
        let slideContent = '';
        let backgroundColor = 'white';

        switch (templateType) {
            case 'title-slide':
                backgroundColor = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                slideContent = `
                <div class="element" data-type="text" style="left: 400px; top: 400px; width: 1120px; height: auto; font-size: 72px; font-weight: 800; color: white; text-align: center; z-index: 2;" contenteditable="true">Your Presentation Title</div>
                <div class="element" data-type="text" style="left: 400px; top: 520px; width: 1120px; height: auto; font-size: 36px; font-weight: 400; color: rgba(255,255,255,0.9); text-align: center; z-index: 3;" contenteditable="true">Subtitle or description goes here</div>
            `;
                break;

            case 'content-slide':
                slideContent = `
                <div class="element" data-type="text" style="left: 100px; top: 100px; width: 800px; height: auto; font-size: 48px; font-weight: 700; color: #2d3748; z-index: 2;" contenteditable="true">Content Title</div>
                <div class="element" data-type="text" style="left: 100px; top: 200px; width: 1720px; height: auto; font-size: 24px; color: #4a5568; z-index: 3;" contenteditable="true">• First point or bullet item
• Second important point
• Third key message
• Additional details</div>
            `;
                break;

            case 'two-column':
                slideContent = `
                <div class="element" data-type="text" style="left: 100px; top: 100px; width: 800px; height: auto; font-size: 36px; font-weight: 700; color: #2d3748; z-index: 2;" contenteditable="true">Left Column</div>
                <div class="element" data-type="text" style="left: 100px; top: 200px; width: 800px; height: auto; font-size: 18px; color: #4a5568; z-index: 3;" contenteditable="true">Content for the left side goes here. Add your text, bullet points, or any other information.</div>
                <div class="element" data-type="text" style="left: 1020px; top: 100px; width: 800px; height: auto; font-size: 36px; font-weight: 700; color: #2d3748; z-index: 4;" contenteditable="true">Right Column</div>
                <div class="element" data-type="text" style="left: 1020px; top: 200px; width: 800px; height: auto; font-size: 18px; color: #4a5568; z-index: 5;" contenteditable="true">Content for the right side goes here. You can balance your information across both columns.</div>
            `;
                break;

            case 'image-content':
                slideContent = `
                <div class="element" data-type="shape" style="left: 100px; top: 200px; width: 600px; height: 400px; background-color: #f7fafc; border: 2px dashed #cbd5e0; z-index: 2; display: flex; align-items: center; justify-content: center; font-size: 48px; color: #a0aec0;">🖼️</div>
                <div class="element" data-type="text" style="left: 800px; top: 100px; width: 1020px; height: auto; font-size: 48px; font-weight: 700; color: #2d3748; z-index: 3;" contenteditable="true">Image & Content</div>
                <div class="element" data-type="text" style="left: 800px; top: 220px; width: 1020px; height: auto; font-size: 24px; color: #4a5568; line-height: 1.6; z-index: 4;" contenteditable="true">Add your image to the left and your content here. This layout works great for:

• Product descriptions
• Case studies
• Before/after comparisons
• Visual explanations</div>
            `;
                break;

            case 'quote-slide':
                backgroundColor = 'linear-gradient(45deg, #667eea, #764ba2)';
                slideContent = `
                <div class="element" data-type="text" style="left: 200px; top: 300px; width: 1520px; height: auto; font-size: 64px; font-weight: 400; color: white; text-align: center; font-style: italic; z-index: 2;" contenteditable="true">"Your inspiring quote goes here"</div>
                <div class="element" data-type="text" style="left: 200px; top: 500px; width: 1520px; height: auto; font-size: 32px; font-weight: 500; color: rgba(255,255,255,0.8); text-align: center; z-index: 3;" contenteditable="true">— Author Name</div>
            `;
                break;

            case 'thank-you':
                backgroundColor = 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)';
                slideContent = `
                <div class="element" data-type="text" style="left: 400px; top: 440px; width: 1120px; height: auto; font-size: 96px; font-weight: 800; color: white; text-align: center; z-index: 2;" contenteditable="true">Thank You</div>
                <div class="element" data-type="text" style="left: 400px; top: 580px; width: 1120px; height: auto; font-size: 28px; font-weight: 400; color: rgba(255,255,255,0.9); text-align: center; z-index: 3;" contenteditable="true">Questions & Discussion</div>
            `;
                break;

            case 'blank-slide':
                slideContent = `
                <div class="element" data-type="text" style="left: 400px; top: 500px; width: 1120px; height: auto; font-size: 48px; font-weight: 400; color: #a0aec0; text-align: center; z-index: 2;" contenteditable="true">Click to add content</div>
            `;
                break;
        }

        // Create new slide with template content
        const newSlide = {
            id: `slide_${this.slideIdCounter++}`,
            name: `${templateType.charAt(0).toUpperCase() + templateType.slice(1).replace('-', ' ')}`,
            content: slideContent,
            backgroundColor: backgroundColor,
            elements: []
        };

        // Add slide and switch to it
        this.slides.push(newSlide);
        this.currentSlideIndex = this.slides.length - 1;
        this.loadSlide(this.currentSlideIndex);
        this.renderSlidesList();
        this.saveState();

        // Show success message
        this.showSuccessMessage(`✨ Created new slide: ${newSlide.name}`);
    }

    // Load slides từ URL params hoặc localStorage
    async loadSlidesFromURLOrStorage() {
        const urlParams = new URLSearchParams(window.location.search);
        const projectName = urlParams.get('project');
        const source = urlParams.get('source');

        // Nếu có project name trong URL, load từ backend API
        if (projectName) {
            console.log('Loading slides for project:', projectName);
            await this.loadSlidesFromAPI(projectName, source);
        } else {
            // Ngược lại, load từ localStorage như cũ
            const slidesLoaded = this.loadSlidesFromStorage();
            if (!slidesLoaded) {
                console.log('No slides to load, using default first slide');
            }
        }
    }

    // Load slides từ backend API
    async loadSlidesFromAPI(projectName, source) {
        try {
            const response = await fetch(`${config.BACKEND_URL}/api/slides/${projectName}`);

            if (!response.ok) {
                throw new Error(`Failed to load slides: ${response.status}`);
            }

            const data = await response.json();
            console.log('Loaded slides from API:', data);

            if (data.slides && data.slides.length > 0) {
                // Clear slides hiện tại
                this.slides = [];
                this.currentSlideIndex = 0;
                this.slideIdCounter = 1;

                // Convert slides từ API
                data.slides.forEach((slideData, index) => {
                    const slide = {
                        id: this.slideIdCounter++,
                        name: slideData.title || `Slide ${index + 1}`,
                        content: this.convertApiSlideToEditorFormat(slideData.content, slideData.metadata),
                        backgroundColor: slideData.backgroundColor || this.extractBackgroundColor(slideData.content) || 'white',
                        zIndexCounter: 1
                    };
                    this.slides.push(slide);
                });

                // Load slide đầu tiên
                if (this.slides.length > 0) {
                    this.loadSlide(0);
                    this.renderSlidesList();
                    this.showSuccessMessage(`✨ Đã load ${this.slides.length} slides từ project ${projectName}`);

                    // Lưu trạng thái ban đầu
                    setTimeout(() => {
                        this.saveOriginalState();
                    }, 100);
                }
            }
        } catch (error) {
            console.error('Error loading slides from API:', error);
            this.showErrorMessage(`Lỗi khi load slides: ${error.message}`);
        }
    }

    loadSlidesFromStorage() {
        // Luôn cố gắng nạp nếu có dữ liệu trong localStorage (không phụ thuộc source)
        const urlParams = new URLSearchParams(window.location.search);
        const source = urlParams.get('source');

        // Lấy dữ liệu slides từ localStorage
        const storedSlides = localStorage.getItem('generatedSlides');
        const slidesSource = localStorage.getItem('slidesSource');
        const originalFileName = localStorage.getItem('originalFileName');

        if (storedSlides) {
            try {
                const slidesData = JSON.parse(storedSlides);
                console.log('Loading slides from storage:', slidesData);

                // Clear slides hiện tại
                this.slides = [];
                this.currentSlideIndex = 0;
                this.slideIdCounter = 1;

                // Convert dữ liệu slides từ API thành format của editor
                slidesData.forEach((slideData, index) => {
                    const slide = {
                        id: this.slideIdCounter++,
                        name: slideData.title || `Slide ${index + 1}`,
                        content: this.convertApiSlideToEditorFormat(slideData.content, slideData.metadata),
                        backgroundColor: slideData.backgroundColor || this.extractBackgroundColor(slideData.content) || 'white',
                        zIndexCounter: 1
                    };
                    this.slides.push(slide);
                });

                // Load slide đầu tiên
                if (this.slides.length > 0) {
                    this.loadSlide(0);
                    this.renderSlidesList();

                    // Hiển thị thông báo thành công
                    this.showSuccessMessage(`✨ Đã load ${this.slides.length} slides từ ${originalFileName || 'file'}`);

                    // Xóa dữ liệu khỏi localStorage sau khi load
                    localStorage.removeItem('generatedSlides');
                    localStorage.removeItem('slidesSource');
                    localStorage.removeItem('originalFileName');

                    // Lưu trạng thái ban đầu cho chức năng reset
                    setTimeout(() => {
                        this.saveOriginalState();
                    }, 100);

                    return true; // Đã load thành công
                }
            } catch (error) {
                console.error('Error loading slides from storage:', error);
                this.showErrorMessage('Lỗi khi load slides từ storage');
            }
        }
        return false; // Không có slides để load
    }

    // Helper function để convert HTML từ API thành format của editor
    convertApiSlideToEditorFormat(htmlContent, metadata = null) {
        try {
            // Dựng iframe như Import Slides để dùng lại processAndAppendImportedNode
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            document.body.appendChild(iframe);

            const doc = iframe.contentDocument;
            doc.open();
            doc.write(htmlContent);
            doc.close();

            const sourceDoc = iframe.contentDocument;
            const sourceWindow = iframe.contentWindow;
            const sourceBody = sourceDoc.body;
            const contentSource = sourceBody.querySelector('.content-wrapper') || sourceBody;

            const tempCanvas = document.createElement('div');
            tempCanvas.style.position = 'relative';
            tempCanvas.style.width = '1920px';
            tempCanvas.style.height = '1080px';

            // Copy tất cả <style>
            sourceDoc.querySelectorAll('style').forEach(styleEl => {
                tempCanvas.appendChild(styleEl.cloneNode(true));
            });

            // Copy SVG defs
            sourceBody.querySelectorAll('svg > defs').forEach(defs => {
                const svgWrapper = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                svgWrapper.setAttribute('width', '0');
                svgWrapper.setAttribute('height', '0');
                svgWrapper.appendChild(defs.cloneNode(true));
                tempCanvas.appendChild(svgWrapper);
            });

            // Áp background
            const bg = this.findSolidBackgroundColor(contentSource, sourceWindow);
            this.applyCanvasBackground(contentSource, sourceWindow, tempCanvas);
            tempCanvas.style.backgroundColor = bg || 'white';

            // Duyệt child và tách element
            Array.from(contentSource.children).forEach(child => {
                if (child.tagName && child.tagName.toLowerCase() === 'svg' && child.querySelector('defs')) return;
                this.processAndAppendImportedNode(child, tempCanvas, sourceWindow);
            });

            // Dọn dẹp iframe
            document.body.removeChild(iframe);

            return tempCanvas.innerHTML;
        } catch (error) {
            console.error('Error converting API slide (iframe pipeline):', error);
            // Fallback cũ
            try {
                const wrapperElement = document.createElement('div');
                wrapperElement.className = 'element html-slide-content';
                wrapperElement.dataset.type = 'html-slide';
                wrapperElement.innerHTML = htmlContent;
                wrapperElement.style.cssText = `position:absolute;left:10px;top:10px;width:calc(100% - 20px);height:calc(100% - 20px);overflow:hidden;z-index:1;`;
                return wrapperElement.outerHTML;
            } catch (_) {
                return `<div class="element" style="position:absolute;left:50px;top:50px;width:500px;height:200px;padding:20px;background:#f8f9fa;border:1px solid #dee2e6;border-radius:8px;">Không thể hiển thị nội dung slide.</div>`;
            }
        }
    }

    // Convert từ metadata elements (cải thiện hơn HTML parsing)
    convertFromMetadataElements(metadataElements) {
        const editorElements = [];

        metadataElements.forEach((elementMeta, index) => {
            try {
                const editorElement = document.createElement('div');
                editorElement.className = 'element';
                editorElement.dataset.type = elementMeta.type || 'text';

                // Set content based on type
                if (elementMeta.type === 'image' && elementMeta.src) {
                    editorElement.innerHTML = `<img src="${elementMeta.src}" style="width: 100%; height: auto;">`;
                } else if (elementMeta.text) {
                    editorElement.innerHTML = elementMeta.text;
                }

                // Parse styles từ metadata
                const styles = this.parseStyleString(elementMeta.style || '');

                // Set default values nếu chưa có
                const defaultStyles = {
                    position: 'absolute',
                    left: styles.left || (100 + index * 50) + 'px',
                    top: styles.top || (100 + index * 100) + 'px',
                    width: styles.width || '400px',
                    height: styles.height || 'auto',
                    fontSize: styles.fontSize || '16px',
                    color: styles.color || '#000000',
                    backgroundColor: styles.backgroundColor || 'transparent',
                    textAlign: styles.textAlign || 'left',
                    fontFamily: styles.fontFamily || 'Arial, sans-serif',
                    zIndex: index + 1
                };

                Object.assign(editorElement.style, defaultStyles);

                // Thêm contenteditable cho text elements
                if (elementMeta.type === 'text' || !elementMeta.type) {
                    editorElement.contentEditable = 'true';
                }

                editorElements.push(editorElement.outerHTML);
            } catch (error) {
                console.error('Error converting metadata element:', error);
            }
        });

        return editorElements.join('\n');
    }

    // Helper để parse CSS style string
    parseStyleString(styleString) {
        const styles = {};
        if (!styleString) return styles;

        styleString.split(';').forEach(rule => {
            const [property, value] = rule.split(':').map(s => s.trim());
            if (property && value) {
                // Convert CSS property names to camelCase
                const camelProperty = property.replace(/-([a-z])/g, (match, letter) => letter.toUpperCase());
                styles[camelProperty] = value;
            }
        });

        return styles;
    }

    // Helper function để convert một HTML element thành editor element
    convertHtmlElementToEditorElement(htmlElement, index) {
        try {
            const tagName = htmlElement.tagName.toLowerCase();

            // Xác định type của element
            let elementType = 'text';
            if (tagName === 'img' || htmlElement.querySelector('img')) elementType = 'image';
            else if (tagName === 'video' || htmlElement.querySelector('video')) elementType = 'video';

            // Tạo element mới cho editor
            const editorElement = document.createElement('div');
            editorElement.className = 'element';
            editorElement.dataset.type = elementType;

            // Copy content
            editorElement.innerHTML = htmlElement.innerHTML;

            // Set default position và styles
            const styles = {
                position: 'absolute',
                left: (50 + index * 20) + 'px',
                top: (50 + index * 80) + 'px',
                width: '600px',
                height: 'auto',
                fontSize: '16px',
                color: '#000000',
                backgroundColor: 'transparent',
                textAlign: 'left',
                fontFamily: 'Arial, sans-serif',
                fontWeight: 'normal',
                zIndex: index + 1
            };

            // Apply styles
            Object.assign(editorElement.style, styles);

            // Thêm contenteditable cho text elements
            if (elementType === 'text') {
                editorElement.contentEditable = 'true';
            }

            return editorElement;
        } catch (error) {
            console.error('Error converting HTML element:', error);
            return null;
        }
    }

    // Helper: scope CSS to only affect the canvas area
    scopeCssToCanvas(css) {
        try {
            if (!css) return '';
            // Replace root selectors that commonly set page background
            let out = css
                .replace(/(^|[\s,{])body(\s*([,{]))/gi, '$1#canvas$2')
                .replace(/(^|[\s,{])html(\s*([,{]))/gi, '$1#canvas$2')
                .replace(/(^|[\s,{]):root(\s*([,{]))/gi, '$1#canvas$2');
            return out;
        } catch (e) {
            console.warn('Failed to scope CSS to canvas:', e);
            return css;
        }
    }

    // Helper function để extract background color chỉ từ body/html
    extractBackgroundColor(htmlContent) {
        try {
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlContent, 'text/html');

            // 1) Inline style trên <body>
            const bodyEl = doc.querySelector('body');
            if (bodyEl && bodyEl.getAttribute('style')) {
                const inline = bodyEl.getAttribute('style');
                const m = inline.match(/background(?:-color)?\s*:\s*([^;]+)/i);
                if (m) return m[1].trim();
            }

            // 2) Tìm trong <style>: selector body, html, :root có background
            const styleElements = doc.querySelectorAll('style');
            for (let styleEl of styleElements) {
                const cssText = styleEl.textContent || '';
                // simple search for body/html/:root with background declarations
                const bodyRule = cssText.match(/body\s*\{[^}]*background(?:-color)?\s*:\s*([^;\}]+)/i);
                if (bodyRule) return bodyRule[1].trim();
                const htmlRule = cssText.match(/html\s*\{[^}]*background(?:-color)?\s*:\s*([^;\}]+)/i);
                if (htmlRule) return htmlRule[1].trim();
                const rootRule = cssText.match(/:root\s*\{[^}]*background(?:-color)?\s*:\s*([^;\}]+)/i);
                if (rootRule) return rootRule[1].trim();
            }

            // Không tìm thấy => trả về null để giữ mặc định trắng
            return null;
        } catch (error) {
            console.error('Error extracting background color:', error);
            return null;
        }
    }

    // Message functions
    showSuccessMessage(message) {
        console.log('✅ Success:', message);
        // Tạo toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        z-index: 10000;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        max-width: 300px;
    `;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    showErrorMessage(message) {
        console.error('❌ Error:', message);
        // Tạo toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ef4444;
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        z-index: 10000;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        max-width: 300px;
    `;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    // Utility function: Debounce để tối ưu hiệu suất
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // === CAPTURE SLIDE FUNCTIONALITY ===
    async captureCurrentSlide() {
        try {
            this.showSuccessMessage('📸 Đang chụp slide...');

            const result = await this.slideCapture.captureCurrentSlide();

            if (result.success) {
                this.showCaptureSuccessDialog(result);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.showErrorMessage(`Lỗi khi chụp slide: ${error.message}`);
        }
    }

    async captureAllSlides() {
        try {
            this.showSuccessMessage('📸 Đang chụp tất cả slides...');

            const result = await this.slideCapture.captureAllSlides();

            if (result.success) {
                this.showCaptureAllSuccessDialog(result);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.showErrorMessage(`Lỗi khi chụp slides: ${error.message}`);
        }
    }

    async exportCurrentSlideToPdf() {
        try {
            this.showSuccessMessage('📄 Đang xuất slide thành PDF...');

            const currentSlide = this.slides[this.currentSlideIndex];
            if (!currentSlide) {
                throw new Error('Không có slide để xuất');
            }

            const response = await fetch(config.endpoints.exportSlidePdf, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    html_content: currentSlide.html || currentSlide.content,
                    slide_name: currentSlide.title || `slide_${this.currentSlideIndex + 1}`
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showPdfExportSuccessDialog(result);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.showErrorMessage(`Lỗi khi xuất PDF: ${error.message}`);
        }
    }

    // Clean slide content by removing editor UI elements
    cleanSlideContentForExport(content) {
        if (!content) return '';

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;

        // Remove all resize handles and editor UI
        tempDiv.querySelectorAll('.resize-handle').forEach(el => el.remove());
        tempDiv.querySelectorAll('.drag-handle').forEach(el => el.remove());
        tempDiv.querySelectorAll('.connector-control-point').forEach(el => el.remove());

        // Remove selected class from elements
        tempDiv.querySelectorAll('.element').forEach(el => {
            el.classList.remove('selected', 'dragging', 'editing');
            el.removeAttribute('contenteditable');
        });

        return tempDiv.innerHTML;
    }

    async exportAllSlidesToPdf() {
        try {
            this.showSuccessMessage('📄 Đang xuất tất cả slides thành PDF...');

            if (this.slides.length === 0) {
                throw new Error('Không có slide để xuất');
            }

            const slidesData = this.slides.map((slide, index) => ({
                html_content: this.cleanSlideContentForExport(slide.content),
                slide_name: slide.title || `slide_${index + 1}`
            }));

            const response = await fetch(config.endpoints.exportSlidesPdf, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    slides: slidesData
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showPdfExportAllSuccessDialog(result);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.showErrorMessage(`Lỗi khi xuất PDF: ${error.message}`);
        }
    }

    previewCurrentSlide() {
        this.slideCapture.previewSlide();
    }

    showCaptureSuccessDialog(result) {
        const modal = document.createElement('div');
        modal.id = 'captureSuccessModal';
        modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.8); display: flex; justify-content: center;
        align-items: center; z-index: 10000; cursor: pointer;
    `;

        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        modal.innerHTML = `
        <div style="background: white; border-radius: 12px; padding: 30px; max-width: 500px; text-align: center; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); cursor: default;">
            <h2 style="margin: 0 0 20px; color: #2d3748;">✅ Chụp thành công!</h2>
            <img src="${result.image_url}" style="max-width: 100%; height: auto; border-radius: 8px; margin-bottom: 20px; border: 1px solid #e2e8f0;">
            <div style="display: flex; gap: 10px; justify-content: center;">
                <a href="${result.download_url}" download style="text-decoration: none;">
                    <button style="padding: 12px 20px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">💾 Download</button>
                </a>
                <button onclick="document.getElementById('captureSuccessModal').remove()" style="padding: 12px 20px; background: #e2e8f0; color: #4a5568; border: none; border-radius: 6px; cursor: pointer;">Đóng</button>
            </div>
            <p style="margin-top: 15px; font-size: 12px; color: #718096;">Click bên ngoài để đóng hoặc nhấn ESC</p>
        </div>
    `;

        // ESC key to close
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);

        document.body.appendChild(modal);

        // Auto close after 10 seconds
        setTimeout(() => {
            if (document.getElementById('captureSuccessModal')) {
                document.getElementById('captureSuccessModal').remove();
            }
        }, 10000);
    }

    showCaptureAllSuccessDialog(result) {
        const modal = document.createElement('div');
        modal.id = 'captureAllSuccessModal';
        modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.8); display: flex; justify-content: center;
        align-items: center; z-index: 10000; cursor: pointer;
    `;

        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        const capturedSlides = result.captured_slides || [];
        const resultsList = capturedSlides.map(slideName => `
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding: 10px; background: #f7fafc; border-radius: 6px;">
            <span>✅ ${slideName}</span>
        </div>
    `).join('');

        modal.innerHTML = `
        <div style="background: white; border-radius: 12px; padding: 30px; max-width: 600px; max-height: 80vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); cursor: default;">
            <h2 style="margin: 0 0 20px; color: #2d3748; text-align: center;">✅ Chụp thành công ${capturedSlides.length} slides!</h2>
            <div style="margin-bottom: 20px;">
                ${resultsList}
            </div>
            <div style="text-align: center; display: flex; gap: 10px; justify-content: center;">
                <a href="${result.download_url}" download style="text-decoration: none;">
                    <button style="padding: 12px 20px; background: #48bb78; color: white; border: none; border-radius: 6px; cursor: pointer;">💾 Download ZIP</button>
                </a>
                <button onclick="document.getElementById('captureAllSuccessModal').remove()" style="padding: 12px 20px; background: #e2e8f0; color: #4a5568; border: none; border-radius: 6px; cursor: pointer;">Đóng</button>
            </div>
            <p style="margin-top: 15px; font-size: 12px; color: #718096; text-align: center;">Click bên ngoài để đóng hoặc nhấn ESC</p>
        </div>
    `;

        // ESC key to close
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);

        document.body.appendChild(modal);

        // Auto close after 15 seconds
        setTimeout(() => {
            if (document.getElementById('captureAllSuccessModal')) {
                document.getElementById('captureAllSuccessModal').remove();
            }
        }, 15000);
    }

    showPdfExportSuccessDialog(result) {
        const modal = document.createElement('div');
        modal.id = 'pdfExportSuccessModal';
        modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.8); display: flex; justify-content: center;
        align-items: center; z-index: 10000; cursor: pointer;
    `;

        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        modal.innerHTML = `
        <div style="background: white; border-radius: 12px; padding: 30px; max-width: 500px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); cursor: default;">
            <h2 style="margin: 0 0 20px; color: #2d3748; text-align: center;">📄 Xuất PDF thành công!</h2>
            <p style="margin-bottom: 20px; color: #4a5568; text-align: center;">${result.message}</p>
            <div style="text-align: center; display: flex; gap: 10px; justify-content: center;">
                <a href="${config.BACKEND_URL}${result.download_url}" download style="text-decoration: none;">
                    <button style="padding: 12px 20px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer;">📄 Download PDF</button>
                </a>
                <button onclick="document.getElementById('pdfExportSuccessModal').remove()" style="padding: 12px 20px; background: #e2e8f0; color: #4a5568; border: none; border-radius: 6px; cursor: pointer;">Đóng</button>
            </div>
            <p style="margin-top: 15px; font-size: 12px; color: #718096; text-align: center;">Click bên ngoài để đóng hoặc nhấn ESC</p>
        </div>
    `;

        // ESC key to close
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);

        document.body.appendChild(modal);

        // Auto close after 10 seconds
        setTimeout(() => {
            if (document.getElementById('pdfExportSuccessModal')) {
                document.getElementById('pdfExportSuccessModal').remove();
            }
        }, 10000);
    }

    showPdfExportAllSuccessDialog(result) {
        const modal = document.createElement('div');
        modal.id = 'pdfExportAllSuccessModal';
        modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.8); display: flex; justify-content: center;
        align-items: center; z-index: 10000; cursor: pointer;
    `;

        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        modal.innerHTML = `
        <div style="background: white; border-radius: 12px; padding: 30px; max-width: 500px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); cursor: default;">
            <h2 style="margin: 0 0 20px; color: #2d3748; text-align: center;">📄 Xuất PDF thành công!</h2>
            <p style="margin-bottom: 20px; color: #4a5568; text-align: center;">${result.message}</p>
            <div style="text-align: center; display: flex; gap: 10px; justify-content: center;">
                <a href="${config.BACKEND_URL}${result.download_url}" download style="text-decoration: none;">
                    <button style="padding: 12px 20px; background: #f97316; color: white; border: none; border-radius: 6px; cursor: pointer;">📄 Download PDF</button>
                </a>
                <button onclick="document.getElementById('pdfExportAllSuccessModal').remove()" style="padding: 12px 20px; background: #e2e8f0; color: #4a5568; border: none; border-radius: 6px; cursor: pointer;">Đóng</button>
            </div>
            <p style="margin-top: 15px; font-size: 12px; color: #718096; text-align: center;">Click bên ngoài để đóng hoặc nhấn ESC</p>
        </div>
    `;

        // ESC key to close
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);

        document.body.appendChild(modal);

        // Auto close after 10 seconds
        setTimeout(() => {
            if (document.getElementById('pdfExportAllSuccessModal')) {
                document.getElementById('pdfExportAllSuccessModal').remove();
            }
        }, 10000);
    }

    showSuccessMessage(message) {
        // Create or update existing message
        let msgEl = document.getElementById('successMessage');
        if (!msgEl) {
            msgEl = document.createElement('div');
            msgEl.id = 'successMessage';
            msgEl.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 9999;
            background: #48bb78; color: white; padding: 12px 20px;
            border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            font-size: 14px; font-weight: 500;
        `;
            document.body.appendChild(msgEl);
        }

        msgEl.textContent = message;
        msgEl.style.display = 'block';

        setTimeout(() => {
            if (msgEl && msgEl.parentNode) {
                msgEl.parentNode.removeChild(msgEl);
            }
        }, 3000);
    }

    showErrorMessage(message) {
        // Create or update existing message
        let msgEl = document.getElementById('errorMessage');
        if (!msgEl) {
            msgEl = document.createElement('div');
            msgEl.id = 'errorMessage';
            msgEl.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 9999;
            background: #f56565; color: white; padding: 12px 20px;
            border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            font-size: 14px; font-weight: 500;
        `;
            document.body.appendChild(msgEl);
        }

        msgEl.textContent = message;
        msgEl.style.display = 'block';

        setTimeout(() => {
            if (msgEl && msgEl.parentNode) {
                msgEl.parentNode.removeChild(msgEl);
            }
        }, 5000);
    }

    // === END CAPTURE FUNCTIONALITY ===

    testCapture() {
        // Enhanced test function
        console.group('🧪 TEST: Capture Process');

        try {
            console.log('Testing capture process...');

            // Test HTML generation
            const html = this.slideCapture.getCurrentSlideHTML();
            if (html) {
                console.log('✅ HTML generated successfully');
                console.log('HTML length:', html.length);
                console.log('HTML preview (first 200 chars):', html.substring(0, 200) + '...');

                // Show preview
                this.slideCapture.previewSlide();

                // Show success message
                this.showSuccessMessage('✅ HTML generated successfully! Check console for details.');
            } else {
                console.error('❌ Failed to generate HTML');
                this.showErrorMessage('❌ Failed to generate HTML');
            }
        } catch (error) {
            console.error('❌ Error in test capture:', error);
            this.showErrorMessage(`❌ Error: ${error.message}`);
        }

        console.groupEnd();
    }

    // Enhanced logging for capture functions
    async captureCurrentSlide() {
        console.log('🎯 Starting capture current slide...');

        try {
            this.showSuccessMessage('📸 Đang chụp slide...');

            const result = await this.slideCapture.captureCurrentSlide();

            console.log('✅ Capture result:', result);

            if (result.success) {
                this.showCaptureSuccessDialog(result);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('❌ Capture error:', error);
            this.showErrorMessage(`Lỗi khi chụp slide: ${error.message}`);
        }
    }
    // === END DEBUG FUNCTIONALITY ===

    // === END RESET FUNCTIONALITY ===

}

// Apply mixins to SlideEditor prototype
Object.assign(SlideEditor.prototype, ExportMixin, PresentationMixin);


// Apply mixins to SlideEditor prototype
Object.assign(SlideEditor.prototype, ExportMixin, PresentationMixin);
