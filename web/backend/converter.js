const puppeteer = require('puppeteer');
const fs = require('fs/promises');
const path = require('path');

async function convertHtmlToAbsolute(inputFilePath, outputFilePath) {
    console.log('[JS] 🚀 Starting advanced conversion process v2 (Block-aware)...');
    // ⚠️ DEV ONLY: --no-sandbox bypasses AppArmor restrictions on Ubuntu 23.10+
    // For production, fix Chrome sandbox properly per Chromium docs
    const browser = await puppeteer.launch({
        headless: "new",
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();

    let inputHeadHtml = '';
    try {
        // Đọc input.html để lấy các thẻ <link rel="stylesheet"> và <style>
        const inputRaw = await fs.readFile(inputFilePath, 'utf8');
        const headMatch = inputRaw.match(/<head[\s\S]*?<\/head>/i);
        if (headMatch) {
            const headContent = headMatch[0];
            // Lấy tất cả <link rel="stylesheet" ...> và <style>...</style>
            const linkAndStyleTags = headContent.match(/<(link[^>]*rel=["']stylesheet["'][^>]*>|style[\s\S]*?<\/style>)/gi);
            if (linkAndStyleTags) {
                inputHeadHtml = linkAndStyleTags.join('\n');
            }
        }
    } catch (e) {
        console.warn('[JS] ⚠️ Không thể lấy font/style từ input:', e);
    }

    try {
        const absoluteInputPath = path.resolve(inputFilePath);

        await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });

        await page.goto(`file://${absoluteInputPath}`, { waitUntil: 'networkidle0' });
        console.log(`[JS] 📁 Page loaded: ${absoluteInputPath}`);

        console.log('[JS] ⏳ Waiting for dynamic content to settle...');
        await page.waitForFunction(() => document.fonts.ready.then(() => true), { timeout: 10000 }).catch(() => console.warn('[JS] ⚠️ Font loading timed out.'));
        console.log('[JS] ✅ Fonts are ready.');

        await page.evaluate(async () => {
            await Promise.all(document.getAnimations().map(anim => anim.finished));
            await new Promise(requestAnimationFrame);
        }).catch(() => console.warn('[JS] ⚠️ Animation waiting failed.'));
        console.log('[JS] ✅ Animations have finished.');

        const pageData = await page.evaluate(() => {
            const stylePropsToCopy = [
                'color', 'background', 'background-color', 'background-image', 'background-size',
                'background-position', 'background-repeat', 'background-attachment', 'background-clip',
                'font-family', 'font-size', 'font-weight', 'font-style', 'line-height',
                'text-align', 'text-decoration', 'text-transform', 'text-shadow', 'letter-spacing', 'word-spacing',
                'border-radius', 'border-image', 'opacity', 'box-shadow', 'filter', 'transform', 'transform-origin',
                'fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin', 'stroke-dasharray',
                'cursor', 'transition', 'user-select', 'pointer-events',
                'list-style-type', 'list-style-position', 'list-style-image', 'clip-path',
                // Bổ sung các thuộc tính quan trọng cho layout và text
                'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
                'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
                'box-sizing', 'line-height', 'letter-spacing', 'text-align', 'vertical-align', 'white-space',
                // ✅ THÊM: Các thuộc tính cho hình ảnh và kích thước
                'width', 'height', 'min-width', 'min-height', 'max-width', 'max-height',
                'object-fit', 'object-position', 'aspect-ratio', 'display'
            ];

            function getVisualStyles(element) {
                const computedStyle = window.getComputedStyle(element);
                let styleString = '';
                const inlineStyle = element.getAttribute('style');
                if (inlineStyle) {
                    styleString += inlineStyle.endsWith(';') ? inlineStyle : inlineStyle + '; ';
                }
                for (const prop of stylePropsToCopy) {
                    if (inlineStyle && inlineStyle.includes(prop + ':')) continue;
                    const value = computedStyle.getPropertyValue(prop);
                    if (value && value !== 'none' && value !== '0px' && value !== 'normal' && value !== 'initial' && value !== 'auto') {
                        styleString += `${prop}: ${value}; `;
                    }
                }
                const borderProps = ['border-top', 'border-right', 'border-bottom', 'border-left'];
                for (const prop of borderProps) {
                    styleString += `${prop}: ${computedStyle.getPropertyValue(prop)}; `;
                }
                return styleString;
            }

            function getImportantAttributes(element) {
                const attributes = {};
                const tagName = element.tagName.toLowerCase();
                const importantAttrs = {
                    'img': ['src', 'alt', 'title', 'loading', 'decoding'], 'a': ['href', 'target', 'title', 'rel'],
                    'input': ['type', 'name', 'value', 'placeholder', 'required', 'disabled', 'readonly', 'checked'],
                    'textarea': ['name', 'placeholder', 'required', 'disabled', 'readonly', 'rows', 'cols'],
                    'button': ['type', 'name', 'disabled'], 'form': ['action', 'method', 'target'], 'iframe': ['src', 'title', 'allowfullscreen'],
                    'video': ['src', 'controls', 'poster'], 'audio': ['src', 'controls'], 'label': ['for']
                };
                const globalAttrs = ['id', 'class', 'title', 'lang', 'data-*'];
                const allAttrs = [...(importantAttrs[tagName] || []), ...globalAttrs];
                allAttrs.forEach(attr => {
                    if (attr === 'data-*') {
                        Array.from(element.attributes).forEach(attribute => {
                            if (attribute.name.startsWith('data-')) attributes[attribute.name] = attribute.value;
                        });
                    } else {
                        const value = element.getAttribute(attr);
                        if (value !== null) attributes[attr] = value;
                    }
                });
                return attributes;
            }

            const isBackgroundLayer = (el, mainContainer) => {
                const tag = el.tagName.toLowerCase();
                let cls = '';
                if (typeof el.className === 'string') {
                    cls = el.className.toLowerCase();
                } else if (el.className && typeof el.className.baseVal === 'string') {
                    cls = el.className.baseVal.toLowerCase();
                }

                return (
                    el === mainContainer ||
                    (tag === 'div' && (cls.includes('background') || cls.includes('bg')))
                );
            };


            const helperFunctions = {
                isOrIsInside: (element, tagNames) => {
                    let current = element;
                    while (current && current !== document.body) {
                        if (tagNames.includes(current.tagName.toLowerCase())) return true;
                        current = current.parentElement;
                    }
                    return false;
                },
                escapeHtml: (content) => {
                    return content
                        .replace(/&/g, '&amp;')
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;')
                        .replace(/"/g, '&quot;')
                        .replace(/'/g, '&#39;');
                }
            };

            const mainContainer = document.body;
            const containerRect = mainContainer.getBoundingClientRect();
            const elements = Array.from(mainContainer.querySelectorAll('*:not(script, style, meta, link, title)'));
            const elementsData = [];
            const processedElements = new Set();

            elements.forEach((el, index) => {
                if (processedElements.has(el)) return;

                const style = window.getComputedStyle(el);
                if (style.visibility === 'hidden' || style.display === 'none' || style.opacity === '0') return;

                const rect = el.getBoundingClientRect();
                if (rect.width === 0 && rect.height === 0) return;

                const tagName = el.tagName.toLowerCase();
                const isComplexBlock = ['ul', 'ol', 'table', 'figure'].includes(tagName);
                let content = '';

                if (isComplexBlock) {
                    content = el.innerHTML;
                    el.querySelectorAll('*').forEach(child => processedElements.add(child));
                } else if (helperFunctions.isOrIsInside(el.parentElement, ['ul', 'ol', 'table', 'figure'])) {
                    return;
                } else if (['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'button'].includes(tagName)) {
                    content = el.innerHTML;
                    el.querySelectorAll('*').forEach(child => processedElements.add(child));
                } else if (['span', 'strong', 'b', 'em', 'i', 'u', 'mark', 'small', 'code', 'sub', 'sup'].includes(tagName)) {
                    // ✅ BỎ QUA inline elements - chúng sẽ được giữ trong innerHTML của parent
                    return;
                } else if (tagName === 'svg') {
                    content = el.outerHTML;
                } else if (['img', 'input', 'br', 'hr', 'iframe', 'video'].includes(tagName)) {
                    content = '';
                } else if (tagName === 'div') {
                    // ✅ DIV: Kiểm tra có text hoặc inline elements không
                    const hasOnlyTextAndInline = Array.from(el.childNodes).every(node => {
                        if (node.nodeType === Node.TEXT_NODE) return true;
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            const childTag = node.tagName.toLowerCase();
                            return ['span', 'strong', 'b', 'em', 'i', 'u', 'mark', 'small', 'code', 'sub', 'sup', 'br'].includes(childTag);
                        }
                        return false;
                    });

                    if (hasOnlyTextAndInline) {
                        // Chỉ có text và inline → lấy innerHTML, mark inline elements
                        content = el.innerHTML;
                        el.querySelectorAll('span, strong, b, em, i, u, mark, small, code, sub, sup').forEach(child => processedElements.add(child));
                    } else {
                        // Có block elements con → không lấy innerHTML, để các con tự xử lý
                        content = '';
                    }
                } else {
                    el.childNodes.forEach(node => {
                        if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                            content += helperFunctions.escapeHtml(node.textContent);
                        }
                    });
                }

                let computedZIndex;
                if (isBackgroundLayer(el, mainContainer)) {
                    computedZIndex = 0; // Nền luôn là thấp nhất
                } else {
                    computedZIndex = 100 + index; // Đảm bảo không trùng, tăng dần theo thứ tự
                }

                // ✅ SPECIAL: Với hình ảnh, tìm container cha có class image-container
                let useRect = { width: rect.width, height: rect.height };
                let useX = rect.left - containerRect.left;
                let useY = rect.top - containerRect.top;

                if (tagName === 'img') {
                    // Tìm container cha có class chứa "image"
                    let parent = el.parentElement;
                    while (parent && parent !== mainContainer) {
                        if (parent.className && parent.className.includes('image-container')) {
                            const parentRect = parent.getBoundingClientRect();
                            useRect = { width: parentRect.width, height: parentRect.height };
                            useX = parentRect.left - containerRect.left;
                            useY = parentRect.top - containerRect.top;
                            break;
                        }
                        parent = parent.parentElement;
                    }
                }

                elementsData.push({
                    tagName: tagName === 'svg' ? 'div' : tagName,
                    rect: useRect,
                    style: getVisualStyles(el),
                    attributes: getImportantAttributes(el),
                    content,
                    index,
                    relativeX: useX,
                    relativeY: useY,
                    zIndex: computedZIndex
                });

                processedElements.add(el);
            });

            // Sau khi thu thập xong elementsData, tự động căn giữa các block text nếu nằm gần giữa một box
            elementsData.forEach((el) => {
                if ([
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'label', 'button', 'a'
                ].includes(el.tagName)) {
                    const parentBox = elementsData.find(box =>
                        ['div', 'section', 'article', 'main'].includes(box.tagName) &&
                        box !== el &&
                        el.relativeX >= box.relativeX &&
                        el.relativeY >= box.relativeY &&
                        el.relativeX + el.rect.width <= box.relativeX + box.rect.width &&
                        el.relativeY + el.rect.height <= box.relativeY + box.rect.height
                    );
                    if (parentBox) {
                        const centerX = parentBox.relativeX + parentBox.rect.width / 2 - el.rect.width / 2;
                        const centerY = parentBox.relativeY + parentBox.rect.height / 2 - el.rect.height / 2;
                        if (Math.abs(el.relativeX - centerX) < 20 && Math.abs(el.relativeY - centerY) < 20) {
                            el.relativeX = centerX;
                            el.relativeY = centerY;
                        }
                    }
                }
            });

            // ✅ TRÍCH XUẤT STYLE TỪ CONTAINER VÀ MERGE VÀO BODY
            let containerStyles = { background: '', padding: { top: 0, right: 0, bottom: 0, left: 0 }, borderRadius: '', boxShadow: '' };

            // Bước 1: Tìm các div con có background (như top-panel, bottom-panel)
            const divsWithBackground = [];
            elementsData.forEach(el => {
                if (el.tagName === 'div') {
                    const style = el.style.toLowerCase();
                    const hasBackground =
                        (style.includes('background-color') && !style.includes('background-color: rgba(0, 0, 0, 0)') && !style.includes('background-color: transparent')) ||
                        (style.includes('background-image') && !style.includes('background-image: none')) ||
                        (style.includes('background:') && !style.includes('background: none') && !style.includes('background: rgba(0, 0, 0, 0)'));

                    if (hasBackground) {
                        divsWithBackground.push(el);
                    }
                }
            });

            // Bước 2: Phân loại container và trích xuất style
            let shouldRemoveContainer = false;

            elementsData.forEach((el, idx) => {
                if (el.tagName === 'div') {
                    const isFullScreenContainer =
                        (el.rect.width >= 1900 && el.rect.height >= 1000) ||
                        (el.relativeX <= 10 && el.relativeY <= 10 && el.rect.width >= containerRect.width * 0.95);

                    if (isFullScreenContainer) {
                        // Kiểm tra xem container có chứa child panels với background không
                        const hasChildPanelsWithBg = divsWithBackground.some(child => {
                            return child !== el && // Không phải chính nó
                                child.relativeX >= el.relativeX &&
                                child.relativeY >= el.relativeY &&
                                child.relativeX + child.rect.width <= el.relativeX + el.rect.width + 50 && // +50 tolerance
                                child.relativeY + child.rect.height <= el.relativeY + el.rect.height + 50;
                        });

                        // ✅ THÊM: Kiểm tra pseudo-elements (::before, ::after)
                        const realElement = elements[idx];
                        let hasPseudoElementsWithBg = false;
                        if (realElement) {
                            const beforeStyle = window.getComputedStyle(realElement, '::before');
                            const afterStyle = window.getComputedStyle(realElement, '::after');

                            const checkPseudoBg = (pseudoStyle) => {
                                if (!pseudoStyle) return false;
                                const bgColor = pseudoStyle.backgroundColor;
                                const bgImage = pseudoStyle.backgroundImage;
                                return (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') ||
                                    (bgImage && bgImage !== 'none');
                            };

                            hasPseudoElementsWithBg = checkPseudoBg(beforeStyle) || checkPseudoBg(afterStyle);
                        }

                        if (!hasChildPanelsWithBg && !hasPseudoElementsWithBg) {
                            // TRƯỜNG HỢP 1: Container có background đơn giản, không có child panels màu, không có pseudo-elements
                            // → Trích xuất background và đánh dấu để loại bỏ
                            shouldRemoveContainer = true;

                            const style = el.style;

                            // Trích xuất background-color
                            const bgColorMatch = style.match(/background-color:\s*(rgb\([^)]+\)|rgba\([^)]+\)|#[a-fA-F0-9]{3,8}|[a-z]+)/i);
                            if (bgColorMatch) containerStyles.background = bgColorMatch[1];

                            // Trích xuất background-image nếu có
                            const bgImageMatch = style.match(/background-image:\s*([^;]+)/i);
                            if (bgImageMatch && !bgImageMatch[1].includes('none')) {
                                containerStyles.background = bgImageMatch[1];
                            }

                            // Trích xuất padding
                            const paddingMatch = style.match(/padding:\s*([\d.]+)px\s+([\d.]+)px\s+([\d.]+)px\s+([\d.]+)px/i);
                            if (paddingMatch) {
                                containerStyles.padding = {
                                    top: parseFloat(paddingMatch[1]),
                                    right: parseFloat(paddingMatch[2]),
                                    bottom: parseFloat(paddingMatch[3]),
                                    left: parseFloat(paddingMatch[4])
                                };
                            }

                            // Trích xuất border-radius
                            const borderRadiusMatch = style.match(/border-radius:\s*([^;]+)/i);
                            if (borderRadiusMatch) containerStyles.borderRadius = borderRadiusMatch[1];

                            // Trích xuất box-shadow
                            const boxShadowMatch = style.match(/box-shadow:\s*([^;]+)/i);
                            if (boxShadowMatch && !boxShadowMatch[1].includes('none')) {
                                containerStyles.boxShadow = boxShadowMatch[1];
                            }
                        }
                        // else: TRƯỜNG HỢP 2 - Container có child panels màu → Giữ lại container
                    }
                }
            });

            // ✅ LỌC BỎ các div rỗng/trong suốt không có nội dung
            const filteredElements = elementsData.filter(el => {
                // Giữ lại tất cả các thẻ không phải div
                if (el.tagName !== 'div') return true;

                // ❌ BỎ QUA các container chính (full-screen divs) - CHỈ nếu shouldRemoveContainer = true
                const isFullScreenContainer =
                    (el.rect.width >= 1900 && el.rect.height >= 1000) || // Gần full viewport
                    (el.relativeX <= 10 && el.relativeY <= 10 && el.rect.width >= containerRect.width * 0.95); // Bắt đầu từ góc và chiếm >95% width

                if (isFullScreenContainer && shouldRemoveContainer) {
                    // Loại bỏ container đơn giản - style đã được trích xuất
                    return false;
                }

                // Kiểm tra div có nội dung không (text hoặc innerHTML)
                const hasContent = el.content && el.content.trim().length > 0;
                if (hasContent) return true;

                // Kiểm tra div có background không (màu sắc hoặc hình ảnh)
                const style = el.style.toLowerCase();
                const hasBackground =
                    (style.includes('background-color') && !style.includes('background-color: rgba(0, 0, 0, 0)') && !style.includes('background-color: transparent')) ||
                    (style.includes('background-image') && !style.includes('background-image: none')) ||
                    (style.includes('background:') && !style.includes('background: none') && !style.includes('background: rgba(0, 0, 0, 0)'));

                if (hasBackground) return true;

                // Kiểm tra div có border không
                const hasBorder =
                    style.includes('border-top:') && !style.includes('border-top: 0px') && !style.includes('border-top: none') ||
                    style.includes('border-right:') && !style.includes('border-right: 0px') && !style.includes('border-right: none') ||
                    style.includes('border-bottom:') && !style.includes('border-bottom: 0px') && !style.includes('border-bottom: none') ||
                    style.includes('border-left:') && !style.includes('border-left: 0px') && !style.includes('border-left: none');

                if (hasBorder) return true;

                // Kiểm tra div có shadow không
                const hasShadow = style.includes('box-shadow') && !style.includes('box-shadow: none');
                if (hasShadow) return true;

                // Nếu không có gì → bỏ qua
                return false;
            });


            const svgDefsHtml = document.querySelector('svg[width="0"][height="0"]')?.outerHTML || '';

            const bodyStyle = window.getComputedStyle(document.body);
            const bg = (bodyStyle.backgroundImage && bodyStyle.backgroundImage !== 'none') ? bodyStyle.background : bodyStyle.backgroundColor;

            // THÊM svgDefsHtml VÀ containerStyles VÀO ĐỐI TƯỢNG TRẢ VỀ
            return {
                svgDefsHtml: svgDefsHtml,
                bodyBg: bg,
                containerStyles: containerStyles, // ✅ Style từ container
                contentBlock: {
                    width: containerRect.width,
                    height: containerRect.height
                },
                elements: filteredElements  // ✅ Trả về danh sách đã lọc
            };
        });

        if (!pageData || pageData.elements.length === 0) {
            throw new Error("No visible elements were found.");
        }

        console.log(`[JS] ✅ Browser-side processing complete. Analyzed ${pageData.elements.length} final elements.`);

        // ✅ Áp dụng background từ container (nếu có) vào body
        const finalBodyBg = pageData.containerStyles.background || pageData.bodyBg;
        const bodyPadding = pageData.containerStyles.padding;
        const bodyBorderRadius = pageData.containerStyles.borderRadius;
        const bodyBoxShadow = pageData.containerStyles.boxShadow;

        let newHtmlContent = `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Converted HTML</title>${inputHeadHtml}<style>
*{box-sizing:border-box;}
html { width: 1920px; height: 1080px; }
body {
  margin: 0;
  padding: 2rem;
  background: ${finalBodyBg};
  overflow: auto;
  ${bodyBorderRadius ? `border-radius: ${bodyBorderRadius};` : ''}
  ${bodyBoxShadow ? `box-shadow: ${bodyBoxShadow};` : ''}
  /* KHÔNG đặt width/height cho body */
}
.outer-wrapper{padding:0;box-sizing:border-box;width:1920px;height:1080px;overflow:hidden;}
.content-wrapper{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) scale(var(--scale,1));transform-origin:center center;width:${pageData.contentBlock.width}px;height:${pageData.contentBlock.height}px;overflow:visible;background:inherit;box-sizing:border-box;}
</style></head><body>${pageData.svgDefsHtml}<div class="outer-wrapper"><div class="content-wrapper">
`;
        pageData.elements.sort((a, b) => a.index - b.index).forEach(data => {
            const styleContent = data.style.replace(/z-index\s*:\s*[^;]+;?/g, '').replace(/'/g, '&#39;');

            // ✅ Điều chỉnh vị trí dựa trên padding của container
            const adjustedX = data.relativeX - bodyPadding.left;
            const adjustedY = data.relativeY - bodyPadding.top;

            // ✅ SPECIAL FIX: Xử lý đặc biệt cho hình ảnh với kích thước container cha  
            let finalStyle;
            if (data.tagName === 'img') {
                // Loại bỏ các thuộc tính width/height cũ và làm clean CSS
                let cleanStyleContent = styleContent
                    .replace(/\bwidth\s*:\s*[^;]+;?\s*/gi, '')
                    .replace(/\bheight\s*:\s*[^;]+;?\s*/gi, '')
                    .replace(/\bobject-fit\s*:\s*[^;]+;?\s*/gi, '')
                    .replace(/stroke-\s*/gi, 'stroke-width: 1px; stroke-') // Sửa lỗi stroke- thiếu width
                    .replace(/;\s*;/g, ';') // Loại bỏ dấu ; thừa
                    .replace(/^\s*;|;\s*$/g, '') // Loại bỏ ; ở đầu/cuối
                    .trim();

                // Đảm bảo có dấu ; cuối nếu cần
                if (cleanStyleContent && !cleanStyleContent.endsWith(';')) {
                    cleanStyleContent += ';';
                }

                finalStyle = `position:absolute;z-index:${data.zIndex};left:${adjustedX}px;top:${adjustedY}px;width:${data.rect.width}px;height:${data.rect.height}px;object-fit:cover!important;box-sizing:border-box;${cleanStyleContent}`;
            } else {
                finalStyle = `position:absolute;z-index:${data.zIndex};left:${adjustedX}px;top:${adjustedY}px;width:${data.rect.width}px;height:${data.rect.height}px;box-sizing:border-box;${styleContent}`;
            }

            let attributesString = '';
            for (const attr in data.attributes) {
                const value = String(data.attributes[attr]).replace(/"/g, '&quot;');
                attributesString += ` ${attr}="${value}"`;
            }
            const selfClosingTags = ['img', 'input', 'br', 'hr', 'iframe'];
            if (selfClosingTags.includes(data.tagName)) {
                newHtmlContent += `    <${data.tagName} style='${finalStyle}'${attributesString}>\n`;
            } else {
                newHtmlContent += `    <${data.tagName} style='${finalStyle}'${attributesString}>${data.content}</${data.tagName}>\n`;
            }
        });

        newHtmlContent += `</div><script>
(function() {
  function resizeContent() {
    var wrapper = document.querySelector('.content-wrapper');
    if (!wrapper) return;
    var ww = window.innerWidth, wh = window.innerHeight;
    var cw = wrapper.offsetWidth, ch = wrapper.offsetHeight;
    var scale = Math.min(ww / cw, wh / ch);
    wrapper.style.setProperty('--scale', scale);
  }
  window.addEventListener('resize', resizeContent);
  window.addEventListener('DOMContentLoaded', resizeContent);
})();
</script></body></html>`;
        await fs.writeFile(outputFilePath, newHtmlContent);
        console.log(`[JS] ✨ Success! Output saved to: ${outputFilePath}`);

    } catch (error) {
        console.error('[JS] ❌ An error occurred during conversion:', error);
        process.exit(1);
    } finally {
        await browser.close();
    }
}

if (process.argv.length < 4) {
    console.error('❌ Error: Missing arguments!\nUsage: node your_script.js <input_file.html> <output_file.html>');
    process.exit(1);
}

convertHtmlToAbsolute(process.argv[2], process.argv[3]);
