/**
 * Pixabay Integration Module
 * Handles searching and inserting images from Pixabay
 */

export class PixabayManager {
    constructor(slideEditor) {
        this.slideEditor = slideEditor;
        this.currentPage = 1;
        this.perPage = 6;
        this.totalHits = 0;
        this.lastQuery = '';
        this.lastImageType = '';
        this.lastOrientation = '';
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const searchBtn = document.getElementById('pixabaySearchBtn');
        const searchInput = document.getElementById('pixabaySearchInput');
        const addImageUrlBtn = document.getElementById('addImageUrlBtn');
        const imageUrlInput = document.getElementById('imageUrlInput');

        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.searchImages());
        }

        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchImages();
                }
            });
        }

        // Add image from URL
        if (addImageUrlBtn && imageUrlInput) {
            addImageUrlBtn.addEventListener('click', () => this.addImageFromUrl());
            imageUrlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.addImageFromUrl();
                }
            });
        }
    }

    addImageFromUrl() {
        const imageUrlInput = document.getElementById('imageUrlInput');
        const url = imageUrlInput.value.trim();

        if (!url) {
            this.showMessage('Vui lòng nhập URL ảnh', 'warning');
            return;
        }

        // Validate URL format
        if (!url.startsWith('http://') && !url.startsWith('https://') && !url.startsWith('data:')) {
            this.showMessage('URL không hợp lệ. Vui lòng nhập URL đầy đủ (http:// hoặc https://)', 'error');
            return;
        }

        // Check if it's likely an image URL
        const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'];
        const hasImageExtension = imageExtensions.some(ext => url.toLowerCase().includes(ext));
        
        if (!hasImageExtension && !url.startsWith('data:image/')) {
            const confirm = window.confirm('URL này có thể không phải là ảnh. Bạn có muốn tiếp tục?');
            if (!confirm) return;
        }

        // Create image at default position (200, 200)
        if (this.slideEditor && this.slideEditor.createImageElementFromURL) {
            this.slideEditor.createImageElementFromURL(url, 200, 200);
            this.showMessage('Đã thêm ảnh từ URL!', 'success');
            
            // Clear input
            imageUrlInput.value = '';
        } else {
            this.showMessage('Không thể thêm ảnh. Vui lòng thử lại.', 'error');
        }
    }

    // Detect if text contains Vietnamese characters
    detectVietnamese(text) {
        const vietnamesePattern = /[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i;
        return vietnamesePattern.test(text);
    }

    // Translate Vietnamese to English using Backend API
    async translateToEnglish(text) {
        // Check cache first
        if (this.translationCache && this.translationCache.has(text)) {
            return this.translationCache.get(text);
        }

        try {
            // Use backend translation API
            const apiUrl = `${window.API_BASE_URL || 'http://localhost:12008'}/api/translate?q=${encodeURIComponent(text)}&source=vi&target=en`;
            const response = await fetch(apiUrl);
            const data = await response.json();
            
            if (data.translated && data.translated !== text) {
                // Save to cache
                if (!this.translationCache) {
                    this.translationCache = new Map();
                }
                this.translationCache.set(text, data.translated);
                return data.translated;
            }
            
            return text; // Return original if translation fails
        } catch (error) {
            console.warn('Translation error:', error);
            return text; // Return original on error
        }
    }

    async searchImages(page = 1) {
        const searchInput = document.getElementById('pixabaySearchInput');
        const imageType = document.getElementById('pixabayImageType');
        const orientation = document.getElementById('pixabayOrientation');
        const resultsContainer = document.getElementById('pixabayResults');
        const loadingIndicator = document.getElementById('pixabayLoading');

        let query = searchInput.value.trim();
        if (!query) {
            this.showMessage('Vui lòng nhập từ khóa tìm kiếm', 'warning');
            return;
        }
        
        try {
            // Show loading
            if (loadingIndicator) loadingIndicator.style.display = 'block';
            if (resultsContainer) resultsContainer.style.display = 'none';

            // Auto-translate Vietnamese to English
            if (this.detectVietnamese(query)) {
                const translatedQuery = await this.translateToEnglish(query);
                console.log(`🌐 Đã dịch: "${query}" → "${translatedQuery}"`);
                query = translatedQuery;
            }

            // Store search params
            this.currentPage = page;
            this.lastQuery = query;
            this.lastImageType = imageType.value;
            this.lastOrientation = orientation.value;

            // Call API
            const params = new URLSearchParams({
                q: query,
                image_type: imageType.value,
                orientation: orientation.value,
                per_page: this.perPage,
                page: page
            });

            const apiUrl = `${window.API_BASE_URL || 'http://localhost:12008'}/api/pixabay/search/images?${params}`;
            const response = await fetch(apiUrl);
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();
            
            // Store total hits for pagination
            this.totalHits = data.totalHits || 0;

            // Hide loading
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            if (resultsContainer) resultsContainer.style.display = 'grid';

            // Display results
            this.displayResults(data, resultsContainer);

        } catch (error) {
            console.error('Pixabay search error:', error);
            this.showMessage('Lỗi khi tìm kiếm. Vui lòng thử lại.', 'error');
            
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            if (resultsContainer) resultsContainer.style.display = 'grid';
        }
    }

    displayResults(data, container) {
        if (!data.hits || data.hits.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 40px 20px; color: #a0aec0;">
                    <div style="font-size: 48px; margin-bottom: 12px;">🔍</div>
                    <div style="font-size: 15px; font-weight: 600; color: #4a5568; margin-bottom: 6px;">Không tìm thấy kết quả</div>
                    <div style="font-size: 13px;">Thử từ khóa khác hoặc thay đổi bộ lọc</div>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        data.hits.forEach(image => {
            const imageCard = document.createElement('div');
            imageCard.className = 'pixabay-image-card';
            imageCard.style.cssText = `
                position: relative;
                cursor: pointer;
                border-radius: 12px;
                overflow: hidden;
                background: #f7fafc;
                aspect-ratio: 4/3;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            `;

            imageCard.innerHTML = `
                <img 
                    src="${image.webformatURL}" 
                    alt="${image.tags}"
                    draggable="true"
                    style="width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); user-select: none;"
                    loading="lazy"
                />
                <div class="pixabay-overlay" style="
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    background: linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.3) 70%, transparent 100%);
                    padding: 12px 10px 8px;
                    opacity: 0;
                    transition: opacity 0.3s;
                    pointer-events: none;
                ">
                    <div style="font-size: 11px; color: white; font-weight: 600; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">
                        📸 ${image.user}
                    </div>
                    <div style="font-size: 10px; color: rgba(255,255,255,0.9); margin-top: 3px; display: flex; gap: 8px; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">
                        <span>❤️ ${image.likes}</span>
                        <span>👁️ ${image.views}</span>
                    </div>
                </div>
            `;

            // Hover effects - Canva Style
            imageCard.addEventListener('mouseenter', () => {
                imageCard.style.transform = 'translateY(-4px)';
                imageCard.style.boxShadow = '0 12px 24px rgba(102, 126, 234, 0.25)';
                const overlay = imageCard.querySelector('.pixabay-overlay');
                if (overlay) overlay.style.opacity = '1';
            });

            imageCard.addEventListener('mouseleave', () => {
                imageCard.style.transform = 'translateY(0)';
                imageCard.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
                const overlay = imageCard.querySelector('.pixabay-overlay');
                if (overlay) overlay.style.opacity = '0';
            });

            // Drag and drop support for images
            const imgElement = imageCard.querySelector('img');
            let isDragging = false;
            
            if (imgElement) {
                imgElement.addEventListener('dragstart', (e) => {
                    isDragging = true;
                    e.dataTransfer.effectAllowed = 'copy';
                    e.dataTransfer.setData('text/uri-list', image.webformatURL);
                    e.dataTransfer.setData('text/plain', image.webformatURL);
                    
                    console.log('Pixabay image drag started:', image.webformatURL);
                });

                imgElement.addEventListener('dragend', () => {
                    setTimeout(() => {
                        isDragging = false;
                    }, 100);
                });
            }

            // Click to insert image (only if not dragging)
            imageCard.addEventListener('click', () => {
                if (!isDragging) {
                    this.insertImageToCanvas(image);
                }
            });

            container.appendChild(imageCard);
        });

        // Add pagination controls
        this.addPaginationControls(container);

        // Show attribution message
        const attribution = document.createElement('div');
        attribution.style.cssText = `
            grid-column: 1 / -1;
            text-align: center;
            padding: 10px;
            font-size: 11px;
            color: #718096;
            border-top: 1px solid #e2e8f0;
            margin-top: 8px;
        `;
        attribution.innerHTML = `
            <a href="https://pixabay.com/" target="_blank" style="color: #667eea; text-decoration: none;">
                Images from Pixabay
            </a>
        `;
        container.appendChild(attribution);
    }

    addPaginationControls(container) {
        const totalPages = Math.ceil(this.totalHits / this.perPage);
        
        if (totalPages <= 1) return; // No pagination needed
        
        const paginationDiv = document.createElement('div');
        paginationDiv.style.cssText = `
            grid-column: 1 / -1;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            padding: 15px 10px;
            border-top: 1px solid #e2e8f0;
            margin-top: 10px;
        `;
        
        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '← Trước';
        prevBtn.disabled = this.currentPage === 1;
        prevBtn.style.cssText = `
            padding: 8px 16px;
            background: ${this.currentPage === 1 ? '#e2e8f0' : '#667eea'};
            color: ${this.currentPage === 1 ? '#a0aec0' : 'white'};
            border: none;
            border-radius: 6px;
            cursor: ${this.currentPage === 1 ? 'not-allowed' : 'pointer'};
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
        `;
        if (this.currentPage > 1) {
            prevBtn.addEventListener('mouseenter', () => prevBtn.style.background = '#5568d3');
            prevBtn.addEventListener('mouseleave', () => prevBtn.style.background = '#667eea');
            prevBtn.addEventListener('click', () => this.searchImages(this.currentPage - 1));
        }
        
        // Page info
        const pageInfo = document.createElement('span');
        pageInfo.textContent = `Trang ${this.currentPage} / ${totalPages}`;
        pageInfo.style.cssText = `
            font-size: 13px;
            color: #4a5568;
            font-weight: 500;
            min-width: 100px;
            text-align: center;
        `;
        
        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Tiếp →';
        nextBtn.disabled = this.currentPage >= totalPages;
        nextBtn.style.cssText = `
            padding: 8px 16px;
            background: ${this.currentPage >= totalPages ? '#e2e8f0' : '#667eea'};
            color: ${this.currentPage >= totalPages ? '#a0aec0' : 'white'};
            border: none;
            border-radius: 6px;
            cursor: ${this.currentPage >= totalPages ? 'not-allowed' : 'pointer'};
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
        `;
        if (this.currentPage < totalPages) {
            nextBtn.addEventListener('mouseenter', () => nextBtn.style.background = '#5568d3');
            nextBtn.addEventListener('mouseleave', () => nextBtn.style.background = '#667eea');
            nextBtn.addEventListener('click', () => this.searchImages(this.currentPage + 1));
        }
        
        paginationDiv.appendChild(prevBtn);
        paginationDiv.appendChild(pageInfo);
        paginationDiv.appendChild(nextBtn);
        container.appendChild(paginationDiv);
    }

    async insertImageToCanvas(imageData) {
        try {
            // Use largeImageURL for better quality
            const imageUrl = imageData.largeImageURL || imageData.webformatURL;
            
            // Show loading notification
            this.showMessage('Đang tải hình ảnh...', 'info');

            // Check if slideEditor and canvas are available
            if (!this.slideEditor || !this.slideEditor.canvas) {
                console.error('SlideEditor or canvas not available');
                this.showMessage('Lỗi: Editor chưa sẵn sàng', 'error');
                return;
            }

            // Create image element to get dimensions
            const img = new Image();
            img.crossOrigin = 'anonymous';
            
            await new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = reject;
                img.src = imageUrl;
            });

            // Calculate size to fit in canvas (max 800x600)
            let width = img.width;
            let height = img.height;
            const maxWidth = 800;
            const maxHeight = 600;
            
            if (width > maxWidth) {
                height = (height * maxWidth) / width;
                width = maxWidth;
            }
            if (height > maxHeight) {
                width = (width * maxHeight) / height;
                height = maxHeight;
            }

            // Create element container following SlideEditor pattern
            const el = document.createElement('div');
            el.className = 'element';
            el.dataset.type = 'image';
            el.id = `element_pixabay_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            el.style.position = 'absolute';
            el.style.left = '200px';
            el.style.top = '200px';
            el.style.width = width + 'px';
            el.style.height = height + 'px';
            el.style.zIndex = this.slideEditor.zIndexCounter++;
            el.style.borderRadius = '12px';
            
            // Store Pixabay metadata
            el.dataset.pixabayId = imageData.id;
            el.dataset.pixabayUser = imageData.user;
            el.dataset.pixabayUrl = imageData.pageURL;
            
            // Create img element
            const imgElement = document.createElement('img');
            imgElement.src = imageUrl;
            imgElement.style.width = '100%';
            imgElement.style.height = '100%';
            imgElement.style.objectFit = 'cover';
            imgElement.style.borderRadius = '12px';
            el.appendChild(imgElement);
            
            // Add to canvas
            this.slideEditor.canvas.appendChild(el);
            
            // Make interactive, select, and save state (following SlideEditor pattern)
            if (this.slideEditor.makeElementInteractive) {
                this.slideEditor.makeElementInteractive(el);
            }
            if (this.slideEditor.selectElement) {
                this.slideEditor.selectElement(el);
            }
            if (this.slideEditor.saveState) {
                this.slideEditor.saveState();
            }
            
            console.log('Image added to canvas successfully');
            this.showMessage('Đã thêm hình ảnh vào slide', 'success');

        } catch (error) {
            console.error('Error inserting Pixabay image:', error);
            this.showMessage('Lỗi khi tải hình ảnh. Vui lòng thử lại.', 'error');
        }
    }

    showMessage(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#48bb78' : type === 'error' ? '#f56565' : type === 'warning' ? '#ed8936' : '#4299e1'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
