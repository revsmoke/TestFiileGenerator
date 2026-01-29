import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash')

async def generate_test_data(file_type: str, prompt: str):
    """
    Generates structured data for a specific file type using Gemini.
    """
    system_instruction = f"""
    You are a test data generator. Your goal is to generate realistic content for a {file_type} file based on the user's prompt.
    Return only a JSON object.
    
    For 'pdf' or 'docx': Provide 'title', 'sections' (list of {{'heading': ..., 'content': ...}}).
    For 'excel' or 'csv': Provide 'sheets' (list of {{'name': ..., 'rows': [list of dicts]}}).
    For 'image': Provide 'description', 'colors' (list), 'elements' (list of {{'type': 'text|rect|circle', 'text': ..., 'pos': [x, y], 'color': ...}}).
    
    Prompt: {prompt}
    """
    
    response = model.generate_content(system_instruction)
    
    # Try to parse JSON from response
    content = response.text.strip()
    if content.startswith("```json"):
        content = content[7:-3].strip()
    elif content.startswith("```"):
        content = content[3:-3].strip()
        
    try:
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return {"error": "Failed to parse data", "raw": content}
