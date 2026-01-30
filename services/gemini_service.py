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

PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")

def _load_prompt(file_type: str) -> str:
    """Loads prompt template from markdown file."""
    path = os.path.join(PROMPT_DIR, f"{file_type}.md")
    if not os.path.exists(path):
        # Fallback to general image/text if specific one missing
        if file_type in ["photo"]:
            path = os.path.join(PROMPT_DIR, "image.md")
        else:
            path = os.path.join(PROMPT_DIR, "pdf.md")
            
    with open(path, "r") as f:
        return f.read()

async def generate_test_data(file_type: str, prompt: str):
    """
    Generates structured data for a specific file type using Gemini.
    """
    primary_model_name = IMAGE_MODEL if file_type in ["image", "photo"] else TEXT_MODEL
    prompt_template = _load_prompt(file_type)
    
    # Try primary model, then fallback
    for model_name in [primary_model_name, FALLBACK_MODEL]:
        print(f"Attempting generation with: {model_name} for {file_type}")
        try:
            model = genai.GenerativeModel(model_name)
            
            full_prompt = f"{prompt_template}\n\nUser Prompt: {prompt}"
            
            # Add a 30s timeout to prevent indefinite stalling
            response = model.generate_content(
                full_prompt,
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
