import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Preferred experimental models
TEXT_MODEL = 'gemini-3-pro-preview'
IMAGE_MODEL = 'gemini-3-pro-image-preview'
FALLBACK_MODEL = 'gemini-2.0-flash'

async def generate_test_data(file_type: str, prompt: str):
    """
    Generates structured data for a specific file type using Gemini.
    """
    primary_model_name = IMAGE_MODEL if file_type == "image" else TEXT_MODEL
    
    # Try primary model, then fallback
    for model_name in [primary_model_name, FALLBACK_MODEL]:
        print(f"Attempting generation with: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            
            system_instruction = f"""
            You are a test data generator. Your goal is to generate realistic content for a {file_type} file based on the user's prompt.
            Return only a JSON object.
            
            For 'pdf' or 'docx': Provide 'title', 'sections' (list of {{'heading': ..., 'content': ...}}).
            For 'excel' or 'csv': Provide 'sheets' (list of {{'name': ..., 'rows': [list of dicts]}}).
            For 'image': Provide 'description', 'colors' (list), 'elements' (list of {{'type': 'text|rect|circle', 'text': ..., 'pos': [x, y], 'color': ...}}).
            
            Prompt: {prompt}
            """
            
            # Add a 30s timeout to prevent indefinite stalling
            response = model.generate_content(
                system_instruction,
                request_options={"timeout": 30}
            )
            content = response.text.strip()
            print(f"Generation successful with {model_name}")
            
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            return json.loads(content)
            
        except Exception as e:
            print(f"Error with model {model_name}: {e}")
            if model_name == FALLBACK_MODEL:
                return {"error": f"All models failed. Last error: {str(e)}"}
            print(f"Falling back from {model_name}...")
            continue
