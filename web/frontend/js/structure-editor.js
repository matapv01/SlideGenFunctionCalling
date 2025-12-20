// structure-editor.js - REDESIGNED for manual text selection with SLIDE PREVIEW

// Global state
let documentText = "";
let documentStructure = [];
let selectedNodeId = null;
let sessionId = null;
let currentSelection = null;
let introSlide = null;  // Intro slide (Level 0)
let draggedNodeId = null;  // Drag & drop state
const API_BASE_URL = (window.config && window.config.BACKEND_URL) || 'http://localhost:12008';

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    const urlParams = new URLSearchParams(window.location.search);
    sessionId = urlParams.get('session');

    if (!sessionId) {
        alert('Không tìm thấy ID phiên làm việc');
        goBack();
        return;
    }

    loadDocumentData();

    // Listen for text selection
    document.getElementById('documentTextContainer').addEventListener('mouseup', handleTextSelection);

    // Listen for level change to filter parent options
    document.getElementById('nodeLevel').addEventListener('change', updateParentOptions);
});

// Load document data from API
async function loadDocumentData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/structure/current?session_id=${sessionId}`);
        const data = await response.json();

        if (data.document_text) {
            documentText = data.document_text;

            // Convert backend format (title/content) → frontend format (type/text)
            function convertFromBackendFormat(nodes) {
                const result = [];
                for (const node of nodes) {
                    // If has title, create title node
                    if (node.title) {
                        result.push({
                            node_id: node.node_id,
                            level: node.level,
                            type: 'title',
                            text: node.title,
                            children: node.children ? convertFromBackendFormat(node.children) : [],
                            is_transition: node.is_transition || false
                        });
                    }
                    // If has content, create content node  
                    if (node.content) {
                        result.push({
                            node_id: node.node_id + '_content',  // Unique ID for content
                            level: node.level,
                            type: 'content',
                            text: node.content,
                            children: [],
                            is_transition: node.is_transition || false
                        });
                    }
                }
                return result;
            }

            documentStructure = convertFromBackendFormat(data.document_structure || []);

            document.getElementById('documentTitle').textContent = data.document_title || 'Tài liệu không tên';
            document.getElementById('documentTextContainer').textContent = documentText;

            updateUI();  // Render both tree and slides
        } else {
            throw new Error('Không nhận được dữ liệu tài liệu');
        }
    } catch (error) {
        console.error('Error loading document:', error);
        alert('Không thể tải tài liệu. Vui lòng thử lại.');
        goBack();
    }
}

// Convert MERGED nodes (backend format) → SPLIT nodes (frontend format)
function splitNodes(mergedNodes) {
    const split = [];

    for (const node of mergedNodes) {
        // If node has both title and content → split into 2 nodes
        if (node.title && node.content) {
            // Title node
            split.push({
                node_id: node.node_id || generateNodeId(),
                level: node.level,
                type: 'title',
                text: node.title,
                children: node.children ? splitNodes(node.children) : [],
                is_transition: node.is_transition || false
            });

            // Content node (use same node_id with suffix)
            split.push({
                node_id: (node.node_id || generateNodeId()) + '_content',
                level: node.level,
                type: 'content',
                text: node.content,
                children: [],  // Content doesn't have children
                is_transition: node.is_transition || false
            });
        }
        // If only title → single title node
        else if (node.title) {
            split.push({
                node_id: node.node_id || generateNodeId(),
                level: node.level,
                type: 'title',
                text: node.title,
                children: node.children ? splitNodes(node.children) : [],
                is_transition: node.is_transition || false
            });
        }
        // If only content → single content node
        else if (node.content) {
            split.push({
                node_id: node.node_id || generateNodeId(),
                level: node.level,
                type: 'content',
                text: node.content,
                children: node.children ? splitNodes(node.children) : [],
                is_transition: node.is_transition || false
            });
        }
    }

    return split;
}

// Handle text selection
function handleTextSelection() {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();

    if (selectedText.length > 0) {
        currentSelection = selectedText;
        document.getElementById('selectedTextPreview').textContent =
            selectedText.length > 100 ? selectedText.substring(0, 100) + '...' : selectedText;
        document.getElementById('selectionControls').style.display = 'block';
    } else {
        currentSelection = null;
        document.getElementById('selectionControls').style.display = 'none';
    }
}

// Add selected text to structure
function addSelectedToStructure() {
    // Get text from selection OR manual input
    let textToAdd = currentSelection;

    // Check manual input from preview box if no selection
    if (!textToAdd) {
        const previewEl = document.getElementById('selectedTextPreview');
        if (previewEl && previewEl.innerText) {
            const manualText = previewEl.innerText.trim();
            // Filter out placeholders
            if (manualText !== 'Chưa chọn văn bản nào' && manualText !== 'Nhập hoặc dán văn bản vào đây...') {
                textToAdd = manualText;
            }
        }
    }

    if (!textToAdd) {
        showAlert('Vui lòng chọn văn bản trước hoặc nhập vào ô');
        return;
    }

    const nodeType = document.getElementById('nodeType').value;
    const nodeLevel = parseInt(document.getElementById('nodeLevel').value);
    const parentId = document.getElementById('parentNode').value;

    // Special handling for Level 0: Create intro slide instead
    if (nodeLevel === 0) {
        introSlide = {
            id: 'intro_slide_0',
            level: 0,
            title: 'Intro',
            content: textToAdd,
            type: 'title',
            children: []
        };

        updateIntroSlidePreview();
        updateUI();
        saveStructure();

        // Clear selection and manual input
        currentSelection = null;
        window.getSelection().removeAllRanges();
        const previewEl = document.getElementById('selectedTextPreview');
        if (previewEl) {
            previewEl.textContent = 'Chưa chọn văn bản nào';
            previewEl.contentEditable = 'false';
            previewEl.style.border = 'none';
        }
        document.getElementById('selectionControls').style.display = 'none';
        return;
    }

    //Create new node
    const newNode = {
        node_id: generateNodeId(),
        level: nodeLevel,
        type: nodeType,
        text: textToAdd,
        children: []
    };

    // Add to structure
    if (parentId) {
        const parent = findNodeById(documentStructure, parentId);
        if (parent) {
            if (!parent.children) parent.children = [];
            parent.children.push(newNode);
        }
    } else {
        documentStructure.push(newNode);
    }

    // Update UI
    updateUI();
    saveStructure();

    // Clear selection and manual input
    currentSelection = null;
    window.getSelection().removeAllRanges();
    const previewEl = document.getElementById('selectedTextPreview');
    if (previewEl) {
        previewEl.textContent = 'Chưa chọn văn bản nào';
        previewEl.contentEditable = 'false';
        previewEl.style.border = 'none';
    }
    document.getElementById('selectionControls').style.display = 'none';
}

// Generate unique node ID
function generateNodeId() {
    return 'node_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Find node by ID
function findNodeById(nodes, nodeId) {
    for (const node of nodes) {
        if (node.node_id === nodeId) {
            return node;
        }
        if (node.children) {
            const found = findNodeById(node.children, nodeId);
            if (found) return found;
        }
    }
    console.warn('Node not found:', nodeId, 'in:', nodes.map(n => n.node_id));
    return null;
}


// ========== UI UPDATE & TREE RENDERING ==========

// Update all UI components
function updateUI() {
    renderTree();   // Column 2: Structure tree
    renderSlides(); // Column 3: Slide previews
    updateParentOptions();
    updateNodeCount();
    updateSlideCount(buildSlides(documentStructure).length);
}

// Update node count
function updateNodeCount() {
    function countNodes(nodes) {
        let count = nodes.length;
        for (const node of nodes) {
            if (node.children) count += countNodes(node.children);
        }
        return count;
    }

    const count = countNodes(documentStructure);
    const element = document.getElementById('nodeCount');
    if (element) {
        element.textContent = count + ' mục';
    }
}

// Render tree view
function renderTree() {
    const container = document.getElementById('treeContainer');

    if (!documentStructure || documentStructure.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted p-4">
                <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                <p class="mt-2">Chưa có cấu trúc. Chọn văn bản để bắt đầu.</p>
            </div>
        `;
        return;
    }

    const treeHTML = renderNodesRecursive(documentStructure);
    container.innerHTML = treeHTML;
}

