// streaming.js - Handle streaming workflow updates
import { config } from '../config.js';

let eventSource = null;
let projectName = null;
let totalSlides = 0;
let completedSlides = 0;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    initializeParticles();
    
    // Get project info from URL params
    const urlParams = new URLSearchParams(window.location.search);
    const filename = urlParams.get('filename');
    
    if (!filename) {
        showError('Không tìm thấy thông tin file');
        return;
    }
    
    // Extract project name from filename (remove .docx extension)
    projectName = filename.replace(/\.docx$/i, '');
    
    // Start streaming
    startStreaming(filename);
    
    // Setup button handlers
    document.getElementById('goToEditor')?.addEventListener('click', goToEditor);
    document.getElementById('backToHome')?.addEventListener('click', () => {
        window.location.href = 'index.html';
    });
    document.getElementById('retryButton')?.addEventListener('click', () => {
        window.location.href = 'index.html';
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
    
    // Create EventSource for SSE
    const url = `${config.BACKEND_URL}/api/upload-docx-stream?filename=${encodeURIComponent(filename)}`;
    console.log('Connecting to:', url);
    eventSource = new EventSource(url);
    
    eventSource.onopen = function() {
        console.log('✅ EventSource connected successfully');
        showToast('✅ Đã kết nối thành công!', 'success');
    };
    
    eventSource.onerror = function(error) {
        console.error('❌ EventSource error:', error);
        if (eventSource.readyState === EventSource.CLOSED) {
            console.error('Connection was closed');
            showToast('⚠️ Mất kết nối với server', 'error');
        } else if (eventSource.readyState === EventSource.CONNECTING) {
            console.log('🔄 Reconnecting...');
        }
    };
    
    // Handle different event types
    eventSource.addEventListener('status', handleStatusEvent);
    eventSource.addEventListener('progress', handleProgressEvent);
    eventSource.addEventListener('slide_completed', handleSlideCompletedEvent);
    eventSource.addEventListener('complete', handleCompleteEvent);
    eventSource.addEventListener('error_event', handleErrorEvent);
    
    // Also listen for generic message event (fallback)
    eventSource.onmessage = function(event) {
        console.log('Generic message received:', event.data);
    };
    
    eventSource.onerror = function(error) {
        console.error('EventSource error:', error);
        console.error('EventSource readyState:', eventSource.readyState);
        if (eventSource.readyState === EventSource.CLOSED) {
            showToast('❌ Kết nối bị đóng', 'error');
            showError('Mất kết nối với server. Vui lòng thử lại.');
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
    
    completedSlides++;
    
    // Always add new slide directly (no placeholders for real-time streaming)
    addSlidePreview(data);
    
    // Update slide count
    const slideCountEl = document.getElementById('slideCount');
    if (slideCountEl) {
        slideCountEl.textContent = completedSlides;
    }
    
    // Show toast notification
    showToast(
        `✨ Slide ${data.index + 1} hoàn tất: ${data.title || 'Untitled'}`,
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
    totalSlides = data.total_slides;
    tempDirectory = data.temp_dir; // Store for cleanup later
    
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
                <div class="slide-title">${slideData.title || 'Untitled'}</div>
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
            <div class="slide-title">${slideData.title || 'Untitled'}</div>
            <div class="slide-status">
                <i class="bi bi-check-circle-fill"></i>
                Hoàn tất
            </div>
        </div>
    `;
    
    slidesGrid.appendChild(slideCard);
    
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
    
    // Redirect to editor
    window.location.href = `edit.html?project=${encodeURIComponent(projectName)}&source=generated`;
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (eventSource) {
        eventSource.close();
    }
});

// ================== TOAST NOTIFICATIONS ==================

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
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
