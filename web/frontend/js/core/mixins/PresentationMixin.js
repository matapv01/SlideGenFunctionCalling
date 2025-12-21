/**
 * PresentationMixin.js
 * Handles presentation mode functionality for slides
 * Includes fullscreen mode, navigation, timeline, and keyboard controls
 */

export const PresentationMixin = {
    /**
     * Start presentation mode
     * @param {boolean} fromStart - Whether to start from first slide (default: true)
     */
    startPresentation(fromStart = true) {
        if (this.slides.length === 0) return;

        // Save current slide
        this.saveCurrentSlide();

        // Start from first slide or current slide based on parameter
        this.presentationSlideIndex = fromStart ? 0 : this.currentSlideIndex;

        // Show presentation mode
        const presentationMode = document.getElementById('presentationMode');
        presentationMode.classList.add('active');
        this.presentationMode = true;

        // Hide scrollbars
        document.body.style.overflow = 'hidden';

        // Request fullscreen API (hides Chrome address bar)
        const elem = presentationMode;
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) { // Safari
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) { // IE11
            elem.msRequestFullscreen();
        }

        // Render first slide
        this.renderPresentationSlide();

        // Setup keyboard navigation
        this.setupPresentationKeyboard();

        // Scale to fit screen
        this.scalePresentationToFit();
    },

    /**
     * Render current slide in presentation mode
     */
    renderPresentationSlide() {
        const slide = this.slides[this.presentationSlideIndex];
        const container = document.getElementById('presentationSlideContainer');
        container.innerHTML = '';

        // Create temporary HTML file for this slide and render via iframe
        const slideHtml = this.createPresentationSlideHtml(slide);
        const blob = new Blob([slideHtml], { type: 'text/html' });
        const iframeUrl = URL.createObjectURL(blob);

        // Create iframe to render the slide
        const iframe = document.createElement('iframe');
        iframe.style.cssText = `
            width: 1920px;
            height: 1080px;
            border: none;
            background: white;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        `;
        iframe.src = iframeUrl;

        // Clean up blob URL after iframe loads
        iframe.onload = () => {
            setTimeout(() => URL.revokeObjectURL(iframeUrl), 100);
        };

        container.appendChild(iframe);

        // Update counter
        document.getElementById('presentationCounter').textContent = 
            `${this.presentationSlideIndex + 1} / ${this.slides.length}`;

        // Update button states
        document.getElementById('prevSlideBtn').disabled = this.presentationSlideIndex === 0;
        document.getElementById('nextSlideBtn').disabled = this.presentationSlideIndex === this.slides.length - 1;

        // Update cursor zones
        const zoneLeft = document.getElementById('presentationZoneLeft');
        const zoneRight = document.getElementById('presentationZoneRight');
        if (this.presentationSlideIndex === 0) {
            zoneLeft.classList.add('disabled');
        } else {
            zoneLeft.classList.remove('disabled');
        }
        if (this.presentationSlideIndex === this.slides.length - 1) {
            zoneRight.classList.add('disabled');
        } else {
            zoneRight.classList.remove('disabled');
        }

        // Update timeline
        this.updatePresentationTimeline();
    },

    /**
     * Create standalone HTML for presentation slide
     * @param {Object} slide - Slide object
     * @returns {string} Complete HTML document
     */
    createPresentationSlideHtml(slide) {
        // Clean up content before rendering
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = slide.content;

        // Remove ALL editor-specific elements and UI controls
        tempDiv.querySelectorAll('.resize-handle').forEach(el => el.remove());
        tempDiv.querySelectorAll('.drag-handle').forEach(el => el.remove());
        tempDiv.querySelectorAll('.rotate-handle').forEach(el => el.remove());
        tempDiv.querySelectorAll('.connection-point').forEach(el => el.remove());
        tempDiv.querySelectorAll('.selection-box').forEach(el => el.remove());
        tempDiv.querySelectorAll('.guide-line').forEach(el => el.remove());
        tempDiv.querySelectorAll('.distance-line').forEach(el => el.remove());
        tempDiv.querySelectorAll('.distance-label').forEach(el => el.remove());
        
        // Clean up element attributes
        tempDiv.querySelectorAll('.element').forEach(el => {
            el.removeAttribute('contenteditable');
            el.classList.remove('selected');
            el.classList.remove('hover');
            el.style.cursor = 'default';
            // Remove any outline or selection styles
            el.style.outline = 'none';
            el.style.border = el.dataset.originalBorder || el.style.border;
        });

        const cleanContent = tempDiv.innerHTML;
        const backgroundColor = slide.backgroundColor || 'white';

        // Determine background CSS
        let backgroundStyle = '';
        if (backgroundColor.startsWith('linear-gradient') || 
            backgroundColor.startsWith('radial-gradient') || 
            backgroundColor.startsWith('url(')) {
            backgroundStyle = `background: ${backgroundColor};`;
        } else {
            backgroundStyle = `background-color: ${backgroundColor};`;
        }

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            width: 1920px;
            height: 1080px;
            ${backgroundStyle}
            position: relative;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
    </style>
</head>
<body>
    ${cleanContent}
</body>
</html>`;
    },

    /**
     * Scale presentation content to fit screen
     */
    scalePresentationToFit() {
        const container = document.getElementById('presentationSlideContainer');
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        
        const scaleX = windowWidth / 1920;
        const scaleY = windowHeight / 1080;
        const scale = Math.min(scaleX, scaleY); // Full screen, no padding
        
        container.style.transform = `scale(${scale})`;
    },

    /**
     * Setup keyboard navigation and event handlers for presentation mode
     */
    setupPresentationKeyboard() {
        this.presentationKeyboardHandler = (e) => {
            switch(e.key) {
                case 'ArrowRight':
                case 'ArrowDown':
                case ' ':
                case 'PageDown':
                    e.preventDefault();
                    this.nextPresentationSlide();
                    break;
                case 'ArrowLeft':
                case 'ArrowUp':
                case 'PageUp':
                    e.preventDefault();
                    this.previousPresentationSlide();
                    break;
                case 'Escape':
                    e.preventDefault();
                    this.exitPresentation();
                    break;
                case 'Home':
                    e.preventDefault();
                    this.presentationSlideIndex = 0;
                    this.renderPresentationSlide();
                    break;
                case 'End':
                    e.preventDefault();
                    this.presentationSlideIndex = this.slides.length - 1;
                    this.renderPresentationSlide();
                    break;
            }
        };

        document.addEventListener('keydown', this.presentationKeyboardHandler);

        // Navigation buttons
        document.getElementById('prevSlideBtn').onclick = () => this.previousPresentationSlide();
        document.getElementById('nextSlideBtn').onclick = () => this.nextPresentationSlide();
        document.getElementById('exitPresentation').onclick = () => this.exitPresentation();

        // Click zones for navigation
        document.getElementById('presentationZoneLeft').onclick = () => this.previousPresentationSlide();
        document.getElementById('presentationZoneRight').onclick = () => this.nextPresentationSlide();

        // Listen for fullscreen exit (when user presses ESC)
        this.fullscreenChangeHandler = () => {
            if (!document.fullscreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement) {
                if (this.presentationMode) {
                    this.exitPresentation();
                }
            }
        };
        document.addEventListener('fullscreenchange', this.fullscreenChangeHandler);
        document.addEventListener('webkitfullscreenchange', this.fullscreenChangeHandler);
        document.addEventListener('msfullscreenchange', this.fullscreenChangeHandler);

        // Window resize
        window.addEventListener('resize', () => this.scalePresentationToFit());

        // Setup timeline
        this.setupPresentationTimeline();
        
        // Setup auto-hide for timeline and controls
        this.setupPresentationAutoHide();
    },

    /**
     * Setup presentation timeline with slide markers
     */
    setupPresentationTimeline() {
        const timelineSlides = document.getElementById('timelineSlides');
        const timelineTrack = document.getElementById('timelineTrack');
        
        // Clear existing markers
        timelineSlides.innerHTML = '';
        
        // Create slide markers
        this.slides.forEach((slide, index) => {
            const marker = document.createElement('div');
            marker.className = 'timeline-slide-marker';
            if (index === this.presentationSlideIndex) {
                marker.classList.add('active');
            }
            
            const slideNumber = document.createElement('div');
            slideNumber.className = 'slide-number';
            slideNumber.textContent = `Slide ${index + 1}`;
            marker.appendChild(slideNumber);
            
            marker.addEventListener('click', () => {
                this.goToPresentationSlide(index);
            });
            
            timelineSlides.appendChild(marker);
        });
        
        // Click on track to jump to slide
        timelineTrack.addEventListener('click', (e) => {
            const rect = timelineTrack.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const percentage = x / rect.width;
            const targetSlide = Math.floor(percentage * this.slides.length);
            this.goToPresentationSlide(Math.max(0, Math.min(targetSlide, this.slides.length - 1)));
        });
        
        this.updatePresentationTimeline();
    },

    /**
     * Update presentation timeline progress and indicators
     */
    updatePresentationTimeline() {
        const progress = document.getElementById('timelineProgress');
        const indicator = document.getElementById('timelineIndicator');
        const markers = document.querySelectorAll('.timeline-slide-marker');
        
        // Update progress bar
        const percentage = ((this.presentationSlideIndex + 1) / this.slides.length) * 100;
        progress.style.width = percentage + '%';
        
        // Update indicator position
        const slidePercentage = (this.presentationSlideIndex / (this.slides.length - 1)) * 100;
        indicator.style.left = slidePercentage + '%';
        
        // Update active marker
        markers.forEach((marker, index) => {
            if (index === this.presentationSlideIndex) {
                marker.classList.add('active');
            } else {
                marker.classList.remove('active');
            }
        });
    },

    /**
     * Jump to specific slide in presentation
     * @param {number} index - Slide index
     */
    goToPresentationSlide(index) {
        if (index >= 0 && index < this.slides.length) {
            this.presentationSlideIndex = index;
            this.renderPresentationSlide();
        }
    },

    /**
     * Navigate to next slide
     */
    nextPresentationSlide() {
        if (this.presentationSlideIndex < this.slides.length - 1) {
            this.presentationSlideIndex++;
            this.renderPresentationSlide();
        }
    },

    /**
     * Navigate to previous slide
     */
    previousPresentationSlide() {
        if (this.presentationSlideIndex > 0) {
            this.presentationSlideIndex--;
            this.renderPresentationSlide();
        }
    },

    /**
     * Setup auto-hide for timeline and controls
     */
    setupPresentationAutoHide() {
        let hideTimeout;
        const timeline = document.getElementById('presentationTimeline');
        const controls = document.querySelector('.presentation-controls');
        
        if (timeline && controls) {
            const showControls = () => {
                timeline.classList.add('show');
                controls.classList.add('show');
                clearTimeout(hideTimeout);
                hideTimeout = setTimeout(() => {
                    timeline.classList.remove('show');
                    controls.classList.remove('show');
                }, 1500);
            };
            
            // Listen on document to catch all mouse movements
            this.presentationMouseMoveHandler = showControls;
            document.addEventListener('mousemove', this.presentationMouseMoveHandler);
            
            // Show initially
            showControls();
        }
    },

    /**
     * Exit presentation mode
     */
    exitPresentation() {
        // Remove fullscreen change handler
        if (this.fullscreenChangeHandler) {
            document.removeEventListener('fullscreenchange', this.fullscreenChangeHandler);
            document.removeEventListener('webkitfullscreenchange', this.fullscreenChangeHandler);
            document.removeEventListener('msfullscreenchange', this.fullscreenChangeHandler);
            this.fullscreenChangeHandler = null;
        }
        
        // Remove auto-hide mouse handler
        if (this.presentationMouseMoveHandler) {
            document.removeEventListener('mousemove', this.presentationMouseMoveHandler);
            this.presentationMouseMoveHandler = null;
        }

        // Exit fullscreen API (only if still in fullscreen)
        if (document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement) {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
        }

        // Remove keyboard handler
        if (this.presentationKeyboardHandler) {
            document.removeEventListener('keydown', this.presentationKeyboardHandler);
            this.presentationKeyboardHandler = null;
        }

        // Hide presentation mode
        const presentationMode = document.getElementById('presentationMode');
        presentationMode.classList.remove('active');
        this.presentationMode = false;

        // Restore scrollbars
        document.body.style.overflow = '';

        // Always return to the slide we were viewing in presentation
        this.currentSlideIndex = this.presentationSlideIndex;
        this.loadSlide(this.currentSlideIndex);
        this.renderSlidesList();
    }
};