// Recursive function to render nodes with merge logic
function renderNodesRecursive(nodes) {
    let html = '';
    const processed = new Set();

    for (let i = 0; i < nodes.length; i++) {
        if (processed.has(i)) continue;

        const node = nodes[i];
        let attachedContentNode = null;

        // Check for merge: Title node followed by Content node (same level)
        if (node.type === 'title') {
            // Look ahead for content sibling
            for (let j = i + 1; j < nodes.length; j++) {
                if (processed.has(j)) continue;
                const other = nodes[j];

                // Stop if we hit another title or different level (strict sibling check)
                // Actually, we just look for the NEXT immediate sibling matching criteria
                // to avoid jumping over other nodes.
                if (j === i + 1 && other.type === 'content' && other.level === node.level) {
                    attachedContentNode = other;
                    processed.add(j);
                }
                break; // Only check immediate sibling
            }
        }

        html += renderNode(node, false, attachedContentNode);
        processed.add(i);
    }
    return html;
}

// Render single node (supports attached content)
function renderNode(node, isChild = false, attachedContentNode = null) {
    const hasChildren = node.children && node.children.length > 0;
    const typeIcon = node.type === 'title' ? 'bi-card-heading' : 'bi-card-text';
    const typeBadge = node.type === 'title' ? 'bg-primary' : 'bg-secondary';

    // Logic for children rendering
    let childrenHTML = '';
    if (hasChildren) {
        childrenHTML = renderNodesRecursive(node.children);
    }

    return `
        <div class="tree-node" data-node-id="${node.node_id}" 
             draggable="true"
             ondragstart="handleDragStart('${node.node_id}', event)"
             ondragover="handleDragOver(event)"
             ondrop="handleDrop('${node.node_id}', event)"
             ondragend="handleDragEnd(event)"
             onclick="selectNode('${node.node_id}', event)">
            <div class="node-header">
                ${hasChildren ? `<i class="bi bi-chevron-right node-toggle" onclick="toggleNode('${node.node_id}', event)"></i>` : `<i class="${typeIcon}"></i>`}
                <span class="node-title">${escapeHtml(node.text).substring(0, 40)}${node.text.length > 40 ? '...' : ''}</span>
                <span class="badge ${typeBadge}">${node.type}</span>
                <span class="node-level">L${node.level}</span>
                ${node.is_transition ? '<span class="badge bg-info ms-1" title="Transition Slide"><i class="bi bi-play-circle"></i> Chuyển tiếp</span>' : ''}
                <i class="bi bi-arrows-move drag-handle ms-2" style="cursor: grab; opacity: 0.5;" ondragstart="event.stopPropagation()"></i>
            </div>
            <div class="node-actions">
                ${node.level === 1 && !node.is_transition ? `
                    <button class="btn btn-sm btn-info" onclick="createTransitionSlide('${node.node_id}', event)" title="Tạo Slide Chuyển tiếp">
                        <i class="bi bi-play-circle"></i>
                    </button>
                ` : ''}
                <button class="btn btn-sm btn-warning" onclick="editNode('${node.node_id}', event)" title="Sửa Tiêu đề">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteNode('${node.node_id}', event)" title="Xóa Tiêu đề">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
            
            ${attachedContentNode ? `
                <div class="node-merged-content" onclick="event.stopPropagation()">
                    <div class="d-flex justify-content-between align-items-start">
                        <div style="flex: 1;">${escapeHtml(attachedContentNode.text)}</div>
                        <div class="ms-2">
                             <button class="btn btn-sm btn-outline-warning p-0 px-1" onclick="editNode('${attachedContentNode.node_id}', event)" title="Sửa Nội dung">
                                <i class="bi bi-pencil" style="font-size: 0.8rem;"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger p-0 px-1 ms-1" onclick="deleteNode('${attachedContentNode.node_id}', event)" title="Xóa Nội dung">
                                <i class="bi bi-trash" style="font-size: 0.8rem;"></i>
                            </button>
                        </div>
                    </div>
                </div>
            ` : ''}

            ${hasChildren ? `<div class="node-children" id="children-${node.node_id}" style="display: none;">
                ${childrenHTML}
            </div>` : ''}
        </div>
    `;
}

