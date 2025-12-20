// streaming.js - Handle streaming workflow updates
// Config is already loaded globally from config.js in HTML head


let eventSource = null;
let projectName = null;
let projectId = null; // Store project ID for redirect
let totalSlides = 0;
let completedSlides = 0;
let slides = []; // Store all slides for presentation
let currentPresentationIndex = 0;
let isPresentationMode = false;
let presentationKeyboardHandler = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    initializeParticles();

    // Get project info from URL params
    const urlParams = new URLSearchParams(window.location.search);
    const filename = urlParams.get('filename');
    const session = urlParams.get('session');
    const manualSession = urlParams.get('manual_session');

    // Route to appropriate workflow
    if (manualSession) {
        // From manual structure editor
        console.log('🎨 Starting manual structure workflow:', manualSession);
        projectName = `manual_${manualSession}`;
        startStreamingFromManualStructure(manualSession);
    } else if (session) {
        // From "Create with Idea"
        projectName = `idea_${session}`;
        startStreamingFromIdea(session);
    } else if (filename) {
        // From file upload (auto workflow)
        projectName = filename.replace(/\.docx$/i, '');

        // Try to restore previous state
        const restored = restoreStreamingState(filename);

        if (!restored) {
            // Start streaming if not restored
            startStreaming(filename);
        }
    } else {
        showError('Không tìm thấy thông tin file hoặc session');
        return;
    }

    // Setup button handlers
    document.getElementById('goToEditor')?.addEventListener('click', goToEditor);
    document.getElementById('backToHome')?.addEventListener('click', () => {
        window.location.href = 'index.html';
    });
    document.getElementById('retryButton')?.addEventListener('click', () => {
        window.location.href = 'index.html';
    });

    // Setup presentation button (will be shown when slides complete)
    document.getElementById('presentButton')?.addEventListener('click', () => {
        if (slides.length > 0) {
            startPresentation(0);
        }
    });
});

function initializeParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 30;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';

        // Random size
        const size = Math.random() * 6 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';

        // Random position
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';

        // Random animation duration
        const duration = Math.random() * 20 + 15;
        particle.style.animationDuration = duration + 's';

        // Random delay
        const delay = Math.random() * 5;
        particle.style.animationDelay = delay + 's';

        particlesContainer.appendChild(particle);
    }
}

