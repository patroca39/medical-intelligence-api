import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import fitz  # PyMuPDF

app = FastAPI(title="Medical Document Intelligence API")

# Setup template engine to serve the UI
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def render_dashboard(request: Request):
    """
    Serves the interactive web interface for drag-and-drop PDF testing.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/v1/extract")
async def extract_medical_record(file: UploadFile = File(...)):
    """
    Asynchronously ingest a medical PDF, extract its text layer using PyMuPDF,
    and prepare it for LLM data extraction.
    """
    # 1. Enforce strict PDF file-type guardrail
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF documents are accepted.")
    
    try:
        # 2. Read file straight into an in-memory byte buffer (No local disk storage)
        pdf_bytes = await file.read()
        
        # 3. Stream bytes into PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # 4. Extract raw text from all pages
        raw_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            raw_text += page.get_text()
            
        doc.close()
        
        # Guardrail if the PDF is purely scanned images (empty text layer)
        if not raw_text.strip():
            return {
                "success": False,
                "error": "The document contains no readable text layer. OCR fallback required."
            }
            
        # 5. Temporary Mock Return (We will swap this with Gemini in the next step)
        return {
            "success": True,
            "filename": file.filename,
            "extracted_characters": len(raw_text),
            "message": "Text layer extracted successfully! Ready for LLM parsing.",
            "preview_text": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal extraction error: {str(e)}")
