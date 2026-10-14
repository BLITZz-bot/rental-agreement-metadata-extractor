from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import shutil

from src.document_loader import load_document
from src.extractor import extract_fields

app = FastAPI(
    title="Rental Agreement Metadata Extractor",
    description="Upload a .docx or .png rental agreement and get 6 fields extracted.",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "API is running. POST a file to /extract"}


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    """
    Upload a .docx or .png file.
    Returns JSON with extracted metadata fields.
    """
    allowed = [".docx", ".png"]
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Use .docx or .png")

    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
        
    try:
        content, content_type = load_document(tmp_path)
        result = extract_fields(content, content_type)
        result["file_name"] = file.filename
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(tmp_path)   # clean up temp file
