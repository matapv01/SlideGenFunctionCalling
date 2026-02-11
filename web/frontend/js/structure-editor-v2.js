// structure-editor-v2.js - Word-like Editor with Formatting Toolbar

// ========== GLOBAL STATE ==========
let documentText = "";
let documentStructure = []; // Backend format: {level, title, content, children}
let sessionId = null;
let introSlide = null;
const API_BASE_URL = window.config?.API_BASE_URL || 'http://localhost:12008';

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', function () {
    const urlParams = new URLSearchParams(window.location.search);
    sessionId = urlParams.get('session');

    if (!sessionId) {
        alert('No session ID provided');
        goBack();
        return;
    }

    loadDocumentData();
    // setupEditorListeners will be called after data loads successfully
});

// Setup editor event listeners
function setupEditorListeners() {
    const editor = document.getElementById('wordEditor');

    // Listen for text selection
    editor.addEventListener('mouseup', handleTextSelection);
    editor.addEventListener('keyup', handleTextSelection);

    // Listen for content changes
    editor.addEventListener('input', debounce(handleContentChange, 500));

    // Prevent dragging text blocks unless using the handle
    editor.addEventListener('dragstart', function (e) {
        if (!e.target.closest('.drag-handle')) {
            e.preventDefault();
        }
    });

    // Setup drag-drop for text blocks
    setupDragDrop();

    // Handle Enter key to break out of text blocks
    editor.addEventListener('keydown', handleEnterKey);
}

function handleEnterKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        const selection = window.getSelection();
        if (!selection.rangeCount) return;

        const range = selection.getRangeAt(0);
        let node = range.commonAncestorContainer;
        if (node.nodeType === 3) node = node.parentElement; // Text node -> Element

        const block = node.closest('.text-block');

        if (block) {
            e.preventDefault();

            // Create new line (standard contenteditable behavior is often div or br)
            // We use a div to ensure a clean new line context
            const newLine = document.createElement('div');
            newLine.innerHTML = '<br>';

            // Insert after the current block
            if (block.nextSibling) {
                block.parentNode.insertBefore(newLine, block.nextSibling);
            } else {
                block.parentNode.appendChild(newLine);
            }

            // Move cursor to the new line
            const newRange = document.createRange();
            newRange.setStart(newLine, 0);
            newRange.collapse(true);
            selection.removeAllRanges();
            selection.addRange(newRange);
        }
    }
}