function startStreaming(filename) {
    console.log('Starting streaming for:', filename);
    showToast('🔗 Đang kết nối đến server...', 'info');

    // Make sure slides preview is visible
    const slidesPreview = document.getElementById('slidesPreview');
    if (slidesPreview) {
        slidesPreview.style.display = 'block';
    }

    // Close existing connection if any
    if (eventSource) {
        eventSource.close();
    }

    // Create EventSource for SSE with auth token
    const token = localStorage.getItem('access_token');
    console.log('🔑 Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'NULL OR MISSING');

    // Check if token exists
    if (!token || token === 'null') {
        console.error('❌ No valid token found! Redirecting to login...');
        showToast('⚠️ Vui lòng đăng nhập để tạo slide', 'error');
        setTimeout(() => {
            window.location.href = 'login.html?redirect=' + encodeURIComponent(window.location.href);
        }, 2000);
        return;
    }

    const url = `${config.BACKEND_URL}/api/upload-docx-stream?filename=${encodeURIComponent(filename)}&token=${encodeURIComponent(token)}`;
    console.log('Connecting to:', url);
    eventSource = new EventSource(url);

    eventSource.onopen = function () {
        console.log('✅ EventSource connected successfully');
        showToast('✅ Đã kết nối thành công!', 'success');
    };

    // Handle different event types
    eventSource.addEventListener('status', handleStatusEvent);
    eventSource.addEventListener('progress', handleProgressEvent);
    eventSource.addEventListener('slide_completed', handleSlideCompletedEvent);
    eventSource.addEventListener('complete', handleCompleteEvent);
    eventSource.addEventListener('error_event', handleErrorEvent);
    eventSource.addEventListener('error', handleErrorEvent); // Also listen for 'error' event type

    // Also listen for generic message event (fallback)
    eventSource.onmessage = function (event) {
        console.log('Generic message received:', event.data);
    };

    eventSource.onerror = function (error) {
        console.error('EventSource error:', error);
        console.error('EventSource readyState:', eventSource.readyState);

        // If the error container is already showing a specific error, don't overwrite it
        const errorContainer = document.getElementById('errorContainer');
        const isShowingSpecificError = errorContainer && errorContainer.style.display === 'flex';

        if (eventSource.readyState === EventSource.CLOSED && !isShowingSpecificError) {
            showToast('❌ Kết nối bị đóng', 'error');
            showError('Mất kết nối với server. Vui lòng thử lại.');
        } else if (eventSource.readyState === EventSource.CONNECTING) {
            console.log('🔄 Reconnecting...');
        }
    };
}

function startStreamingFromIdea(session_id) {
    console.log('Starting streaming from idea for session:', session_id);
    showToast('🔗 Đang kết nối đến server...', 'info');

    // Make sure slides preview is visible
    const slidesPreview = document.getElementById('slidesPreview');
    if (slidesPreview) {
        slidesPreview.style.display = 'block';
    }

    // Close existing connection if any
    if (eventSource) {
        eventSource.close();
    }

    // Create EventSource for idea-based SSE with auth token
    const token = localStorage.getItem('access_token');
    console.log('🔑 Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'NULL OR MISSING');

    // Check if token exists
    if (!token || token === 'null') {
        console.error('❌ No valid token found! Redirecting to login...');
        showToast('⚠️ Vui lòng đăng nhập để tạo slide', 'error');
        setTimeout(() => {
            window.location.href = 'login.html?redirect=' + encodeURIComponent(window.location.href);
        }, 2000);
        return;
    }

    const url = `${config.BACKEND_URL}/api/generate-from-idea-stream?session_id=${encodeURIComponent(session_id)}&token=${encodeURIComponent(token)}`;
    console.log('Connecting to:', url);
    eventSource = new EventSource(url);

    eventSource.onopen = function () {
        console.log('✅ EventSource connected successfully');
        showToast('✅ Đã kết nối thành công!', 'success');
    };

    // Handle different event types (same as file upload)
    eventSource.addEventListener('status', handleStatusEvent);
    eventSource.addEventListener('progress', handleProgressEvent);
    eventSource.addEventListener('slide_completed', handleSlideCompletedEvent);
    eventSource.addEventListener('complete', handleCompleteEvent);
    eventSource.addEventListener('error_event', handleErrorEvent);
    eventSource.addEventListener('error', handleErrorEvent);

    // Also listen for generic message event (fallback)
    eventSource.onmessage = function (event) {
        console.log('Generic message received:', event.data);
    };

    eventSource.onerror = function (error) {
        console.error('EventSource error:', error);

        const errorContainer = document.getElementById('errorContainer');
        const isShowingSpecificError = errorContainer && errorContainer.style.display === 'flex';

        if (eventSource.readyState === EventSource.CLOSED && !isShowingSpecificError) {
            console.error('Connection was closed');
            showToast('⚠️ Mất kết nối với server', 'error');
            showError('Mất kết nối với server. Vui lòng thử lại.');
        } else if (eventSource.readyState === EventSource.CONNECTING) {
            console.log('🔄 Reconnecting...');
        }
    };
}

function startStreamingFromManualStructure(session_id) {
    console.log('Starting streaming from manual structure for session:', session_id);
    showToast('🔗 Đang kết nối đến server...', 'info');

    // Make sure slides preview is visible
    const slidesPreview = document.getElementById('slidesPreview');
    if (slidesPreview) {
        slidesPreview.style.display = 'block';
    }

    // Close existing connection if any
    if (eventSource) {
        eventSource.close();
    }

    // Create EventSource for manual structure SSE with auth token
    const token = localStorage.getItem('access_token');
    const url = `${config.BACKEND_URL}/api/generate-from-manual-structure-stream?session_id=${encodeURIComponent(session_id)}&token=${encodeURIComponent(token)}`;
    console.log('Connecting to manual structure endpoint:', url);
    eventSource = new EventSource(url);

    eventSource.onopen = function () {
        console.log('✅ Manual structure EventSource connected');
        showToast('✅ Đã kết nối thành công!', 'success');
    };

    // Handle different event types (same handlers as other workflows)
    eventSource.addEventListener('status', handleStatusEvent);
    eventSource.addEventListener('progress', handleProgressEvent);
    eventSource.addEventListener('slide_completed', handleSlideCompletedEvent);
    eventSource.addEventListener('complete', handleCompleteEvent);
    eventSource.addEventListener('error_event', handleErrorEvent);
    eventSource.addEventListener('error', handleErrorEvent);

    // Also listen for generic message event (fallback)
    eventSource.onmessage = function (event) {
        console.log('Generic message received:', event.data);
    };

    eventSource.onerror = function (error) {
        console.error('EventSource error:', error);

        const errorContainer = document.getElementById('errorContainer');
        const isShowingSpecificError = errorContainer && errorContainer.style.display === 'flex';

        if (eventSource.readyState === EventSource.CLOSED && !isShowingSpecificError) {
            console.error('Connection was closed');
            showToast('⚠️ Mất kết nối với server', 'error');
            showError('Mất kết nối với server. Vui lòng thử lại.');
        } else if (eventSource.readyState === EventSource.CONNECTING) {
            console.log('🔄 Reconnecting...');
        }
    };
}


function handleStatusEvent(event) {
    console.log('📢 Status event received:', event);
    const data = JSON.parse(event.data);
    console.log('Status data:', data);

    // Update current activity text to match step message
    const currentActivityDiv = document.getElementById('current-activity');
    if (currentActivityDiv) {
        // Map step messages to activity text
        let activityText = data.message;
        if (data.message.includes('Phân tích')) {
            activityText = 'Đang phân tích nội dung tài liệu...';
        } else if (data.message.includes('Chuẩn bị')) {
            activityText = 'Đang chuẩn bị nội dung cho các slide...';
        } else if (data.message.includes('Thiết kế')) {
            activityText = 'Đang thiết kế và tạo các slide...';
        }
        currentActivityDiv.textContent = activityText;
    }

    updateActivity(data.title, data.description);
    updateStepStatus(data.step);
}

function handleProgressEvent(event) {
    const data = JSON.parse(event.data);
    console.log('Progress event:', data);

    updateProgress(data.current, data.total, data.percentage);

    if (data.message) {
        updateActivity(data.title || 'Đang xử lý...', data.message);
    }

    // Update total count but DON'T create placeholders yet
    // Wait for complete event with actual total
    if (data.total && data.total > 0) {
        const totalCountEl = document.getElementById('totalSlideCount');
        if (totalCountEl) totalCountEl.textContent = data.total;
    }
}

function handleSlideCompletedEvent(event) {
    console.log('🎉 Slide completed event received:', event);
    const data = JSON.parse(event.data);
    console.log('Slide data:', data);

    // Store slide for presentation
    slides.push(data);

    completedSlides++;

    // Save state to sessionStorage
    saveStreamingState();

    // Always add new slide directly (no placeholders for real-time streaming)
    addSlidePreview(data);

    // Update slide count
    const slideCountEl = document.getElementById('slideCount');
    if (slideCountEl) {
        slideCountEl.textContent = completedSlides;
    }

    // Show toast notification
    showToast(
        `✨ Slide ${data.index + 1} hoàn tất`,
        'success'
    );

    // Update activity
    if (data.total && completedSlides < data.total) {
        updateActivity(
            `Đang tạo slide ${completedSlides + 1}/${data.total}...`,
            'Vui lòng đợi...'
        );
    } else {
        updateActivity(
            `Đang hoàn tất...`,
            `Đã tạo ${completedSlides} slide`
        );
    }
}

let tempDirectory = null;

function handleCompleteEvent(event) {
    const data = JSON.parse(event.data);
    console.log('Complete event:', data);

    projectName = data.project_name;
    projectId = data.project_id; // Store project ID for redirect
    totalSlides = data.total_slides;
    tempDirectory = data.temp_dir; // Store for cleanup later

    // Save completed state
    saveStreamingState(true);

    // Update total count with actual number from complete event
    const totalCountEl = document.getElementById('totalSlideCount');
    if (totalCountEl) totalCountEl.textContent = totalSlides;

    // Close event source
    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }

    // Update UI to show completion
    updateActivity(
        '🎉 Hoàn tất!',
        `Đã tạo thành công ${totalSlides} slide`
    );

    updateProgress(100, 100, 100);
    updateAllStepsComplete();

    showToast(`🎉 Hoàn tất! Đã tạo thành công ${totalSlides} slide`, 'success');

    // Show action buttons
    document.getElementById('actionButtons').style.display = 'flex';

    // Hide spinner
    document.querySelector('.activity-icon .spinner').style.display = 'none';
}

function handleErrorEvent(event) {
    const data = JSON.parse(event.data);
    console.error('Error event:', data);

    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }

    showError(data.message || 'Đã xảy ra lỗi khi tạo slide');
    showToast(`❌ Lỗi: ${data.message}`, 'error');
}

