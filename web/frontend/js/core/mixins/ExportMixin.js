/**
 * ExportMixin.js
 * Handles HTML export functionality for slides
 * Supports both responsive and fixed-size export modes
 */

export const ExportMixin = {
    /**
     * Display export options modal
     */
    showExportOptions() {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;

        const dialog = document.createElement('div');
        dialog.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 30px;
            max-width: 500px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        `;

        dialog.innerHTML = `
            <h2 style="margin: 0 0 20px; color: #2d3748;">Xuất HTML</h2>
            <p style="margin: 0 0 20px; color: #4a5568;">Chọn kiểu xuất HTML:</p>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <button data-type="responsive" style="text-align: left; padding: 15px; border: 1px solid #e2e8f0; border-radius: 8px; background: white; cursor: pointer;">
                    <div style="font-weight: 600; color: #2d3748;">🖥️ Responsive</div>
                    <div style="font-size: 14px; color: #718096;">Tự động điều chỉnh kích thước theo màn hình</div>
                </button>
                <button data-type="fixed" style="text-align: left; padding: 15px; border: 1px solid #e2e8f0; border-radius: 8px; background: white; cursor: pointer;">
                    <div style="font-weight: 600; color: #2d3748;">📏 Giữ nguyên kích thước</div>
                    <div style="font-size: 14px; color: #718096;">Giữ đúng kích thước và tỉ lệ gốc</div>
                </button>
            </div>
            <div style="margin-top: 20px; text-align: right;">
                <button id="cancelExport" style="padding: 8px 16px; border: none; background: #e2e8f0; border-radius: 6px; margin-right: 10px; cursor: pointer;">Hủy</button>
            </div>
        `;

        modal.appendChild(dialog);
        document.body.appendChild(modal);

        // Add event listeners for buttons
        dialog.querySelectorAll('button[data-type]').forEach(button => {
            button.addEventListener('mouseenter', () => {
                button.style.borderColor = '#667eea';
                button.style.backgroundColor = '#f7fafc';
            });
            button.addEventListener('mouseleave', () => {
                button.style.borderColor = '#e2e8f0';
                button.style.backgroundColor = 'white';
            });
            button.addEventListener('click', () => {
                const type = button.dataset.type;
                document.body.removeChild(modal);
                this.exportHTML(type);
            });
        });

        document.getElementById('cancelExport').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    },

    /**
     * Export slides as HTML files
     * @param {string} type - Export type: 'responsive' or 'fixed'
     */
    exportHTML(type) {
        if (this.slides.length === 0) {
            alert('Không có slide nào để xuất!');
            return;
        }

        // Single slide: export directly as HTML file
        if (this.slides.length === 1) {
            const htmlContent = this.createSlideHTML(this.slides[0], type);
            const blob = new Blob([htmlContent], { type: 'text/html' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'slide.html';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);
            return;
        }

        // Multiple slides: export as ZIP
        try {
            const zip = new JSZip();

            // Create HTML content for each slide
            this.slides.forEach((slide, index) => {
                const slideNumber = (index + 1).toString().padStart(3, '0');
                const fileName = `slide_${slideNumber}.html`;
                const htmlContent = this.createSlideHTML(slide, type);
                zip.file(fileName, htmlContent);
            });

            // Create index.html
            const indexContent = this.createIndexHTML(type);
            zip.file('index.html', indexContent);

            // Generate and download ZIP
            zip.generateAsync({ type: "blob" }).then((content) => {
                const link = document.createElement('a');
                link.href = URL.createObjectURL(content);
                link.download = 'slides.zip';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(link.href);
            });

        } catch (error) {
            console.error("Error exporting slides:", error);
            alert("Có lỗi xảy ra khi xuất slides!");
        }
    },

    /**
     * Create HTML content for a single slide
     * @param {Object} slide - Slide data
     * @param {string} type - Export type: 'responsive' or 'fixed'
     * @returns {string} HTML content
     */
    createSlideHTML(slide, type) {
        const originalWidth = 1920;
        const originalHeight = 1080;

        const template = `<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${slide.name || 'Slide'}</title>
    <style>
        body {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f0f4f8;
            font-family: 'Inter', Arial, sans-serif;
        }
        .slide-container {
            position: relative;
            width: ${originalWidth}px;
            height: ${originalHeight}px;
            background: ${slide.backgroundColor || 'white'};
            ${type === 'responsive' ? `
            transform-origin: top left;
            transform: scale(calc(min(100vw / ${originalWidth}, 100vh / ${originalHeight})));
            margin: auto;` : ''}
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
    </style>
</head>
<body>
    <div class="slide-container">
        ${this.prepareSlideContent(slide.content)}
    </div>
</body>
</html>`;

        return template;
    },

    /**
     * Create index.html with list of all slides
     * @param {string} type - Export type: 'responsive' or 'fixed'
     * @returns {string} HTML content
     */
    createIndexHTML(type) {
        return `<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Danh sách Slides</title>
    <style>
        body {
            margin: 0;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Inter', Arial, sans-serif;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 40px;
        }
        .slides-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .slide-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
        }
        .slide-card:hover {
            transform: translateY(-5px);
        }
        .slide-title {
            font-size: 18px;
            margin-bottom: 15px;
            color: #2d3748;
        }
        .slide-link {
            display: inline-block;
            padding: 8px 16px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            transition: opacity 0.3s;
        }
        .slide-link:hover {
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Danh sách Slides</h1>
        <div class="slides-grid">
${this.slides.map((slide, index) => {
            const slideNumber = (index + 1).toString().padStart(3, '0');
            return `
            <div class="slide-card">
                <a href="slide_${slideNumber}.html" class="slide-link" target="_blank">Slide ${index + 1}</a>
            </div>
        `;
        }).join('')}
        </div>
    </div>
</body>
</html>`;
    },

    /**
     * Clean slide content before export
     * Removes editor-specific elements and attributes
     * @param {string} content - HTML content
     * @returns {string} Cleaned HTML content
     */
    prepareSlideContent(content) {
        if (!content) return '';

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;

        // Remove editor-specific elements and classes
        tempDiv.querySelectorAll('.resize-handle').forEach(el => el.remove());
        tempDiv.querySelectorAll('.element').forEach(el => {
            el.removeAttribute('contenteditable');
            el.classList.remove('selected', 'dragging');
            el.style.outline = 'none';
            el.style.cursor = 'default';
        });

        return tempDiv.innerHTML;
    }
};
