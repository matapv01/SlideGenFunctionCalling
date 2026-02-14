// SlideCapture Class
import { config } from '../../config.js';

export // SlideCapture Class - Chụp ảnh slides
        class SlideCapture {
constructor(slideEditor) {
    this.slideEditor = slideEditor;
}

getCurrentSlideHTML() {
    console.log('🔍 SlideCapture.getCurrentSlideHTML() called');
    
    const currentSlide = this.slideEditor.slides[this.slideEditor.currentSlideIndex];
    if (!currentSlide) {
        console.error('❌ No current slide found');
        return null;
    }
    
    console.log('📄 Current slide data:', {
        index: this.slideEditor.currentSlideIndex,
        name: currentSlide.name,
        backgroundColor: currentSlide.backgroundColor,
        contentLength: currentSlide.content?.length || 0
    });
    
    const html = this.createCompleteHTML(currentSlide);
    
    console.log('✅ HTML generated, length:', html?.length || 0);
    
    return html;
}

createCompleteHTML(slide) {
    console.log('🏗️ SlideCapture.createCompleteHTML() called for slide:', slide.name);
    
    const backgroundColor = slide.backgroundColor || 'white';
    const content = slide.content || '';
    
    console.log('🎨 Slide properties:', {
        backgroundColor,
        contentLength: content.length,
        hasContent: !!content
    });

    const html = `<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${slide.name || 'Slide'}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
margin: 0;
padding: 0;
box-sizing: border-box;
        }
        
        body {
margin: 0;
padding: 0;
width: 100vw;
height: 100vh;
overflow: hidden;
display: flex;
justify-content: center;
align-items: center;
background: #f0f4f8;
font-family: 'Inter', Arial, sans-serif;
        }
        
        .slide-container {
position: relative;
width: 1920px;
height: 1080px;
background: ${backgroundColor};
overflow: hidden;
transform-origin: center center;
transform: scale(calc(min(100vw / 1920, 100vh / 1080)));
        }
        
        .element {
position: absolute;
user-select: none;
        }
        
        .element img, .element video {
width: 100%;
height: 100%;
object-fit: cover;
border-radius: inherit;
        }
        
        /* Remove editor-specific styles */
        .resize-handle,
        .connector-control-point,
        .context-menu,
        .properties-panel,
        .smart-guide,
        .distance-indicator {
display: none !important;
        }
        
        .element.selected {
outline: none !important;
box-shadow: none !important;
        }
        
        .element[contenteditable="true"] {
cursor: default !important;
outline: none !important;
        }
        
        .element::after,
        .element::before {
display: none !important;
        }
    </style>
</head>
<body>
    <div class="slide-container">
        ${this.cleanSlideContent(content)}
    </div>
</body>
</html>`;
    
    console.log('📝 Complete HTML generated, length:', html.length);
    return html;
}

cleanSlideContent(content) {
    console.log('🧹 SlideCapture.cleanSlideContent() called');
    console.log('📥 Original content length:', content?.length || 0);
    
    if (!content) {
        console.log('⚠️ No content to clean');
        return '';
    }
    
    // Tạo temporary DOM để xử lý
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = content;

    console.log('🔍 Elements before cleaning:', tempDiv.children.length);

    // Xóa các elements của editor
    const resizeHandles = tempDiv.querySelectorAll('.resize-handle');
    const controlPoints = tempDiv.querySelectorAll('.connector-control-point');
    const smartGuides = tempDiv.querySelectorAll('.smart-guide');
    const distanceIndicators = tempDiv.querySelectorAll('.distance-indicator');
    
    console.log('🗑️ Removing editor elements:', {
        resizeHandles: resizeHandles.length,
        controlPoints: controlPoints.length,
        smartGuides: smartGuides.length,
        distanceIndicators: distanceIndicators.length
    });

    resizeHandles.forEach(el => el.remove());
    controlPoints.forEach(el => el.remove());
    smartGuides.forEach(el => el.remove());
    distanceIndicators.forEach(el => el.remove());
    
    const elements = tempDiv.querySelectorAll('.element');
    console.log('🎨 Processing elements:', elements.length);
    
    elements.forEach((el, index) => {
        console.log(`  Element ${index + 1}:`, {
            tagName: el.tagName,
            className: el.className,
            hasContentEditable: el.hasAttribute('contenteditable'),
            textContent: el.textContent?.substring(0, 50) + '...'
        });
        
        el.removeAttribute('contenteditable');
        el.classList.remove('selected', 'dragging', 'editing', 'hover');
        el.style.outline = 'none';
        el.style.cursor = 'default';
        
        if (el.style.border && el.style.border.includes('dashed')) {
            el.style.border = 'none';
        }
        
        if (el.style.backgroundColor === 'rgba(255, 0, 0, 0.1)') {
            el.style.backgroundColor = '';
        }
    });

    const cleanedContent = tempDiv.innerHTML;
    console.log('✅ Cleaned content length:', cleanedContent.length);
    console.log('📤 Cleaned content preview:', cleanedContent.substring(0, 200) + '...');

    return cleanedContent;
}

async captureCurrentSlide() {
    const slideHTML = this.getCurrentSlideHTML();
    if (!slideHTML) {
        throw new Error('Không thể lấy HTML của slide hiện tại');
    }

    const currentSlide = this.slideEditor.slides[this.slideEditor.currentSlideIndex];
    console.log('📸 Đang chụp slide:', currentSlide.name);

    try {
        const response = await fetch(config.endpoints.captureSlide, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                html_content: slideHTML,
                slide_name: currentSlide.name || 'slide'
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.success) {
            return {
                success: true,
                image_url: result.image_url,
                download_url: result.download_url,
                message: result.message
            };
        } else {
            throw new Error(result.error || 'Unknown error');
        }
    } catch (error) {
        console.error('❌ Lỗi khi chụp slide:', error);
        throw error;
    }
}

async captureAllSlides() {
    const slides = this.slideEditor.slides;
    if (!slides || slides.length === 0) {
        throw new Error('Không có slide nào để chụp');
    }

    console.log(`📸 Đang chuẩn bị chụp ${slides.length} slides...`);

    const slidesData = slides.map((slide, index) => ({
        html_content: this.createCompleteHTML(slide),
        slide_name: slide.name || `slide_${index + 1}`
    }));

    try {
        const response = await fetch(config.endpoints.captureSlidesBatch, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                slides: slidesData
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.success) {
            return {
                success: true,
                download_url: result.download_url,
                message: result.message,
                captured_slides: result.captured_slides,
                filename: result.filename
            };
        } else {
            throw new Error(result.error || 'Unknown error');
        }
    } catch (error) {
        console.error('❌ Lỗi khi chụp tất cả slides:', error);
        throw error;
    }
}

previewSlide(slideIndex = null) {
    const index = slideIndex !== null ? slideIndex : this.slideEditor.currentSlideIndex;
    const slide = this.slideEditor.slides[index];
    
    if (!slide) {
        console.error('Slide không tồn tại');
        return;
    }

    const html = this.createCompleteHTML(slide);
    
    const previewWindow = window.open('', '_blank', 'width=1200,height=800');
    previewWindow.document.write(html);
    previewWindow.document.close();
    previewWindow.document.title = `Preview: ${slide.name}`;
}
        }