// Debounce helper
function debounce(func, wait) {
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

// ========== LOAD DATA ==========
async function loadDocumentData() {
    console.log('🔄 loadDocumentData called with sessionId:', sessionId);
    console.log('🔗 API URL:', `${API_BASE_URL}/api/structure/current?session_id=${sessionId}`);

    try {
        const url = `${API_BASE_URL}/api/structure/current?session_id=${sessionId}`;
        console.log('📡 Fetching:', url);

        const response = await fetch(url);
        console.log('📥 Response status:', response.status, response.statusText);

        if (!response.ok) {
            console.error('API response not OK:', response.status, response.statusText);
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Loaded data:', data);

        if (data.document_text) {
            documentText = data.document_text;
            document.getElementById('documentTitle').textContent = data.document_title || 'Untitled Document';

            // Render text in editor
            const editor = document.getElementById('wordEditor');

            // If we have existing structure, render with formatting
            if (data.document_structure && data.document_structure.length > 0) {
                renderExistingStructure(data.document_structure);
            } else {
                // Plain text
                editor.innerHTML = escapeHtml(documentText);
            }

            // Setup listeners AFTER content is loaded
            setupEditorListeners();

            updateStats();
            syncEditorToStructure();
            renderSlides();
        } else {
            console.error('No document_text in response:', data);
            throw new Error('No document data received');
        }
    } catch (error) {
        console.error('Error loading document:', error);
        alert('Failed to load document. Please try again.');
        goBack();
    }
}

// Render existing structure with formatting
function renderExistingStructure(structure) {
    const editor = document.getElementById('wordEditor');
    let html = '';

    function renderNodes(nodes) {
        let result = '';
        for (const node of nodes) {
            // Render title if exists
            if (node.title) {
                result += `<span class="text-block text-level-${node.level} text-title" 
                    data-level="${node.level}" 
                    data-type="title" 
                    data-node-id="${node.node_id || generateNodeId()}"
                    ${node.is_transition ? 'data-transition="true"' : ''}><span class="drag-handle" contenteditable="false"><i class="bi bi-grip-vertical"></i></span>${escapeHtml(node.title)}</span>\n`;
            }

            // Render content if exists
            if (node.content) {
                result += `<span class="text-block text-level-${node.level} text-content" 
                    data-level="${node.level}" 
                    data-type="content" 
                    data-node-id="${(node.node_id || generateNodeId()) + '_c'}"><span class="drag-handle" contenteditable="false"><i class="bi bi-grip-vertical"></i></span>${escapeHtml(node.content)}</span>\n`;
            }

            // Render children
            if (node.children && node.children.length > 0) {
                result += renderNodes(node.children);
            }
        }
        return result;
    }

    html = renderNodes(structure);

    // Add remaining unformatted text if any
    editor.innerHTML = html || escapeHtml(documentText);
}

// ========== TEXT SELECTION HANDLING ==========
function handleTextSelection() {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();
    const selectionInfo = document.getElementById('selectionInfo');
    const selectionTextEl = document.getElementById('selectionText');
    const selectionLengthEl = document.getElementById('selectionLength');

    if (selectedText.length > 0) {
        selectionInfo.classList.add('visible');
        selectionTextEl.textContent = selectedText.length > 80
            ? selectedText.substring(0, 80) + '...'
            : selectedText;
        selectionLengthEl.textContent = selectedText.length + ' chars';
    } else {
        selectionInfo.classList.remove('visible');
    }
}

// Handle click on text block
function handleBlockClick(event) {
    const block = event.target.closest('.text-block');

    // Remove selection from all blocks
    document.querySelectorAll('.text-block.selected').forEach(b => b.classList.remove('selected'));

    if (block) {
        block.classList.add('selected');

        // Update toolbar to match block's properties
        const level = block.dataset.level;
        const type = block.dataset.type;

        document.getElementById('toolbarLevel').value = level;
        document.getElementById('toolbarType').value = type;
    }
}

// ========== FORMATTING FUNCTIONS ==========

// Global state for 2-step formatting
let pendingLevel = null;
let pendingType = null;

// Apply formatting to selected text
function applyFormatting(newLevel, newType) {
    const selection = window.getSelection();

    // Get existing block context
    let existingBlock = null;
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        existingBlock = range.commonAncestorContainer.closest?.('.text-block')
            || range.commonAncestorContainer.parentElement?.closest('.text-block');
    }

    // CASE 1: EDITING EXISTING BLOCK (Immediate Effect)
    if (existingBlock) {
        // If Normal/Unformat requested
        if (newLevel === 'normal') {
            unformatBlock(existingBlock);
            clearPendingState();
            return;
        }

        // Apply partial updates immediately
        const level = newLevel !== null ? newLevel : existingBlock.dataset.level;
        const type = newType !== null ? newType : existingBlock.dataset.type;

        updateBlockStyle(existingBlock, level, type);
        clearPendingState(); // Clear any pending state to avoid confusion
        updateToolbarVisuals(level, type);
        return;
    }

    // CASE 2: CREATING NEW BLOCK (Two-Step Process)

    // Update Pending State
    if (newLevel !== null) pendingLevel = newLevel;
    if (newType !== null) pendingType = newType;

    // Handle "Normal" or "Intro" special cases
    if (newLevel === 'normal') {
        // Just clear pending, as we are already in normal text
        clearPendingState();
        updateToolbarVisuals(null, null);
        return; // Already normal
    }
    if (newLevel === 0) {
        // Intro doesn't usually need a type, default to 'title' if not set
        if (!pendingType) pendingType = 'title';
    }

    // Update UI to show what's selected
    updateToolbarVisuals(pendingLevel, pendingType);

    // Check if we have BOTH Level and Type to proceed
    if (pendingLevel !== null && pendingType !== null) {
        createFormattedBlock(pendingLevel, pendingType);

        // Reset pending state after creation? 
        // Or keep it for continuous typing?
        // User request suggests "then create box", implies one-off action.
        // Let's reset to avoid sticking.
        clearPendingState();
        updateToolbarVisuals(null, null);
    }
}

function clearPendingState() {
    pendingLevel = null;
    pendingType = null;
}

function updateToolbarVisuals(level, type) {
    // Remove all active classes
    document.querySelectorAll('.style-card').forEach(btn => btn.classList.remove('active'));

    // Add active class to matching buttons
    if (level !== null && level !== undefined) {
        const levelBtn = document.querySelector(`.style-card[onclick*="applyFormatting(${level},"]`)
            || document.querySelector(`.style-card[onclick*="applyFormatting('${level}',"]`);
        if (levelBtn) levelBtn.classList.add('active');
    }

    if (type !== null && type !== undefined) {
        const typeBtn = document.querySelector(`.style-card[onclick*="applyFormatting(null, '${type}')"]`);
        if (typeBtn) typeBtn.classList.add('active');
    }
}

function unformatBlock(block) {
    // Clone block to get clean text without handle
    const clone = block.cloneNode(true);
    const handle = clone.querySelector('.drag-handle');
    if (handle) handle.remove();

    const text = clone.textContent; // Keep original spacing/newlines
    const textNode = document.createTextNode(text);

    // Check if next sibling is a <br> (added by us) and remove it
    if (block.nextSibling && block.nextSibling.tagName === 'BR') {
        block.nextSibling.remove();
    }

    block.replaceWith(textNode);
    if (textNode.parentElement) textNode.parentElement.normalize();

    // Update everything
    updateStats();
    syncEditorToStructure();
    renderSlides();
    saveStructure();
    console.log('✅ Converted to Normal Text');
}

function updateBlockStyle(block, level, type) {
    block.className = `text-block text-level-${level} text-${type}`;
    block.dataset.level = level;
    block.dataset.type = type;

    updateStats();
    syncEditorToStructure();
    renderSlides();
    saveStructure();
    console.log(`✅ Updated: Level ${level}, Type ${type}`);
}

function createFormattedBlock(level, type) {
    const selection = window.getSelection();
    if (!selection.rangeCount) return;
    const range = selection.getRangeAt(0);
    const nodeId = generateNodeId();

    try {
        // Create wrapper
        const wrapper = document.createElement('span');
        wrapper.className = `text-block text-level-${level} text-${type}`;
        wrapper.dataset.level = level;
        wrapper.dataset.type = type;
        wrapper.dataset.nodeId = nodeId;

        // Extract contents
        const contents = range.extractContents();

        // Add handle
        const handle = document.createElement('span');
        handle.className = 'drag-handle';
        handle.contentEditable = 'false';
        handle.innerHTML = '<i class="bi bi-grip-vertical"></i>';
        wrapper.appendChild(handle);

        wrapper.appendChild(contents);
        range.insertNode(wrapper);

        // Add break
        const br = document.createElement('br');
        wrapper.after(br);

        // Clear selection
        selection.removeAllRanges();

        // Update everything
        updateStats();
        syncEditorToStructure();
        renderSlides();
        saveStructure();
        console.log(`✅ Created: Level ${level}, Type ${type}`);

    } catch (error) {
        console.error('Error applying formatting:', error);
        showAlert('Could not apply formatting.');
    }
}



// Handle content changes
function handleContentChange() {
    updateStats();
    syncEditorToStructure();
    renderSlides();
    saveStructure();
}

// ========== SYNC EDITOR TO STRUCTURE ==========

// Sync editor DOM to documentStructure
function syncEditorToStructure() {
    const editor = document.getElementById('wordEditor');
    const blocks = editor.querySelectorAll('.text-block');

    // Build flat list of blocks (filter empty ones)
    const flatBlocks = [];
    blocks.forEach(block => {
        // Clone block to get text without handle text (if any)
        const clone = block.cloneNode(true);
        const handle = clone.querySelector('.drag-handle');
        if (handle) handle.remove();

        const text = clone.textContent.trim();
        // Skip blocks with empty text
        if (!text) return;

        flatBlocks.push({
            node_id: block.dataset.nodeId || generateNodeId(),
            level: block.dataset.level !== undefined ? parseInt(block.dataset.level) : 1,
            type: block.dataset.type || 'content',
            text: text,
            is_transition: block.dataset.transition === 'true'
        });
    });

    // Convert flat list to hierarchical structure (like backend expects)
    documentStructure = buildHierarchy(flatBlocks);

    // Debug logging
    console.log('📊 Synced structure:', documentStructure.length, 'root nodes');
    console.log('🔍 flatBlocks:', flatBlocks.map(b => ({ level: b.level, type: b.type, text: b.text.substring(0, 30) })));
    console.log('🏗️ documentStructure:', documentStructure.map(n => ({ level: n.level, title: n.title?.substring(0, 30) })));
    console.log('🎬 introSlide:', introSlide ? introSlide.content?.substring(0, 30) : 'null');
}

// Build hierarchy from flat blocks
function buildHierarchy(flatBlocks) {
    // Reset intro slide first
    // (Only set it if we find a level 0 block in this sync)
    const introBlocks = flatBlocks.filter(b => b.level === 0);
    if (introBlocks.length > 0) {
        // Combine all level 0 blocks into one intro slide
        const combinedText = introBlocks.map(b => b.text).join('\n');
        introSlide = {
            id: 'intro_slide_0',
            level: 0,
            title: 'Intro',
            content: combinedText,
            type: 'title',
            children: []
        };
    }
    // Note: Don't reset introSlide to null here - it may have been set via modal

    // Filter out Level 0 (Intro) - handled separately above
    const blocks = flatBlocks.filter(b => b.level > 0);

    const result = [];
    const stack = [{ level: 0, children: result }];

    // Group consecutive title + content at same level
    const grouped = [];
    for (let i = 0; i < blocks.length; i++) {
        const block = blocks[i];

        // Check if next block is content for this title
        if (block.type === 'title' && i + 1 < blocks.length) {
            const next = blocks[i + 1];
            if (next.type === 'content' && next.level === block.level) {
                grouped.push({
                    node_id: block.node_id,
                    level: block.level,
                    title: block.text,
                    content: next.text,
                    children: [],
                    is_transition: block.is_transition
                });
                i++; // Skip next block
                continue;
            }
        }

        // Single block
        grouped.push({
            node_id: block.node_id,
            level: block.level,
            title: block.type === 'title' ? block.text : '',
            content: block.type === 'content' ? block.text : '',
            children: [],
            is_transition: block.is_transition
        });
    }

    // Build tree from grouped nodes
    for (const node of grouped) {
        // Pop until we find a valid parent
        while (stack.length > 1 && stack[stack.length - 1].level >= node.level) {
            stack.pop();
        }

        // Add to current parent
        const parent = stack[stack.length - 1];
        parent.children.push(node);

        // Push this node as potential parent
        stack.push(node);
    }

    return result;
}

// ========== SLIDE RENDERING ==========

function renderSlides() {
    const container = document.getElementById('slidesContainer');
    const slides = buildSlides();

    if (slides.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted p-4">
                <i class="bi bi-file-slides" style="font-size: 3rem;"></i>
                <p class="mt-2">Format text to generate slides</p>
            </div>
        `;
        updateSlideCount(0);
        return;
    }

    const slidesHTML = slides.map((slide, index) => renderSlide(slide, index + 1)).join('');
    container.innerHTML = slidesHTML;
    updateSlideCount(slides.length);
}

// Build slides from structure
function buildSlides() {
    const slides = [];

    // Add intro slide first
    if (introSlide) {
        slides.push({
            slide_id: 'intro_slide_0',
            title: 'Intro Slide',
            content: introSlide.content,
            bullets: [],
            isIntroSlide: true
        });
    }

    // Get Level 1 nodes as slides
    for (const node of documentStructure) {
        if (node.level === 1) {
            slides.push({
                slide_id: node.node_id,
                title: node.title || 'Untitled',
                content: node.content || '',
                bullets: flattenChildren(node.children),
                is_transition: node.is_transition
            });
        }
    }

    return slides;
}

// Flatten children to bullets
function flattenChildren(children) {
    if (!children || children.length === 0) return [];

    const bullets = [];
    for (const child of children) {
        let text = child.title;
        if (child.content) {
            text = text ? `${text}: ${child.content}` : child.content;
        }

        bullets.push({
            level: child.level,
            text: text,
            node_id: child.node_id
        });

        if (child.children) {
            bullets.push(...flattenChildren(child.children));
        }
    }
    return bullets;
}

// Render single slide
function renderSlide(slide, slideNumber) {
    const bulletsHTML = slide.bullets.map(bullet => {
        const levelClass = 'level-' + bullet.level;
        return `<li class="slide-bullet ${levelClass}">${escapeHtml(bullet.text)}</li>`;
    }).join('');

    const bulletsSection = bulletsHTML ? `<ul class="slide-bullets">${bulletsHTML}</ul>` : '';

    let slideContentHTML = '';
    if (slide.content && slide.content.trim()) {
        slideContentHTML = `<div class="slide-content">${escapeHtml(slide.content)}</div>`;
    }

    const transitionBadge = slide.is_transition
        ? '<span class="badge bg-info ms-2"><i class="bi bi-play-circle"></i> Transition</span>'
        : '';

    const slideClass = slide.is_transition ? 'slide-thumbnail slide-transition' : 'slide-thumbnail';

    // Show "Add Transition" button only for non-transition Level 1 slides (not intro)
    const transitionBtn = (!slide.is_transition && !slide.isIntroSlide)
        ? `<button class="btn btn-sm btn-info mt-2" onclick="createTransitionSlide('${slide.slide_id}')" title="Create Transition Slide">
             <i class="bi bi-play-circle"></i> Add Transition
           </button>`
        : '';

    // Show "Delete Transition" button for transition slides
    const deleteTransitionBtn = slide.is_transition
        ? `<button class="btn btn-sm btn-danger mt-2" onclick="deleteTransitionSlide('${slide.slide_id}')" title="Delete Transition Slide">
             <i class="bi bi-trash"></i> Delete Transition
           </button>`
        : '';

    // Show "Delete Intro" button for intro slides
    const deleteIntroBtn = slide.isIntroSlide
        ? `<button class="btn btn-sm btn-danger mt-2" onclick="deleteIntroSlide()" title="Delete Intro Slide">
             <i class="bi bi-trash"></i> Delete Intro
           </button>`
        : '';

    return `
        <div class="${slideClass}" data-slide-id="${slide.slide_id}">
            <div class="slide-number">Slide ${slideNumber}</div>
            <div class="slide-title">${escapeHtml(slide.title)}${transitionBadge}</div>
            ${slideContentHTML}
            ${bulletsSection}
            ${transitionBtn}
            ${deleteTransitionBtn}
            ${deleteIntroBtn}
        </div>
    `;
}

// ========== SAVE STRUCTURE ==========

async function saveStructure() {
    try {
        // Convert to backend format
        function convertToBackendFormat(nodes) {
            return nodes.map(node => ({
                level: node.level,
                title: node.title || '',
                content: node.content || '',
                children: node.children ? convertToBackendFormat(node.children) : [],
                is_transition: node.is_transition || false,
                node_id: node.node_id
            }));
        }

        const backendStructure = convertToBackendFormat(documentStructure);

        await fetch(`${API_BASE_URL}/api/structure/update`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                document_structure: backendStructure,
                intro_slide: introSlide
            })
        });

        console.log('✅ Structure saved:', backendStructure.length, 'nodes');
    } catch (error) {
        console.error('❌ Error saving structure:', error);
    }
}

// ========== INTRO SLIDE ==========

function openIntroSlideModal() {
    const modal = new bootstrap.Modal(document.getElementById('introSlideModal'));
    const textarea = document.getElementById('introSlideInput');

    if (introSlide) {
        textarea.value = introSlide.content;
    } else {
        textarea.value = '';
    }

    document.getElementById('introCharCount').textContent = textarea.value.length;
    textarea.addEventListener('input', function () {
        document.getElementById('introCharCount').textContent = this.value.length;
    });

    modal.show();
}

function saveIntroSlide() {
    const content = document.getElementById('introSlideInput').value.trim();

    if (!content) {
        alert('Please enter intro slide content');
        return;
    }

    introSlide = {
        id: 'intro_slide_0',
        level: 0,
        title: 'Intro',
        content: content,
        type: 'title',
        children: []
    };

    // Also add to editor as formatted block
    const editor = document.getElementById('wordEditor');
    const introBlock = document.createElement('span');
    introBlock.className = 'text-block text-level-0 text-title';
    introBlock.dataset.level = '0';
    introBlock.dataset.type = 'title';
    introBlock.dataset.nodeId = 'intro_slide_0';
    introBlock.dataset.type = 'title';
    introBlock.dataset.nodeId = 'intro_slide_0';
    introBlock.innerHTML = `<span class="drag-handle" contenteditable="false"><i class="bi bi-grip-vertical"></i></span>${escapeHtml(content)}`;

    // Insert at beginning
    const firstChild = editor.firstChild;
    if (firstChild) {
        editor.insertBefore(introBlock, firstChild);
        editor.insertBefore(document.createElement('br'), introBlock.nextSibling);
    } else {
        editor.appendChild(introBlock);
    }

    updateStats();
    renderSlides();
    saveStructure();

    const modal = bootstrap.Modal.getInstance(document.getElementById('introSlideModal'));
    modal.hide();
}

// ========== APPROVE AND CONTINUE ==========

async function approveAndContinue() {
    if (documentStructure.length === 0 && !introSlide) {
        showAlert('Please format at least one text block before continuing.');
        return;
    }

    const slideCount = buildSlides().length;
    showConfirm(`Approve structure with ${slideCount} slide(s)? This will start the slide generation process.`, async () => {
        try {
            const btn = event?.target;
            const originalText = btn?.innerHTML;
            if (btn) btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
            if (btn) btn.disabled = true;

            await saveStructure();

            const response = await fetch(`${API_BASE_URL}/api/structure/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ APPROVE RESPONSE:', data);
                window.location.href = `streaming.html?manual_session=${sessionId}`;
            } else {
                throw new Error('Failed to approve structure');
            }
        } catch (error) {
            console.error('Error approving structure:', error);
            showAlert('Failed to continue workflow. Please try again.');

            const btn = event?.target;
            if (btn) {
                btn.innerHTML = '<i class="bi bi-check-circle"></i> Approve & Continue';
                btn.disabled = false;
            }
        }
    });
}