function updateActivity(title, description) {
    const titleEl = document.getElementById('activityTitle');
    const descEl = document.getElementById('activityDescription');

    if (titleEl) titleEl.textContent = title;
    if (descEl) descEl.textContent = description;
}

function updateProgress(current, total, percentage) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }

    if (progressText) {
        progressText.textContent = `${Math.round(percentage)}%`;
    }
}

function updateStepStatus(stepNumber) {
    // Reset all steps
    for (let i = 1; i <= 3; i++) {
        const step = document.getElementById(`step-${i}`);
        if (step) {
            step.classList.remove('active', 'completed');
        }
    }

    // Mark completed steps with staggered animation for steps 1 and 2
    for (let i = 1; i < stepNumber; i++) {
        // Each step: 5 seconds
        const delay = (i <= 2) ? (i - 1) * 5000 : 0;
        setTimeout(() => {
            const step = document.getElementById(`step-${i}`);
            if (step) {
                step.classList.add('completed');
                const statusText = step.querySelector('.status-text');
                if (statusText) statusText.textContent = 'Hoàn tất';
            }
        }, delay);
    }

    // Mark current step with delay if previous steps need animation
    const activationDelay = (stepNumber === 2) ? 5000 : (stepNumber === 3) ? 10000 : 0; // 5s for step 2, 10s (5+5) for step 3
    setTimeout(() => {
        const currentStep = document.getElementById(`step-${stepNumber}`);
        if (currentStep) {
            currentStep.classList.add('active');
            const statusText = currentStep.querySelector('.status-text');
            if (statusText) statusText.textContent = 'Đang xử lý...';
        }
    }, activationDelay);
}

