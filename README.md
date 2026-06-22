# Medical Document Intelligence API 🏥

An asynchronous, robust FastAPI backend designed to extract structured clinical data from unstructured and messy medical PDF records. 

This project bridges the gap between raw document parsing and highly structured database ingestion, utilizing AI orchestration to handle missing fields, bad OCR, and narrative clinical texts.

## 🚀 Live Demo
**[Insert Your Hugging Face Space URL Here]**

## ⚙️ Tech Stack
* **Backend:** FastAPI, Python 3.11, Uvicorn
* **Document Parsing:** PyMuPDF (fitz) for fast, in-memory byte-stream text extraction.
* **AI Orchestration:** Pydantic schema enforcement coupled with LLM structured output parsing.
* **Deployment:** Docker, Hugging Face Spaces

## 🛠️ Features
* **Strict Schema Enforcement:** Utilizes Pydantic to guarantee 100% predictable JSON structures.
* **Edge-Case Resiliency:** Intelligently handles missing patient demographics (returning standard nulls), standardizes erratic date formats, and corrects heavy OCR/typographical errors seamlessly.
* **In-Memory Processing:** PDFs are buffered and parsed entirely in memory without writing temporary files to the disk, ensuring high throughput and strict HIPAA-compliant data handling practices.

## 📡 API Endpoint
**`POST /api/v1/extract`**

Accepts `multipart/form-data` with a `.pdf` file payload.

**Sample Successful Response:**
```json
{
    "success": true,
    "filename": "clinical_note.pdf",
    "data": {
        "patient_name": "Sarah Jenkins",
        "date_of_birth": "1972-07-04",
        "encounter_date": "2026-04-12",
        "primary_diagnosis": "Acute bronchitis",
        "prescribed_medications": [
            {
                "name": "Albuterol",
                "dosage": "Two puffs every four hours as needed"
            }
        ],
        "attending_physician": "Dr. Gregory House"
    }
}