// ========== RESET ==========

function resetStructure() {
    showConfirm('Reset all formatting? This will convert everything back to plain text.', () => {
        const editor = document.getElementById('wordEditor');

        // Get all text content
        const plainText = editor.textContent;

        // Reset to plain text
        editor.innerHTML = escapeHtml(plainText);

        // Reset state
        documentStructure = [];
        introSlide = null;

        updateStats();
        renderSlides();
        saveStructure();

        console.log('✅ Structure reset');
    });
}

// ========== UTILITY FUNCTIONS ==========

function generateNodeId() {
    return 'node_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function updateStats() {
    const editor = document.getElementById('wordEditor');
    const blocks = editor.querySelectorAll('.text-block');
    const charCount = editor.textContent.length;
    const slides = buildSlides();

    document.getElementById('blockCount').textContent = blocks.length;
    document.getElementById('charCount').textContent = charCount;
    document.getElementById('slideCountStat').textContent = slides.length;
}

function updateSlideCount(count) {
    const element = document.getElementById('slideCount');
    if (element) {
        element.textContent = count + ' slide' + (count !== 1 ? 's' : '');
    }
}

function goBack() {
    window.history.back();
}

function cancelEdit() {
    showConfirm('Cancel editing? All changes will be lost.', () => {
        goBack();
    });
}

