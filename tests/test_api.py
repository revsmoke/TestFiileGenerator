import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

@patch("services.gemini_service.generate_test_data", new_callable=AsyncMock)
def test_generate_pdf_endpoint(mock_gemini):
    mock_gemini.return_value = {
        "title": "Mock PDF",
        "sections": [{"heading": "H1", "content": "C1"}]
    }
    
    response = client.post("/generate", json={
        "file_type": "pdf",
        "prompt": "make a pdf"
    })
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment; filename=test.pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF-")

@patch("services.gemini_service.generate_test_data", new_callable=AsyncMock)
def test_generate_excel_endpoint(mock_gemini):
    mock_gemini.return_value = {
        "sheets": [{"name": "S1", "rows": [{"col1": "val1"}]}]
    }
    
    response = client.post("/generate", json={
        "file_type": "excel",
        "prompt": "make an excel"
    })
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment; filename=test.xlsx" in response.headers["content-disposition"]
    assert response.content.startswith(b"PK\x03\x04")

@patch("services.gemini_service.generate_test_data", new_callable=AsyncMock)
def test_generate_image_endpoint(mock_gemini):
    mock_gemini.return_value = {
        "elements": [{"type": "text", "pos": [0,0], "text": "Test"}]
    }
    
    response = client.post("/generate", json={
        "file_type": "image",
        "prompt": "make an image"
    })
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert "attachment; filename=test.png" in response.headers["content-disposition"]
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")

def test_unsupported_type():
    response = client.post("/generate", json={
        "file_type": "word",
        "prompt": "invalid"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported file type"
