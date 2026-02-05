"""
Test Suite for SlideGen API
"""
import pytest
from fastapi.testclient import TestClient
from web.backend.app.api import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code in [200, 404]  # 404 if index.html doesn't exist


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data


def test_upload_docx_invalid_file():
    """Test DOCX upload with invalid file type"""
    files = {"file": ("test.txt", b"test content", "text/plain")}
    response = client.post("/api/v1/upload/docx", files=files)
    assert response.status_code == 400
    assert "DOCX" in response.json()["detail"]


def test_upload_zip_invalid_file():
    """Test ZIP upload with invalid file type"""
    files = {"file": ("test.txt", b"test content", "text/plain")}
    response = client.post("/api/v1/upload-zip", files=files)
    assert response.status_code == 400
    assert "ZIP" in response.json()["detail"]


def test_get_image_not_found():
    """Test image endpoint with non-existent image"""
    response = client.get("/api/v1/images/nonexistent.png")
    assert response.status_code == 404


def test_conversion_status_not_found():
    """Test conversion status for non-existent project"""
    response = client.get("/api/v1/conversion-status/nonexistent_project")
    assert response.status_code in [404, 503]  # 503 if converter not available


def test_download_capture_not_found():
    """Test download capture with non-existent file"""
    response = client.get("/api/v1/download-capture/nonexistent.png")
    assert response.status_code in [404, 503]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