// ========== MODAL HELPERS ==========

function showAlert(message) {
    document.getElementById('customAlertMessage').textContent = message;
    const modal = new bootstrap.Modal(document.getElementById('customAlertModal'));
    modal.show();
}

function showConfirm(message, onConfirm) {
    document.getElementById('customConfirmMessage').textContent = message;
    const modal = new bootstrap.Modal(document.getElementById('customConfirmModal'));

    const okBtn = document.getElementById('customConfirmOk');
    okBtn.onclick = () => {
        modal.hide();
        onConfirm();
    };

    modal.show();
}

// ========== TRANSITION SLIDE ==========

// Create transition slide for Level 1 nodes
function createTransitionSlide(nodeId) {
    const nodeIndex = documentStructure.findIndex(n => n.node_id === nodeId);

    if (nodeIndex === -1) {
        showAlert('Node not found');
        return;
    }

    const node = documentStructure[nodeIndex];

    if (node.level !== 1) {
        showAlert('Transition slides can only be created for Level 1 nodes');
        return;
    }

    if (nodeIndex > 0) {
        const prevNode = documentStructure[nodeIndex - 1];
        if (prevNode.is_transition && prevNode.title === node.title) {
            showAlert('Transition slide already exists for this node');
            return;
        }
    }

    const transitionNode = {
        node_id: generateNodeId(),
        level: 1,
        title: node.title,
        content: node.content || '',
        children: [],
        is_transition: true
    };

    documentStructure.splice(nodeIndex, 0, transitionNode);
    addTransitionBlockToEditor(transitionNode, nodeId);

    console.log('✅ Created transition slide for:', node.title.substring(0, 30));
    updateStats();
    renderSlides();
    saveStructure();
}

