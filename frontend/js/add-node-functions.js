// Show Add Node Form (reuse selection controls)
function showAddNodeForm() {
    // Show the selection controls section
    const selectionControls = document.getElementById('selectionControls');
    selectionControls.style.display = 'block';

    // Clear and enable the text preview for manual input
    const textPreview = document.getElementById('selectedTextPreview');
    textPreview.contentEditable = 'true';
    textPreview.textContent = 'Type or paste node text here...';
    textPreview.style.minHeight = '60px';
    textPreview.style.cursor = 'text';

    // Focus on it
    textPreview.focus();

    // Select all text for easy replacement
    if (window.getSelection) {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(textPreview);
        selection.removeAllRanges();
        selection.addRange(range);
    }

    // Scroll to view
    textPreview.scrollIntoView({ behavior: 'smooth', block: 'center' });

    console.log('📝 Add Node form activated - type or paste text');
}
