const BACKEND_URL = "http://localhost:8000";

async function handleDocxUpload() {
    const fileInput = document.getElementById('docxFile');
    const status = document.getElementById('status');
    const downloadLink = document.getElementById('downloadLink');
    const file = fileInput.files[0];

    if (!file) {
        status.textContent = "Please select a DOCX file!";
        status.style.color = "red";
        return;
    }

    status.textContent = "Processing...";
    status.style.color = "blue";
    downloadLink.style.display = "none";

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${BACKEND_URL}/upload-docx/`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            downloadLink.href = url;
            downloadLink.style.display = "inline";
            status.textContent = "Slides generated successfully!";
            status.style.color = "green";
        } else {
            const error = await response.json();
            status.textContent = `Error: ${error.detail}`;
            status.style.color = "red";
        }
    } catch (error) {
        status.textContent = `Error: ${error.message}`;
        status.style.color = "red";
    }
}