function addTransitionBlockToEditor(transitionNode, beforeNodeId) {
    const editor = document.getElementById('wordEditor');
    const beforeBlock = editor.querySelector(`[data-node-id="${beforeNodeId}"]`);

    if (beforeBlock) {
        const transitionBlock = document.createElement('span');
        transitionBlock.className = 'text-block text-level-1 text-title';
        transitionBlock.dataset.level = '1';
        transitionBlock.dataset.type = 'title';
        transitionBlock.dataset.nodeId = transitionNode.node_id;
        transitionBlock.dataset.transition = 'true';
        transitionBlock.innerHTML = `<span class="drag-handle" contenteditable="false"><i class="bi bi-grip-vertical"></i></span>${escapeHtml(transitionNode.title)}`;
        transitionBlock.style.borderColor = '#0dcaf0';
        transitionBlock.style.background = 'rgba(13, 202, 240, 0.15)';

        beforeBlock.parentNode.insertBefore(transitionBlock, beforeBlock);
        beforeBlock.parentNode.insertBefore(document.createElement('br'), beforeBlock);

        if (transitionNode.content) {
            const contentBlock = document.createElement('span');
            contentBlock.className = 'text-block text-level-1 text-content';
            contentBlock.dataset.level = '1';
            contentBlock.dataset.type = 'content';
            contentBlock.dataset.nodeId = transitionNode.node_id + '_c';
            contentBlock.dataset.transition = 'true';
            contentBlock.dataset.transition = 'true';
            contentBlock.innerHTML = `<span class="drag-handle" contenteditable="false"><i class="bi bi-grip-vertical"></i></span>${escapeHtml(transitionNode.content)}`;
            contentBlock.style.borderColor = '#0dcaf0';
            contentBlock.style.background = 'rgba(13, 202, 240, 0.1)';

            beforeBlock.parentNode.insertBefore(contentBlock, beforeBlock);
            beforeBlock.parentNode.insertBefore(document.createElement('br'), beforeBlock);
        }
    }
}