function updateAllStepsComplete() {
    for (let i = 1; i <= 3; i++) {
        const step = document.getElementById(`step-${i}`);
        if (step) {
            step.classList.remove('active');
            step.classList.add('completed');
            const statusText = step.querySelector('.status-text');
            if (statusText) statusText.textContent = 'Hoàn tất';
        }
    }
}

function ensurePlaceholderSlides(total) {
    const slidesGrid = document.getElementById('slidesGrid');
    if (!slidesGrid) return;

    const existingPlaceholders = slidesGrid.querySelectorAll('.slide-placeholder-card').length;
    const existingSlides = slidesGrid.querySelectorAll('.slide-card:not(.slide-placeholder-card)').length;

    // Only create placeholders if we don't have them yet
    if (existingPlaceholders === 0 && existingSlides === 0) {
        for (let i = 0; i < total; i++) {
            createPlaceholderSlide(i);
        }
    }
}

function createPlaceholderSlide(index) {
    const slidesGrid = document.getElementById('slidesGrid');
    if (!slidesGrid) return;

    const placeholder = document.createElement('div');
    placeholder.className = 'slide-card slide-placeholder-card';
    placeholder.setAttribute('data-index', index);

    const staggerDelay = index * 0.08;
    placeholder.style.animationDelay = `${staggerDelay}s`;

    placeholder.innerHTML = `
        <div class="slide-number">Slide ${index + 1}</div>
        <div class="slide-preview loading">
            <div class="slide-placeholder">
                <i class="bi bi-hourglass-split"></i>
            </div>
        </div>
        <div class="slide-generating">
            <div class="slide-generating-text">
                <i class="bi bi-stars"></i> Đang tạo...
            </div>
            <div class="slide-progress-bar">
                <div class="slide-progress-fill"></div>
            </div>
        </div>
    `;

    slidesGrid.appendChild(placeholder);

    setTimeout(() => {
        placeholder.classList.add('show');
    }, 50);
}