// Toggle node
function toggleNode(nodeId, event) {
    event.stopPropagation();
    const childrenDiv = document.getElementById(`children-${nodeId}`);
    const toggle = event.target;

    if (childrenDiv) {
        const isVisible = childrenDiv.style.display !== 'none';
        childrenDiv.style.display = isVisible ? 'none' : 'block';
        toggle.classList.toggle('expanded');
    }
}

// Select node
function selectNode(nodeId, event) {
    if (event) event.stopPropagation();

    document.querySelectorAll('.tree-node').forEach(n => n.classList.remove('selected'));
    const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`);
    if (nodeElement) {
        nodeElement.classList.add('selected');
        selectedNodeId = nodeId;
    }
}

// ========== SLIDE RENDERING ==========

// Render slides
function renderSlides() {
    const container = document.getElementById('slidesContainer');

    // Build slides from Level 1 nodes - FRESH build every time
    const slides = buildSlides(documentStructure);
    console.log('Rendering slides, count:', slides.length);

    if (slides.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted p-4">
                <i class="bi bi-file-slides" style="font-size: 3rem;"></i>
                <p class="mt-2">Chưa có slides. Thêm node Level 1 để tạo slides.</p>
            </div>
        `;
        updateSlideCount(0);
        return;
    }

    const slidesHTML = slides.map((slide, index) => renderSlide(slide, index + 1)).join('');
    container.innerHTML = slidesHTML;
    updateSlideCount(slides.length);
}

// Build slides from document structure (with merge)
function buildSlides(structure) {
    // Merge title+content siblings first
    // IMPORTANT: Only merge if content is IMMEDIATELY after title (index i+1)
    function quickMerge(nodes) {
        const result = [];
        const skip = new Set();

        for (let i = 0; i < nodes.length; i++) {
            if (skip.has(i)) continue;
            const n = nodes[i];

            if (n.type === 'title') {
                let content = '';
                // Check if NEXT node (index i+1) is content with same level
                if (i + 1 < nodes.length) {
                    const nextNode = nodes[i + 1];
                    if (nextNode.type === 'content' && nextNode.level === n.level) {
                        content = nextNode.text;
                        skip.add(i + 1);  // Mark next node as used
                    }
                }
                result.push({ ...n, mergedContent: content, children: n.children ? quickMerge(n.children) : [] });
            } else if (n.type === 'content') {
                result.push({ ...n, mergedContent: n.text, children: n.children ? quickMerge(n.children) : [] });
            }
            skip.add(i);
        }
        return result;
    }

    // Flatten merged children recursively
    function flattenBullets(nodes) {
        const bullets = [];
        for (const node of nodes) {
            // Format: "Title: Content" or just "Title" or just "Content"
            let text = '';
            if (node.text && node.mergedContent) {
                text = node.text + ': ' + node.mergedContent;
            } else if (node.text) {
                text = node.text;
            } else if (node.mergedContent) {
                text = node.mergedContent;
            }

            bullets.push({
                level: node.level,
                text: text,
                node_id: node.node_id
            });

            // Recursively add children
            if (node.children && node.children.length > 0) {
                bullets.push(...flattenBullets(node.children));
            }
        }
        return bullets;
    }

    const merged = quickMerge(structure);
    const slides = [];

    // Add intro slide first (if exists)
    if (introSlide) {
        slides.push({
            slide_id: 'intro_slide_0',
            title: 'Intro Slide',
            content: introSlide.content,
            bullets: [],
            isIntroSlide: true
        });
    }

    // Only show title nodes as slides (ignore standalone content nodes)
    const level1 = merged.filter(n => n.level === 1 && n.type === 'title');

    for (const node of level1) {
        slides.push({
            slide_id: node.node_id,
            title: node.text,
            content: node.mergedContent || '',
            bullets: node.children ? flattenBullets(node.children) : [],
            is_transition: node.is_transition || false  // Include transition flag
        });
    }
    return slides;

}