// ========== DELETE TRANSITION SLIDE ==========

function deleteTransitionSlide(nodeId) {
    const nodeIndex = documentStructure.findIndex(n => n.node_id === nodeId);

    if (nodeIndex === -1) {
        showAlert('Transition slide not found');
        return;
    }

    const node = documentStructure[nodeIndex];

    if (!node.is_transition) {
        showAlert('This is not a transition slide');
        return;
    }

    // Remove from structure
    documentStructure.splice(nodeIndex, 1);

    // Remove from editor
    const editor = document.getElementById('wordEditor');
    const block = editor.querySelector(`[data-node-id="${nodeId}"]`);
    if (block) {
        // Also remove associated content block if exists
        const nextEl = block.nextElementSibling;
        if (nextEl && nextEl.tagName === 'BR') nextEl.remove();
        block.remove();
    }

    // Also remove content block if exists
    const contentBlock = editor.querySelector(`[data-node-id="${nodeId}_c"]`);
    if (contentBlock) {
        const nextEl = contentBlock.nextElementSibling;
        if (nextEl && nextEl.tagName === 'BR') nextEl.remove();
        contentBlock.remove();
    }

    console.log('🗑️ Deleted transition slide:', node.title.substring(0, 30));

    updateStats();
    renderSlides();
    saveStructure();
}

