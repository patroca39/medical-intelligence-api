import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
from google.genai import types
import fitz  # PyMuPDF

app = FastAPI(title="Medical Document Intelligence API")

# Setup template engine to serve the UI
templates = Jinja2Templates(directory="templates")

# ----------------------------------------------------------------------
# PHASE 2.3: DEFINING THE STRICT MEDICAL SCHEMA VIA PYDANTIC
# ----------------------------------------------------------------------
class Medication(BaseModel):
    name: str = Field(description="The generic or brand name of the prescribed drug.")
    dosage: Optional[str] = Field(None, description="The dosage instructions, e.g., '500mg daily'.")

class MedicalRecordExtraction(BaseModel):
    patient_name: Optional[str] = Field(None, description="Full name of the patient. Clear capitalization.")
    date_of_birth: Optional[str] = Field(None, description="Patient's date of birth, standardized to YYYY-MM-DD if possible.")
    encounter_date: Optional[str] = Field(None, description="The date the clinical encounter or report took place.")
    primary_diagnosis: Optional[str] = Field(None, description="The main medical condition or reason for the visit identified by the clinician.")
    prescribed_medications: List[Medication] = Field(default=[], description="List of all medications mentioned along with their dosages.")
    attending_physician: Optional[str] = Field(None, description="The name of the doctor, clinician, or specialist who signed the record.")

# ----------------------------------------------------------------------
# API ROUTING & PROCESSING ENGINE
# ----------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def render_dashboard(request: Request):
    """Serves the interactive web interface for drag-and-drop PDF testing."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/v1/extract")
async def extract_medical_record(file: UploadFile = File(...)):
    """
    Asynchronously ingest a medical PDF, extract its text layer using PyMuPDF,
    and orchestrate structural extraction using Gemini structured output forcing.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF documents are accepted.")
    
    # Securely retrieve the API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="System configuration error: GEMINI_API_KEY environment variable is missing."
        )

    try:
        # PHASE 2.2: Read file straight into an in-memory byte buffer
        pdf_bytes = await file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        raw_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            raw_text += page.get_text()
            
        doc.close()
        
        if not raw_text.strip():
            return {
                "success": False,
                "error": "The document contains no readable text layer. Native PDF text extraction found nothing."
            }

        # PHASE 2.3: Initialize the Google GenAI Client & Execute Structured Extraction
        client = genai.Client(api_key=api_key)
        
        system_instruction = (
            "You are an expert clinical data extraction agent. Analyze the provided unstructured medical record "
            "text and accurately extract fields following the required JSON schema. If a specific field is entirely "
            "absent or cannot be determined from the text, set its value to null. Do not guess or extrapolate clinical data."
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Extract data from this medical text:\n\n{raw_text}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=MedicalRecordExtraction,
                temperature=0.1,  # Low temperature ensures high determinism and clinical accuracy
            ),
        )

        # Gemini returns the JSON as a string, so we parse it back into a dictionary for the API response
        parsed_data = json.loads(response.text)

        return {
            "success": True,
            "filename": file.filename,
            "data": parsed_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal extraction processing failure: {str(e)}")