function replacePlaceholderWithSlide(placeholder, slideData) {
    console.log('🔄 Replacing placeholder with slide:', slideData);

    // Build iframe URL
    let iframeUrl = '';
    let displayName = `Slide ${slideData.index + 1}`;

    if (slideData.is_temp && slideData.html_path) {
        // Use temp file API for real-time streaming with query parameter
        iframeUrl = `${config.BACKEND_URL}/api/temp-file?path=${encodeURIComponent(slideData.html_path)}`;
        displayName = slideData.html_path.split('/').pop();
        console.log('📄 Loading from temp:', slideData.html_path);
        console.log('🔗 Iframe URL:', iframeUrl);
    } else {
        // Use static output folder
        const htmlFilename = slideData.html_path ? slideData.html_path.split('/').pop() : `slide_${slideData.index + 1}.html`;
        iframeUrl = `${config.BACKEND_URL}/static/output/${projectName}/html/${htmlFilename}`;
        displayName = htmlFilename;
        console.log('📄 Loading from output:', htmlFilename);
    }

    // Fade out placeholder content
    placeholder.style.transition = 'opacity 0.3s ease';
    placeholder.style.opacity = '0.5';

    setTimeout(() => {
        // Replace content
        placeholder.className = 'slide-card show';
        placeholder.removeAttribute('data-index');
        placeholder.style.opacity = '1';

        placeholder.innerHTML = `
            <div class="slide-number">Slide ${slideData.index + 1}</div>
            <div class="slide-preview loading" id="preview-${slideData.index}">
                <iframe src="${iframeUrl}" 
                         frameborder="0" 
                         scrolling="no"
                         onload="console.log('✅ Iframe loaded:', '${displayName}'); this.classList.add('loaded'); this.parentElement.classList.remove('loading');"
                         onerror="console.error('❌ Iframe load error:', '${displayName}'); this.parentElement.innerHTML = '<div class=\\'slide-placeholder\\'><i class=\\'bi bi-exclamation-triangle\\'></i></div>';"></iframe>
            </div>
            <div class="slide-info">
                <div class="slide-status">
                    <i class="bi bi-check-circle-fill"></i>
                    Hoàn tất
                </div>
            </div>
        `;

        // Trigger animation
        placeholder.style.transform = 'scale(1.05)';
        setTimeout(() => {
            placeholder.style.transform = 'scale(1)';
        }, 200);

        // Scroll to show the completed slide
        placeholder.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 300);
}

function addSlidePreview(slideData) {
    const slidesGrid = document.getElementById('slidesGrid');
    if (!slidesGrid) return;

    console.log('➕ Adding slide preview:', slideData);

    // Build iframe URL
    let iframeUrl = '';
    if (slideData.is_temp && slideData.html_path) {
        // Use temp file API for real-time streaming with query parameter
        iframeUrl = `${config.BACKEND_URL}/api/temp-file?path=${encodeURIComponent(slideData.html_path)}`;
        console.log('📄 Creating iframe from temp:', slideData.html_path);
        console.log('🔗 Iframe URL:', iframeUrl);
    } else {
        // Use static output folder
        const htmlFilename = slideData.html_path ? slideData.html_path.split('/').pop() : `slide_${slideData.index + 1}.html`;
        iframeUrl = `${config.BACKEND_URL}/static/output/${projectName}/html/${htmlFilename}`;
        console.log('📄 Creating iframe from output:', htmlFilename);
    }

    // Get display name for logging
    let displayName = `Slide ${slideData.index + 1}`;
    if (slideData.is_temp && slideData.html_path) {
        displayName = slideData.html_path.split('/').pop();
    } else if (slideData.html_path) {
        displayName = slideData.html_path.split('/').pop();
    }

    const slideCard = document.createElement('div');
    slideCard.className = 'slide-card';

    // Calculate stagger delay for animation
    const existingCards = slidesGrid.querySelectorAll('.slide-card').length;
    const staggerDelay = existingCards * 0.1; // 100ms delay between each
    slideCard.style.animationDelay = `${staggerDelay}s`;

    slideCard.innerHTML = `
        <div class="slide-number">Slide ${slideData.index + 1}</div>
        <div class="slide-preview loading" id="preview-${slideData.index}" data-slide-index="${slideData.index}">
            <iframe src="${iframeUrl}" 
                     frameborder="0" 
                     scrolling="no"
                     onload="console.log('✅ Iframe loaded:', '${displayName}'); this.classList.add('loaded'); this.parentElement.classList.remove('loading');"
                     onerror="console.error('❌ Iframe load error:', '${displayName}');"></iframe>
        </div>
        <div class="slide-info">
            <div class="slide-status">
                <i class="bi bi-check-circle-fill"></i>
                Hoàn tất
            </div>
        </div>
    `;

    // Add click handler to open presentation from this slide
    slideCard.addEventListener('click', () => {
        const slideIndex = slides.findIndex(s => s.index === slideData.index);
        if (slideIndex !== -1) {
            startPresentation(slideIndex);
        }
    });
    slideCard.style.cursor = 'pointer';

    slidesGrid.appendChild(slideCard);

    // Notify presentation mode if active
    onNewSlideAdded(slideData);

    // Animate in with slight delay
    setTimeout(() => {
        slideCard.classList.add('show');
    }, 50);

    // Scroll to show the new slide
    setTimeout(() => {
        slideCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100 + (staggerDelay * 1000));
}

function addStatusMessage(message, type = 'info') {
    // Status messages removed from UI
    console.log(`[${type.toUpperCase()}] ${message}`);
}

function showError(message) {
    const errorContainer = document.getElementById('errorContainer');
    const errorMessage = document.getElementById('errorMessage');
    const currentActivity = document.getElementById('currentActivity');

    if (errorContainer && errorMessage) {
        errorMessage.textContent = message;
        errorContainer.style.display = 'flex';
    }

    if (currentActivity) {
        currentActivity.style.display = 'none';
    }
}

async function goToEditor() {
    if (!projectName) {
        showError('Không tìm thấy thông tin project');
        return;
    }

    // Clear streaming state when going to editor
    clearStreamingState();

    // Cleanup temp directory before navigating
    if (tempDirectory) {
        try {
            const response = await fetch(`${config.BACKEND_URL}/api/cleanup-temp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ temp_dir: tempDirectory })
            });
            const result = await response.json();
            console.log('🗑️ Cleanup result:', result);
        } catch (error) {
            console.error('⚠️ Cleanup error:', error);
        }
    }

    // Save to localStorage
    localStorage.setItem('projectName', projectName);
    localStorage.setItem('slidesSource', 'docx-generated');

    // Redirect to editor with project ID
    if (projectId) {
        window.location.href = `edit.html?id=${projectId}&source=generated`;
    } else {
        // Fallback to project name if ID not available
        window.location.href = `edit.html?project=${encodeURIComponent(projectName)}&source=generated`;
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', function () {
    if (eventSource) {
        eventSource.close();
    }
});

// ================== PRESENTATION MODE ==================

function startPresentation(startIndex = 0) {
    if (slides.length === 0) {
        showToast('❌ Chưa có slide nào để trình chiếu', 'error');
        return;
    }

    isPresentationMode = true;
    currentPresentationIndex = startIndex;

    // Create presentation overlay
    const overlay = document.createElement('div');
    overlay.id = 'presentationOverlay';
    overlay.className = 'presentation-overlay';
    overlay.innerHTML = `
        <div class="presentation-click-zone left" id="presZoneLeft"></div>
        <div class="presentation-click-zone right" id="presZoneRight"></div>
        <div class="presentation-slide-container" id="presSlideContainer"></div>
        <div class="presentation-controls">
            <div style="display: flex; align-items: center; gap: 20px;">
                <button id="prevSlideBtn" title="Previous Slide (←)">◀</button>
                <span class="presentation-counter" id="presCounter">1 / 1</span>
                <button id="nextSlideBtn" title="Next Slide (→)">▶</button>
            </div>
            <button id="exitPresBtn" title="Exit (ESC)">✕</button>
        </div>
        <div class="presentation-timeline" id="presTimeline">
            <div class="timeline-track" id="presTimelineTrack">
                <div class="timeline-progress" id="presProgress"></div>
                <div class="timeline-slides" id="presTimelineSlides"></div>
                <div class="timeline-current-indicator" id="presIndicator"></div>
            </div>
        </div>
        <div class="toast-container" id="presentationToastContainer"></div>
    `;

    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';

    // Request fullscreen
    if (overlay.requestFullscreen) {
        overlay.requestFullscreen();
    } else if (overlay.webkitRequestFullscreen) {
        overlay.webkitRequestFullscreen();
    }

    // Render initial slide
    renderPresentationSlide();

    // Setup controls
    setupPresentationControls();
    setupPresentationTimeline();

    // Show overlay
    setTimeout(() => overlay.classList.add('active'), 10);

    showToast('🎬 Bắt đầu trình chiếu', 'success');
}

function renderPresentationSlide() {
    const slide = slides[currentPresentationIndex];
    if (!slide) return;

    const container = document.getElementById('presSlideContainer');
    if (!container) return;

    // Build iframe URL
    let iframeUrl = '';
    if (slide.is_temp && slide.html_path) {
        iframeUrl = `${config.BACKEND_URL}/api/temp-file?path=${encodeURIComponent(slide.html_path)}`;
    } else {
        const htmlFilename = slide.html_path ? slide.html_path.split('/').pop() : `slide_${slide.index + 1}.html`;
        iframeUrl = `${config.BACKEND_URL}/static/output/${projectName}/html/${htmlFilename}`;
    }

    container.innerHTML = `
        <iframe src="${iframeUrl}" 
                frameborder="0" 
                scrolling="no"
                style="width: 1920px; height: 1080px; border: none; background: white;"></iframe>
    `;

    // Scale to fit
    scalePresentationToFit();

    // Update counter
    const counter = document.getElementById('presCounter');
    if (counter) {
        counter.textContent = `${currentPresentationIndex + 1} / ${slides.length}`;
    }

    // Update button states
    const prevBtn = document.getElementById('prevSlideBtn');
    const nextBtn = document.getElementById('nextSlideBtn');
    if (prevBtn) prevBtn.disabled = currentPresentationIndex === 0;
    if (nextBtn) nextBtn.disabled = currentPresentationIndex === slides.length - 1;

    // Update zones
    const zoneLeft = document.getElementById('presZoneLeft');
    const zoneRight = document.getElementById('presZoneRight');
    if (zoneLeft) {
        zoneLeft.classList.toggle('disabled', currentPresentationIndex === 0);
    }
    if (zoneRight) {
        zoneRight.classList.toggle('disabled', currentPresentationIndex === slides.length - 1);
    }

    updatePresentationTimeline();
}

function scalePresentationToFit() {
    const container = document.getElementById('presSlideContainer');
    if (!container) return;

    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    const scaleX = windowWidth / 1920;
    const scaleY = windowHeight / 1080;
    const scale = Math.min(scaleX, scaleY);

    container.style.transform = `scale(${scale})`;
}

function setupPresentationControls() {
    // Keyboard navigation
    presentationKeyboardHandler = (e) => {
        if (!isPresentationMode) return;

        switch (e.key) {
            case 'ArrowRight':
            case 'ArrowDown':
            case ' ':
            case 'PageDown':
                e.preventDefault();
                nextPresentationSlide();
                break;
            case 'ArrowLeft':
            case 'ArrowUp':
            case 'PageUp':
                e.preventDefault();
                previousPresentationSlide();
                break;
            case 'Escape':
                e.preventDefault();
                exitPresentation();
                break;
            case 'Home':
                e.preventDefault();
                goToPresentationSlide(0);
                break;
            case 'End':
                e.preventDefault();
                goToPresentationSlide(slides.length - 1);
                break;
        }
    };

    document.addEventListener('keydown', presentationKeyboardHandler);

    // Button handlers
    document.getElementById('prevSlideBtn')?.addEventListener('click', previousPresentationSlide);
    document.getElementById('nextSlideBtn')?.addEventListener('click', nextPresentationSlide);
    document.getElementById('exitPresBtn')?.addEventListener('click', exitPresentation);

    // Click zones
    document.getElementById('presZoneLeft')?.addEventListener('click', previousPresentationSlide);
    document.getElementById('presZoneRight')?.addEventListener('click', nextPresentationSlide);

    // Window resize
    window.addEventListener('resize', scalePresentationToFit);

    // Timeline and Controls auto-hide
    let hideTimeout;
    const timeline = document.getElementById('presTimeline');
    const controls = document.querySelector('.presentation-controls');
    const overlay = document.getElementById('presentationOverlay');

    if (overlay && timeline && controls) {
        const showControls = () => {
            timeline.classList.add('show');
            controls.classList.add('show');
            clearTimeout(hideTimeout);
            hideTimeout = setTimeout(() => {
                timeline.classList.remove('show');
                controls.classList.remove('show');
            }, 1500);
        };

        overlay.addEventListener('mousemove', showControls);

        // Show initially
        showControls();
    }
}

function setupPresentationTimeline() {
    const timelineSlides = document.getElementById('presTimelineSlides');
    const timelineTrack = document.getElementById('presTimelineTrack');

    if (!timelineSlides || !timelineTrack) return;

    // Clear existing
    timelineSlides.innerHTML = '';

    // Create markers
    slides.forEach((slide, index) => {
        const marker = document.createElement('div');
        marker.className = 'timeline-slide-marker';
        if (index === currentPresentationIndex) {
            marker.classList.add('active');
        }

        const slideNumber = document.createElement('div');
        slideNumber.className = 'slide-number';
        slideNumber.textContent = `Slide ${index + 1}`;
        marker.appendChild(slideNumber);

        marker.addEventListener('click', () => goToPresentationSlide(index));
        timelineSlides.appendChild(marker);
    });

    // Click on track
    timelineTrack.addEventListener('click', (e) => {
        const rect = timelineTrack.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const percentage = x / rect.width;
        const targetSlide = Math.floor(percentage * slides.length);
        goToPresentationSlide(Math.max(0, Math.min(targetSlide, slides.length - 1)));
    });
}

function updatePresentationTimeline() {
    const progress = document.getElementById('presProgress');
    const indicator = document.getElementById('presIndicator');
    const markers = document.querySelectorAll('.timeline-slide-marker');

    if (progress) {
        const percentage = ((currentPresentationIndex + 1) / slides.length) * 100;
        progress.style.width = percentage + '%';
    }

    if (indicator && slides.length > 1) {
        const slidePercentage = (currentPresentationIndex / (slides.length - 1)) * 100;
        indicator.style.left = slidePercentage + '%';
    }

    markers.forEach((marker, index) => {
        marker.classList.toggle('active', index === currentPresentationIndex);
    });
}

function goToPresentationSlide(index) {
    if (index >= 0 && index < slides.length) {
        currentPresentationIndex = index;
        renderPresentationSlide();
    }
}

function nextPresentationSlide() {
    if (currentPresentationIndex < slides.length - 1) {
        currentPresentationIndex++;
        renderPresentationSlide();
    }
}

function previousPresentationSlide() {
    if (currentPresentationIndex > 0) {
        currentPresentationIndex--;
        renderPresentationSlide();
    }
}

function exitPresentation() {
    isPresentationMode = false;

    // Remove keyboard handler
    if (presentationKeyboardHandler) {
        document.removeEventListener('keydown', presentationKeyboardHandler);
        presentationKeyboardHandler = null;
    }

    // Exit fullscreen
    if (document.fullscreenElement || document.webkitFullscreenElement) {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        }
    }

    // Remove overlay
    const overlay = document.getElementById('presentationOverlay');
    if (overlay) {
        overlay.classList.remove('active');
        setTimeout(() => overlay.remove(), 300);
    }

    document.body.style.overflow = '';
    showToast('👋 Đã thoát chế độ trình chiếu', 'info');
}

// Listen for new slides being added during presentation
function onNewSlideAdded(slideData) {
    // If in presentation mode and new slide added, update timeline
    if (isPresentationMode) {
        setupPresentationTimeline();
        updatePresentationTimeline();

        // Show toast notification
        showToast(`✨ Slide ${slideData.index + 1} vừa được thêm!`, 'info');
    }
}

// ================== TOAST NOTIFICATIONS ==================

function showToast(message, type = 'info') {
    // Use presentation toast container if in presentation mode, otherwise use main container
    let toastContainer = isPresentationMode
        ? document.getElementById('presentationToastContainer')
        : document.getElementById('toastContainer');

    if (!toastContainer) {
        toastContainer = document.getElementById('toastContainer');
    }
    if (!toastContainer) return;

    const icons = {
        success: 'check-circle-fill',
        error: 'x-circle-fill',
        warning: 'exclamation-triangle-fill',
        info: 'info-circle-fill'
    };

    const colors = {
        success: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
        error: 'linear-gradient(135deg, #eb3349 0%, #f45c43 100%)',
        warning: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        info: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    };

    const toast = document.createElement('div');
    toast.className = 'custom-toast';
    toast.style.background = colors[type] || colors.info;

    toast.innerHTML = `
        <i class="bi bi-${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;

    toastContainer.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Remove after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ================== STATE PERSISTENCE ==================

function saveStreamingState(isComplete = false) {
    const state = {
        filename: new URLSearchParams(window.location.search).get('filename'),
        projectName: projectName,
        totalSlides: totalSlides,
        completedSlides: completedSlides,
        slides: slides,
        tempDirectory: tempDirectory,
        isComplete: isComplete,
        timestamp: Date.now()
    };

    try {
        sessionStorage.setItem('streamingState', JSON.stringify(state));
        console.log('💾 Saved streaming state:', state);
    } catch (e) {
        console.error('⚠️ Failed to save state:', e);
    }
}

function restoreStreamingState(filename) {
    try {
        const savedState = sessionStorage.getItem('streamingState');
        if (!savedState) return false;

        const state = JSON.parse(savedState);

        // Check if state is for current file and not too old (within 1 hour)
        const isExpired = (Date.now() - state.timestamp) > 3600000;
        const isSameFile = state.filename === filename;

        if (!isSameFile || isExpired) {
            sessionStorage.removeItem('streamingState');
            return false;
        }

        console.log('🔄 Restoring streaming state:', state);

        // Restore variables
        projectName = state.projectName;
        totalSlides = state.totalSlides;
        completedSlides = state.completedSlides;
        slides = state.slides || [];
        tempDirectory = state.tempDirectory;

        // Update UI
        const slideCountEl = document.getElementById('slideCount');
        const totalCountEl = document.getElementById('totalSlideCount');
        if (slideCountEl) slideCountEl.textContent = completedSlides;
        if (totalCountEl) totalCountEl.textContent = totalSlides;

        // Restore slides in UI
        slides.forEach(slideData => {
            addSlidePreview(slideData);
        });

        if (state.isComplete) {
            // Show completion state
            updateActivity(
                '🎉 Hoàn tất!',
                `Đã tạo thành công ${totalSlides} slide`
            );
            updateProgress(100, 100, 100);
            updateAllStepsComplete();
            document.getElementById('actionButtons').style.display = 'flex';
            document.querySelector('.activity-icon .spinner').style.display = 'none';
            showToast('✅ Đã khôi phục trạng thái hoàn tất', 'success');
        } else {
            // Show incomplete state - don't restart streaming
            const percentage = totalSlides > 0 ? (completedSlides / totalSlides) * 100 : 0;
            updateActivity(
                '⚠️ Đã khôi phục trạng thái',
                `Đã tạo ${completedSlides}/${totalSlides} slide (phiên streaming đã kết thúc)`
            );
            updateProgress(completedSlides, totalSlides, percentage);

            // If we have some slides, show them
            if (completedSlides > 0) {
                showToast(`🔄 Đã khôi phục ${completedSlides} slide`, 'info');
            }

            // Hide spinner since streaming won't continue
            const spinner = document.querySelector('.activity-icon .spinner');
            if (spinner) spinner.style.display = 'none';
        }

        return true;
    } catch (e) {
        console.error('⚠️ Failed to restore state:', e);
        sessionStorage.removeItem('streamingState');
        return false;
    }
}

function clearStreamingState() {
    sessionStorage.removeItem('streamingState');
    console.log('🗑️ Cleared streaming state');
}

// ================== DARK MODE ==================

function toggleDarkMode() {
    const body = document.body;
    body.classList.toggle('dark-mode');

    // Save state to localStorage
    const isDarkMode = body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);

    // Add ripple effect on click
    const toggle = document.querySelector('.theme-toggle');
    if (toggle) {
        toggle.style.transform = 'scale(0.9)';
        setTimeout(() => {
            toggle.style.transform = '';
        }, 150);
    }
}

// Restore dark mode state on page load
(function () {
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
        document.body.classList.add('dark-mode');
    }
})();