// ========== DELETE INTRO SLIDE ==========

function deleteIntroSlide() {
    if (!introSlide) {
        showAlert('No intro slide to delete');
        return;
    }

    const editor = document.getElementById('wordEditor');
    const block = editor.querySelector('[data-node-id="intro_slide_0"]');
    if (block) {
        const nextEl = block.nextElementSibling;
        if (nextEl && nextEl.tagName === 'BR') nextEl.remove();
        block.remove();
    }

    introSlide = null;
    console.log('🗑️ Deleted intro slide');

    updateStats();
    renderSlides();
    saveStructure();
}

// ========== DRAG & DROP FOR TEXT BLOCKS ==========

let draggedBlock = null;

function setupDragDrop() {
    const editor = document.getElementById('wordEditor');
    const observer = new MutationObserver(() => {
        addDragListenersToBlocks();
    });
    observer.observe(editor, { childList: true, subtree: true });
    addDragListenersToBlocks();
}

function addDragListenersToBlocks() {
    const blocks = document.querySelectorAll('.text-block');

    blocks.forEach(block => {
        if (block.getAttribute('draggable') === 'true') return; // Already setup

        block.setAttribute('draggable', 'true');
        // block.style.cursor = 'grab'; // Removed: handled by CSS (handle has grab, block has text)

        block.addEventListener('dragstart', handleBlockDragStart);
        block.addEventListener('dragend', handleBlockDragEnd);
        block.addEventListener('dragover', handleBlockDragOver);
        block.addEventListener('drop', handleBlockDrop);
        block.addEventListener('dragleave', handleBlockDragLeave);
    });
}

