from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import os

def generate_pdf(data: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, data.get("title", "Test Document"))
    
    # Content
    c.setFont("Helvetica", 12)
    y = height - 100
    for section in data.get("sections", []):
        if y < 100:
            c.showPage()
            y = height - 72
            
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, y, section.get("heading", "Section"))
        y -= 20
        
        c.setFont("Helvetica", 10)
        # Simple text wrapping could be added here, but for test files this is a start
        c.drawString(72, y, section.get("content", ""))
        y -= 40
        
    c.save()
    buffer.seek(0)
    return buffer

def generate_excel(data: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        for sheet in data.get("sheets", [{"name": "Sheet1", "rows": []}]):
            df = pd.DataFrame(sheet.get("rows", []))
            df.to_excel(writer, sheet_name=sheet.get("name", "Sheet1"), index=False)
    buffer.seek(0)
    return buffer

def generate_image(data: dict) -> io.BytesIO:
    print(f"Generating image with {len(data.get('elements', []))} elements")
    # 800x600 default
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Limit to 100 elements to prevent accidental OOM or slowness
    elements = data.get("elements", [])[:100]
    
    for element in elements:
        etype = element.get("type")
        pos = element.get("pos", [50, 50])
        color = element.get("color", "black")
        
        # Ensure pos is a list of two numbers
        if not isinstance(pos, (list, tuple)) or len(pos) < 2:
            pos = [50, 50]
        
        try:
            if etype == "text":
                draw.text((pos[0], pos[1]), str(element.get("text", "Test")), fill=color)
            elif etype == "rect":
                draw.rectangle([pos[0], pos[1], pos[0]+100, pos[1]+100], outline=color, fill=color)
            elif etype == "circle":
                draw.ellipse([pos[0], pos[1], pos[0]+100, pos[1]+100], outline=color, fill=color)
        except Exception as e:
            print(f"Skipping malformed element {etype}: {e}")
            
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    print("Image generation complete")
    return buffer
