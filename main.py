from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import services.gemini_service as gemini
import services.file_generator as generator
from pydantic import BaseModel
import io

app = FastAPI(title="Gemini Test File Generator Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    file_type: str
    prompt: str

@app.post("/generate")
async def generate_file(req: GenerateRequest):
    supported_types = ["pdf", "excel", "xlsx", "image"]
    if req.file_type not in supported_types:
        raise HTTPException(status_code=400, detail="Unsupported file type")
        
    data = await gemini.generate_test_data(req.file_type, req.prompt)
    
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
        
    try:
        if req.file_type == "pdf":
            buffer = generator.generate_pdf(data)
            media_type = "application/pdf"
            filename = "test.pdf"
        elif req.file_type in ["excel", "xlsx"]:
            buffer = generator.generate_excel(data)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = "test.xlsx"
        elif req.file_type == "image":
            buffer = generator.generate_image(data)
            media_type = "image/png"
            filename = "test.png"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
            
        return StreamingResponse(
            buffer, 
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