function handleBlockDragStart(e) {
    // Only allow drag if using the handle
    if (!e.target.closest('.drag-handle')) {
        e.preventDefault();
        return;
    }

    const block = e.target.closest('.text-block');
    if (!block) return;

    draggedBlock = block;
    block.style.opacity = '0.5';
    // block.style.cursor = 'grabbing'; 
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', block.dataset.nodeId);
}

function handleBlockDragEnd(e) {
    if (draggedBlock) {
        draggedBlock.style.opacity = '1';
        // draggedBlock.style.cursor = 'grab'; // Removing cursor reset as handled by CSS
    }

    // Fallback if draggedBlock is null (though shouldn't be)
    const block = e.target.closest('.text-block');
    if (block) {
        block.style.opacity = '1';
    }

    draggedBlock = null;

    // Remove all drop indicators
    document.querySelectorAll('.text-block').forEach(b => {
        b.style.borderTop = '';
        b.style.borderBottom = '';
    });
}

function handleBlockDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';

    const targetBlock = e.target.closest('.text-block');

    if (targetBlock && targetBlock !== draggedBlock) {
        // Show drop indicator
        const rect = targetBlock.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;

        // Reset borders
        targetBlock.style.borderTop = '';
        targetBlock.style.borderBottom = '';

        if (e.clientY < midY) {
            targetBlock.style.borderTop = '3px solid #667eea';
        } else {
            targetBlock.style.borderBottom = '3px solid #667eea';
        }
    }
}

function handleBlockDragLeave(e) {
    const targetBlock = e.target.closest('.text-block');
    if (targetBlock) {
        targetBlock.style.borderTop = '';
        targetBlock.style.borderBottom = '';
    }
}

function handleBlockDrop(e) {
    e.preventDefault();

    if (!draggedBlock) return;

    // Ensure opacity is reset even on drop
    draggedBlock.style.opacity = '1';

    if (e.target === draggedBlock || e.target.closest('.text-block') === draggedBlock) return;

    const targetBlock = e.target.closest('.text-block');
    if (!targetBlock) return;

    // Determine drop position (before or after)
    const rect = targetBlock.getBoundingClientRect();
    const midY = rect.top + rect.height / 2;
    const insertBefore = e.clientY < midY;

    // Move the dragged block
    const editor = document.getElementById('wordEditor');

    if (insertBefore) {
        targetBlock.parentNode.insertBefore(draggedBlock, targetBlock);
    } else {
        // Insert after
        if (targetBlock.nextSibling) {
            targetBlock.parentNode.insertBefore(draggedBlock, targetBlock.nextSibling);
        } else {
            targetBlock.parentNode.appendChild(draggedBlock);
        }
    }

    // Reset styles
    targetBlock.style.borderTop = '';
    targetBlock.style.borderBottom = '';

    console.log('📦 Moved block:', draggedBlock.dataset.nodeId);

    // Sync and save
    syncEditorToStructure();
    renderSlides();
    saveStructure();

    draggedBlock = null; // Clear dragged block reference
}
