import io
import pytest
from services.file_generator import generate_pdf, generate_excel, generate_image

def test_generate_pdf():
    data = {
        "title": "Test PDF",
        "sections": [
            {"heading": "Section 1", "content": "Hello World"}
        ]
    }
    buffer = generate_pdf(data)
    assert isinstance(buffer, io.BytesIO)
    content = buffer.getvalue()
    assert content.startswith(b'%PDF-')

def test_generate_excel():
    data = {
        "sheets": [
            {"name": "TestSheet", "rows": [{"A": 1, "B": 2}]}
        ]
    }
    buffer = generate_excel(data)
    assert isinstance(buffer, io.BytesIO)
    # Basic check for Excel signature (zip format)
    content = buffer.getvalue()
    assert content.startswith(b'PK\x03\x04')

def test_generate_image():
    data = {
        "elements": [
            {"type": "rect", "pos": [0, 0], "color": "red"},
            {"type": "text", "pos": [10, 10], "text": "Hi", "color": "blue"}
        ]
    }
    buffer = generate_image(data)
    assert isinstance(buffer, io.BytesIO)
    content = buffer.getvalue()
    # PNG signature
    assert content.startswith(b'\x89PNG\r\n\x1a\n')