// Flatten children into bullet array
function flattenChildren(children) {
    if (!children || children.length === 0) return [];

    const bullets = [];
    for (const child of children) {
        bullets.push({
            level: child.level,
            text: child.text,
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

        // Parse "Title: Content"
        let title = '', content = '';
        if (bullet.text.includes(': ')) {
            const parts = bullet.text.split(': ');
            title = parts[0];
            content = parts.slice(1).join(': ');
        } else {
            title = bullet.text;
        }

        let html = '<li class="slide-bullet ' + levelClass + '">';
        html += '<div class="bullet-title"><strong>' + escapeHtml(title) + '</strong></div>';
        if (content) html += '<div class="bullet-content">' + escapeHtml(content) + '</div>';
        html += '</li>';
        return html;
    }).join('');

    const bulletsSection = bulletsHTML ? '<ul class="slide-bullets">' + bulletsHTML + '</ul>' : '';

    // Slide content (L1 content) - only show if not empty
    let slideContentHTML = '';
    if (slide.content && slide.content.trim()) {
        slideContentHTML = '<div class="slide-content">' + escapeHtml(slide.content) + '</div>';
    }

    // Transition badge (if applicable)
    let transitionBadge = '';
    if (slide.is_transition) {
        transitionBadge = '<span class="badge bg-info ms-2" style="font-size: 0.7rem;"><i class="bi bi-play-circle"></i> Chuyển tiếp</span>';
    }

    return '<div class="slide-thumbnail' + (slide.is_transition ? ' slide-transition' : '') + '" data-slide-id="' + slide.slide_id + '" onclick="selectSlide(\'' + slide.slide_id + '\', event)">' +
        '<div class="slide-number">Slide ' + slideNumber + '</div>' +
        '<div class="slide-title">' + escapeHtml(slide.title) + transitionBadge + '</div>' +
        slideContentHTML +
        bulletsSection +
        '<div class="slide-actions">' +
        '<button class="btn btn-sm btn-warning" onclick="editSlide(\'' + slide.slide_id + '\', event)">' +
        '<i class="bi bi-pencil"></i>' +
        '</button>' +
        '<button class="btn btn-sm btn-danger" onclick="deleteSlide(\'' + slide.slide_id + '\', event)">' +
        '<i class="bi bi-trash"></i>' +
        '</button>' +
        '</div>' +
        '</div>';

}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Select slide
function selectSlide(slideId, event) {
    if (event) event.stopPropagation();

    document.querySelectorAll('.slide-thumbnail').forEach(s => s.classList.remove('selected'));
    const slideElement = document.querySelector('[data-slide-id="' + slideId + '"]');
    if (slideElement) {
        slideElement.classList.add('selected');
        selectedNodeId = slideId;
    }
}

// Edit slide
function editSlide(slideId, event) {
    editNode(slideId, event);
}

// Delete slide
function deleteSlide(slideId, event) {
    deleteNode(slideId, event);
}

// Update slide count
function updateSlideCount(count) {
    const element = document.getElementById('slideCount');
    if (element) {
        element.textContent = count + ' slide';
    }
}

// ========== NODE EDITING ==========

// Edit node - ENHANCED
function editNode(nodeId, event) {
    if (event) event.stopPropagation();

    const node = findNodeById(documentStructure, nodeId);
    if (!node) return;

    // Populate modal
    document.getElementById('editNodeType').value = node.type;
    document.getElementById('editNodeLevel').value = node.level;
    document.getElementById('editNodeText').value = node.text;
    document.getElementById('editCharCount').textContent = node.text.length;

    // Update parent dropdown and set current parent
    const currentParentId = findParentId(documentStructure, nodeId);
    updateEditParentOptions(nodeId);
    setTimeout(() => {
        if (currentParentId) {
            document.getElementById('editParentNode').value = currentParentId;
        }
    }, 50);

    const modal = new bootstrap.Modal(document.getElementById('editModal'));
    modal.show();

    selectedNodeId = nodeId;

    // Char count listener
    document.getElementById('editNodeText').oninput = function () {
        document.getElementById('editCharCount').textContent = this.value.length;
    };
}

// Update parent options for editing (exclude self and descendants)
function updateEditParentOptions(currentNodeId) {
    const select = document.getElementById('editParentNode');
    const editLevelSelect = document.getElementById('editNodeLevel');
    const targetLevel = editLevelSelect ? parseInt(editLevelSelect.value) : 1;

    // Reset options
    select.innerHTML = '<option value="">Gốc (Không có cha)</option>';

    // If target level is 1, no parents allowed
    if (targetLevel === 1) {
        select.disabled = true;
        return;
    }
    select.disabled = false;

    function addOptions(nodes, indent = 0) {
        for (const node of nodes) {
            if (node.type === 'title' && node.level === targetLevel - 1) {
                const prefix = '—'.repeat(indent);
                const text = node.text.substring(0, 30);
                // Add (transition) suffix for transition nodes
                const suffix = node.is_transition ? ' (transition)' : '';
                select.innerHTML += '<option value="' + node.node_id + '">' + prefix + ' ' + text + '...' + suffix + '</option>';
            }
            if (node.children && node.children.length > 0) {
                addOptions(node.children, indent + 1);
            }
        }
    }

    addOptions(documentStructure);
}

// Check if node is descendant
function isDescendant(node, targetId) {
    if (node.node_id === targetId) return true;
    if (node.children) {
        for (const child of node.children) {
            if (isDescendant(child, targetId)) return true;
        }
    }
    return false;
}

// Find parent ID - FIXED for proper nested lookup
function findParentId(nodes, targetId, parentId = null) {
    for (const node of nodes) {
        if (node.node_id === targetId) {
            return parentId;  // Return the parent's ID
        }
        if (node.children && node.children.length > 0) {
            const found = findParentId(node.children, targetId, node.node_id);
            if (found !== null && found !== undefined) {
                return found;  // Return the found parent ID
            }
        }
    }
    return null;  // Target not found in this branch
}

// Save node edit - ENHANCED
function saveNodeEdit() {
    const node = findNodeById(documentStructure, selectedNodeId);
    if (!node) return;

    const newType = document.getElementById('editNodeType').value;
    const newLevel = parseInt(document.getElementById('editNodeLevel').value);
    const newText = document.getElementById('editNodeText').value;
    const newParentId = document.getElementById('editParentNode').value;

    console.log('🔧 Editing node:', selectedNodeId);
    console.log('   Old values:', { type: node.type, level: node.level, text: node.text.substring(0, 30) });
    console.log('   New values:', { type: newType, level: newLevel, text: newText.substring(0, 30) });

    // VALIDATION: Prevent "drifting" (Orphan nodes)
    // If Level > 1, a Parent MUST be selected.
    if (newLevel > 1 && !newParentId) {
        alert('Node cấp độ ' + newLevel + ' phải có Node Cha.\nVui lòng chọn cha hoặc đổi Cấp độ thành 1.');
        return;
    }

    const oldParentId = findParentId(documentStructure, selectedNodeId);
    console.log('   Parent change:', oldParentId, '=>', newParentId || 'null');

    // Update properties IN PLACE
    node.type = newType;
    node.level = newLevel;
    node.text = newText;
    // Preserve is_transition flag (don't overwrite)
    // node.is_transition stays the same

    console.log('   ✓ Updated node in place');

    // Move node if parent changed
    if (oldParentId !== newParentId) {
        console.log('   ⚠️ Moving node to different parent...');
        // Remove from old location
        if (oldParentId) {
            const oldParent = findNodeById(documentStructure, oldParentId);
            oldParent.children = oldParent.children.filter(c => c.node_id !== selectedNodeId);
        } else {
            documentStructure = documentStructure.filter(n => n.node_id !== selectedNodeId);
        }

        // Add to new location
        if (newParentId) {
            const newParent = findNodeById(documentStructure, newParentId);
            if (!newParent.children) newParent.children = [];
            newParent.children.push(node);
        } else {
            documentStructure.push(node);
        }
        console.log('   ✓ Node moved');
    }

    bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
    updateUI();  // Update both tree and slides
    saveStructure();
    console.log('   ✓ Save complete');
}

// Delete node
function deleteNode(nodeId, event) {
    if (event) event.stopPropagation();

    showConfirm('Xóa node này và tất cả con của nó?', () => {

        // Special handling: If deleting transition TITLE, check for paired content
        const node = findNodeById(documentStructure, nodeId);
        if (node && node.is_transition && node.type === 'title') {
            // Find siblings to check for paired content
            const parentId = findParentId(documentStructure, nodeId);
            const siblings = parentId ? findNodeById(documentStructure, parentId).children : documentStructure;
            const nodeIndex = siblings.findIndex(n => n.node_id === nodeId);

            // Check if next node is transition content at same level
            if (nodeIndex !== -1 && nodeIndex + 1 < siblings.length) {
                const nextNode = siblings[nodeIndex + 1];
                if (nextNode.is_transition && nextNode.type === 'content' && nextNode.level === node.level) {
                    // Delete both title and content
                    console.log('🗑️ Deleting transition pair: title + content');
                    documentStructure = removeNodeById(documentStructure, nodeId);
                    documentStructure = removeNodeById(documentStructure, nextNode.node_id);
                    updateUI();
                    saveStructure();
                    return;
                }
            }
        }

        // Normal deletion (including transition content nodes, or title without content)
        documentStructure = removeNodeById(documentStructure, nodeId);
        updateUI();
        saveStructure();
    });
}

// Remove node by ID
function removeNodeById(nodes, nodeId) {
    return nodes.filter(node => {
        if (node.node_id === nodeId) return false;
        if (node.children) {
            node.children = removeNodeById(node.children, nodeId);
        }
        return true;
    });
}

// Update parent options dropdown - Smart filtering by level
function updateParentOptions() {
    const select = document.getElementById('parentNode');
    const levelSelect = document.getElementById('nodeLevel');
    const targetLevel = (levelSelect && levelSelect.value) ? parseInt(levelSelect.value) : 1;

    // Reset options
    select.innerHTML = '<option value="">Root (No parent)</option>';

    // If target level is 1, no parents allowed (it's a root node)
    if (targetLevel === 1) {
        select.disabled = true;
        return;
    }
    select.disabled = false;

    function addOptions(nodes, indent = 0) {
        for (const node of nodes) {
            if (node.type === 'title') {
                // Smart Filter: Only show parents that are 1 level higher (level = targetLevel - 1)
                // e.g. If adding Level 3, only show Level 2 parents
                if (node.level === targetLevel - 1) {
                    const prefix = '—'.repeat(indent);
                    const text = node.text.substring(0, 30);
                    // Add (transition) suffix for transition nodes
                    const suffix = node.is_transition ? ' (transition)' : '';
                    select.innerHTML += '<option value="' + node.node_id + '">' + prefix + ' ' + text + '...' + suffix + '</option>';
                }

                if (node.children && node.children.length > 0) {
                    addOptions(node.children, indent + 1);
                }
            }
        }
    }

    addOptions(documentStructure);
}


// Save structure to backend
async function saveStructure() {
    try {
        // STEP 1: Merge title + content nodes that are siblings
        function mergeNodes(nodes) {
            const merged = [];
            const processed = new Set();

            for (let i = 0; i < nodes.length; i++) {
                if (processed.has(i)) continue;

                const node = nodes[i];

                // If this is a title node, look for matching content node
                if (node.type === 'title') {
                    // Look for content node at same level (sibling)
                    let contentNode = null;
                    let contentIndex = -1;

                    for (let j = i + 1; j < nodes.length; j++) {
                        if (processed.has(j)) continue;
                        const other = nodes[j];

                        // Check if it's a content node at same level as sibling
                        if (other.type === 'content' && other.level === node.level) {
                            contentNode = other;
                            contentIndex = j;
                            break;
                        }
                    }

                    // Create merged node
                    const mergedNode = {
                        node_id: node.node_id,
                        level: node.level,
                        title: node.text,
                        content: contentNode ? contentNode.text : '',
                        children: node.children ? mergeNodes(node.children) : [],
                        is_transition: node.is_transition || false  // Preserve transition flag
                    };

                    merged.push(mergedNode);
                    if (contentIndex >= 0) processed.add(contentIndex);

                } else if (node.type === 'content') {
                    // Content without title - use empty title
                    merged.push({
                        node_id: node.node_id,
                        level: node.level,
                        title: '',
                        content: node.text,
                        children: node.children ? mergeNodes(node.children) : [],
                        is_transition: node.is_transition || false
                    });
                } else {
                    // Other nodes (shouldn't happen)
                    merged.push({
                        node_id: node.node_id,
                        level: node.level,
                        title: node.text || '',
                        content: '',
                        children: node.children ? mergeNodes(node.children) : [],
                        is_transition: node.is_transition || false
                    });
                }

                processed.add(i);
            }

            return merged;
        }

        // Convert frontend format (type/text) → backend format (title/content)
        function convertToBackendFormat(nodes) {
            return nodes.map(node => ({
                level: node.level,
                title: node.type === 'title' ? node.text : '',
                content: node.type === 'content' ? node.text : '',
                children: node.children ? convertToBackendFormat(node.children) : [],
                is_transition: node.is_transition || false,
                node_id: node.node_id  // Preserve node_id
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

        console.log('✅ Structure saved:', backendStructure.length, 'nodes' + (introSlide ? ' + intro slide' : ''));
    } catch (error) {
        console.error('❌ Error saving structure:', error);
    }
}

// Reset structure
function resetStructure() {
    showConfirm('Đặt lại cấu trúc? Mọi thay đổi sẽ mất và quay về trạng thái rỗng.', () => {
        // Clear document structure
        documentStructure = [];

        // Clear intro slide if exists
        introSlide = null;
        updateIntroSlidePreview();

        // Reset UI components
        renderTree();          // Clear tree view
        renderSlides();        // Clear slides preview
        updateParentOptions(); // Clear parent dropdown
        updateNodeCount();     // Update node count to 0
        updateSlideCount(0);   // Update slide count to 0

        // Clear selection controls
        currentSelection = null;
        document.getElementById('selectionControls').style.display = 'none';

        // Save empty structure to backend
        saveStructure();

        console.log('✅ Structure reset successfully');
    });
}

// Cancel edit
function cancelEdit() {
    showConfirm('Hủy chỉnh sửa? Mọi thay đổi sẽ bị mất.', () => {
        goBack();
    });
}

// Approve and continue
async function approveAndContinue() {
    if (documentStructure.length === 0) {
        showAlert('Vui lòng tạo ít nhất một node cấu trúc trước khi tiếp tục.');
        return;
    }

    // Confirm before approving
    const slideCount = buildSlides(documentStructure).length;
    showConfirm(`Duyệt cấu trúc với ${slideCount} slide? Quá trình tạo slide sẽ bắt đầu.`, async () => {
        try {
            // Show loading state
            const btn = event?.target;
            const originalText = btn?.innerHTML;
            if (btn) btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Đang xử lý...';
            if (btn) btn.disabled = true;

            await saveStructure();

            const response = await fetch(`${API_BASE_URL}/api/structure/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });

            if (response.ok) {
                // Get and log response data
                const data = await response.json();
                console.log('✅ APPROVE RESPONSE:', data);
                console.log('📋 Document Structure:', data.document_structure);
                console.log('📊 Structure Length:', data.document_structure?.length);
                console.log('🔍 First 3 nodes:', data.document_structure?.slice(0, 3));

                // Redirect to streaming with manual session parameter
                window.location.href = `streaming.html?manual_session=${sessionId}`;
            } else {
                throw new Error('Duyệt cấu trúc thất bại');
            }
        } catch (error) {
            console.error('Error approving structure:', error);
            showAlert('Không thể tiếp tục quy trình. Vui lòng thử lại.');

            // Restore button
            const btn = event?.target;
            if (btn) {
                btn.innerHTML = '<i class="bi bi-check-circle"></i> Duyệt & Tiếp tục';
                btn.disabled = false;
            }
        }
    });
}

// Go back
function goBack() {
    window.history.back();
}

// ========== INTRO SLIDE FUNCTIONS ==========

// Open intro slide modal
function openIntroSlideModal() {
    const modal = new bootstrap.Modal(document.getElementById('introSlideModal'));
    const textarea = document.getElementById('introSlideInput');

    if (introSlide) {
        textarea.value = introSlide.content;
    } else {
        textarea.value = '';
    }

    // Update char count
    document.getElementById('introCharCount').textContent = textarea.value.length;

    // Listen for input changes
    textarea.addEventListener('input', function () {
        document.getElementById('introCharCount').textContent = this.value.length;
    });

    modal.show();
}

// Save intro slide
function saveIntroSlide() {
    const content = document.getElementById('introSlideInput').value.trim();

    if (!content) {
        alert('Vui lòng nhập nội dung slide giới thiệu');
        return;
    }

    // Create intro slide object (Level 0)
    introSlide = {
        id: 'intro_slide_0',
        level: 0,
        title: 'Intro',
        content: content,
        type: 'title',
        children: []
    };

    // Update UI
    updateIntroSlidePreview();
    updateUI();

    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('introSlideModal'));
    modal.hide();
}

// Edit intro slide
function editIntroSlide() {
    openIntroSlideModal();
}

// Remove intro slide
function removeIntroSlide() {
    if (confirm('Xóa slide giới thiệu?')) {
        introSlide = null;
        updateIntroSlidePreview();
        updateUI();
    }
}

// Update intro slide preview
function updateIntroSlidePreview() {
    const btn = document.getElementById('introSlideBtn');
    const preview = document.getElementById('introSlidePreview');

    if (introSlide) {
        btn.style.display = 'none';
        preview.style.display = 'block';
        document.getElementById('introSlideText').textContent = introSlide.content.substring(0, 100) +
            (introSlide.content.length > 100 ? '...' : '');
    } else {
        btn.style.display = 'block';
        preview.style.display = 'none';
    }
}


// ========== TRANSITION SLIDE FUNCTIONS ==========

// Create transition slide for level 1 nodes
function createTransitionSlide(nodeId, event) {
    if (event) event.stopPropagation();

    const node = findNodeById(documentStructure, nodeId);
    if (!node) {
        alert('Không tìm thấy node');
        return;
    }

    // Only allow for Level 1 nodes
    if (node.level !== 1) {
        alert('Slide chuyển tiếp chỉ có thể tạo cho node Level 1');
        return;
    }

    // Check if node already has transition slide (check if previous sibling is a transition)
    const parentId = findParentId(documentStructure, nodeId);
    const siblings = parentId ? findNodeById(documentStructure, parentId).children : documentStructure;
    const nodeIndex = siblings.findIndex(n => n.node_id === nodeId);

    if (nodeIndex > 0) {
        const previousNode = siblings[nodeIndex - 1];
        if (previousNode.is_transition && previousNode.text === node.text) {
            alert('Slide chuyển tiếp đã tồn tại cho node này');
            return;
        }
    }

    // Find merged content if exists (look for content node immediately after this title)
    let mergedContent = '';
    if (node.type === 'title' && nodeIndex + 1 < siblings.length) {
        const nextNode = siblings[nodeIndex + 1];
        if (nextNode.type === 'content' && nextNode.level === node.level) {
            mergedContent = nextNode.text;
        }
    }

    // Create transition node with same title/content but empty children
    const transitionNode = {
        node_id: generateNodeId(),
        level: 1,
        type: 'title',
        text: node.text,
        children: [],
        is_transition: true  // Mark as transition slide
    };

    // Create content node if original has merged content
    let transitionContentNode = null;
    if (mergedContent) {
        transitionContentNode = {
            node_id: generateNodeId(),
            level: 1,
            type: 'content',
            text: mergedContent,
            children: [],
            is_transition: true
        };
    }

    // Insert transition node BEFORE the original node
    if (transitionContentNode) {
        siblings.splice(nodeIndex, 0, transitionNode, transitionContentNode);
    } else {
        siblings.splice(nodeIndex, 0, transitionNode);
    }

    console.log('✅ Created transition slide for:', node.text.substring(0, 30));

    // Update UI
    updateUI();
    saveStructure();
}

// Helper: Find node index in structure
function findNodeIndex(nodes, nodeId, parentId = null) {
    for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].node_id === nodeId) {
            return { index: i, parentId: parentId };
        }
        if (nodes[i].children && nodes[i].children.length > 0) {
            const found = findNodeIndex(nodes[i].children, nodeId, nodes[i].node_id);
            if (found) return found;
        }
    }
    return null;
}

// ========== DRAG & DROP FUNCTIONS ==========

// Handle drag start
function handleDragStart(nodeId, event) {
    event.stopPropagation();  // Prevent event bubbling to parent nodes
    draggedNodeId = nodeId;
    const draggedNode = findNodeById(documentStructure, nodeId);
    console.log('DRAG START - Node:', nodeId, 'Level:', draggedNode?.level, 'Type:', draggedNode?.type);

    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/html', event.target.innerHTML);

    // Add visual feedback
    const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`);
    if (nodeElement) {
        nodeElement.style.opacity = '0.5';
        nodeElement.style.cursor = 'grabbing';
    }
}

// Handle drag over
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();  // Prevent bubbling
    event.dataTransfer.dropEffect = 'move';

    const nodeElement = event.target.closest('.tree-node');
    if (nodeElement && nodeElement !== document.querySelector(`[data-node-id="${draggedNodeId}"]`)) {
        nodeElement.style.borderTop = '3px solid #667eea';
        nodeElement.style.paddingTop = '8px';
    }
}

// Handle drag end
function handleDragEnd(event) {
    // Remove visual feedback from all nodes
    document.querySelectorAll('.tree-node').forEach(node => {
        node.style.opacity = '1';
        node.style.cursor = 'default';
        node.style.borderTop = 'none';
        node.style.paddingTop = '0';
    });
}

// Handle drop - FIXED for proper parent checking
function handleDrop(targetNodeId, event) {
    event.preventDefault();
    event.stopPropagation();

    console.log('DROP - From:', draggedNodeId, 'To:', targetNodeId);

    if (!draggedNodeId || draggedNodeId === targetNodeId) {
        draggedNodeId = null;
        handleDragEnd(event);
        return;
    }

    // Find dragged and target nodes
    const draggedNode = findNodeById(documentStructure, draggedNodeId);
    const targetNode = findNodeById(documentStructure, targetNodeId);

    console.log('Dragged node:', draggedNode ? { level: draggedNode.level, text: draggedNode.text.substring(0, 20) } : 'NOT FOUND');
    console.log('Target node:', targetNode ? { level: targetNode.level, text: targetNode.text.substring(0, 20) } : 'NOT FOUND');

    if (!draggedNode || !targetNode) {
        console.log('Node not found - dragged:', draggedNode, 'target:', targetNode);
        draggedNodeId = null;
        handleDragEnd(event);
        return;
    }

    // Only swap if same level
    if (draggedNode.level !== targetNode.level) {
        console.log('LEVEL MISMATCH - Dragged:', draggedNode.level, 'Target:', targetNode.level);
        alert('Chỉ có thể sắp xếp lại các node cùng cấp độ');
        draggedNodeId = null;
        handleDragEnd(event);
        return;
    }

    // Find parent of both nodes
    const draggedParentId = findParentId(documentStructure, draggedNodeId);
    const targetParentId = findParentId(documentStructure, targetNodeId);

    console.log('Dragged parent ID:', draggedParentId, 'Target parent ID:', targetParentId);

    // They must have same parent to reorder
    // Note: Both can be null if they're root level nodes
    if (draggedParentId !== targetParentId) {
        console.log('PARENT MISMATCH');
        alert('Các node phải cùng cha mới có thể sắp xếp lại');
        draggedNodeId = null;
        handleDragEnd(event);
        return;
    }

    // Get parent's children array
    let parentChildren = null;
    if (draggedParentId === null) {
        // Both are root level nodes
        parentChildren = documentStructure;
        console.log('Both are root nodes');
    } else {
        // Both are children of same parent
        const parent = findNodeById(documentStructure, draggedParentId);
        if (!parent || !parent.children) {
            console.log('Parent not found or has no children');
            draggedNodeId = null;
            handleDragEnd(event);
            return;
        }
        parentChildren = parent.children;
        console.log('Parent found, children count:', parentChildren.length);
    }

    // Find indices
    const draggedIndex = parentChildren.findIndex(n => n.node_id === draggedNodeId);
    const targetIndex = parentChildren.findIndex(n => n.node_id === targetNodeId);

    console.log('Dragged index:', draggedIndex, 'Target index:', targetIndex);

    if (draggedIndex !== -1 && targetIndex !== -1) {
        const draggedIsTitle = draggedNode.type === 'title';
        const targetIsTitle = targetNode.type === 'title';

        let draggedContentIndex = -1;
        let targetContentIndex = -1;

        // Find content node immediately following dragged title
        if (draggedIsTitle && draggedIndex + 1 < parentChildren.length) {
            const nextNode = parentChildren[draggedIndex + 1];
            if (nextNode.type === 'content' && nextNode.level === draggedNode.level) {
                draggedContentIndex = draggedIndex + 1;
            }
        }

        // Find content node immediately following target title
        if (targetIsTitle && targetIndex + 1 < parentChildren.length) {
            const nextNode = parentChildren[targetIndex + 1];
            if (nextNode.type === 'content' && nextNode.level === targetNode.level) {
                targetContentIndex = targetIndex + 1;
            }
        }

        console.log('Dragged block: Title at', draggedIndex, 'Content at', draggedContentIndex);
        console.log('Target block: Title at', targetIndex, 'Content at', targetContentIndex);

        // Build blocks to swap
        const draggedBlock = [draggedNode];
        if (draggedContentIndex !== -1) {
            draggedBlock.push(parentChildren[draggedContentIndex]);
        }

        const targetBlock = [targetNode];
        if (targetContentIndex !== -1) {
            targetBlock.push(parentChildren[targetContentIndex]);
        }

        // Remove dragged block (remove higher index first)
        if (draggedContentIndex !== -1) {
            parentChildren.splice(draggedContentIndex, 1);
        }
        parentChildren.splice(draggedIndex, 1);

        // Adjust targetIndex after removing dragged block
        let adjustedTargetIndex = targetIndex;
        if (draggedIndex < targetIndex) {
            adjustedTargetIndex -= (draggedContentIndex !== -1 ? 2 : 1);
        }

        // Remove target block (remove higher index first)
        if (targetContentIndex !== -1) {
            let adjustedContentIndex = targetContentIndex;
            if (draggedIndex < targetIndex) {
                adjustedContentIndex -= (draggedContentIndex !== -1 ? 2 : 1);
            }
            parentChildren.splice(adjustedContentIndex, 1);
        }
        parentChildren.splice(adjustedTargetIndex, 1);

        // Insert target block at dragged position
        parentChildren.splice(draggedIndex, 0, ...targetBlock);

        // Calculate insertion position for dragged block
        let insertPosForDragged = adjustedTargetIndex;
        if (draggedIndex <= adjustedTargetIndex) {
            insertPosForDragged += targetBlock.length;
        }
        parentChildren.splice(insertPosForDragged, 0, ...draggedBlock);

        console.log('✓ Blocks swapped successfully!');
        updateUI();
        saveStructure();
    } else {
        console.log('✗ Could not find both nodes in parent children');
    }

    draggedNodeId = null;
    handleDragEnd(event);
}

// Show Add Node Form - simple version
function showAddNodeForm() {
    // Show selection controls
    document.getElementById('selectionControls').style.display = 'block';

    // Make text preview editable
    const preview = document.getElementById('selectedTextPreview');
    preview.contentEditable = 'true';
    preview.textContent = '';
    preview.placeholder = 'Nhập hoặc dán văn bản node vào đây...';
    preview.style.minHeight = '80px';
    preview.style.border = '2px dashed #0dcaf0';

    // Focus
    preview.focus();


    console.log('📝 Add Node: form ready for manual input');
}

// ========== CUSTOM ALERT/CONFIRM MODALS ==========

// Custom Alert (replaces window.alert)
function showAlert(message) {
    document.getElementById('customAlertMessage').textContent = message;
    const modal = new bootstrap.Modal(document.getElementById('customAlertModal'));
    modal.show();
}

// Custom Confirm (replaces window.confirm)
function showConfirm(message, onConfirm) {
    document.getElementById('customConfirmMessage').textContent = message;
    const modal = new bootstrap.Modal(document.getElementById('customConfirmModal'));

    // Set up OK button handler
    const okBtn = document.getElementById('customConfirmOk');
    okBtn.onclick = function () {
        modal.hide();
        if (onConfirm) onConfirm();
    };

    modal.show();
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
