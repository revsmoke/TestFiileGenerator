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
    
    # Handle optional background color from palette description if provided
    # (Simple heuristic: if 'colors' contains a hex code, use it for background)
    colors_desc = data.get("colors", "")
    if isinstance(colors_desc, str) and "#" in colors_desc:
        import re
        hex_match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}', colors_desc)
        if hex_match:
            img = Image.new('RGB', (800, 600), color=hex_match.group(0))
            draw = ImageDraw.Draw(img)

    # Limit to 100 elements
    elements = data.get("elements", [])[:100]
    
    for element in elements:
        etype = element.get("type", "rect")
        
        # Support new photo-style fields with fallback to old names
        pos = element.get("image_pos") or element.get("text_pos") or element.get("pos", [50, 50])
        size = element.get("image_size", [100, 100])
        color = element.get("text_color") or element.get("color", "black")
        
        if not isinstance(pos, (list, tuple)) or len(pos) < 2:
            pos = [50, 50]
        if not isinstance(size, (list, tuple)) or len(size) < 2:
            size = [100, 100]
        
        try:
            # Handle shot types as themed overlays or special framing
            if etype in ["wide shot", "medium shot", "close up"]:
                # Draw a frame or a gradient box to represent the "shot"
                alpha = 50 if etype == "wide shot" else 100 if etype == "medium shot" else 200
                draw.rectangle([pos[0], pos[1], pos[0]+size[0], pos[1]+size[1]], outline=color, width=2)
            elif etype == "text" or "text" in element:
                draw.text((pos[0], pos[1]), str(element.get("text", "Photo Detail")), fill=color)
            elif etype == "rect":
                draw.rectangle([pos[0], pos[1], pos[0]+size[0], pos[1]+size[1]], outline=color, fill=color)
            elif etype == "circle":
                draw.ellipse([pos[0], pos[1], pos[0]+size[0], pos[1]+size[1]], outline=color, fill=color)
            else:
                # Default to a box for unknown types (like 'bird', 'wave' etc if AI gets creative)
                draw.rectangle([pos[0], pos[1], pos[0]+size[0], pos[1]+size[1]], outline=color)
        except Exception as e:
            print(f"Skipping malformed element {etype}: {e}")
            
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    print("Image generation complete")
    return buffer
